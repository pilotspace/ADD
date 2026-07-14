#!/usr/bin/env python3
"""Red/green for status-ancestor-warn (orientation-honesty, frozen §3 v1).

`status` run in a dir with no local .add/ but an ANCESTOR project above prints a
one-line stderr note naming the resolved ancestor + the exact `init` command to
scope a project here — so a nested agent stops spelunking "why is the project the
parent's?". A cwd that owns its own project stays silent.

Run: python3 -m unittest test_status_ancestor_warn -v
"""
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.A = Path(tempfile.mkdtemp(prefix="add-anc-")).resolve()
        self.addCleanup(shutil.rmtree, self.A, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.A)
        self._run("init", "--name", "parent-proj", "--stage", "mvp")

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()


class AncestorNoteTest(_Harness):
    def test_nested_dir_prints_ancestor_note(self):
        work = self.A / "work"
        work.mkdir()
        os.chdir(work)
        code, out, err = self._run("status")
        self.assertIn(code, (None, 0), "status still exits cleanly")
        self.assertIn("ancestor project", err, "must name the resolved ancestor project")
        self.assertIn(str(self.A), err, "must print the resolved ancestor path")
        self.assertIn("add.py init --name", err, "must hand the exact init command to scope here")
        self.assertTrue(out.strip(), "the normal status body still prints on stdout")

    def test_cwd_owned_project_is_silent(self):
        # at A itself (owns .add/state.json) -> no ancestor note
        code, out, err = self._run("status")
        self.assertNotIn("ancestor project", err, "a cwd that owns a project emits no note")

    def test_note_goes_to_stderr_not_stdout(self):
        work = self.A / "work"
        work.mkdir()
        os.chdir(work)
        code, out, err = self._run("status")
        self.assertNotIn("ancestor project", out, "the note must not pollute stdout")


if __name__ == "__main__":
    unittest.main()
