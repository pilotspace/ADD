"""Scenarios: report renders the arm-vs-arm markdown comparison from fixture
record.json files alone (M1-M4, R1-R2) — hermetic, no live agent/judge call.
"""
from __future__ import annotations

import pathlib

import pytest

from benchmark import report as report_mod
from benchmark.arms.loader import ARM_NAMES
from benchmark.runner.records import write_record_atomic
from benchmark.schema.run_record import validate


def _record(
    arm: str,
    wm: int,
    *,
    status: str = "done",
    requirement_coverage: float = 0.82,
    oracle_pass_rate: float = 1.0,
    regression_rate: float = 0.0,
    context_rot_slope: float = 0.0,
    tokens_total: float = 4200.0,
    cost_usd: float = 0.31,
    extra_artifacts: dict | None = None,
):
    artifacts = {
        "workspace": f"/runs/{arm}/wm{wm}/workspace",
        "transcript": f"/runs/{arm}/wm{wm}/transcript.jsonl",
        "oracle_report": f"/runs/{arm}/wm{wm}/oracle_report.json",
    }
    if extra_artifacts:
        artifacts.update(extra_artifacts)
    return validate(
        {
            "arm": arm,
            "wm": wm,
            "rep": 0,
            "status": status,
            "metrics": {
                "regression_rate": regression_rate,
                "requirement_coverage": requirement_coverage,
                "oracle_pass_rate": oracle_pass_rate,
                "tokens_total": tokens_total,
                "cost_usd": cost_usd,
                "context_rot_slope": context_rot_slope,
                "time_to_first_edit": 3.0,
            },
            "artifacts": artifacts,
        }
    )


def _seed_full_grid(runs_root: pathlib.Path) -> None:
    for arm in ARM_NAMES:
        for wm in (1, 2, 3):
            record = _record(arm, wm)
            write_record_atomic(runs_root / arm / f"wm{wm}" / "record.json", record)


def test_report_renders_full_grid(tmp_path):
    runs_root = tmp_path / "runs"
    _seed_full_grid(runs_root)

    text = report_mod.render_report(runs_root)

    # 3 tables, one per WM
    assert text.count("WM1") >= 1
    assert text.count("WM2") >= 1
    assert text.count("WM3") >= 1
    for arm in ARM_NAMES:
        assert text.count(arm) >= 3  # appears in each of the 3 tables
    # evidence links present for every cell (record.json / transcript paths)
    assert "workspace" in text or "record.json" in text
    assert "transcript.jsonl" in text


def test_report_missing_record_renders_not_run(tmp_path):
    runs_root = tmp_path / "runs"
    _seed_full_grid(runs_root)
    # remove gsd/wm2 entirely
    missing = runs_root / "gsd" / "wm2" / "record.json"
    missing.unlink()

    text = report_mod.render_report(runs_root)

    assert "not run" in text
    # other cells still populated
    assert "0.82" in text


def test_report_wm1_wm2_na_annotation(tmp_path):
    runs_root = tmp_path / "runs"
    # tokens_total/cost_usd deliberately avoid a trailing ".00" so the
    # assertion below is unambiguous about which cells it's checking.
    record = _record(
        "add",
        1,
        regression_rate=0.0,
        context_rot_slope=0.0,
        tokens_total=4321.55,
        cost_usd=0.31,
    )
    write_record_atomic(runs_root / "add" / "wm1" / "record.json", record)

    text = report_mod.render_report(runs_root, arms=["add"], wms=[1])

    assert "N/A (by definition)" in text
    assert "0.00" not in text


# (honest-fidelity-meter) the spec_fidelity_audit / "(unaudited)" annotation
# was DROPPED: requirement_coverage is deterministic (probes against the built
# app), so there is no subjective per-record score for a human to attest.


def test_report_rejects_unknown_arm(tmp_path):
    from benchmark import run as run_mod

    runs_root = tmp_path / "runs"
    runs_root.mkdir()

    rc = run_mod.main(["report", "--arm", "ghost", "--runs-root", str(runs_root)])
    assert rc == 2


def test_report_rejects_invalid_wm(tmp_path, capsys):
    from benchmark import run as run_mod

    runs_root = tmp_path / "runs"
    runs_root.mkdir()

    rc = run_mod.main(["report", "--wm", "9", "--runs-root", str(runs_root)])
    assert rc == 2
    out = capsys.readouterr()
    assert "invalid_wm" in out.err
