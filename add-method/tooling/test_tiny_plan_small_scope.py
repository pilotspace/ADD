#!/usr/bin/env python3
"""tiny-plan-small-scope: `new-milestone --tiny` — one compact plan (goal · Plan ·
Done-when) for small scope; member tasks default to the fast lane; observe defers
to milestone close; the trust floor (contract · red · gate) is unchanged.

Benchmark evidence (wm2/wm3): ADD is already 2-3x faster/cheaper on small scope —
the residual waste is the full MILESTONE.md scaffold, full-template member tasks,
and per-task observe ceremony.

Run:
    python3 -m unittest test_tiny_plan_small_scope -v
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"


def _run(cwd, *args):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=cwd,
                          capture_output=True, text=True, timeout=120)


class TinyPlanBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        r = _run(self.root, "init", "--name", "tp", "--stage", "mvp")
        assert r.returncode == 0, r.stderr + r.stdout

    def tearDown(self):
        self._tmp.cleanup()

    def _mfile(self, slug):
        return pathlib.Path(self.root) / ".add" / "milestones" / slug / "MILESTONE.md"


class TinyScaffold(TinyPlanBase):
    def test_tiny_scaffold_is_compact(self):
        # S1: --tiny writes goal + Plan + Done-when ONLY (no contracts scaffold)
        r = _run(self.root, "new-milestone", "quick-fixes", "--tiny",
                 "--goal", "polish CLI errors")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        t = self._mfile("quick-fixes").read_text()
        self.assertIn("## Plan", t)
        self.assertIn("## Done when", t)
        self.assertNotIn("## Shared / risky contracts", t,
                         "a tiny plan must not carry the full contracts scaffold")

    def test_tiny_flag_recorded_in_state(self):
        _run(self.root, "new-milestone", "quick-fixes", "--tiny", "--goal", "g")
        state = json.loads((pathlib.Path(self.root) / ".add" / "state.json").read_text())
        self.assertTrue(state["milestones"]["quick-fixes"].get("tiny"),
                        "state.json must record tiny=true")

    def test_non_tiny_unchanged(self):
        # S6: without --tiny the full scaffold (contracts section) still appears
        r = _run(self.root, "new-milestone", "normal-one", "--goal", "g")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("## Shared / risky contracts", self._mfile("normal-one").read_text())


class TinyConfirm(TinyPlanBase):
    def test_empty_plan_refused(self):
        # S5: unfilled tiny plan -> tiny_plan_unfilled
        _run(self.root, "new-milestone", "quick-fixes", "--tiny", "--goal", "g",
             "--await-confirm")
        r = _run(self.root, "milestone-confirm", "quick-fixes")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("tiny_plan_unfilled", r.stderr + r.stdout)

    def test_filled_plan_confirms_without_contracts(self):
        _run(self.root, "new-milestone", "quick-fixes", "--tiny", "--goal", "g",
             "--await-confirm")
        f = self._mfile("quick-fixes")
        t = f.read_text()
        t = t.replace("## Plan", "## Plan\n- [ ] fix-exit-codes — nonzero on error", 1)
        t = t.replace("## Done when", "## Done when\n- [ ] `add.py nope` exits 2", 1)
        f.write_text(t)
        r = _run(self.root, "milestone-confirm", "quick-fixes")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)


class TinyMemberTasks(TinyPlanBase):
    def _tiny_confirmed(self):
        _run(self.root, "new-milestone", "quick-fixes", "--tiny", "--goal", "g")
        f = self._mfile("quick-fixes")
        t = f.read_text()
        t = t.replace("## Plan", "## Plan\n- [ ] a — b", 1)
        t = t.replace("## Done when", "## Done when\n- [ ] c", 1)
        f.write_text(t)

    def test_member_task_defaults_to_fast_lane(self):
        # S2: no --fast flag needed under a tiny milestone
        self._tiny_confirmed()
        r = _run(self.root, "new-task", "fix-exit-codes", "--title", "t")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        body = (pathlib.Path(self.root) / ".add" / "tasks" / "fix-exit-codes"
                / "TASK.md").read_text()
        self.assertIn("fast", body.splitlines()[2].lower() + body[:400].lower(),
                      "tiny member task must scaffold the fast-lane template")

    def test_full_flag_opts_back(self):
        self._tiny_confirmed()
        r = _run(self.root, "new-task", "big-one", "--title", "t", "--full")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        body = (pathlib.Path(self.root) / ".add" / "tasks" / "big-one" / "TASK.md").read_text()
        self.assertIn("## 0", body, "--full must scaffold the full template (has §0 GROUND)")

    def test_security_sensitivity_forces_full(self):
        # S4/R6: base-class sensitivity overrides the tiny default
        self._tiny_confirmed()
        r = _run(self.root, "new-task", "patch-auth", "--title", "t",
                 "--sensitivity", "security")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        body = (pathlib.Path(self.root) / ".add" / "tasks" / "patch-auth" / "TASK.md").read_text()
        self.assertIn("## 0", body,
                      "a security-sensitive task in a tiny milestone gets the FULL template")


if __name__ == "__main__":
    unittest.main(verbosity=2)
