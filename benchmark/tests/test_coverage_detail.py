"""Red/green for coverage-detail (honest-fidelity-meter, frozen §3 v1).

`score_record` emits a per-WM `coverage_detail` artifact — one {"id","covered"}
row per frozen checklist requirement — so every `requirement_coverage` score is
self-explaining (a 0.0 says WHICH requirements failed, not just that it failed).
Non-gating: an `artifacts` string, never a metric; the float is derived from the
SAME detail (one boot) so they can never disagree.

Reuses the WM1 booking-app fixtures from test_requirement_coverage.
"""
from __future__ import annotations

import json

import pytest

from benchmark import score as score_mod
from benchmark.schema.run_record import (
    OPTIONAL_METRICS,
    REQUIRED_METRICS,
    BenchError,
    validate,
)
from benchmark.tests.test_requirement_coverage import _write_wm1_app


def _checklist_ids(wm):
    return [r["id"] for r in score_mod._load_checklist(wm, "wm")]


# --- M1/M2: shape + agreement with the aggregate (single boot) -----------------

def test_coverage_detail_shape_and_agrees_with_coverage(tmp_path):
    ws = tmp_path / "workspace"
    _write_wm1_app(ws)  # complete WM1 app -> every requirement covered
    detail = score_mod.compute_coverage_detail(ws, 1)

    assert [d["id"] for d in detail] == _checklist_ids(1)  # one row per req, in order
    assert all(isinstance(d["covered"], bool) for d in detail)
    assert all(d["covered"] for d in detail)  # complete app
    # the float is DERIVED from this detail -> they agree by construction
    assert score_mod._coverage_from_detail(detail) == score_mod.compute_requirement_coverage(ws, 1) == 1.0


def test_coverage_detail_flags_the_uncovered_row(tmp_path):
    ws = tmp_path / "workspace"
    _write_wm1_app(ws, with_delete=False)  # DELETE disabled -> R-delete uncovered
    detail = score_mod.compute_coverage_detail(ws, 1)

    by_id = {d["id"]: d["covered"] for d in detail}
    assert by_id["R-delete"] is False
    covered = sum(1 for d in detail if d["covered"])
    assert score_mod._coverage_from_detail(detail) == score_mod.compute_requirement_coverage(ws, 1)
    assert score_mod._coverage_from_detail(detail) == covered / len(detail)


# --- M3: an unbootable app still emits a detail (all covered:false) -------------

def test_unbootable_workspace_detail_all_false(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()  # no app -> nothing boots
    detail = score_mod.compute_coverage_detail(ws, 1)

    assert [d["id"] for d in detail] == _checklist_ids(1)  # detail STILL present
    assert all(d["covered"] is False for d in detail)      # every row false, not mute
    assert score_mod.compute_requirement_coverage(ws, 1) == 0.0


# --- M1/M4: score_record persists the artifact, never a metric -----------------

def test_score_record_writes_coverage_detail(tmp_path, monkeypatch):
    ws = tmp_path / "runs" / "vanilla" / "wm2" / "workspace"
    ws.mkdir(parents=True)
    record = {
        "arm": "vanilla", "wm": 2, "rep": 0, "status": "done",
        "metrics": {"regression_rate": 0.0, "requirement_coverage": 0.0,
                    "oracle_pass_rate": 0.0, "tokens_total": 10.0, "cost_usd": 0.1,
                    "context_rot_slope": 0.0, "time_to_first_edit": 1.0},
        "artifacts": {"workspace": str(ws), "transcript": "", "oracle_report": "",
                      "attempts": "attempt 1: done"},
    }
    # wm2 needs a prior wm1 record for the (unused-here) slope chain? wm==2 < 3, so no.
    (tmp_path / "runs" / "vanilla" / "wm2" / "record.json").write_text(json.dumps(record))

    fake_detail = [
        {"id": "R-auth-401", "covered": True},
        {"id": "R-ownership-403", "covered": False},
        {"id": "R-double-booking-409", "covered": True},
        {"id": "R-cancellation-window-422", "covered": True},
        {"id": "R-tenant-isolation", "covered": True},
    ]  # 4/5 covered
    monkeypatch.setattr("benchmark.score.compute_coverage_detail", lambda ws, wm, family="wm": fake_detail)
    monkeypatch.setattr("benchmark.score.compute_oracle_pass_rate", lambda ws, wm, family="wm": 1.0)
    monkeypatch.setattr("benchmark.score.compute_regression_rate_v2", lambda ws, wm, family="wm": 0.0)

    scored = score_mod.score_record("vanilla", 2, runs_root=tmp_path / "runs")

    assert scored.metrics["requirement_coverage"] == 0.8              # derived from the detail
    assert "coverage_detail" not in scored.metrics                   # never a metric
    assert json.loads(scored.artifacts["coverage_detail"]) == fake_detail  # emitted verbatim


# --- R1: coverage_detail can never become a gating metric ----------------------

def test_coverage_detail_is_not_a_metric():
    assert "coverage_detail" not in REQUIRED_METRICS
    assert "coverage_detail" not in OPTIONAL_METRICS
    record = {
        "arm": "vanilla", "wm": 1, "rep": 0, "status": "done",
        "metrics": {
            "regression_rate": 0.0, "requirement_coverage": 1.0,
            "oracle_pass_rate": 1.0, "tokens_total": 10.0, "cost_usd": 0.1,
            "context_rot_slope": 0.0, "time_to_first_edit": 1.0,
            "coverage_detail": "[]",  # forbidden as a metric
        },
        "artifacts": {"workspace": "/x", "transcript": "", "oracle_report": ""},
    }
    with pytest.raises(BenchError, match="invalid_run_record"):
        validate(record)


# --- R2: a checklist row without a stable id is rejected -----------------------

def test_checklist_row_without_id_rejected():
    with pytest.raises(BenchError, match="invalid_checklist"):
        score_mod.validate_checklist([{"description": "x", "probe": lambda b, w: True}])
