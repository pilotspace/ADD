#!/usr/bin/env python3
"""Red/green tests for delta-task-backlink (traceability-ids M4/1).

Completes the delta->task lineage so it is BIDIRECTIONAL:
  - a `--from-delta` seed pre-fills the new task's §0 `Related intent:` with a backlink to its
    originating delta (mirrors the existing §1 Feature pre-fill) — placeholder-only, seed-only;
  - `add.py check` WARNs (nudge, exit 0) on a `[SPEC · seeded] … [→ slug]` whose pointer task is
    neither a live state task NOR archived (`_archived_task_slugs`) — a dangling lineage.

Run: cd add-method/tooling && python3 -m unittest test_delta_task_backlink -v
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ADD_PY_COPIES = [
    HERE / "add.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
]
_CANON_SKILL = HERE.parent / "skill" / "add"
PHASES_POOL = [
    "phases/0-setup.md", "phases/1-specify.md",
    "phases/2-scenarios.md", "phases/3-plan.md", "phases/4-tests.md",
    "phases/5-build.md", "phases/6-verify.md", "phases/7-observe.md",
]
_REL_LINE = re.compile(r"(?m)^Related intent:\s*(.+?)\s*$")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-dtbl-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

    def _silent(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                if e.code:
                    raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        buf = io.StringIO()
        code = 0
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), code

    def _task_md(self, slug: str) -> Path:
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _related_intent(self, slug: str):
        m = _REL_LINE.search(self._task_md(slug).read_text(encoding="utf-8"))
        return m.group(1) if m else None

    def _append_delta(self, slug: str, line: str):
        p = self._task_md(slug)
        p.write_text(p.read_text(encoding="utf-8") + "\n" + line + "\n", encoding="utf-8")

    def _give_open_delta(self, slug: str, text="rate-limit the retry path"):
        self._append_delta(slug, f"  - [SPEC · open] {text} (evidence: prod herd)")


class SeedPrefillsBacklink(_Board):
    def test_seed_prefills_section0_backlink(self):              # M1
        self._silent("new-task", "prior", "--title", "P")
        self._give_open_delta("prior")
        self._silent("new-task", "child", "--title", "C", "--from-delta", "prior")
        rel = self._related_intent("child") or ""
        self.assertIn("prior", rel, "child §0 Related intent must name the prior task")
        self.assertNotIn("<", rel, "the §0 placeholder must be replaced, not left as <…>")
        prior_txt = self._task_md("prior").read_text(encoding="utf-8")
        self.assertIn("[→ child]", prior_txt, "the source delta is flipped to seeded [→ child]")

    def test_plain_newtask_leaves_section0(self):                # M2, R:backlink_clobbers_authored
        self._silent("new-task", "plain", "--title", "X")
        rel = self._related_intent("plain") or ""
        self.assertIn("<", rel, "a non-seeded task keeps the §0 Related-intent placeholder")


class CheckWarnsDangling(_Board):
    def test_check_warns_on_dangling_pointer(self):             # M3
        self._silent("new-task", "host", "--title", "H")
        self._append_delta("host", "  - [SPEC · seeded] a thing (evidence: y) [→ ghost]")
        out, code = self._run("check")
        self.assertIn("ghost", out, "the WARN must name the missing pointer task")
        self.assertEqual(code, 0, "a dangling-lineage finding is a WARN, never red")

    def test_archived_pointer_is_silent(self):                  # M4, R:false_dangling_warn
        self._silent("new-task", "host", "--title", "H")
        self._append_delta("host", "  - [SPEC · seeded] a thing (evidence: y) [→ arch-child]")
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text(encoding="utf-8"))
        st.setdefault("archived", []).append({"slug": "v0", "task_slugs": ["arch-child"]})
        sp.write_text(json.dumps(st, indent=2), encoding="utf-8")
        out, code = self._run("check")
        self.assertNotIn("arch-child", out, "an archived pointer must NOT warn as dangling")
        self.assertEqual(code, 0)

    def test_live_pointer_is_silent(self):                      # M4
        self._silent("new-task", "host", "--title", "H")
        self._silent("new-task", "target", "--title", "T")
        self._append_delta("host", "  - [SPEC · seeded] a thing (evidence: y) [→ target]")
        out, code = self._run("check")
        self.assertNotIn("dangling", out.lower(), "a live pointer must not warn as dangling")
        self.assertEqual(code, 0)

    def test_dangling_warn_never_blocks(self):                  # R:lineage_warn_blocks
        self._silent("new-task", "host", "--title", "H")
        self._append_delta("host", "  - [SPEC · seeded] a thing (evidence: y) [→ ghost]")
        _, code = self._run("check")
        self.assertEqual(code, 0, "the dangling WARN must not turn `check` red")


class SeededPointerHelper(unittest.TestCase):
    def test_seeded_delta_pointers_pure(self):                  # M3 (unit)
        text = (
            "  - [SPEC · seeded] x (evidence: a) [→ alpha]\n"
            "  - [SPEC · open] y (evidence: b)\n"
            "  - [SPEC · dropped] z (evidence: c) [→ beta]\n"
            "  - [SPEC · seeded] w (evidence: d) [→ gamma]\n"
        )
        self.assertEqual(add._seeded_delta_pointers(text), ["alpha", "gamma"],
                         "only SEEDED deltas' pointers, in order; open/dropped ignored")


class EnginePinnedAndPoolUntouched(unittest.TestCase):
    def test_engine_byte_identical_to_pin(self):                # M5, R:engine_pin_drift
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match the re-pinned engine_pin.ENGINE_MD5")

if __name__ == "__main__":
    unittest.main(verbosity=2)
