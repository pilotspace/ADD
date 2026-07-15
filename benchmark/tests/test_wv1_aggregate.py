"""WV1 rep aggregation of the v2 trust metrics (v2-wv1-longitudinal TASK.md
§3 CONTRACT @ v1; M1, M2, R1) — aggregate_reps stays PURE and v1-byte-stable;
optional v2 keys aggregate over their CARRIERS with n_missing disclosure,
never a fabricated 0.0 mean."""
from __future__ import annotations

import pytest

from benchmark.pilot import aggregate_reps
from benchmark.schema.run_record import RunRecord

_V1_METRICS = {
    "regression_rate": 0.0,
    "requirement_coverage": 0.9,
    "tokens_total": 1000.0,
    "cost_usd": 1.0,
    "context_rot_slope": 0.0,
    "time_to_first_edit": 5.0,
}


def _record(wm: int, rep: int, metrics: dict) -> RunRecord:
    return RunRecord(
        arm="add",
        wm=wm,
        rep=rep,
        status="done",
        metrics=metrics,
        artifacts={"workspace": "w", "transcript": "t", "oracle_report": "o"},
    )


def test_aggregate_v2_metrics():
    records = [
        _record(2, 0, {**_V1_METRICS, "regression_rate": 0.0, "oracle_pass_rate": 0.8}),
        _record(2, 1, {**_V1_METRICS, "regression_rate": 0.1, "oracle_pass_rate": 1.0}),
        _record(2, 2, {**_V1_METRICS, "regression_rate": 0.0, "oracle_pass_rate": 0.9}),
    ]
    entry = aggregate_reps(records)[("add", 2)]
    assert entry["pass_rate"]["mean"] == pytest.approx(0.9)
    assert entry["pass_rate"]["min"] == 0.8
    assert entry["pass_rate"]["max"] == 1.0
    assert entry["regression"]["mean"] == pytest.approx(0.1 / 3)


def test_aggregate_v1_output_unchanged():
    records = [
        _record(1, 0, dict(_V1_METRICS)),
        _record(1, 1, {**_V1_METRICS, "cost_usd": 3.0}),
    ]
    entry = aggregate_reps(records)[("add", 1)]
    # the v1 triple aggregates exactly as before the v2 extension
    assert entry["n"] == 2
    assert entry["tokens"] == {"mean": 1000.0, "min": 1000.0, "max": 1000.0}
    assert entry["cost"] == {"mean": 2.0, "min": 1.0, "max": 3.0}
    assert entry["fidelity"] == {"mean": 0.9, "min": 0.9, "max": 0.9}


def test_aggregate_mixed_records_n_missing():
    records = [
        _record(2, 0, {**_V1_METRICS, "oracle_pass_rate": 0.8}),
        _record(2, 1, {**_V1_METRICS, "oracle_pass_rate": 1.0}),
        _record(2, 2, dict(_V1_METRICS)),  # no oracle_pass_rate -> aggregator discloses n_missing
    ]
    entry = aggregate_reps(records)[("add", 2)]
    assert entry["pass_rate"]["mean"] == pytest.approx(0.9)
    assert entry["pass_rate"]["n_missing"] == 1
    # ZERO carriers -> n_missing only, no fabricated distribution   # R1
    assert entry["weakened"] == {"n_missing": 3}
    # required keys never carry n_missing noise
    assert "n_missing" not in entry["cost"]
