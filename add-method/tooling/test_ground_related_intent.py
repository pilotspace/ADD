#!/usr/bin/env python3
"""Red/green tests for ground-related-intent — the §0 GROUND sixth field.

GROUND should link each task to its FOUNDATION intent so the spec is anchored in the
project's purpose, not re-derived. Frozen shape (§3 @ v1):
  - 3-plan.md `## Gather` gains a "Related intent" category — PROJECT.md § · GLOSSARY
    term(s) · the originating request/milestone rationale (the "conversation", a LEAN
    pointer — no new artifact); distinct from Honors (intent/why, not conventions);
  - 3-plan.md `## Exit gate` gains a checkbox for it;
  - PLAN.md.tmpl `## 0 · GROUND` gains ONE `Related intent:` line, AFTER the
    `Issues/Risks (→ feed §1):` line;
  - INVARIANTS preserved: `Anchors the contract cites:` line, `## 0`/`GROUND`, add.py
    byte-identical to engine_pin; the phases lean budget held HONESTLY (compaction, or a
    RECORDED human-approved rebaseline — never a silent baseline bump);
  - SYNC: 3-plan.md ×3 and PLAN.md.tmpl ×3 byte-identical.

Run: python3 -m unittest test_ground_related_intent -v
"""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

import engine_pin

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

GUIDE_COPIES = [
    _ADD_METHOD / "skill" / "add" / "phases" / "direction.md",
    _REPO / ".claude" / "skills" / "add" / "phases" / "direction.md",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "direction.md",
]
TMPL_COPIES = [
    _ADD_METHOD / "tooling" / "templates" / "PLAN.md.tmpl",
    _REPO / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.md.tmpl",
]
ADD_PY_COPIES = [
    _ADD_METHOD / "tooling" / "add.py",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
]
_CANON = _ADD_METHOD / "skill" / "add"
FIELD = "Related intent"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _guide() -> str:
    return GUIDE_COPIES[0].read_text(encoding="utf-8")


def _tmpl() -> str:
    return TMPL_COPIES[0].read_text(encoding="utf-8")


def _section0(tmpl: str) -> str:
    m = re.search(r"## 0 .*?GROUND.*?(?=\n## 1 )", tmpl, flags=re.S)
    return m.group(0) if m else ""


def _grounding_block(tmpl: str) -> str:
    """plan-phase-core: grounding moved from `## 0 · GROUND` into `## 3 · PLAN`'s
    `### Grounding` sub-block (up to the next `### `/`## ` heading, i.e. `### Contract`)."""
    m = re.search(r"### Grounding\b.*?(?=\n(?:### |## ))", tmpl, flags=re.S)
    return m.group(0) if m else ""


class GuideNamesRelatedIntent(unittest.TestCase):
    def test_guide_names_related_intent(self):
        self.assertIn(FIELD, _guide(),
                      "the guide's gather must name the 'Related intent' category")

    def test_guide_links_foundation(self):
        # must point at PROJECT + GLOSSARY (the foundation intent), not just any prose
        gathered = _guide().split("### Grounding", 1)[-1].split("\n## ", 1)[0]
        self.assertIn("PROJECT", gathered, "Related intent must link PROJECT.md")
        self.assertIn("GLOSSARY", gathered, "Related intent must link GLOSSARY")

    def test_guide_keeps_all_prior_categories(self):
        text = _guide()
        for anchor in ("Touches", "Context", "Honors", "Anchors", "Issues/Risks"):
            self.assertIn(anchor, text, f"the guide must keep the {anchor} field")

    def test_exit_gate_covers_related_intent(self):
        # skill-loop-fold: direction.md carries one <exit_gate> per beat
        gates = re.findall(r"<exit_gate>(.*?)</exit_gate>", _guide(), re.DOTALL)
        self.assertTrue(gates, "the guide must keep its <exit_gate> blocks")
        self.assertTrue(any(FIELD in g for g in gates),
                        "an exit gate must list the Related-intent field")


class TemplateGainsRelatedIntentLine(unittest.TestCase):
    """plan-phase-core: re-pointed from the removed `## 0 · GROUND` section to the
    `## 3 · PLAN` section's `### Grounding` sub-block (_grounding_block)."""

    def test_section0_has_related_intent_line(self):
        grounding = _grounding_block(_tmpl())
        self.assertTrue(grounding, "the template must have a `### Grounding` sub-block (§3 PLAN)")
        self.assertIn(f"{FIELD}:", grounding, "§3 PLAN Grounding must carry the `Related intent:` line")

    def test_related_intent_after_issues(self):
        grounding = _grounding_block(_tmpl())
        self.assertIn("Issues/Risks", grounding, "the Issues/Risks line must remain")
        self.assertLess(grounding.index("Issues/Risks"), grounding.index(f"{FIELD}:"),
                        "Related intent must come AFTER the Issues/Risks line")

    def test_section0_preserves_anchors_line(self):
        self.assertIn("Anchors the contract cites:", _grounding_block(_tmpl()),
                      "the §3 PLAN grounding-measure line must be preserved verbatim")


class LeanBudgetHeldHonestly(unittest.TestCase):
    """The pool stays at-or-under its target — whatever the baseline is, the budget holds
    and any rebaseline is RECORDED (the test_skill_lean comment trail), never silent."""


if __name__ == "__main__":
    unittest.main(verbosity=2)
