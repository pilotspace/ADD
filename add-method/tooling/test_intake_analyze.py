"""intake-analyze suite — analyze a raw request into a task before sizing it.

Locks the skill's front-door capability: ADD reads raw intent into a task shape
FIRST (restate · extract · name-unstated · surface-hidden), and only then sizes it.
This is the "analyst, not just orchestrator" identity.

RED targets (the edit drives these green):
  - test_analyze_section_present   : intake.md carries the Analyze section + its four moves.
  - test_analyze_before_interview  : Analyze sits BEFORE Interview, which sits before the buckets
    (pins the order: analyze → interview → classify).
  - test_skill_identity_reframed   : SKILL.md's opening frames intent→task, not pure-orchestrator.
  - test_terms_decoder_linked      : terms.md exists and SKILL.md points to it.
  - test_design_refs_qualified     : design.md's UDD-schema pointers resolve (templates/ path),
    never a bare dangling sibling.

Mirror parity (the 3 SKILL.md trees + canonical↔bundle skill tree) is owned by the
STANDING fences (test_intent_handoff, test_bundle_parity) — not duplicated here.
"""
from __future__ import annotations

import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_SKILL = _TOOLING.parent / "skill" / "add"
_INTAKE = _SKILL / "intake.md"
_SKILL_MD = _SKILL / "SKILL.md"
_TERMS = _SKILL / "terms.md"
_DESIGN = _SKILL / "design.md"

_ANALYZE_HEADER = "## Analyze the request before you size it"
_INTERVIEW_HEADER = "## Interview before you size"
_BUCKETS_HEADER = "## The four buckets"
_MOVES = (
    "Restate the intent",
    "Extract the latent requirements",
    "Name the unstated",
    "Surface the hidden work",
)


class IntakeAnalyze(unittest.TestCase):
    def test_analyze_section_present(self):
        text = _INTAKE.read_text(encoding="utf-8")
        self.assertIn(_ANALYZE_HEADER, text, "intake.md is missing the Analyze section")
        for move in _MOVES:
            self.assertIn(move, text, f"intake.md Analyze section is missing the move: {move!r}")

    def test_analyze_before_interview(self):
        text = _INTAKE.read_text(encoding="utf-8")
        for header in (_ANALYZE_HEADER, _INTERVIEW_HEADER, _BUCKETS_HEADER):
            self.assertIn(header, text, f"intake.md is missing: {header!r}")
        self.assertLess(
            text.index(_ANALYZE_HEADER), text.index(_INTERVIEW_HEADER),
            "Analyze must precede Interview (read the request before probing it)",
        )
        self.assertLess(
            text.index(_INTERVIEW_HEADER), text.index(_BUCKETS_HEADER),
            "Interview must still precede the buckets (analysis before classification)",
        )

    def test_skill_identity_reframed(self):
        text = _SKILL_MD.read_text(encoding="utf-8")
        self.assertIn(
            "turn intent into the right task", text,
            "SKILL.md's opening must frame ADD as turning intent into a task, not a bare orchestrator",
        )

    def test_terms_decoder_linked(self):
        self.assertTrue(_TERMS.exists(), "terms.md (the coined-vocabulary decoder) is missing")
        terms = _TERMS.read_text(encoding="utf-8")
        self.assertIn("compound-cross", terms, "terms.md must decode the loop's coined terms")
        self.assertIn(
            "terms.md", _SKILL_MD.read_text(encoding="utf-8"),
            "SKILL.md must link the terms.md decoder (one level deep)",
        )

    def test_design_refs_qualified(self):
        text = _DESIGN.read_text(encoding="utf-8")
        self.assertIn(
            "templates/udd-tokens.md", text,
            "design.md's tokens-schema pointer must name the templates/ path so it resolves",
        )
        self.assertNotIn(
            "(`udd-tokens.md`)", text,
            "design.md must not carry a bare dangling (`udd-tokens.md`) pointer",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
