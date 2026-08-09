"""`add fold` retags an open delta `folded` — the human's consolidation, recorded by the engine.

The AI never self-folds (deltas.md): a human names which delta merges into its spec, and fold flips
its status token open→folded. It refuses when nothing matches, so a fold never silently no-ops.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def test_fold_retags_the_matching_open_delta(tmp_path):
    """covers: M1 — the matched open delta becomes folded; open hides it, folded shows it."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "system", "must reject a cross-tenant token", evidence="scenario failed")
    ok, note = add.fold(tmp_path, "system", "cross-tenant")
    assert ok is True, note
    assert not any("cross-tenant" in t for _, _, t in add.deltas(tmp_path, "open")[0]), "still open"
    assert any("cross-tenant" in t for _, _, t in add.deltas(tmp_path, "folded")[0]), "not folded"


def test_fold_refuses_without_a_match(tmp_path):
    """covers: R:NOMATCH — no open delta matches → refuse, change nothing."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "system", "a real open delta", evidence="e")
    ok, note = add.fold(tmp_path, "system", "nothing-like-this")
    assert ok is False and "match" in note.lower()
    assert any("a real open delta" in t for _, _, t in add.deltas(tmp_path, "open")[0]), \
        "a refused fold must leave the open delta untouched"
