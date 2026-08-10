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
import shlex
import signal
import shutil
import subprocess
import threading
import time
from typing import Sequence

from benchmark.arms.loader import Arm
from benchmark.check_isolation import find_leaks
from benchmark.check_isolation import main as check_isolation_main
from benchmark.runner.agent import PINNED_MODEL, build_argv
from benchmark.runner.pin import resolve_pin
from benchmark.runner.records import DEFAULT_RUNS_ROOT, write_record_atomic
from benchmark.schema.run_record import RunRecord, validate
from benchmark.workload._oracle_lib import http_call, running_app

BENCHMARK_ROOT = pathlib.Path(__file__).resolve().parents[1]

_EDIT_TOOL_NAMES = frozenset({"Edit", "Write"})


def _prompt_path(wm: int, family: str = "wm") -> pathlib.Path:
    """Workload family seam (wv2-family): `family` names the workload track
    (wm = longitudinal, hv = hostile-change); indexes are family-local."""
    return BENCHMARK_ROOT / "workload" / f"{family}{wm}" / "PROMPT.md"


def _wrap_prompt(text: str, wrapper: str) -> str:
    if wrapper == "plan-then-execute":
        return f"Plan first, then execute:\n\n{text}"
    if wrapper == "add-loop":
        # ABF-1 / ADD 3.0 surface. The engine CLI is `cli.py`; `add.py` is a library module with no
        # `__main__`, so invoking it prints nothing and exits 0 — an arm pointed at it orients into
        # a void and never learns it asked the wrong question. `tests/test_adherence_census.py`
        # sweeps this string against `cli.build_parser()` so a retired verb cannot survive here.
        return (
            "Drive this repo's ADD loop for the whole job (see CLAUDE.md): run "
            "`python3 .add/tooling/cli.py status` FIRST and follow its next-step through the "
            "beats; write NO app code before the task's contract is FROZEN and its red suite "
            "exists; record the verify gate before finishing. This is a headless run with no "
            "human available: you carry the human's proxy authority — approve contract "
            "freezes and gates yourself (record them as usual) and NEVER end the run waiting "
            "for a human reply; the job is done only when the app meets the requirements. "
            "This is a CLEARED, fully-specified benchmark task, so take the one-pass walk: create "
            "each task with `python3 .add/tooling/cli.py new Task <slug> --title \"...\" "
            "--scope <files>`, then author its whole Direction bundle in ONE pass — `## RULES` "
            "(Musts and Rejects), `## PLAN`, and `## CHECKS` with a `covers:` key on every line "
            "naming the rule it proves. Freeze refuses a node that still carries template "
            "placeholders, so replace them all first, then approve with "
            "`python3 .add/tooling/cli.py freeze <slug> --by <you> --authority human`. Build to "
            "green, then record evidence with `python3 .add/tooling/cli.py run <slug> "
            "--junitxml r.xml -- <test cmd> --junitxml=r.xml` — the test command must write that "
            "file itself, since the gate binds each `covers:` rule to a PASSING test id in it and "
            "refuses a PASS for any rule left unproven. Close with "
            "`python3 .add/tooling/cli.py gate <slug> PASS --by <you>`. The floor never bends: the "
            "contract is FROZEN and the red suite precedes the build (never skip contract, tests, "
            "build, or verify). "
            "Finish the run once the app meets the requirements and the verify gate is recorded "
            "— do NOT run milestone-done, fold (ledger work), or milestone-archive: that "
            "milestone-ledger close-out is project bookkeeping, not part of delivering this "
            "feature, and is out of scope for the benchmark.\n\n"
            + text
        )
    return text  # "raw" (and any unrecognized wrapper) passes through verbatim


# What the agent sees on resume. Deliberately bare: naming a file, a tool, or a
# method would hand one arm its own idiom back and tell the others where to look
# — the whole question is what each method left behind that survives a lost
# conversation, so the prompt must not supply the answer.
RESUME_PROMPT = (
    "Continue the work in this workspace. A previous session was interrupted "
    "before it finished. Determine what remains and complete it."
)


