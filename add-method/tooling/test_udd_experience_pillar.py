#!/usr/bin/env python3
"""Red suite for udd-experience-pillar (milestone strategy-intake). Contract §3 FROZEN @ v1.

Redefines UDD from UI-design into EXPERIENCE-DRIVEN development: design.md's framing
broadens to a UI feature OR any human-facing experience surface (a screen · an interaction ·
a human gate), and the design-intake beat gains a FIFTH axis — INTERACTION (cadence ·
when/how to seek the human · turn-rhythm) — alongside the four originals (which stay, frozen
names). SKILL.md's UDD trigger names experience surfaces, not UI features only. The human
gate is NAMED an in-scope UDD surface. report-template.md is NOT folded here (that is
gate-experience-udd). The DESIGN.md.tmpl + glossary INTERACTION field is a deferred
completion (this task is the conceptual foundation).

Red before the build, green after. Run: python3 -m unittest test_udd_experience_pillar -v
"""
import hashlib
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_REPO = _TOOLING.parent.parent
CANON = _TOOLING.parent / "skill" / "add"
BUNDLED = _TOOLING.parent / "src" / "add_method" / "_bundled" / "skill" / "add"
DOGFOOD = _REPO / ".claude" / "skills" / "add"
DESIGN = CANON / "design.md"
SKILL = CANON / "SKILL.md"

_ORIGINAL_FOUR = ("fidelity", "concept", "layout", "visual design")


class ExperienceDrivenFramingTest(unittest.TestCase):
    """M1 / R2 — UDD is experience-driven, not UI-only."""

    def setUp(self):
        self.text = DESIGN.read_text(encoding="utf-8")
        self.low = self.text.lower()
        # the opening framing window (before the loop diagram)
        self.head = self.low[: self.low.find("## the loop")] if "## the loop" in self.low else self.low[:1000]

    def test_framing_is_experience_driven(self):
        self.assertTrue(
            "experience surface" in self.head or "experience-driven" in self.head,
            "design.md's framing must scope UDD to a human-facing EXPERIENCE surface, not UI only",
        )

    def test_framing_names_a_gate_as_a_surface(self):
        self.assertIn(
            "gate", self.head,
            "the framing must name a human GATE as an in-scope UDD experience surface",
        )

    def test_not_ui_only(self):
        # the bare "when a UI feature reaches specify" (UI-only) framing must be broadened
        self.assertNotIn(
            "when a **ui feature** reaches specify, design it before you build it",
            self.low,
            "udd_still_ui_only: the UI-only framing must be broadened to experience surfaces",
        )


class FifthAxisTest(unittest.TestCase):
    """M2 / R1 — the design-intake beat names five axes incl. INTERACTION; the four stay."""

    def setUp(self):
        self.text = DESIGN.read_text(encoding="utf-8")
        self.low = self.text.lower()

    def test_interaction_axis_named(self):
        self.assertIn(
            "interaction", self.low,
            "the design-intake beat must add the INTERACTION axis",
        )

    def test_interaction_axis_covers_cadence_and_seeking(self):
        # find the INTERACTION axis line and check its content
        i = self.low.find("interaction")
        self.assertNotEqual(i, -1)
        window = self.low[i : i + 200]
        self.assertIn("cadence", window, "INTERACTION must cover cadence")
        self.assertTrue(
            "seek" in window or "when/how" in window or "turn-rhythm" in window or "turn rhythm" in window,
            "INTERACTION must cover when/how to seek the human · turn-rhythm",
        )

    def test_five_axes_phrasing(self):
        self.assertIn(
            "five", self.low,
            "the design-intake beat / hard-rules must say FIVE axes, not four",
        )
        self.assertNotIn(
            "four design axes", self.low,
            "the 'four design axes' phrasing must become five",
        )

    def test_original_four_axes_intact(self):
        for axis in _ORIGINAL_FOUR:
            self.assertIn(
                axis, self.low,
                f"axis_dropped: the original '{axis}' axis must stay (frozen name)",
            )


class SkillTriggerTest(unittest.TestCase):
    """M3 — SKILL.md's UDD trigger names experience surfaces; ceiling + parity hold."""

    def test_udd_trigger_names_experience_surface(self):
        skill = SKILL.read_text(encoding="utf-8").lower()
        i = skill.find("udd loop")
        self.assertNotEqual(i, -1, "SKILL.md must keep the UDD-loop trigger")
        window = skill[max(0, i - 120) : i + 40]
        self.assertTrue(
            "experience" in window,
            "the SKILL.md UDD trigger must name a human-experience surface, not UI feature only",
        )

    def test_skill_under_ceiling(self):
        self.assertLess(SKILL.stat().st_size, 9500, "SKILL.md must stay under the 9500 B ceiling")


class ParityTest(unittest.TestCase):
    """M3 — design.md + SKILL.md byte-identical across the three skill trees."""

    def test_three_trees_byte_identical(self):
        for rel in ("design.md", "SKILL.md"):
            a = hashlib.md5((CANON / rel).read_bytes()).hexdigest()
            b = hashlib.md5((BUNDLED / rel).read_bytes()).hexdigest()
            c = hashlib.md5((DOGFOOD / rel).read_bytes()).hexdigest()
            self.assertEqual(a, b, f"{rel}: canonical vs _bundled must be byte-identical")
            self.assertEqual(a, c, f"{rel}: canonical vs dogfood must be byte-identical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
