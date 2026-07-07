"""execute_wm — the one atomic-outcome unit (bench-runner TASK.md §5 Safety rule).

Workspace -> setup -> invoke (timeout+bounded retry) -> capture -> post-agent
app check -> isolation check -> record assembly -> atomic write. Sequential,
single-process, no concurrency (§1 chosen framing).
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import signal
import subprocess
import time
from typing import Sequence

from benchmark.arms.loader import Arm
from benchmark.check_isolation import find_leaks
from benchmark.check_isolation import main as check_isolation_main
from benchmark.runner.agent import build_argv
from benchmark.runner.pin import resolve_pin
from benchmark.runner.records import DEFAULT_RUNS_ROOT, write_record_atomic
from benchmark.schema.run_record import RunRecord, validate
from benchmark.workload._oracle_lib import http_call, running_app

BENCHMARK_ROOT = pathlib.Path(__file__).resolve().parents[1]

_EDIT_TOOL_NAMES = frozenset({"Edit", "Write"})


def _prompt_path(wm: int) -> pathlib.Path:
    return BENCHMARK_ROOT / "workload" / f"wm{wm}" / "PROMPT.md"


def _wrap_prompt(text: str, wrapper: str) -> str:
    if wrapper == "plan-then-execute":
        return f"Plan first, then execute:\n\n{text}"
    return text  # "raw" (and any unrecognized wrapper) passes through verbatim


def _invoke_once(argv: list[str], *, timeout_s: float, log_path: pathlib.Path) -> tuple[str, list[str], float]:
    """Run one attempt. Returns (outcome, stdout_lines, first_edit_elapsed_s).

    outcome is "done" (exit 0), "failed" (nonzero exit), or "timeout".
    Kills the whole process group on timeout so no zombie survives.
    """
    start = time.monotonic()
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,  # own process group -> killable as a unit
    )
    lines: list[str] = []
    first_edit_elapsed = 0.0
    timed_out = False
    try:
        stdout_text, _ = proc.communicate(timeout=timeout_s)
        rc = proc.returncode
        outcome = "done" if rc == 0 else "failed"
        lines = (stdout_text or "").splitlines()
        elapsed_total = time.monotonic() - start
        for idx, line in enumerate(lines):
            with contextlib.suppress(json.JSONDecodeError):
                event = json.loads(line)
                if _is_edit_event(event):
                    # true per-event timestamps aren't available once the
                    # stream is drained via communicate(); approximate by the
                    # event's position in the run's total elapsed time.
                    first_edit_elapsed = elapsed_total * (idx + 1) / max(len(lines), 1)
                    break
    except subprocess.TimeoutExpired:
        timed_out = True
        outcome = "timeout"
    finally:
        if proc.poll() is None:
            _kill_process_group(proc)
            with contextlib.suppress(Exception):
                proc.wait(timeout=5)
    if timed_out:
        with contextlib.suppress(Exception):
            # drain whatever partial output exists so it still lands in the transcript
            if proc.stdout is not None:
                lines = (proc.stdout.read() or "").splitlines()

    with log_path.open("a") as fh:
        fh.write("\n".join(lines))
        fh.write("\n")

    return outcome, lines, first_edit_elapsed


def _kill_process_group(proc: subprocess.Popen) -> None:
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)


def _is_edit_event(event: object) -> bool:
    if not isinstance(event, dict):
        return False
    if event.get("type") == "tool_use" and event.get("name") in _EDIT_TOOL_NAMES:
        return True
    message = event.get("message")
    if isinstance(message, dict):
        for block in message.get("content", []) or []:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") in _EDIT_TOOL_NAMES:
                return True
    return False


def _parse_tokens_and_cost(lines: list[str]) -> tuple[int, float, bool]:
    """Return (tokens_total, cost_usd, unparseable) from the stream-json
    lines' final result event, per the pinned live-spike field names."""
    for line in reversed(lines):
        with contextlib.suppress(json.JSONDecodeError):
            event = json.loads(line)
            if not isinstance(event, dict):
                continue
            usage = event.get("usage")
            if isinstance(usage, dict) and ("total_cost_usd" in event or usage):
                tokens_total = (
                    int(usage.get("input_tokens", 0))
                    + int(usage.get("cache_creation_input_tokens", 0))
                    + int(usage.get("cache_read_input_tokens", 0))
                    + int(usage.get("output_tokens", 0))
                )
                cost_usd = float(event.get("total_cost_usd", 0.0))
                return tokens_total, cost_usd, False
    return 0, 0.0, True


