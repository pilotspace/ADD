#!/usr/bin/env python3
"""Behavioral proof of the v3 ship-clean residuals (task: ship-clean).

Two independent concerns, frozen @ v1:
  (A) add-method/package.json has a `prepublishOnly` hook that RUNS the manifest guard
      (test_packaging), so `npm publish` from a dirty/incomplete tree is blocked. Proven by
      WIRING linkage (the hook is run as a subprocess and asserted to execute the guard +
      exit 0) — the strongest npm-free proof; it reds on broken/misspelled wiring.
  (B) `add.py project` prints .add/PROJECT.md (read-first foundation), read-only, and fails
      closed (non-zero + stderr) when the foundation is missing.
One test per SCENARIO. Run: python3 -m unittest test_ship_clean -v
"""
import contextlib
import io
import json
import os
import re
import shlex
import subprocess
import tempfile
import shutil
import unittest
from pathlib import Path

import add

PKG_ROOT = Path(__file__).resolve().parent.parent      # add-method/ (holds package.json)
_HOOK_TIMEOUT = 180                                    # design-for-failure: never hang the suite


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


# --- Concern A: prepublishOnly wired to the manifest guard ---------------------
class PrepublishGuardTest(unittest.TestCase):
    def _prepublish_cmd(self) -> str:
        pkg = json.loads((PKG_ROOT / "package.json").read_text(encoding="utf-8"))
        return (pkg.get("scripts") or {}).get("prepublishOnly")

    def test_prepublish_hook_wired_to_manifest_guard(self):
        cmd = self._prepublish_cmd()
        self.assertIsNotNone(cmd, "package.json scripts.prepublishOnly is missing")
        self.assertIn("test_packaging", cmd,
                      f"prepublishOnly must run the manifest guard (test_packaging); got: {cmd!r}")

    def test_prepublish_hook_runs_the_guard(self):
        # behavioral: run the CONFIGURED hook command; it must actually execute the manifest
        # guard and pass on the clean tree. Reds if the command points at no real test.
        cmd = self._prepublish_cmd()
        self.assertIsNotNone(cmd, "package.json scripts.prepublishOnly is missing")
        proc = subprocess.run(shlex.split(cmd), cwd=PKG_ROOT,
                              capture_output=True, text=True, timeout=_HOOK_TIMEOUT)
        combined = proc.stdout + proc.stderr
        self.assertRegex(combined, r"Ran [1-9]",
                         f"the hook ran no manifest tests (misspelled pattern?):\n{combined}")
        self.assertEqual(proc.returncode, 0,
                         f"the manifest guard must pass on the clean tree:\n{combined}")


# --- Concern B: add.py project prints the foundation ---------------------------
class ProjectCmdTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-ship-clean-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = add.find_root()

    def tearDown(self):
        os.chdir(self._cwd)

    def test_project_prints_foundation(self):
        foundation = (self.root / "PROJECT.md").read_text(encoding="utf-8")
        state_before = (self.root / "state.json").read_text(encoding="utf-8")
        code, out, _ = _run(["project"])
        self.assertEqual(code, 0, "project must exit 0 when the foundation exists")
        self.assertIn(foundation.strip(), out,
                      "project must print the full PROJECT.md foundation")
        self.assertEqual((self.root / "state.json").read_text(encoding="utf-8"),
                         state_before, "project is read-only — state.json must be unchanged")

    def test_project_missing_foundation_fails_closed(self):
        (self.root / "PROJECT.md").unlink()
        state_before = (self.root / "state.json").read_text(encoding="utf-8")
        code, out, err = _run(["project"])
        self.assertNotEqual(code, 0, "missing foundation must fail closed (non-zero exit)")
        self.assertIn("PROJECT.md", err, "the error must name the missing foundation file")
        self.assertEqual(out, "", "nothing should be printed to stdout on the error path")
        self.assertEqual((self.root / "state.json").read_text(encoding="utf-8"),
                         state_before, "the error path must not write to disk")


if __name__ == "__main__":
    unittest.main(verbosity=2)
