"""Read fan-out: read-only work (grounding · residue lenses · explore research) fans out to N
parallel readers with no wave and no worktree — facts merge; builds carry implicit decisions and
keep the wave machinery whole.

Red-first for task `read-fanout` (milestone dynamic-flow).
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
STREAMS = SKILL / "streams.md"

WAVE_REFUSALS = ("R:INTRADEP", "R:OVERLAP", "R:CYCLE")


def _streams() -> str:
    return STREAMS.read_text(encoding="utf-8")


def _fanout_section(text: str) -> str:
    m = re.search(r"^#+ .*read fan-out.*$", text, re.M | re.I)
    assert m, "no read fan-out section in streams.md"
    return text[m.start():]


def test_streams_documents_read_fanout():
    """covers: M1, A2 — no wave, no worktree for read-only delegates; read-only is pinned to
    the spawn instruction, not to good intentions."""
    sect = _fanout_section(_streams())
    assert re.search(r"no wave", sect, re.I) and re.search(r"no worktree", sect, re.I), \
        "free fan-out (no wave, no worktree) not stated"
    assert re.search(r"spawn (instruction|prompt)", sect, re.I), \
        "read-only must be pinned to the spawn instruction"


def test_streams_states_boundary_with_reason():
    """covers: M2, A4 — facts merge, decisions serialize, one write taints the delegate."""
    sect = _fanout_section(_streams())
    assert re.search(r"facts[^.\n]*merge", sect, re.I), "facts-merge reason missing"
    assert re.search(r"(implicit )?decisions", sect, re.I), "decisions-serialize reason missing"
    assert re.search(r"one write[^.\n]*(taints|wave)", sect, re.I), "the one-write-taints rule missing"


def test_streams_fanout_keeps_floors():
    """covers: M3 — no reader gates, fold through the main thread, security HARD-STOP."""
    sect = _fanout_section(_streams())
    assert re.search(r"(no reader|never) owns? a gate|no reader gates", sect, re.I), \
        "no-reader-owns-a-gate missing"
    assert re.search(r"HARD-STOP", sect), "security HARD-STOP missing from the fan-out floors"


def test_wave_refusals_survive_verbatim():
    """covers: R:WAVE_WEAKENED, E1 — the fan-out landed AND the wave's write-safety is intact."""
    text = _streams()
    _fanout_section(text)  # red until the section exists
    for code in WAVE_REFUSALS:
        assert code in text, f"wave refusal {code} lost"
    assert re.search(r"disjoint scope is the write-safety invariant", text), \
        "the disjoint-scope invariant sentence must survive verbatim"


def test_streams_within_budget():
    """covers: R:BUDGET, E2 — the fan-out landed AND streams.md fits the file budget."""
    text = _streams()
    _fanout_section(text)  # red until the section exists
    assert len(text.splitlines()) <= 350, "streams.md over the 350-line file budget"
