#!/usr/bin/env python3
"""Red/green tests for the fast-lane skill guide + glossary (task fast-lane-guide, milestone fast-lane).

A prose/skill task: ship `phases/fast-lane.md` (×3 skill trees), a SKILL.md pointer (×3), and a
"fast lane" glossary term in the book (appendix-c-glossary.md) + the dogfood survivor (.add/GLOSSARY.md).
The guide must KEEP the trust floor (frozen contract · red test before build · recorded verify gate) —
it teaches collapse, never skip. Byte-parity of the new files rides the existing tree/bundle suites.

Run: python3 -m unittest test_fast_lane_guide -v
"""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent              # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

SKILL_TREES = (
    ADD_METHOD / "skill" / "add",
    REPO / ".claude" / "skills" / "add",
    BUNDLE / "skill" / "add",
)
GUIDES = tuple(t / "phases" / "fast-lane.md" for t in SKILL_TREES)
SKILLS = tuple(t / "SKILL.md" for t in SKILL_TREES)

BOOK_GLOSSARY = ADD_METHOD / "docs" / "appendix-c-glossary.md"
SURVIVOR_GLOSSARY = REPO / ".add" / "GLOSSARY.md"


class FastLaneGuidePresent(unittest.TestCase):
    def test_guide_exists_in_all_three_trees(self):
        for p in GUIDES:
            self.assertTrue(p.exists(), f"missing fast-lane guide: {p}")

    def test_guide_byte_identical_across_trees(self):
        bodies = {p.read_bytes() for p in GUIDES if p.exists()}
        self.assertEqual(len(bodies), 1, "fast-lane.md diverged across the skill trees")

    def test_guide_keeps_the_floor(self):
        """collapse-never-skip: the guide must name the frozen contract, the red test, and the gate."""
        text = GUIDES[0].read_text().lower()
        self.assertIn("freez", text, "guide must name the frozen contract")
        self.assertIn("red", text, "guide must name the red-test-before-build")
        self.assertIn("gate", text, "guide must name the verify gate")
        self.assertTrue(re.search(r"collapse", text), "guide must frame it as collapse, not skip")

    def test_guide_does_not_teach_skipping_the_floor(self):
        text = GUIDES[0].read_text().lower()
        for bad in ("skip the freeze", "skip the contract", "skip the gate", "without a gate",
                    "no frozen contract", "drop the floor"):
            self.assertNotIn(bad, text, f"guide must not teach a bypass: {bad!r}")

    def test_skill_points_to_the_guide(self):
        for p in SKILLS:
            self.assertTrue(p.exists(), f"missing SKILL.md: {p}")
            self.assertIn("fast-lane.md", p.read_text(),
                          f"SKILL.md does not point to the fast-lane guide: {p}")

    def test_glossary_defines_the_term(self):
        self.assertRegex(BOOK_GLOSSARY.read_text(), r"(?i)fast lane",
                         "book glossary missing the 'fast lane' term")
        self.assertRegex(SURVIVOR_GLOSSARY.read_text(), r"(?i)fast lane",
                         ".add/GLOSSARY.md missing the 'fast lane' term")


if __name__ == "__main__":
    unittest.main()
