#!/usr/bin/env python3
"""Red/green tests for project-goal (v20) — an explicit project GOAL in the
foundation, surfaced by `status` (with the active milestone's goal) and `guide`.

GOAL is read LIVE from PROJECT.md / MILESTONE.md (never copied into state.json);
a missing source degrades to a named sentinel and the command STILL exits 0 —
orientation never crashes. Run: python3 -m unittest test_project_goal -v
"""
import io
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add

GOAL_LINE = "ship ADD as a product, less doc-time than GSD"


class ProjectGoalTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-project-goal-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])              # grandfathered-locked (no setup key)
        self.add_dir = self.tmp / ".add"
        self.project_md = self.add_dir / "PROJECT.md"

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------
    def _set_goal(self, value: str) -> None:
        """Put exactly one top-level `goal:` line just after the slug line."""
        lines = [l for l in self.project_md.read_text(encoding="utf-8").splitlines()
                 if not l.startswith("goal:")]
        out, inserted = [], False
        for line in lines:
            out.append(line)
            if not inserted and line.startswith("slug:"):
                out.append(f"goal: {value}")
                inserted = True
        if not inserted:
            out.insert(0, f"goal: {value}")
        self.project_md.write_text("\n".join(out) + "\n", encoding="utf-8")

    def _strip_goal(self) -> None:
        lines = [l for l in self.project_md.read_text(encoding="utf-8").splitlines()
                 if not l.startswith("goal:")]
        self.project_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _status(self, *args) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["status", *args])
        return buf.getvalue()

    def _guide(self, *args) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["guide", *args])
        return buf.getvalue()

    # --- helper: _project_goal ----------------------------------------------
    def test_project_goal_reads_first_line(self):
        self._set_goal(GOAL_LINE)
        self.assertEqual(add._project_goal(self.add_dir), GOAL_LINE)

    def test_project_goal_unset_sentinel(self):
        self._strip_goal()
        self.assertEqual(add._project_goal(self.add_dir), add.GOAL_UNSET)

    # --- status surfaces -----------------------------------------------------
    def test_status_prints_project_goal(self):
        self._set_goal(GOAL_LINE)
        add.main(["new-task", "feat-a", "--title", "Feat A"])
        out = self._status()
        self.assertIn(GOAL_LINE, out)
        self.assertIn("project :", out)            # additive — existing lines untouched
        self.assertIn("stage   :", out)
        self.assertIn("active  :", out)

    def test_status_prints_active_milestone_goal(self):
        self._set_goal(GOAL_LINE)
        add.main(["new-milestone", "v1", "--goal", "deepen verify"])
        add.main(["new-task", "feat-a", "--milestone", "v1"])
        out = self._status()
        self.assertIn("deepen verify", out)        # the active milestone goal renders
        self.assertIn("v1", out)                    # attributed to its slug
        self.assertIn(GOAL_LINE, out)               # project GOAL still present (both together)

    def test_guide_prints_project_goal(self):
        self._set_goal(GOAL_LINE)
        add.main(["new-task", "feat-a"])
        out = self._guide()
        self.assertIn(GOAL_LINE, out)
        self.assertIn("active :", out)             # additive — existing guide lines untouched
        self.assertIn("next   :", out)
        self.assertIn("read   :", out)

    # --- reject render states (never blank, never crash, exit 0) -------------
    def test_status_goal_unset_hint_not_blank(self):
        self._strip_goal()
        add.main(["new-task", "feat-a"])
        out = self._status()
        self.assertIn("(unset", out)                                   # the hint, not a blank
        self.assertIn("add a 'goal:' line to PROJECT.md", out)         # actionable
        self.assertIn("active  :", out)                                # rest of status still printed

    def test_status_milestone_goal_unreadable(self):
        self._set_goal(GOAL_LINE)
        add.main(["new-milestone", "v1", "--goal", "deepen verify"])
        add.main(["new-task", "feat-a", "--milestone", "v1"])
        (self.add_dir / "milestones" / "v1" / "MILESTONE.md").unlink()  # goal source gone
        out = self._status()
        self.assertIn("(unknown)", out)             # m-goal degrades gracefully
        self.assertIn(GOAL_LINE, out)               # project GOAL still prints (one source never blanks the other)

    # --- prose surfaces ------------------------------------------------------
    def test_glossary_defines_goal(self):
        glossary = (self.add_dir / "GLOSSARY.md").read_text(encoding="utf-8")
        goal_lines = [l for l in glossary.splitlines() if l.startswith("GOAL:")]
        self.assertTrue(goal_lines, "GLOSSARY must define a GOAL term")
        self.assertIn("outcome", goal_lines[0].lower())        # GOAL = a durable outcome
        self.assertIn("Must", goal_lines[0])                   # distinguished from a task §1 Must

    def test_project_template_has_goal_line(self):
        text = self.project_md.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?im)^goal:")     # the scaffold carries a goal line
        self.assertIn("Domain (DDD)", text)        # existing foundation sections intact
        self.assertIn("Spec", text)
        self.assertIn("UDD", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
