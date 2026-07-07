"""Scenarios: unknown_arm / invalid_arm_recipe / invalid_wm / nothing_to_resume
(R1-R4) — CLI rejects before any workspace/record/agent-spawn."""
from __future__ import annotations

import pathlib

import pytest

import benchmark.run as run_mod
from benchmark.runner import core as core_mod
from benchmark.runner import records as records_mod


def test_unknown_arm_rejected(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(records_mod, "DEFAULT_RUNS_ROOT", tmp_path / "runs")
    monkeypatch.setattr(core_mod, "DEFAULT_RUNS_ROOT", tmp_path / "runs")

    rc = run_mod.main(["run", "--arm", "ghost", "--wm", "1"])
    assert rc == 2
    out = capsys.readouterr()
    assert "unknown_arm" in out.err
    assert not (tmp_path / "runs" / "ghost").exists()


def test_invalid_arm_recipe_rejected(tmp_path, capsys, monkeypatch):
    arms_dir = tmp_path / "arms"
    arms_dir.mkdir()
    (arms_dir / "vanilla.toml").write_text(
        'name = "vanilla"\n'
        'prompt_wrapper = "raw"\n'
        'pin = ""\n'
        "same_model = true\n"
        "token_ceiling = 200000\n"
        "turn_ceiling = 60\n"
        # setup_steps deliberately missing
    )
    monkeypatch.setattr(run_mod, "ARMS_DIR", arms_dir)
    monkeypatch.setattr(records_mod, "DEFAULT_RUNS_ROOT", tmp_path / "runs")
    monkeypatch.setattr(core_mod, "DEFAULT_RUNS_ROOT", tmp_path / "runs")

    rc = run_mod.main(["run", "--arm", "vanilla", "--wm", "1"])
    assert rc == 2
    out = capsys.readouterr()
    assert "invalid_arm_recipe" in out.err
    assert not (tmp_path / "runs" / "vanilla").exists()


def test_invalid_wm_rejected(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(records_mod, "DEFAULT_RUNS_ROOT", tmp_path / "runs")
    monkeypatch.setattr(core_mod, "DEFAULT_RUNS_ROOT", tmp_path / "runs")

    rc = run_mod.main(["run", "--arm", "vanilla", "--wm", "4"])
    assert rc == 2
    out = capsys.readouterr()
    assert "invalid_wm" in out.err
    assert not (tmp_path / "runs").exists()


def test_resume_nothing_to_resume(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(records_mod, "DEFAULT_RUNS_ROOT", tmp_path / "runs")
    monkeypatch.setattr(core_mod, "DEFAULT_RUNS_ROOT", tmp_path / "runs")

    rc = run_mod.main(["resume", "--arm", "vanilla"])
    assert rc == 2
    out = capsys.readouterr()
    assert "nothing_to_resume" in out.err
