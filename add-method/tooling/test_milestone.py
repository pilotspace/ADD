#!/usr/bin/env python3
"""Red/green tests for the milestone (SDD) tier + dependency ordering.
Run: python3 -m unittest test_milestone -v
"""
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout
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


class MilestoneTierTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-ms-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _run_capture(self, *argv) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(list(argv))
        return buf.getvalue()

    def test_new_milestone_scaffolds_and_activates(self):
        add.main(["new-milestone", "mvp", "--goal", "core money movement", "--stage", "mvp"])
        self.assertTrue((Path(self.tmp) / ".add" / "milestones" / "mvp" / "MILESTONE.md").exists())
        st = self._state()
        self.assertEqual(st["active_milestone"], "mvp")
        self.assertIn("mvp", st["milestones"])

    def test_new_task_links_milestone_and_deps(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", "transfer", "--depends-on", "accounts,login"])
        t = self._state()["tasks"]["transfer"]
        self.assertEqual(t["milestone"], "mvp")
        self.assertEqual(t["depends_on"], ["accounts", "login"])

    def test_ready_lists_only_unblocked(self):
        add.main(["new-task", "a"])
        add.main(["phase", "verify", "a"])        # escape hatch: scaffold to verify
        add.main(["gate", "PASS", "a"])           # a is done
        add.main(["new-task", "b", "--depends-on", "a"])
        add.main(["new-task", "c", "--depends-on", "b"])
        out = self._run_capture("ready")
        listed = set(out.split())
        self.assertIn("b", listed)        # b's only dep (a) is done -> ready
        self.assertNotIn("c", listed)     # c blocked by unfinished b
        self.assertNotIn("a", listed)     # a is done -> not listed

    def test_milestone_done_blocks_incomplete(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", "t"])               # not done
        with self.assertRaises(SystemExit) as cm:
            add.main(["milestone-done", "mvp"])
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(self._state()["milestones"]["mvp"]["status"], "active")

    def test_milestone_done_passes_when_all_done(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", "t"])
        add.main(["phase", "verify", "t"])        # escape hatch: scaffold to verify
        add.main(["gate", "PASS", "t"])
        _meet_exit_criteria("mvp")   # v20 goal-gate: meet criteria before close
        add.main(["milestone-done", "mvp"])
        self.assertEqual(self._state()["milestones"]["mvp"]["status"], "done")

    def test_check_detects_cycle(self):
        add.main(["new-task", "a"])
        add.main(["new-task", "b", "--depends-on", "a"])
        # introduce a cycle a -> b -> a directly in state
        st = self._state()
        st["tasks"]["a"]["depends_on"] = ["b"]
        (Path(self.tmp) / ".add" / "state.json").write_text(json.dumps(st))
        with self.assertRaises(SystemExit) as cm:
            add.main(["check"])
        self.assertEqual(cm.exception.code, 1)

    def test_new_task_unknown_milestone_rejected(self):
        with self.assertRaises(SystemExit) as cm:
            add.main(["new-task", "x", "--milestone", "ghost"])
        self.assertEqual(cm.exception.code, 1)
        self.assertNotIn("x", self._state()["tasks"])

    def test_backward_compat_old_state_still_loads(self):
        # craft a pre-milestone state: no milestones/active_milestone, task w/o new fields
        sp = Path(self.tmp) / ".add" / "state.json"
        st = json.loads(sp.read_text())
        st.pop("milestones", None)
        st.pop("active_milestone", None)
        st["tasks"]["legacy"] = {"title": "Legacy", "phase": "specify", "gate": "none"}
        (Path(self.tmp) / ".add" / "tasks" / "legacy").mkdir(parents=True, exist_ok=True)
        (Path(self.tmp) / ".add" / "tasks" / "legacy" / "TASK.md").write_text("phase: specify\n")
        sp.write_text(json.dumps(st))
        # status and check must not crash on a minimal, old-style task
        self._run_capture("status")
        self._run_capture("check")

    # --- set-milestone (attach/move/detach an existing task) ---
    def test_set_milestone_attaches(self):
        add.main(["new-task", "t"])               # created before any milestone -> milestone=None
        self.assertIsNone(self._state()["tasks"]["t"]["milestone"])
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["set-milestone", "t", "mvp"])
        self.assertEqual(self._state()["tasks"]["t"]["milestone"], "mvp")

    def test_set_milestone_none_detaches(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", "t"])               # auto-linked to active milestone mvp
        add.main(["set-milestone", "t", "none"])
        self.assertIsNone(self._state()["tasks"]["t"]["milestone"])

    def test_set_milestone_unknown_task_rejected(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        with self.assertRaises(SystemExit) as cm:
            add.main(["set-milestone", "ghost", "mvp"])
        self.assertEqual(cm.exception.code, 1)

    def test_set_milestone_unknown_milestone_rejected(self):
        add.main(["new-task", "t"])
        before = self._state()["tasks"]["t"].get("milestone")
        with self.assertRaises(SystemExit) as cm:
            add.main(["set-milestone", "t", "ghost"])
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(self._state()["tasks"]["t"].get("milestone"), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
