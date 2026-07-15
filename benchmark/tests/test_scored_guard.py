"""Guard: an UNSCORED `execute_wm` record must never be misread as scored.

Root cause this guards (see project_ceremony_turn_cut_planned lesson): `execute_wm`
writes `oracle_pass_rate: 0.0` and `requirement_coverage: 0.0` as PLACEHOLDERS — the
real values are computed later by `score_record` (which the pilot calls after
execute_wm). A launcher that calls execute_wm directly and reads those 0.0s as real
concludes "the build failed" when the build was actually perfect.

The guard is a `scored` marker metric that ONLY `score_record` emits. `is_scored()`
reads it; `require_scored()` refuses an unscored record loudly instead of letting a
0.0 placeholder pass as a real score.

Run: python3 -m pytest benchmark/tests/test_scored_guard.py -q
"""
from __future__ import annotations

import pytest

from benchmark import score as score_mod
from benchmark.schema.run_record import (
    OPTIONAL_METRICS,
    REQUIRED_METRICS,
    BenchError,
    RunRecord,
    validate,
)


def _placeholder_metrics() -> dict[str, float]:
    """Exactly what execute_wm writes for a fresh (unscored) record."""
    return {
        "regression_rate": 0.0,
        "requirement_coverage": 0.0,  # placeholder
        "oracle_pass_rate": 0.0,      # placeholder
        "tokens_total": 4200.0,
        "cost_usd": 0.31,
        "context_rot_slope": 0.0,
        "time_to_first_edit": 12.5,
    }


def _record(metrics: dict[str, float]) -> RunRecord:
    return RunRecord(
        arm="add",
        wm=1,
        rep=0,
        status="done",
        metrics=metrics,
        artifacts={"workspace": "w", "transcript": "t", "oracle_report": "o"},
    )


def test_scored_is_an_optional_metric():
    # the marker must be schema-legal, else score_record's validate() would reject it
    assert "scored" in OPTIONAL_METRICS
    assert "scored" not in REQUIRED_METRICS


def test_execute_wm_placeholder_is_unscored():
    rec = _record(_placeholder_metrics())
    assert score_mod.is_scored(rec) is False


def test_require_scored_raises_on_placeholder():
    rec = _record(_placeholder_metrics())
    with pytest.raises(BenchError, match="unscored_record"):
        score_mod.require_scored(rec)


def test_scored_marker_marks_a_scored_record():
    metrics = _placeholder_metrics()
    metrics["oracle_pass_rate"] = 1.0
    metrics["requirement_coverage"] = 1.0
    metrics["scored"] = 1.0
    rec = _record(metrics)
    assert score_mod.is_scored(rec) is True
    assert score_mod.require_scored(rec) is rec


def test_is_scored_accepts_a_bare_metrics_mapping():
    # convenience: helper works on the metrics dict too, not only a RunRecord
    assert score_mod.is_scored(_placeholder_metrics()) is False
    assert score_mod.is_scored({**_placeholder_metrics(), "scored": 1.0}) is True


def test_validate_accepts_the_scored_marker():
    metrics = {**_placeholder_metrics(), "scored": 1.0}
    rec = validate(
        {
            "arm": "add",
            "wm": 1,
            "rep": 0,
            "status": "done",
            "metrics": metrics,
            "artifacts": {"workspace": "w", "transcript": "t", "oracle_report": "o"},
        }
    )
    assert rec.metrics["scored"] == 1.0


def test_validate_still_rejects_an_unknown_metric():
    # additive is NOT open-ended — the guard adds exactly `scored`, nothing else
    metrics = {**_placeholder_metrics(), "totally_made_up": 1.0}
    with pytest.raises(BenchError, match="invalid_run_record"):
        validate(
            {
                "arm": "add",
                "wm": 1,
                "rep": 0,
                "status": "done",
                "metrics": metrics,
                "artifacts": {"workspace": "w", "transcript": "t", "oracle_report": "o"},
            }
        )
