#!/usr/bin/env python3
"""Marker guard for the decision arc (task: report-arc, milestone v23;
extended by task: report-plan-approve).

gate-udd.md gains an ARC block — three labelled lines goal:/done:/plan:
rendered ABOVE the five existing blocks — that every human gate carries, so the
human confirms with full sight of the work's arc (the goal it serves, what's
proven, the plan ahead) rather than a local snapshot.

report-plan-approve further adds: a decision banner (PLAN · <title> · <gate> →
APPROVE? + a 📄 path line) rendered above the ARC; an optional PLAN block (multi-
step breakdown) and a freeze-only SHAPE block; and renames the DECISION block to
APPROVE, reordered to sit last among the core blocks.

The shipped skill doc is the artifact under test. We assert the frozen §3 ARC
contract: the three labels in order above SUMMARY, the seven-gate rule, the
engine-source mapping, and SKILL.md's pointer naming the ARC. Parity across the
three skill trees is guarded by test_tree_parity + test_bundle_parity; banned
wording by test_wording_lint + test_ubiquitous_language. The arc's per-gate
quality is a human read at the gate — this file guards only the mechanical shape.

Red before the build edit, green after. Run: python3 -m unittest test_report_arc -v
"""
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
CANON_SKILL = _TOOLING.parent / "skill" / "add"
TEMPLATE = CANON_SKILL / "gate-udd.md"
SKILL = CANON_SKILL / "SKILL.md"

# the seven human gates the arc is required at (frozen §3)
GATES = (
    "baseline-lock",
    "contract-freeze",
    "verify",
    "intake",
    "scope",
    "milestone-close",
    "graduation",
)


class ReportArcMarkerTest(unittest.TestCase):
    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_arc_block_has_three_labels_in_order(self):
        self.assertIn("ARC", self.text, "gate-udd.md must define an ARC block")
        for label in ("goal:", "done:", "plan:"):
            self.assertIn(
                label, self.text, f"the ARC block must carry the label {label!r}"
            )
        g = self.text.index("goal:")
        d = self.text.index("done:")
        p = self.text.index("plan:")
        self.assertTrue(
            g < d < p, "ARC labels must appear in order: goal: · done: · plan:"
        )

    def test_arc_renders_above_the_five_blocks(self):
        # ARC first, above SUMMARY; the unchanged five blocks all remain present.
        self.assertIn("ARC", self.text, "gate-udd.md must define an ARC block")
        self.assertIn("SUMMARY", self.text, "the SUMMARY block must remain present")
        self.assertLess(
            self.text.index("ARC"),
            self.text.index("SUMMARY"),
            "the ARC block must render ABOVE SUMMARY",
        )
        for block in ("SUMMARY", "APPROVE", "FLAGS", "EVIDENCE", "NEXT"):
            self.assertIn(block, self.text, f"the {block} block must remain present")

    def test_arc_required_at_all_seven_gates(self):
        for gate in GATES:
            self.assertIn(
                gate,
                self.text,
                f"the ARC must be named as required at the {gate!r} gate",
            )

    def test_arc_facts_are_engine_sourced(self):
        for src in ("m-goal", "DECIDE NEXT"):
            self.assertIn(
                src, self.text, f"the ARC source mapping must name {src!r}"
            )
        # the 'done' line maps to exit-criteria met/total + tasks done
        self.assertTrue(
            "exit-criteria" in self.text or "exit criteria" in self.text,
            "the ARC 'done' line must map to exit-criteria met/total",
        )

    def test_at_least_one_per_gate_example(self):
        # one shared shape, per-gate content: >=1 worked example beyond the spec line.
        self.assertIn(
            "example",
            self.text.lower(),
            "the template must carry >=1 worked per-gate example",
        )
        self.assertGreaterEqual(
            self.text.count("goal:"),
            2,
            "expected the arc spec plus >=1 worked example (>=2 'goal:' lines)",
        )

    def test_skill_pointer_names_the_arc(self):
        skill = SKILL.read_text(encoding="utf-8")
        i = skill.find("gate-udd")
        self.assertNotEqual(i, -1, "SKILL.md must point at gate-udd.md")
        window = skill[max(0, i - 200) : i + 400]
        self.assertIn(
            "ARC",
            window,
            "SKILL.md's gate-udd pointer must name the ARC block",
        )


class DecisionBannerMarkerTest(unittest.TestCase):
    """task: report-plan-approve — the banner rendered above the ARC."""

    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_banner_names_plan_and_approve(self):
        self.assertIn("PLAN ·", self.text, "the banner must open with 'PLAN ·'")
        self.assertIn(
            "APPROVE?", self.text, "the banner must end its title line with 'APPROVE?'"
        )

    def test_banner_carries_a_path_line(self):
        self.assertIn(
            "📄", self.text, "the banner must carry a 📄 path line to TASK.md"
        )

    def test_banner_renders_above_the_arc(self):
        banner_i = self.text.find("PLAN ·")
        arc_i = self.text.find("ARC  goal:")
        self.assertNotEqual(banner_i, -1, "banner marker 'PLAN ·' must be present")
        self.assertNotEqual(arc_i, -1, "the ARC spec line must be present")
        self.assertLess(banner_i, arc_i, "the banner must render ABOVE the ARC")


class PlanShapeBlockMarkerTest(unittest.TestCase):
    """task: report-plan-approve — the optional PLAN block and freeze-only SHAPE block."""

    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_plan_block_defined_with_glyph_legend(self):
        self.assertIn("PLAN   <milestone", self.text, "a PLAN block must be defined")
        for glyph in ("✅", "🔄", "⬜", "⚠"):
            self.assertIn(glyph, self.text, f"the PLAN block glyph legend must include {glyph!r}")

    def test_plan_block_collapses_done_and_caps_live_items(self):
        self.assertIn(
            "done (N)", self.text, "PLAN must collapse done items to a count, not enumerate them"
        )
        self.assertIn("5–7", self.text, "PLAN must state the live-item cap (~5-7)")

    def test_shape_block_is_freeze_only(self):
        self.assertIn("SHAPE   <task title", self.text, "a SHAPE block must be defined")
        self.assertIn(
            "freeze-only", self.text, "SHAPE must be documented as freeze-only"
        )


class DecisionRenamedApproveTest(unittest.TestCase):
    """task: report-plan-approve — DECISION is renamed APPROVE, reordered last."""

    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_decision_no_longer_used_as_a_block_name(self):
        self.assertNotIn(
            "DECISION",
            self.text,
            "the DECISION block must be fully renamed to APPROVE — no 'DECISION' left",
        )

    def test_approve_sits_after_evidence(self):
        self.assertIn("APPROVE", self.text)
        self.assertIn("EVIDENCE", self.text)
        self.assertLess(
            self.text.index("EVIDENCE"),
            self.text.rindex("APPROVE"),
            "APPROVE must be reordered to sit after EVIDENCE, last among the core blocks",
        )


class ReportTemplateRippleMarkerTest(unittest.TestCase):
    """task: report-plan-approve — the DECISION->APPROVE rename ripples into 4 referencing guides."""

    def test_skill_and_phase_guides_say_approve_not_decision(self):
        for rel in (
            "SKILL.md",
            "phases/0-setup.md",
            "phases/3-plan.md",
            "phases/6-verify.md",
        ):
            path = CANON_SKILL / rel
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(
                "DECISION", text, f"{rel} must not reference the retired DECISION block name"
            )
            self.assertIn(
                "APPROVE", text, f"{rel} must reference the renamed APPROVE block"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
