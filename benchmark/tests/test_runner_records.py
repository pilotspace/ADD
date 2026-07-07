"""Scenarios: crash mid-write leaves no partial record (R5); nothing_to_resume
groundwork for find_resume_point (R4 is exercised at the CLI level)."""
from __future__ import annotations

import pathlib

import pytest

from benchmark.runner import records as records_mod
from benchmark.runner.records import find_resume_point, write_record_atomic
from benchmark.schema.run_record import validate

VALID = {
    "arm": "fake-arm",
    "wm": 1,
    "rep": 0,
    "status": "done",
    "metrics": {
        "regression_rate": 0.0,
        "spec_fidelity": 0.0,
        "tokens_total": 0.0,
        "cost_usd": 0.0,
        "context_rot_slope": 0.0,
        "time_to_first_edit": 0.0,
    },
    "artifacts": {"workspace": "w", "transcript": "t", "oracle_report": "o"},
}


def test_write_record_atomic_round_trip(tmp_path):
    record = validate(VALID)
    path = tmp_path / "record.json"
    write_record_atomic(path, record)
    assert path.exists()

    from benchmark.schema.run_record import RunRecord

    assert RunRecord.from_json(path.read_text()) == record


def test_crash_mid_write_leaves_no_partial_record(tmp_path, monkeypatch):
    record = validate(VALID)
    path = tmp_path / "runs" / "fake-arm" / "wm1" / "record.json"

    def _boom(_src, _dst):
        raise RuntimeError("simulated crash before rename")

    monkeypatch.setattr(records_mod.os, "replace", _boom)

    with pytest.raises(RuntimeError):
        write_record_atomic(path, record)

    assert not path.exists()
    # no leaked temp file either
    assert list(path.parent.glob(".record-*")) == []

    resume_point = find_resume_point("fake-arm", runs_root=tmp_path / "runs")
    assert resume_point is None  # not-done: wm1 has no record at all


def test_crash_mid_write_preserves_prior_complete_record(tmp_path, monkeypatch):
    record = validate(VALID)
    path = tmp_path / "runs" / "fake-arm" / "wm1" / "record.json"
    write_record_atomic(path, record)
    assert path.exists()

    def _boom(_src, _dst):
        raise RuntimeError("simulated crash before rename")

    monkeypatch.setattr(records_mod.os, "replace", _boom)
    with pytest.raises(RuntimeError):
        write_record_atomic(path, record)

    # the prior complete record survives untouched
    from benchmark.schema.run_record import RunRecord

    assert RunRecord.from_json(path.read_text()) == record
