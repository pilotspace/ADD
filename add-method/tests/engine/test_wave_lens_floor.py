"""`wave` sensitivity lens-floor (A3, task 2).

A stream whose task `sensitivity:` needs more than `process` authority (data · architecture ·
security) MUST carry a lens, or `wave` refuses R:NOLENS and writes nothing. A `mechanical` stream
is unaffected. Enforces PRESENCE of a lens, not domain-match (that stays the AI's judgment).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _setup(tmp_path, sens_a):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "a", title="a", milestone="m", sensitivity=sens_a, scope=["fa.py"])
    add.new(tmp_path, "Task", "b", title="b", milestone="m", sensitivity="mechanical", scope=["fb.py"])
    add.new(tmp_path, "Persona", "backend-systems", title="backend-systems")


def _active_wave(tmp_path):
    m = add.read(tmp_path / "milestones" / "m.md", "T2")
    return (m["fm"] or {}).get("active_wave")


def test_architecture_stream_without_lens_refuses(tmp_path):
    """covers: R:NOLENS — an architecture stream given bare refuses and records nothing."""
    _setup(tmp_path, "architecture")
    picks, note = add.wave(tmp_path, "m", streams=["a", "b"])   # 'a' is architecture, no lens
    assert picks is None and "R:NOLENS" in note, note
    assert _active_wave(tmp_path) is None, "a refused wave must not record active_wave"


def test_architecture_stream_with_lens_is_recorded(tmp_path):
    """covers: M1 — the same architecture stream WITH a lens records normally."""
    _setup(tmp_path, "architecture")
    picks, note = add.wave(tmp_path, "m", streams=["a:backend-systems", "b"])
    assert picks is not None, note
    assert "a:backend-systems" in str(_active_wave(tmp_path)), note


def test_mechanical_stream_needs_no_lens(tmp_path):
    """covers: M1 — a mechanical stream as a bare slug is allowed (no floor)."""
    _setup(tmp_path, "mechanical")
    picks, note = add.wave(tmp_path, "m", streams=["a", "b"])
    assert picks is not None, note
    assert _active_wave(tmp_path) is not None, note
