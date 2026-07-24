#!/usr/bin/env python3
"""risk-proportional-skip: strategy.md's explicit risk→depth ladder.

The three depth tiers already exist in strategy.md but scattered — the Skip line (micro),
the Trigger line, and the CONVERGE advisor condition (low- vs high-uncertainty). This task
unifies them into ONE legible risk-proportional ladder so a reader SEES depth-scales-by-risk,
and states the micro/--tiny zero-cost skip as first-class. To be red-first, these checks
target a DEDICATED depth SECTION (its own heading), not the pre-existing scattered lines.
"""

import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
REPO = TOOLING.parent.parent
SKILL_TREES = [
    REPO / "add-method" / "skill" / "add",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "skill" / "add",
    REPO / ".claude" / "skills" / "add",
]
CANON = SKILL_TREES[0] / "strategy.md"


def _text():
    return CANON.read_text(encoding="utf-8") if CANON.is_file() else ""


def _depth_section():
    """The dedicated depth section: a heading mentioning depth/deep/risk-proportional,
    to the next heading. Scattered mentions elsewhere don't count — the deliverable is a
    UNIFIED section."""
    text = _text()
    m = re.search(r"^##+ .*(how deep|depth|risk-proportional).*$", text,
                  re.MULTILINE | re.IGNORECASE)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^##+ ", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


class DepthLadder(unittest.TestCase):
    def test_depth_ladder_names_three_tiers(self):                      # M1
        sec = _depth_section().lower()
        self.assertTrue(sec, "strategy.md must have a dedicated risk-proportional depth section")
        self.assertTrue("--tiny" in sec or "micro" in sec, "tier 1: micro/--tiny must be named")
        self.assertTrue("low-uncertainty" in sec or "multi-task" in sec or "several task" in sec,
                        "tier 2: the multi-task / low-uncertainty middle tier must be named")
        self.assertIn("high-uncertainty", sec, "tier 3: high-uncertainty (full loop + advisor)")
        self.assertIn("advisor", sec, "tier 3 must name the advisor refute as the deepest rung")

    def test_micro_skip_is_zero_cost(self):                             # M2, R:micro_cost_added
        sec = _depth_section().lower()
        self.assertTrue("zero" in sec and "cost" in sec,
                        "the micro/--tiny tier must state ZERO added per-turn cost")
        self.assertTrue("drafted-blank" in sec or "runs nothing" in sec or "run nothing"
                        in sec or "skip" in sec,
                        "the micro tier must state the loop runs nothing / drafted-blank / skip")

    def test_depth_is_soft_skill_judgment_not_engine_gate(self):        # M3, R:engine_gated_skip
        sec = _depth_section().lower()
        self.assertTrue("soft" in sec, "the ladder must be stated SOFT")
        self.assertIn("hard-stop", sec, "security-HARD-STOP must be restated")
        self.assertTrue("not an engine gate" in sec or "never an engine gate" in sec
                        or "skill's judgment" in sec or "skill judgment" in sec,
                        "the depth must be the SKILL's judgment, not an engine gate on ## Strategy")

    def test_ladder_reuses_existing_signals(self):                      # M4
        sec = _depth_section().lower()
        # ties to the existing signals rather than inventing a new numeric threshold
        self.assertTrue("reus" in sec or "signal" in sec or "above" in sec,
                        "the ladder must tie to the EXISTING Trigger/Skip + CONVERGE signals")
        # no fabricated new percentage/number as a risk threshold in this section
        self.assertNotRegex(sec, r"\b\d{1,3}\s*%\s*(risk|uncertain)",
                            "the ladder must not invent a new numeric risk threshold")


class TwinParity(unittest.TestCase):
    def test_strategy_twinned(self):                                    # M5
        blobs = {t: (t / "strategy.md").read_bytes()
                 for t in SKILL_TREES if (t / "strategy.md").is_file()}
        self.assertGreater(len(blobs), 1, "expected multiple strategy.md twins")
        first = next(iter(blobs.values()))
        for t, blob in blobs.items():
            self.assertEqual(blob, first, f"strategy.md twin drift: {t}")


if __name__ == "__main__":
    unittest.main()
