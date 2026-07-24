#!/usr/bin/env python3
"""persona-at-intake: intake.md must LOAD the fitting persona before it sizes.

SKILL.md:88 already claims "at each decision point (intake · bundle · gate · close)
the fitting persona OWNS the gate report", and design.md carries the proven load-or-seed
mechanism. But intake.md — the guide that actually runs intake — has no load step, so a
persona owns the intake REPORT yet nothing loads one to shape the SIZING. This closes that:
intake.md must load the fitting persona before analyze/interview/size, via the SAME
match-else-seed mechanism, and keep it advisory (never a gate on the hard floors).
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
CANON_INTAKE = SKILL_TREES[0] / "intake.md"


def _canon():
    return CANON_INTAKE.read_text(encoding="utf-8")


def _headings(text):
    return re.findall(r"^##+ .*$", text, flags=re.MULTILINE)


class IntakeLoadsPersona(unittest.TestCase):
    def test_intake_loads_persona_before_analyze(self):                 # M1
        text = _canon()
        heads = _headings(text)
        analyze = [i for i, h in enumerate(heads) if "Analyze the request" in h]
        self.assertTrue(analyze, "sanity: intake.md must still have the Analyze step")

        persona_heads = [i for i, h in enumerate(heads)
                         if re.search(r"persona", h, re.IGNORECASE)]
        self.assertTrue(persona_heads,
                        "intake.md has no persona-load heading — the fitting persona must "
                        "be loaded to shape sizing, not only own the report (SKILL.md:88)")
        self.assertLess(min(persona_heads), analyze[0],
                        "the persona-load step must come BEFORE '## Analyze the request' — "
                        "the persona shapes the sizing, so it loads first")

    def test_load_step_mirrors_match_else_seed(self):                   # M2
        text = _canon()
        self.assertIn(".add/personas/", text,
                      "the load step must match a persona in .add/personas/ (design.md's mechanism)")
        self.assertIn(".add/personas-teacher/", text,
                      "the load step must seed from .add/personas-teacher/ when none fits — "
                      "the same match-else-seed path design.md uses, not a new one")

    def test_intake_persona_is_advisory(self):                         # M3
        # The persona shapes intake but may never convert intake's soft floors into hard gates.
        flat = re.sub(r"\s+", " ", _canon())
        # Locate the persona section: from its heading to the next heading.
        m = re.search(r"##+[^\n]*persona[^\n]*", _canon(), re.IGNORECASE)
        self.assertIsNotNone(m, "no persona section to check for the advisory caveat")
        section = re.split(r"\n##+ ", _canon()[m.start():], maxsplit=1)[0]
        sflat = re.sub(r"\s+", " ", section).lower()

        self.assertTrue(
            "advisory" in sflat or "never lower" in sflat or "never required" in sflat,
            "the persona step must state it is advisory / never required")
        self.assertTrue(
            "ask_human" in sflat or "security" in sflat,
            "the step must name a hard floor (ask_human / security) the persona can't lower")


class IntakeTwinParity(unittest.TestCase):
    def test_intake_twins_identical(self):                             # M4
        present = {t: (t / "intake.md") for t in SKILL_TREES if (t / "intake.md").is_file()}
        self.assertGreater(len(present), 1, "expected multiple intake.md twins")
        blobs = {t: f.read_bytes() for t, f in present.items()}
        first = next(iter(blobs.values()))
        for t, blob in blobs.items():
            self.assertEqual(blob, first, f"intake.md twin drift: {t}")


if __name__ == "__main__":
    unittest.main()
