#!/usr/bin/env python3
"""extract-render (engine-modularization 9/N) — the 8 terminal-render primitives
(`_bar`·`_phase_track`·`_use_ascii`·`_color_enabled`·`_term_width`·`_colorize`·`_clip`·`_wrap`)
moved from add.py into a NEW add_engine/render.py, re-exported as add.py module globals.
The render-private `_ANSI` travels with the cluster; the SHARED `_DEFAULT_WIDTH` relocates
to constants.py (single source for render.py + the staying default-arg signatures).

Closed cluster (transitive-closure AST = zero outbound), none patched -> plain re-export.
Run: python3 -m unittest test_engine_extract_render -v
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

MOVED = ("_bar", "_phase_track", "_use_ascii", "_color_enabled",
         "_term_width", "_colorize", "_clip", "_wrap")


class ReexportTest(unittest.TestCase):
    def test_render_live_in_module(self):
        from add_engine import render
        for name in MOVED:
            self.assertTrue(hasattr(render, name), f"render.py must define {name}")
        self.assertTrue(hasattr(render, "_ANSI"),
                        "the render-private _ANSI must travel with the cluster")

    def test_render_reexported_same_object(self):
        import add
        from add_engine import render
        for name in MOVED:
            self.assertTrue(hasattr(add, name), f"render_drift: add.{name} missing")
            self.assertIs(getattr(add, name), getattr(render, name),
                          f"render_drift: add.{name} is not the render object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src, f"dead-code: add.py still defines {name}")
        self.assertNotIn("\n_ANSI = {", src, "dead-code: add.py still defines _ANSI")
        self.assertNotIn("\n_DEFAULT_WIDTH = ", src,
                         "dead-code: add.py still defines _DEFAULT_WIDTH (moved to constants)")


class OutputPreservedTest(unittest.TestCase):
    def test_bar(self):
        import add
        g = {"reached": "#", "pending": "."}
        self.assertEqual(add._bar(1, 2, 4, g), "##..")
        self.assertEqual(add._bar(0, 0, 4, g), "....", "0/0 must be all-empty (no div-by-zero)")
        self.assertEqual(add._bar(9, 3, 4, g), "####", "over-full clamps to cells")

    def test_colorize_wraps_tokens(self):
        import add
        out = add._colorize("PASS")
        self.assertIn("\x1b[32m", out, "PASS must get the green ANSI code")
        self.assertIn("PASS", out)
        self.assertIn("\x1b[0m", out)

    def test_wrap_returns_lines(self):
        import add
        rows = add._wrap("alpha beta gamma delta", 12, "L")
        self.assertIsInstance(rows, list)
        self.assertTrue(all(isinstance(r, str) for r in rows))


class DefaultWidthTest(unittest.TestCase):
    def test_default_width_relocated_to_constants(self):
        import add
        from add_engine import constants
        self.assertEqual(constants._DEFAULT_WIDTH, 72,
                         "_DEFAULT_WIDTH must live in constants.py as the single source")
        self.assertEqual(add._DEFAULT_WIDTH, 72,
                         "add._DEFAULT_WIDTH must still resolve (the staying default-args need it)")


class NoCycleTest(unittest.TestCase):
    def test_render_imports_without_add(self):
        code = ("import add_engine.render as r; "
                "assert all(hasattr(r, n) for n in ['_bar','_colorize','_wrap','_ANSI'])")
        res = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"cycle/import error: {res.stderr.strip()}")


class PinTest(unittest.TestCase):

    def test_pkg_digest_includes_render_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("render.py", names, "render.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != the package digest")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src, f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
