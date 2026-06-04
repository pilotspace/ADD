#!/usr/bin/env python3
"""Behavioral proof of the fold-nudge (task: v11 fold-nudge).

Emission and folding of competency deltas are decoupled — a fast run accumulates
open deltas that sit unfolded because nothing surfaces them (the v6 RETRO flagged
this; the v5 convergence-signal task was cut). v11 wires the already-shipped
_collect_open_deltas into `status` (a passive count) and `milestone-done` (a fold
reminder at the natural fold point). Read-only and additive: silent at zero.
Run: python3 -m unittest test_fold_nudge -v
"""
import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class FoldNudgeTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-fold-nudge-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _add_delta(self, slug, line):
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        text = p.read_text(encoding="utf-8")
        marker = "### Competency deltas"
        idx = text.index(marker) + len(marker)
        p.write_text(text[:idx] + "\n" + line + "\n" + text[idx:], encoding="utf-8")

    def _complete_task_in_milestone(self, ms, slug):
        add.main(["new-milestone", ms, "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", slug])
        add.main(["phase", "verify", slug])   # escape hatch: scaffold straight to verify
        add.main(["gate", "PASS", slug])      # task is now done

    # --- status: a passive nudge --------------------------------------------
    def test_status_nudges_when_open_deltas(self):
        add.main(["new-task", "a"])
        self._add_delta("a", "- [TDD · open] a learning (evidence: e)")
        _, out, _ = _run(["status"])
        self.assertRegex(out, r"deltas\s*:\s*1 open",
                         "status must surface the open-delta count")
        self.assertIn("add.py deltas", out)

    def test_status_silent_when_no_open_deltas(self):
        add.main(["new-task", "a"])  # task exists, but no deltas
        _, out, _ = _run(["status"])
        self.assertNotRegex(out, r"deltas\s*:\s*\d+ open",
                            "status must NOT nudge when there are no open deltas")

    def test_status_silent_when_only_folded(self):
        add.main(["new-task", "a"])
        self._add_delta("a", "- [TDD · folded] historical (evidence: e)")
        _, out, _ = _run(["status"])
        self.assertNotRegex(out, r"deltas\s*:\s*\d+ open",
                            "folded deltas are not open — no nudge")

    # --- milestone-done: a fold reminder at the natural fold point ----------
    def test_milestone_done_nudges_open_deltas(self):
        self._complete_task_in_milestone("mvp", "t")
        self._add_delta("t", "- [DDD · open] domain gap found (evidence: prod signal)")
        code, out, _ = _run(["milestone-done", "mvp"])
        self.assertEqual(code, 0)
        self.assertIn("open", out)
        self.assertIn("add.py deltas", out, "milestone-done must point at the fold")

    def test_milestone_done_silent_when_no_open_deltas(self):
        self._complete_task_in_milestone("mvp", "t")
        code, out, _ = _run(["milestone-done", "mvp"])
        self.assertEqual(code, 0)
        self.assertNotIn("add.py deltas", out,
                         "no fold nudge when there are no open deltas")


if __name__ == "__main__":
    unittest.main(verbosity=2)
