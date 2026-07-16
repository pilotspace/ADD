#!/usr/bin/env python3
"""Red/green tests for gate render cards (task gate-read-diet, frozen contract v1):
the weight audit (2026-07-13) measured gate-udd.md (9.6KB, 3 call sites) +
run.md (8.9KB, 4 call sites) re-read per gate/session — the two heaviest
task-agnostic reads after SKILL.md. The fix: each gate's phase guide carries the
render SKELETON inline (a card), the big files demote to read-at-most-once
references. Skeleton + pointer — details keep ONE home (template-dedup discipline).

  M1 — phases/3-plan.md's freeze section carries the freeze card: the skeleton
       section names IN ORDER (banner → ARC → SHAPE → SUMMARY → FLAGS → DECIDED →
       EVIDENCE → APPROVE → NEXT) + the read-once pointer.
  M2 — phases/6-verify.md's gate section carries the verify card (its dialect:
       no SHAPE/DECIDED) + the kept reconcile sentence.
  M3 — SKILL.md states the read-once rule naming BOTH big references.
  M4 — the report-gate imperatives survive verbatim in both guides.
  R1 — the arc_gate_wiring pins survive (gate-udd + ARC per guide).
  R2 — the phases pool stays within its 33284B target (compress-to-absorb).

One test per §1 Must/Reject. Run: python3 -m unittest test_gate_read_diet -v
"""
import unittest
from pathlib import Path

_SKILL = Path(__file__).resolve().parent.parent / "skill" / "add"
_PLAN = _SKILL / "phases" / "3-plan.md"
_VERIFY = _SKILL / "phases" / "6-verify.md"
_SKILLMD = _SKILL / "SKILL.md"

_PHASES_POOL_TARGET = 33284  # test_skill_lean's phases baseline — the card must fit


def _ordered(text: str, names: list[str], where: str, tc: unittest.TestCase):
    last = -1
    for n in names:
        idx = text.find(n, last + 1)
        tc.assertGreater(idx, last, f"{where}: card section {n!r} missing or out of order")
        last = idx


class FreezeCardTest(unittest.TestCase):
    def test_plan_guide_carries_render_card(self):                 # M1
        text = _PLAN.read_text(encoding="utf-8")
        # the card lives in the freeze section, after the checklist intro
        card = text[text.index("## The freeze"):]
        _ordered(card, ["banner", "ARC", "SHAPE", "SUMMARY", "FLAGS",
                        "DECIDED", "EVIDENCE", "APPROVE", "NEXT"],
                 "3-plan.md freeze card", self)
        self.assertIn("at most once", card,
                      "the card must demote gate-udd.md to a read-once reference")

    def test_freeze_imperative_survives(self):                     # M4
        text = _PLAN.read_text(encoding="utf-8")
        self.assertIn("render before `FROZEN`, then record `Reported: yes`", text)
        self.assertIn("never on a timeout", text)


class VerifyCardTest(unittest.TestCase):
    def test_verify_guide_carries_render_card(self):               # M2
        text = _VERIFY.read_text(encoding="utf-8")
        card = text[text.index("## Record exactly one outcome"):]
        _ordered(card, ["banner", "ARC", "SUMMARY", "FLAGS",
                        "EVIDENCE", "APPROVE", "NEXT"],
                 "6-verify.md gate card", self)
        self.assertIn("at most once", card,
                      "the card must demote gate-udd.md to a read-once reference")
        # the reconcile sentence is KEPT (contract Must)
        self.assertIn("reconcile FLAGS", card)
        self.assertIn("report --decide", card)

    def test_verify_imperative_survives(self):                     # M4
        text = _VERIFY.read_text(encoding="utf-8")
        self.assertIn("render before `gate` and record `Reported: yes` in §6, never self-stamp", text)


class ReadOnceRuleTest(unittest.TestCase):
    def test_read_once_rule_in_skill(self):                        # M3
        text = _SKILLMD.read_text(encoding="utf-8")
        self.assertIn("at most once per session", text,
                      "SKILL.md must state the read-once rule")
        # the rule names both heavy references
        idx = text.index("at most once per session")
        window = text[max(0, idx - 400):idx + 400]
        self.assertIn("gate-udd.md", window)
        self.assertIn("run.md", window)


class GuardTest(unittest.TestCase):
    def test_wiring_pins_survive(self):                            # R1
        for path in (_PLAN, _VERIFY):
            text = path.read_text(encoding="utf-8")
            self.assertIn("gate-udd", text, f"{path.name}: arc_gate_wiring pin lost")
            self.assertIn("ARC", text, f"{path.name}: arc_gate_wiring pin lost")

    def test_phases_pool_within_target(self):                      # R2
        total = sum(len(p.read_bytes()) for p in sorted((_SKILL / "phases").glob("[0-7]-*.md")))
        self.assertLessEqual(total, _PHASES_POOL_TARGET,
                             f"phases pool {total}B over its {_PHASES_POOL_TARGET}B target — "
                             "compress-to-absorb, never rebaseline")


if __name__ == "__main__":
    unittest.main()
