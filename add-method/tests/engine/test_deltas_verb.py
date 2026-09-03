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
    """covers: M2 — a folded delta is decided, not carried; the open listing hides it.

    RE-AIMED by `dated-addressable-deltas`. The fixture used to hand-edit the literal
    `[TDD · open]`; once the head carried an id and a date that replace matched nothing, the
    delta stayed open, and the assertion passed VACUOUSLY because the text it looked for had
    never been written. It now folds through the verb, so the fixture cannot silently no-op.
    """
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "quality", "a settled one", evidence="e")
    add.learn(tmp_path, "quality", "a live open one", evidence="e")
    assert len(add.deltas(tmp_path)[0]) == 2, "the fixture must start with two open deltas"

    ok, note = add.fold(tmp_path, "quality", "a settled one")
    assert ok is True, note

    items, _ = add.deltas(tmp_path)
    assert all("settled one" not in t for _, _, t in items), "a folded delta must not appear in open"
    assert any("a live open one" in t for _, _, t in items), "the open delta must still be carried"
