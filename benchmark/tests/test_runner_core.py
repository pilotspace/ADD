"""Scenarios: execute_wm success/timeout/retry/tokens/oracle-leak/pin
(M1, M2, M3, M5, M5-edge, M6, M7) — fully hermetic via the fake-agent seam,
no live `claude` call."""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import sys
import textwrap

import pytest

from benchmark.arms.loader import Arm
from benchmark.runner.core import execute_wm

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "benchmark"


def _arm(name: str = "fake-arm", pin: str = "") -> Arm:
    return Arm(
        name=name,
        setup_steps=[],
        prompt_wrapper="raw",
        pin=pin,
        same_model=True,
        token_ceiling=200000,
        turn_ceiling=60,
    )


def _write_script(tmp_path: pathlib.Path, name: str, body: str) -> pathlib.Path:
    script = tmp_path / name
    script.write_text(textwrap.dedent(body))
    script.chmod(0o755)
    return script


def test_run_writes_done_record(tmp_path):
    script = _write_script(
        tmp_path,
        "fake_ok.py",
        """
        #!/usr/bin/env python3
        import json, sys
        print(json.dumps({"type": "tool_use", "name": "Write"}))
        print(json.dumps({
            "type": "result",
            "total_cost_usd": 0.01,
            "usage": {"input_tokens": 10, "output_tokens": 5,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        }))
        sys.exit(0)
        """,
    )
    runs_root = tmp_path / "runs"
    record = execute_wm(
        _arm(),
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10,
        retries=1,
        runs_root=runs_root,
    )
    assert record.status == "done"
    record_path = runs_root / "fake-arm" / "wm1" / "record.json"
    assert record_path.exists()
    from benchmark.schema.run_record import RunRecord

    reloaded = RunRecord.from_json(record_path.read_text())
    assert reloaded.status == "done"
    assert reloaded.metrics["tokens_total"] == 15.0


def test_run_timeout_kills_and_records(tmp_path):
    script = _write_script(
        tmp_path,
        "fake_sleep.py",
        """
        #!/usr/bin/env python3
        import time
        time.sleep(30)
        """,
    )
    runs_root = tmp_path / "runs"
    record = execute_wm(
        _arm(),
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=0.5,
        retries=1,
        runs_root=runs_root,
    )
    assert record.status == "timeout"
    record_path = runs_root / "fake-arm" / "wm1" / "record.json"
    assert record_path.exists()


def test_run_retries_then_fails(tmp_path):
    counter_file = tmp_path / "counter.txt"
    script = _write_script(
        tmp_path,
        "fake_fail.py",
        f"""
        #!/usr/bin/env python3
        import sys
        counter_path = {str(counter_file)!r}
        try:
            with open(counter_path) as f:
                n = int(f.read() or "0")
        except FileNotFoundError:
            n = 0
        with open(counter_path, "w") as f:
            f.write(str(n + 1))
        sys.exit(1)
        """,
    )
    runs_root = tmp_path / "runs"
    record = execute_wm(
        _arm(),
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10,
        retries=2,
        runs_root=runs_root,
    )
    assert record.status == "failed"
    assert counter_file.read_text() == "3"  # N+1 = 2+1 invocations
    assert "attempt 1" in record.artifacts["attempts"]
    assert "attempt 3" in record.artifacts["attempts"]


def test_transcript_and_tokens_captured(tmp_path):
    script = _write_script(
        tmp_path,
        "fake_tokens.py",
        """
        #!/usr/bin/env python3
        import json, sys
        print(json.dumps({
            "type": "result",
            "total_cost_usd": 0.02,
            "usage": {"input_tokens": 100, "output_tokens": 50,
                      "cache_creation_input_tokens": 1, "cache_read_input_tokens": 2},
        }))
        sys.exit(0)
        """,
    )
    runs_root = tmp_path / "runs"
    record = execute_wm(
        _arm(),
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10,
        retries=0,
        runs_root=runs_root,
    )
    assert record.status == "done"
    assert record.metrics["tokens_total"] == 153.0
    transcript_path = pathlib.Path(record.artifacts["transcript"])
    assert transcript_path.exists()
    assert "total_cost_usd" in transcript_path.read_text()


def test_tokens_fallback_when_absent(tmp_path):
    script = _write_script(
        tmp_path,
        "fake_plain.py",
        """
        #!/usr/bin/env python3
        print("just plain text, not json")
        """,
    )
    runs_root = tmp_path / "runs"
    record = execute_wm(
        _arm(),
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10,
        retries=0,
        runs_root=runs_root,
    )
    assert record.status == "done"
    assert record.metrics["tokens_total"] == 0.0
    assert record.artifacts.get("token_source") == "unparseable"


def test_oracle_leak_fails_run(tmp_path, monkeypatch):
    wm1_oracle_dir = BENCHMARK_ROOT / "workload" / "wm1" / "oracle"
    oracle_files = sorted(wm1_oracle_dir.glob("test_*.py"))
    assert oracle_files, "no wm1 oracle files found to leak"

    runs_root = tmp_path / "runs"
    workspace_dir = runs_root / "fake-arm" / "wm1" / "workspace"

    script = _write_script(
        tmp_path,
        "fake_leak.py",
        f"""
        #!/usr/bin/env python3
        import shutil, sys
        shutil.copyfile({str(oracle_files[0])!r}, {str(workspace_dir)!r} + "/leaked.py")
        sys.exit(0)
        """,
    )
    record = execute_wm(
        _arm(),
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10,
        retries=0,
        runs_root=runs_root,
    )
    assert record.status == "failed"
    assert record.artifacts.get("leak_path")


def test_add_arm_pin_resolved_to_sha(tmp_path):
    script = _write_script(
        tmp_path,
        "fake_add.py",
        """
        #!/usr/bin/env python3
        import sys
        sys.exit(0)
        """,
    )
    from benchmark.arms.loader import load_arm

    arm = load_arm(BENCHMARK_ROOT / "arms" / "add.toml")
    runs_root = tmp_path / "runs"
    record = execute_wm(
        arm,
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10,
        retries=0,
        runs_root=runs_root,
    )
    assert record.status == "done"
    resolved = record.artifacts["resolved_pin"]
    assert resolved != arm.pin
    assert len(resolved) in (7, 40) or all(c in "0123456789abcdef" for c in resolved)
