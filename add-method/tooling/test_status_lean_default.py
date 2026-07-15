#!/usr/bin/env python3
"""Red/green for status-lean-default (frozen §3 v1).

Bare `add.py status` gets a LEAN default: the 5 big blocks (goal + m-goal prose,
the personas roster, the milestones list, the tasks list, the streams per-line
detail) move behind `--all`, each replaced by a one-line count/pointer. This is
GUARANTEED at the engine (an agent calling bare `status`, not `--brief`, still
gets a small output). `status --all` restores the full output; `--brief`/`--json`
/`--section` are unchanged.

Run: python3 -m unittest test_status_lean_default -v
"""
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

PERSONA_FM = "---\nslug: {s}\nflow: build\nvibe: a deliberate lean persona for the roster test\n---\nbody\n"


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-lean-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._run("init", "--name", "demo", "--stage", "mvp")
        self._run("lock")
        # two REAL personas so the roster block has a body to gate
        personas = self.tmp / ".add" / "personas"
        personas.mkdir(parents=True, exist_ok=True)
        for s in ("alpha-persona", "beta-persona"):
            (personas / f"{s}.md").write_text(PERSONA_FM.format(s=s))
        # two milestones + a couple tasks so the list/roster blocks are non-empty
        self._run("new-milestone", "m-one", "--title", "One", "--goal", "first goal")
        self._run("milestone-confirm", "m-one")
        self._run("new-task", "task-a", "--title", "A", "--milestone", "m-one")
        self._run("new-milestone", "m-two", "--title", "Two", "--goal", "second goal")
        self._run("milestone-confirm", "m-two")

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()

    def _status(self, *flags):
        return self._run("status", *flags)[1]


class LeanDefaultTest(_Harness):
    def test_bare_status_gates_persona_roster_body(self):
        bare = self._status()
        # the roster BODY (per-persona bullet) is gone; a count pointer stands
        self.assertNotIn("alpha-persona", bare, "persona roster body must gate behind --all")
        self.assertIn("status --all", bare, "a --all pointer must be present")

    def test_bare_status_gates_milestone_and_task_rows(self):
        bare = self._status()
        # milestone/task ROWS gone from the lean default (count line instead)
        self.assertNotIn("m-one", bare, "milestone rows must gate behind --all")
        self.assertNotIn("task-a", bare, "task rows must gate behind --all")

    def test_all_flag_restores_full_output(self):
        full = self._status("--all")
        # everything the lean default hid is present under --all
        self.assertIn("alpha-persona", full)
        self.assertIn("m-one", full)
        self.assertIn("task-a", full)

    def test_lean_is_smaller_than_all(self):
        self.assertLess(len(self._status()), len(self._status("--all")),
                        "the lean default must be strictly smaller than --all")

    def test_brief_unchanged(self):
        brief = self._status("--brief")
        self.assertLessEqual(brief.count("\n"), 3, "--brief stays the 2-line resume")
        self.assertNotIn("alpha-persona", brief)


if __name__ == "__main__":
    unittest.main()
