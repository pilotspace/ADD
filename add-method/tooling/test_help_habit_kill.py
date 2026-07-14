#!/usr/bin/env python3
"""Red/green tests for help-habit-kill (call-residuals, frozen §3 v1):
a mistyped top-level command makes argparse dump the full 50-choice usage — unreadable
at a glance, so the agent's reflex is `--help` or a re-read (the measured 1/rep lever).
This intercepts ONLY that case (top-level `prog == "add.py"` invalid-choice) with a
concise "unknown command 'X' — did you mean '<near>'?" + a pointer to `add.py status`.
Every other parse error (missing slug, a subcommand's own invalid choice) keeps
argparse's default behaviour.

Run: python3 -m unittest test_help_habit_kill -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-hhk-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._run("init", "--name", "demo", "--stage", "mvp")

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()


class UnknownCommandTest(_Harness):
    def test_close_match_suggested_and_status_pointer(self):
        code, out, err = self._run("statuss")
        blob = out + err
        self.assertEqual(code, 2, "an unknown command still exits 2")
        self.assertIn("unknown command 'statuss'", blob)
        self.assertIn("did you mean 'status'?", blob, "the closest command must be suggested")
        self.assertIn("add.py status", blob, "a resume pointer to status must be present")

    def test_no_choices_dump_and_no_help_mention(self):
        code, out, err = self._run("statuss")
        blob = out + err
        self.assertNotIn("invalid choice", blob, "the raw argparse invalid-choice text must be gone")
        self.assertNotIn("--help", blob, "no surface may tell the agent to run --help")
        # the 50-choice dump lists many commands comma-separated; a concise error names few.
        self.assertNotIn("graduation-report", blob, "the full choices dump must not print")

    def test_no_near_match_still_points_to_status(self):
        code, out, err = self._run("zzqqxx")
        blob = out + err
        self.assertEqual(code, 2)
        self.assertIn("unknown command 'zzqqxx'", blob)
        self.assertNotIn("did you mean", blob, "no suggestion when nothing is close")
        self.assertIn("add.py status", blob, "still points to status")

    def test_valid_command_unaffected(self):
        code, out, err = self._run("status", "--brief")
        self.assertIn(code, (None, 0), "a valid command exits cleanly")
        self.assertNotIn("unknown command", out + err, "a valid command is never flagged as unknown")


if __name__ == "__main__":
    unittest.main()
