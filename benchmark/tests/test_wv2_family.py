"""Workload family seam (v2-wv2-hostile-change TASK.md §3 CONTRACT @ v1, M1+M7).

A `family` string (default "wm") threads through prompt/run-dir/oracle/
survivors/snapshot resolution; the wm pipeline stays byte-identical. The hv
workload DATA these pins once guarded was pruned 2026-07-10
(prune-benchmark-deadweight §3 @ v1) — the seam itself stays, fixture-tested,
so a future family only needs new workload dirs.
"""
from __future__ import annotations

import json
import pathlib
import re
import types

import pytest

from benchmark import score as score_mod
from benchmark import tamper as tamper_mod
from benchmark.runner import core as core_mod
from benchmark.schema.run_record import BenchError

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKLOAD = REPO_ROOT / "benchmark" / "workload"



# --------------------------------------------------------------------------
# M1 — the family seam, default-stable
# --------------------------------------------------------------------------


def test_prompt_path_family_defaults_to_wm():
    assert core_mod._prompt_path(2) == WORKLOAD / "wm2" / "PROMPT.md"
    assert core_mod._prompt_path(3, family="hv") == WORKLOAD / "hv3" / "PROMPT.md"


def test_unknown_family_fails_loud_pre_spawn(monkeypatch):
    def boom(*a, **k):  # any spawn is a contract violation on a bad family
        raise AssertionError("subprocess must not spawn for an unknown family")

    monkeypatch.setattr(score_mod.subprocess, "run", boom)
    with pytest.raises(BenchError, match="unknown_workload_family"):
        score_mod.compute_oracle_pass_rate(pathlib.Path("/tmp/ws"), 1, family="zz")


def test_oracle_resolution_is_family_local(monkeypatch, tmp_path):
    """R4 family_oracle_mismatch: scoring with a non-wm family must resolve
    ONLY that family's workload paths — a wm path in the pytest argv is a
    cross-family leak. Uses a SYNTHETIC family under a monkeypatched
    REPO_ROOT: the original hv-data coupling died with the hv track
    (prune-benchmark-deadweight), and the seam must be provable with zero
    real workload data — that is the seam's whole promise."""
    fake_root = tmp_path / "repo"
    for step in (1, 2, 3):
        oracle = fake_root / "benchmark" / "workload" / f"zz{step}" / "oracle"
        oracle.mkdir(parents=True)
        (oracle / "test_probe.py").write_text("def test_p():\n    assert True\n")
        (oracle / "survivors.py").write_text("def test_s():\n    assert True\n")
    calls: list = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        return types.SimpleNamespace(returncode=0, stdout="4 passed in 0.1s", stderr="")

    monkeypatch.setattr(score_mod, "REPO_ROOT", fake_root)
    monkeypatch.setattr(score_mod.subprocess, "run", fake_run)
    score_mod.compute_oracle_pass_rate(pathlib.Path("/tmp/ws"), 3, family="zz")
    score_mod.compute_regression_rate_v2(pathlib.Path("/tmp/ws"), 3, family="zz")
    joined = " ".join(str(p) for call in calls for p in call)
    assert "zz3" in joined and "zz1" in joined and "zz2" in joined
    assert not re.search(r"workload/wm\d", joined), f"wm leak into family scoring: {joined}"


def test_snapshot_dirs_are_family_keyed(tmp_path):
    ws = tmp_path / "ws"
    (ws / "tests").mkdir(parents=True)
    (ws / "tests" / "test_a.py").write_text("def test_x():\n    assert f() == 1\n")
    dest = tamper_mod.snapshot_tests(ws, tmp_path / "runs" / "add", 2, family="hv")
    assert dest == tmp_path / "runs" / "add" / "snapshots" / "hv2"
    # weakened diff reads the same family keying
    (ws / "tests" / "test_a.py").write_text("def test_x():\n    assert f() == 2\n")
    tamper_mod.snapshot_tests(ws, tmp_path / "runs" / "add", 3, family="hv")
    assert tamper_mod.compute_tests_weakened(tmp_path / "runs" / "add", 3, family="hv") == 1


# --------------------------------------------------------------------------
# M7 — records self-certify the meter
# --------------------------------------------------------------------------


def test_execute_wm_stamps_model(tmp_path):
    """artifacts.model = the pinned meter literal, stamped at execution time."""
    src = (REPO_ROOT / "benchmark" / "runner" / "core.py").read_text()
    assert '"model": PINNED_MODEL' in src, (
        "execute_wm must stamp the resolved model into every record's artifacts"
    )
    from benchmark.runner.agent import PINNED_MODEL, default_agent_cmd

    argv = default_agent_cmd("P")
    model = argv[argv.index("--model") + 1]
    assert model == PINNED_MODEL == "claude-sonnet-5"  # one source of truth


# --------------------------------------------------------------------------
# M5 — pilot CLI carries --family (spend still human-gated at run time)
# --------------------------------------------------------------------------


def test_pilot_cli_accepts_family():
    src = (REPO_ROOT / "benchmark" / "pilot.py").read_text()
    assert '"--family"' in src, "run-all must accept --family"
    assert 'default="wm"' in src, "the --family CLI default must be wm"
    assert '"hv"' in src, "hv must be an accepted family choice"
