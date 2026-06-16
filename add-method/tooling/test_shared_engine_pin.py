#!/usr/bin/env python3
"""shared-engine-pin — one ENGINE_MD5 source, five importers.

Five prose-only suites each carried their own hard-coded engine pin; every
legitimate engine change meant five hand re-aims (the stale-guard sweeps of
dd5b665 and wave-status-hint). This suite drives the single source: a literal
constant in engine_pin.py — never computed (a pin that recomputes is vacuous) —
imported by the five pin-bearing suites, with a sweep proving no second pin
can creep back in.

Run: python3 -m unittest test_shared_engine_pin -v
"""
import hashlib
import io
import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

ENGINE_PATHS = (
    TOOLING / "add.py",
    REPO_ROOT / ".add" / "tooling" / "add.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)
IMPORTERS = (
    "test_getting_started_spine.py",
    "test_installer_handoff.py",
    "test_release_1_7_0.py",
    "test_review_checklist.py",
    "test_skill_onramp.py",
)
IMPORT_LINE = "from engine_pin import ENGINE_MD5"
# an assignment binding a 32-hex literal to an ENGINE_MD5-ish name
_PIN_ASSIGN = re.compile(r'ENGINE_MD5\w*\s*=\s*"[0-9a-f]{32}"')


class SingleSourceTest(unittest.TestCase):
    """engine_pin.py is the only pin home, and it is a literal."""

    def test_pin_module_is_literal_source(self):
        import engine_pin
        self.assertRegex(engine_pin.ENGINE_MD5, r"^[0-9a-f]{32}$")
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        self.assertIn(f'"{engine_pin.ENGINE_MD5}"', src,
                      "vacuous_pin: the value must live in source as a LITERAL")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src,
                             f"vacuous_pin: a pin that derives its value cannot "
                             f"catch drift (found {forbidden!r})")

    def test_pin_matches_all_three_engines(self):
        import engine_pin
        for p in ENGINE_PATHS:
            self.assertTrue(p.exists(), f"missing engine copy: {p}")
            self.assertEqual(
                hashlib.md5(p.read_bytes()).hexdigest(), engine_pin.ENGINE_MD5,
                f"{p} does not match the single-source pin")

    def test_five_importers_no_local_literals(self):
        for name in IMPORTERS:
            src = (TOOLING / name).read_text(encoding="utf-8")
            self.assertIn(IMPORT_LINE, src,
                          f"{name} must import the single-source pin")
            self.assertIsNone(_PIN_ASSIGN.search(src),
                              f"pin_not_single_source: {name} still binds its "
                              f"own 32-hex literal")

    def test_sweep_no_second_pin(self):
        # EVERY tooling .py except the single source — a pin cannot hide in a
        # helper module either.
        offenders = [p.name for p in sorted(TOOLING.glob("*.py"))
                     if p.name != "engine_pin.py"
                     and _PIN_ASSIGN.search(p.read_text(encoding="utf-8"))]
        self.assertEqual(offenders, [],
                         "pin_not_single_source: a second hard-coded engine pin "
                         "crept back in")

    def test_pin_importable_from_any_cwd(self):
        # the full-suite runner injects the tooling dir on sys.path and runs
        # from elsewhere — prove that path, don't assume it.
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as other_cwd:
            proc = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {str(TOOLING)!r}); "
                 "import engine_pin; print(engine_pin.ENGINE_MD5)"],
                cwd=other_cwd, capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0,
                         f"engine_pin must import cwd-independently: {proc.stderr}")
        self.assertRegex(proc.stdout.strip(), r"^[0-9a-f]{32}$")

    def test_five_guards_still_green(self):
        loader = unittest.defaultTestLoader
        suite = unittest.TestSuite(
            loader.loadTestsFromName(name[:-3]) for name in IMPORTERS)
        result = unittest.TextTestRunner(
            stream=io.StringIO(), verbosity=0).run(suite)
        self.assertTrue(result.wasSuccessful(),
                        "engine_touched / regression: the five pin-bearing "
                        f"suites must stay green — {result.failures} "
                        f"{result.errors}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
