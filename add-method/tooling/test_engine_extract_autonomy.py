#!/usr/bin/env python3
"""extract-autonomy (engine-modularization 16/N, the LAST clean cluster) — the 4
autonomy-level resolver fns (`_autonomy_level`·`_effective_autonomy`·`_project_autonomy`·
`_project_autonomy_token`) + cluster-private `_AUTONOMY_LINE_RE`, moved from add.py into a
NEW add_engine/autonomy.py. The SHARED `_AUTONOMY_LEVELS` relocates to constants.py.

Closed cluster (transitive-closure AST = zero outbound), none patched -> plain re-export.
Run: python3 -m unittest test_engine_extract_autonomy -v
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

MOVED = ("_autonomy_level", "_effective_autonomy", "_project_autonomy", "_project_autonomy_token")


class ReexportTest(unittest.TestCase):
    def test_autonomy_live_in_module(self):
        from add_engine import autonomy
        for name in MOVED:
            self.assertTrue(hasattr(autonomy, name), f"autonomy.py must define {name}")
        self.assertTrue(hasattr(autonomy, "_AUTONOMY_LINE_RE"),
                        "the cluster-private _AUTONOMY_LINE_RE must travel with the cluster")

    def test_autonomy_reexported_same_object(self):
        import add
        from add_engine import autonomy
        for name in MOVED:
            self.assertTrue(hasattr(add, name), f"autonomy_drift: add.{name} missing")
            self.assertIs(getattr(add, name), getattr(autonomy, name),
                          f"autonomy_drift: add.{name} is not the autonomy object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src, f"dead-code: add.py still defines {name}")
        self.assertNotIn("\n_AUTONOMY_LINE_RE = ", src,
                         "dead-code: add.py still defines _AUTONOMY_LINE_RE")
        self.assertNotIn("\n_AUTONOMY_LEVELS = ", src,
                         "dead-code: add.py still defines _AUTONOMY_LEVELS (moved to constants)")


class SharedLevelsTest(unittest.TestCase):
    def test_levels_relocated_to_constants(self):
        from add_engine import constants
        self.assertEqual(constants._AUTONOMY_LEVELS, ("manual", "conservative", "auto"),
                         "_AUTONOMY_LEVELS must live in constants.py as the single source")

    def test_levels_resolve_on_both_sides(self):
        import add
        from add_engine import constants, autonomy
        self.assertIs(add._AUTONOMY_LEVELS, constants._AUTONOMY_LEVELS,
                      "add._AUTONOMY_LEVELS must resolve to the constants object (staying side)")
        self.assertIs(autonomy._AUTONOMY_LEVELS, constants._AUTONOMY_LEVELS)

    def test_order_stays_in_add(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        self.assertIn("_AUTONOMY_ORDER", src,
                      "_AUTONOMY_ORDER must stay in add.py (it consumes the relocated _AUTONOMY_LEVELS)")


class BehaviorTest(unittest.TestCase):
    def test_autonomy_level_reads_declared_token(self):
        import add
        self.assertEqual(add._autonomy_level("autonomy: conservative"), "conservative")
        self.assertEqual(add._autonomy_level("autonomy: auto"), "auto")
        # documented contract: no `autonomy:` line -> None (UNSET); a REAL token
        # outside the set -> "?" (unknown). Behaviour preserved verbatim by the move.
        self.assertIsNone(add._autonomy_level("no autonomy line here"))
        self.assertEqual(add._autonomy_level("autonomy: boguslevel"), "?")


class NoCycleTest(unittest.TestCase):
    def test_autonomy_imports_without_add(self):
        code = ("import add_engine.autonomy as a; "
                "assert a._autonomy_level('autonomy: manual') == 'manual'; "
                "assert a._AUTONOMY_LEVELS[0] == 'manual'")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"cycle/import error: {r.stderr.strip()}")


class PinTest(unittest.TestCase):
    def test_engine_md5_still_pins_add_py(self):
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must stay md5(add.py), re-aimed after the shrink")

    def test_pkg_digest_includes_autonomy_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("autonomy.py", names, "autonomy.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != ENGINE_PKG_MD5")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src, f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
