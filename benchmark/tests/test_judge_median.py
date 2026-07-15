"""Median-of-N judging (bench-judge-median fast task): variance-resistant
judging via judge_fidelity_median + auditable raw scores.

`judge_fidelity_median` itself is unchanged and still tested here. What CHANGED
at honest-fidelity-meter: the judge LEFT the score_record metric path entirely
(fidelity is now deterministic requirement_coverage). Task judge-advisory then
re-added the judge as an advisory, source-aware `code_quality_annotation`
artifact (never a metric) — so the integration test pins that the annotation
lands in `artifacts`, never in `metrics`, and the old `judge_scores` sentinel
is gone."""
from __future__ import annotations

import json
import sys
import textwrap

import pytest

from benchmark.judge import judge_fidelity_median
from benchmark.schema.run_record import BenchError
from benchmark.score import score_record


def _stateful_judge(tmp_path, outputs):
    """A fake judge argv that emits outputs[k] on its k-th invocation,
    counting via a state file. An output of "ERR" exits nonzero with empty
    stdout (judge_fidelity raises unparseable)."""
    state = tmp_path / "judge_calls.txt"
    script = tmp_path / "fake_judge.py"
    script.write_text(textwrap.dedent(f"""
        import pathlib, sys
        state = pathlib.Path({str(state)!r})
        k = int(state.read_text()) if state.exists() else 0
        state.write_text(str(k + 1))
        outputs = {outputs!r}
        out = outputs[min(k, len(outputs) - 1)]
        if out == "ERR":
            sys.exit(3)
        print(out)
    """))
    return [sys.executable, str(script)]


def test_median_of_three_varying_scores(tmp_path):
    cmd = _stateful_judge(tmp_path, ["0.9", "0.5", "0.9"])
    median, scores = judge_fidelity_median(tmp_path, 1, {}, judge_cmd=cmd, n=3)
    assert median == 0.9
    assert scores == [0.9, 0.5, 0.9]


def test_tolerates_one_failed_call(tmp_path):
    cmd = _stateful_judge(tmp_path, ["ERR", "0.8", "0.6"])
    median, scores = judge_fidelity_median(tmp_path, 1, {}, judge_cmd=cmd, n=3)
    assert scores == [0.8, 0.6]
    assert median == pytest.approx(0.7)  # median of 2 = mean


def test_two_failures_raise(tmp_path):
    cmd = _stateful_judge(tmp_path, ["ERR", "ERR", "0.8"])
    with pytest.raises(BenchError, match="only 1/3 judge calls succeeded"):
        judge_fidelity_median(tmp_path, 1, {}, judge_cmd=cmd, n=3)


def test_score_record_annotates_judge_out_of_metric_path(tmp_path, monkeypatch):
    """The judge no longer feeds any metric: score_record records deterministic
    requirement_coverage and no spec_fidelity, and the judge's output lands in
    `artifacts["code_quality_annotation"]` (never in metrics); the old
    `judge_scores` deferral sentinel is gone."""
    ws = tmp_path / "runs" / "vanilla" / "wm1" / "workspace"
    ws.mkdir(parents=True)
    record = {
        "arm": "vanilla", "wm": 1, "rep": 0, "status": "done",
        "metrics": {"regression_rate": 0.0, "requirement_coverage": 0.0,
                    "oracle_pass_rate": 0.0, "tokens_total": 10.0, "cost_usd": 0.1,
                    "context_rot_slope": 0.0, "time_to_first_edit": 1.0},
        "artifacts": {"workspace": str(ws), "transcript": "", "oracle_report": "",
                      "attempts": "attempt 1: done"},
    }
    (tmp_path / "runs" / "vanilla" / "wm1" / "record.json").write_text(json.dumps(record))

    # deterministic seams — no live pytest / app boot in this wiring test.
    monkeypatch.setattr("benchmark.score.compute_requirement_coverage", lambda ws, wm, family="wm": 0.5)
    monkeypatch.setattr("benchmark.score.compute_oracle_pass_rate", lambda ws, wm, family="wm": 1.0)
    monkeypatch.setattr("benchmark.score.compute_regression_rate_v2", lambda ws, wm, family="wm": 0.0)

    cmd = _stateful_judge(tmp_path, ["0.9", "0.5", "0.9"])
    scored = score_record("vanilla", 1, judge_cmd=cmd, runs_root=tmp_path / "runs")

    assert scored.metrics["requirement_coverage"] == 0.5
    assert "spec_fidelity" not in scored.metrics
    assert "judge_scores" not in scored.artifacts
    assert "code_quality_annotation" in scored.artifacts
    assert "code_quality_annotation" not in scored.metrics
    # judge_cmd supplied + would-succeed -> the annotation is that judge's stdout
    assert scored.artifacts["code_quality_annotation"] == "0.9"
