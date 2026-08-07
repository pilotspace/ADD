"""`add deltas` lists every open delta across the five specs — the loop's carried inventory.

The AI reads open deltas at close to propose the next tasks (loop.md). A reader over the frozen
grammar: it surfaces `open` and, by design, hides `folded`/`rejected` — those are decided, not carried.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def test_deltas_lists_every_open_delta(tmp_path):
    """covers: M1 — every open delta across specs is listed with its spec + competency."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "domain", "an entity was wrong", evidence="scenario x failed")
    add.learn(tmp_path, "method", "a harness helped", evidence="build log")
    items, note = add.deltas(tmp_path)
    texts = " ".join(t for _, _, t in items)
    assert "an entity was wrong" in texts and "a harness helped" in texts, items
    specs = {s for s, _, _ in items}
    assert {"domain", "method"} <= specs, f"deltas must name each delta's spec: {specs}"
    assert "DDD" in {c for _, c, _ in items} and "ADD" in {c for _, c, _ in items}


def test_deltas_excludes_folded(tmp_path):
    """covers: M2 — a folded delta is decided, not carried; the open listing hides it."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "quality", "a live open one", evidence="e")
    # hand-fold one delta (as the human would): flip its status token
    spec = tmp_path / "specs" / "quality.md"
    spec.write_text(spec.read_text(encoding="utf-8").replace(
        "[TDD · open] a live open one", "[TDD · folded] a settled one"), encoding="utf-8")
    items, _ = add.deltas(tmp_path)
    assert all("settled one" not in t for _, _, t in items), "a folded delta must not appear in open"
