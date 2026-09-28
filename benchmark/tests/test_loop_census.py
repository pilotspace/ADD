"""loop census — did an ADD run actually walk the loop? (add-4 · add-3x pilot)

ADD 4.0 has no engine, so the 3.x engine-call census reads 0 on a perfectly
disciplined 4.0 run. What a 4.0 run leaves instead is WORKSPACE STATE: task
files, `freeze(<slug>)` / `verify(<slug>)` commits, a verdict in `## EVIDENCE`.

The trap this census exists to refuse is the vacuous zero. A benchmark workspace
lives under `benchmark/runs/`, INSIDE the harness's own git repo, so a census
that asks git "what commits are there?" from a workspace that was never given
its own repo reads the PARENT repo's history — or, pointed at a wrong path,
finds nothing and reports a clean 0. Both must come back `measured: False`
with a reason, never a count.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from benchmark import loop_census as lc


# ---------------------------------------------------------------- fixtures


def _git(ws: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ws), *args], check=True, capture_output=True, text=True
    ).stdout


def _repo(ws: pathlib.Path) -> pathlib.Path:
    ws.mkdir(parents=True, exist_ok=True)
    _git(ws, "init", "-q")
    _git(ws, "config", "user.name", "t")
    _git(ws, "config", "user.email", "t@example.invalid")
    _git(ws, "config", "commit.gpgsign", "false")
    (ws / "README.md").write_text("base\n")
    _git(ws, "add", "-A")
    _git(ws, "commit", "-q", "-m", "chore(bench): workspace baseline")
    return ws


def _commit(ws: pathlib.Path, msg: str) -> None:
    _git(ws, "add", "-A")
    _git(ws, "commit", "-q", "--allow-empty", "-m", msg)


TASK = """---
type: Task
title: slugify
status: {status}
---
## CARD
goal: slugify text

## RULES
- M1 lowercases

## CHECKS
- C1 covers: M1 · acceptance · tests/test_slug.py::test_lower

