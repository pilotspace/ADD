#!/usr/bin/env python3
"""atomic-node: hygiene guards for the ONE atomic PLAN.md template.

Carried forward from the retired test_seams_template_wiring.py (whose subject —
the §3 `Seams consulted:` grounding line — left the template with the Grounding
block): the generic template-integrity guards that outlive any one field.

  tag census      — the frozen closed 6-tag vocab, each tag exactly one open +
                    one close, line-anchored (a bare new <word> line is a parser
                    hazard: it collides with the frozen-tag census at freeze)
  comment balance — every `<!--` has its `-->` (an unmatched `<!--` corrupts
                    the freeze parser; TASK.md.tmpl-edit-hazards lesson)
  engine anchors  — the exact lines the kernel greps; losing one silently
                    disables a floor (the load-bearing strings, pinned)
  3-tree parity   — canon → repo-root dogfood → bundled, byte-identical

Run: cd add-method/tooling && python3 -m unittest test_template_atomic -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
REPO_ROOT = PKG_ROOT.parent

TMPL_TREES = (
    HERE / "templates" / "PLAN.md.tmpl",
    REPO_ROOT / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.md.tmpl",
)

# the frozen closed tag vocab (v16 XML convention; test_template_form_tags owns semantics).
# `scenarios` RETIRED (fold-scenarios-tests): the §2 SCENARIOS section folded into §4 TESTS & SCENARIOS.
FROZEN_TAGS = ("must", "reject", "after", "assumptions", "test_plan")

# the exact strings the engine greps — each one gates a floor or a parse
ENGINE_ANCHORS = (
    "phase: direction",
    "## 1 · SPECIFY",
    "Boundary: <",                       # boundary_unfilled floor (§1 span)
    "## 3 · PLAN",
    "Status: DRAFT",                     # contract_not_drafted floor
    "Scope (may touch):",                # scope-lock source (§3 Build-strategy)
    "Regression floor:",                 # inherited-floors: host suite is an edge
    "### AI-verify record (required when gate_mode: ai-plan-verify)",
    "## 4 · TESTS & SCENARIOS",          # §4 absorbed the retired §2 scenario role
    "Tests live in:",                    # §4 declared-suite parser line
    "## 5 · BUILD",
    "Strategy actually used:",           # ADR harvest source
    "## 6 · VERIFY",
    "### Refute-read verdict",
    "### GATE RECORD",
    "Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>",
    "## 7 · OBSERVE",
    "### Decisions (ADR)",               # harvest refill anchor
    "### Spec delta",
    "### Competency deltas",
)


class TagCensusTest(unittest.TestCase):
    def setUp(self):
        self.text = TMPL_TREES[0].read_text(encoding="utf-8")

    def test_each_frozen_tag_opens_and_closes_exactly_once(self):
        pairs = re.findall(r"(?m)^<(/?)([a-z_]+)>$", self.text)
        for tag in FROZEN_TAGS:
            self.assertEqual([p for p in pairs if p == ("", tag)], [("", tag)], tag)
            self.assertEqual([p for p in pairs if p == ("/", tag)], [("/", tag)], tag)

    def test_no_tag_outside_the_frozen_vocab(self):
        pairs = re.findall(r"(?m)^<(/?)([a-z_]+)>$", self.text)
        self.assertEqual({name for _, name in pairs}, set(FROZEN_TAGS),
                         "a bare line-anchored <word> outside the frozen vocab is a "
                         "freeze-parser hazard — never add one casually")


class CommentBalanceTest(unittest.TestCase):
    def test_every_comment_opens_and_closes(self):
        text = TMPL_TREES[0].read_text(encoding="utf-8")
        self.assertEqual(text.count("<!--"), text.count("-->"),
                         "unmatched <!-- corrupts the freeze parser")


class EngineAnchorsTest(unittest.TestCase):
    def test_every_load_bearing_line_present(self):
        text = TMPL_TREES[0].read_text(encoding="utf-8")
        for anchor in ENGINE_ANCHORS:
            self.assertIn(anchor, text, f"engine anchor lost: {anchor!r}")

    def test_retired_surfaces_stay_retired(self):
        text = TMPL_TREES[0].read_text(encoding="utf-8")
        for gone in ("### Grounding", "### Deep checks", "### Live-verify evidence",
                     "### Advisor 3-lens verdict", "### Build expectations",
                     "Optimization stance:", "## 2 · SCENARIOS",
                     "Coverage target:", "Watch (reuse scenarios"):
            self.assertNotIn(gone, text, f"retired template surface returned: {gone!r}")


class ThreeTreeParityTest(unittest.TestCase):
    def test_byte_identical_across_trees(self):
        blobs = {p: p.read_bytes() for p in TMPL_TREES if p.exists()}
        self.assertEqual(len(blobs), len(TMPL_TREES), "a template twin is missing")
        self.assertEqual(len(set(blobs.values())), 1,
                         "template twins diverged — sync canon -> dogfood -> bundled")


if __name__ == "__main__":
    unittest.main()
