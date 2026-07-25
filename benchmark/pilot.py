"""pilot — sequences the full 5-arm x 3-WM live pilot, provisioning +
run + score, honoring resume (bench-pilot-report TASK.md §3 CONTRACT @ v1).

The human-in-the-loop `attest_record` spot-check writer for the LLM
`spec_fidelity` was RETIRED at honest-fidelity-meter: fidelity is now the
deterministic `requirement_coverage` (probes against the built app), so
there is no subjective per-record score left to audit.

Reuses `execute_wm`/`score_record`/`find_resume_point`/`write_record_atomic`
verbatim (imported, not reimplemented) — this module is pure orchestration
composed of already-frozen, already-tested building blocks. Stdlib-first,
fail-loud: every Reject case raises BenchError("<code>: ...") before any
disk write.
"""
from __future__ import annotations

import argparse
import dataclasses
import pathlib
import sys
from typing import Sequence

from benchmark.arms.loader import ARM_NAMES, Arm, load_arm
from benchmark.runner.core import execute_wm
from benchmark.runner.records import DEFAULT_RUNS_ROOT, find_resume_point, write_record_atomic
from benchmark.schema.run_record import BenchError, RunRecord
from benchmark.score import score_record
from benchmark.tamper import snapshot_tests

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ARMS_DIR = pathlib.Path(__file__).resolve().parent / "arms"
REPO_ROOT_TOKEN = "{REPO_ROOT}"
VALID_WMS = (1, 2, 3, 4, 5, 6)


def resolve_setup_steps(arm: Arm, repo_root: pathlib.Path) -> Arm:
    """Replace every literal "{REPO_ROOT}" token in `arm.setup_steps` with
    `str(repo_root)`, returning a NEW Arm (dataclasses.replace) — the
    original loaded Arm is never mutated. Identity passthrough (by value)
    for an arm with no token in any step (M5).

    Raises BenchError("invalid_repo_root: ...") if `repo_root` does not
    exist on disk (R7) — a silently-wrong path would otherwise surface as a
    confusing downstream setup_steps failure instead of a clear one.
    """
    repo_root = pathlib.Path(repo_root)
    if not repo_root.exists():
        raise BenchError(f"invalid_repo_root: {repo_root} does not exist")

    resolved_steps = [line.replace(REPO_ROOT_TOKEN, str(repo_root)) for line in arm.setup_steps]
    return dataclasses.replace(arm, setup_steps=resolved_steps)


def run_pilot(
    arms: Sequence[str] = ARM_NAMES,
    wms: Sequence[int] = (1, 2, 3, 4, 5, 6),
    *,
    resume: bool = True,
    agent_cmd: Sequence[str] | None = None,
    judge_cmd: Sequence[str] | None = None,
    timeout_s: float = 1800.0,
    retries: int = 1,
    runs_root: pathlib.Path | None = None,
    repo_root: pathlib.Path | None = None,
    family: str = "wm",
    session_mode: str = "fresh",
) -> list[RunRecord]:
    """Sequences, PER ARM independently: resolve the arm (load_arm +
    resolve_setup_steps) -> determine the starting WM (find_resume_point
    when resume and prior records exist, else wms[0]) -> for each WM in
    order call execute_wm and, only if that WM's resulting status=="done",
    call score_record before continuing -- else HALT this arm's remaining
    WM sequence (M7, M8). Arms never share state: a halt on one arm never
    blocks the next arm's own independent sequence (M9's own-arm resume
    semantics; per-arm all-or-nothing-forward is this task's safety rule).

    Raises BenchError("unknown_arm: ...") per-arm BEFORE any workspace is
    touched for that arm (R6) -- checked for every requested arm up front,
    so a bad arm never causes partial work on an earlier arm to be lost,
    but does not itself abort work already committed to other arms.
    """
    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT
    repo_root_path = pathlib.Path(repo_root) if repo_root is not None else REPO_ROOT

    for arm_name in arms:
        if arm_name not in ARM_NAMES:
            raise BenchError(f"unknown_arm: {arm_name!r} not in {ARM_NAMES}")

    records: list[RunRecord] = []

    for arm_name in arms:
        arm = load_arm(ARMS_DIR / f"{arm_name}.toml")
        resolved_arm = resolve_setup_steps(arm, repo_root_path)

        if resume:
            resume_point = find_resume_point(arm_name, runs_root=root)
            start_wm = resume_point if resume_point is not None else wms[0]
        else:
            start_wm = wms[0]

        sequence = [wm for wm in wms if wm >= start_wm]

        for wm in sequence:
            record = execute_wm(
                resolved_arm,
                wm,
                agent_cmd=agent_cmd,
                timeout_s=timeout_s,
                retries=retries,
                runs_root=root,
                family=family,
                session_mode=session_mode,
            )
            records.append(record)
            if record.status != "done":
                break  # halt this arm's remaining WMs (M8); continue to next arm
            # v2-meter-fixes M8: snapshot the workspace's test files BEFORE
            # scoring, so score_record can compute tests_weakened at wm>=2
            # with no manual step. Failed/timeout WMs never reach here.
            snapshot_tests(pathlib.Path(record.artifacts["workspace"]), root / arm_name, wm, family)
            scored = score_record(arm_name, wm, judge_cmd=judge_cmd, runs_root=root, family=family)
            records[-1] = scored

    return records


