"""B3 RED: accepted Task Must transfers keep exact identity and inherited authority."""
import re
import sys
from pathlib import Path

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
    path.write_text(raw, encoding="utf-8")
    if frozen:
        # A source fixture must carry a real, current seal. A placeholder digest would test
        # acceptance of an unattested obligation instead of acceptance of a carried one.
        node = add.read(path, "T2")
        authority = add.authority_for(add.scan(root), cid)
        signer = "human:fixture" if authority == "human" else "plan:fixture"
        stamp = (f'{{ by: "{signer}", at: 2026-09-15, act: freeze, authority: {authority}, '
                 f'direction: "{add.direction_digest(node)}", carries: "{add.carry_digest(node)}" }}')
        add.write(path, f"---\n{add.append_item(node['raw'], 'verified', stamp)}\n---\n{node['body']}")
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
    node = add.read(destination, "T2")
    gate = '{ by: "plan:fixture", at: 2026-09-15, act: gate, authority: plan, outcome: PASS }'
    add.write(destination, f"---\n{add.append_item(node['raw'], 'verified', gate)}\n---\n{node['body']}")
    ok, _, note = add.done(tmp_path, cid)
    assert ok, note
    assert source.read_bytes() == before, "closing the destination rewrote closed original"
    assert add.read(destination, "T0")["fm"]["status"] == "done"


BAD_EDGES = (
    "/tasks/missing.md#RULES:M1 -> /tasks/destination.md#RULES:M1",
    "/tasks/original.md#RULES:M99 -> /tasks/destination.md#RULES:M1",
    "/tasks/original.md#EXIT:C1 -> /tasks/destination.md#RULES:M1",
    "/milestones/original.md#EXIT:C1 -> /tasks/destination.md#RULES:M1",
    "/tasks/original.md#RULES:M1 -> /tasks/other.md#RULES:M1",
)


def test_dangling_wrong_id_and_wrong_type_refuse_before_freeze(tmp_path):
    for index, edge in enumerate(BAD_EDGES):
        root = tmp_path / str(index)
        root.mkdir()
        _setup(root)
        _task(root, "original", frozen=True)
        cid, _ = _task(root, "destination", carries=[edge])
        _refuse_freeze(root, cid, "R:BAD_CARRY")


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


def test_removed_destination_carry_refuses_gate_and_done(tmp_path):
    _setup(tmp_path)
    _, source = _task(tmp_path, "original", frozen=True, done=True)
    cid, destination = _task(tmp_path, "destination", carries=[_edge("original", "destination")])
    assert add.freeze(tmp_path, cid, by="plan:fixture", authority="plan")[0]
    accepted_source = source.read_bytes()
    destination.write_text(destination.read_text().replace(
        f'carries:\n  - "{_edge("original", "destination")}"\n', ""), encoding="utf-8")
    before = destination.read_bytes()
    ok, note = add.gate(tmp_path, cid, "PASS", by="plan:fixture")
    assert ok is None and "R:UNACCEPTED_CARRY" in note, note
    assert destination.read_bytes() == before
    node = add.read(destination, "T2")
    gate = '{ by: "plan:fixture", at: 2026-09-15, act: gate, authority: plan, outcome: PASS }'
    add.write(destination, f"---\n{add.append_item(node['raw'], 'verified', gate)}\n---\n{node['body']}")
    before = destination.read_bytes()
    ok, _, note = add.done(tmp_path, cid)
    assert ok is None and "R:UNACCEPTED_CARRY" in note, note
    assert destination.read_bytes() == before and source.read_bytes() == accepted_source


def test_removed_intermediate_carry_cannot_be_laundered_downstream(tmp_path):
    _setup(tmp_path)
    _task(tmp_path, "origin", frozen=True, done=True)
    _, first = _task(tmp_path, "first", carries=[_edge("origin", "first")], frozen=True)
    text = first.read_text()
    first.write_text(text.replace(
        f'carries:\n  - "{_edge("origin", "first")}"\n', ""), encoding="utf-8")
    cid, second = _task(tmp_path, "second", carries=[_edge("first", "second")])
    before = second.read_bytes()
    ok, note = add.freeze(tmp_path, cid, by="plan:fixture", authority="plan")
    assert ok is None and "R:UNACCEPTED_CARRY" in note, note
    assert "first.md#RULES:M1" in note and second.read_bytes() == before


