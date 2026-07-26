"""Interrupt-resume mechanics: the kill must be fair, real, and inescapable.

Three failure modes this suite exists to prevent, all of which would produce
numbers that look fine:

FAIRNESS — a kill point that varies by arm compares methods at different amounts
of completed work while presenting itself as a controlled experiment. The guard
is structural, not statistical: sample_kill_point takes no arm parameter at all.

REALITY — a "kill" that leaves the agent's CHILDREN alive lets a test runner or
server keep writing into the workspace we are about to resume, so the resumed
run races the corpse of the interrupted one.

INESCAPABILITY — an agent that writes no code never reaches the k-th write. With
no backstop, not building would buy immunity from interruption, and a
planning-heavy method could post perfect recovery by never having started.

The fake agents here are real subprocesses that really write files and really
spawn children. A mocked kill proves the mock.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import time

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.interrupt import (
    DEFAULT_SEED,
    count_code_writes,
    sample_kill_point,
    watch_and_kill,
)

# A fake agent: appends `writes` Write events to a streaming transcript, one per
# tick, then idles. Spawns a child first so the process-group kill is testable.
_FAKE_AGENT = r'''
import json, os, subprocess, sys, time
transcript, writes, delay = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
child_pidfile = sys.argv[4]

child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
open(child_pidfile, "w").write(str(child.pid))

with open(transcript, "a", buffering=1) as fh:
    fh.write(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "thinking first"}]}}) + "\n")
    for i in range(writes):
        time.sleep(delay)
        fh.write(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write",
             "input": {"file_path": f"app/m{i}.py", "content": "x"}}]}}) + "\n")
time.sleep(120)
'''


def _spawn(tmp_path: pathlib.Path, writes: int, delay: float = 0.15):
    script = tmp_path / "fake_agent.py"
    script.write_text(_FAKE_AGENT, encoding="utf-8")
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    pidfile = tmp_path / "child.pid"
    proc = subprocess.Popen(
        [sys.executable, str(script), str(transcript), str(writes), str(delay),
         str(pidfile)],
        start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc, transcript, pidfile


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, OSError):
        return False
    return True


# ── M1 · fairness ─────────────────────────────────────────────────────────────

class TestKillPointFairness:
    def test_kill_point_is_deterministic(self):
        # M1 — a campaign must be reproducible, and a reader must be able to
        # recompute any published kill point from the record.
        assert sample_kill_point(1, 0) == sample_kill_point(1, 0)
        assert sample_kill_point(1, 0, seed=DEFAULT_SEED) == sample_kill_point(1, 0)

    def test_kill_point_is_arm_independent(self):
        # M1 / R:unfair_kill_point — THE FAIRNESS GUARD, made structural. An
        # arm-dependent K would interrupt methods at different amounts of
        # completed work while claiming to be a controlled comparison.
        import inspect
        params = inspect.signature(sample_kill_point).parameters
        assert "arm" not in params, "sample_kill_point can see the arm"
        assert set(params) <= {"wm", "rep", "seed", "lo", "hi"}, params

    def test_kill_point_spans_its_range(self):
        # A constant K would be trivially "fair" and measure one point only.
        seen = {sample_kill_point(wm, rep) for wm in range(1, 11) for rep in range(10)}
        assert len(seen) > 1, f"kill point never varies: {seen}"
        assert all(2 <= k <= 8 for k in seen), seen

    def test_invalid_range_is_rejected(self):
        with pytest.raises(ValueError):
            sample_kill_point(1, 0, lo=0)
        with pytest.raises(ValueError):
            sample_kill_point(1, 0, lo=5, hi=2)


# ── M2 · counting matches the scorer ──────────────────────────────────────────

class TestWriteCounting:
    def test_code_write_counting_matches_the_scorer(self):
        # M2 — the kill trigger and the scorer's edit_pos cut-point MUST share a
        # vocabulary. If they drifted, a run could be killed at a moment the
        # scorer does not consider a write, and nothing else would notice.
        import benchmark.interrupt as interrupt
        import benchmark.score as score
        assert interrupt._WRITE_TOOLS is score._WRITE_TOOLS
        assert interrupt._BASH_WRITE is score._BASH_WRITE

    def test_counts_write_edit_and_bash_writes(self):
        import json
        lines = [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "hi"}]}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Write", "input": {"file_path": "a.py"}}]}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Edit", "input": {"file_path": "a.py"}}]}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash",
                 "input": {"command": "cat > b.py <<'PY'\nx\nPY"}}]}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": "pytest -q"}}]}},
        ]
        text = "\n".join(json.dumps(x) for x in lines)
        assert count_code_writes(text) == 3

    def test_partial_final_line_does_not_crash(self):
        # The transcript is read WHILE being streamed, so the last line is
        # routinely half-written. A crash here would silently disable
        # interruption for that run rather than failing loudly.
        assert count_code_writes('{"type": "assist') == 0
        assert count_code_writes('{"bad json\n{"also bad') == 0


# ── M2 / M3 · the kill is real ────────────────────────────────────────────────

class TestKilling:
    def test_kills_on_the_kth_write(self, tmp_path):
        proc, transcript, _ = _spawn(tmp_path, writes=5)
        try:
            out = watch_and_kill(proc, transcript, k=3, backstop_s=30, poll_s=0.05)
            assert out["fired"] == "kth_write", out
            assert out["writes_seen"] >= 3, out
        finally:
            proc.kill()

    def test_kill_takes_the_whole_process_group(self, tmp_path):
        # M2 — an agent spawns test runners and servers. Killing only the parent
        # leaves them writing into the workspace the resume is about to use.
        proc, transcript, pidfile = _spawn(tmp_path, writes=5)
        try:
            watch_and_kill(proc, transcript, k=2, backstop_s=30, poll_s=0.05)
            child_pid = int(pidfile.read_text())
            deadline = time.monotonic() + 5
            while _alive(child_pid) and time.monotonic() < deadline:
                time.sleep(0.05)
            assert not _alive(child_pid), f"child {child_pid} survived the kill"
        finally:
            proc.kill()

    def test_backstop_kills_a_run_that_never_writes(self, tmp_path):
        # M3 — without this, writing no code buys immunity from the track.
        proc, transcript, _ = _spawn(tmp_path, writes=0)
        try:
            out = watch_and_kill(proc, transcript, k=3, backstop_s=1.0, poll_s=0.05)
            assert out["fired"] == "backstop", out
            assert out["writes_seen"] == 0, out
        finally:
            proc.kill()

    def test_no_kill_when_the_run_finishes_first(self, tmp_path):
        # M6 — "none" is a real outcome to be RECORDED, not retried. Re-running
        # until an interrupt lands would bias the sample toward slow runs.
        proc = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)
        transcript = tmp_path / "empty.jsonl"
        transcript.write_text("", encoding="utf-8")
        out = watch_and_kill(proc, transcript, k=3, backstop_s=30, poll_s=0.05)
        assert out["fired"] == "none", out

    def test_missing_transcript_does_not_crash_the_watcher(self, tmp_path):
        # The transcript may not exist for the first moments of a run.
        proc, _, _ = _spawn(tmp_path, writes=0)
        try:
            out = watch_and_kill(proc, tmp_path / "never.jsonl", k=3,
                                 backstop_s=1.0, poll_s=0.05)
            assert out["fired"] == "backstop", out
        finally:
            proc.kill()


# ── M4 / M5 / M6 · the runner wiring ──────────────────────────────────────────

class TestRunnerWiring:
    def test_uninterrupted_execute_wm_is_unchanged(self):
        # M6 — the guarantee is structural, not reviewed: the default path still
        # goes through _invoke_once, and the streaming path exists only for
        # interruption. A shared code path would make "unchanged" a claim
        # requiring proof on every future edit.
        import inspect

        from benchmark.runner import core
        src = inspect.getsource(core.execute_wm)
        assert "if interrupt is not None:" in src, "interrupt path is not gated"
        gated = src.index("if interrupt is not None:")
        assert "_invoke_interruptible" not in src[:gated], \
            "the streaming path is reachable with interrupt=None"
        assert inspect.signature(core.execute_wm).parameters["interrupt"].default is None

    def test_resume_runs_on_the_same_workspace(self):
        # M4 — the on-disk state is the only carrier, so the resume MUST land in
        # the same directory the interrupted run was building in.
        import inspect

        from benchmark.runner import core
        src = inspect.getsource(core.execute_wm)
        block = src[src.index("if interrupt is not None:"):]
        resume = block[block.index("resume_text"):]
        assert "cwd=workspace_dir" in resume, "resume does not reuse the workspace"

    def test_resume_carries_no_prior_conversation(self):
        # M4 / R:context_carryover — a resume that inherits the conversation
        # measures the agent's MEMORY, not what the method left on disk. The
        # runner passes no conversation-carrying flag anywhere, by design.
        #
        # Docstrings are stripped first: core.py's own prose RECORDS that
        # `--continue` was removed in 2026-07, and a raw text scan reads that
        # removal note as the flag itself. Prose about a flag is not a flag —
        # the same false positive the amb1 contamination scan had to handle.
        import ast
        import inspect

        from benchmark.runner import core
        tree = ast.parse(inspect.getsource(core))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)):
                node.value.value = ""
        code = ast.unparse(tree)
        for flag in ("--continue", "--resume"):
            assert flag not in code, f"runner passes {flag} — conversation carries over"

    def test_resume_prompt_names_no_method_artifact(self):
        # The prompt must not hand one arm its own idiom back. Naming PLAN.md
        # would tell every other arm where ADD keeps its state, and naming none
        # of them is the only symmetric choice.
        from benchmark.runner.core import RESUME_PROMPT
        low = RESUME_PROMPT.lower()
        for token in ("plan.md", "add.py", ".add", "spec.md", "constitution",
                      "todo.md", "tasks.md"):
            assert token not in low, f"resume prompt leaks an arm's idiom: {token}"

    def test_record_carries_the_kill_point(self):
        # M5 — the intended k AND what actually fired both land on the record.
        import inspect

        from benchmark.runner import core
        src = inspect.getsource(core.execute_wm)
        assert 'artifacts["interrupt"]' in src
        assert '"k": int(interrupt["k"])' in src, "the intended kill point is not recorded"


class TestWatcherCannotHang:
    """Found by mutation: deleting the backstop made watch_and_kill loop forever,
    so the suite HUNG rather than failed. A hang in CI is a multi-hour timeout
    instead of a red X — the one failure mode nobody reads."""

    def test_rejects_a_nonpositive_backstop(self, tmp_path):
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                                start_new_session=True)
        try:
            with pytest.raises(ValueError):
                watch_and_kill(proc, tmp_path / "t.jsonl", k=3, backstop_s=0)
        finally:
            proc.kill()

    def test_watcher_always_terminates(self, tmp_path):
        # The circuit breaker, exercised: even with a k that is never reached,
        # the call returns within a bounded time and the process is dead.
        proc, transcript, _ = _spawn(tmp_path, writes=0)
        try:
            started = time.monotonic()
            out = watch_and_kill(proc, transcript, k=999, backstop_s=0.5, poll_s=0.05)
            assert time.monotonic() - started < 20, "watcher did not terminate promptly"
            assert out["fired"] in ("backstop", "ceiling"), out
        finally:
            proc.kill()
