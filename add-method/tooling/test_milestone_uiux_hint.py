#!/usr/bin/env python3
"""Red/green test for the MILESTONE.md.tmpl UI/UX vocabulary hint.

A prose/template-only enhancement: the ## Scope section gains a conditional hint —
when a milestone's scope is UI/UX-flavored, name it in the design vocabulary the
persona-teacher-bundle actually uses (`.add/personas-teacher/design/*.md`), not
generic "make it nice" language — AND, precise isn't the same as distinctive, so it
also carries the anti-genericness principle from Claude Code's own `frontend-design`
skill (skip the templated AI-design defaults, name one deliberate signature element).
Placed at MILESTONE, not TASK.md.tmpl (which sits at its pinned <12 `<!--` comment
ceiling with zero headroom — see
test_template_form_tags.py::test_lean_pass_single_freeze_comment), so it is read
once per milestone rather than bloating the highest-frequency per-task file. Points
at the existing design.md/DESIGN.md UDD mechanism rather than duplicating it.

Run: python3 -m unittest test_milestone_uiux_hint -v
"""
import hashlib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent          # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

MILE_TMPL_COPIES = [
    HERE / "templates" / "MILESTONE.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "MILESTONE.md.tmpl",
    BUNDLE / "tooling" / "templates" / "MILESTONE.md.tmpl",
]

# the design-vocabulary anchors the hint must name — drawn from the persona-teacher
# corpus (design-ui-designer.md, design-ux-architect.md, design-ux-researcher.md)
VOCAB_ANCHORS = (
    "information architecture", "interaction pattern", "visual hierarchy",
    "design tokens", "component states", "accessibility floor", "WCAG AA",
    "responsive breakpoints", "user journey",
)
# the anti-genericness anchors — drawn from Claude Code's own frontend-design skill
DISTINCTIVENESS_ANCHORS = ("signature element", "frontend-design", "generic")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class MilestoneUiuxHintTest(unittest.TestCase):
    def test_hint_present_in_scope_section(self):
        text = MILE_TMPL_COPIES[0].read_text(encoding="utf-8")
        self.assertIn("## Scope", text)
        scope_block = text.split("## Scope", 1)[1].split("## Shared decisions", 1)[0]
        self.assertIn("UI/UX", scope_block, "the Scope section must carry a UI/UX hint")
        for anchor in VOCAB_ANCHORS:
            self.assertIn(anchor, scope_block, f"hint must name: {anchor}")

    def test_hint_cites_persona_teacher_source(self):
        text = MILE_TMPL_COPIES[0].read_text(encoding="utf-8")
        self.assertIn("personas-teacher", text,
                      "the hint must trace its vocabulary to the persona-teacher-bundle")

    def test_hint_carries_distinctiveness_principle(self):
        # precise naming alone can still be a generic AI-design default — the hint must
        # also nudge toward ONE deliberate choice, sourced from the frontend-design skill
        text = MILE_TMPL_COPIES[0].read_text(encoding="utf-8")
        scope_block = text.split("## Scope", 1)[1].split("## Shared decisions", 1)[0]
        for anchor in DISTINCTIVENESS_ANCHORS:
            self.assertIn(anchor, scope_block, f"hint must name: {anchor}")

    def test_hint_points_at_design_loop_not_duplicate(self):
        text = MILE_TMPL_COPIES[0].read_text(encoding="utf-8")
        self.assertIn("design.md", text,
                      "the hint must point at the existing UDD design-definition loop, not fork it")

    def test_mirrors_byte_identical(self):
        digests = {_md5(p) for p in MILE_TMPL_COPIES}
        self.assertEqual(len(digests), 1, "the 3 MILESTONE.md.tmpl copies must be byte-identical")

    def test_release_field_still_present(self):
        # regression guard: the pre-existing release-backlink field must survive this edit
        text = MILE_TMPL_COPIES[0].read_text(encoding="utf-8")
        self.assertIn("release:", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
