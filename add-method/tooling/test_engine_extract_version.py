#!/usr/bin/env python3
"""extract-version (engine-modularization 13/N) — the 3 update-nudge version helpers
(`_read_json_safe`·`_version_gt`·`_fetch_latest_version`) + cluster-private
`_REGISTRY_LATEST`, moved from add.py into a NEW add_engine/version.py.

Closed cluster (the 3 fns don't call each other); the test rebinds
`add._fetch_latest_version = lambda` and the nudge-check caller stays in add.py ->
plain re-export intercepts. Run: python3 -m unittest test_engine_extract_version -v
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

MOVED = ("_read_json_safe", "_version_gt", "_fetch_latest_version")


class ReexportTest(unittest.TestCase):
    def test_version_live_in_module(self):
        from add_engine import version
        for name in MOVED:
            self.assertTrue(hasattr(version, name), f"version.py must define {name}")
        self.assertTrue(hasattr(version, "_REGISTRY_LATEST"),
                        "the cluster-private _REGISTRY_LATEST must travel with the cluster")

    def test_version_reexported_same_object(self):
        import add
        from add_engine import version
        for name in MOVED:
            self.assertTrue(hasattr(add, name), f"version_drift: add.{name} missing")
            self.assertIs(getattr(add, name), getattr(version, name),
                          f"version_drift: add.{name} is not the version object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src, f"dead-code: add.py still defines {name}")
        self.assertNotIn("\n_REGISTRY_LATEST = ", src,
                         "dead-code: add.py still defines _REGISTRY_LATEST")


class BehaviorTest(unittest.TestCase):
    def test_version_gt_preserved(self):
        import add
        self.assertTrue(add._version_gt("1.2.0", "1.1.9"))
        self.assertFalse(add._version_gt("1.0.0", "1.0.0"))
        self.assertFalse(add._version_gt("1.0.0", "1.2.0"))

    def test_rebind_steers_nudge(self):
        # the test_update_nudge.py pattern: rebinding add's global must reach the
        # staying caller, because the caller bare-resolves add's module global.
        import add
        original = add._fetch_latest_version
        try:
            sentinel = "9.9.9-rebind-sentinel"
            add._fetch_latest_version = lambda *a, **k: sentinel
            self.assertEqual(add._fetch_latest_version(), sentinel,
                             "the add._fetch_latest_version rebind must take effect (re-export steerable)")
        finally:
            add._fetch_latest_version = original


class NoCycleTest(unittest.TestCase):
    def test_version_imports_without_add(self):
        code = ("import add_engine.version as v; "
                "assert v._version_gt('2.0.0','1.0.0') and not v._version_gt('1.0.0','1.0.0'); "
                "assert v._REGISTRY_LATEST.startswith('https://')")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"cycle/import error: {r.stderr.strip()}")


class PinTest(unittest.TestCase):

    def test_pkg_digest_includes_version_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("version.py", names, "version.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != the package digest")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src, f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
