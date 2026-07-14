#!/usr/bin/env python3
"""Red/green tests for the init resume pointer (task init-resume-pointer, frozen v1
— SUPERSEDED by init-idempotent-nudge, call-residuals, frozen §3 v1):
the WM1 re-measure showed every rep re-running `init` on an already-initialised
project (+2–4 calls/rep). The message still names the resume command, but the
re-init is now an exit-0 NO-OP (was a nonzero refusal): a re-init should not cost
the agent a recovery call. It still writes nothing to the tree. `--force` still
resets. (The full new contract — incl. the status "do not re-init" line — is
pinned in test_init_idempotent_nudge.py.)

Run: python3 -m unittest test_init_resume_pointer -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-irp-")).resolve()
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


class ResumePointerTest(_Harness):
    def test_reinit_names_resume(self):                            # M1+M2 (superseded contract)
        out, code = self._run("init", "--name", "demo", "--stage", "mvp")
        self.assertEqual(code, 0, out)
        before = self._snapshot()
        out, code = self._run("init", "--name", "demo", "--stage", "mvp")
        self.assertEqual(code, 0, "a re-init is now an exit-0 no-op (init-idempotent-nudge)")
        self.assertIn("already initialised", out, "the existing message head survives")
        self.assertIn("resume: add.py status", out,
                      "the no-op must name the resume command")
        self.assertEqual(before, self._snapshot(),
                         "a no-op re-init must write nothing")

    def test_force_still_resets(self):                             # R1
        self._run("init", "--name", "demo", "--stage", "mvp")
        out, code = self._run("init", "--name", "demo", "--stage", "mvp", "--force")
        self.assertEqual(code, 0, f"--force must still reset: {out}")


if __name__ == "__main__":
    unittest.main()
