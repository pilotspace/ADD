"""`status` surfaces the active wave with its lenses (A3, task 4).

When a milestone carries an `active_wave:`, the resume report names it and each stream with its
lens (`slug→persona`, bare slug when unlensed). With no live wave, no line is printed.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "a", title="a", milestone="m", scope=["fa.py"])
    add.new(tmp_path, "Task", "b", title="b", milestone="m", scope=["fb.py"])
    add.new(tmp_path, "Persona", "backend-systems", title="backend-systems")


def test_status_surfaces_active_wave_with_lenses(tmp_path):
    """covers: M1 — a lensed wave shows `slug→persona` and a bare slug in the report."""
    _bundle(tmp_path)
    add.wave(tmp_path, "m", streams=["a:backend-systems", "b"])
    report = add.status(tmp_path)
    assert "wave on m" in report, report
    assert "a→backend-systems" in report, report
    assert "b" in report


def test_status_omits_wave_line_when_none(tmp_path):
    """covers: M2 — a bundle with no active wave prints no `~ wave` line."""
    _bundle(tmp_path)
    report = add.status(tmp_path)
    assert "wave on" not in report, report
