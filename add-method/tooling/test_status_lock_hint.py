#!/usr/bin/env python3
"""Behavioral proof of the status unlocked->lock hint (task: status-lock-hint, v12-1).

CONTRACT (frozen @ v1): in the non-json `status` view, when the setup is present
but UNLOCKED (`not _setup_locked(state)`), the terminal guidance names
`.add/SETUP-REVIEW.md` and `add.py lock`, and the generic resume / first-run
"/add" hint is suppressed. When locked or grandfathered (no "setup" key) the
output is unchanged. `--json` is untouched.

RED driver: the two unlocked tests (no lock hint exists today). The two locked
tests are the behaviour-preserving safety net. Run:
  python3 -m unittest test_status_lock_hint -v
"""
import contextlib
import io
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add


def _run(argv):
    """Run add.main(argv), capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class StatusLockHintTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-status-lock-hint-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    # --- RED: unlocked states surface the lock hint --------------------------
    def test_unlocked_with_task_shows_lock_hint(self):
        add.main(["init", "--name", "demo", "--await-lock"])
        add.main(["new-task", "first", "--title", "First feature"])  # first task allowed pre-lock
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0)
        self.assertIn("SETUP-REVIEW.md", out, "unlocked status must name SETUP-REVIEW.md")
        self.assertIn("add.py lock", out, "unlocked status must name `add.py lock`")
        self.assertNotIn("start the next feature", out,
                         "generic resume hint must be suppressed while unlocked")
        self.assertNotIn("read .add/tasks/", out,
                         "generic resume hint must be suppressed while unlocked")

    def test_unlocked_no_tasks_shows_lock_hint(self):
        add.main(["init", "--name", "demo", "--await-lock"])
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0)
        self.assertIn("SETUP-REVIEW.md", out, "unlocked status (no tasks) must name SETUP-REVIEW.md")
        self.assertIn("add.py lock", out, "unlocked status (no tasks) must name `add.py lock`")
        self.assertNotIn("you're set up. In Claude Code", out,
                         "first-run /add panel must be suppressed while unlocked")

    # --- safety net: locked / grandfathered are unchanged --------------------
    def test_locked_shows_resume_not_lock_hint(self):
        add.main(["init", "--name", "demo", "--await-lock"])
        add.main(["lock", "--by", "Tin"])
        add.main(["new-task", "first", "--title", "First feature"])
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0)
        self.assertNotIn("SETUP-REVIEW.md", out,
                         "a locked project must NOT show the lock hint")

    def test_grandfathered_shows_resume_not_lock_hint(self):
        add.main(["init", "--name", "demo"])  # plain init -> no "setup" key (grandfathered-locked)
        add.main(["new-task", "first", "--title", "First feature"])
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0)
        self.assertNotIn("SETUP-REVIEW.md", out,
                         "a grandfathered project must NOT show the lock hint")


if __name__ == "__main__":
    unittest.main(verbosity=2)
