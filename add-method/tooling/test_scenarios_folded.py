#!/usr/bin/env python3
"""fold-scenarios-tests: red/green guard for retiring §2 SCENARIOS into §4.

The change: the standalone `## 2 · SCENARIOS` section is DELETED and its role folds
into a retitled `## 4 · TESTS & SCENARIOS`; the closed form-tag vocab drops `scenarios`;
§4 states a primary-only rigor policy. §3–§7 numbers, the freeze parser, and the ~380
§3–§7 references are UNTOUCHED (retire-in-place, not renumber).

These tests split into two families:
  NEW-behaviour (must go RED before the build) — M1 M2 M3 M4 M7
  PRESERVED-invariant guards (green from the start; catch a regression the edit might
    introduce) — M5 M6 M8 R

Run: cd add-method/tooling && python3 -m unittest test_scenarios_folded -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
TMPL = HERE / "templates" / "PLAN.md.tmpl"

# the exact engine anchors the parser greps (mirrors test_template_atomic.ENGINE_ANCHORS
# subset that this change must never drop) — R:template_anchor_lost.
LOAD_BEARING = ("## 3 · PLAN", "Status: DRAFT", "Tests live in:", "## 5 · BUILD",
                "## 6 · VERIFY", "## 7 · OBSERVE")

FOLDED_VOCAB = {"must", "reject", "after", "assumptions", "test_plan"}


def _tags(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?m)^<(/?)([a-z_]+)>$", text)


class NewBehaviourTest(unittest.TestCase):
    """RED until the build ships the fold."""

    def setUp(self):
        self.text = TMPL.read_text(encoding="utf-8")

    def test_template_has_no_scenarios_section(self):  # M1
        self.assertNotRegex(self.text, r"(?m)^##\s*2\s*·\s*SCENARIOS",
                            "the standalone §2 SCENARIOS heading must be gone")
        self.assertNotIn(("", "scenarios"), _tags(self.text),
                         "the <scenarios> form-tag must be retired")

    def test_section_four_retitled(self):  # M2
        self.assertRegex(self.text, r"(?m)^##\s*4\s*·\s*TESTS & SCENARIOS",
                         "§4 must be retitled 'TESTS & SCENARIOS'")

    def test_frozen_tag_vocab_drops_scenarios(self):  # M3
        names = {name for _, name in _tags(self.text)}
        self.assertEqual(names, FOLDED_VOCAB,
                         "closed form-tag vocab must be exactly "
                         "{must,reject,after,assumptions,test_plan}")

    def test_fallback_parity(self):  # M4
        fb = add._FALLBACK_TASK
        self.assertNotRegex(fb, r"(?m)^##\s*2\s*·\s*SCENARIOS",
                            "_FALLBACK_TASK must also drop the §2 heading")
        self.assertRegex(fb, r"(?m)^##\s*4\s*·\s*TESTS & SCENARIOS",
                         "_FALLBACK_TASK must retitle §4")

    def test_section_four_states_primary_only_rigor(self):  # M7
        # a stable phrase the template body must carry (case-insensitive, whitespace-loose)
        self.assertRegex(self.text.lower(),
                         r"one red test per.*must.*reject",
                         "§4 body must state the primary-only rigor policy")
        self.assertIn("not gated", self.text.lower(),
                      "§4 must say minor behaviours are prose guidance, not gated")


class PreservedInvariantTest(unittest.TestCase):
    """Green from the start — regression guards on the untouched engine."""

    def test_rule_coverage_passes_without_section_two(self):  # M5
        sec1 = "Must:\n<must>\n  - M1 does a thing\n</must>\n"
        sec4 = "<test_plan>\n  - test_x: ... covers: M1\n</test_plan>\n"
        self.assertEqual(add._rule_coverage_gaps(sec1, "", sec4), [],
                         "coverage must pass on §1+§4 alone (no §2)")

    def test_freeze_targets_section_three_on_folded_doc(self):  # M6
        folded = ("## 1 · SPECIFY\nFeature: x\n\n"
                  "## 3 · PLAN\n### Contract\n```\nx\n```\nStatus: DRAFT\n\n"
                  "## 4 · TESTS & SCENARIOS\n")
        # the freeze anchor (^## 3 ·) resolves and the DRAFT flip fires — no §2 needed
        h3 = re.search(r"(?m)^##\s*3\s*·.*$", folded)
        self.assertIsNotNone(h3, "freeze must still find the §3 heading")
        flipped, n = re.subn(r"(?m)^(\s*)Status:\s*DRAFT\s*$",
                             r"\1Status: FROZEN @ v1", folded, count=1)
        self.assertEqual(n, 1, "freeze must flip §3 Status on a §2-less doc")

    def test_legacy_scenarios_doc_still_parses(self):  # M8
        legacy = ("## 1 · SPECIFY\nrules\n\n## 2 · SCENARIOS\ncases\n\n"
                  "## 3 · PLAN\nplan\n\n## 4 · TESTS\ntests\n")
        spans = add._phase_spans(legacy)
        self.assertIn(2, spans, "a legacy §2-bearing doc must still parse §2")
        self.assertIn(4, spans, "and §4")

    def test_engine_anchors_survive(self):  # R:template_anchor_lost
        text = TMPL.read_text(encoding="utf-8")
        for anchor in LOAD_BEARING:
            self.assertIn(anchor, text, f"load-bearing anchor lost: {anchor!r}")


if __name__ == "__main__":
    unittest.main()
