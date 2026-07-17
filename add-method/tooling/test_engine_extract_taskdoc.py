#!/usr/bin/env python3
"""extract-taskdoc (engine-modularization 15/N) — the 11 PLAN.md structural-reader fns
moved from add.py into a NEW add_engine/taskdoc.py, with the 3 SHARED delta regexes
(`_DELTA_RE`·`_EVIDENCE_RE`·`_SPEC_DELTA_RE`) relocated to constants.py (single source for
the moved readers AND the staying deltas-web lint).

Closed cluster (transitive-closure AST = zero outbound), none patched -> plain re-export.
Run: python3 -m unittest test_engine_extract_taskdoc -v
"""
import hashlib
import subprocess
import sys
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

MOVED = ("_task_header", "_count_test_defs", "_primary_test_files", "_tests_count",
         "_declared_test_files", "_declared_tests_count", "_tests_info", "_task_prose",
         "_phase_spans", "_raw_phase_bodies", "_spec_delta_entries")

REGEXES = ("_DELTA_RE", "_EVIDENCE_RE", "_SPEC_DELTA_RE")


class ReexportTest(unittest.TestCase):
    def test_taskdoc_live_in_module(self):
        from add_engine import taskdoc
        for name in MOVED:
            self.assertTrue(hasattr(taskdoc, name), f"taskdoc.py must define {name}")

    def test_taskdoc_reexported_same_object(self):
        import add
        from add_engine import taskdoc
        for name in MOVED:
            self.assertTrue(hasattr(add, name), f"taskdoc_drift: add.{name} missing")
            self.assertIs(getattr(add, name), getattr(taskdoc, name),
                          f"taskdoc_drift: add.{name} is not the taskdoc object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src, f"dead-code: add.py still defines {name}")
        for rx in REGEXES:
            self.assertNotIn(f"\n{rx} = re.compile", src,
                             f"dead-code: add.py still defines the relocated {rx}")


class SharedRegexTest(unittest.TestCase):
    def test_regexes_relocated_to_constants(self):
        from add_engine import constants
        for rx in REGEXES:
            self.assertTrue(hasattr(constants, rx),
                            f"the SHARED {rx} must live in constants.py (single source)")

    def test_regexes_resolve_on_both_sides(self):
        import add
        from add_engine import constants, taskdoc
        for rx in REGEXES:
            # the staying deltas-web lint resolves them via add's _-import
            self.assertIs(getattr(add, rx), getattr(constants, rx),
                          f"add.{rx} must resolve to the constants object (staying lint side)")
        # the moved reader resolves them via taskdoc's own import
        self.assertIs(taskdoc._DELTA_RE, constants._DELTA_RE)

    def test_siblings_kept_in_add(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for sib in ("_SPEC_STATUSES", "_STATUS_SETS", "_TAG_BROAD_RE"):
            self.assertIn(f"{sib} =", src,
                          f"the interleaved sibling {sib} must stay in add.py (deltas-web only)")


class NoCycleTest(unittest.TestCase):
    def test_taskdoc_imports_without_add(self):
        code = ("import add_engine.taskdoc as t; "
                "assert all(hasattr(t, n) for n in "
                "['_task_prose','_phase_spans','_spec_delta_entries','_tests_info'])")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"cycle/import error: {r.stderr.strip()}")


class PinTest(unittest.TestCase):

    def test_pkg_digest_includes_taskdoc_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("taskdoc.py", names, "taskdoc.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != the package digest")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src, f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
