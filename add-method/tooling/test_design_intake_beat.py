"""Red suite for design-intake-beat (milestone udd-design-intake). Contract §3 FROZEN @ v1.

Adds a `design-intake` beat (beat 0) to the UDD design loop in design.md — the agent
interviews the human on FOUR axes (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) BEFORE
review-domain, records the answers BOTH altitudes (project defaults in DESIGN.md
"## Design intake"; per-screen overrides in the per-feature design note), surfaces identity
(never auto-picks), and keeps it convention-only (the engine never renders).

One assertion per frozen scenario. RED until the beat / section / book entries exist; GREEN
after build. Mirror parity (3 trees) is asserted here AND by test_tree_parity/test_bundle_parity.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import add  # noqa: F401 — kept for _render_template parity with the sibling suites

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

_CANON_SKILL = _ADD_METHOD / "skill" / "add"
_BUNDLE_SKILL = _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
_DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add"

_BUNDLE_TOOLING = _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling"
_DOGFOOD_TOOLING = _REPO / ".add" / "tooling"

_DESIGN = _CANON_SKILL / "design.md"
_DOCS = _ADD_METHOD / "docs"
_FOUNDATION = _DOCS / "14-foundation.md"
_GLOSSARY = _DOCS / "appendix-c-glossary.md"

# the four intake axes, frozen names
_AXES = ("fidelity", "concept", "layout", "visual design")


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _render_template():
    return add._render_template("DESIGN.md", date="2026-01-01", project="Demo", stage="mvp")


def _section(doc: str, heading: str) -> str:
    """The '## <heading>…' block up to the next '## ' (or EOF). '' if absent."""
    out, capturing = [], False
    for ln in doc.splitlines():
        if ln.startswith("## "):
            if capturing:
                break
            capturing = ln[3:].strip().lower().startswith(heading.lower())
            if capturing:
                out.append(ln)
                continue
        elif capturing:
            out.append(ln)
    return "\n".join(out)


class DesignIntakeBeatTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guide = _text(_DESIGN)
        cls.lower = cls.guide.lower()

    # Scenario: design-intake is beat 0 of the loop
    def test_intake_is_beat_zero(self) -> None:
        self.assertIn("design-intake", self.lower, "design.md must add a design-intake beat")
        i_intake = self.lower.find("design-intake")
        i_domain = self.lower.find("review-domain")
        self.assertNotEqual(i_domain, -1, "review-domain beat must still exist")
        self.assertLess(i_intake, i_domain, "design-intake must come BEFORE review-domain")

    def test_loop_diagram_lists_intake_first(self) -> None:
        # the diagram line names all five beats in order, intake first
        order = ["design-intake", "review-domain", "research-components",
                 "wireframe", "render-capture-confirm"]
        pos = [self.lower.find(b) for b in order]
        self.assertNotIn(-1, pos, f"a beat is missing from the loop: {order}")
        self.assertEqual(pos, sorted(pos), f"five beats out of order: {pos}")

    # Scenario: the beat names all four axes with their options
    def test_four_axes_named(self) -> None:
        for axis in _AXES:
            self.assertIn(axis, self.lower, f"design-intake must name the '{axis}' axis")

    def test_axis_option_sets_present(self) -> None:
        for opt in ("lo-fi", "hi-fi", "production",   # fidelity
                    "structure", "grid", "hierarchy",  # layout
                    "spacing", "imagery"):             # visual design
            self.assertIn(opt, self.lower, f"design-intake must offer the option '{opt}'")

    # Scenario: the four answers are recorded before review-domain (both altitudes)
    def test_records_both_altitudes(self) -> None:
        self.assertIn("## design intake", self.lower,
                      "design.md must point at the DESIGN.md '## Design intake' section")
        self.assertTrue(
            "override" in self.lower or "per-screen" in self.lower,
            "design.md must describe per-screen OVERRIDES alongside project defaults",
        )

    # Scenario: VISUAL DESIGN surfaces identity, never auto-picks
    def test_visual_design_surfaces_identity(self) -> None:
        self.assertTrue(
            "surface" in self.lower,
            "the VISUAL DESIGN axis must SURFACE identity values",
        )
        self.assertTrue(
            "human-owned" in self.lower or "never auto-pick" in self.lower
            or "never invent" in self.lower,
            "identity_auto_picked: identity must stay human-owned in the intake beat",
        )

    # Scenario: FIDELITY is record-only intent, not a gate / convention-only
    def test_fidelity_is_intent_not_gate(self) -> None:
        # isolate the BEAT BODY (### 0 … up to ### 1), not the diagram line where both tokens co-occur
        start = self.lower.find("### 0")
        end = self.lower.find("### 1")
        self.assertNotEqual(start, -1, "the design-intake beat must have a '### 0' heading")
        intake = self.lower[start:end]
        self.assertIn("fidelity", intake, "the intake beat must cover FIDELITY")
        self.assertTrue(
            "intent" in intake or "inform" in intake,
            "FIDELITY must be framed as recorded intent that informs the later beats",
        )


class DesignIntakeTemplateTest(unittest.TestCase):
    # Scenario: DESIGN.md template seeds a Design intake section
    def test_template_has_design_intake_section(self) -> None:
        doc = _render_template()
        self.assertIn("## Design intake", doc, "DESIGN.md.tmpl must seed a '## Design intake' section")

    def test_section_names_four_axes(self) -> None:
        block = _section(_render_template(), "Design intake").lower()
        for axis in _AXES:
            self.assertIn(axis, block, f"the Design intake section must list the '{axis}' axis")

    def test_section_is_prompt_not_prefilled(self) -> None:
        block = _section(_render_template(), "Design intake")
        self.assertIn("<!--", block, "Design intake fields must be HTML-comment prompts (fill-then-delete)")
        no_comments = re.sub(r"<!--.*?-->", "", block, flags=re.DOTALL)
        self.assertNotRegex(no_comments, r"#[0-9A-Fa-f]{6}",
                            "a concrete brand hex outside a prompt = identity_auto_picked")

    def test_section_crossrefs_identity(self) -> None:
        block = _section(_render_template(), "Design intake").lower()
        self.assertIn("identity", block,
                      "the Design intake section must cross-reference ## Identity, not restate it")


class DesignIntakeBookTest(unittest.TestCase):
    # Scenario: the book documents the five-beat loop and the axis terms
    def test_foundation_narrates_intake_beat(self) -> None:
        text = _text(_FOUNDATION).lower()
        self.assertIn("design-intake", text,
                      "14-foundation.md must narrate the loop with the design-intake beat")

    def test_glossary_defines_axis_terms(self) -> None:
        text = _text(_GLOSSARY).lower()
        for axis in _AXES:
            self.assertIn(axis, text, f"appendix-c-glossary.md must define the '{axis}' axis term")


class DesignIntakeParityTest(unittest.TestCase):
    # Scenario: every surface is mirrored byte-identical
    def test_design_guide_mirrored(self) -> None:
        canon = _DESIGN.read_bytes()
        self.assertEqual(canon, (_BUNDLE_SKILL / "design.md").read_bytes(),
                         "design.md: canonical ≠ bundled (mirror_drift)")
        self.assertEqual(canon, (_DOGFOOD_SKILL / "design.md").read_bytes(),
                         "design.md: canonical ≠ dogfood (mirror_drift)")

    def test_design_template_mirrored(self) -> None:
        rel = "templates/DESIGN.md.tmpl"
        canon = (_TOOLING / rel).read_bytes()
        self.assertEqual(canon, (_BUNDLE_TOOLING / rel).read_bytes(),
                         f"{rel}: canonical ≠ bundled (mirror_drift)")
        self.assertEqual(canon, (_DOGFOOD_TOOLING / rel).read_bytes(),
                         f"{rel}: canonical ≠ dogfood (mirror_drift)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
