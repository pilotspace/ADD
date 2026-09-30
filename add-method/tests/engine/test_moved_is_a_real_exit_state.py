"""B2 RED: authored moved EXIT lines survive the goal tally and need accepted destinations."""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _milestone(root, slug, exit_lines, frozen=False):
    cid, _ = add.new(root, "Milestone", slug, title=slug)
    path = root / cid.lstrip("/")
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"(## EXIT\n).*?(\n## )", rf"\1{exit_lines}\2", raw, flags=re.DOTALL)
    raw = re.sub(r"(?m)^why:.*$", "why: this authored obligation must remain visible", raw)
    raw = re.sub(r"(?m)^goal:.*$", "goal: keep the named exit obligation accountable", raw)
    path.write_text(raw, encoding="utf-8")
    if frozen:
        stamp, note = add.freeze(root, cid, by="plan:test", authority="plan")
        assert stamp is not None, note
    return cid, path


def _setup(root):
    add.init(root, "code", "B2")


def _close_refuses(root, cid, code, source="C2"):
    ok, note = add.milestone_done(root, cid)
    assert ok is None, f"{code}: moved criterion closed as complete: {note!r}"
    assert code in note and source in note, f"refusal lost source identity: {note!r}"
    return note


def test_real_counterexample_keeps_exit_nine_and_eleven_total():
    path = REPO.parent / ".add/milestones/loop-that-closes.md"
    before = path.read_bytes()
    body = add.read(path, "T2")["body"]
    criteria = add._box_lines(add._section_of(body, "EXIT"))
    assert len(criteria) == 11, f"R:INVISIBLE_MOVE — authored EXIT:9 disappeared: {len(criteria)}/11"
    assert "quick-lane-tripwire" in criteria[8][2], "authored EXIT:9 changed identity"
    assert criteria[8][1] is False, "the moved criterion was silently counted met"
    assert path.read_bytes() == before, "historical milestone changed during a read"


def test_mixed_fences_do_not_turn_examples_into_exit_criteria(tmp_path):
    _setup(tmp_path)
    exit_text = "```\n~~~\n- [x] C1 fenced example\n~~~\n```\n- [x] C2 real criterion\n"
    cid, path = _milestone(tmp_path, "src", exit_text)
    criteria = add._box_lines(add._section_of(add.read(path, "T2")["body"], "EXIT"))
    assert len(criteria) == 1 and "C2 real criterion" in criteria[0][2], criteria
    closed, report = add.milestone_done(tmp_path, cid)
    assert closed is True and "1/1" in report, report


def test_orphan_and_dangling_moves_refuse_by_original_identity(tmp_path):
    cases = [
        ("", "R:ORPHAN_MOVE"),
        (" (moves-to: /milestones/missing.md#EXIT:C1)", "R:DANGLING_MOVE"),
        (" (moves-to: /milestones/dest.md#EXIT:C99)", "R:DANGLING_MOVE"),
        (" (moves-to: /tasks/dest.md#EXIT:C1)", "R:DANGLING_MOVE"),
    ]
    for n, (target, code) in enumerate(cases):
        root = tmp_path / f"locator-{n}"
        root.mkdir()
        _setup(root)
        if "dest.md" in target:
            _milestone(root, "dest", "- [ ] C1 destination\n", frozen=True)
        if "/tasks/dest.md" in target:
            add.new(root, "Task", "dest", title="wrong node type")
        src, path = _milestone(root, "src", "- [x] C1 met\n- [~] C2 original" + target + "\n")
        before = path.read_bytes()
        _close_refuses(root, src, code)
        assert path.read_bytes() == before, f"case {n}: refused close rewrote the original obligation"


def test_unaccepted_destination_refuses_without_laundering_a_target(tmp_path):
    cases = [("", True), (" (accepts: /milestones/src.md#EXIT:C2)", False)]
    for n, (accepts, frozen) in enumerate(cases):
        root = tmp_path / f"acceptance-{n}"
        root.mkdir()
        _setup(root)
        _, target = _milestone(root, "dest", "- [ ] C1 destination" + accepts + "\n", frozen=frozen)
        src, _ = _milestone(root, "src", "- [x] C1 met\n- [~] C2 original (moves-to: /milestones/dest.md#EXIT:C1)\n")
        before = target.read_bytes()
        _close_refuses(root, src, "R:REJECTED_MOVE")
        assert target.read_bytes() == before, f"case {n}: a rejected move silently accepted itself"


