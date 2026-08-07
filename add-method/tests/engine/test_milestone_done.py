"""`milestone-done` is the goal-gate: it REFUSES to close while any exit criterion is unchecked.

loop.md's spine — a milestone is done when its GOAL is met, not when its tasks are. The engine
reads the `- [x]`/`- [ ]` tally in the milestone's `## EXIT`; it never judges the goal. Checking
the last box is the human's single affirmation. Refusing is the notary's duty, not guarding: a human
can still write `status: done` by hand.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _mk_milestone(root, exit_lines: str):
    add.init(root, "code", "M")
    cid, _ = add.new(root, "Milestone", "m1", title="first slice")
    path = root / cid.lstrip("/")
    text = path.read_text(encoding="utf-8")
    # replace the scaffold EXIT body with the given criteria lines
    text = re.sub(r"(## EXIT\n).*?(\n## )", rf"\1{exit_lines}\2", text, flags=re.DOTALL)
    # fill the required why: so these tests exercise the goal-gate, not the why-gate (see test_why_in_card)
    text = re.sub(r"(?m)^why:.*$", "why: the first slice that proves the loop end to end", text)
    path.write_text(text, encoding="utf-8")
    return cid


def _status(root, cid):
    return (add.read(root / cid.lstrip("/"), "T0")["fm"] or {}).get("status")


def test_refuses_while_a_criterion_is_unchecked(tmp_path):
    cid = _mk_milestone(tmp_path, "- [x] one done\n- [ ] two not yet\n")
    ok, note = add.milestone_done(tmp_path, cid)
    assert ok is False, "must refuse while a box is unchecked"
    assert "milestone_goal_unmet" in note
    assert "1/2" in note, "the refusal must report the m/n tally"
    assert _status(tmp_path, cid) != "done", "a refused milestone must not be marked done"


def test_closes_when_all_criteria_checked(tmp_path):
    cid = _mk_milestone(tmp_path, "- [x] one done\n- [x] two done\n")
    ok, note = add.milestone_done(tmp_path, cid)
    assert ok is True, "must close when every box is checked"
    assert _status(tmp_path, cid) == "done", "a closed milestone is status: done"


def test_refuses_a_non_milestone(tmp_path):
    add.init(tmp_path, "code", "M")
    cid, _ = add.new(tmp_path, "Task", "a-task", title="t")
    ok, note = add.milestone_done(tmp_path, cid)
    assert ok is False and "not a Milestone" in note, "milestone-done closes milestones only"
