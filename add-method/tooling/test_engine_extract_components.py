#!/usr/bin/env python3
"""extract-components (engine-modularization 11/N) — the 7 component/federation reader
fns (`_confined`·`_components`·`_cite_region`·`_contracts`·`_federation`·
`_contract_snapshot`·`_in_scope`) moved from add.py into a NEW add_engine/components.py.

Closed cluster (transitive-closure AST = zero outbound), none patched -> plain re-export.
components.py replicates add.py's degrade-safe `tomllib` guard (py3.10 import safety).
Run: python3 -m unittest test_engine_extract_components -v
"""
import hashlib
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

MOVED = ("_confined", "_components", "_cite_region", "_contracts",
         "_federation", "_contract_snapshot", "_in_scope")


class ReexportTest(unittest.TestCase):
    def test_components_live_in_module(self):
        from add_engine import components
        for name in MOVED:
            self.assertTrue(hasattr(components, name), f"components.py must define {name}")

    def test_components_reexported_same_object(self):
        import add
        from add_engine import components
        for name in MOVED:
            self.assertTrue(hasattr(add, name), f"component_drift: add.{name} missing")
            self.assertIs(getattr(add, name), getattr(components, name),
                          f"component_drift: add.{name} is not the components object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src, f"dead-code: add.py still defines {name}")


class OptInInvariantTest(unittest.TestCase):
    def test_no_registry_returns_empty(self):
        import add
        tmp = Path(tempfile.mkdtemp(prefix="add-comp-")).resolve()
        try:
            # no components.toml in tmp -> the registry reader degrades to {} (opt-in)
            self.assertEqual(add._components(tmp), {},
                             "no components.toml must yield {} (the opt-in/byte-identical invariant)")
        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)


class NoCycleTest(unittest.TestCase):
    def test_components_imports_without_add(self):
        # also exercises the tomllib guard path (import must not crash)
        code = ("import add_engine.components as c; "
                "assert all(hasattr(c, n) for n in ['_components','_contracts','_federation']); "
                "assert hasattr(c, 'tomllib')")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"cycle/import/guard error: {r.stderr.strip()}")


class PinTest(unittest.TestCase):

    def test_pkg_digest_includes_components_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("components.py", names, "components.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != the package digest")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src, f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
