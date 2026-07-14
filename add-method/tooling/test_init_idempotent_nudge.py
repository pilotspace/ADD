#!/usr/bin/env python3
"""Red/green tests for init-idempotent-nudge (call-residuals, frozen §3 v1):
the WM1 re-measure showed every rep re-running `init` on an already-initialised
project (+2–4 calls/rep — the double-init lever). This task makes the repeat a
LOUD NO-OP: exit 0, print the resume pointer, write nothing — and makes `status`
open with a "do not re-init" line so the agent never re-calls init in the first
place. Supersedes init-resume-pointer v1 (which kept it a nonzero refusal).

Run: python3 -m unittest test_init_idempotent_nudge -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-iin-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _snapshot(self):
        return {p: p.read_bytes() for p in (self.tmp / ".add").rglob("*") if p.is_file()}


class ReinitNoopTest(_Harness):
    def test_reinit_is_exit0_noop_resume(self):
        out, code = self._run("init", "--name", "demo", "--stage", "mvp")
        self.assertEqual(code, 0, out)
        before = self._snapshot()
        out, code = self._run("init", "--name", "demo", "--stage", "mvp")
        self.assertEqual(code, 0, f"a re-init must be an exit-0 no-op now: {out}")
        self.assertIn("already initialised", out, "the existing message head survives")
        self.assertIn("resume: add.py status", out, "the no-op must name the resume command")
        self.assertEqual(before, self._snapshot(),
                         "a no-op re-init must write nothing under .add/")

    def test_force_still_resets(self):
        self._run("init", "--name", "demo", "--stage", "mvp")
        out, code = self._run("init", "--name", "demo", "--stage", "mvp", "--force")
        self.assertEqual(code, 0, f"--force must still reset: {out}")

    def test_fresh_init_still_seeds(self):
        out, code = self._run("init", "--name", "demo", "--stage", "mvp")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.tmp / ".add" / "state.json").exists(),
                        "a fresh init must still seed state.json")


class StatusDoNotInitTest(_Harness):
    def test_status_opens_with_do_not_init_when_project_exists(self):
        self._run("init", "--name", "demo", "--stage", "mvp")
        out, code = self._run("status")
        self.assertEqual(code, 0, out)
        self.assertIn("do not re-init", out,
                      "status must tell the agent the project exists — do not re-init")

    def test_status_no_project_is_unchanged(self):
        out, code = self._run("status")
        self.assertNotIn("do not re-init", out,
                         "the do-not-init line must only appear when a project exists")


if __name__ == "__main__":
    unittest.main()
