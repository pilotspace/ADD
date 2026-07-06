#!/usr/bin/env python3
"""Red/green tests for fastlane-intake-nudge — `new-task` (non-`--fast`) prints a one-line
advisory recommending the fast lane or a direct edit when a keyword heuristic on the title/slug
finds no RISK_KEYWORDS hit. Recommend-only: never blocks, never flips `fast`, never changes the
exit code or state.json shape. Mirrors the existing warn-never-block precedent (the "not attached
to a milestone" nudge) rather than replacing it.

Run: python3 -m unittest test_fastlane_intake_nudge -v
"""
from __future__ import annotations

import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


class FastlaneIntakeNudgeTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="addfastlanenudge-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._run("init", "--name", "demo")

    def tearDown(self):
        os.chdir(self._cwd)

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        with redirect_stdout(out), redirect_stderr(err):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code, out.getvalue(), err.getvalue()

    def test_trivial_title_gets_the_nudge(self):
        code, out, _ = self._run("new-task", "fix-typo-banner", "--title", "fix typo in banner")
        self.assertEqual(code, 0)
        low = out.lower()
        self.assertIn("--fast", low, f"expected a --fast recommendation, got: {out!r}")
        self.assertIn("recommend", low, f"expected the print to disclose it is a recommendation, got: {out!r}")
        state = add.load_state(add.find_root())
        self.assertNotIn("fast", state["tasks"]["fix-typo-banner"],
                          "the nudge must never flip the task's own fast marker")

    def test_risk_keyword_title_suppresses_the_nudge(self):
        code, out, _ = self._run("new-task", "auth-migration", "--title", "migrate auth schema")
        self.assertEqual(code, 0)
        self.assertNotIn("--fast", out.lower(),
                         f"a risk-keyword title must NOT get the fast-lane nudge, got: {out!r}")

    def test_fast_flag_suppresses_the_nudge_even_for_a_trivial_title(self):
        code, out, _ = self._run(
            "new-task", "fix-typo-banner-2", "--fast", "--title", "fix typo in banner")
        self.assertEqual(code, 0)
        self.assertNotIn("recommend", out.lower(),
                         f"a task already created with --fast must not also get the nudge, got: {out!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
