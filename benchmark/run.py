#!/usr/bin/env python3
"""run.py — thin CLI over benchmark/runner/ (bench-runner TASK.md §3 CONTRACT).

  run.py run --arm <name> --wm <1|2|3> [--timeout-s S] [--retries N] [--agent-cmd ARGV...]
  run.py resume --arm <name> [--timeout-s S] [--retries N] [--agent-cmd ARGV...]
  run.py score --arm <name> --wm <1|2|3> [--judge-cmd ARGV...]

exit 0 on success; exit 2 with one of the frozen codes on rejection
(unknown_arm | invalid_arm_recipe | invalid_wm | nothing_to_resume |
record_not_found | record_not_done | missing_prior_wm_record |
unparseable_judge_output | regression_run_failed) — no workspace/record
created or modified for any exit-2 path (bench-scoring TASK.md §3 CONTRACT).
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from benchmark.arms.loader import ARM_NAMES, load_arm
from benchmark.report import render_report
from benchmark.runner.core import execute_wm
from benchmark.runner.records import find_resume_point
from benchmark.schema.run_record import BenchError
from benchmark.score import score_record

ARMS_DIR = pathlib.Path(__file__).resolve().parent / "arms"
VALID_WMS = (1, 2, 3, 4, 5)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="run.py")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--arm", required=True)
    common.add_argument("--timeout-s", type=float, default=1800.0)
    common.add_argument("--retries", type=int, default=1)
    common.add_argument("--agent-cmd", nargs="*", default=None)

    run_p = sub.add_parser("run", parents=[common])
    run_p.add_argument("--wm", type=int, required=True)

    sub.add_parser("resume", parents=[common])

    score_p = sub.add_parser("score")
    score_p.add_argument("--arm", required=True)
    score_p.add_argument("--wm", type=int, required=True)
    score_p.add_argument("--judge-cmd", nargs="*", default=None)

    report_p = sub.add_parser("report")
    report_p.add_argument("--arm", default=None)
    report_p.add_argument("--wm", type=int, default=None)
    report_p.add_argument("--runs-root", default=None)
    report_p.add_argument("--out", default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        if args.wm not in VALID_WMS:
            print(f"invalid_wm: {args.wm}", file=sys.stderr)
            return 2
        if args.arm not in ARM_NAMES:
            print(f"unknown_arm: {args.arm}", file=sys.stderr)
            return 2
        try:
            arm = load_arm(ARMS_DIR / f"{args.arm}.toml")
        except BenchError as exc:
            print(str(exc), file=sys.stderr)
            return 2

        record = execute_wm(
            arm,
            args.wm,
            agent_cmd=args.agent_cmd,
            timeout_s=args.timeout_s,
            retries=args.retries,
        )
        print(record.to_json())
        return 0

    if args.command == "resume":
        if args.arm not in ARM_NAMES:
            print(f"unknown_arm: {args.arm}", file=sys.stderr)
            return 2
        resume_wm = find_resume_point(args.arm)
        if resume_wm is None:
            print(f"nothing_to_resume: {args.arm}", file=sys.stderr)
            return 2
        try:
            arm = load_arm(ARMS_DIR / f"{args.arm}.toml")
        except BenchError as exc:
            print(str(exc), file=sys.stderr)
            return 2

        last_record = None
        for wm in range(resume_wm, 6):
            last_record = execute_wm(
                arm,
                wm,
                agent_cmd=args.agent_cmd,
                timeout_s=args.timeout_s,
                retries=args.retries,
            )
            print(last_record.to_json())
        return 0

    if args.command == "score":
        try:
            record = score_record(args.arm, args.wm, judge_cmd=args.judge_cmd)
        except BenchError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(record.to_json())
        return 0

    if args.command == "report":
        if args.arm is not None and args.arm not in ARM_NAMES:
            print(f"unknown_arm: {args.arm}", file=sys.stderr)
            return 2
        if args.wm is not None and args.wm not in VALID_WMS:
            print(f"invalid_wm: {args.wm}", file=sys.stderr)
            return 2

        runs_root = pathlib.Path(args.runs_root) if args.runs_root else None
        arms = [args.arm] if args.arm is not None else ARM_NAMES
        wms = [args.wm] if args.wm is not None else VALID_WMS
        text = render_report(runs_root, arms=arms, wms=wms)
        if args.out:
            pathlib.Path(args.out).write_text(text)
        else:
            print(text)
        return 0

    parser.error("unknown command")
    return 2  # pragma: no cover


if __name__ == "__main__":
    raise SystemExit(main())