def test_acceptance_edited_after_freeze_refuses(tmp_path):
    _setup(tmp_path)
    _, target = _milestone(tmp_path, "dest", "- [ ] C1 destination\n", frozen=True)
    raw = target.read_text(encoding="utf-8")
    target.write_text(raw.replace("C1 destination", "C1 destination (accepts: /milestones/src.md#EXIT:C2)"), encoding="utf-8")
    src, _ = _milestone(tmp_path, "src", "- [x] C1 met\n- [~] C2 original (moves-to: /milestones/dest.md#EXIT:C1)\n")
    _close_refuses(tmp_path, src, "R:REJECTED_MOVE")


def test_check_cannot_erase_a_moved_criterion(tmp_path):
    _setup(tmp_path)
    src, path = _milestone(tmp_path, "src", "- [x] C1 met\n- [~] C2 original\n")
    before = path.read_bytes()
    ok, note = add.check(tmp_path, src, [2], section="EXIT")
    assert ok is None and "moved" in note and "NOTHING was written" in note, note
    assert path.read_bytes() == before, "the moved state was silently marked met"


def test_destination_completion_keeps_its_frozen_acceptance(tmp_path):
    _setup(tmp_path)
    dest, _ = _milestone(tmp_path, "dest", "- [ ] C1 destination (accepts: /milestones/src.md#EXIT:C2)\n", frozen=True)
    marked, note = add.check(tmp_path, dest, [1], section="EXIT")
    assert marked is True, note
    src, _ = _milestone(tmp_path, "src", "- [x] C1 met\n- [~] C2 original (moves-to: /milestones/dest.md#EXIT:C1)\n")
    closed, report = add.milestone_done(tmp_path, src)
    assert closed is True and "1/2" in report and "C2" in report, report


def test_self_and_two_node_cycles_refuse(tmp_path):
    for two_node in (False, True):
        root = tmp_path / f"cycle-{int(two_node)}"
        root.mkdir()
        _setup(root)
        if two_node:
            _milestone(root, "dest", "- [x] C9 already met\n- [~] C1 destination (moves-to: /milestones/src.md#EXIT:C2) (accepts: /milestones/src.md#EXIT:C2)\n", frozen=True)
            target = "/milestones/dest.md#EXIT:C1"
        else:
            target = "/milestones/src.md#EXIT:C2"
        src, _ = _milestone(root, "src", "- [x] C1 met\n- [~] C2 original (moves-to: " + target + ")" +
                                 ("" if not two_node else " (accepts: /milestones/dest.md#EXIT:C1)") + "\n", frozen=True)
        _close_refuses(root, src, "R:CYCLIC_MOVE")


def test_accepted_terminal_move_preserves_original_denominator_and_bytes(tmp_path):
    _setup(tmp_path)
    _, target = _milestone(tmp_path, "dest", "- [ ] C1 destination (accepts: /milestones/src.md#EXIT:C2)\n", frozen=True)
    src, source = _milestone(tmp_path, "src", "- [x] C1 met\n- [~] C2 original (moves-to: /milestones/dest.md#EXIT:C1)\n")
    target_before, source_before = target.read_bytes(), source.read_bytes()
    ok, note = add.milestone_done(tmp_path, src)
    assert ok is True, f"valid accepted move failed closure: {note!r}"
    assert "1/2" in note and "moved" in note.lower() and "C2" in note, f"R:INVISIBLE_MOVE — original total or moved identity lost: {note!r}"
    assert target.read_bytes() == target_before, "source closure rewrote destination"
    assert "- [~] C2 original" in source.read_text(encoding="utf-8"), "source obligation was erased"
    assert source_before != source.read_bytes(), "the normal close transition did not occur"
    closed_before = source.read_bytes()
    already, report = add.milestone_done(tmp_path, src)
    assert already is True and "already done" in report and "1/2" in report and "C2" in report, report
    assert source.read_bytes() == closed_before, "a read of the closed milestone rewrote its history"
