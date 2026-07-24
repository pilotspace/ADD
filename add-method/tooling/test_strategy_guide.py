#!/usr/bin/env python3
"""strategy-guide: the persona-framed DISCUSS→OPTIMIZE→CONVERGE loop guide.

strategy-section shipped the `## Strategy` slot in MILESTONE.md; persona-at-intake made
the persona load before sizing. The missing piece is the HOW — the guide that drives the
loop filling that slot with an optimized task DAG, converging on the EXISTING confidence
self-score, kept SOFT (never a new gate; security stays HARD-STOP).

These checks assert the guide exists, reuses the intake persona and the existing self-score
(never a new mechanism), stays advisory, and is pointed at from SKILL.md + beyond.md.
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
CANON = SKILL_TREES[0]
STRATEGY = CANON / "strategy.md"


def _read(name):
    f = CANON / name
    return f.read_text(encoding="utf-8") if f.is_file() else ""


class StrategyGuideContent(unittest.TestCase):
    def test_strategy_guide_has_the_loop(self):                         # M1
        t = _read("strategy.md")
        self.assertTrue(t, "strategy.md must exist")
        up = t.upper()
        for stage in ("DISCUSS", "OPTIMIZE", "CONVERGE"):
            self.assertIn(stage, up, f"strategy.md must name the {stage} stage")
        low = t.lower()
        # the four DAG facets the loop must produce
        self.assertTrue(re.search(r"freeze-first", low), "must name freeze-first contracts")
        self.assertTrue(re.search(r"wave", low), "must name parallel waves")
        self.assertTrue(re.search(r"unblock", low), "must name the first unblocking slice")
        self.assertTrue(re.search(r"sequenc|approach", low), "must name the sequencing approach")
        self.assertIn("## Strategy", t, "must say it fills the milestone's ## Strategy slot")

    def test_strategy_reuses_intake_persona(self):                      # M2
        low = _read("strategy.md").lower()
        self.assertIn("persona", low, "the loop must be persona-framed")
        self.assertIn("intake", low,
                      "strategy.md must reuse the persona loaded at intake, not re-select one")

    def test_converge_cites_existing_selfscore(self):                   # M3
        low = _read("strategy.md").lower()
        self.assertIn("phases/direction.md", low,
                      "CONVERGE must cite the existing self-score in phases/direction.md")
        self.assertTrue(
            "self-score" in low or "six" in low or "confidence" in low,
            "CONVERGE must reuse the confidence self-score, not invent a new bar")

    def test_strategy_is_soft_not_a_gate(self):                         # M4
        low = _read("strategy.md").lower()
        self.assertTrue("soft" in low or "advisory" in low,
                        "the strategy must be stated SOFT/advisory")
        self.assertTrue("security" in low and "hard-stop" in low,
                        "security-always-HARD-STOP must be restated")
        self.assertTrue("drafted-blank" in low or "--tiny" in low or "micro" in low,
                        "a micro/--tiny milestone may skip the loop (drafted-blank)")

    def test_skill_and_beyond_point_to_strategy(self):                  # M5
        self.assertIn("strategy.md", _read("SKILL.md"),
                      "SKILL.md 'Beyond the bundle' must point at strategy.md")
        self.assertIn("strategy.md", _read("beyond.md"),
                      "beyond.md full prose must route to strategy.md")


class StrategyTwinParity(unittest.TestCase):
    def test_strategy_files_twinned(self):                             # M6
        for name in ("strategy.md", "SKILL.md", "beyond.md"):
            blobs = {t: (t / name).read_bytes()
                     for t in SKILL_TREES if (t / name).is_file()}
            self.assertGreater(len(blobs), 1, f"expected multiple twins of {name}")
            first = next(iter(blobs.values()))
            for t, blob in blobs.items():
                self.assertEqual(blob, first, f"{name} twin drift: {t}")


if __name__ == "__main__":
    unittest.main()
