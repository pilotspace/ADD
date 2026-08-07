"""`add milestone-archive` retires a done milestone — and refuses one that is not done (loop.md).

milestone-done is the only path to done; archive is the only path past it, and it refuses to archive
a milestone whose goal-gate never closed. So there is no quiet way to shelve unfinished work.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _status(root, cid):
    return (add.read(root / cid.lstrip("/"), "T0")["fm"] or {}).get("status")


def test_archives_a_done_milestone(tmp_path):
    """covers: M1 — a done milestone becomes archived."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Milestone", "m", title="m")
    add._transition(tmp_path, cid, sets={"status": "done"})
    ok, _ = add.milestone_archive(tmp_path, cid)
    assert ok is True
    assert _status(tmp_path, cid) == "archived"


def test_refuses_a_milestone_not_done(tmp_path):
    """covers: R:NOTDONE — a milestone that never closed cannot be archived."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Milestone", "m", title="m")  # status: direction
    ok, note = add.milestone_archive(tmp_path, cid)
    assert ok is False and "done" in note.lower()
    assert _status(tmp_path, cid) != "archived"


def test_refuses_a_non_milestone(tmp_path):
    """covers: R:NOTMILESTONE — archive retires milestones only."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    ok, note = add.milestone_archive(tmp_path, cid)
    assert ok is False and "milestone" in note.lower()
