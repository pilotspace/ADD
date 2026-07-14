#!/usr/bin/env python3
"""Red/green tests for the risk-proportional gate render (task risk-report-render,
frozen v1): a `sensitivity: mechanical` or fast-lane task's verify gate renders a
compact form (banner - SUMMARY - EVIDENCE - APPROVE); the full card is reserved for
security / data / architecture and every freeze. Prose-only, message layer — the
dispatch lives in the phase guides (single home; report-template.md untouched).

  M1 — 6-verify.md's gate card carries the dispatch: mechanical + fast -> compact;
       security / data / architecture -> full card.
  M2 — the compact subset names its sections IN ORDER within the dispatch.
  M3 — 3-plan.md reserves the freeze for the full card ("never the compact form").
  M4 — fast-lane.md matches: freeze full, fast verify gate compact.
  R1 — the report-gate imperatives survive verbatim in both gate guides.
  R2 — single home: the dispatch phrase stays out of report-template.md.
  R3 — the phases pool stays within its 33284B target.

One test per §1 Must/Reject. Run: python3 -m unittest test_risk_report_render -v
"""
import unittest
from pathlib import Path

_SKILL = Path(__file__).resolve().parent.parent / "skill" / "add"
_PLAN = _SKILL / "phases" / "3-plan.md"
_VERIFY = _SKILL / "phases" / "6-verify.md"
_FAST = _SKILL / "phases" / "fast-lane.md"
_TEMPLATE = _SKILL / "report-template.md"

_PHASES_POOL_TARGET = 33284


def _ordered(text: str, names: list[str], where: str, tc: unittest.TestCase):
    last = -1
    for n in names:
        idx = text.find(n, last + 1)
        tc.assertGreater(idx, last, f"{where}: {n!r} missing or out of order")
        last = idx


class VerifyDispatchTest(unittest.TestCase):
    def test_verify_card_dispatch(self):                           # M1
        text = _VERIFY.read_text(encoding="utf-8")
        card = text[text.index("## Record exactly one outcome"):]
        self.assertIn("compact form", card)
        self.assertIn("`sensitivity: mechanical`", card)
        self.assertIn("fast-lane", card)
        for cls in ("`security`", "`data`", "`architecture`"):
            self.assertIn(cls, card, f"the full-card reservation must name {cls}")

    def test_compact_subset_order(self):                           # M2
        text = _VERIFY.read_text(encoding="utf-8")
        i = text.index("compact form")
        _ordered(text[i:i + 200], ["banner", "SUMMARY", "EVIDENCE", "APPROVE"],
                 "6-verify.md compact form", self)


class FreezeReservationTest(unittest.TestCase):
    def test_freeze_reserves_full(self):                           # M3
        text = _PLAN.read_text(encoding="utf-8")
        self.assertIn("never the compact form", text,
                      "3-plan.md must reserve the freeze for the full card")

    def test_fast_lane_matches(self):                              # M4
        text = _FAST.read_text(encoding="utf-8")
        self.assertIn("full card", text, "fast-lane.md: the freeze renders full")
        self.assertIn("compact form", text, "fast-lane.md: the fast verify gate is compact")
        _ordered(text, ["banner", "SUMMARY", "EVIDENCE", "APPROVE"],
                 "fast-lane.md compact form", self)


class GuardTest(unittest.TestCase):
    def test_imperatives_survive(self):                            # R1
        self.assertIn("render before `FROZEN`, then record `Reported: yes`; never on a timeout",
                      _PLAN.read_text(encoding="utf-8"))
        self.assertIn("render before `gate` and record `Reported: yes` in §6, never self-stamp",
                      _VERIFY.read_text(encoding="utf-8"))

    def test_single_home(self):                                    # R2
        text = _TEMPLATE.read_text(encoding="utf-8")
        self.assertNotIn("sensitivity: mechanical", text,
                         "the dispatch's home is the phase guides, not the template")
        self.assertNotIn("compact form", text,
                         "the dispatch's home is the phase guides, not the template")

    def test_phases_pool_within_target(self):                      # R3
        total = sum(len(p.read_bytes())
                    for p in sorted((_SKILL / "phases").glob("[0-7]-*.md")))
        self.assertLessEqual(total, _PHASES_POOL_TARGET,
                             f"phases pool {total}B over target — compress-to-absorb")


if __name__ == "__main__":
    unittest.main()
