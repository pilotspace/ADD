"""`doctor` surfaces unadvised sensitive tasks (A4, task 2).

R:NOLENS enforces a lens for parallel wave streams only. A sequential task whose sensitivity floor is
above `process` (data · architecture · security) never touches a wave, so its missing lens is invisible.
`doctor` reports it as a reports-only `unadvised_sensitive` finding — a nudge, never a write, never a gate.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _codes(root):
    return [f["code"] for f in add.doctor(root)]


def _snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


def test_unadvised_sensitive_task_is_reported(tmp_path):
    """covers: M1 — an architecture task with no lens yields an unadvised_sensitive finding."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "a", title="a", milestone="m", sensitivity="architecture", scope=["a.py"])
    assert "unadvised_sensitive" in _codes(tmp_path)


def test_lensed_or_mechanical_task_is_not_flagged(tmp_path):
    """covers: M2 — a mechanical task and a lensed sensitive task both produce no finding."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "mech", title="mech", milestone="m", sensitivity="mechanical", scope=["m.py"])
    add.new(tmp_path, "Task", "lensed", title="lensed", milestone="m", sensitivity="security",
            scope=["s.py"], persona="sec-rev")
    add.new(tmp_path, "Task", "advised", title="advised", milestone="m", sensitivity="architecture",
            scope=["d.py"], **{"advised_by": "backend-systems"})
    assert "unadvised_sensitive" not in _codes(tmp_path)


def test_doctor_writes_nothing(tmp_path):
    """covers: R:DOCTORWRITES — a doctor run that produces the finding mutates no bundle bytes."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "a", title="a", milestone="m", sensitivity="architecture", scope=["a.py"])
    before = _snapshot(tmp_path)
    add.doctor(tmp_path)
    assert _snapshot(tmp_path) == before, "doctor must write nothing (law 3)"