## EVIDENCE
{evidence}
"""


def _full_loop(ws: pathlib.Path, verdict: str = "PASS") -> None:
    """The 4.0 task loop, exactly as SKILL.md spells it: seal, build, verify."""
    (ws / ".add" / "tasks").mkdir(parents=True, exist_ok=True)
    (ws / "tests").mkdir(exist_ok=True)
    (ws / ".add" / "tasks" / "slugify.md").write_text(TASK.format(status="build", evidence=""))
    (ws / "tests" / "test_slug.py").write_text("def test_lower():\n    assert False\n")
    _commit(ws, "freeze(slugify): slugify text")
    (ws / "app.py").write_text("x = 1\n")
    _commit(ws, "feat(app): slugify")
    (ws / ".add" / "tasks" / "slugify.md").write_text(
        TASK.format(status="done", evidence=f"freeze: abc · head: def\nverdict: {verdict}"))
    _commit(ws, f"verify(slugify): {verdict}")


# ------------------------------------------------- the vacuous-zero guard


class TestUnmeasurableIsNeverZero:
    def test_missing_workspace_is_unmeasurable(self, tmp_path):
        out = lc.census(tmp_path / "nope")
        assert out["measured"] is False
        assert "missing" in out["reason"]
        assert "tasks" not in out, "an unmeasurable census must carry no counts at all"

    def test_workspace_without_its_own_repo_is_unmeasurable_even_inside_a_repo(self, tmp_path):
        """covers: R:VACUOUS — the exact benchmark shape: runs/ nested in the harness repo.

        git would happily answer from the PARENT repo here. A census that trusted it
        would report the harness's own freeze commits as the arm's adherence.
        """
        parent = _repo(tmp_path / "harness")
        _commit(parent, "freeze(parent-task): not the arm's")
        ws = parent / "runs" / "add-4" / "wm1" / "workspace"
        ws.mkdir(parents=True)
        out = lc.census(ws)
        assert out["measured"] is False
        assert ".git" in out["reason"]

    def test_a_dotgit_that_is_not_the_toplevel_is_refused(self, tmp_path, monkeypatch):
        """A stray/empty `.git` entry must not pass the guard by mere existence."""
        parent = _repo(tmp_path / "harness")
        ws = parent / "ws"
        (ws / ".git").mkdir(parents=True)          # an empty dir: not a repository
        out = lc.census(ws)
        assert out["measured"] is False

    def test_a_true_zero_is_measured(self, tmp_path):
        ws = _repo(tmp_path / "ws")
        out = lc.census(ws)
        assert out["measured"] is True
        assert out["tasks"] == 0
        assert out["freeze_commits"] == 0 and out["verify_commits"] == 0
        assert out["commits"] == 1                  # the baseline — proves git was READ


# --------------------------------------------------------- the counts


class TestLoopCounts:
    def test_counts_a_full_4_0_loop(self, tmp_path):
        ws = _repo(tmp_path / "ws")
        _full_loop(ws)
        out = lc.census(ws)
        assert out["measured"] is True
        assert out["tasks"] == 1
        assert out["freeze_commits"] == 1
        assert out["verify_commits"] == 1
        assert out["verify_verdicts"] == {"PASS": 1}
        assert out["evidence_verdicts"] == {"PASS": 1}
        assert out["sealed_slugs"] == ["slugify"]
        assert out["seals_intact"] == 1 and out["seals_broken"] == []

    def test_a_sealed_check_edited_during_build_is_a_broken_seal(self, tmp_path):
        ws = _repo(tmp_path / "ws")
        (ws / ".add" / "tasks").mkdir(parents=True)
        (ws / "tests").mkdir()
        (ws / ".add" / "tasks" / "slugify.md").write_text(TASK.format(status="build", evidence=""))
        (ws / "tests" / "test_slug.py").write_text("def test_lower():\n    assert False\n")
        _commit(ws, "freeze(slugify): slugify text")
        (ws / "tests" / "test_slug.py").write_text("def test_lower():\n    assert True\n")
        _commit(ws, "feat(app): weaken the sealed check")
        _commit(ws, "verify(slugify): PASS")
        out = lc.census(ws)
        assert out["seals_broken"] == ["slugify"]
        assert out["seals_intact"] == 0

    def test_a_refreeze_moves_the_seal(self, tmp_path):
        ws = _repo(tmp_path / "ws")
        (ws / ".add" / "tasks").mkdir(parents=True)
        (ws / "tests").mkdir()
        (ws / ".add" / "tasks" / "slugify.md").write_text(TASK.format(status="build", evidence=""))
        (ws / "tests" / "test_slug.py").write_text("def test_lower():\n    assert False\n")
        _commit(ws, "freeze(slugify): slugify text")
        (ws / "tests" / "test_slug.py").write_text("def test_lower():\n    assert 1 == 1\n")
        _commit(ws, "refreeze(slugify): check aimed at the wrong thing")
        _commit(ws, "verify(slugify): PASS")
        out = lc.census(ws)
        assert out["freeze_commits"] == 1 and out["refreeze_commits"] == 1
        assert out["seals_intact"] == 1 and out["seals_broken"] == []

    @pytest.mark.parametrize("line", [
        "verdict: <PASS | RISK-ACCEPTED | HARD-STOP>",     # 4.0 template
        "gate: <PASS | RISK-ACCEPTED | HARD-STOP>",        # 3.7 template
        "verdict: pending",
    ])
    def test_a_template_verdict_is_not_a_verdict(self, tmp_path, line):
        ws = _repo(tmp_path / "ws")
        (ws / ".add" / "tasks").mkdir(parents=True)
        (ws / ".add" / "tasks" / "t.md").write_text(TASK.format(status="build", evidence=line))
        assert lc.census(ws)["evidence_verdicts"] == {}

    def test_a_verdict_outside_evidence_does_not_count(self, tmp_path):
        ws = _repo(tmp_path / "ws")
        (ws / ".add" / "tasks").mkdir(parents=True)
        text = TASK.format(status="build", evidence="").replace("## CARD", "## CARD\nverdict: PASS")
        (ws / ".add" / "tasks" / "t.md").write_text(text)
        assert lc.census(ws)["evidence_verdicts"] == {}

    def test_the_3_7_gate_line_counts(self, tmp_path):
        ws = _repo(tmp_path / "ws")
        (ws / ".add" / "tasks").mkdir(parents=True)
        (ws / ".add" / "tasks" / "t.md").write_text(TASK.format(status="done", evidence="gate: PASS"))
        assert lc.census(ws)["evidence_verdicts"] == {"PASS": 1}

    def test_subdirectory_files_are_not_tasks(self, tmp_path):
        """3.7 writes run receipts under `.add/tasks/<slug>.d/runs/`; they are not tasks."""
        ws = _repo(tmp_path / "ws")
        (ws / ".add" / "tasks" / "t.d" / "runs").mkdir(parents=True)
        (ws / ".add" / "tasks" / "t.md").write_text(TASK.format(status="build", evidence=""))
        (ws / ".add" / "tasks" / "t.d" / "runs" / "1.md").write_text("receipt")
        assert lc.census(ws)["tasks"] == 1


# ------------------------------------------------- red before the seal


def _tool_use(tid: str, command: str) -> str:
    return json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": tid, "name": "Bash", "input": {"command": command}}]}})


def _tool_result(tid: str, text: str, is_error: bool = False) -> str:
    return json.dumps({"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": tid, "content": text, "is_error": is_error}]}})


class TestRedFirst:
    def test_failing_run_before_the_4_0_seal(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text("\n".join([
            _tool_use("a", "python3 -m pytest -q tests/test_slug.py 2>&1 | tail -5"),
            _tool_result("a", "F\n1 failed in 0.01s"),        # piped: is_error stays False
            _tool_use("b", 'git add -A && git commit -m "freeze(slugify): slugify text"'),
            _tool_result("b", "[main 1a2b3c] freeze(slugify)"),
        ]) + "\n")
        red = lc.red_first(t)
        assert red["seal_seen"] is True
        assert red["failing_runs_before_seal"] == 1
        assert red["red_first"] is True

    def test_a_colored_unittest_failure_is_red(self, tmp_path):
        # Real pilot output (add-4 × amb1): unittest wraps markers in ANSI color codes, which broke
        # both `FAILED (failures=` and the `\bAssertionError\b` boundary (the code ends in `m`).
        colored = ("\x1b[1;35mAssertionError\x1b[0m: \x1b[35mserver did not start on $PORT\x1b[0m\n"
                   "Ran 29 tests in 1.741s\n\n\x1b[1;31mFAILED\x1b[0m (\x1b[1;31mfailures=29\x1b[0m)")
        t = tmp_path / "transcript.jsonl"
        t.write_text("\n".join([
            _tool_use("a", "python3 -m unittest discover -s tests"),
            _tool_result("a", colored),
            _tool_use("b", 'git commit -m "freeze(booking): booking service"'),
            _tool_result("b", "[main 9037bb9] freeze(booking)"),
        ]) + "\n")
        red = lc.red_first(t)
        assert red["failing_runs_before_seal"] == 1
        assert red["red_first"] is True

    def test_an_import_error_is_not_red_for_the_right_reason(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text("\n".join([
            _tool_use("a", "pytest -q"),
            _tool_result("a", "ERROR tests/test_slug.py\nModuleNotFoundError: No module named 'app'\n"
                              "1 error in 0.02s", is_error=True),
            _tool_use("b", "git commit -qm 'freeze(slugify): x'"),
            _tool_result("b", "ok"),
        ]) + "\n")
        red = lc.red_first(t)
        assert red["failing_runs_before_seal"] == 0
        assert red["error_runs_before_seal"] == 1
        assert red["red_first"] is False

    def test_the_3x_engine_freeze_is_a_seal(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text("\n".join([
            _tool_use("a", ".venv/bin/python -m pytest tests -q"),
            _tool_result("a", "2 failed, 1 passed in 0.1s", is_error=True),
            _tool_use("b", "python3 .add/tooling/cli.py freeze slugify --by bench --authority human"),
            _tool_result("b", "freeze recorded"),
        ]) + "\n")
        assert lc.red_first(t)["red_first"] is True

    def test_red_only_after_the_seal_does_not_count(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text("\n".join([
            _tool_use("b", "git commit -m 'freeze(slugify): x'"),
            _tool_result("b", "ok"),
            _tool_use("a", "pytest -q"),
            _tool_result("a", "1 failed in 0.01s"),
        ]) + "\n")
        red = lc.red_first(t)
        assert red["failing_runs_before_seal"] == 0 and red["red_first"] is False

    def test_no_seal_is_undetectable_not_false(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text(_tool_use("a", "pytest -q") + "\n" + _tool_result("a", "1 failed") + "\n")
        red = lc.red_first(t)
        assert red["seal_seen"] is False
        assert red["red_first"] is None

    def test_missing_transcript_is_undetectable(self, tmp_path):
        red = lc.red_first(tmp_path / "nope.jsonl")
        assert red["red_first"] is None and "missing" in red["reason"]

    def test_census_carries_red_first_when_given_a_transcript(self, tmp_path):
        ws = _repo(tmp_path / "ws")
        t = tmp_path / "transcript.jsonl"
        t.write_text(_tool_use("b", "git commit -m 'freeze(x): y'") + "\n")
        out = lc.census(ws, t)
        assert out["red_first"]["seal_seen"] is True


# ----------------------------------------------- wired into score_record


def _scorable(tmp_path: pathlib.Path, arm: str) -> pathlib.Path:
    runs_root = tmp_path / "runs"
    wm_dir = runs_root / arm / "wm1"
    ws = _repo(wm_dir / "workspace")
    _full_loop(ws)
    (wm_dir / "transcript.jsonl").write_text("")
    (wm_dir / "oracle_report.json").write_text(json.dumps({"isolation_clean": True}))
    (wm_dir / "record.json").write_text(json.dumps({
        "arm": arm, "wm": 1, "rep": 0, "status": "done",
        "metrics": {"regression_rate": 0.0, "requirement_coverage": 0.0,
                    "oracle_pass_rate": 0.0, "tokens_total": 1.0, "cost_usd": 0.1,
                    "context_rot_slope": 0.0, "time_to_first_edit": 1.0},
        "artifacts": {"workspace": str(ws), "transcript": str(wm_dir / "transcript.jsonl"),
                      "oracle_report": str(wm_dir / "oracle_report.json")},
    }))
    return runs_root


@pytest.mark.parametrize("arm", ["add-4", "add-3x"])
def test_score_record_writes_the_loop_census_for_the_pilot_arms(tmp_path, monkeypatch, arm):
    from benchmark import score as score_mod

    monkeypatch.setattr(score_mod, "compute_coverage_detail",
                        lambda ws, wm, family="wm": [{"id": "a", "covered": True}])
    monkeypatch.setattr(score_mod, "compute_oracle_pass_rate", lambda ws, wm, family="wm": 1.0)
    runs_root = _scorable(tmp_path, arm)
    scored = score_mod.score_record(arm, 1, runs_root=runs_root)
    census = json.loads(scored.artifacts["loop_census"])
    assert census["measured"] is True and census["freeze_commits"] == 1
    assert "engine_calls" in scored.artifacts, "the 3.x engine census must survive beside it"


def test_score_record_leaves_other_arms_alone(tmp_path, monkeypatch):
    from benchmark import score as score_mod

    monkeypatch.setattr(score_mod, "compute_coverage_detail",
                        lambda ws, wm, family="wm": [{"id": "a", "covered": True}])
    monkeypatch.setattr(score_mod, "compute_oracle_pass_rate", lambda ws, wm, family="wm": 1.0)
    runs_root = _scorable(tmp_path, "vanilla")
    scored = score_mod.score_record("vanilla", 1, runs_root=runs_root)
    assert "loop_census" not in scored.artifacts
