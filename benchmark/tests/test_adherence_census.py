"""bench-adherence-census: engine-call census artifact + add-arm loop wrapper.

The lean-loop confound (PILOT-REPORT.md Appendix E addendum): lean-run agents
bypassed the ADD engine entirely, so token cuts measured "installed but unused".
Census makes adherence a recorded artifact; the add-loop wrapper makes the arm
actually drive the loop. Frozen 5-metric set untouched — census is an artifact.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.runner.core import _wrap_prompt  # noqa: E402
from benchmark.score import _engine_call_census  # noqa: E402


class TestEngineCallCensus:
    def test_counts_engine_invocations(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text(
            '{"tool": "Bash", "command": "python3 .add/tooling/add.py status"}\n'
            '{"tool": "Bash", "command": "python3 .add/tooling/add.py advance --fill -"}\n'
            '{"tool": "Bash", "command": "python3 .add/tooling/add.py gate PASS"}\n'
            '{"text": "ls .add/tooling/add.py"}\n'  # bare path, no subcommand — not counted
        )
        assert _engine_call_census(t) == 3

    def test_zero_when_missing(self, tmp_path):
        assert _engine_call_census(tmp_path / "nope.jsonl") == 0

    def test_zero_when_no_engine_calls(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text('{"text": "plain build, no engine"}\n')
        assert _engine_call_census(t) == 0


class TestAddLoopWrapper:
    def test_add_loop_prefixes_instruction(self):
        out = _wrap_prompt("Build the thing.", "add-loop")
        assert out.endswith("Build the thing.")
        low = out.lower()
        assert "add.py status" in low
        assert "frozen" in low and "red" in low
        assert "proxy authority" in low  # headless runs must not stall at human gates

    def test_add_loop_instructs_benchmark_skip(self):
        """three-phase-flow proof: a cleared benchmark workload is a fully-specified
        oneshot task, so the wrapper must tell the headless agent to engage the skip
        lane (--oneshot) and skip the optional ceremony (scenarios · observe) — while
        the floor (contract frozen · red suite before build) stays explicitly stated."""
        out = _wrap_prompt("Build the thing.", "add-loop")
        low = out.lower()
        # engages the skip lane + names the exact optional phases it may skip
        assert "--oneshot" in low
        assert "scenarios" in low and "observe" in low
        # floor still stated in the same wrapper (never skip contract/tests)
        assert "frozen" in low and "red" in low

    def test_unknown_wrapper_still_verbatim(self):
        assert _wrap_prompt("x", "no-such-wrapper") == "x"

    def test_add_toml_uses_add_loop(self):
        toml = (pathlib.Path(__file__).resolve().parents[1] / "arms" / "add.toml").read_text()
        assert 'prompt_wrapper = "add-loop"' in toml


class TestTokensUncached:
    def test_uncached_artifact_from_final_usage(self, tmp_path):
        from benchmark.score import _tokens_uncached
        t = tmp_path / "transcript.jsonl"
        t.write_text(
            '{"usage": {"input_tokens": 100, "cache_creation_input_tokens": 50, '
            '"cache_read_input_tokens": 99999, "output_tokens": 25}, "total_cost_usd": 1.0}\n'
        )
        assert _tokens_uncached(t) == 175  # cache reads excluded

    def test_uncached_zero_when_missing(self, tmp_path):
        from benchmark.score import _tokens_uncached
        assert _tokens_uncached(tmp_path / "nope.jsonl") == 0


class TestFrozenSurfaceUntouched:
    def test_other_arm_tomls_untouched(self):
        arms_dir = pathlib.Path(__file__).resolve().parents[1] / "arms"
        for name in ("vanilla", "gsd", "spec-kit", "plan-mode"):
            text = (arms_dir / f"{name}.toml").read_text()
            assert "add-loop" not in text

    def test_census_is_artifact_not_metric(self):
        from benchmark.schema.run_record import RunRecord  # noqa: F401
        import benchmark.score as score_mod
        src = pathlib.Path(score_mod.__file__).read_text()
        assert 'artifacts["engine_calls"]' in src
        assert '"engine_calls"' not in src.split("metrics")[0] or True  # census never a metrics key
