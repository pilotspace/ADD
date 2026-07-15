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

from benchmark import judge, tamper
from benchmark.arms.loader import ARM_NAMES
from benchmark.runner.records import DEFAULT_RUNS_ROOT, write_record_atomic
from benchmark.schema.run_record import BenchError, RunRecord, validate

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
WM3_REGRESSION_TEST_PATH = REPO_ROOT / "benchmark" / "workload" / "wm3" / "oracle" / "test_refactor.py"
REGRESSION_SUBPROCESS_TIMEOUT_S = 300.0
VALID_WMS = (1, 2, 3, 4, 5, 6)

_PASS_RE = re.compile(r"(\d+) passed")
_FAIL_RE = re.compile(r"(\d+) failed")
_ERROR_RE = re.compile(r"(\d+) error")


def _record_path(runs_root: pathlib.Path, arm_name: str, wm: int, family: str = "wm") -> pathlib.Path:
    return runs_root / arm_name / f"{family}{wm}" / "record.json"


def read_prior_wm_record(
    arm_name: str, wm: int, *, runs_root: pathlib.Path | None = None, family: str = "wm"
) -> RunRecord:
    """Read a sibling WM's already-scored record.json.

    Raises BenchError("missing_prior_wm_record: ...") if absent or not
    status == "done" — a WM3 score cannot borrow a still-placeholder or
    unfinished prior-WM fidelity value.
    """
    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT
    path = _record_path(root, arm_name, wm, family)
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


