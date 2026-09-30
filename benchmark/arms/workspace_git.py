#!/usr/bin/env python3
"""Arm setup step: give the workspace (the cwd) its OWN git repo and a baseline commit.

    python3 {REPO_ROOT}/benchmark/arms/workspace_git.py      # run with cwd = the workspace

Why a harness step and not the agent's business:

* A workspace lives under `benchmark/runs/`, INSIDE the harness's git repo (gitignored).
  Without its own repo, every `git commit` an arm makes — ADD 4.0's `freeze(<slug>)` seal
  among them — resolves to the harness repo; and a census reading `git log` would report
  the harness's history as the arm's adherence.
* ADD 3.7's `gate` refuses a receipt whose content digest it cannot take outside a git
  working tree. Both ADD arms get this step, identically, so neither starts ahead.

Local config only (never the operator's global): a fixed identity, commit/tag signing off
(an operator's `commit.gpgsign=true` would otherwise block every headless commit), and
hooks pointed at an empty path. `.venv/` is ignored — it is setup's, not the arm's work.
Idempotent: re-running on a clean tree (session mode, a carried-forward workspace) adds
no commit. Stdlib only; exits non-zero with the git error on any failure.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

IDENTITY = {"user.name": "bench-agent", "user.email": "bench-agent@example.invalid"}
LOCAL_CONFIG = {**IDENTITY, "commit.gpgsign": "false", "tag.gpgsign": "false",
                "core.hooksPath": ".git/no-hooks"}
BASELINE_MSG = "chore(bench): workspace baseline"


def _git(ws: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=ws, check=True, capture_output=True,
                          text=True).stdout.strip()


def main() -> int:
    ws = pathlib.Path.cwd().resolve()
    try:
        if not (ws / ".git").exists():
            _git(ws, "init", "-q")
            _git(ws, "symbolic-ref", "HEAD", "refs/heads/main")   # deterministic, git-version-proof
        top = pathlib.Path(_git(ws, "rev-parse", "--show-toplevel")).resolve()
        if top != ws:
            print(f"workspace_git: git toplevel is {top}, not the workspace {ws}", file=sys.stderr)
            return 1
        for key, value in LOCAL_CONFIG.items():
            _git(ws, "config", "--local", key, value)
        ignore = ws / ".gitignore"
        lines = ignore.read_text().splitlines() if ignore.exists() else []
        if ".venv/" not in lines and ".venv" not in lines:
            ignore.write_text("\n".join([*lines, ".venv/"]) + "\n")
        _git(ws, "add", "-A")
        if _git(ws, "status", "--porcelain"):
            _git(ws, "commit", "-q", "--no-verify", "-m", BASELINE_MSG)
            print(f"workspace_git: baseline committed in {ws}")
        else:
            print(f"workspace_git: {ws} already clean — no commit")
    except subprocess.CalledProcessError as exc:
        print(f"workspace_git: {' '.join(exc.cmd)} -> {exc.returncode}: {exc.stderr}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
