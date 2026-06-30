#!/usr/bin/env python3
"""extract-predicates (engine-modularization 5/N) — 4 pure state/markdown predicates
(`_phase_owner`, `_setup_locked`, `_milestone_confirmed`, `_section_unfilled`) moved
from add.py into a NEW add_engine/predicates.py, re-exported as add.py module globals.

AST free-name scan (upfront): deps = PHASE_OWNER (constants) + _die (io_state) + re.
Unpatched. Run: python3 -m unittest test_engine_extract_predicates -v
"""
import hashlib
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

MOVED = ("_phase_owner", "_setup_locked", "_milestone_confirmed", "_section_unfilled")


class ReexportTest(unittest.TestCase):
    def test_predicates_live_in_module(self):
        from add_engine import predicates
        for name in MOVED:
            self.assertTrue(hasattr(predicates, name),
                            f"predicates.py must define {name} after the extraction")

    def test_predicates_reexported_same_object(self):
        import add
        from add_engine import predicates
        for name in MOVED:
            self.assertTrue(hasattr(add, name),
                            f"predicate_drift: add.{name} missing after the split")
            self.assertIs(getattr(add, name), getattr(predicates, name),
                          f"predicate_drift: add.{name} is not the predicates object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src,
                             f"dead-code: add.py still defines {name} (duplicate of predicates)")


class BehaviorTest(unittest.TestCase):
    def test_phase_owner_maps_known_phases(self):
        import add
        # _phase_owner reads PHASE_OWNER; every declared phase resolves to its owner
        for phase, owner in add.PHASE_OWNER.items():
            self.assertEqual(add._phase_owner(phase), owner)

    def test_section_unfilled_detects_fill(self):
        import add
        md_filled = "## 1 · SPECIFY\nFeature: a real feature line\n\n## 2 · NEXT\n"
        md_empty = "## 1 · SPECIFY\n\n## 2 · NEXT\n"
        self.assertFalse(add._section_unfilled(md_filled, "## 1 · SPECIFY"),
                         "a section with content must read as filled")
        self.assertTrue(add._section_unfilled(md_empty, "## 1 · SPECIFY"),
                        "an empty section must read as unfilled")

    def test_section_unfilled_ignores_backtick_notation(self):
        """A filled section may carry literal angle-bracket technical notation INSIDE
        code spans (`<persona>`, `.add/personas/<slug>.md`). That is content, not an
        unfilled `<…>` template placeholder — only a BARE <…> outside backticks counts."""
        import add
        hdr = "## Shared / risky contracts"
        # real content whose ONLY angle brackets are inside backtick code spans -> FILLED
        md_backtick = (hdr + "\n"
                       "- the persona-injection point in the `streams.md` worker contract "
                       "(`<persona>`/`<expertise>` load `.add/personas/<slug>.md`; cross-runner) "
                       "-> owning task persona-subagent-prompt\n\n## Next\n")
        self.assertFalse(add._section_unfilled(md_backtick, hdr),
                         "backtick-wrapped <…> notation is content, not an unfilled placeholder")
        # the scaffold default whose <…> are BARE (outside backticks) -> still UNFILLED
        md_bare = hdr + "\n- <contract name> -> owning task <slug>\n\n## Next\n"
        self.assertTrue(add._section_unfilled(md_bare, hdr),
                        "a bare <…> placeholder must still read as unfilled")


class PinTest(unittest.TestCase):
    def test_engine_md5_still_pins_add_py(self):
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must stay md5(add.py), re-aimed after the shrink")

    def test_pkg_digest_includes_predicates_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("predicates.py", names, "predicates.py must join the package manifest")
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
