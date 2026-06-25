#!/usr/bin/env python3
"""Red/green tests for `add.py archive-milestone` — light, state-only collapse.

Archiving a DONE milestone removes it + its tasks from the active state.json and
appends a compact summary to state["archived"]; files on disk are untouched, and
an active/incomplete milestone is refused (no data loss). Backward-compatible via
.get defaults. Run: python3 -m unittest test_milestone_archive -v
"""
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
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


class MilestoneArchiveTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-archive-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------

    def _state_path(self) -> Path:
        return self.tmp / ".add" / "state.json"

    def _load(self) -> dict:
        return json.loads(self._state_path().read_text(encoding="utf-8"))

    def _capture(self, *argv) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(list(argv))
        return buf.getvalue()

    def _make_done_milestone(self, ms="m1", n=2) -> list[str]:
        add.main(["new-milestone", ms, "--title", "Milestone One"])
        members = []
        for i in range(n):
            t = f"{ms}-t{i}"
            add.main(["new-task", t, "--milestone", ms])
            add.main(["phase", "verify", t])        # escape hatch: scaffold to verify
            add.main(["gate", "PASS", t])           # gate PASS -> phase done -> _task_done
            members.append(t)
        _meet_exit_criteria(ms)      # v20 goal-gate: meet criteria before close
        add.main(["milestone-done", ms])             # status -> done
        return members

    # --- scenarios -----------------------------------------------------------

    def test_archive_collapses_state(self):
        members = self._make_done_milestone("m1", 2)
        add.main(["archive-milestone", "m1"])
        st = self._load()
        self.assertNotIn("m1", st.get("milestones", {}), "milestone must leave active state")
        for t in members:
            self.assertNotIn(t, st.get("tasks", {}), f"task {t} must leave active state")
        archived = st.get("archived", [])
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0]["slug"], "m1")
        self.assertEqual(archived[0]["tasks"], 2)

    def test_archive_keeps_files_on_disk(self):
        members = self._make_done_milestone("m1", 1)
        add.main(["archive-milestone", "m1"])
        self.assertTrue((self.tmp / ".add" / "milestones" / "m1" / "MILESTONE.md").exists(),
                        "light archive must keep the MILESTONE.md on disk")
        for t in members:
            self.assertTrue((self.tmp / ".add" / "tasks" / t / "TASK.md").exists(),
                            f"light archive must keep {t}/TASK.md on disk")

    def test_status_shows_archived_rollup(self):
        self._make_done_milestone("m1", 2)
        add.main(["archive-milestone", "m1"])
        out = self._capture("status")
        self.assertIn("archived: 1 milestone (2 tasks)", out)

    def test_archive_clears_active_pointers(self):
        self._make_done_milestone("m1", 2)          # active_milestone=m1, active_task=member
        add.main(["archive-milestone", "m1"])
        st = self._load()
        self.assertIsNone(st.get("active_milestone"), "archived milestone can't stay active")
        self.assertIsNone(st.get("active_task"), "archived task can't stay active")

    def test_archive_rejects_unknown(self):
        before = self._state_path().read_bytes()
        err = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stderr(err):
            add.main(["archive-milestone", "nope"])
        self.assertIn("unknown_milestone", err.getvalue(),
                      "must fail for the right reason, not a parse error")
        self.assertEqual(self._state_path().read_bytes(), before, "reject must not mutate state")

    def test_archive_rejects_not_done(self):
        add.main(["new-milestone", "m2", "--title", "Two"])
        add.main(["new-task", "m2-t0", "--milestone", "m2"])    # unfinished
        err = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stderr(err):
            add.main(["archive-milestone", "m2"])
        self.assertIn("milestone_not_done", err.getvalue(),
                      "an active milestone must be refused (no data loss)")
        st = self._load()
        self.assertIn("m2", st.get("milestones", {}), "refused milestone must remain")
        self.assertIn("m2-t0", st.get("tasks", {}), "its task must remain")

    # --- review-driven regression guards (v2 contract) -----------------------

    def test_archive_rejects_incomplete_member(self):
        # A new incomplete task attached to an already-done milestone makes the
        # `status==done` flag stale. Archiving must NOT silently delete it.
        self._make_done_milestone("m1", 1)
        add.main(["new-task", "late", "--milestone", "m1"])   # phase specify, not done
        before = self._state_path().read_bytes()
        err = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stderr(err):
            add.main(["archive-milestone", "m1"])
        self.assertIn("milestone_has_incomplete_tasks", err.getvalue(),
                      "must refuse to archive a milestone with a live incomplete task")
        st = self._load()
        self.assertIn("m1", st.get("milestones", {}), "refused: milestone stays")
        self.assertIn("late", st.get("tasks", {}), "the incomplete task must NOT be destroyed")
        self.assertEqual(self._state_path().read_bytes(), before,
                         "reject is pre-mutation: state.json byte-identical")

    def test_archive_preserves_non_member_active_task(self):
        # clearing active pointers must be conditional — a task from another
        # milestone that happens to be active must survive the archive.
        self._make_done_milestone("m1", 1)
        add.main(["new-milestone", "m2", "--title", "Two"])   # active_milestone -> m2
        add.main(["new-task", "t-m2", "--milestone", "m2"])   # active_task -> t-m2 (non-member of m1)
        add.main(["archive-milestone", "m1"])
        st = self._load()
        self.assertEqual(st.get("active_task"), "t-m2", "non-member active task must survive")
        self.assertEqual(st.get("active_milestone"), "m2", "non-member active milestone must survive")

    def test_archive_keeps_cross_milestone_dep_resolvable(self):
        # a task in m2 depends on a done task in m1; archiving m1 must NOT break
        # check (false "unknown task") or ready (false "blocked").
        add.main(["new-milestone", "m1", "--title", "M1"])
        add.main(["new-task", "auth", "--milestone", "m1"])
        add.main(["phase", "verify", "auth"])     # escape hatch: scaffold to verify
        add.main(["gate", "PASS", "auth"])
        _meet_exit_criteria("m1")    # v20 goal-gate: meet criteria before close
        add.main(["milestone-done", "m1"])
        add.main(["new-milestone", "m2", "--title", "M2"])
        add.main(["new-task", "transfer", "--milestone", "m2", "--depends-on", "auth"])
        add.main(["archive-milestone", "m1"])
        check_ok = True
        try:
            self._capture("check")
        except SystemExit:
            check_ok = False
        self.assertTrue(check_ok, "check must pass after archive (archived dep resolves)")
        self.assertIn("transfer", self._capture("ready"),
                      "a task whose only dep is archived/done must be ready")


if __name__ == "__main__":
    unittest.main(verbosity=2)
