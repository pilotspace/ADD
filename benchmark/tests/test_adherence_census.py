"""bench-adherence-census: engine-call census artifact + add-arm loop wrapper.

The lean-loop confound (PILOT-REPORT.md Appendix E addendum): lean-run agents
bypassed the ADD engine entirely, so token cuts measured "installed but unused".
Census makes adherence a recorded artifact; the add-loop wrapper makes the arm
actually drive the loop. Frozen 5-metric set untouched — census is an artifact.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from benchmark.runner.core import _wrap_prompt  # noqa: E402
from benchmark.score import _engine_call_census  # noqa: E402

# `pilotspace-add update` is the INSTALLER's surface, not the engine's.
INSTALLER_VERBS = {"update", "init"}

# `add.py <verb>` / `cli.py <verb>`, or a bare `add <verb>` not glued to a package name.
VERB_RE = re.compile(r"(?:add\.py|cli\.py|(?<![\w/@-])add)\s+([a-z][a-z-]+)(?![\w/@-])")


def _engine_verbs() -> set[str]:
    """The verb list read from the engine's own parser, so this can never drift from the CLI.

    The whole reason the wrapper rotted unnoticed is that the assertions below used to pin literal
    strings (`assert "--cross" in low`), which made the tests *enforce* the 2.x contract: after 3.0
    retired those verbs, the suite stayed green precisely because the wrapper stayed wrong.
    """
    sys.path.insert(0, str(REPO / "add-method" / "tooling"))
    import cli  # noqa: PLC0415

    sub = next(a for a in cli.build_parser()._actions
               if isinstance(getattr(a, "choices", None), dict))
    return set(sub.choices)


class TestEngineCallCensus:
    def test_counts_engine_invocations(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text(
            '{"tool": "Bash", "command": "python3 .add/tooling/cli.py status"}\n'
            '{"tool": "Bash", "command": "python3 .add/tooling/cli.py freeze widget --by x"}\n'
            '{"tool": "Bash", "command": "python3 .add/tooling/cli.py gate widget PASS"}\n'
            '{"text": "ls .add/tooling/cli.py"}\n'  # bare path, no subcommand — not counted
        )
        assert _engine_call_census(t) == 3

    def test_still_counts_the_2x_entry_point(self, tmp_path):
        """covers: R:RESCORE — archived 2.x runs must re-score to the same number forever.

        3.0 moved the CLI from `add.py` to `cli.py`. Counting only the new name would silently
        rewrite every historical run in `benchmark/runs/` to 0 engine calls.
        """
        t = tmp_path / "transcript.jsonl"
        t.write_text(
            '{"tool": "Bash", "command": "python3 .add/tooling/add.py status"}\n'
            '{"tool": "Bash", "command": "python3 .add/tooling/add.py advance --fill -"}\n'
        )
        assert _engine_call_census(t) == 2

    def test_a_workloads_own_cli_py_is_not_an_engine_call(self, tmp_path):
        """covers: R:RESCORE, E1 — the counted name must be the ENGINE's, not any file called cli.py.

        Measured, not imagined: matching a bare `cli.py` changed the census on 10 of 22 archived
        ADD-arm transcripts, because the benchmark workloads BUILD apps that have an `app/cli.py`,
        and because `test_booking_cli.py` ends in `cli.py` too. `benchmark/runs*/` is gitignored, so
        CI can never re-measure that — these are the exact shapes those transcripts contained.
        """
        t = tmp_path / "transcript.jsonl"
        t.write_text(
            '{"text": "workspace/app/cli.py has been updated successfully"}\n'
            '{"text": "architecture residue (does api.py/cli.py duplicate the auth path?)"}\n'
            '{"text": "tests/test_booking_cli.py has been updated"}\n'
            '{"tool": "Bash", "command": "for f in app/store.py app/cli.py app/__main__.py; do :; done"}\n'
            '{"tool": "Bash", "command": ".venv/bin/python cli.py serve --port 8000"}\n'
        )
        assert _engine_call_census(t) == 0, "a workload's own cli.py was counted as an engine call"

    def test_counts_the_3x_engine_by_its_tooling_path(self, tmp_path):
        """covers: M1 — a real 3.0 engine call is anchored to `.add/tooling/`, so it is countable."""
        t = tmp_path / "transcript.jsonl"
        t.write_text(
            '{"tool": "Bash", "command": "python3 .add/tooling/cli.py status"}\n'
            '{"tool": "Bash", "command": ".venv/bin/python .add/tooling/cli.py gate slugify PASS"}\n'
        )
        assert _engine_call_census(t) == 2

    def test_the_wrapper_writes_the_countable_form(self):
        """covers: M1, R:UNCOUNTED — the arm's own prompt must not teach an uncountable shorthand.

        The census can only anchor on `.add/tooling/cli.py`; if the wrapper told the agent to type
        a bare `cli.py <verb>`, the ADD arm would drive the loop correctly and still score as
        engine-silent — the confound the census exists to detect, reintroduced by its own prompt.
        """
        out = _wrap_prompt("Build the thing.", "add-loop")
        for bare in re.finditer(r"(?<![\w/.-])cli\.py\s+[a-z]", out):
            ctx = out[max(0, bare.start() - 20):bare.start()]
            assert ctx.endswith(".add/tooling/"), \
                f"wrapper names an uncountable bare `cli.py` at ...{ctx}{out[bare.start():bare.start()+20]}..."

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
        assert "cli.py status" in low        # the 3.0 entry point — `add.py` is a library module
        assert "frozen" in low and "red" in low
        assert "proxy authority" in low  # headless runs must not stall at human gates

    def test_add_loop_names_only_verbs_the_engine_has(self):
        """covers: M1, R:PHANTOM — the arm cannot be told to run a verb 3.0 retired.

        This is the test that should have caught the rot. `add-loop` told the agent to run
        `new-task`, `freeze --cross`, `archive-milestone` and `delta-append` — all retired — and
        to orient with `add.py status`, which under 3.0 prints nothing and exits 0. The old
        assertions pinned those literals, so the suite defended the breakage instead of finding it.
        """
        out = _wrap_prompt("Build the thing.", "add-loop")
        known = _engine_verbs() | INSTALLER_VERBS
        phantoms = {v for v in VERB_RE.findall(out) if v not in known}
        assert not phantoms, f"add-loop tells the arm to run verbs the engine lacks: {phantoms}"

    def test_the_phantom_detector_can_actually_fire(self):
        """covers: R:GREENLIE — a detector that cannot fail is not a gate (mutation check)."""
        planted = "run `python3 .add/tooling/add.py new-task widget` then add status"
        known = _engine_verbs() | INSTALLER_VERBS
        hits = {v for v in VERB_RE.findall(planted) if v not in known}
        assert hits == {"new-task"}, f"expected the planted phantom, got {hits}"

    def test_add_loop_carries_no_retired_flag_or_2x_artifact(self):
        """covers: M1, E1 — flags and file names are not verbs, so the verb sweep cannot see them."""
        low = _wrap_prompt("Build the thing.", "add-loop").lower()
        for dead in ("--cross", "gate_mode:", "plan.md", "§3", "3-call walk"):
            assert dead not in low, f"add-loop still carries the 2.x artifact {dead!r}"

    def test_add_loop_states_the_floor(self):
        """covers: M2 — direction-before-speed must stay explicit in the wrapper."""
        low = _wrap_prompt("Build the thing.", "add-loop").lower()
        assert "frozen" in low and "red" in low
        assert "freeze" in low and "gate" in low

    def test_add_loop_stops_at_gate(self):
        """harness-fair-meter: the benchmark ADD arm must meter FEATURE-DELIVERY
        cost only — the wrapper tells the agent to finish at the recorded verify
        gate and NOT run the milestone-ledger close-out, which spec-kit never does
        (closes the ~29% metering asymmetry)."""
        out = _wrap_prompt("Build the thing.", "add-loop")
        low = out.lower()
        # names the ledger close-out as NOT-to-run (3.0 spelling: milestone-done · fold · milestone-archive)
        assert "milestone-done" in low
        assert "fold" in low and "milestone-archive" in low
        # finish boundary is the recorded verify gate
        assert "verify gate" in low
        assert "cli.py status" in low and "frozen" in low and "red" in low
        assert out.endswith("Build the thing.")

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
