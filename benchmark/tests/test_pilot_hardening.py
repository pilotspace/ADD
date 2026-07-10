"""Live-pilot hardening (pilot-live-hardening fast task): an unlaunchable
setup command fails the attempt loudly instead of crashing the pilot, and the
arm setup lines are idempotent / PATH-independent."""
from __future__ import annotations

import pathlib
import sys

import tomllib

from benchmark.arms.loader import Arm
from benchmark.runner.core import execute_wm

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ARMS = REPO_ROOT / "benchmark" / "arms"


def _arm_with_setup(steps):
    return Arm(
        name="fake-arm",
        setup_steps=steps,
        prompt_wrapper="raw",
        pin="",
        same_model=True,
        token_ceiling=200000,
        turn_ceiling=60,
    )


def test_unlaunchable_setup_fails_attempt_loudly(tmp_path):
    arm = _arm_with_setup(["definitely-not-a-real-binary-xyz --flag"])
    record = execute_wm(
        arm,
        1,
        agent_cmd=[sys.executable, "-c", "import sys; sys.exit(0)"],
        timeout_s=10,
        retries=0,
        runs_root=tmp_path / "runs",
    )
    assert record.status == "failed"
    assert "unlaunchable" in record.artifacts["attempts"]
    assert "definitely-not-a-real-binary-xyz" in record.artifacts["attempts"]


def test_arm_setup_lines_hardened():
    def steps(name):
        with open(ARMS / f"{name}.toml", "rb") as f:
            return tomllib.load(f)["setup_steps"]

    add = steps("add")
    assert any("uv venv" in s and "--clear" in s for s in add), \
        "add venv line must be idempotent (--clear)"
    assert steps("vanilla") == [], "vanilla needs no setup ceremony"
    assert steps("plan-mode") == [], "plan-mode needs no setup ceremony"
    gsd = steps("gsd")
    assert len(gsd) == 1 and gsd[0].startswith("npx -y get-shit-done-cc@1.42.3"), \
        "gsd setup must be npx-based (no global-install PATH dependency)"
