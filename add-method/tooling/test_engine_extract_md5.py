#!/usr/bin/env python3
"""extract-md5 (engine-modularization 12/N) — the 2 md5 hashing helpers
(`_md5_text`·`_md5_file`) FOLDED from add.py into the existing add_engine/io_state.py
(the low-level IO/byte primitives module — no new module). Re-exported as add globals.

Closed, unpatched, stdlib-only (hashlib/Path) -> plain re-export.
Run: python3 -m unittest test_engine_extract_md5 -v
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

MOVED = ("_md5_text", "_md5_file")


class ReexportTest(unittest.TestCase):
    def test_md5_live_in_io_state(self):
        from add_engine import io_state
        for name in MOVED:
            self.assertTrue(hasattr(io_state, name), f"io_state.py must define {name}")

    def test_md5_folded_same_object(self):
        import add
        from add_engine import io_state
        for name in MOVED:
            self.assertTrue(hasattr(add, name), f"hash_drift: add.{name} missing")
            self.assertIs(getattr(add, name), getattr(io_state, name),
                          f"hash_drift: add.{name} is not the io_state object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src, f"dead-code: add.py still defines {name}")


class HashPreservedTest(unittest.TestCase):
    def test_md5_text_known_hex(self):
        import add
        self.assertEqual(add._md5_text("abc"), hashlib.md5(b"abc").hexdigest())
        self.assertEqual(add._md5_text("abc"), "900150983cd24fb0d6963f7d28e17f72")

    def test_md5_file_fail_closed(self):
        import add
        missing = TOOLING / "no_such_file_xyz.bin"
        self.assertIsNone(add._md5_file(missing),
                          "_md5_file must return None on OSError (fail-closed), never raise")

    def test_md5_file_reads_real_bytes(self):
        import add
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"hello")
            p = Path(fh.name)
        try:
            self.assertEqual(add._md5_file(p), hashlib.md5(b"hello").hexdigest())
        finally:
            p.unlink(missing_ok=True)


class NoCycleTest(unittest.TestCase):
    def test_io_state_imports_without_add(self):
        code = ("import add_engine.io_state as s; "
                "assert s._md5_text('') and s._md5_file.__name__ == '_md5_file'")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"cycle/import error: {r.stderr.strip()}")


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
            self.assertNotIn(forbidden, src, f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
