"""Scenarios: unknown_arm / invalid_arm_recipe / invalid_wm / nothing_to_resume
(R1-R4) — CLI rejects before any workspace/record/agent-spawn."""
from __future__ import annotations

import pathlib
import sys

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


def _write_vanilla_arm(arms_dir: pathlib.Path) -> None:
    arms_dir.mkdir(exist_ok=True)
    (arms_dir / "vanilla.toml").write_text(
        'name = "vanilla"\n'
        "setup_steps = []\n"
        'prompt_wrapper = "raw"\n'
        'pin = ""\n'
        "same_model = true\n"
        "token_ceiling = 200000\n"
        "turn_ceiling = 60\n"
    )


def _write_fake_agent(tmp_path: pathlib.Path, name: str = "fake_ok.py") -> pathlib.Path:
    script = tmp_path / name
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        'print(json.dumps({"type": "result", "total_cost_usd": 0.0, '
        '"usage": {"input_tokens": 1, "output_tokens": 1, '
        '"cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}))\n'
        "sys.exit(0)\n"
    )
    script.chmod(0o755)
    return script


def test_run_cli_success_end_to_end(tmp_path, monkeypatch):
    """gapfix CLI: `run.py run` succeeds end-to-end with a fake agent —
    record.json exists, exit 0."""
    arms_dir = tmp_path / "arms"
    _write_vanilla_arm(arms_dir)
    monkeypatch.setattr(run_mod, "ARMS_DIR", arms_dir)
    runs_root = tmp_path / "runs"
    monkeypatch.setattr(records_mod, "DEFAULT_RUNS_ROOT", runs_root)
    monkeypatch.setattr(core_mod, "DEFAULT_RUNS_ROOT", runs_root)

    script = _write_fake_agent(tmp_path)

    rc = run_mod.main(
        ["run", "--arm", "vanilla", "--wm", "1", "--agent-cmd", sys.executable, str(script)]
    )
    assert rc == 0
    record_path = runs_root / "vanilla" / "wm1" / "record.json"
    assert record_path.exists()


def test_resume_cli_sequences_remaining_wms(tmp_path, monkeypatch):
    """gapfix CLI: `run.py resume` sequences the remaining WMs after a done
    wm1 — invokes only wm2/wm3, writes their records, exit 0."""
    arms_dir = tmp_path / "arms"
    _write_vanilla_arm(arms_dir)
    monkeypatch.setattr(run_mod, "ARMS_DIR", arms_dir)
    runs_root = tmp_path / "runs"
    monkeypatch.setattr(records_mod, "DEFAULT_RUNS_ROOT", runs_root)
    monkeypatch.setattr(core_mod, "DEFAULT_RUNS_ROOT", runs_root)

    # seed wm1 as already done, so resume must skip it
    from benchmark.runner.records import write_record_atomic
    from benchmark.schema.run_record import validate

    wm1_record = validate(
        {
            "arm": "vanilla",
            "wm": 1,
            "rep": 0,
            "status": "done",
            "metrics": {
                "regression_rate": 0.0,
                "spec_fidelity": 0.0,
                "tokens_total": 0.0,
                "cost_usd": 0.0,
                "context_rot_slope": 0.0,
                "time_to_first_edit": 0.0,
            },
            "artifacts": {"workspace": "w", "transcript": "t", "oracle_report": "o"},
        }
    )
    write_record_atomic(runs_root / "vanilla" / "wm1" / "record.json", wm1_record)

    invocation_log = tmp_path / "invocations.txt"
    script = tmp_path / "fake_counted.py"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"with open({str(invocation_log)!r}, 'a') as f:\n"
        "    f.write('invoked\\n')\n"
        "sys.exit(0)\n"
    )
    script.chmod(0o755)

    rc = run_mod.main(["resume", "--arm", "vanilla", "--agent-cmd", sys.executable, str(script)])
    assert rc == 0
    assert invocation_log.read_text().count("invoked") == 2  # wm2 + wm3 only, never wm1
    assert (runs_root / "vanilla" / "wm2" / "record.json").exists()
    assert (runs_root / "vanilla" / "wm3" / "record.json").exists()
