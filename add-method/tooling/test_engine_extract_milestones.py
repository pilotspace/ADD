#!/usr/bin/env python3
"""extract-milestones (engine-modularization 10/N) — the 7 milestone-doc reader fns
(`_has_production_roadmap`·`_project_goal`·`_milestone_doc`·`_exit_criteria`·
`_exit_criteria_cited`·`_stage_criteria`·`_all_milestones_done`) + the cluster-private
`_VERIFY_CITE_RE`, moved from add.py into a NEW add_engine/milestones.py.

Closed cluster (transitive-closure AST = zero outbound), none patched -> plain re-export.
Run: python3 -m unittest test_engine_extract_milestones -v
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)

MOVED = ("_has_production_roadmap", "_project_goal", "_milestone_doc", "_exit_criteria",
         "_exit_criteria_cited", "_stage_criteria", "_all_milestones_done")


class ReexportTest(unittest.TestCase):
    def test_milestones_live_in_module(self):
        from add_engine import milestones
        for name in MOVED:
            self.assertTrue(hasattr(milestones, name), f"milestones.py must define {name}")
        self.assertTrue(hasattr(milestones, "_VERIFY_CITE_RE"),
                        "the cluster-private _VERIFY_CITE_RE must travel with the cluster")

    def test_milestones_reexported_same_object(self):
        import add
        from add_engine import milestones
        for name in MOVED:
            self.assertTrue(hasattr(add, name), f"milestone_drift: add.{name} missing")
            self.assertIs(getattr(add, name), getattr(milestones, name),
                          f"milestone_drift: add.{name} is not the milestones object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src, f"dead-code: add.py still defines {name}")
        self.assertNotIn("\n_VERIFY_CITE_RE = ", src,
                         "dead-code: add.py still defines _VERIFY_CITE_RE")


class ReadsPreservedTest(unittest.TestCase):
    def test_exit_criteria_and_goal(self):
        import add
        cwd = os.getcwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-ms-")).resolve()
        try:
            os.chdir(tmp)
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                add.main(["init", "--name", "demo"])
            root = add.find_root(tmp)
            # the default mvp milestone exists; exit-criteria returns a (cited, total) pair
            done, total = add._exit_criteria(root, "mvp")
            self.assertIsInstance(done, int)
            self.assertIsInstance(total, int)
            self.assertGreaterEqual(total, done)
            # _all_milestones_done reads state and returns a bool
            self.assertIsInstance(add._all_milestones_done(add.load_state(root)), bool)
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)


class NoCycleTest(unittest.TestCase):
    def test_milestones_imports_without_add(self):
        code = ("import add_engine.milestones as m; "
                "assert all(hasattr(m, n) for n in "
                "['_project_goal','_exit_criteria','_all_milestones_done','_VERIFY_CITE_RE'])")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"cycle/import error: {r.stderr.strip()}")


class PinTest(unittest.TestCase):
    def test_engine_md5_still_pins_add_py(self):
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must stay md5(add.py), re-aimed after the shrink")

    def test_pkg_digest_includes_milestones_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("milestones.py", names, "milestones.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != ENGINE_PKG_MD5")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src, f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
