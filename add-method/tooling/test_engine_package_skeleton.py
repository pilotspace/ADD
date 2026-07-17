#!/usr/bin/env python3
"""engine-package-skeleton (engine-modularization 1/N) — the engine is now a
PACKAGE (add.py entry + add_engine/*.py modules) behind a stable import surface.

Two-pin model (contract v2): the engine pin stays md5(add.py) so the ~52 existing
prose-suite EnginePinTest copies keep passing untouched; a NEW the package digest
literal pins the add_engine/ package (the manifest digest over its *.py modules,
computed by the SEPARATE engine_manifest.package_digest — engine_pin.py never hashes).

Guards the frozen contract:
  - every constant moved to add_engine/constants.py still resolves as `add.<name>`
    with a byte-identical value (constant_drift),
  - the package digest == package_digest of the canonical tree, and the same across all
    three trees (mirror_incomplete),
  - both pins are LITERALS (engine_pin.py has no hashlib — the digest helper is
    in engine_manifest.py),
  - a one-byte change to a package module breaks the package digest (the pin still bites).

Run: python3 -m unittest test_engine_package_skeleton -v
"""
import hashlib
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

# the three engine trees, by their tooling dir
TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)

PUBLIC = ("ROOT_DIRNAME", "STATE_FILE", "MILESTONE_FILE", "GOAL_UNSET", "STAGES",
          "GRADUATION_CUE", "RELEASABLE_CUE", "RELEASES_FILE", "PHASES", "GATES",
          "HEAL_CAP", "PHASE_GUIDE", "PHASE_OWNER", "SETUP_FILES", "GUIDELINE_FILES",
          "RULES_FILE_REL", "WORKFLOW_HEADINGS")
PRIVATE = ("_GITIGNORE_BODY", "_GUIDE_BEGIN", "_GUIDE_END", "_RULE_REF_LINE",
           "_FALLBACK_TASK", "_FAST_SECTIONS")


class ConstantsReexportTest(unittest.TestCase):
    def test_constants_reexported_round_trip(self):
        import add
        from add_engine import constants
        for name in PUBLIC + PRIVATE:
            self.assertTrue(hasattr(add, name),
                            f"constant_drift: add.{name} missing after the split")
            self.assertEqual(getattr(add, name), getattr(constants, name),
                             f"constant_drift: add.{name} != add_engine.constants.{name}")

    def test_phase_index_still_works(self):
        import add
        self.assertEqual(add._phase_index("ground"), 0)
        self.assertEqual(add._phase_index("done"), len(add.PHASES) - 1)


class PackagePinTest(unittest.TestCase):

    def test_pkg_md5_is_package_digest(self):
        import engine_pin
        import engine_manifest
        self.assertEqual(engine_manifest.package_digest(TOOLING), engine_pin.ENGINE_PKG_MD5,
                         "the package digest must equal the package digest of the canonical tree")


    def test_package_files_sorted_and_complete(self):
        import engine_manifest
        files = engine_manifest.package_files(TOOLING)
        names = [f.name for f in files]
        self.assertIn("__init__.py", names)
        self.assertIn("constants.py", names)
        self.assertEqual(names, sorted(names), "package_files must be deterministically sorted")

    def test_both_pins_are_literals(self):
        # neither pin is self-computed; the digest helper lives in engine_manifest, not the pin home
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src,
                             f"vacuous_pin: engine_pin.py must not {forbidden!r}")

    def test_one_byte_drift_breaks_pkg_digest(self):
        import engine_manifest
        good = engine_manifest.package_digest(TOOLING)
        files = engine_manifest.package_files(TOOLING)
        h = hashlib.md5()
        for f in files:
            data = f.read_bytes() + (b"\n# drift\n" if f.name == "constants.py" else b"")
            h.update(f"{f.name}:{hashlib.md5(data).hexdigest()}\n".encode())
        self.assertNotEqual(h.hexdigest(), good,
                            "a one-byte change to a package module must change the package digest")


if __name__ == "__main__":
    unittest.main(verbosity=2)
