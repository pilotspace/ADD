"""The injectable judge-command seam (bench-scoring TASK.md §3 CONTRACT @ v1).

Mirrors `benchmark/runner/agent.py`'s injectable-argv seam exactly: a real
`spec_fidelity` score requires a live `claude -p <rubric>` rubric call; tests
inject a fake stdlib judge script via `judge_cmd` so the suite never spawns
the live `claude` binary. Stdlib only, fail-loud: BenchError("unparseable_judge_output: ...")
on anything the subprocess can't turn into a float in [0.0, 1.0].
"""
from __future__ import annotations

import pathlib
import statistics
import subprocess
from typing import Sequence

from benchmark.schema.run_record import BenchError

BENCHMARK_ROOT = pathlib.Path(__file__).resolve().parent
JUDGE_TIMEOUT_S = 120.0


def default_judge_cmd(rubric_prompt: str) -> list[str]:
    """The real `claude -p <rubric>` rubric-scoring invocation — model PINNED
    (v2-meter-fixes M5, closes todo #28-judge): an unpinned judge made v1
    fidelity numbers noise across model generations. The judge is a SECONDARY
    annotator in v2; oracle_pass_rate is the fidelity of record."""
    return ["claude", "-p", rubric_prompt, "--model", "claude-sonnet-5"]


def build_judge_argv(rubric_prompt: str, judge_cmd: Sequence[str] | None) -> list[str]:
    """Resolve the actual argv: an injected fake-judge argv gets the rubric
    prompt appended as its final positional arg; absent an injection, fall
    back to the real `claude -p` argv."""
    if judge_cmd:
        return [*judge_cmd, rubric_prompt]
    return default_judge_cmd(rubric_prompt)


def _prompt_path(wm: int) -> pathlib.Path:
    return BENCHMARK_ROOT / "workload" / f"wm{wm}" / "PROMPT.md"


def build_rubric_prompt(wm: int, oracle_report: dict) -> str:
    """Grounding text for the rubric judge: the WM's PROMPT.md requirements
    plus the oracle_report.json's app_check/isolation_clean signal (already
    computed by the runner — no second oracle subprocess run here)."""
    prompt_text = _prompt_path(wm).read_text()
    app_check = oracle_report.get("app_check", "unavailable")
    isolation_clean = oracle_report.get("isolation_clean", "unavailable")
    return (
        f"Rate spec fidelity in [0.0, 1.0] for workload milestone {wm}.\n\n"
        f"Requirements (PROMPT.md):\n{prompt_text}\n\n"
        f"Oracle app_check: {app_check!r}\n"
        f"Oracle isolation_clean: {isolation_clean!r}\n\n"
        "Respond with a single float in [0.0, 1.0] and nothing else."
    )


def judge_fidelity(
    workspace: pathlib.Path,
    wm: int,
    oracle_report: dict,
    *,
    judge_cmd: Sequence[str] | None = None,
) -> float:
    """Run the judge command's argv; parse stdout as a float in [0.0, 1.0].

    Raises BenchError("unparseable_judge_output: ...") on anything else —
    a non-numeric stdout, an out-of-range value, or the subprocess itself
    failing to launch. Never coerces a bad result to a silent default.
    """
    rubric_prompt = build_rubric_prompt(wm, oracle_report)
    argv = build_judge_argv(rubric_prompt, judge_cmd)
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=JUDGE_TIMEOUT_S,
            cwd=str(workspace) if pathlib.Path(workspace).exists() else None,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise BenchError(f"unparseable_judge_output: judge invocation failed: {exc}") from exc

    stdout = (proc.stdout or "").strip()
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    if not lines:
        raise BenchError(f"unparseable_judge_output: empty judge stdout (stderr={proc.stderr!r})")

    try:
        value = float(lines[-1].strip())
    except ValueError as exc:
        raise BenchError(f"unparseable_judge_output: not a float: {lines[-1]!r}") from exc

    if value != value or not (0.0 <= value <= 1.0):  # value != value catches NaN
        raise BenchError(f"unparseable_judge_output: value out of range [0.0, 1.0]: {value!r}")

    return value


def judge_fidelity_median(
    workspace: pathlib.Path,
    wm: int,
    oracle_report: dict,
    *,
    judge_cmd: Sequence[str] | None = None,
    n: int = 3,
) -> tuple[float, list[float]]:
    """Run judge_fidelity up to `n` times and return (median, scores).

    Single-call judging showed a +-0.05-0.10 spread on identical inputs in
    the round-3 pilot sweep — larger than any arm-vs-arm fidelity gap.
    Individual call failures are tolerated; fewer than 2 successes raises,
    since a lone value is exactly the noise this function exists to damp.
    """
    scores: list[float] = []
    last_err: BenchError | None = None
    for _ in range(n):
        try:
            scores.append(judge_fidelity(workspace, wm, oracle_report, judge_cmd=judge_cmd))
        except BenchError as exc:
            last_err = exc
    if len(scores) < 2:
        raise BenchError(
            f"unparseable_judge_output: only {len(scores)}/{n} judge calls succeeded; last: {last_err}"
        )
    return statistics.median(scores), scores
