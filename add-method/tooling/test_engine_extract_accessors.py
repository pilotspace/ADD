#!/usr/bin/env python3
"""extract-accessors (engine-modularization 4/N) — the 6 PURE active-task/milestone
state-dict accessors (`_active_milestone`, `_active_task`, `_set_active_milestone`,
`_set_active_task`, `_activate_milestone`, `_deactivate_milestone`) moved from add.py
into a NEW add_engine/accessors.py, re-exported as add.py module globals.

AST-confirmed dependency-free (the only free name is `_active_milestone`, itself in
the move set). Unpatched pure dict ops. The full suite (multi-active / team-collab)
is the net for the real selection behavior.

Run: python3 -m unittest test_engine_extract_accessors -v
"""
import hashlib
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)

MOVED = ("_active_milestone", "_active_task", "_set_active_milestone",
         "_set_active_task", "_activate_milestone", "_deactivate_milestone")


class ReexportTest(unittest.TestCase):
    def test_accessors_live_in_module(self):
        from add_engine import accessors
        for name in MOVED:
            self.assertTrue(hasattr(accessors, name),
                            f"accessors.py must define {name} after the extraction")

    def test_accessors_reexported_same_object(self):
        import add
        from add_engine import accessors
        for name in MOVED:
            self.assertTrue(hasattr(add, name),
                            f"accessor_drift: add.{name} missing after the split")
            self.assertIs(getattr(add, name), getattr(accessors, name),
                          f"accessor_drift: add.{name} is not the accessors object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src,
                             f"dead-code: add.py still defines {name} (duplicate of accessors)")

    def test_accessors_module_is_a_pure_leaf(self):
        # no imports beyond __future__ — pure in-memory dict ops
        src = (TOOLING / "add_engine" / "accessors.py").read_text(encoding="utf-8")
        for forbidden in ("import os", "import sys", "import subprocess", "import json",
                          "from add_engine.io_state", "import add\n"):
            self.assertNotIn(forbidden, src,
                             f"accessors.py must stay a pure leaf — found {forbidden!r}")


class ActiveSelectionTest(unittest.TestCase):
    def test_active_milestone_and_task_track_through_cli(self):
        import add
        cwd = os.getcwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-acc-")).resolve()
        try:
            os.chdir(tmp)
            buf, err = io.StringIO(), io.StringIO()
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["init", "--name", "demo"])
                add.main(["new-task", "alpha", "--title", "Alpha"])
            root = add.find_root(tmp)
            state = add.load_state(root)
            self.assertEqual(add._active_task(state), "alpha",
                             "the moved accessor must report the just-created active task")
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)


class PinTest(unittest.TestCase):

    def test_pkg_digest_includes_accessors_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("accessors.py", names, "accessors.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != the package digest")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src,
                             f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
