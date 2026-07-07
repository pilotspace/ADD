"""score — computes the 5 frozen metrics for a finished arm×WM run from
artifacts alone (bench-scoring TASK.md §3 CONTRACT @ v1).

Orchestrates read -> validate-eligibility -> compute -> write_record_atomic,
reusing the frozen `RunRecord`/`validate` shape and `write_record_atomic`
writer verbatim (second writer, not a second schema). Stdlib-first,
fail-loud: every Reject case raises BenchError("<code>: ...") before any
disk write; a scored write is all-or-nothing.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
from typing import Sequence

from benchmark import judge
from benchmark.arms.loader import ARM_NAMES
from benchmark.runner.records import DEFAULT_RUNS_ROOT, write_record_atomic
from benchmark.schema.run_record import BenchError, RunRecord, validate

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
WM3_REGRESSION_TEST_PATH = REPO_ROOT / "benchmark" / "workload" / "wm3" / "oracle" / "test_refactor.py"
REGRESSION_SUBPROCESS_TIMEOUT_S = 300.0
VALID_WMS = (1, 2, 3)

_PASS_RE = re.compile(r"(\d+) passed")
_FAIL_RE = re.compile(r"(\d+) failed")
_ERROR_RE = re.compile(r"(\d+) error")


def _record_path(runs_root: pathlib.Path, arm_name: str, wm: int) -> pathlib.Path:
    return runs_root / arm_name / f"wm{wm}" / "record.json"


def read_prior_wm_record(arm_name: str, wm: int, *, runs_root: pathlib.Path | None = None) -> RunRecord:
    """Read a sibling WM's already-scored record.json.

    Raises BenchError("missing_prior_wm_record: ...") if absent or not
    status == "done" — a WM3 score cannot borrow a still-placeholder or
    unfinished prior-WM fidelity value.
    """
    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT
    path = _record_path(root, arm_name, wm)
    if not path.exists():
        raise BenchError(f"missing_prior_wm_record: {path} does not exist")
    record = RunRecord.from_json(path.read_text())
    if record.status != "done":
        raise BenchError(f"missing_prior_wm_record: {path} status={record.status!r} (must be 'done')")
    return record


def compute_context_rot_slope(fidelities: list[float]) -> float:
    """Pure least-squares slope over (index, fidelity) pairs, 1-indexed by WM.

    slope = Σ((x-x̄)(y-ȳ)) / Σ((x-x̄)²)
    """
    n = len(fidelities)
    xs = list(range(1, n + 1))
    x_bar = sum(xs) / n
    y_bar = sum(fidelities) / n
    numerator = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, fidelities))
    denominator = sum((x - x_bar) ** 2 for x in xs)
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _pytest_argv() -> list[str]:
    """A pytest-capable interpreter argv: the current interpreter when pytest
    is importable in it, else the uv-managed fallback — the live-pilot host's
    `sys.executable` (homebrew 3.14) has no pytest, and its "No module named
    pytest" exit-1 otherwise parses as a silent zero-collection."""
    if importlib.util.find_spec("pytest") is not None:
        return [sys.executable, "-m", "pytest"]
    return ["uv", "run", "--no-project", "--with", "pytest", "python", "-m", "pytest"]


