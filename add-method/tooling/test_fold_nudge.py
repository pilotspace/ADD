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
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add


def _meet_exit_criteria(ms: str) -> None:
    """v20 goal-gate: check the milestone's '## Exit criteria' box so milestone-done
    releases. Targets only the Exit-criteria section — never the Tasks rows."""
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")


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
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
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
        _meet_exit_criteria(ms)              # v20 goal-gate: meet criteria before close

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

    # --- milestone-done: COUNT the open deltas + point at the living-spec channel --
    def test_milestone_done_previews_deltas_and_fold_command(self):
        """kernel-trim (ADD 2.0 M5): the fold ceremony died — the close prompt
        counts the open §7 deltas and points at delta-append (the living-spec
        channel), never at a fold verb."""
        self._complete_task_in_milestone("mvp", "t")
        self._add_delta("t", "- [DDD \u00b7 open] domain gap found (evidence: prod signal)")
        code, out, _ = _run(["milestone-done", "mvp"])
        self.assertEqual(code, 0)
        self.assertRegex(out, r"note: 1 open delta", "close must count the open deltas")
        self.assertIn("add.py delta-append", out, "must point at the living-spec channel")
        self.assertIn("add.py deltas", out, "must still point at the review command")
        self.assertNotIn("add.py fold", out, "the fold verb is dead — never suggested")

    # --- observe transition: file lessons into the living specs at completion ------
    def test_gate_completion_suggests_fold(self):
        """kernel-trim (ADD 2.0 M5): a completing gate points §7 lessons at
        delta-append (the living-spec channel), never at the dead fold verb."""
        add.main(["new-task", "a"])             # fresh project is grandfathered-locked
        add.main(["phase", "verify", "a"])      # to the gate
        code, out, _ = _run(["gate", "PASS", "a"])
        self.assertEqual(code, 0)
        self.assertIn("add.py delta-append", out,
                      "a completing gate must point at the living-spec channel")
        self.assertIn("§7", out, "the suggestion names where the lessons live")
        self.assertNotIn("add.py fold", out, "the fold verb is dead — never suggested")

    def test_advance_crossings_silent_on_fold(self):
        """The fold suggestion fires ONLY at gate/completion — advancing
        into any phase stays silent on folding (additive, no noise)."""
        add.main(["new-task", "a"])             # at direction (phase-collapse-3 seed)
        p = Path(add.find_root()) / "tasks" / "a" / "TASK.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by T\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none"),
            encoding="utf-8")                   # pass the crossing's freeze + flag floor
        code, out, _ = _run(["advance", "a"])   # direction -> build
        self.assertEqual(code, 0)
        self.assertNotIn("add.py fold", out,
                         "advance crossings must not suggest folding")


if __name__ == "__main__":
    unittest.main(verbosity=2)
