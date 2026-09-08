"""Red suite for `milestone-freeze-is-interviewed` — proof, not a typed name.

M34 records a false attestation that cannot be withdrawn: a go-ahead on a RECOMMENDATION was
read as approval of exit criteria written afterwards, the human-authority stamp went in on text
no human had seen, and the append-only ledger made it impossible to take back. A task at a human
floor already has proof-of-conversation. A milestone — where the expensive stamp actually lives —
had none.

The rung arms on the CLAIMED authority, inverting the task rung's rule, and that is deliberate:
a milestone carries no `sensitivity:`, so its computed floor is never human and a floor-keyed rung
would be dead code. Claiming plan authority is the LOWER, honest claim M34 itself prescribes, so
leaving it open is not an off switch (R:OFFSWITCH).
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

CRITERIA = ["the engine records the count", "the doctor names the slot", "the close drains"]


def milestone(root, slug, criteria=CRITERIA, authored=True):
    add.new(root, "Milestone", slug, title=slug)
    path = Path(root) / "milestones" / f"{slug}.md"
    s = path.read_text()
    if authored:
        s = s.replace("goal: <one line>", "goal: a goal a human wrote")
        s = s.replace("why: <why this milestone exists — required>", "why: a reason a human wrote")
    s = s.replace("evidence: <one row per task>", "evidence: recorded at close")
    boxes = "\n".join(f"- [ ] {c}   (a task)" for c in criteria) or ""
    s = s.replace("- [ ] <criterion>   (← <task>)", boxes)
    if not criteria:                       # E1: no boxes at all, not a placeholder box
        s = s.replace("## EXIT\n\n\n", "## EXIT\n\n")
    path.write_text(s)
    return f"/milestones/{slug}.md"


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Interviewed")
    return tmp_path


def test_interview_compiles_milestone_criteria(bundle):
    """covers: M1, A3, A9, A10 — the boxes, in document order, rendered whole."""
    cid = milestone(bundle, "m-ask")
    questions, note = add.interview(bundle, cid)
    assert len(questions) == len(CRITERIA), f"A3 — an authored goal satisfied the criteria: {note}"
    assert [q["id"] for q in questions] == ["C1", "C2", "C3"], questions
    for c in CRITERIA:                                   # A10: the text, never only the id
        assert c in note, f"a question showed an id without its criterion:\n{note}"
    order = [note.index(c) for c in CRITERIA]            # A9: document order
    assert order == sorted(order), f"the criteria were reordered:\n{note}"


def test_the_sidecar_lands_beside_its_node(bundle):
    """covers: M2, R:TASKSIDECAR, E4 — a record filed under the wrong tree is a lost record."""
    cid = milestone(bundle, "m-side")
    add.interview(bundle, cid, answers={"C1": "confirm"}, by="human:t")
    assert list((Path(bundle) / "milestones" / "m-side.d" / "interviews").glob("*.md")), \
        "the milestone's interview was not written beside it"
    assert not (Path(bundle) / "tasks" / "m-side.d").exists(), "R:TASKSIDECAR"

    tcid, _ = add.new(bundle, "Task", "t-side", title="T")
    path = Path(bundle) / "tasks" / "t-side.md"
    path.write_text(path.read_text().replace(
        "- A1 [who] covers: <S ids> · the request does not say <who may act / whose data>; "
        "taking <reading> -> <cost if wrong>",
        "- A1 [who] covers: S1 · the request does not say who acts; taking a reading -> a cost"))
    add.interview(bundle, tcid, answers={"A1": "confirm"}, by="human:t")
    assert list((Path(bundle) / "tasks" / "t-side.d" / "interviews").glob("*.md")), \
        "E4 — a task's interview moved out from under tasks/"


def test_human_claim_refuses_while_criteria_are_unanswered(bundle):
    """covers: M3, A4, A11, E3 — a tick states MET, never approved."""
    cid = milestone(bundle, "m-claim")
    path = Path(bundle) / "milestones" / "m-claim.md"
    path.write_text(path.read_text().replace(f"- [ ] {CRITERIA[0]}", f"- [x] {CRITERIA[0]}"))
    node, note = add.freeze(bundle, cid, by="Tin Dang", authority="human")
    assert node is None and "UNINTERVIEWED" in note, note
    assert "C1" in note, f"A4 — a ticked box was read as an answer:\n{note}"
    assert "interview" in note and "plan" in note, \
        f"A11 — the refusal named no honest way forward:\n{note}"


def test_a_lower_claim_still_freezes(bundle):
    """covers: M4, R:OFFSWITCH, A1, E5 — both halves, so neither can be vacuous."""
    cid = milestone(bundle, "m-lower")
    assert add.freeze(bundle, cid, by="plan:x", authority="human")[0] is None, \
        "the rung never fires, so the plan-authority half proves nothing"
    node, note = add.freeze(bundle, cid, by="plan:x", authority="plan")
    assert node is not None, f"the honest lower claim was refused:\n{note}"


def test_rewording_a_criterion_reopens_it(bundle):
    """covers: M5, R:STALEANSWER, A5, E2 — an answer belongs to a wording."""
    cid = milestone(bundle, "m-reword")
    add.interview(bundle, cid, answers={c: "confirm" for c in ("C1", "C2", "C3")}, by="Tin Dang")
    assert add.freeze(bundle, cid, by="Tin Dang", authority="human")[0] is not None, \
        "a fully answered milestone was still refused"
    path = Path(bundle) / "milestones" / "m-reword.md"
    path.write_text(path.read_text().replace(CRITERIA[1], "the doctor names the slot AND the file"))
    node, note = add.freeze(bundle, cid, by="Tin Dang", authority="human")
    assert node is None and "C2" in note, f"a reworded criterion kept its old answer:\n{note}"


def test_nothing_to_ask_is_not_something_to_refuse(bundle):
    """covers: M6, A6, E1 — the engine writes the scaffold; it must not then block it."""
    armed = milestone(bundle, "m-has-boxes")
    assert add.freeze(bundle, armed, by="Tin Dang", authority="human")[0] is None, \
        "the rung never fires, so an exemption from it proves nothing"
    # The reachable "nothing to ask" is a LOWER AUTHORITY, not an empty EXIT. A milestone with no
    # boxes is a scaffold, so the scaffold rung refuses it first — the old fixture asserted `is
    # not None` on a rung that answered `False` and was green on that refusal.
    cid = milestone(bundle, "m-plan")
    node, note = add.freeze(bundle, cid, by="Tin Dang", authority="plan")
    assert node is not None, f"a stamp claiming no human was refused for want of a human:\n{note}"


def test_the_record_invents_no_answer(bundle):
    """covers: A2, A7 — a defaulted answer is the false attestation this prevents."""
    cid = milestone(bundle, "m-record")
    add.interview(bundle, cid, answers={"C1": "confirm"}, by="Tin Dang")
    side = next((Path(bundle) / "milestones" / "m-record.d" / "interviews").glob("*.md"))
    text = side.read_text()
    assert "by: Tin Dang" in text, "the by: name was not recorded verbatim"
    assert "C2" in text, "A7 — an unanswered criterion vanished from the record"
    node, note = add.freeze(bundle, cid, by="Tin Dang", authority="human")
    assert node is None and "C2" in note and "C1" not in note, \
        f"an unanswered criterion was defaulted:\n{note}"


def test_the_rung_stays_last(bundle):
    """covers: A8 — never put template text to a person."""
    cid = milestone(bundle, "m-unauthored", authored=False)
    node, note = add.freeze(bundle, cid, by="Tin Dang", authority="human")
    assert not node, note
    assert "scaffold" in note, f"the scaffold check did not come first:\n{note}"
    assert "UNINTERVIEWED" not in note, f"the interview jumped the scaffold check:\n{note}"
    assert add.freeze(bundle, milestone(bundle, "m-authored"), by="Tin Dang",
                      authority="human")[1].count("UNINTERVIEWED"), \
        "the rung is merely last because it does not exist"