def compute_regression_rate(workspace: pathlib.Path) -> float:
    """Run `pytest -m regression` against the WM3 oracle re-exports for
    `workspace`; return failed_count / total_regression_count.

    Raises BenchError("regression_run_failed: ...") on a collection/
    execution error (pytest exit codes outside {0 (all passed), 1 (some
    failed)}) — never conflated with a normal test failure, which is
    signal, not error.
    """
    proc = subprocess.run(
        [
            *_pytest_argv(),
            "-m",
            "regression",
            "-p",
            "no:cacheprovider",
            "--tb=no",
            "-q",
            str(WM3_REGRESSION_TEST_PATH),
        ],
        cwd=str(REPO_ROOT),
        env={**os.environ, "BENCH_WORKSPACE": str(workspace)},
        capture_output=True,
        text=True,
        timeout=REGRESSION_SUBPROCESS_TIMEOUT_S,
    )
    if proc.returncode not in (0, 1):
        raise BenchError(
            f"regression_run_failed: pytest exited {proc.returncode}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )

    summary = proc.stdout
    passed = _extract_count(_PASS_RE, summary)
    failed = _extract_count(_FAIL_RE, summary)
    errored = _extract_count(_ERROR_RE, summary)
    total = passed + failed + errored
    if total == 0:
        raise BenchError(
            f"regression_run_failed: no regression tests collected\n{summary}\nstderr:\n{proc.stderr}"
        )
    return (failed + errored) / total


def _extract_count(pattern: re.Pattern, text: str) -> int:
    match = pattern.search(text)
    return int(match.group(1)) if match else 0


def score_record(
    arm_name: str,
    wm: int,
    *,
    judge_cmd: Sequence[str] | None = None,
    runs_root: pathlib.Path | None = None,
) -> RunRecord:
    """Orchestrate read -> validate-eligibility -> compute -> write_record_atomic.

    Raises BenchError("<code>: ...") for every Reject case; never partially
    writes — the full 5-key metrics dict is validate()'d once, in memory,
    before write_record_atomic is ever called.
    """
    if wm not in VALID_WMS:
        raise BenchError(f"invalid_wm: {wm} not in {VALID_WMS}")
    if arm_name not in ARM_NAMES:
        raise BenchError(f"unknown_arm: {arm_name!r} not in {ARM_NAMES}")

    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT
    record_path = _record_path(root, arm_name, wm)
    if not record_path.exists():
        raise BenchError(f"record_not_found: {record_path}")

    record = RunRecord.from_json(record_path.read_text())
    if record.status != "done":
        raise BenchError(f"record_not_done: status={record.status!r} (nothing to score)")

    # WM3 needs WM1+WM2's own already-scored spec_fidelity before computing
    # anything — checked (and may raise missing_prior_wm_record) before any
    # compute/write, per the all-or-nothing safety rule.
    prior_fidelities: list[float] = []
    if wm == 3:
        wm1_record = read_prior_wm_record(arm_name, 1, runs_root=root)
        wm2_record = read_prior_wm_record(arm_name, 2, runs_root=root)
        prior_fidelities = [wm1_record.metrics["spec_fidelity"], wm2_record.metrics["spec_fidelity"]]

    metrics = dict(record.metrics)
    artifacts = dict(record.artifacts)

    # M2: tokens_total/cost_usd/time_to_first_edit are VALIDATED, never
    # recomputed — the runner already wrote real values from the transcript.
    for key in ("tokens_total", "cost_usd", "time_to_first_edit"):
        value = metrics.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise BenchError(f"invalid_run_record: metrics[{key!r}] must be numeric and >= 0, got {value!r}")

    if artifacts.get("token_source") == "unparseable":
        existing = artifacts.get("metrics_warnings", "")
        note = "tokens_total unparseable-sourced (token_source=unparseable)"
        artifacts["metrics_warnings"] = f"{existing}; {note}" if existing else note

    workspace = pathlib.Path(artifacts["workspace"])
    oracle_report_path_str = artifacts.get("oracle_report", "")
    oracle_report: dict = {}
    if oracle_report_path_str:
        oracle_report_path = pathlib.Path(oracle_report_path_str)
        if oracle_report_path.exists():
            oracle_report = json.loads(oracle_report_path.read_text())

    # M3: spec_fidelity always recomputed via the injectable judge seam —
    # median-of-3 to damp single-call variance, raw scores kept auditable.
    spec_fidelity, judge_scores = judge.judge_fidelity_median(
        workspace, wm, oracle_report, judge_cmd=judge_cmd
    )
    artifacts["judge_scores"] = ";".join(str(s) for s in judge_scores)

    if wm == 3:
        # M4/M6: regression_rate + context_rot_slope are real computations at WM3.
        regression_rate = compute_regression_rate(workspace)
        context_rot_slope = compute_context_rot_slope([*prior_fidelities, spec_fidelity])
    else:
        # M5/M7: 0.0 BY DEFINITION before WM3 — structurally N/A, not a failure;
        # an unconditional early-return branch, never routed through a Reject raise.
        regression_rate = 0.0
        context_rot_slope = 0.0

    metrics["spec_fidelity"] = spec_fidelity
    metrics["regression_rate"] = regression_rate
    metrics["context_rot_slope"] = context_rot_slope

    updated = validate(
        {
            "arm": record.arm,
            "wm": record.wm,
            "rep": record.rep,
            "status": record.status,
            "metrics": metrics,
            "artifacts": artifacts,
        }
    )
    write_record_atomic(record_path, updated)
    return updated
