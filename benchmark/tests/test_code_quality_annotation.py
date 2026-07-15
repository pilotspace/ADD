"""code_quality_annotation (task judge-advisory): the demoted LLM judge returns
as a SOURCE-AWARE, NON-GATING advisory artifact.

The honest-fidelity-meter law is "NO LLM in the metric path" — so the judge is
back only as an `artifacts` string, never a `metrics` key. It is CLAUDE-LESS BY
DEFAULT (no judge_cmd -> "unavailable", zero subprocesses, so deterministic
re-scoring never spawns an LLM) and BEST-EFFORT when a judge_cmd is supplied
(a judge failure degrades to "unavailable", never raises, never a score).
"""
from __future__ import annotations

import sys

import pytest

from benchmark import judge
from benchmark.judge import build_code_quality_prompt, code_quality_annotation
from benchmark.schema.run_record import BenchError, OPTIONAL_METRICS, REQUIRED_METRICS, validate


def _workspace_with_app(tmp_path, marker="SENTINEL_BOOKING_SYMBOL"):
    ws = tmp_path / "workspace"
    (ws / "app").mkdir(parents=True)
    (ws / "app" / "__init__.py").write_text("")
    (ws / "app" / "api.py").write_text(f"def {marker}():\n    return 'booking created'\n")
    return ws


# --- M3: claude-less by default (no subprocess) --------------------------------

def test_claudeless_by_default_no_subprocess(tmp_path, monkeypatch):
    ws = _workspace_with_app(tmp_path)
    calls = []
    monkeypatch.setattr(judge.subprocess, "run", lambda *a, **k: calls.append(a) or None)

    note = code_quality_annotation(ws, 1, judge_cmd=None)

    assert note.startswith("unavailable")
    assert calls == []  # NO LLM subprocess spawned on the deterministic path


# --- M2: source-aware prompt (reads the built app) -----------------------------

def test_prompt_is_source_aware(tmp_path):
    ws = _workspace_with_app(tmp_path)
    prompt = build_code_quality_prompt(1, ws)
    # the built app's actual source symbol is in the prompt (fixes the retired
    # rubric's artifact-blindness — it only saw PROMPT.md + oracle booleans)
    assert "SENTINEL_BOOKING_SYMBOL" in prompt
    assert "api.py" in prompt


# --- M4: best-effort when a judge_cmd IS supplied ------------------------------

def test_judge_cmd_stdout_becomes_the_annotation(tmp_path):
    ws = _workspace_with_app(tmp_path)
    cmd = [sys.executable, "-c", "print('idiomatic; small; clear')"]
    note = code_quality_annotation(ws, 1, judge_cmd=cmd)
    assert note == "idiomatic; small; clear"


def test_launch_failure_degrades_to_unavailable(tmp_path):
    ws = _workspace_with_app(tmp_path)
    note = code_quality_annotation(ws, 1, judge_cmd=["/no/such/judge/binary"])
    assert note.startswith("unavailable")  # never raises


def test_empty_judge_output_degrades_to_unavailable(tmp_path):
    ws = _workspace_with_app(tmp_path)
    cmd = [sys.executable, "-c", "import sys; sys.exit(3)"]  # nonzero, empty stdout
    note = code_quality_annotation(ws, 1, judge_cmd=cmd)
    assert note.startswith("unavailable")


# --- R1: the annotation can NEVER become a gating metric -----------------------

def test_code_quality_annotation_is_not_a_metric():
    assert "code_quality_annotation" not in REQUIRED_METRICS
    assert "code_quality_annotation" not in OPTIONAL_METRICS

    record = {
        "arm": "vanilla", "wm": 1, "rep": 0, "status": "done",
        "metrics": {
            "regression_rate": 0.0, "requirement_coverage": 1.0,
            "oracle_pass_rate": 1.0, "tokens_total": 10.0, "cost_usd": 0.1,
            "context_rot_slope": 0.0, "time_to_first_edit": 1.0,
            "code_quality_annotation": "looks clean",  # forbidden as a metric
        },
        "artifacts": {"workspace": "/x", "transcript": "", "oracle_report": ""},
    }
    with pytest.raises(BenchError, match="invalid_run_record"):
        validate(record)
