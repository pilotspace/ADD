"""Scenarios: a re-run must not inherit the previous run's transcript, and every
subcommand that touches a runs tree must be able to name which tree.

Live proof 2026-08-10 (3.0 harness validation): a dry run whose stand-in agent
made exactly 8 engine calls scored `engine_calls: 122`. The other 114 were a
July campaign's transcript sitting at the same default path — `run` writes only
to `benchmark/runs/<arm>/wm<n>/` (`--runs-root` existed on `report` alone), and
every transcript write site opens the file with "a". The census was reading two
campaigns as one, complete with the older one's retired verbs.

Two independent holes, so two independent fixes: the transcript is truncated
once per `execute_wm`, and `--runs-root` reaches `run`/`resume`/`score` the same
way it already reaches `report`. Either alone leaves a way to silently blend
runs.
"""
from __future__ import annotations

import json
import pathlib
import sys
import textwrap

import pytest

import benchmark.run as run_mod
from benchmark.arms.loader import Arm
from benchmark.runner import core as core_mod
from benchmark.runner import records as records_mod
from benchmark.runner.core import execute_wm
from benchmark.score import _engine_call_census

STALE = "\n".join(
    json.dumps({"type": "tool_use", "name": "Bash",
                "input": {"command": f"python3 .add/tooling/cli.py status # july {i}"}})
    for i in range(114)
)


def _arm(name: str = "fake-arm") -> Arm:
    return Arm(name=name, setup_steps=[], prompt_wrapper="raw", pin="",
               same_model=True, token_ceiling=200000, turn_ceiling=60)


def _script(tmp_path: pathlib.Path, name: str, body: str) -> pathlib.Path:
    path = tmp_path / name
    path.write_text(textwrap.dedent(body))
    path.chmod(0o755)
    return path


AGENT_TWO_CALLS = """
    #!/usr/bin/env python3
    import json, sys
    for verb in ("status", "gate"):
        print(json.dumps({"type": "tool_use", "name": "Bash",
                          "input": {"command": "python3 .add/tooling/cli.py " + verb}}))
    print(json.dumps({
        "type": "result", "total_cost_usd": 0.0,
        "usage": {"input_tokens": 1, "output_tokens": 1,
                  "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
    }))
    sys.exit(0)
"""


def test_a_prior_transcript_does_not_leak_into_a_fresh_run(tmp_path):
    """The 122-vs-8 bug, at the census that reported it."""
    runs_root = tmp_path / "runs"
    wm_dir = runs_root / "fake-arm" / "wm1"
    wm_dir.mkdir(parents=True)
    transcript = wm_dir / "transcript.jsonl"
    transcript.write_text(STALE + "\n")

    record = execute_wm(_arm(), 1,
                        agent_cmd=[sys.executable, str(_script(tmp_path, "a.py", AGENT_TWO_CALLS))],
                        timeout_s=30, retries=1, runs_root=runs_root)

    assert record.status == "done"
    assert "july" not in transcript.read_text(), "the prior run's transcript survived into this one"
    assert _engine_call_census(transcript) == 2


def test_both_attempts_of_one_run_are_kept(tmp_path):
    """Truncate once per RUN, not once per attempt — a retried run's earlier
    attempts are part of what that run did and must stay countable."""
    counter = tmp_path / "n.txt"
    script = _script(tmp_path, "retry.py", f"""
        #!/usr/bin/env python3
        import json, pathlib, sys
        c = pathlib.Path({str(counter)!r})
        n = int(c.read_text()) + 1 if c.exists() else 1
        c.write_text(str(n))
        print(json.dumps({{"type": "tool_use", "name": "Bash",
                          "input": {{"command": "python3 .add/tooling/cli.py status # try %d" % n}}}}))
        if n == 1:
            sys.exit(1)
        print(json.dumps({{
            "type": "result", "total_cost_usd": 0.0,
            "usage": {{"input_tokens": 1, "output_tokens": 1,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}},
        }}))
        sys.exit(0)
    """)
    runs_root = tmp_path / "runs"
    record = execute_wm(_arm(), 1, agent_cmd=[sys.executable, str(script)],
                        timeout_s=30, retries=1, runs_root=runs_root)

    assert record.status == "done"
    text = (runs_root / "fake-arm" / "wm1" / "transcript.jsonl").read_text()
    assert "try 1" in text and "try 2" in text


def test_setup_output_survives_the_truncation(tmp_path):
    """Setup steps log to the same transcript, so the truncation must land
    BEFORE them — truncating later would erase the install log the record's
    `attempts` artifact points at."""
    runs_root = tmp_path / "runs"
    arm = Arm(name="fake-arm", setup_steps=["echo SETUP-RAN"], prompt_wrapper="raw",
              pin="", same_model=True, token_ceiling=200000, turn_ceiling=60)
    execute_wm(arm, 1,
               agent_cmd=[sys.executable, str(_script(tmp_path, "a.py", AGENT_TWO_CALLS))],
               timeout_s=30, retries=1, runs_root=runs_root)
    assert "SETUP-RAN" in (runs_root / "fake-arm" / "wm1" / "transcript.jsonl").read_text()


# --- the CLI half: every runs-tree subcommand can name its tree -------------


@pytest.fixture
def spy(monkeypatch):
    """Capture the runs_root each subcommand hands down, without running one."""
    seen: dict = {}

    class _Rec:
        status = "done"

        def to_json(self):
            return "{}"

    def fake_execute(arm, wm, **kw):
        seen.setdefault("execute", []).append(kw.get("runs_root"))
        return _Rec()

    def fake_score(arm, wm, **kw):
        seen["score"] = kw.get("runs_root")
        return _Rec()

    monkeypatch.setattr(run_mod, "execute_wm", fake_execute)
    monkeypatch.setattr(run_mod, "score_record", fake_score)
    monkeypatch.setattr(run_mod, "resolve_setup_steps", lambda arm, root: arm)
    return seen


def test_run_sends_the_named_runs_root_down(tmp_path, spy):
    assert run_mod.main(["run", "--arm", "add", "--wm", "1",
                         "--runs-root", str(tmp_path / "campaign")]) == 0
    assert spy["execute"] == [pathlib.Path(tmp_path / "campaign")]


def test_score_sends_the_named_runs_root_down(tmp_path, spy):
    assert run_mod.main(["score", "--arm", "add", "--wm", "1",
                         "--runs-root", str(tmp_path / "campaign")]) == 0
    assert spy["score"] == pathlib.Path(tmp_path / "campaign")


def test_resume_reads_and_writes_the_named_runs_root(tmp_path, spy, monkeypatch):
    """Both halves: the resume POINT is found in the named tree, and the runs
    it then drives are written there. A resume that reads one tree and writes
    another is worse than no --runs-root at all."""
    asked: dict = {}

    def fake_find(arm_name, **kw):
        asked["runs_root"] = kw.get("runs_root")
        return 6

    monkeypatch.setattr(run_mod, "find_resume_point", fake_find)
    campaign = tmp_path / "campaign"
    assert run_mod.main(["resume", "--arm", "add", "--runs-root", str(campaign)]) == 0
    assert asked["runs_root"] == pathlib.Path(campaign)
    assert spy["execute"] == [pathlib.Path(campaign)]


def test_omitting_runs_root_keeps_the_default(tmp_path, spy):
    """None, not a resolved path — the default lives in ONE place
    (DEFAULT_RUNS_ROOT), and tests monkeypatch it there."""
    assert run_mod.main(["run", "--arm", "add", "--wm", "1"]) == 0
    assert spy["execute"] == [None]
