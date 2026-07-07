"""Scenarios: run record round-trip / reject corrupt run record (M4, R:invalid_run_record)."""
import copy

import pytest

from benchmark.schema.run_record import RunRecord, validate, BenchError

VALID = {
    "arm": "add",
    "wm": 1,
    "rep": 0,
    "status": "done",
    "metrics": {
        "regression_rate": 0.0,
        "spec_fidelity": 0.9,
        "tokens_total": 12345,
        "cost_usd": 0.42,
        "context_rot_slope": 0.01,
        "time_to_first_edit": 30.5,
    },
    "artifacts": {
        "workspace": "benchmark/runs/add/wm1/workspace",
        "transcript": "benchmark/runs/add/wm1/transcript.jsonl",
        "oracle_report": "benchmark/runs/add/wm1/oracle_report.json",
    },
}


def test_run_record_round_trip():
    record = validate(VALID)
    assert isinstance(record, RunRecord)
    payload = record.to_json()
    restored = RunRecord.from_json(payload)
    assert restored == record


def test_invalid_run_record_rejected_missing_field():
    bad = copy.deepcopy(VALID)
    del bad["metrics"]
    with pytest.raises(BenchError) as exc_info:
        validate(bad)
    assert "invalid_run_record" in str(exc_info.value)


def test_invalid_run_record_rejected_bad_metric_name():
    bad = copy.deepcopy(VALID)
    bad["metrics"]["speed"] = 1.0
    with pytest.raises(BenchError) as exc_info:
        validate(bad)
    assert "invalid_run_record" in str(exc_info.value)