def _invoke_interruptible(
    argv: list[str], *, cwd: pathlib.Path, timeout_s: float, log_path: pathlib.Path,
    interrupt: dict,
) -> tuple[str, list[str], dict]:
    """Run one attempt that a watcher may KILL mid-flight. Returns
    (outcome, stdout_lines, interrupt_result).

    Why this exists as a separate path rather than a flag on `_invoke_once`:
    that function drains stdout with `communicate()` and writes the transcript
    only AFTER the process exits, so there is nothing on disk for a watcher to
    poll until it is far too late to interrupt anything. Interruption needs the
    transcript to exist WHILE the agent works.

    Streaming only here — never on the default path — is deliberate: it makes
    "an uninterrupted run behaves exactly as before" true by construction rather
    than by careful review of a shared code path.
    """
    from benchmark.interrupt import watch_and_kill

    proc = subprocess.Popen(
        argv,
        cwd=str(cwd),
        env={**os.environ, "ADD_ROOT_CEILING": str(cwd)},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    lines: list[str] = []
    result: dict = {}

    def _watch() -> None:
        result.update(watch_and_kill(
            proc, log_path, k=int(interrupt["k"]),
            backstop_s=float(interrupt.get("backstop_s", timeout_s / 2)),
            poll_s=float(interrupt.get("poll_s", 0.5))))

    watcher = threading.Thread(target=_watch, daemon=True)
    watcher.start()
    with log_path.open("a", buffering=1) as fh:
        for line in proc.stdout or []:            # stream: the watcher reads this
            lines.append(line.rstrip("\n"))
            fh.write(line if line.endswith("\n") else line + "\n")
    proc.wait()
    watcher.join(timeout=10)
    if proc.poll() is None:
        _kill_process_group(proc)
    outcome = "interrupted" if result.get("fired") in ("kth_write", "backstop") else (
        "done" if proc.returncode == 0 else "failed")
    return outcome, lines, (result or {"fired": "none", "writes_seen": 0,
                                       "elapsed_s": 0.0})


def _invoke_once(
    argv: list[str], *, cwd: pathlib.Path, timeout_s: float, log_path: pathlib.Path
) -> tuple[str, list[str], float]:
    """Run one attempt. Returns (outcome, stdout_lines, first_edit_elapsed_s).

    outcome is "done" (exit 0), "failed" (nonzero exit), or "timeout".
    Kills the whole process group on timeout so no zombie survives.
    """
    start = time.monotonic()
    proc = subprocess.Popen(
        argv,
        cwd=str(cwd),  # the agent starts inside its sandbox, never the pilot's cwd
        # Scope the engine's root-walk to the workspace (harness-workspace-isolation):
        # a run dir nested under the repo's own .add/ would otherwise resolve the
        # PARENT project on the agent's first pre-init `status`, inflating startup.
        env={**os.environ, "ADD_ROOT_CEILING": str(cwd)},
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


def _run_setup_steps(
    setup_steps: list[str], *, cwd: pathlib.Path, log_path: pathlib.Path
) -> tuple[bool, list[str]]:
    """Run an arm's `setup_steps` lines, in order, before agent invocation.

    Per line: strip an inline `#` comment, `shlex.split()` the remainder, run
    as list-form argv (no `shell=True`) with cwd=the sandboxed workspace. A
    nonzero step fails loudly — recorded, not swallowed — and stops the
    remaining steps. Empty `setup_steps` is a no-op.
    """
    log_lines: list[str] = []
    for raw_line in setup_steps:
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        argv = shlex.split(line)
        if not argv:
            continue
        try:
            proc = subprocess.run(
                argv,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except OSError as exc:  # unlaunchable command: fail the attempt, never the pilot
            entry = f"setup: {argv} -> unlaunchable: {type(exc).__name__}: {exc}"
            log_lines.append(entry)
            with log_path.open("a") as fh:
                fh.write(entry + "\n")
            return False, log_lines
        entry = f"setup: {argv} -> exit {proc.returncode}"
        log_lines.append(entry)
        with log_path.open("a") as fh:
            fh.write(entry + "\n")
            if proc.stdout:
                fh.write(proc.stdout)
                if not proc.stdout.endswith("\n"):
                    fh.write("\n")
        if proc.returncode != 0:
            return False, log_lines
    return True, log_lines


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


def _seed_from_prior(
    workspace_dir: pathlib.Path, arm_name: str, wm: int, runs_root: pathlib.Path,
    family: str = "wm",
) -> str | None:
    """Carry the prior WM's completed workspace forward (bench-carry-forward).

    WM2/WM3 prompts assume the prior milestone's app exists. Seeds ONLY a fresh
    (empty) workspace for wm>1 — a populated workspace (resume/retry) is never
    overwritten; `.venv` is excluded (setup recreates it per WM).
    Returns a one-line note for the attempts log, or None when not applicable.
    """
    if wm <= 1 or any(workspace_dir.iterdir()):
        return None
    prior = runs_root / arm_name / f"{family}{wm - 1}" / "workspace"
    if not prior.is_dir():
        return f"unseeded: no prior workspace at {family}{wm - 1}"
    shutil.copytree(prior, workspace_dir, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".venv"))
    return f"seeded from {family}{wm - 1}"


def execute_wm(
    arm: Arm,
    wm: int,
    *,
    agent_cmd: Sequence[str] | None = None,
    timeout_s: float = 1800.0,
    retries: int = 1,
    runs_root: pathlib.Path | None = None,
    family: str = "wm",
    session_mode: str = "fresh",
    interrupt: dict | None = None,
) -> RunRecord:
    """Drive one arm x WM end-to-end and write exactly one RunRecord.

    session_mode: "fresh" (default) is the classic per-WM shape — new
    workspace seeded by copy, new conversation. "continue" persists the
    PROJECT, never the conversation: ONE workspace
    (runs/<arm>/session/workspace, never copy-seeded), setup at WM1 only,
    and a FRESH conversation every milestone (`--continue` removed
    2026-07-18 by user decision) — the on-disk board is the only carrier
    across milestones, exactly the resume-anytime shape the methods claim
    to support. Per-WM records still land at
    runs/<arm>/<family><wm>/record.json."""
    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT
    wm_dir = root / arm.name / f"{family}{wm}"
    continuing = session_mode == "continue"
    if continuing:
        workspace_dir = root / arm.name / "session" / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)
        seed_note = "session-mode: persistent workspace (no copy-seed)"
        wm_dir.mkdir(parents=True, exist_ok=True)
    else:
        workspace_dir = wm_dir / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)
        seed_note = _seed_from_prior(workspace_dir, arm.name, wm, root, family)
    transcript_path = wm_dir / "transcript.jsonl"
    record_path = wm_dir / "record.json"

    # One execute_wm call is one run, so the transcript starts empty. Every write
    # site below opens "a" — deliberately, since setup steps and each retry
    # attempt all accumulate into the SAME run's transcript — which means a
    # re-run at an already-used path would otherwise inherit its predecessor.
    # Live proof 2026-08-10: a stand-in agent making 8 engine calls scored
    # engine_calls 122, the other 114 belonging to a July campaign sitting at
    # the default path. Truncate here, before setup, and exactly once.
    transcript_path.write_text("")

    prompt_text = _wrap_prompt(_prompt_path(wm, family).read_text(), arm.prompt_wrapper)

    attempts_log: list[str] = []
    if seed_note:
        attempts_log.append(seed_note)

    if continuing and wm > 1:
        setup_ok, setup_log = True, ["setup skipped: session-mode continues the WM1 board"]
    else:
        setup_ok, setup_log = _run_setup_steps(arm.setup_steps, cwd=workspace_dir, log_path=transcript_path)
    attempts_log.extend(setup_log)
    if not setup_ok:
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
                    "model": PINNED_MODEL,
                },
            }
        )
        write_record_atomic(record_path, record)
        return record

    outcome = "failed"
    lines: list[str] = []
    first_edit_elapsed = 0.0
    attempt_count = 0
    max_attempts = retries + 1
    interrupt_result: dict | None = None

    if interrupt is not None:
        # The interrupt-resume shape: ONE interrupted attempt, then ONE resume.
        # The resume is a FRESH invocation on the SAME workspace — a new
        # conversation with no prior context, so the on-disk state is the only
        # carrier. Anything else would measure the agent's memory rather than
        # what the method left behind for it to pick up (R:context_carryover).
        argv = build_argv(prompt_text, agent_cmd)
        outcome, lines, interrupt_result = _invoke_interruptible(
            argv, cwd=workspace_dir, timeout_s=timeout_s,
            log_path=transcript_path, interrupt=interrupt)
        attempts_log.append(
            f"interrupted: {interrupt_result.get('fired')} after "
            f"{interrupt_result.get('writes_seen')} writes")
        if interrupt_result.get("fired") in ("kth_write", "backstop"):
            resume_text = _wrap_prompt(
                interrupt.get("resume_prompt", RESUME_PROMPT), arm.prompt_wrapper)
            outcome, lines, first_edit_elapsed = _invoke_once(
                build_argv(resume_text, agent_cmd), cwd=workspace_dir,
                timeout_s=timeout_s, log_path=transcript_path)
            attempts_log.append(f"resume: {outcome}")
        else:
            first_edit_elapsed = 0.0
        max_attempts = 0   # the interrupt path owns its own attempt structure

    for attempt_idx in range(max_attempts):
        attempt_count = attempt_idx + 1
        argv = build_argv(prompt_text, agent_cmd)
        outcome, lines, first_edit_elapsed = _invoke_once(
            argv, cwd=workspace_dir, timeout_s=timeout_s, log_path=transcript_path
        )
        attempts_log.append(f"attempt {attempt_count}: {outcome}")
        if outcome == "done":
            break  # a timeout or a failed attempt each consume a retry;
            # only "done" is terminal early — a timeout is retried like any
            # other transient failure, and only the LAST attempt's outcome
            # (timeout or failed) becomes the final status once retries are
            # exhausted, per §1's frozen "after exhausting retries" wording.

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
                    "model": PINNED_MODEL,
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
                    "model": PINNED_MODEL,
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
    if continuing:
        artifacts["session_mode"] = "continue"
    if interrupt_result is not None:
        # M5: the kill point that ACTUALLY fired, not the one we intended. A
        # published recovery number is only auditable if a reader can see where
        # each arm was cut — and whether the cut landed at a comparable place.
        artifacts["interrupt"] = json.dumps(
            {"k": int(interrupt["k"]), **interrupt_result}, separators=(",", ":"))
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
                "requirement_coverage": 0.0,  # placeholder; score_record computes the real value
                "oracle_pass_rate": 0.0,      # placeholder; score_record computes the real value
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
        "requirement_coverage": 0.0,
        "oracle_pass_rate": 0.0,
        "tokens_total": 0.0,
        "cost_usd": 0.0,
        "context_rot_slope": 0.0,
        "time_to_first_edit": 0.0,
    }
