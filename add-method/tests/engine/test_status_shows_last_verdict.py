"""Red-first contract for the consequential verdict in the ADD resume view.

Stamps are inserted through the engine's transition writer so the fixture exercises
the real T0 parser. Their identical dates make verified[] order, not a clock, decisive.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Gate board")
    return tmp_path


def _task(root, slug, *, status="verify"):
    cid, _ = add.new(root, "Task", slug, title=f"task {slug}")
    add._transition(root, cid, sets={"status": status})
    return cid


def _stamp(root, cid, act, *, outcome=None, receipt=None, kind=None):
    fields = ["by: test", "at: 2026-09-15", f"act: {act}"]
    if act == "gate":
        fields.append("authority: process")
    if outcome is not None:
        fields.append(f"outcome: {outcome}")
    if receipt is not None:
        fields.append(f"receipt: {receipt}")
    if kind is not None:
        fields.append(f"kind: {kind}")
    add._transition(root, cid, appends=[("verified", "{ " + ", ".join(fields) + " }")])


def _now(out):
    return next((line.strip() for line in out.splitlines() if line.strip().startswith("now:")), "")


def _evidence(out):
    return next((line.strip() for line in out.splitlines() if line.strip().startswith("evidence:")), "")


def test_same_day_later_acts_keep_the_stopped_gate_and_its_receipt(bundle):
    """covers: M1,M2,M3,R:ACTASVERDICT,R:BORROWED_RECEIPT,A3,E1."""
    cid = _task(bundle, "stopped")
    _stamp(bundle, cid, "gate", outcome="HARD-STOP",
           receipt="/tasks/stopped.d/runs/1.md")
    for act in ("check", "run", "refute"):
        _stamp(bundle, cid, act, receipt="/tasks/stopped.d/runs/2.md" if act == "run" else None)
        out = add.status(bundle)
        assert "stopped" in _now(out) and "beat=verify" in _now(out), out
        assert "last-gate=HARD-STOP" in _now(out), out
        assert "receipt=runs/1.md" in _evidence(out), out
        assert "runs/2.md" not in _evidence(out), out
        assert "/tasks/stopped.md#verified" in _evidence(out), out
        assert f"last: {act} stopped" in out, out


def test_later_gate_supersedes_stop_without_borrowing_receipts(bundle):
    """covers: M2,M3,R:BORROWED_RECEIPT,E3."""
    cid = _task(bundle, "resolved")
    _stamp(bundle, cid, "gate", outcome="HARD-STOP", receipt="/tasks/resolved.d/runs/1.md")
    _stamp(bundle, cid, "gate", outcome="PASS", receipt="/tasks/resolved.d/runs/2.md")
    _stamp(bundle, cid, "run", receipt="/tasks/resolved.d/runs/3.md")
    out = add.status(bundle)
    assert "last-gate=PASS" in _now(out), out
    assert "receipt=runs/2.md" in _evidence(out), out
    assert "runs/1.md" not in _evidence(out) and "runs/3.md" not in _evidence(out), out
    assert "last: run resolved" in out, out


def test_reopen_resets_the_current_gate(bundle):
    """covers: M2,R:STALEGATE,E2."""
    cid = _task(bundle, "cycled", status="done")
    _stamp(bundle, cid, "gate", outcome="PASS", receipt="/tasks/cycled.d/runs/1.md")
    _stamp(bundle, cid, "reopen")
    add._transition(bundle, cid, sets={"status": "build"})
    out = add.status(bundle)
    assert "cycled" in _now(out) and "beat=build" in _now(out), out
    assert "last-gate=none" in _now(out), out
    assert not _evidence(out), out
    _stamp(bundle, cid, "gate", outcome="HARD-STOP", receipt="/tasks/cycled.d/runs/2.md")
    out = add.status(bundle)
    assert "last-gate=HARD-STOP" in _now(out), out
    assert "receipt=runs/2.md" in _evidence(out), out


def test_multiple_stops_have_stable_attention_even_under_row_cap(bundle):
    """covers: M1,M4,A5,A6,E4."""
    for i in range(add.MAX_LINES + 5):
        _task(bundle, f"filler-{i:02d}", status="verify")
    for slug in ("z-stop", "a-stop"):
        cid = _task(bundle, slug, status="verify")
        _stamp(bundle, cid, "gate", outcome="HARD-STOP",
               receipt=f"/tasks/{slug}.d/runs/1.md")
    for all_rows in (False, True):
        out = add.status(bundle, all=all_rows)
        assert "a-stop" in _now(out), out
        assert "last-gate=HARD-STOP" in _now(out), out
        assert "receipt=runs/1.md" in _evidence(out), out
        assert all(len(line) <= 100 for line in out.splitlines()), out
        assert out.splitlines()[-1].startswith("next:"), out


def test_sources_and_legacy_gate_evidence_is_explicit(bundle):
    """covers: M3,A4,E5."""
    cid = _task(bundle, "sources")
    _stamp(bundle, cid, "gate", outcome="HARD-STOP", kind="sources")
    out = add.status(bundle)
    assert "last-gate=HARD-STOP" in _now(out), out
    assert "/tasks/sources.md#FINDINGS" in _evidence(out), out
    assert "receipt=unrecorded" in _evidence(out), out
    add._transition(bundle, cid, sets={"status": "done"})
    other = _task(bundle, "legacy")
    _stamp(bundle, other, "gate", outcome="HARD-STOP")
    _stamp(bundle, other, "run", receipt="/tasks/legacy.d/runs/9.md")
    out = add.status(bundle)
    assert "legacy" in _now(out), out
    assert "receipt=unrecorded" in _evidence(out), out
    assert "/tasks/legacy.md#verified" in _evidence(out), out
    assert "runs/9.md" not in _evidence(out), out


def test_no_open_task_has_no_current_verdict(bundle):
    """covers: M1,A2,E6."""
    cid = _task(bundle, "history")
    _stamp(bundle, cid, "gate", outcome="HARD-STOP")
    assert "history" in _now(add.status(bundle))
    add._transition(bundle, cid, sets={"status": "done"})
    for all_rows in (False, True):
        out = add.status(bundle, all=all_rows)
        assert not _now(out) and not _evidence(out), out
        assert "last: gate history" in out, out


def test_verdictless_gate_does_not_clear_a_known_stop(bundle):
    """covers: M2,M3,A4,R:ACTASVERDICT,E7 — an unknown gate is no resolution."""
    cid = _task(bundle, "unresolved")
    _stamp(bundle, cid, "gate", outcome="HARD-STOP",
           receipt="/tasks/unresolved.d/runs/1.md")
    _stamp(bundle, cid, "gate", receipt="/tasks/unresolved.d/runs/2.md")
    out = add.status(bundle)
    assert "last-gate=HARD-STOP" in _now(out), out
    assert "receipt=runs/1.md" in _evidence(out), out
    assert "runs/2.md" not in _evidence(out), out
    assert "last: gate unresolved" in out, out


def test_long_slug_keeps_summaries_bounded_and_next_exact(bundle):
    """covers: M3,M4,A6,E8 — clipping the action is worse than an overwide final command."""
    slug = "a" * 85
    cid = _task(bundle, slug)
    _stamp(bundle, cid, "gate", outcome="HARD-STOP",
           receipt=f"/tasks/{slug}.d/runs/1.md")
    out = add.status(bundle)
    for line in out.splitlines():
        if not line.startswith("next:"):
            assert len(line) <= 100, f"summary line wraps ({len(line)}): {line!r}"
    assert "last: gate" in out and "last-gate=HARD-STOP" in _now(out), out
    assert out.splitlines()[-1].startswith("next:") and slug in out.splitlines()[-1], out


def test_cross_node_same_day_last_marks_unknown_order(bundle):
    """covers: M3,A3,E9 — day-only stamps cannot establish cross-node chronology."""
    for slug in ("first", "second"):
        cid = _task(bundle, slug)
        _stamp(bundle, cid, "gate", outcome="PASS")
    out = add.status(bundle)
    last = next(line for line in out.splitlines() if line.strip().startswith("last:"))
    assert "day tie" in last, f"same-day cross-node order was claimed as known: {last!r}"
    assert len(last) <= 100, last


def test_verify_next_includes_required_gate_verdict(bundle):
    """covers: M3,E10 — gate requires a verdict and a named actor slot."""
    _task(bundle, "needs-verdict", status="verify")
    nxt = add.status(bundle).splitlines()[-1]
    assert nxt.startswith("next: add gate needs-verdict PASS --by"), nxt


def test_unrun_build_next_does_not_borrow_foreign_command(bundle):
    """covers: M3,R:FOREIGN_CMD,E11 — the command belongs to its Task."""
    foreign = _task(bundle, "foreign", status="build")
    add.run(bundle, foreign, ["python3", "-c", "print('FOREIGN_CMD')"])
    add._transition(bundle, foreign, sets={"status": "done"})
    _task(bundle, "unrun", status="build")
    nxt = add.status(bundle).splitlines()[-1]
    assert nxt == "next: add show unrun", f"unrun Task borrowed another run: {nxt!r}"
    assert "FOREIGN_CMD" not in nxt


def test_task_owned_junit_command_replays_once(bundle):
    """covers: M3,R:FOREIGN_CMD,E12 — an owned JUnit path must not be appended twice."""
    cid = _task(bundle, "owned", status="build")
    add.run(bundle, cid, ["python3", "-c", "print('OWNED')",
                          "--junitxml=/private/tmp/owned-status.xml"])
    nxt = add.status(bundle).splitlines()[-1]
    assert nxt.startswith("next: add run owned -- python3 -c"), nxt
    assert "OWNED" in nxt and nxt.count("--junitxml") == 1, nxt


def test_status_gate_summary_stays_frontmatter_only(bundle, monkeypatch):
    """covers: M4,R:T2SCAN,A1."""
    cid = _task(bundle, "lightweight")
    _stamp(bundle, cid, "gate", outcome="HARD-STOP",
           receipt="/tasks/lightweight.d/runs/1.md")
    original = add.read

    def t0_only(path, tier="T2", *args, **kwargs):
        if tier != "T0":
            raise AssertionError(f"status read {tier} body: {path}")
        return original(path, tier, *args, **kwargs)

    monkeypatch.setattr(add, "read", t0_only)
    out = add.status(bundle)
    assert "last-gate=HARD-STOP" in _now(out), out
    assert "receipt=runs/1.md" in _evidence(out), out
