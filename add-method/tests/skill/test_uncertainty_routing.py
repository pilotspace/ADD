"""Uncertainty routing: intake tallies the unknowns explicitly and routes on them — high
unknowns go Explore-first, the closed floor still dominates everything, and the emitted
classification carries depth as a vetoable decision output.

Red-first for task `uncertainty-routing` (milestone dynamic-flow).
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"


def _intake() -> str:
    return (SKILL / "intake.md").read_text(encoding="utf-8")


def test_intake_names_unknowns_tally():
    """covers: M1, A4 — the shape-read carries an unknowns tally with the counting rule."""
    text = _intake()
    assert re.search(r"tally", text, re.I), "no unknowns tally in the shape-read"
    assert re.search(r"contract shape", text, re.I), \
        "the counting rule (an unknown counts when its answer would change the contract shape) is missing"


def test_intake_routes_high_unknowns_explore_first():
    """covers: M2, A5 — explore-first on high unknowns; uncertainty dominates size."""
    text = _intake()
    assert re.search(r"uncertainty dominates size", text, re.I), \
        "the routing rule `uncertainty dominates size` is not stated"


def test_intake_floor_dominates_tally():
    """covers: R:FLOOR_UNDERCUT, A8, E1 — the closed floor is checked first and beats the tally."""
    text = _intake()
    assert re.search(r"floor[^.\n]*(first|wins)[^.\n]*tally|tally[^.\n]*floor[^.\n]*(first|wins)",
                     text, re.I), "floor-beats-tally is not stated"


def test_intake_classification_carries_depth():
    """covers: M3 — the emitted classification names depth alongside lane and rationale."""
    text = _intake()
    assert re.search(r"\{\s*lane,\s*depth,\s*rationale", text), \
        "the classification shape does not carry depth"


def test_intake_within_budget():
    """covers: R:BUDGET, E2 — the tally step landed AND every budget holds."""
    text = _intake()
    assert re.search(r"tally", text, re.I), "red until the tally step exists"
    assert len(text.splitlines()) <= 350, "intake.md over the 350-line file budget"
    skill_lines = len((SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines())
    assert skill_lines <= 176, f"SKILL.md at {skill_lines} lines — past the pinned budget (176; re-pinned from 150 at 3.1.0)"
