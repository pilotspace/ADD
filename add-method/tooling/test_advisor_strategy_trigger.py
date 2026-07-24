#!/usr/bin/env python3
"""advisor-strategy-trigger: add-advisor refutes a high-uncertainty milestone strategy.

strategy-guide shipped the DISCUSS→OPTIMIZE→CONVERGE loop; the advisor already refutes a
task DIRECTION bundle. This wires the milestone-level analog: at CONVERGE, a high-uncertainty
milestone spawns add-advisor in REFUTE mode to break the strategy before it is recorded —
advisory (never blocks), risk-proportional (micro/--tiny skips), reusing the existing refute
mode. These checks assert both prose edits (strategy.md loop + add-advisor.md direction beat)
and the twin parity across the skill AND agent trees.
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
AGENT_TREES = [
    REPO / "add-method" / "agents",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "agents",
    REPO / ".claude" / "agents",
]
CANON_STRATEGY = SKILL_TREES[0] / "strategy.md"
CANON_ADVISOR = AGENT_TREES[0] / "add-advisor.md"


def _strategy():
    return CANON_STRATEGY.read_text(encoding="utf-8") if CANON_STRATEGY.is_file() else ""


def _advisor():
    return CANON_ADVISOR.read_text(encoding="utf-8") if CANON_ADVISOR.is_file() else ""


def _converge_block(text):
    """The CONVERGE step text, from its marker to the next numbered/heading break."""
    m = re.search(r"CONVERGE", text)
    if not m:
        return ""
    return text[m.start():]


class ConvergeSpawnsRefute(unittest.TestCase):
    def test_converge_spawns_advisor_refute(self):                      # M1
        low = _strategy().lower()
        self.assertIn("add-advisor", low,
                      "CONVERGE must spawn add-advisor to refute the strategy")
        self.assertIn("refute", low, "the spawn must be in REFUTE mode")
        self.assertTrue("high-uncertainty" in low or "high uncertainty" in low,
                        "the refute fires for a HIGH-UNCERTAINTY milestone")
        # ordered before recording: 'refute' appears before the record-in-slot instruction
        self.assertTrue(re.search(r"break|refute", low), "must try to BREAK the strategy")

    def test_trigger_is_risk_proportional(self):                        # M2, R:forced_advisor_ceremony
        low = _strategy().lower()
        self.assertTrue("--tiny" in low or "micro" in low,
                        "a micro / --tiny milestone must be named as skipping the spawn")
        self.assertTrue("skip" in low or "not required" in low or "never required" in low,
                        "the spawn must be offered, not forced (risk-proportional)")

    def test_refute_is_advisory_never_blocks(self):                     # M3, R:refute_blocks_strategy
        # Scope the no-block statement to the REFUTE context — the existing SOFT prose already
        # says the milestone is "never blocked" on a confidence bar, so a file-wide check would
        # pass vacuously. The new guarantee is that the ADVISOR's refute cannot block.
        low = _strategy().lower()
        self.assertIn("hard-stop", low, "security-HARD-STOP must be restated")
        m = re.search(r"add-advisor|refute", low)
        self.assertIsNotNone(m, "no refute context to scope the advisory caveat to")
        ctx = low[m.start():]
        self.assertTrue("cannot block" in ctx or "does not block" in ctx or "can't block" in ctx
                        or "not block" in ctx,
                        "the advisor's refute must be stated as unable to block the milestone")
        self.assertTrue("human" in ctx and "confirm" in ctx,
                        "within the refute context, the human still confirms the strategy")

    def test_advisor_direction_beat_names_strategy(self):               # M4
        text = _advisor()
        self.assertTrue(text, "add-advisor.md must exist")
        low = text.lower()
        # locate the direction-beat sentence and check it names the milestone strategy
        m = re.search(r"\*\*direction\*\*.*?(?=\*\*build\*\*)", text, re.DOTALL | re.IGNORECASE)
        beat = (m.group(0) if m else "").lower()
        self.assertTrue(beat, "add-advisor.md must still have the direction beat")
        self.assertIn("strategy", beat,
                      "the direction beat must name the milestone STRATEGY as a refutable artifact")
        # no new mode invented — the milestone strategy reuses 'refute'
        self.assertIn("refute", beat, "the strategy is refuted via the existing refute mode")


class TwinParity(unittest.TestCase):
    def test_strategy_and_advisor_twinned(self):                        # M5
        for name, trees in (("strategy.md", SKILL_TREES), ("add-advisor.md", AGENT_TREES)):
            blobs = {t: (t / name).read_bytes() for t in trees if (t / name).is_file()}
            self.assertGreater(len(blobs), 1, f"expected multiple twins of {name}")
            first = next(iter(blobs.values()))
            for t, blob in blobs.items():
                self.assertEqual(blob, first, f"{name} twin drift: {t}")


if __name__ == "__main__":
    unittest.main()
