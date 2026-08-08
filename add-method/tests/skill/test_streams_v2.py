"""streams.md v2 — the parallel-builder pipeline is documented and reachable, four floors intact.

The engine now HAS `wave` + `join`. The skill doc must teach an agent to actually run a parallel wave
(plan → worktree → build → join), no longer say "deferred / do not fan out", name the safety invariants
the engine enforces, and keep every one of the four floors that hold a delegate to hands-not-permission.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STREAMS = REPO / "skill" / "add" / "streams.md"


def test_streams_v2_documents_the_pipeline():
    """covers: M1 — the doc names `add wave` and `add join` and drops the v1 hard deferral."""
    text = STREAMS.read_text(encoding="utf-8")
    low = text.lower()
    assert "add wave" in text and "add join" in text, "the v2 pipeline must cite the real wave/join verbs"
    assert "worktree" in low, "the v2 pipeline must document git-worktree isolation per stream"
    assert "do not fan out" not in low and "do NOT fan out" not in text, \
        "the v1 deferral must be gone — the shipped capability is now reachable"
    assert "deferred" not in low, "streams must no longer describe parallel streams as deferred"


def test_streams_v2_keeps_the_four_floors():
    """covers: M2, R:LOWERFLOOR — no floor is dropped or softened in the N-builder rewrite."""
    low = STREAMS.read_text(encoding="utf-8").lower()
    assert "hard-stop" in low, "security = HARD-STOP must survive"
    assert "never" in low and "gate" in low, "a stream must never own a gate"
    assert "escalate" in low, "high-risk must still escalate to the human"
    assert "scope" in low and "frozen" in low, "a stream stays in scope / never edits a frozen gives"


def test_streams_v2_names_the_invariants():
    """covers: M3 — the doc names the engine-enforced safety invariants of a wave."""
    text = STREAMS.read_text(encoding="utf-8")
    assert "R:OVERLAP" in text and "disjoint scope" in text.lower(), "disjoint-scope invariant must be named"
    assert "R:INTRADEP" in text, "the no-intra-wave-dependency invariant must be named"
    assert "PASS-only" in text or "pass-only" in text.lower(), "join's PASS-only rule must be named"
