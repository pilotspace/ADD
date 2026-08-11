"""The `next:` affordances tell the truth (field-report findings #4/#5).

A cold agent obeys `next:`. Two of them lied: `status` said `add brief` for a task just created (its
node isn't authored yet — freeze is what's next), and a closed task's CARD still read `next: add
freeze`. Both are fixed from one BEAT_NEXT map: status names the beat's verb, and the CARD self-heals.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _card(root, cid):
    return add.card_of(add.read(root / cid.lstrip("/"), "T2")["body"])


def test_status_hints_freeze_for_an_unfrozen_task(tmp_path):
    """covers: M1 — a fresh (unfrozen) task points at freeze, never the premature brief."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Task", "t", title="t")
    out = add.status(tmp_path)
    nxt = out.strip().splitlines()[-1]
    assert "freeze" in nxt and "brief" not in nxt, f"an unfrozen task should point at freeze: {nxt!r}"


def test_status_hints_brief_for_a_frozen_task(tmp_path, draft):
    """covers: M1 — once frozen (authoring done), the composed brief is the sensible next step."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    draft(tmp_path, cid)
    add.freeze(tmp_path, cid, by="human:x")
    out = add.status(tmp_path)
    nxt = out.strip().splitlines()[-1]
    assert "brief" in nxt, f"a frozen task should point at brief: {nxt!r}"


def test_render_card_refreshes_next_with_the_beat(tmp_path):
    """covers: M2, R:STALEFREEZE — a done task's CARD next: becomes `add status`, never `add freeze`."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    add._transition(tmp_path, cid, sets={"status": "done"})  # frontmatter done, CARD still 'direction'
    add.render_card(tmp_path, cid)
    card = _card(tmp_path, cid)
    assert "add freeze" not in card, "a done card must not still say add freeze (R:STALEFREEZE)"
    assert "beat: done" in card and "add status" in card, f"next: must track the done beat:\n{card}"
