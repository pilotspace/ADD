#!/usr/bin/env python3
"""run.py — thin CLI over benchmark/runner/ (bench-runner TASK.md §3 CONTRACT).

  run.py run --arm <name> --wm <1|2|3> [--timeout-s S] [--retries N] [--agent-cmd ARGV...]
  run.py resume --arm <name> [--timeout-s S] [--retries N] [--agent-cmd ARGV...]

exit 0 on success; exit 2 with one of the frozen codes on rejection
(unknown_arm | invalid_arm_recipe | invalid_wm | nothing_to_resume) — no
workspace/record created for any exit-2 path.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from benchmark.arms.loader import ARM_NAMES, load_arm
from benchmark.runner.core import execute_wm
from benchmark.runner.records import find_resume_point
from benchmark.schema.run_record import BenchError

ARMS_DIR = pathlib.Path(__file__).resolve().parent / "arms"
VALID_WMS = (1, 2, 3)


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
        for wm in range(resume_wm, 4):
            last_record = execute_wm(
                arm,
                wm,
                agent_cmd=args.agent_cmd,
                timeout_s=args.timeout_s,
                retries=args.retries,
            )
            print(last_record.to_json())
        return 0

    parser.error("unknown command")
    return 2  # pragma: no cover


if __name__ == "__main__":
    raise SystemExit(main())
