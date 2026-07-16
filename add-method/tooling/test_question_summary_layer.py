"""question-summary-layer §4 suite — the question is a summary, never the artifact.

Four RED targets (the build drives these green):
  - test_rule_bullet_present     : gate-udd.md <constraints> carries the frozen
    bullet — rule name + both layers' needles (positional "immediately before the ask",
    compositional "two lines at most", and "the flag count").
  - test_ask_itself_tie_in       : the "**The ask itself**" tie-in sits in the
    five-blocks section.
  - test_skill_anchor_names_rule : SKILL.md's template-anchor line names the rule.
  - test_one_home_only           : the rule's needle phrase lives in EXACTLY
    {gate-udd.md, SKILL.md} across skill/add/**/*.md — red now (0 homes),
    green only at exactly 2. Guards the contract's `rule_sprinkled` rejection
    permanently: a third home (or a deleted home) goes red.

One GREEN guard (green at write-time, disclosed in §4 — guards `guard_weakened`):
  - test_existing_constraints_verbatim : the 5 pre-existing constraint bullets stay
    byte-present; the new bullet is ADDITIVE, never a rewording.

Lint / inventory / mirror parity are owned by the STANDING fences (wording_lint,
semantic-inventory, the skill/add tree-parity guard) — declared in §4, not duplicated.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLING))

_SKILL = _TOOLING.parent / "skill" / "add"
_TEMPLATE = _SKILL / "gate-udd.md"
_SKILL_MD = _SKILL / "SKILL.md"

# The frozen hunk-A needles (contract §3, verbatim fragments — guard-dense: one per claim).
_RULE_TITLE = "The question is a summary, never the artifact."
_NEEDLE_POSITIONAL = "immediately before the ask"
_NEEDLE_COMPOSITIONAL = "two lines at most"
_NEEDLE_FLAG_COUNT = "the flag count"
# The frozen hunk-B needle.
_NEEDLE_TIE_IN = "**The ask itself**"
# The home-identity needle (case-folded; shared by the bullet title and the anchor clause).
_HOME_NEEDLE = "question is a summary"

# The 5 pre-existing constraint bullets — first-line fragments, byte-exact.
_EXISTING_BULLETS = (
    "**Summary-first.** Never bury the decision under a task list or a diff.",
    "**Show before ask.** Render the artifact (digest · diff · report) before any",
    "**Never pre-stamp a human decision point.** Freeze / gate / lock fields stay DRAFT or",
    "**One report per decision point.** After an approval, point at the frozen artifact —",
    "**Honest scope.** \"Done\" means the request, not the last task: report",
)


class QuestionSummaryLayer(unittest.TestCase):
    def test_rule_bullet_present(self) -> None:
        text = _TEMPLATE.read_text(encoding="utf-8")
        for needle in (_RULE_TITLE, _NEEDLE_POSITIONAL,
                       _NEEDLE_COMPOSITIONAL, _NEEDLE_FLAG_COUNT):
            self.assertIn(needle, text,
                          f"gate-udd.md is missing the frozen needle: {needle!r}")

    def test_ask_itself_tie_in(self) -> None:
        text = _TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(_NEEDLE_TIE_IN, text,
                      "the five-blocks section is missing the 'The ask itself' tie-in")

    def test_skill_anchor_names_rule(self) -> None:
        text = _SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("the question is a summary, never the artifact", text,
                      "SKILL.md's template-anchor line must name the rule")

    def test_one_home_only(self) -> None:
        homes = sorted(
            p.relative_to(_SKILL).as_posix()
            for p in _SKILL.rglob("*.md")
            if _HOME_NEEDLE in p.read_text(encoding="utf-8").lower()
        )
        self.assertEqual(homes, ["SKILL.md", "gate-udd.md"],
                         f"the rule must live in exactly two homes, found: {homes}")

    def test_existing_constraints_verbatim(self) -> None:
        text = _TEMPLATE.read_text(encoding="utf-8")
        for bullet in _EXISTING_BULLETS:
            self.assertIn(bullet, text,
                          f"a pre-existing constraint bullet changed or vanished: {bullet!r}")


if __name__ == "__main__":
    unittest.main()