def test_legacy_refreeze_cannot_erase_intermediate_carry_history(tmp_path):
    _setup(tmp_path)
    _task(tmp_path, "origin", sensitivity="security", frozen=True, done=True)
    _, first = _task(tmp_path, "first", carries=[_edge("origin", "first")], frozen=True)
    first.write_text(first.read_text().replace(
        f'carries:\n  - "{_edge("origin", "first")}"\n', ""), encoding="utf-8")
    node = add.read(first, "T2")
    legacy = (f'{{ by: "human:fixture", at: 2026-09-15, act: refreeze, authority: human, '
              f'direction: "{add.direction_digest(node)}" }}')
    add.write(first, f"---\n{add.append_item(node['raw'], 'verified', legacy)}\n---\n{node['body']}")
    cid, second = _task(tmp_path, "second", carries=[_edge("first", "second")])
    assert add.interview(tmp_path, cid, {"E1": "confirm", "TC1": "confirm"}, by="human:fixture")[0]
    before = second.read_bytes()
    ok, note = add.freeze(tmp_path, cid, by="human:fixture", authority="human")
    assert ok is None and "R:UNACCEPTED_CARRY" in note, note
    assert "first.md#RULES:M1" in note and second.read_bytes() == before


def test_removal_and_refreeze_cannot_lower_historical_human_floor(tmp_path):
    _setup(tmp_path)
    _task(tmp_path, "origin", sensitivity="security", frozen=True, done=True)
    first_id, first = _task(tmp_path, "first", carries=[_edge("origin", "first")])
    assert add.interview(tmp_path, first_id, {"E1": "confirm", "TC1": "confirm"}, by="human:fixture")[0]
    assert add.freeze(tmp_path, first_id, by="human:fixture", authority="human")[0]
    first.write_text(first.read_text().replace(
        f'carries:\n  - "{_edge("origin", "first")}"\n', ""), encoding="utf-8")
    assert add.authority_for(add.scan(tmp_path), first_id) == "human"
    before = first.read_bytes()
    ok, note = add.freeze(tmp_path, first_id, by="plan:fixture", authority="plan")
    assert ok is None and "R:UNINTERVIEWED" in note, note
    assert first.read_bytes() == before
    assert add.interview(tmp_path, first_id, {"E1": "confirm"}, by="human:fixture")[0]
    before = first.read_bytes()
    ok, note = add.freeze(tmp_path, first_id, by="plan:fixture", authority="plan")
    assert ok is None and "R:LOWERED_CARRY_AUTHORITY" in note, note
    assert first.read_bytes() == before
    assert add.freeze(tmp_path, first_id, by="human:fixture", authority="human")[0]
    second_id, _ = _task(tmp_path, "second", carries=[_edge("first", "second")])
    assert add.authority_for(add.scan(tmp_path), second_id) == "human"
    assert add.interview(tmp_path, second_id, {"E1": "confirm", "TC1": "confirm"}, by="human:fixture")[0]
    ok, note = add.freeze(tmp_path, second_id, by="plan:fixture", authority="plan")
    assert ok is None and "R:LOWERED_CARRY_AUTHORITY" in note, note


def test_duplicate_and_cycle_refuse_before_freeze(tmp_path):
    for mode in ("duplicate", "self", "two_node"):
        root = tmp_path / mode
        root.mkdir()
        _setup(root)
        _task(root, "original", frozen=True)
        if mode == "duplicate":
            _task(root, "first", carries=[_edge("original", "first")], frozen=True)
            cid, _ = _task(root, "second", carries=[_edge("original", "second")])
            code = "R:DUPLICATE_CARRY"
        elif mode == "self":
            cid, _ = _task(root, "first", carries=[_edge("first", "first")])
            code = "R:CYCLIC_CARRY"
        else:
            _task(root, "first", carries=[_edge("second", "first")], frozen=True)
            cid, _ = _task(root, "second", carries=[_edge("first", "second")])
            code = "R:CYCLIC_CARRY"
        _refuse_freeze(root, cid, code)


def test_self_edge_between_distinct_musts_refuses_before_freeze(tmp_path):
    _setup(tmp_path)
    cid, path = _task(tmp_path, "self-owner")
    raw = path.read_text().replace(
        "- M1 preserve this exact duty (from: B3)",
        "- M1 preserve this exact duty (from: B3)\n- M2 independent duty (from: B3)")
    raw = raw.replace("covers: M1, E1", "covers: M1, M2, E1")
    path.write_text(raw)
    assert add.freeze(tmp_path, cid, by="plan:fixture", authority="plan")[0]
    node = add.read(path, "T2")
    edge = "/tasks/self-owner.md#RULES:M1 -> /tasks/self-owner.md#RULES:M2"
    raw = node["raw"].replace("verified:\n", f'carries:\n  - "{edge}"\nverified:\n', 1)
    add.write(path, f"---\n{raw}\n---\n{node['body']}")
    _refuse_freeze(tmp_path, cid, "R:CYCLIC_CARRY")


