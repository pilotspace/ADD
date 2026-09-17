"""B3 RED: accepted Task Must transfers keep exact identity and inherited authority."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tooling"))
import add  # noqa: E402


def _setup(root):
    add.init(root, "code", "B3")


def _task(root, slug, *, carries=(), sensitivity="mechanical", frozen=False, done=False):
    cid, note = add.new(root, "Task", slug, title=slug, depth="quick", sensitivity=sensitivity)
    assert cid, note
    path = root / cid.lstrip("/")
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"(?m)^status:.*$", "status: done" if done else "status: direction", raw)
    if carries:
        rows = "\n".join(f'  - "{edge}"' for edge in carries)
        raw = raw.replace("verified: []", f"carries:\n{rows}\nverified: []")
    body = ("## CARD\n"
            f"goal: {slug} owns an authored Must\n"
            "why: this duty has a named owner\n\n"
            "## RULES\n<must>\n- M1 preserve this exact duty (from: B3)\n</must>\n\n"
            "## PLAN\nregression: none · isolated B3 fixture\n\n"
            "## EDGES\n- E1 exact duty stays visible\n\n"
            "## CHECKS\n- test_duty · covers: M1, E1 · proves exact duty\nred-first: this case fails before Build\n\n"
            "## EVIDENCE\nreceipt: fixture\ngate: pending\n")
    raw = raw.split("---", 2)[0] + "---" + raw.split("---", 2)[1] + "---\n" + body
    if frozen:
        raw = raw.replace("verified: []", "verified:\n  - { by: plan:fixture, at: 2026-09-15, act: freeze, authority: plan, direction: \"sha256:fixture\" }")
    path.write_text(raw, encoding="utf-8")
    return cid, path


def _edge(source, destination):
    return f"/tasks/{source}.md#RULES:M1 -> /tasks/{destination}.md#RULES:M1"


def _refuse_freeze(root, cid, code):
    before = (root / cid.lstrip("/")).read_bytes()
    ok, note = add.freeze(root, cid, by="plan:fixture", authority="plan")
    assert ok is None, f"{code}: invalid transfer froze: {note!r}"
    assert code in note and "M1" in note, f"{code}: refusal lost exact Must identity: {note!r}"
    assert (root / cid.lstrip("/")).read_bytes() == before, "refusal wrote an acceptance stamp"


def test_accepted_carry_preserves_original_and_seals_mapping(tmp_path):
    _setup(tmp_path)
    _, source = _task(tmp_path, "original", frozen=True, done=True)
    cid, destination = _task(tmp_path, "destination", carries=[_edge("original", "destination")])
    before = source.read_bytes()
    ok, note = add.freeze(tmp_path, cid, by="plan:fixture", authority="plan")
    assert ok, note
    stamp = add.read(destination, "T2")["fm"]["verified"][-1]
    assert stamp.get("carries", "").startswith("sha256:"), "destination freeze did not seal its carry"
    assert source.read_bytes() == before, "acceptance rewrote closed original"
    assert "M1" in destination.read_text(encoding="utf-8"), "destination duty disappeared"


@pytest.mark.parametrize("edge", [
    "/tasks/missing.md#RULES:M1 -> /tasks/destination.md#RULES:M1",
    "/tasks/original.md#RULES:M99 -> /tasks/destination.md#RULES:M1",
    "/tasks/original.md#EXIT:C1 -> /tasks/destination.md#RULES:M1",
    "/milestones/original.md#EXIT:C1 -> /tasks/destination.md#RULES:M1",
    "/tasks/original.md#RULES:M1 -> /tasks/other.md#RULES:M1",
])
def test_dangling_wrong_id_and_wrong_type_refuse_before_freeze(tmp_path, edge):
    _setup(tmp_path)
    _task(tmp_path, "original", frozen=True)
    cid, _ = _task(tmp_path, "destination", carries=[edge])
    _refuse_freeze(tmp_path, cid, "R:BAD_CARRY")


def test_post_freeze_edit_refuses_at_done(tmp_path):
    _setup(tmp_path)
    _, source = _task(tmp_path, "original", frozen=True, done=True)
    _task(tmp_path, "other", frozen=True, done=True)
    cid, destination = _task(tmp_path, "destination", carries=[_edge("original", "destination")])
    ok, note = add.freeze(tmp_path, cid, by="plan:fixture", authority="plan")
    assert ok, note
    accepted_source = source.read_bytes()
    destination.write_text(destination.read_text().replace(
        _edge("original", "destination"), _edge("other", "destination")), encoding="utf-8")
    raw = destination.read_text().replace("verified:\n", "verified:\n  - { by: plan:fixture, at: 2026-09-15, act: gate, authority: plan, outcome: PASS }\n", 1)
    destination.write_text(raw, encoding="utf-8")
    before = destination.read_bytes()
    ok, _, note = add.done(tmp_path, cid)
    assert ok is None and "R:UNACCEPTED_CARRY" in note, f"changed mapping closed: {note!r}"
    assert destination.read_bytes() == before and source.read_bytes() == accepted_source


@pytest.mark.parametrize("mode", ["duplicate", "self", "two_node"])
def test_duplicate_and_cycle_refuse_before_freeze(tmp_path, mode):
    _setup(tmp_path)
    _task(tmp_path, "original", frozen=True)
    if mode == "duplicate":
        _task(tmp_path, "first", carries=[_edge("original", "first")], frozen=True)
        cid, _ = _task(tmp_path, "second", carries=[_edge("original", "second")])
        code = "R:DUPLICATE_CARRY"
    elif mode == "self":
        cid, _ = _task(tmp_path, "first", carries=[_edge("first", "first")])
        code = "R:CYCLIC_CARRY"
    else:
        _task(tmp_path, "first", carries=[_edge("second", "first")], frozen=True)
        cid, _ = _task(tmp_path, "second", carries=[_edge("first", "second")])
        code = "R:CYCLIC_CARRY"
    _refuse_freeze(tmp_path, cid, code)


def test_security_authority_inherits_across_hops_without_reusing_approval(tmp_path):
    _setup(tmp_path)
    _task(tmp_path, "original", sensitivity="security", frozen=True, done=True)
    _task(tmp_path, "first", carries=[_edge("original", "first")], frozen=True)
    cid, destination = _task(tmp_path, "second", carries=[_edge("first", "second")])
    assert add.authority_for(add.scan(tmp_path), cid) == "human", "two-hop carry lowered security floor"
    before = destination.read_bytes()
    ok, note = add.freeze(tmp_path, cid, by="plan:fixture", authority="plan")
    assert ok is None and ("R:LOWERED_CARRY_AUTHORITY" in note or "human" in note.lower()), note
    assert destination.read_bytes() == before, "process actor reused original human approval"


def test_no_carry_control_and_b2_move_are_independent(tmp_path):
    _setup(tmp_path)
    cid, path = _task(tmp_path, "ordinary")
    ok, note = add.freeze(tmp_path, cid, by="plan:fixture", authority="plan")
    assert ok, note
    assert not (add.read(path, "T2")["fm"].get("carries") or []), "ordinary Task acquired a carry"
    b2 = (Path(__file__).resolve().parents[3] / ".add/milestones/loop-that-closes.md")
    before = b2.read_bytes()
    assert "[~]" in b2.read_text(), "B2 counterexample lost its moved EXIT line"
    assert b2.read_bytes() == before, "B3 read changed B2 historical milestone"
