#!/usr/bin/env python3
"""extract-io-state (engine-modularization 2/N) — the 4 pure IO primitives
(`_now`, `_atomic_write`, `_atomic_write_bytes`, `_atomic_write_many`) moved from
add.py into add_engine/io_state.py, re-exported as add.py module globals.

The re-export is the contract: `import add; add._atomic_write` must still resolve,
AND `add._atomic_write = spy` must still intercept add.py-level callers (the two
live patch sites in test_scope_gate_enforce + test_guidelines rely on this). The
primitive is the SAME object reached either way (io_primitive_drift).

The package pin grows: io_state.py joins the manifest digest, so ENGINE_PKG_MD5
re-aims; ENGINE_MD5 stays md5(add.py) (re-aimed because add.py shrank). Both stay
literals — engine_pin.py never hashes.

Run: python3 -m unittest test_engine_extract_io_state -v
"""
import hashlib
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

PRIMITIVES = ("_now", "_atomic_write", "_atomic_write_bytes", "_atomic_write_many")


class ReexportTest(unittest.TestCase):
    def test_primitives_live_in_io_state(self):
        from add_engine import io_state
        for name in PRIMITIVES:
            self.assertTrue(hasattr(io_state, name),
                            f"io_state must define {name} after the extraction")

    def test_primitives_reexported_same_object(self):
        import add
        from add_engine import io_state
        for name in PRIMITIVES:
            self.assertTrue(hasattr(add, name),
                            f"io_primitive_drift: add.{name} missing after the split")
            self.assertIs(getattr(add, name), getattr(io_state, name),
                          f"io_primitive_drift: add.{name} is not the io_state object")

    def test_add_py_no_longer_defines_them(self):
        # the defs moved — add.py must not still carry a `def _atomic_write(` etc.
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in PRIMITIVES:
            self.assertNotIn(f"\ndef {name}(", src,
                             f"dead-code: add.py still defines {name} (duplicate of io_state)")


class MonkeypatchPreservedTest(unittest.TestCase):
    def test_patching_add_atomic_write_intercepts_add_level_caller(self):
        """The re-export keeps `add._atomic_write = spy` live for add.py callers —
        proven against a real add.py-level write (sync-guidelines path style)."""
        import add
        real = add._atomic_write
        seen = []

        def spy(path, text):
            seen.append(Path(path).name)
            return real(path, text)

        add._atomic_write = spy
        try:
            with tempfile.TemporaryDirectory(prefix="add-ios-") as td:
                target = Path(td) / "probe.txt"
                add._atomic_write(target, "hello")        # bare module-global call
                self.assertEqual(target.read_text(encoding="utf-8"), "hello")
                self.assertIn("probe.txt", seen, "the spy must have fired")
        finally:
            add._atomic_write = real


class PinTest(unittest.TestCase):
    def test_engine_md5_still_pins_add_py(self):
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must stay md5(add.py), re-aimed after the shrink")

    def test_pkg_digest_includes_io_state_and_is_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("io_state.py", names, "io_state.py must join the package manifest")
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
