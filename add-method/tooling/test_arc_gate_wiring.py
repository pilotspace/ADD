#!/usr/bin/env python3
"""Marker guard for arc gate-wiring (task: arc-gate-wiring, milestone v23).

Task 1 (report-arc) defined the ARC block centrally in report-template.md. This
task makes it TRACEABLE IN EVERY GATE PATH: each of the seven gate-path guides
gains a one-line cue at its human-approval moment, pointing at report-template.md
— so a reviewer opening any single guide finds the arc named there, not only via
the central SKILL.md pointer.

The cue POINTS central (progressive disclosure): the per-gate examples + the
seven-gate rule stay owned by report-template.md; a guide naming the arc must not
re-spell that content. The seven gates map to seven files (three naming systems
do NOT align — pin them here so wiring six and missing one fails loudly):

    baseline-lock   -> phases/0-setup.md
    contract-freeze -> phases/3-plan.md
    verify          -> phases/6-verify.md
    intake          -> intake.md
    scope           -> scope.md
    milestone-close -> loop.md
    graduation      -> graduate.md

The reconcile rule (a gate report's FLAGS must reconcile with `report --decide`'s
open-item count) was FOLDED into report-template.md by human choice at the §3
freeze — asserted as a SEPARATE case so the wiring's green bar never depends on it.

Red before the cue edits, green after. Run: python3 -m unittest test_arc_gate_wiring -v
"""
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
CANON_SKILL = _TOOLING.parent / "skill" / "add"

# the seven gate -> file pairs (frozen §3); paths relative to the skill root
GATE_FILES = {
    "baseline-lock": "phases/0-setup.md",
    "contract-freeze": "phases/3-plan.md",
    "verify": "phases/6-verify.md",
    "intake": "intake.md",
    "scope": "scope.md",
    "milestone-close": "loop.md",
    "graduation": "graduate.md",
}


def _read(rel: str) -> str:
    return (CANON_SKILL / rel).read_text(encoding="utf-8")


class ArcGateWiringMarkerTest(unittest.TestCase):
    def test_every_gate_guide_names_the_arc(self):
        # the all-7 guard: wiring six and missing one fails here, naming the gap.
        missing = []
        for gate, rel in GATE_FILES.items():
            text = _read(rel)
            names_template = "report-template" in text
            names_arc = "ARC" in text or "arc" in text
            if not (names_template and names_arc):
                missing.append(f"{gate} ({rel})")
        self.assertEqual(
            missing,
            [],
            "gate path(s) left unwired (no arc cue naming report-template):\n  "
            + "\n  ".join(missing),
        )

    def test_cue_points_central_not_respelled(self):
        # progressive disclosure: a guide names the arc but must NOT re-spell the
        # central per-gate example labels. report-template owns those four examples.
        # The verify example line in report-template is the canonical re-spell marker.
        respell_marker = "report-arc tests"  # from report-template's worked example
        for gate, rel in GATE_FILES.items():
            self.assertNotIn(
                respell_marker,
                _read(rel),
                f"{gate} ({rel}) re-spells report-template's per-gate example "
                "instead of pointing at it (arc_duplicated)",
            )

    def test_skill_central_pointer_still_present(self):
        # task 1's central pointer must stay (the cues add to it, never replace it).
        skill = _read("SKILL.md")
        self.assertIn("report-template", skill)
        self.assertIn("ARC", skill)

    def test_reconcile_rule_folded_into_report_template(self):
        # SEPARATE case (human folded it here at the freeze): if this regresses the
        # wiring above still passes. The rule lives centrally, not per-guide.
        tmpl = _read("report-template.md")
        self.assertIn(
            "reconcile",
            tmpl,
            "report-template.md must gain the digest-reconciliation rule "
            "(FLAGS must reconcile with report --decide's open-item count)",
        )
        self.assertIn(
            "report --decide",
            tmpl,
            "the reconcile rule must name the `report --decide` open-item count",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