# --------------------------------------------------------------------------
# harness-multirep — controlled N-rep runs + distribution aggregation
# --------------------------------------------------------------------------

_REP_METRICS = (
    ("tokens", "tokens_total"),
    ("cost", "cost_usd"),
    ("fidelity", "requirement_coverage"),
    # v2-wv1-longitudinal M2: the v2 trust metrics. regression_rate is a
    # required key; oracle_pass_rate/tests_weakened are OPTIONAL (schema v2) —
    # aggregation tolerates records that don't carry them (n_missing below).
    ("pass_rate", "oracle_pass_rate"),
    ("regression", "regression_rate"),
    ("weakened", "tests_weakened"),
)


def aggregate_reps(records: Sequence[RunRecord]) -> dict:
    """PURE — group `records` by (arm, wm) and, per group, return `n` plus
    {mean, min, max} for every _REP_METRICS entry. No IO. Empty input -> {}.
    The full distribution (not just the mean) is reported so single-rep
    variance can't hide behind a central-tendency number.

    OPTIONAL v2 keys (schema v2) aggregate over the records CARRYING them;
    absent carriers are disclosed as "n_missing": <count> inside that
    metric's entry (only when > 0). A metric with ZERO carriers reports
    {"n_missing": n} alone — never a fabricated 0.0 mean (R1)."""
    groups: dict[tuple[str, int], list[RunRecord]] = {}
    for record in records:
        groups.setdefault((record.arm, record.wm), []).append(record)

    summary: dict[tuple[str, int], dict] = {}
    for key, recs in groups.items():
        entry: dict = {"n": len(recs)}
        for label, metric in _REP_METRICS:
            values = [float(r.metrics[metric]) for r in recs if metric in r.metrics]
            missing = len(recs) - len(values)
            if not values:
                entry[label] = {"n_missing": missing}
                continue
            stats: dict = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }
            if missing:
                stats["n_missing"] = missing
            entry[label] = stats
        summary[key] = entry
    return summary


