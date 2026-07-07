"""Pilot round-2 hardening (pilot-cwd-hardening fast task): the agent
subprocess starts INSIDE its sandbox workspace, and regression scoring uses a
pytest-capable interpreter argv (uv fallback) instead of silently parsing a
"No module named pytest" failure as zero collected tests."""
from __future__ import annotations

import pathlib
import sys
import textwrap

import pytest

import benchmark.score as score
from benchmark.arms.loader import Arm
from benchmark.runner.core import execute_wm
from benchmark.schema.run_record import BenchError


def _bare_arm():
    return Arm(
        name="fake-arm",
        setup_steps=[],
        prompt_wrapper="raw",
        pin="",
        same_model=True,
        token_ceiling=200000,
        turn_ceiling=60,
    )


def test_agent_runs_inside_workspace(tmp_path):
    """The fake agent writes its own os.getcwd() to a side-effect file; it
    must be the WM workspace dir, never the pilot's launch cwd."""
    marker = tmp_path / "agent_cwd.txt"
    fake_agent = [
        sys.executable,
        "-c",
        f"import os,pathlib;pathlib.Path({str(marker)!r}).write_text(os.getcwd())",
    ]
    record = execute_wm(
        _bare_arm(),
        1,
        agent_cmd=fake_agent,
        timeout_s=30,
        retries=0,
        runs_root=tmp_path / "runs",
    )
    expected_ws = pathlib.Path(record.artifacts["workspace"]).resolve()
    assert marker.exists(), "fake agent never ran"
    assert pathlib.Path(marker.read_text()).resolve() == expected_ws


def test_pytest_argv_uses_sys_executable_when_available(monkeypatch):
    monkeypatch.setattr(score.importlib.util, "find_spec", lambda name: object())
    assert score._pytest_argv() == [sys.executable, "-m", "pytest"]


def test_pytest_argv_falls_back_to_uv(monkeypatch):
    monkeypatch.setattr(score.importlib.util, "find_spec", lambda name: None)
    assert score._pytest_argv() == [
        "uv", "run", "--no-project", "--with", "pytest", "python", "-m", "pytest",
    ]


def test_zero_collected_error_includes_stderr(monkeypatch, tmp_path):
    class FakeProc:
        returncode = 1
        stdout = ""
        stderr = "/some/python: No module named pytest"

    monkeypatch.setattr(score.subprocess, "run", lambda *a, **k: FakeProc())
    with pytest.raises(BenchError) as exc:
        score.compute_regression_rate(tmp_path)
    msg = str(exc.value)
    assert msg.startswith("regression_run_failed: no regression tests collected")
    assert "No module named pytest" in msg