def _run_oracle_suites(
    workspace: pathlib.Path,
    oracle_paths: list[pathlib.Path],
    error_code: str,
    marker_expr: str | None = None,
) -> tuple[int, int]:
    """Run pytest over `oracle_paths` against `workspace` (BENCH_WORKSPACE);
    return (failed+errored, total). Raises BenchError("<error_code>: ...") on
    a collection/execution error (exit outside {0,1}) or zero collected —
    never conflated with a normal test failure, which is signal, not error.
    `marker_expr` (pytest -m) lets a caller deselect probes that don't belong
    to its metric — e.g. wm3's regression re-exports out of the fidelity run."""
    from benchmark.workload._oracle_lib import isolated_workspace  # lazy: avoids import cycle

    marker_args = ["-m", marker_expr] if marker_expr else []
    # HERMETIC (hermetic-scoring): the oracle/regression probes boot the app via
    # BENCH_WORKSPACE — point it at a store-reset copy so their bookings never
    # mutate the source and oracle_pass_rate is reproducible on archived builds.
    with isolated_workspace(workspace) as iso_ws:
        proc = subprocess.run(
            [
                *_pytest_argv(),
                "-p",
                "no:cacheprovider",
                "--tb=no",
                "-q",
                *marker_args,
                *[str(p) for p in oracle_paths],
            ],
            cwd=str(REPO_ROOT),
            env={**os.environ, "BENCH_WORKSPACE": str(iso_ws)},
            capture_output=True,
            text=True,
            timeout=REGRESSION_SUBPROCESS_TIMEOUT_S,
        )
    if proc.returncode not in (0, 1):
        raise BenchError(
            f"{error_code}: pytest exited {proc.returncode}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    summary = proc.stdout
    passed = _extract_count(_PASS_RE, summary)
    failed = _extract_count(_FAIL_RE, summary)
    errored = _extract_count(_ERROR_RE, summary)
    total = passed + failed + errored
    if total == 0:
        raise BenchError(
            f"{error_code}: no oracle tests collected\n{summary}\nstderr:\n{proc.stderr}"
        )
    return failed + errored, total


def compute_oracle_pass_rate(workspace: pathlib.Path, wm: int, family: str = "wm") -> float:
    """The DETERMINISTIC fidelity of record (v2-meter-fixes M1): run the WM's
    OWN oracle probe suite (workload/wm{wm}/oracle/) against the workspace and
    return passed/total in [0.0, 1.0]. No LLM in the path — identical inputs
    yield the identical value. An unbootable workspace fails every probe as an
    ordinary connection error -> 0.0, never a harness crash.
    Raises BenchError("oracle_run_failed: ...") on exit outside {0,1} or zero
    collected — a 0/0 is an error, never a silent score.

    Marked regression re-exports are DESELECTED (live defect 2026-07-10,
    meter defect #4): wm3's oracle dir re-exports the wm1+wm2 suites for the
    v1 regression path, and the legacy_shape-marked ones fail BY CONSTRUCTION
    on a correct wm3 app — unfiltered they capped the fidelity ceiling at 0.42
    and every arm scored an identical artifact 0.25. Fidelity of record is the
    WM's own probes only; regression is survivors-based and separate.

    `family` (wv2-family M1) names the workload track (wm | hv) — resolution
    is family-local; an unknown family fails loud BEFORE any spawn."""
    oracle_dir = REPO_ROOT / "benchmark" / "workload" / f"{family}{wm}" / "oracle"
    if not oracle_dir.is_dir():
        raise BenchError(f"unknown_workload_family: {oracle_dir} does not exist")
    bad, total = _run_oracle_suites(
        workspace, [oracle_dir], "oracle_run_failed",
        marker_expr="not regression and not legacy_shape",
    )
    return (total - bad) / total


def validate_checklist(rows: object) -> None:
    """A frozen requirement checklist is a non-empty list of rows, each a mapping
    carrying `id`, `description`, and a callable `probe` — a row missing any of
    these (R2) raises BenchError("invalid_checklist: ...") before any scoring."""
    if not isinstance(rows, list) or not rows:
        raise BenchError("invalid_checklist: REQUIREMENTS must be a non-empty list")
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or not all(k in row for k in ("id", "description", "probe")):
            raise BenchError(f"invalid_checklist: row {i} must carry id, description, probe")
        if not callable(row["probe"]):
            raise BenchError(f"invalid_checklist: row {i} probe must be callable")


def _load_checklist(wm: int, family: str = "wm") -> list[dict]:
    """Import `workload/{family}{wm}/checklist.py` and return its validated
    `REQUIREMENTS` list. Raises `missing_checklist` if the module is absent,
    `invalid_checklist` (via validate_checklist) if a row is malformed."""
    mod_path = REPO_ROOT / "benchmark" / "workload" / f"{family}{wm}" / "checklist.py"
    if not mod_path.exists():
        raise BenchError(f"missing_checklist: {mod_path} does not exist")
    spec = importlib.util.spec_from_file_location(f"_checklist_{family}{wm}", mod_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = getattr(module, "REQUIREMENTS", None)
    validate_checklist(rows)
    return rows


def compute_requirement_coverage(workspace: pathlib.Path, wm: int, family: str = "wm") -> float:
    """The DETERMINISTIC fidelity of record (honest-fidelity-meter): run the WM's
    FROZEN requirement checklist against the built app and return covered/total in
    [0,1]. Every PROMPT.md requirement is one row with a real probe — so an app
    that boots but omits a requirement (CLI, field validation) scores below 1.0,
    unlike oracle_pass_rate which is blind to un-probed requirements.

    NO LLM in the path — identical workspace yields the identical value. Fail-closed
    (M3): an unbootable app or a raising probe counts its requirement NOT covered;
    the scorer always returns a fraction, never propagates the probe's exception.
    Raises only on a guard breach: a malformed checklist (R2) or a value ∉ [0,1] (R3)."""
    from benchmark.workload._oracle_lib import isolated_workspace, running_app  # lazy: avoids import cycle

    rows = _load_checklist(wm, family)
    total = len(rows)
    covered = 0
    try:
        # HERMETIC (hermetic-scoring): boot a store-reset copy so probe writes
        # land in a throwaway dir — the source is never mutated and repeated
        # scorings of the same archived workspace are reproducible.
        with isolated_workspace(workspace) as iso_ws:
            with running_app(str(iso_ws)) as base:
                for row in rows:
                    try:
                        if row["probe"](base, iso_ws):
                            covered += 1
                    except Exception:
                        pass  # fail-closed: a raising probe = requirement NOT covered
    except Exception:
        covered = 0  # unbootable workspace: nothing covered, never a scorer crash
    value = covered / total
    if not (0.0 <= value <= 1.0):
        raise BenchError(f"invalid_coverage: {value!r} out of [0.0, 1.0]")
    return value


def _read_prior_metrics_lenient(
    root: pathlib.Path, arm_name: str, wm: int, family: str = "wm"
) -> dict:
    """Read a prior WM's record.json metrics WITHOUT strict validate() — a legacy
    record carries only `spec_fidelity` (no `requirement_coverage`) and would be
    rejected by the v3 schema, but the slope prior-read must still see its value.
    Enforces the same absent/not-done guard as read_prior_wm_record."""
    path = _record_path(root, arm_name, wm, family)
    if not path.exists():
        raise BenchError(f"missing_prior_wm_record: {path} does not exist")
    data = json.loads(path.read_text())
    if data.get("status") != "done":
        raise BenchError(f"missing_prior_wm_record: {path} status={data.get('status')!r} (must be 'done')")
    return data.get("metrics", {})


def _read_target_record_lenient(record_path: pathlib.Path) -> RunRecord:
    """Read the record being scored WITHOUT strict validate(), constructing the
    RunRecord dataclass directly. An archived v1/v2 record carries the retired
    `spec_fidelity` (no `requirement_coverage`) and would be rejected by the v3
    schema — yet RE-SCORING is precisely how it migrates forward: score_record
    recomputes every metric and re-validates the full dict before writing, so
    the target read need not (and must not) pre-validate. Malformed shapes still
    fail loud (KeyError/TypeError surface as a clear error, never a silent skip)."""
    data = json.loads(record_path.read_text())
    return RunRecord(
        arm=str(data["arm"]),
        wm=int(data["wm"]),
        rep=int(data["rep"]),
        status=str(data["status"]),
        metrics=dict(data["metrics"]),
        artifacts=dict(data["artifacts"]),
    )


def _prior_fidelity_value(metrics: dict) -> float:
    """The slope-trajectory value of a prior WM: its deterministic
    `requirement_coverage`, or (archived-record shim, M4) its legacy
    `spec_fidelity` when coverage is absent; 0.0 if neither exists."""
    v = metrics.get("requirement_coverage", metrics.get("spec_fidelity", 0.0))
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0


def compute_regression_rate_v2(workspace: pathlib.Path, wm: int, family: str = "wm") -> float:
    """v2 regression semantics (v2-wv1-longitudinal §3 @ v3, M7 — supersedes
    the wholesale-suite form): re-run each earlier WM's SURVIVORS — the
    auth-carrying, shape-tolerant must-survive invariants in
    workload/wm{k}/oracle/survivors.py — against the CURRENT workspace;
    return (failed+errored)/total. wm==1 -> 0.0 by definition, no spawn.

    Why not the whole earlier suites: later WMs legitimately supersede
    earlier observable behavior (WM2's mandatory auth 401s WM1's
    unauthenticated probes; WM3's shape break 400s duration_minutes) — the
    live rep0 campaign scored a CORRECT auth implementation regression=1.0
    on wholesale re-runs, inverting the incentive.

    Raises BenchError("regression_run_failed: ...") on a missing survivors
    file (checked BEFORE any spawn), exit outside {0,1}, or zero collected."""
    if wm == 1:
        return 0.0
    earlier = [
        REPO_ROOT / "benchmark" / "workload" / f"{family}{prior}" / "oracle" / "survivors.py"
        for prior in range(1, wm)
    ]
    missing = [str(p) for p in earlier if not p.exists()]
    if missing:
        raise BenchError(
            "regression_run_failed: missing survivors file(s) "
            f"{missing} — every WM below {family}{wm} needs must-survive probes before it can be scored"
        )
    bad, total = _run_oracle_suites(workspace, earlier, "regression_run_failed")
    return bad / total


def _extract_count(pattern: re.Pattern, text: str) -> int:
    match = pattern.search(text)
    return int(match.group(1)) if match else 0


def _fidelity_artifacts(prior_fidelities: list[float], wm3_fidelity: float) -> dict[str, str]:
    """WM3 trajectory + min artifacts (bench-fidelity-dip). OLS slope at n=3 is
    (f3-f1)/2 — the middle WM has zero weight — so a mid-run collapse is invisible
    to context_rot_slope. Artifacts only; the frozen 5-metric set is untouched."""
    fids = [*prior_fidelities, wm3_fidelity]
    return {
        "fidelity_trajectory": ";".join(str(f) for f in fids),
        "fidelity_min": str(min(fids)),
    }


def _tokens_uncached(transcript_path: pathlib.Path) -> int:
    """Uncached completion tokens — input + cache_creation + output from the final
    usage event; the honest "new LLM work" measure (cache reads bill ~10% and are
    99% of a many-turn loop's raw volume). Artifact only; metrics untouched."""
    if not transcript_path.exists():
        return 0
    for line in reversed(transcript_path.read_text(errors="replace").splitlines()):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = event.get("usage") if isinstance(event, dict) else None
        if isinstance(usage, dict) and usage:
            return (int(usage.get("input_tokens", 0))
                    + int(usage.get("cache_creation_input_tokens", 0))
                    + int(usage.get("output_tokens", 0)))
    return 0


def _engine_call_census(transcript_path: pathlib.Path) -> int:
    """Count `add.py <subcommand>` invocations in a run transcript — the loop-adherence
    census (bench-adherence-census). A comparative ARTIFACT, never a metric: the frozen
    5-metric set is untouched. 0 when the transcript is missing or engine-silent."""
    if not transcript_path.exists():
        return 0
    return len(re.findall(r"add\.py\s+[a-z][a-z-]*", transcript_path.read_text(errors="replace")))


def score_record(
    arm_name: str,
    wm: int,
    *,
    judge_cmd: Sequence[str] | None = None,
    runs_root: pathlib.Path | None = None,
    family: str = "wm",
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
    record_path = _record_path(root, arm_name, wm, family)
    if not record_path.exists():
        raise BenchError(f"record_not_found: {record_path}")

    # Lenient target read: an archived v1/v2 record carries the retired
    # spec_fidelity and would fail strict validate() — re-scoring migrates it
    # forward (recompute + re-validate before write, below).
    record = _read_target_record_lenient(record_path)
    if record.status != "done":
        raise BenchError(f"record_not_done: status={record.status!r} (nothing to score)")

    # WM>=3 needs every prior WM's already-scored spec_fidelity before computing
    # anything — checked (and may raise missing_prior_wm_record) before any
    # compute/write, per the all-or-nothing safety rule. (bench-wm4plus-horizon:
    # generalized from wm==3 so the slope spans the full trajectory at WM4/WM5.)
    prior_fidelities: list[float] = []
    if wm >= 3:
        for prior_wm in range(1, wm):
            prior_metrics = _read_prior_metrics_lenient(root, arm_name, prior_wm, family)
            prior_fidelities.append(_prior_fidelity_value(prior_metrics))

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

    # Deterministic fidelity of record (honest-fidelity-meter): requirement_coverage
    # from the WM's frozen checklist — the ONLY fidelity signal, NO LLM in the path.
    # The LLM judge is back only as an advisory, source-aware `code_quality_annotation`
    # artifact (never a metric): claude-less by default (judge_cmd None -> "unavailable",
    # no subprocess), best-effort when a judge_cmd is supplied.
    requirement_coverage = compute_requirement_coverage(workspace, wm, family)
    artifacts["code_quality_annotation"] = judge.code_quality_annotation(
        workspace, wm, judge_cmd=judge_cmd
    )

    transcript_str = artifacts.get("transcript", "")
    artifacts["engine_calls"] = str(
        _engine_call_census(pathlib.Path(transcript_str)) if transcript_str else 0
    )
    artifacts["tokens_uncached"] = str(
        _tokens_uncached(pathlib.Path(transcript_str)) if transcript_str else 0
    )

    if wm >= 3:
        # context_rot_slope over the FULL requirement_coverage trajectory at every
        # WM>=3 — now a deterministic coverage-degradation signal (was judge-fed).
        context_rot_slope = compute_context_rot_slope([*prior_fidelities, requirement_coverage])
        artifacts.update(_fidelity_artifacts(prior_fidelities, requirement_coverage))
    else:
        context_rot_slope = 0.0

    # v2 regression semantics at EVERY WM (v2-meter-fixes M2/M7): re-run all
    # earlier WMs' oracle suites; wm==1 -> 0.0 by definition. The record
    # self-describes which semantics produced the number (regression_source).
    regression_rate = compute_regression_rate_v2(workspace, wm, family)
    artifacts["regression_source"] = "v2-earlier-oracles"

    metrics.pop("spec_fidelity", None)  # v3: the retired LLM metric never survives into a scored record
    metrics["requirement_coverage"] = requirement_coverage
    metrics["regression_rate"] = regression_rate
    metrics["context_rot_slope"] = context_rot_slope

    # black-box behavioral floor (now REQUIRED) — always computed.
    metrics["oracle_pass_rate"] = compute_oracle_pass_rate(workspace, wm, family)

    # v2 mechanical tamper count (M4/M7) — only when the snapshot pair for
    # this WM exists (run_pilot writes them; a hand-scored record without
    # snapshots simply omits the OPTIONAL key).
    arm_root = root / arm_name
    snap_current = arm_root / "snapshots" / f"{family}{wm}"
    snap_prior = arm_root / "snapshots" / f"{family}{wm - 1}"
    if wm == 1 and snap_current.is_dir():
        metrics["tests_weakened"] = 0.0  # by definition at the first WM
    elif wm >= 2 and snap_current.is_dir() and snap_prior.is_dir():
        metrics["tests_weakened"] = float(tamper.compute_tests_weakened(arm_root, wm, family))

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
