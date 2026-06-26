#!/usr/bin/env python3
"""extract-release (engine-modularization 14/N) — the 6 changelog/RELEASES render
helpers (`_releases_path`·`_closed_milestones`·`_key_decisions_for`·`_build_in_flight`·
`_render_changelog_block`·`_render_releases_row`) moved from add.py into a NEW
add_engine/release.py, re-exported as add.py module globals.

Closed cluster (transitive-closure AST = zero outbound), none patched -> plain re-export.
Run: python3 -m unittest test_engine_extract_release -v
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

MOVED = ("_releases_path", "_closed_milestones", "_key_decisions_for",
         "_build_in_flight", "_render_changelog_block", "_render_releases_row")


class ReexportTest(unittest.TestCase):
    def test_release_live_in_module(self):
        from add_engine import release
        for name in MOVED:
            self.assertTrue(hasattr(release, name), f"release.py must define {name}")

    def test_release_reexported_same_object(self):
        import add
        from add_engine import release
        for name in MOVED:
            self.assertTrue(hasattr(add, name), f"release_drift: add.{name} missing")
            self.assertIs(getattr(add, name), getattr(release, name),
                          f"release_drift: add.{name} is not the release object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src, f"dead-code: add.py still defines {name}")


class RenderPreservedTest(unittest.TestCase):
    def test_releases_path_is_root_sibling(self):
        import add
        # root IS the .add dir -> the ledger sits at the project root, sibling of CHANGELOG
        self.assertEqual(add._releases_path(Path("/proj/.add")), Path("/proj/RELEASES.md"))

    def test_render_releases_row_verbatim(self):
        import add
        row = add._render_releases_row("1.0.0", "2026-01-01", [{"slug": "m1"}], [], None)
        self.assertEqual(
            row,
            "## 1.0.0 — 2026-01-01\n"
            "milestones: m1\n"
            "loose tasks: none\n"
            "waivers: none\n"
            "evidence: recorded by add.py release\n\n",
        )

    def test_render_releases_row_with_actor_and_loose(self):
        import add
        row = add._render_releases_row("2.0.0", "2026-02-02", [{"slug": "a"}, {"slug": "b"}],
                                       ["w1"], "suite 10/0", actor="Tin", loose=[{"slug": "t1"}])
        self.assertIn("milestones: a, b\n", row)
        self.assertIn("loose tasks: t1\n", row)
        self.assertIn("waivers: w1\n", row)
        self.assertIn("actor: Tin\n", row)
        self.assertIn("evidence: suite 10/0\n", row)


class NoCycleTest(unittest.TestCase):
    def test_release_imports_without_add(self):
        code = ("import add_engine.release as r; "
                "assert all(hasattr(r, n) for n in "
                "['_render_releases_row','_render_changelog_block','_releases_path'])")
        res = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"cycle/import error: {res.stderr.strip()}")


class PinTest(unittest.TestCase):
    def test_engine_md5_still_pins_add_py(self):
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must stay md5(add.py), re-aimed after the shrink")

    def test_pkg_digest_includes_release_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("release.py", names, "release.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != ENGINE_PKG_MD5")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src, f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
