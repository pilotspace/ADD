#!/usr/bin/env python3
"""Red/green tests for delta-match-selector (delta-resolution-polish 2/3): a `--match <substr>`
selector on `new-task --from-delta` and `drop-delta` targets ONE open SPEC delta among several.
CONTRACT frozen @ v1. --match absent → byte-identical first-open behavior. Run:
  python3 -m unittest test_delta_match_selector -v
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    try:
        with redirect_stdout(out), redirect_stderr(err):
            add.main(list(argv))
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    return code, out.getvalue(), err.getvalue()


class _Project(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-dms-")).resolve()
        os.chdir(self.tmp)
        _run(["init", "--name", "demo"])
        self.root = self.tmp / ".add"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _task_md(self, slug):
        return (self.root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")

    def _mk(self, slug):
        _run(["new-task", slug, "--title", "Feature"])

    def _set_spec(self, slug, *open_texts):
        """Plant one open SPEC delta per text in slug's §7 OBSERVE."""
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        idx = s.index("## 7 · OBSERVE")
        head_end = s.index("\n", idx) + 1
        lines = "".join(f"- [SPEC · open] {t} (evidence: ev)\n" for t in open_texts)
        body = f"\n### Spec delta\n{lines}\n### Competency deltas\n"
        p.write_text(s[:head_end] + body, encoding="utf-8")


class DropMatchTest(_Project):
    def test_drop_match_targets_specific(self):
        self._mk("t"); self._set_spec("t", "alpha thing", "beta thing")
        code, out, err = _run(["drop-delta", "t", "--match", "beta"])
        self.assertEqual(code, 0, err)
        md = self._task_md("t")
        self.assertIn("[SPEC · dropped] beta thing", md)
        self.assertIn("[SPEC · open] alpha thing", md)

    def test_match_case_insensitive(self):
        self._mk("t"); self._set_spec("t", "Rate Limit retries")
        code, out, err = _run(["drop-delta", "t", "--match", "rate limit"])
        self.assertEqual(code, 0, err)
        self.assertIn("[SPEC · dropped] Rate Limit retries", self._task_md("t"))

    def test_no_match_first_open_byte_identical(self):
        self._mk("t"); self._set_spec("t", "alpha", "beta")
        code, out, err = _run(["drop-delta", "t"])           # no --match
        self.assertEqual(code, 0, err)
        md = self._task_md("t")
        self.assertIn("[SPEC · dropped] alpha", md)          # first open
        self.assertIn("[SPEC · open] beta", md)

    def test_no_matching_rejects(self):
        self._mk("t"); self._set_spec("t", "alpha")
        before = self._task_md("t")
        code, out, err = _run(["drop-delta", "t", "--match", "zzz"])
        self.assertNotEqual(code, 0)
        self.assertIn("no_matching_spec_delta", out + err)
        self.assertEqual(self._task_md("t"), before)         # byte-unchanged

    def test_ambiguous_rejects(self):
        self._mk("t"); self._set_spec("t", "alpha one", "alpha two")
        before = self._task_md("t")
        code, out, err = _run(["drop-delta", "t", "--match", "alpha"])
        self.assertNotEqual(code, 0)
        self.assertIn("ambiguous_spec_match", out + err)
        self.assertEqual(self._task_md("t"), before)

    def test_match_excludes_evidence_even_when_unclosed(self):
        # a malformed delta (unclosed evidence paren) must NOT let --match hit the evidence text
        self._mk("t")
        p = self.root / "tasks" / "t" / "TASK.md"
        s = p.read_text(encoding="utf-8")
        idx = s.index("## 7 · OBSERVE"); he = s.index("\n", idx) + 1
        p.write_text(s[:he] + "\n### Spec delta\n- [SPEC · open] fix logic (evidence: SPECIALKEY\n\n"
                     "### Competency deltas\n", encoding="utf-8")
        before = p.read_text(encoding="utf-8")
        code, out, err = _run(["drop-delta", "t", "--match", "SPECIALKEY"])   # only in the evidence
        self.assertNotEqual(code, 0)
        self.assertIn("no_matching_spec_delta", out + err)
        self.assertEqual(p.read_text(encoding="utf-8"), before)
        # but the real text IS matchable
        code, out, err = _run(["drop-delta", "t", "--match", "fix logic"])
        self.assertEqual(code, 0, err)


class SeedMatchTest(_Project):
    def test_seed_match_targets_and_prefills(self):
        self._mk("prior"); self._set_spec("prior", "rate limit", "retry budget")
        code, out, err = _run(["new-task", "follow", "--from-delta", "prior", "--match", "retry budget"])
        self.assertEqual(code, 0, err)
        prior = self._task_md("prior")
        self.assertIn("[SPEC · seeded] retry budget (evidence: ev) [→ follow]", prior)
        self.assertIn("[SPEC · open] rate limit", prior)
        self.assertIn("retry budget", self._task_md("follow"))   # §1 Feature pre-filled from the matched delta

    def test_match_requires_from_delta(self):
        code, out, err = _run(["new-task", "foo", "--match", "bar"])   # no --from-delta
        self.assertNotEqual(code, 0)
        self.assertIn("match_requires_from_delta", out + err)
        self.assertFalse((self.root / "tasks" / "foo").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
