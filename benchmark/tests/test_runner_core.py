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
from benchmark.runner.agent import default_agent_cmd
from benchmark.runner.core import execute_wm


def test_default_agent_cmd_isolates_env():
    """harness-isolate-env: every real benchmark `claude -p` must run in a minimal,
    identical environment — no operator skills/commands/MCP leak into the measured
    system prompt (harness problem #2). Asserts the two isolation flags AND the
    preserved stream-json transcript contract + the prompt positional."""
    argv = default_agent_cmd("PROMPT")
    # env isolation
    assert "--disable-slash-commands" in argv  # strips the 148-skill/174-command catalog
    assert "--strict-mcp-config" in argv       # no MCP servers absent an explicit --mcp-config
    # preserved contract
    for tok in ("claude", "-p", "PROMPT", "--output-format", "stream-json"):
        assert tok in argv, tok

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

    real_add = load_arm(BENCHMARK_ROOT / "arms" / "add.toml")
    # Fixture correction (re-cross, human-approved 2026-07-07): keep the real
    # add.toml pin but drop its env-provisioning setup_steps, which cannot
    # succeed in an empty sandbox — this test asserts M7 (pin -> SHA), not M1.
    arm = Arm(
        name=real_add.name,
        setup_steps=[],
        prompt_wrapper=real_add.prompt_wrapper,
        pin=real_add.pin,
        same_model=real_add.same_model,
        token_ceiling=real_add.token_ceiling,
        turn_ceiling=real_add.turn_ceiling,
    )
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


def test_setup_steps_run_in_order_before_agent(tmp_path):
    """gapfix M1: setup_steps run, in order, before the agent invocation."""
    order_file = tmp_path / "order.txt"
    script = _write_script(
        tmp_path,
        "fake_after_setup.py",
        f"""
        #!/usr/bin/env python3
        import sys
        with open({str(order_file)!r}, "a") as f:
            f.write("agent\\n")
        sys.exit(0)
        """,
    )
    arm = Arm(
        name="setup-arm",
        setup_steps=[
            f"{sys.executable} -c \"open({str(order_file)!r}, 'a').write('step1\\n')\"  # inline comment stripped",
            f"{sys.executable} -c \"open({str(order_file)!r}, 'a').write('step2\\n')\"",
        ],
        prompt_wrapper="raw",
        pin="",
        same_model=True,
        token_ceiling=200000,
        turn_ceiling=60,
    )
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
    assert order_file.read_text().splitlines() == ["step1", "step2", "agent"]
    # setup outcomes are visible in artifacts/transcript, like agent attempts
    assert "setup:" in record.artifacts["attempts"]
    transcript_path = pathlib.Path(record.artifacts["transcript"])
    assert "setup:" in transcript_path.read_text()


def test_setup_steps_empty_is_noop(tmp_path):
    script = _write_script(
        tmp_path,
        "fake_ok2.py",
        """
        #!/usr/bin/env python3
        import sys
        sys.exit(0)
        """,
    )
    runs_root = tmp_path / "runs"
    record = execute_wm(
        _arm(),  # setup_steps=[] by default
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10,
        retries=0,
        runs_root=runs_root,
    )
    assert record.status == "done"
    assert "setup:" not in record.artifacts["attempts"]


def test_setup_step_failure_fails_attempt_visibly(tmp_path):
    """A nonzero setup step fails that attempt loudly — recorded, not
    swallowed — and the agent is never invoked."""
    invocation_log = tmp_path / "invocations.txt"
    script = _write_script(
        tmp_path,
        "fake_never.py",
        f"""
        #!/usr/bin/env python3
        import sys
        with open({str(invocation_log)!r}, "a") as f:
            f.write("invoked\\n")
        sys.exit(0)
        """,
    )
    arm = Arm(
        name="setup-fail-arm",
        setup_steps=[f"{sys.executable} -c \"import sys; sys.exit(1)\"  # deliberately fails"],
        prompt_wrapper="raw",
        pin="",
        same_model=True,
        token_ceiling=200000,
        turn_ceiling=60,
    )
    runs_root = tmp_path / "runs"
    record = execute_wm(
        arm,
        1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10,
        retries=1,
        runs_root=runs_root,
    )
    assert record.status == "failed"
    assert not invocation_log.exists()  # agent never invoked
    assert "setup:" in record.artifacts["attempts"]
    assert "exit 1" in record.artifacts["attempts"]


def test_timeout_consumes_a_retry_then_succeeds(tmp_path):
    """gapfix M2: a timeout counts as one failed attempt that consumes a
    retry; status='timeout' only once retries are exhausted."""
    sentinel = tmp_path / "sentinel"
    script = _write_script(
        tmp_path,
        "fake_flip.py",
        f"""
        #!/usr/bin/env python3
        import pathlib, sys, time
        sentinel = pathlib.Path({str(sentinel)!r})
        if not sentinel.exists():
            sentinel.write_text("x")
            time.sleep(30)
        else:
            sys.exit(0)
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
    assert record.status == "done"
    assert "attempt 1: timeout" in record.artifacts["attempts"]
    assert "attempt 2: done" in record.artifacts["attempts"]
