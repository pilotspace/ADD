#!/usr/bin/env python3
"""fold-residue-engine-guide: the engine may not instruct a section it does not ship.

The scenarios-into-tests fold retired the standalone §2 and retitled §4, but
PHASE_GUIDE["direction"] — the action string `add.py guide` prints to every user in
the direction phase — kept telling them to write "§2 one scenario per rule". The
template has no §2. That instruction survived the fold, a milestone close and a
release cut with nothing objecting, because no check compared what the engine SAYS
against what the template CONTAINS.

These checks close that: every section the engine cites must exist in the file the
engine is describing.
"""

import re
import sys
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
REPO = TOOLING.parent.parent
TEMPLATE = TOOLING / "templates" / "PLAN.md.tmpl"

ENGINE_TREES = [
    REPO / "add-method" / "tooling",
    REPO / ".add" / "tooling",
    REPO / "add-method" / ".add" / "tooling",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling",
]

SECTION_HEADING = re.compile(r"^## (\d+) · ", re.MULTILINE)
# "§4" and ranges "§1–§4" (EN-dash) / "§1-§4" (hyphen) — a range spans every number.
SECTION_RANGE = re.compile(r"§(\d+)\s*[–-]\s*§?(\d+)")
SECTION_ONE = re.compile(r"§(\d+)")


def _template_sections():
    return {int(n) for n in SECTION_HEADING.findall(TEMPLATE.read_text(encoding="utf-8"))}


def _cited_sections(text):
    """Every §N the string asserts, with ranges expanded."""
    cited, consumed = set(), text
    for lo, hi in SECTION_RANGE.findall(text):
        cited.update(range(int(lo), int(hi) + 1))
    consumed = SECTION_RANGE.sub(" ", consumed)
    cited.update(int(n) for n in SECTION_ONE.findall(consumed))
    return cited


def _phase_guide():
    if str(TOOLING) not in sys.path:
        sys.path.insert(0, str(TOOLING))
    from add_engine.constants import PHASE_GUIDE
    return PHASE_GUIDE


class GuideSectionVocabulary(unittest.TestCase):
    def test_guide_cites_no_phantom_section(self):                      # M1
        sections = _template_sections()
        self.assertIn(4, sections, "sanity: the template really does have a §4")
        self.assertNotIn(2, sections, "sanity: §2 really was retired")

        phantom = []
        for phase, value in _phase_guide().items():
            action = value[0] if isinstance(value, (tuple, list)) else str(value)
            for n in sorted(_cited_sections(action) - sections):
                phantom.append(f"PHASE_GUIDE[{phase!r}] instructs §{n}, absent from PLAN.md.tmpl")
        self.assertEqual(phantom, [], "; ".join(phantom))

    def test_direction_guide_keeps_its_duties(self):                    # M2
        action = _phase_guide()["direction"]
        action = action[0] if isinstance(action, (tuple, list)) else str(action)

        # The fix must RE-AIM the instruction, never thin it out: each duty the
        # direction bundle owes the user has to survive somewhere in the string.
        for duty, needle in (
            ("the §1 rules", "rules"),
            ("the change plan", "change PLAN"),
            ("the red suite", "red suite"),
            ("one case per rule", "per rule"),
            ("the single freeze approval", "freeze"),
        ):
            self.assertIn(needle, action, f"PHASE_GUIDE['direction'] dropped {duty}")


class EnginePinCurrent(unittest.TestCase):
    def test_engine_pkg_pin_current(self):                              # M3
        if str(TOOLING) not in sys.path:
            sys.path.insert(0, str(TOOLING))
        import engine_manifest
        import engine_pin
        self.assertEqual(
            engine_manifest.package_digest(TOOLING), engine_pin.ENGINE_PKG_MD5,
            "add_engine/*.py changed without re-aiming ENGINE_PKG_MD5 in engine_pin.py")


class EngineTwinParity(unittest.TestCase):
    def test_engine_twins_identical(self):                              # M4
        for rel in (Path("add_engine") / "constants.py", Path("engine_pin.py")):
            blobs = {}
            for tree in ENGINE_TREES:
                f = tree / rel
                if f.is_file():
                    blobs[tree] = f.read_bytes()
            self.assertGreater(len(blobs), 1, f"expected multiple twins of {rel}")
            first = next(iter(blobs.values()))
            for tree, blob in blobs.items():
                self.assertEqual(blob, first, f"twin drift: {tree / rel}")


if __name__ == "__main__":
    unittest.main()