def run_reps(
    arms: Sequence[str] = ARM_NAMES,
    wms: Sequence[int] = (1, 2, 3, 4, 5, 6),
    reps: int = 1,
    *,
    runs_root: pathlib.Path | None = None,
    repo_root: pathlib.Path | None = None,
    agent_cmd: Sequence[str] | None = None,
    judge_cmd: Sequence[str] | None = None,
    timeout_s: float = 1800.0,
    retries: int = 1,
    family: str = "wm",
    session_mode: str = "fresh",
) -> list[RunRecord]:
    """Run the full arms×wms pilot `reps` times into DISTINCT `runs_root/rep{i}`
    roots (resume disabled per rep so each is an independent fresh sample), and
    return the flat concatenation of every rep's records. Fail-loud: reps<1 is
    rejected before any run starts."""
    if reps < 1:
        raise BenchError("invalid_reps: must be >= 1")

    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT

    records: list[RunRecord] = []
    for i in range(reps):
        rep_records = run_pilot(
            arms,
            wms,
            resume=False,
            agent_cmd=agent_cmd,
            judge_cmd=judge_cmd,
            timeout_s=timeout_s,
            retries=retries,
            runs_root=root / f"rep{i}",
            repo_root=repo_root,
            family=family,
            session_mode=session_mode,
        )
        records.extend(rep_records)
    return records


# --------------------------------------------------------------------------
# thin argparse CLI: `pilot.py run-all`
# --------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pilot.py")
    sub = parser.add_subparsers(dest="command", required=True)

    run_all_p = sub.add_parser("run-all")
    run_all_p.add_argument("--arms", nargs="*", default=list(ARM_NAMES))
    run_all_p.add_argument("--wms", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    run_all_p.add_argument("--resume", type=lambda s: s.lower() != "false", default=True)
    run_all_p.add_argument("--agent-cmd", nargs="*", default=None)
    run_all_p.add_argument("--judge-cmd", nargs="*", default=None)
    run_all_p.add_argument("--timeout-s", type=float, default=1800.0)
    run_all_p.add_argument("--retries", type=int, default=1)
    run_all_p.add_argument("--reps", type=int, default=1)
    run_all_p.add_argument("--runs-root", default=None)
    run_all_p.add_argument("--repo-root", default=None)
    run_all_p.add_argument("--family", default="wm", choices=("wm", "hv", "amb"))
    run_all_p.add_argument("--session-mode", default="fresh", choices=("fresh", "continue"),
                           dest="session_mode",
                           help="continue = ONE persistent workspace + ONE continuing "
                                "conversation across WMs (context-rot-cross-milestones); "
                                "fresh = classic per-WM shape (default)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-all":
        runs_root = pathlib.Path(args.runs_root) if args.runs_root else None
        repo_root = pathlib.Path(args.repo_root) if args.repo_root else None
        try:
            if args.reps > 1:
                records = run_reps(
                    arms=args.arms,
                    wms=tuple(args.wms),
                    reps=args.reps,
                    agent_cmd=args.agent_cmd,
                    judge_cmd=args.judge_cmd,
                    timeout_s=args.timeout_s,
                    retries=args.retries,
                    runs_root=runs_root,
                    repo_root=repo_root,
                    family=args.family,
                    session_mode=args.session_mode,
                )
                for (arm, wm), stats in sorted(aggregate_reps(records).items()):
                    print(
                        f"{arm} wm{wm}  n={stats['n']}  "
                        f"tokens[mean={stats['tokens']['mean']:.0f} "
                        f"min={stats['tokens']['min']:.0f} max={stats['tokens']['max']:.0f}]  "
                        f"cost[mean={stats['cost']['mean']:.4f} "
                        f"min={stats['cost']['min']:.4f} max={stats['cost']['max']:.4f}]  "
                        f"fidelity[mean={stats['fidelity']['mean']:.3f} "
                        f"min={stats['fidelity']['min']:.3f} max={stats['fidelity']['max']:.3f}]"
                    )
                return 0
            records = run_pilot(
                arms=args.arms,
                wms=tuple(args.wms),
                resume=args.resume,
                agent_cmd=args.agent_cmd,
                judge_cmd=args.judge_cmd,
                timeout_s=args.timeout_s,
                retries=args.retries,
                runs_root=runs_root,
                repo_root=repo_root,
                family=args.family,
                session_mode=args.session_mode,
            )
        except BenchError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        for record in records:
            print(record.to_json())
        return 0

    parser.error("unknown command")
    return 2  # pragma: no cover


if __name__ == "__main__":
    raise SystemExit(main())
