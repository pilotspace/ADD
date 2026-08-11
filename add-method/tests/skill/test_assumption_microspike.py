"""Micro-spike discharge: a high cost-if-wrong assumption may be answered before freeze by a
bounded, recorded micro-explore — `found:` plus its evidence ref on the line, the line never
deleted, the outgrown question routed to the Explore lane. Optional, never required.

Red-first for task `assumption-microspike` (milestone dynamic-flow).
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
DIRECTION = SKILL / "phases" / "direction.md"

PROBE_GRAMMAR = "probe: <what shipped behavior must show>"


def _direction() -> str:
    return DIRECTION.read_text(encoding="utf-8")


def test_direction_documents_microspike_discharge():
    """covers: M1, A3 — the bounded micro-explore discharge exists, keyed on cost-if-wrong."""
    text = _direction()
    assert re.search(r"micro-explore|micro-spike", text, re.I), "no micro-explore discharge documented"
    assert re.search(r"(micro-explore|micro-spike)[^#]*cost", text, re.I | re.S), \
        "the discharge is not keyed on cost-if-wrong"


def test_found_grammar_requires_evidence():
    """covers: M2, A8 — found-line grammar with a required evidence ref; the line stays."""
    text = _direction()
    assert re.search(r"found:", text), "the found-line grammar is not documented"
    assert re.search(r"found:[^\n]*evidence", text, re.I), \
        "found without its evidence ref — the grammar must require the ref"
    assert re.search(r"never deleted|stays (in|on)", text, re.I), \
        "the discharged line must stay on the record"


def test_discharge_escalates_to_explore_lane():
    """covers: M3 — an outgrown question routes to the Explore lane through intake."""
    text = _direction()
    assert re.search(r"(micro-explore|micro-spike)[^#]*Explore lane", text, re.I | re.S), \
        "the escalation to the Explore lane is not named"


def test_discharge_stays_optional():
    """covers: R:CEREMONY_CREEP — optional, and a priced guess stays legitimate."""
    text = _direction()
    assert re.search(r"(micro-explore|micro-spike)[^#]*(optional|MAY)", text, re.S), \
        "the discharge must be stated as optional"
    assert re.search(r"priced guess", text, re.I), \
        "a priced guess must remain a legitimate outcome"


def test_direction_within_budget():
    """covers: R:BUDGET, E1, E2 — the discharge landed AND budgets + probe grammar hold."""
    text = _direction()
    assert re.search(r"micro-explore|micro-spike", text, re.I), "red until the discharge exists"
    assert len(text.splitlines()) <= 350, "direction.md over the 350-line file budget"
    assert PROBE_GRAMMAR in text, "the probe grammar line the gate binds must survive verbatim"
