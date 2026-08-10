"""Red suite for e4 `build-node-verbs` — new · freeze · done.

One test per Must / Reject of tasks/build-node-verbs. The hardest thing here is M3's
boundary: the engine must refuse to CREATE a record no evidence entitles, while never
blocking a human who records one with their own authority. Both directions are asserted.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Verbs")
    return tmp_path


# ------------------------------------------------------------------------- new (M1)


def test_new_creates_typed_node(bundle):
    """covers: M1 — the node carries its type and the sections that type requires."""
    cid, note = add.new(bundle, "Task", "reject-overlaps", title="Reject overlaps")
    node = add.read(bundle / cid.lstrip("/"), "T2")
    assert node["fm"]["type"] == "Task"
    assert node["fm"]["title"] == "Reject overlaps"
    assert "## CARD" in node["body"]


def test_new_is_attributed(bundle):
    """covers: M1 — nothing the engine writes is unattributed (OKF §10)."""
    cid, note = add.new(bundle, "Task", "attributed", title="A")
    gen = add.read(bundle / cid.lstrip("/"), "T0")["fm"]["generated"]
    assert gen.get("by") and gen.get("at")


def test_new_rejects_duplicate_slug(bundle):
    """covers: M1, R:DUPSLUG — a collision reports; it never silently suffixes."""
    add.new(bundle, "Task", "twice", title="First")
    before = (bundle / "tasks" / "twice.md").read_bytes()

    cid, note = add.new(bundle, "Task", "twice", title="Second")
    assert cid is None, "a duplicate slug was created anyway"
    assert "twice" in note
    assert (bundle / "tasks" / "twice.md").read_bytes() == before, "the original was overwritten"
    assert not (bundle / "tasks" / "twice-2.md").exists(), "the slug was silently renamed"


# ----------------------------------------------------------------------- freeze (M2)


def test_freeze_appends_stamp(bundle, draft):
    """covers: M2 — `verified[]` gains a freeze stamp."""
    cid, _ = add.new(bundle, "Task", "frozen", title="F")
    draft(bundle, cid)
    add.freeze(bundle, cid, by="human:tindang")
    stamps = add.read(bundle / cid.lstrip("/"), "T0")["fm"]["verified"]
    assert any(s.get("act") == "freeze" for s in stamps)


def test_freeze_preserves_comments(bundle):
    """covers: M2, M5, R:REGEN — a transition is surgical, so rationale comments survive."""
    cid, _ = add.new(bundle, "Task", "commented", title="C")
    path = bundle / cid.lstrip("/")
    raw = path.read_text().replace("status:", "# a comment carrying rationale\nstatus:", 1)
    path.write_text(raw)

    add.freeze(bundle, cid, by="human:tindang")
    assert "# a comment carrying rationale" in path.read_text()


def test_refreeze_keeps_old_stamp(bundle, draft):
    """covers: M2, R:INPLACE — §3.5: a changed interface appends, the old stamp remains."""
    cid, _ = add.new(bundle, "Task", "twice-frozen", title="T")
    draft(bundle, cid)
    add.freeze(bundle, cid, by="human:tindang")
    add.freeze(bundle, cid, by="human:tindang")
    stamps = add.read(bundle / cid.lstrip("/"), "T0")["fm"]["verified"]
    acts = [s.get("act") for s in stamps]
    assert acts.count("freeze") >= 1 and "refreeze" in acts, f"no refreeze recorded: {acts}"
    assert len(stamps) == 2, "a stamp was replaced instead of appended"


# ---------------------------------------------- done refuses to forge, but does not guard (M3)


def test_done_refuses_without_gate(bundle):
    """covers: M3, R:FORGE — no gate stamp, no transition, and the note says why."""
    cid, _ = add.new(bundle, "Task", "ungated", title="U")
    ok, missing, note = add.done(bundle, cid)
    assert ok is False
    assert missing, "nothing was reported as missing"
    assert add.read(bundle / cid.lstrip("/"), "T0")["fm"]["status"] != "done"


def test_done_transitions_with_gate(bundle):
    """covers: M3 — with an entitling gate stamp present, the transition happens."""
    cid, _ = add.new(bundle, "Task", "gated", title="G")
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T0")
    raw = add.append_item(n["raw"], "verified",
                          '{ by: "human:tindang", at: 2026-07-29, act: gate, authority: human, outcome: PASS }')
    add.write(path, f"---\n{raw}\n---\n{n['body']}")

    ok, missing, note = add.done(bundle, cid)
    assert ok is True, f"a gated task was refused: {missing}"
    assert add.read(path, "T0")["fm"]["status"] == "done"


def test_done_does_not_block_human_record(bundle):
    """covers: M3 — the engine refuses to FORGE, never to let a human record their own act.

    This is the line between notary and guard. If the engine can prevent a human from
    writing their own stamp with their own authority, law 3 is violated in the other
    direction.
    """
    cid, _ = add.new(bundle, "Task", "self-recorded", title="S")
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T0")
    raw = add.set_key(n["raw"], "status", "done")
    add.write(path, f"---\n{raw}\n---\n{n['body']}")
    assert add.read(path, "T0")["fm"]["status"] == "done", "the engine blocked a human's own record"


# -------------------------------------------------------------- the authority ladder (M4)


def test_authority_floor_from_sensitivity(bundle):
    """covers: M4 — FORMAT §3.1's table, executable."""
    graph = add.scan(bundle)
    cid, _ = add.new(bundle, "Task", "sec", title="S", sensitivity="security")
    cid2, _ = add.new(bundle, "Task", "mech", title="M", sensitivity="mechanical")
    graph = add.scan(bundle)
    assert add.authority_for(graph, cid) == "human"
    assert add.authority_for(graph, cid2) == "process"