def _post_agent_app_check(workspace_dir: pathlib.Path) -> dict[str, object]:
    """Confirm the workspace's app answers its entry contract (closes the
    bench-scaffold dead-code finding on running_app/http_call). Never
    raises — an unreachable app is recorded, not a harness crash."""
    try:
        with running_app(str(workspace_dir)) as base_url:
            try:
                status, _ = http_call("GET", f"{base_url}/bookings")
                return {"app_reachable": True, "status": status}
            except AssertionError as exc:
                return {"app_reachable": False, "detail": str(exc)}
    except Exception as exc:  # pragma: no cover - defensive, never crash the run
        return {"app_reachable": False, "detail": str(exc)}


def _isolation_check(workspace_dir: pathlib.Path) -> tuple[bool, list[str]]:
    """Return (clean, leak_paths) — runs check_isolation.main (the runner is
    its first non-test caller) and also surfaces leak paths for artifacts."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check_isolation_main([str(workspace_dir)])
    leaks = [str(p) for p in find_leaks(workspace_dir)]
    return rc == 0, leaks


def execute_wm(
    arm: Arm,
    wm: int,
    *,
    agent_cmd: Sequence[str] | None = None,
    timeout_s: float = 1800.0,
    retries: int = 1,
    runs_root: pathlib.Path | None = None,
) -> RunRecord:
    """Drive one arm x WM end-to-end and write exactly one RunRecord."""
    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT
    wm_dir = root / arm.name / f"wm{wm}"
    workspace_dir = wm_dir / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = wm_dir / "transcript.jsonl"
    record_path = wm_dir / "record.json"

    prompt_text = _wrap_prompt(_prompt_path(wm).read_text(), arm.prompt_wrapper)

    attempts_log: list[str] = []
    outcome = "failed"
    lines: list[str] = []
    first_edit_elapsed = 0.0
    attempt_count = 0
    max_attempts = retries + 1

    for attempt_idx in range(max_attempts):
        attempt_count = attempt_idx + 1
        argv = build_argv(prompt_text, agent_cmd)
        outcome, lines, first_edit_elapsed = _invoke_once(argv, timeout_s=timeout_s, log_path=transcript_path)
        attempts_log.append(f"attempt {attempt_count}: {outcome}")
        if outcome in ("done", "timeout"):
            break  # timeout is terminal, never retried; done needs no retry

    if outcome == "timeout":
        record = validate(
            {
                "arm": arm.name,
                "wm": wm,
                "rep": 0,
                "status": "timeout",
                "metrics": _zero_metrics(),
                "artifacts": {
                    "workspace": str(workspace_dir),
                    "transcript": str(transcript_path),
                    "oracle_report": "",
                    "attempts": "; ".join(attempts_log),
                },
            }
        )
        write_record_atomic(record_path, record)
        return record

    if outcome == "failed":
        record = validate(
            {
                "arm": arm.name,
                "wm": wm,
                "rep": 0,
                "status": "failed",
                "metrics": _zero_metrics(),
                "artifacts": {
                    "workspace": str(workspace_dir),
                    "transcript": str(transcript_path),
                    "oracle_report": "",
                    "attempts": "; ".join(attempts_log),
                },
            }
        )
        write_record_atomic(record_path, record)
        return record

    # outcome == "done": parse tokens/cost, run the post-agent app check,
    # then the isolation check, before finalizing the record.
    tokens_total, cost_usd, unparseable = _parse_tokens_and_cost(lines)
    app_check = _post_agent_app_check(workspace_dir)
    isolation_clean, leak_paths = _isolation_check(workspace_dir)

    oracle_report_path = wm_dir / "oracle_report.json"
    oracle_report_path.write_text(
        json.dumps({"app_check": app_check, "isolation_clean": isolation_clean, "leaks": leak_paths})
    )

    artifacts: dict[str, str] = {
        "workspace": str(workspace_dir),
        "transcript": str(transcript_path),
        "oracle_report": str(oracle_report_path),
        "attempts": "; ".join(attempts_log),
    }
    if unparseable:
        artifacts["token_source"] = "unparseable"
    if arm.name == "add":
        artifacts["resolved_pin"] = resolve_pin(arm.pin, arm.name)
    if not isolation_clean:
        artifacts["leak_path"] = "; ".join(leak_paths)

    status = "done" if isolation_clean else "failed"

    record = validate(
        {
            "arm": arm.name,
            "wm": wm,
            "rep": 0,
            "status": status,
            "metrics": {
                "regression_rate": 0.0,
                "spec_fidelity": 0.0,
                "tokens_total": float(tokens_total),
                "cost_usd": cost_usd,
                "context_rot_slope": 0.0,
                "time_to_first_edit": first_edit_elapsed,
            },
            "artifacts": artifacts,
        }
    )
    write_record_atomic(record_path, record)
    return record


def _zero_metrics() -> dict[str, float]:
    return {
        "regression_rate": 0.0,
        "spec_fidelity": 0.0,
        "tokens_total": 0.0,
        "cost_usd": 0.0,
        "context_rot_slope": 0.0,
        "time_to_first_edit": 0.0,
    }
