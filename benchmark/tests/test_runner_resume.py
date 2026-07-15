"""Scenario: resume skips a WM already done (M4) — hermetic fake-agent seam."""
from __future__ import annotations

import pathlib
import sys
import textwrap

from benchmark.arms.loader import Arm
from benchmark.runner.core import execute_wm
from benchmark.runner.records import find_resume_point
from benchmark.schema.run_record import RunRecord, validate
from benchmark.runner.records import write_record_atomic


def _arm(name: str = "resume-arm") -> Arm:
    return Arm(
        name=name,
        setup_steps=[],
        prompt_wrapper="raw",
        pin="",
        same_model=True,
        token_ceiling=200000,
        turn_ceiling=60,
    )


def _seed_done_record(runs_root: pathlib.Path, arm_name: str, wm: int) -> None:
    record = validate(
        {
            "arm": arm_name,
            "wm": wm,
            "rep": 0,
            "status": "done",
            "metrics": {
                "regression_rate": 0.0,
                "requirement_coverage": 0.0,
                "oracle_pass_rate": 0.0,
                "tokens_total": 0.0,
                "cost_usd": 0.0,
                "context_rot_slope": 0.0,
                "time_to_first_edit": 0.0,
            },
            "artifacts": {"workspace": "w", "transcript": "t", "oracle_report": "o"},
        }
    )
    path = runs_root / arm_name / f"wm{wm}" / "record.json"
    write_record_atomic(path, record)


def test_resume_skips_done_wm(tmp_path):
    runs_root = tmp_path / "runs"
    arm = _arm()
    _seed_done_record(runs_root, arm.name, 1)

    resume_wm = find_resume_point(arm.name, runs_root=runs_root)
    assert resume_wm == 2

    invocation_log = tmp_path / "invocations.txt"
    script_path = tmp_path / "fake_once.py"
    script_path.write_text(
        textwrap.dedent(
            f"""
            #!/usr/bin/env python3
            import sys
            with open({str(invocation_log)!r}, "a") as f:
                f.write("invoked\\n")
            sys.exit(0)
            """
        )
    )
    script_path.chmod(0o755)

    record = execute_wm(
        arm,
        resume_wm,
        agent_cmd=[sys.executable, str(script_path)],
        timeout_s=10,
        retries=0,
        runs_root=runs_root,
    )
    assert record.wm == 2
    assert invocation_log.read_text().count("invoked") == 1

    wm1_record = RunRecord.from_json((runs_root / arm.name / "wm1" / "record.json").read_text())
    assert wm1_record.status == "done"
