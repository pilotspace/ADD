#!/usr/bin/env python3
"""Red/green tests for inline-lane (ADD 2.0 M4 skill-unify, commit A).

CONTRACT: intake gains the AI-ROUTED inline lane — the route for a change too
small to deserve versioned scope. No task, no milestone: the AI does the edit
directly and the RECEIPT is the spec diff — `add.py delta-append <dd>` files
the lesson/delta into its living 5-DD spec (specs-5dd), and the git diff +
that spec line are the whole audit trail.

- intake.md: a `## The inline lane` section sits BETWEEN the interview
  section and `## The four buckets` (the lane is judged before bucketing —
  buckets create scope; the lane exists precisely because no scope should).
- The AI routes it silently (no bucket proposal for the lane itself), but the
  floor is closed: **security · data · architecture** changes ALWAYS escalate
  to a real task — the triad is named verbatim, and the human can always
  force a task ("make it a task" overrides the route).
- The receipt is pinned: the section must name `delta-append` as the receipt
  channel and name the spec diff as the audit trail.
- SKILL.md names the lane at its intake beat (on-demand pointer discipline —
  prose lives in intake.md, SKILL.md only routes) and stays <= its 9500B
  ceiling.
- The frozen intake pins survive: `## The four buckets` heading and the
  `never guess a bucket` floor are untouched (test_intake_interview binds).

Run: python3 -m unittest test_inline_lane -v
"""
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_SKILL = _TOOLING.parent / "skill" / "add"
_INTAKE = _SKILL / "intake.md"
_SKILL_MD = _SKILL / "SKILL.md"

_LANE_HEADER = "## The inline lane"
_TRIAD = "security · data · architecture"


class InlineLaneSection(unittest.TestCase):
    def setUp(self):
        self.text = _INTAKE.read_text(encoding="utf-8")

    # Must: the lane section exists, placed between interview and buckets
    def test_lane_between_interview_and_buckets(self):
        self.assertIn(_LANE_HEADER, self.text, "intake.md must gain the inline-lane section")
        self.assertLess(self.text.index("## Interview before you size"),
                        self.text.index(_LANE_HEADER),
                        "the lane is judged AFTER the interview sharpens the request")
        self.assertLess(self.text.index(_LANE_HEADER),
                        self.text.index("## The four buckets"),
                        "the lane is judged BEFORE bucketing — buckets create scope")

    # Must: no scope artifacts — the lane creates no task and no milestone
    def test_lane_creates_no_scope(self):
        section = self._section()
        self.assertIn("no task", section.lower())
        self.assertIn("no milestone", section.lower())

    # Must: the receipt channel is delta-append into the living specs
    def test_receipt_is_delta_append(self):
        section = self._section()
        self.assertIn("delta-append", section,
                      "the lane's receipt must route through the specs-5dd verb")
        self.assertIn("diff", section.lower(),
                      "the spec/git diff must be named as the audit trail")

    # Reject: the escalation triad is closed and verbatim
    def test_escalation_triad_verbatim(self):
        section = self._section()
        self.assertIn(_TRIAD, section,
                      "security · data · architecture must ALWAYS escalate to a task")
        self.assertIn("HARD-STOP", section,
                      "the security floor keeps its name even on the inline lane")

    # Must: the human override is named — the route is AI-owned, never AI-final
    def test_human_can_force_a_task(self):
        section = self._section()
        self.assertIn("make it a task", section,
                      "the human's override phrase must be named")

    # Boundary: the frozen intake pins survive untouched
    def test_frozen_pins_survive(self):
        self.assertIn("## The four buckets", self.text)
        self.assertIn("never guess a bucket", self.text)

    def _section(self) -> str:
        start = self.text.index(_LANE_HEADER)
        end = self.text.index("## The four buckets")
        return self.text[start:end]


class SkillRoutesLane(unittest.TestCase):
    # Must: SKILL.md routes to the lane; prose stays in intake.md
    def test_skill_names_inline_lane(self):
        skill = _SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("inline lane", skill.lower(),
                      "SKILL.md's intake beat must name the inline lane")

    # Floor: the 9500B ceiling holds after the pointer lands
    def test_skill_ceiling_holds(self):
        self.assertLessEqual(_SKILL_MD.stat().st_size, 9500)


if __name__ == "__main__":
    unittest.main()