def test_security_authority_inherits_across_hops_without_reusing_approval(tmp_path):
    _setup(tmp_path)
    _task(tmp_path, "original", sensitivity="security", frozen=True, done=True)
    _task(tmp_path, "first", carries=[_edge("original", "first")], frozen=True)
    cid, destination = _task(tmp_path, "second", carries=[_edge("first", "second")])
    graph = add.scan(tmp_path)
    assert add._carry_problem(graph, cid, accepted=False) == "", "the chain fixture is not accepted"
    assert add.authority_for(graph, cid) == "human", "two-hop carry lowered security floor"
    questions, note = add.interview(tmp_path, cid)
    assert [q["id"] for q in questions] == ["E1", "TC1"], note
    assert add.interview(tmp_path, cid, {"E1": "confirm", "TC1": "confirm"}, by="human:fixture")[0]
    before = destination.read_bytes()
    ok, note = add.freeze(tmp_path, cid, by="plan:fixture", authority="plan")
    assert ok is None and "R:LOWERED_CARRY_AUTHORITY" in note, note
    assert destination.read_bytes() == before, "process actor reused original human approval"
    ok, note = add.freeze(tmp_path, cid, by="human:fixture", authority="human")
    assert ok, note
    assert add._carry_problem(add.scan(tmp_path), cid, accepted=True) == ""
    ok, note = add.gate(tmp_path, cid, "PASS", by="plan:fixture")
    assert ok is None and "R:LOWERED_CARRY_AUTHORITY" in note, note
    node = add.read(destination, "T2")
    stop = '{ by: "human:fixture", at: 2026-09-15, act: gate, authority: human, outcome: HARD-STOP }'
    add.write(destination, f"---\n{add.append_item(node['raw'], 'verified', stop)}\n---\n{node['body']}")
    ok, _, note = add.done(tmp_path, cid, override="ship despite finding", by="human:fixture")
    assert ok is None and "HARD-STOP" in note, note


def test_human_carry_rejects_empty_identity_at_interview_and_freeze(tmp_path):
    _setup(tmp_path)
    _task(tmp_path, "security-origin", sensitivity="security", frozen=True, done=True)
    cid, destination = _task(tmp_path, "destination", carries=[_edge("security-origin", "destination")])
    before = destination.read_bytes()
    answers = {"E1": "confirm", "TC1": "confirm"}
    ok, note = add.interview(tmp_path, cid, answers, by="human:")
    assert ok is None and "R:LOWERED_CARRY_AUTHORITY" in note, note
    assert destination.read_bytes() == before
    assert add.interview(tmp_path, cid, answers, by="human:fixture")[0]
    before = destination.read_bytes()
    ok, note = add.freeze(tmp_path, cid, by="human:", authority="human")
    assert ok is None and "R:LOWERED_CARRY_AUTHORITY" in note, note
    assert destination.read_bytes() == before
    assert add.freeze(tmp_path, cid, by="human:fixture", authority="human")[0]
    ok, note = add.gate(tmp_path, cid, "PASS", by="human:")
    assert ok is None and "R:LOWERED_CARRY_AUTHORITY" in note, note


def test_scalar_and_ambiguous_carries_refuse_without_a_stamp(tmp_path):
    _setup(tmp_path)
    _task(tmp_path, "original", frozen=True)
    cid, path = _task(tmp_path, "destination")
    before = path.read_text()
    path.write_text(before.replace("verified: []", f'carries: "{_edge("original", "destination")}"\nverified: []'))
    _refuse_freeze(tmp_path, cid, "R:BAD_CARRY")
    path.write_text(before.replace("verified: []", "carries:\n"
                                 f'  - "{_edge("original", "destination")}"\n'
                                 f'  - "{_edge("original", "destination")}"\nverified: []'))
    _refuse_freeze(tmp_path, cid, "R:DUPLICATE_CARRY")


def test_revisiting_a_task_through_a_distinct_must_is_not_a_cycle(tmp_path):
    """A chain is over obligation addresses, even when it passes through one Task twice."""
    _setup(tmp_path)
    first, first_path = _task(tmp_path, "first")
    text = first_path.read_text().replace(
        "- M1 preserve this exact duty (from: B3)",
        "- M1 preserve this exact duty (from: B3)\n- M2 an independent duty (from: B3)")
    text = text.replace("covers: M1, E1", "covers: M1, M2, E1")
    first_path.write_text(text)
    assert add.freeze(tmp_path, first, by="plan:fixture", authority="plan")[0]

    second, _ = _task(tmp_path, "second", carries=[
        "/tasks/first.md#RULES:M2 -> /tasks/second.md#RULES:M1"])
    assert add.freeze(tmp_path, second, by="plan:fixture", authority="plan")[0]

    node = add.read(first_path, "T2")
    edge = "/tasks/second.md#RULES:M1 -> /tasks/first.md#RULES:M1"
    raw = node["raw"].replace("verified:\n", f'carries:\n  - "{edge}"\nverified:\n', 1)
    add.write(first_path, f"---\n{raw}\n---\n{node['body']}")
    ok, note = add.freeze(tmp_path, first, by="plan:fixture", authority="plan")
    assert ok, note
    assert add._carry_problem(add.scan(tmp_path), first, accepted=True) == ""


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
