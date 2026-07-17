#!/usr/bin/env python3
"""Red/green tests for multi-file-commit (delta-resolution-polish 1/3): harden
`_atomic_write_many` into a TRUE all-or-nothing N-file commit via RENAME-ASIDE rollback,
and route fold/release/seed through it. CONTRACT frozen @ v1.

Today's primitive narrows but does not eliminate the partial-write window: a phase-2
mid-rename failure leaves the already-renamed targets committed. The hardened primitive
moves each existing target ASIDE to a `.bak` before moving the new temp in, and on ANY
commit failure rolls back in reverse (unlink the landed new file, rename the `.bak` back),
so the set is all-or-nothing. Run:
  python3 -m unittest test_multi_file_commit -v
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)

_REAL_REPLACE = os.replace


def _flaky_replace(fail_dsts):
    """An os.replace that raises ONCE on the first move whose DEST is in fail_dsts (the
    commit move-IN of a target path), then runs for real — so the COMMIT fails but the
    subsequent ROLLBACK restore (same dest) succeeds, the realistic transient-failure case.
    Every other move (incl. move-aside to a .bak temp) runs for real throughout."""
    fail = {str(p) for p in fail_dsts}
    fired = set()

    def _inner(src, dst, *a, **k):
        key = str(dst)
        if key in fail and key not in fired:
            fired.add(key)
            raise OSError("injected commit failure")
        return _REAL_REPLACE(src, dst, *a, **k)

    return _inner


def _siblings(*dirs):
    """Every .tmp / .bak sibling left behind across the given dirs."""
    leftovers = []
    for d in dirs:
        leftovers += [p.name for p in Path(d).iterdir()
                      if p.suffix in (".tmp", ".bak")]
    return leftovers


class PrimitiveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mfc-")).resolve()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_all_files_land_happy_path(self):
        a = self.tmp / "a.txt"; a.write_text("OLD-A", encoding="utf-8")
        b = self.tmp / "b.txt"                       # absent
        c = self.tmp / "sub" / "c.txt"               # absent, nested
        add._atomic_write_many([(a, "NEW-A"), (b, "NEW-B"), (c, "NEW-C")])
        self.assertEqual(a.read_text(encoding="utf-8"), "NEW-A")
        self.assertEqual(b.read_text(encoding="utf-8"), "NEW-B")
        self.assertEqual(c.read_text(encoding="utf-8"), "NEW-C")
        self.assertEqual(_siblings(self.tmp, self.tmp / "sub"), [])

    def test_stage_failure_commits_nothing(self):
        a = self.tmp / "a.txt"; a.write_text("OLD-A", encoding="utf-8")
        b = self.tmp / "b.txt"; b.write_text("OLD-B", encoding="utf-8")
        real_mkstemp = tempfile.mkstemp
        calls = {"n": 0}

        def flaky_mkstemp(*args, **kw):
            calls["n"] += 1
            if calls["n"] == 2:                      # second staged temp fails (disk-full sim)
                raise OSError("injected stage failure")
            return real_mkstemp(*args, **kw)

        with mock.patch("add.tempfile.mkstemp", side_effect=flaky_mkstemp):
            with self.assertRaises(OSError):
                add._atomic_write_many([(a, "NEW-A"), (b, "NEW-B")])
        self.assertEqual(a.read_text(encoding="utf-8"), "OLD-A")   # nothing committed
        self.assertEqual(b.read_text(encoding="utf-8"), "OLD-B")
        self.assertEqual(_siblings(self.tmp), [])                  # staged temp cleaned

    def test_fsync_failure_leaves_no_tmp(self):
        # a write/fsync failure (not mkstemp) must still clean the staged .tmp — the temp is
        # tracked BEFORE the write, so the finally reaches it.
        a = self.tmp / "a.txt"; a.write_text("OLD-A", encoding="utf-8")
        with mock.patch("add.os.fsync", side_effect=OSError("injected fsync failure")):
            with self.assertRaises(OSError):
                add._atomic_write_many([(a, "NEW-A")])
        self.assertEqual(a.read_text(encoding="utf-8"), "OLD-A")    # target untouched
        self.assertEqual(_siblings(self.tmp), [])                   # no .tmp leaked

    def test_commit_failure_rolls_back_all(self):
        a = self.tmp / "a.txt"; a.write_text("OLD-A", encoding="utf-8")
        b = self.tmp / "b.txt"; b.write_text("OLD-B", encoding="utf-8")
        c = self.tmp / "c.txt"                        # absent
        with mock.patch("add.os.replace", side_effect=_flaky_replace([b])):
            with self.assertRaises(OSError):
                add._atomic_write_many([(a, "NEW-A"), (b, "NEW-B"), (c, "NEW-C")])
        self.assertEqual(a.read_text(encoding="utf-8"), "OLD-A")   # the landed rename rolled back
        self.assertEqual(b.read_text(encoding="utf-8"), "OLD-B")   # never changed
        self.assertFalse(c.exists())                               # stayed absent
        self.assertEqual(_siblings(self.tmp), [])                  # no .tmp/.bak residue


class _Project(unittest.TestCase):
    """A real .add project in a tmp cwd."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mfc-proj-")).resolve()
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self.root = self.tmp / ".add"
        self.project = self.root / "PROJECT.md"
        self.conventions = self.root / "CONVENTIONS.md"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _silent(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit:
            pass
        return out.getvalue() + err.getvalue()

    def _task_md(self, slug):
        return (self.root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")

    def _set_spec(self, slug, text):
        """Plant one open SPEC delta in slug's §7 OBSERVE (mirrors test_seed_and_drop)."""
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        idx = s.index("## 7 · OBSERVE")
        head_end = s.index("\n", idx) + 1
        body = f"\n### Spec delta\n- [SPEC · open] {text} (evidence: ev)\n\n### Competency deltas\n"
        p.write_text(s[:head_end] + body, encoding="utf-8")

    # fold scaffolding (mirrors test_fold_command) --------------------------------
    def _plant_comp(self, slug, tag, text, ev="e"):
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        i = s.index("### Competency deltas") + len("### Competency deltas")
        p.write_text(s[:i] + f"\n- [{tag} · open] {text} (evidence: {ev})\n" + s[i:],
                     encoding="utf-8")

    def _set_fv(self, n):
        s = self.project.read_text(encoding="utf-8")
        if re.search(r"foundation-version:\s*\d+", s):
            s = re.sub(r"foundation-version:\s*\d+", f"foundation-version: {n}", s)
        else:
            s = re.sub(r"(?m)^(slug:.*)$", rf"\1 · foundation-version: {n}", s, count=1)
        self.project.write_text(s, encoding="utf-8")

    def _add_method_learnings(self):
        s = self.conventions.read_text(encoding="utf-8")
        if "## Method learnings" not in s:
            self.conventions.write_text(
                s.rstrip() + "\n\n## Method learnings (folded from OBSERVE deltas)\n",
                encoding="utf-8")

    def _fv(self):
        m = re.search(r"foundation-version:\s*(\d+)", self.project.read_text(encoding="utf-8"))
        return int(m.group(1)) if m else None

    def _make_foldable(self):
        self._set_fv(50)
        self._add_method_learnings()
        self._silent("new-task", "alpha")
        self._plant_comp("alpha", "SDD", "an SDD lesson")       # -> PROJECT.md §Spec
        self._silent("new-task", "beta")
        self._plant_comp("beta", "ADD", "an ADD lesson")        # -> CONVENTIONS.md §Method learnings


class AdoptionTest(_Project):
    def test_fold_routes_through_primitive(self):
        self._make_foldable()
        with mock.patch("add._atomic_write_many", wraps=add._atomic_write_many) as spy:
            self._silent("fold")
        self.assertTrue(spy.called, "fold must commit via _atomic_write_many")

    def test_release_routes_through_primitive(self):
        with mock.patch("add._atomic_write_many", wraps=add._atomic_write_many) as spy:
            self._silent("release", "0.0.0-test", "--force")
        self.assertEqual(spy.call_count, 1, "release must commit via one _atomic_write_many")
        writes = spy.call_args.args[0]
        names = sorted(Path(p).name for p, _ in writes)
        self.assertEqual(names, ["CHANGELOG.md", "RELEASES.md"])

    def test_seed_routes_through_primitive(self):
        self._silent("new-task", "prior")
        self._set_spec("prior", "a deferred idea")
        with mock.patch("add._atomic_write_many", wraps=add._atomic_write_many) as spy:
            self._silent("new-task", "followup", "--from-delta", "prior")
        self.assertEqual(spy.call_count, 1, "from-delta seed must commit both files via one call")
        writes = spy.call_args.args[0]
        self.assertEqual(len(writes), 2, "the new TASK.md + the consumed source TASK.md")


class FoldAtomicityTest(_Project):
    def test_fold_atomic_under_injected_commit_failure(self):
        self._make_foldable()
        fv_before = self._fv()
        # fail on the move-IN of CONVENTIONS.md (the 2nd file) -> PROJECT.md (1st, committed) must roll back.
        # The primitive rolls back then RE-RAISES; cmd_fold lets the IO error propagate (expected).
        with mock.patch("add.os.replace", side_effect=_flaky_replace([self.conventions])):
            with self.assertRaises(OSError):
                self._silent("fold")
        self.assertEqual(self._fv(), fv_before, "PROJECT.md foundation-version must NOT advance on a partial fold")
        self.assertIn("[SDD · open]", self._task_md("alpha"), "the lesson must stay open (no silent flip)")
        self.assertIn("[ADD · open]", self._task_md("beta"))
        self.assertEqual(_siblings(self.root), [], "no .tmp/.bak left in .add/ after a rolled-back fold")


class ReleaseAtomicityTest(_Project):
    def test_release_all_or_nothing_on_commit_failure(self):
        # seed a prior CHANGELOG/RELEASES, then fail the RELEASES.md move-IN mid-cut
        changelog = self.tmp / "CHANGELOG.md"; changelog.write_text("# Changelog\n\nOLD-CL\n", encoding="utf-8")
        releases = self.tmp / "RELEASES.md"; releases.write_text("# Releases\n\nOLD-REL\n", encoding="utf-8")  # project root, sibling of CHANGELOG
        with mock.patch("add.os.replace", side_effect=_flaky_replace([releases])):
            out = self._silent("release", "0.0.0-test", "--force")
        self.assertIn("release_write_failed", out)                      # command-level error preserved
        self.assertIn("OLD-CL", changelog.read_text(encoding="utf-8"))  # CHANGELOG rolled back
        self.assertNotIn("0.0.0-test", changelog.read_text(encoding="utf-8"))
        self.assertIn("OLD-REL", releases.read_text(encoding="utf-8"))  # RELEASES untouched
        self.assertEqual(_siblings(self.tmp, self.root), [])            # no .tmp/.bak residue


class SeedAtomicityTest(_Project):
    def test_seed_all_or_nothing_on_commit_failure(self):
        self._silent("new-task", "prior")
        self._set_spec("prior", "a deferred idea")
        prior_before = self._task_md("prior")
        followup_md = self.root / "tasks" / "followup" / "TASK.md"
        # fail on the source-delta (prior TASK.md) move-IN -> the new followup TASK.md must roll back too
        prior_md = self.root / "tasks" / "prior" / "TASK.md"
        with mock.patch("add.os.replace", side_effect=_flaky_replace([prior_md])):
            with self.assertRaises(OSError):
                self._silent("new-task", "followup", "--from-delta", "prior")
        self.assertEqual(self._task_md("prior"), prior_before, "source delta must NOT be half-flipped")
        self.assertFalse(followup_md.exists(), "the new TASK.md must not be left behind on a failed seed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
