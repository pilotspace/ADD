"""pilot — sequences the full 5-arm x 3-WM live pilot, provisioning +
run + score, honoring resume; and `attest_record`, the human-in-the-loop
spot-check writer for spec_fidelity (bench-pilot-report TASK.md §3
CONTRACT @ v1).

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
from benchmark.schema.run_record import BenchError, RunRecord, validate
from benchmark.score import score_record

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


def _record_path(runs_root: pathlib.Path, arm_name: str, wm: int) -> pathlib.Path:
    return runs_root / arm_name / f"wm{wm}" / "record.json"


def attest_record(
    arm_name: str, wm: int, note: str, *, runs_root: pathlib.Path | None = None
) -> RunRecord:
    """Human-in-the-loop spot-check writer: reads record.json, raises
    BenchError("record_not_found"/"record_not_done"/"record_not_scored")
    per the Reject list, else writes
    artifacts["spec_fidelity_audit"] = "spot-checked: <note>" via
    write_record_atomic (reused verbatim) and returns the updated RunRecord.

    Mirrors score_record's exact guard-clause-before-any-I/O shape: read the
    full record, validate eligibility, mutate only the one field in an
    in-memory copy, re-validate the complete dict, write once.
    """
    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT
    record_path = _record_path(root, arm_name, wm)
    if not record_path.exists():
        raise BenchError(f"record_not_found: {record_path}")

    record = RunRecord.from_json(record_path.read_text())
    if record.status != "done":
        raise BenchError(f"record_not_done: status={record.status!r} (nothing to attest)")

    if record.metrics.get("spec_fidelity") == 0.0:
        raise BenchError("record_not_scored: metrics['spec_fidelity'] is still the unscored 0.0 placeholder")

    artifacts = dict(record.artifacts)
    artifacts["spec_fidelity_audit"] = f"spot-checked: {note}"

    updated = validate(
        {
            "arm": record.arm,
            "wm": record.wm,
            "rep": record.rep,
            "status": record.status,
            "metrics": dict(record.metrics),
            "artifacts": artifacts,
        }
    )
    write_record_atomic(record_path, updated)
    return updated


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
            )
            records.append(record)
            if record.status != "done":
                break  # halt this arm's remaining WMs (M8); continue to next arm
            scored = score_record(arm_name, wm, judge_cmd=judge_cmd, runs_root=root)
            records[-1] = scored

    return records


# --------------------------------------------------------------------------
# thin argparse CLI: `pilot.py run-all` / `pilot.py attest`
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
    run_all_p.add_argument("--runs-root", default=None)
    run_all_p.add_argument("--repo-root", default=None)

    attest_p = sub.add_parser("attest")
    attest_p.add_argument("--arm", required=True)
    attest_p.add_argument("--wm", type=int, required=True)
    attest_p.add_argument("--note", required=True)
    attest_p.add_argument("--runs-root", default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-all":
        runs_root = pathlib.Path(args.runs_root) if args.runs_root else None
        repo_root = pathlib.Path(args.repo_root) if args.repo_root else None
        try:
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
            )
        except BenchError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        for record in records:
            print(record.to_json())
        return 0

    if args.command == "attest":
        runs_root = pathlib.Path(args.runs_root) if args.runs_root else None
        try:
            record = attest_record(args.arm, args.wm, args.note, runs_root=runs_root)
        except BenchError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(record.to_json())
        return 0

    parser.error("unknown command")
    return 2  # pragma: no cover


if __name__ == "__main__":
    raise SystemExit(main())
