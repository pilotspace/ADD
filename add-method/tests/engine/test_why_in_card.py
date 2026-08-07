"""A one-line `why:` in the CARD — scaffolded for every node, gated *required* on milestones.

A node's `goal:` says what it does; the `why:` says why it exists — the decision-rationale that a
plausible-looking goal can hide. Tasks may carry it (optional); a milestone MUST, so `milestone_done`
refuses to close while its `why:` is still an unfilled `<placeholder>` — rationale is not a silent skip.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _card(root, cid):
    body = add.read(root / cid.lstrip("/"), "T2")["body"]
    return add._section(body, "card")


def _fill_exit(root, cid, lines):
    path = root / cid.lstrip("/")
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(## EXIT\n).*?(\n## )", rf"\1{lines}\2", text, flags=re.DOTALL)
    path.write_text(text, encoding="utf-8")


def _set_why(root, cid, why):
    path = root / cid.lstrip("/")
    text = path.read_text(encoding="utf-8")
    path.write_text(re.sub(r"(?m)^why:.*$", f"why: {why}", text), encoding="utf-8")


def test_milestone_template_carries_why(tmp_path):
    """covers: M1 — a new Milestone's CARD has a why: line."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Milestone", "m", title="m")
    assert re.search(r"(?m)^why:", _card(tmp_path, cid)), "Milestone CARD must scaffold a why: line"


def test_task_template_carries_why(tmp_path):
    """covers: M1 — a new Task's CARD has a why: line (optional, but present to prompt)."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    assert re.search(r"(?m)^why:", _card(tmp_path, cid)), "Task CARD must scaffold a why: line"


def test_refuses_unset_why_even_when_boxes_checked(tmp_path):
    """covers: M2, R:WHYUNSET — an unfilled why: is refused despite every box checked."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Milestone", "m", title="m")
    _fill_exit(tmp_path, cid, "- [x] all done\n")  # goal-gate satisfied; why: still a placeholder
    ok, note = add.milestone_done(tmp_path, cid)
    assert ok is False, "an unset why: must refuse the close even with all boxes checked"
    assert "why" in note.lower()
    assert (add.read(tmp_path / cid.lstrip("/"), "T0")["fm"] or {}).get("status") != "done"


def test_closes_once_why_is_set(tmp_path):
    """covers: M2 — a filled why: plus checked boxes closes."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Milestone", "m", title="m")
    _fill_exit(tmp_path, cid, "- [x] all done\n")
    _set_why(tmp_path, cid, "the loop had no place to record why a milestone exists")
    ok, _ = add.milestone_done(tmp_path, cid)
    assert ok is True, "a filled why: with all boxes checked must close"
    assert (add.read(tmp_path / cid.lstrip("/"), "T0")["fm"] or {}).get("status") == "done"
