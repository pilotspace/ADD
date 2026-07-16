#!/usr/bin/env python3
"""Marker guard for the decision arc in the book (task: arc-book-align, milestone v23).

Tasks 1–2 shipped the decision arc into the skill: gate-udd.md renders it,
all seven gate guides cue it. This task makes the METHOD'S OWN PROSE explain it —
a GLOSSARY term + one chapter mention — so a reader meets the arc as a defined
concept, not only as skill machinery (exit-criterion 3: the book + GLOSSARY
describe the decision arc consistently with the gates).

This is a PRESENCE FENCE, not a quality proof. It guards that the named term
exists and that its three-part label stays consistent with the gates the skill
renders (`goal:` / `done:` / `plan:`). The substantive guard remains the human
verify read plus the standing suites (test_ubiquitous_language for lint,
test_bundle_parity + test_v8_docs for tree agreement).

The gate-consistency assertion is the one that matters: MILESTONE.md called the
arc "goal · achievement · plan" but the shipped reports render `done:`. The book
must define it as goal · done · plan (achievement glossed onto `done`) or it
contradicts every gate report — the exact inconsistency this task removes.

Red before the edits (term + mention absent), green after.
Run: python3 -m unittest test_decision_arc_book -v
"""
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
CANON_DOCS = _TOOLING.parent / "docs"
GLOSSARY = CANON_DOCS / "appendix-c-glossary.md"
FLOW = CANON_DOCS / "02-the-flow.md"

MIDDOT = "·"  # · — the trio separator the gates and glossary use


def _read(path: Path) -> str:
    # design-for-failure: a missing canonical doc is a loud, named failure, not a
    # confusing FileNotFoundError mid-assert.
    if not path.exists():
        raise AssertionError(f"canonical doc missing: {path}")
    return path.read_text(encoding="utf-8")


def _arc_definition(glossary_text: str) -> str:
    """The GLOSSARY paragraph that defines the term — from '**The decision arc**'
    to the next blank line. Works whether the entry is one physical line or wrapped."""
    marker = "**The decision arc**"
    idx = glossary_text.find(marker)
    if idx == -1:
        return ""
    rest = glossary_text[idx:]
    end = rest.find("\n\n")
    return rest if end == -1 else rest[:end]


def _chapter_arc_paragraph(flow_text: str) -> str:
    """The 02-the-flow markdown paragraph that mentions the arc (the block containing
    'decision arc'). Used to fence gate coverage in the chapter, not the whole file."""
    for para in flow_text.split("\n\n"):
        if "decision arc" in para.lower():
            return para
    return ""


class DecisionArcBookMarkerTest(unittest.TestCase):
    def test_glossary_defines_the_arc(self):
        self.assertIn(
            "decision arc",
            _read(GLOSSARY).lower(),
            "appendix-c-glossary.md must define the term 'The decision arc'",
        )

    def test_chapter_gives_the_term_a_home(self):
        self.assertIn(
            "decision arc",
            _read(FLOW).lower(),
            "02-the-flow.md must mention the decision arc (the term's chapter home)",
        )

    def test_label_reconciles_with_gates(self):
        # the consistency guard: goal · done · plan (the shipped labels), achievement
        # glossed onto done — NEVER named as the trio "goal · achievement · plan".
        defn = _arc_definition(_read(GLOSSARY))
        self.assertTrue(defn, "glossary term '**The decision arc**' not found")
        for label in ("goal", "done", "plan", "achievement"):
            self.assertIn(
                label,
                defn,
                f"the decision-arc definition must carry '{label}' "
                "(goal · done · plan, with achievement glossed onto done)",
            )
        wrong_trio = f"goal {MIDDOT} achievement {MIDDOT} plan"
        self.assertNotIn(
            wrong_trio,
            defn,
            "the arc must NOT be named 'goal · achievement · plan' — the gates "
            "render `done:`, so that trio contradicts every shipped gate report "
            "(arc_label_inconsistent_with_gates)",
        )

    def test_arc_described_as_presentation(self):
        # not-a-gate framing: the definition says presentation and names a gate
        # outcome it does NOT change.
        defn = _arc_definition(_read(GLOSSARY))
        self.assertTrue(defn, "glossary term '**The decision arc**' not found")
        self.assertIn(
            "presentation",
            defn.lower(),
            "the arc must be described as presentation only (arc_misdescribed_as_gate)",
        )
        self.assertTrue(
            any(o in defn for o in ("PASS", "RISK-ACCEPTED", "HARD-STOP")),
            "the arc definition must name a gate outcome it never changes "
            "(PASS / RISK-ACCEPTED / HARD-STOP)",
        )

    def test_chapter_spans_all_wired_gates(self):
        # v2 gate-coverage fence (change-request): the arc is wired at all SEVEN gates
        # (test_arc_gate_wiring), but the v1 chapter named only five — dropping the
        # baseline approval and scope. A partial list contradicts the term's "every
        # decision point". Fence the two it dropped so the gap class can't recur.
        para = _chapter_arc_paragraph(_read(FLOW))
        self.assertTrue(para, "02-the-flow.md arc paragraph not found")
        for gate in ("baseline", "scope"):
            self.assertIn(
                gate,
                para.lower(),
                f"the chapter arc paragraph must name the '{gate}' gate — the arc is "
                "wired at all seven gates (test_arc_gate_wiring), not the five the v1 "
                "list named (arc_gate_coverage_incomplete)",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
