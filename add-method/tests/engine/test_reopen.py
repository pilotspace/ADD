"""`add reopen` returns a done task to a beat with a reset gate + a recorded reason (loop.md).

When a deepened verify finds a criterion unmet on a task already `done`, reopen puts it back in the
flow. The gate must RESET — a stale PASS from before the reopen can't entitle `done` again, or the
reopen would be theatre. So `done` counts only gates that postdate the last reopen.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _gate_stamp(by):
    # a stamp is a pre-formatted ABF flow-map string (the engine's own convention), not a dict.
    return f'{{ by: {by}, at: 2026-08-06, act: gate, authority: process, outcome: PASS }}'


def _freeze_stamp(by="x"):
    # `done` requires a (re)freeze BEFORE the entitling gate: a gate that closes a node the ONE
    # approval never touched is a forged record, not a lenient one (task risk-accepted-integrity).
    return f'{{ by: {by}, at: 2026-08-06, act: freeze, authority: human, direction: "sha256:0" }}'


def _make_done(root, cid):
    add._transition(root, cid, sets={"status": "done"},
                    appends=[("verified", _freeze_stamp()), ("verified", _gate_stamp("x"))])


def _status(root, cid):
    return (add.read(root / cid.lstrip("/"), "T0")["fm"] or {}).get("status")


def test_reopen_returns_a_done_task_to_a_beat(tmp_path):
    """covers: M1 — a done task returns to the named beat with the reason recorded."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    _make_done(tmp_path, cid)
    ok, _ = add.reopen(tmp_path, cid, "build", "verify found an unmet criterion")
    assert ok is True
    fm = add.read(tmp_path / cid.lstrip("/"), "T0")["fm"]
    assert fm["status"] == "build"
    assert any(s.get("act") == "reopen" and "unmet" in str(s.get("reason", "")) for s in fm["verified"])


def test_reopen_resets_the_gate(tmp_path):
    """covers: M2 — after reopen, done refuses until a gate postdates the reopen."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    _make_done(tmp_path, cid)
    add.reopen(tmp_path, cid, "verify", "needs a fresh receipt")
    ok, _missing, _ = add.done(tmp_path, cid)
    assert ok is False, "a stale pre-reopen gate must not entitle done"
    add._transition(tmp_path, cid, appends=[("verified", _gate_stamp("y"))])
    ok, _missing, _ = add.done(tmp_path, cid)
    assert ok is True, "a gate that postdates the reopen re-entitles done"


def test_reopen_refuses_a_task_not_done(tmp_path):
    """covers: R:NOTDONE — only a done task is reopened; nothing to reopen otherwise."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")  # status: direction
    ok, note = add.reopen(tmp_path, cid, "build", "reason")
    assert ok is False and "done" in note.lower()