def test_authority_raised_by_sensitive_path(bundle):
    """covers: M4, R:AUTHDROP — A17 outranks the declared sensitivity, mechanically."""
    index = bundle / "index.md"
    n = add.read(index, "T0")
    raw = add.set_key(n["raw"], "sensitive_paths", "[ engine/**.py ]")
    add.write(index, f"---\n{raw}\n---\n{n['body']}")

    cid, _ = add.new(bundle, "Task", "touches-engine", title="T",
                     sensitivity="mechanical", scope=["engine/core.py"])
    assert add.authority_for(add.scan(bundle), cid) == "human", \
        "a scope match failed to raise the floor — A17 was not applied"


# ------------------------------------------------------------- surgical + next + floor


def test_transition_is_surgical(bundle):
    """covers: M5, R:REGEN — a transition touches only the keys it names."""
    cid, _ = add.new(bundle, "Task", "surgical", title="S")
    path = bundle / cid.lstrip("/")
    before = path.read_text().splitlines()

    add.freeze(bundle, cid, by="human:tindang")
    after = path.read_text().splitlines()
    changed = [l for l in before if l not in after]
    assert changed == ["verified: []"] or changed == [], f"unexpected lines changed: {changed}"


def test_every_verb_returns_next(bundle):
    """covers: M6 — the engine teaches at the moment of use (law 4)."""
    cid, note_new = add.new(bundle, "Task", "nexted", title="N")
    _, note_freeze = add.freeze(bundle, cid, by="human:tindang")
    _, _, note_done = add.done(bundle, cid)
    for note in (note_new, note_freeze, note_done):
        assert "next:" in note.lower(), f"no next: line in {note!r}"


def test_live_bundle_still_validates(tmp_path):
    """covers: M5 — the M0 oracle still exits 0 after the engine writes transitions."""
    add.init(tmp_path, "code", "Floor")
    cid, _ = add.new(tmp_path, "Task", "floor-check", title="F")
    add.freeze(tmp_path, cid, by="human:tindang")
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "validate_bundle.py"), str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"the engine wrote a bundle the oracle rejects:\n{r.stdout}"


def test_append_to_inline_empty_list(bundle):
    """covers: M2, R:REGEN — regression: `verified: []` must become a block list.

    Found by e4, not by e1: e1's suite only appended to `scope:`, which already had items,
    so the inline-empty-list path was never exercised. The defect was silent — the item
    landed under a surviving `[]` and parsed back as an empty list.
    """
    raw = 'type: Task\nverified: []\nscope:\n  - a.py\n'
    out = add.append_item(raw, "verified", '{ by: "x", act: freeze }')
    fm, _ = add.parse(f"---\n{out}\n---\n")
    assert len(fm["verified"]) == 1, f"append to an inline empty list was lost: {out!r}"
    assert fm["verified"][0]["act"] == "freeze"
    assert fm["scope"] == ["a.py"], "an unrelated list was disturbed"
