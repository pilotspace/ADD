#!/usr/bin/env python3
"""extract-pure-leaves (engine-modularization 7/N) — the LAST two clean pure leaves:
`_task_done` (a pure state predicate) -> add_engine/predicates.py, and
`_load_state_for_json` (the --json state loader, deps all in io_state) -> add_engine/io_state.py.
Both moved verbatim into their rightful existing modules, re-exported as add.py globals.

After this the clean-leaf phase is COMPLETE; only the entangled giant regions remain.
Run: python3 -m unittest test_engine_extract_pure_leaves -v
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)


class ReexportTest(unittest.TestCase):
    def test_task_done_in_predicates_reexported(self):
        import add
        from add_engine import predicates
        self.assertTrue(hasattr(predicates, "_task_done"),
                        "predicates.py must define _task_done after the move")
        self.assertIs(add._task_done, predicates._task_done,
                      "leaf_drift: add._task_done is not the predicates object")
        # truth table preserved
        self.assertTrue(add._task_done({"phase": "done", "gate": "PASS"}))
        self.assertTrue(add._task_done({"phase": "done", "gate": "RISK-ACCEPTED"}))
        self.assertFalse(add._task_done({"phase": "done", "gate": "none"}),
                         "a bare `phase done` with no verdict must NOT count as done")
        self.assertFalse(add._task_done({"phase": "build", "gate": "PASS"}))

    def test_load_state_for_json_in_io_state_reexported(self):
        import add
        from add_engine import io_state
        self.assertTrue(hasattr(io_state, "_load_state_for_json"),
                        "io_state.py must define _load_state_for_json after the move")
        self.assertIs(add._load_state_for_json, io_state._load_state_for_json,
                      "leaf_drift: add._load_state_for_json is not the io_state object")

    def test_load_state_for_json_real_roundtrip(self):
        import add
        cwd = os.getcwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-leaf-")).resolve()
        try:
            os.chdir(tmp)
            buf = io.StringIO()
            from contextlib import redirect_stdout, redirect_stderr
            with redirect_stdout(buf), redirect_stderr(buf):
                add.main(["init", "--name", "demo"])
            root, state = add._load_state_for_json()
            self.assertEqual(root, add.find_root(tmp))
            self.assertIsInstance(state, dict)
            self.assertIn("active_milestones", state,
                          "the loader must forward-migrate to the multi-active schema")
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in ("_task_done", "_load_state_for_json"):
            self.assertNotIn(f"\ndef {name}(", src,
                             f"dead-code: add.py still defines {name}")


class NoCycleTest(unittest.TestCase):
    def test_modules_import_without_add(self):
        # importing the two leaf modules standalone must NOT require `add` (no cycle)
        code = ("import add_engine.predicates, add_engine.io_state; "
                "assert hasattr(add_engine.predicates, '_task_done'); "
                "assert hasattr(add_engine.io_state, '_load_state_for_json')")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0,
                         f"cycle/import error: {r.stderr.strip()}")


class PinTest(unittest.TestCase):
    def test_engine_md5_still_pins_add_py(self):
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must stay md5(add.py), re-aimed after the shrink")

    def test_pkg_digest_3tree(self):
        import engine_pin
        import engine_manifest
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != ENGINE_PKG_MD5")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src,
                             f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
