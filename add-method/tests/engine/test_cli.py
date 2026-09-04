"""The real CLI (e11): every referenced verb dispatches, and exit codes tell the truth.

0 success · 1 an engine refusal · 2 a usage error. The last test is the anti-seam: every verb the
CLI advertises maps to a real engine function, so `add <verb>` can never promise a function that
isn't there (the failure mode the spike census was built to expose, now guarded at the CLI).
"""
import argparse
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
import cli  # noqa: E402

# Verbs the CLI wires in v1 — every one has a real engine function.
WIRED = {"init", "status", "new", "freeze", "run", "gate", "done", "brief", "learn",
         "milestone-done", "deltas", "fold", "reopen", "milestone-archive", "doctor", "wave", "join",
         "advise", "locate", "todo", "upgrade", "replan", "check", "interview", "search"}


def _run(root, *argv):
    return cli.main(["--root", str(root), *argv])


def test_init_new_status_dispatch(tmp_path):
    assert _run(tmp_path, "init", "T", "--profile", "code") == 0
    assert _run(tmp_path, "new", "Task", "add-thing", "--title", "Add thing") == 0
    assert _run(tmp_path, "status") == 0
    assert (tmp_path / "tasks" / "add-thing.md").is_file()


def test_run_timeout_flag_reaches_the_engine(tmp_path, monkeypatch):
    """Receipt-cost follow-up (PR #197 review) — a receipt command wrapping a slow suite (a
    production build, cost-tuned hashing) can exceed the silent 900s default; the ceiling must
    be settable from the CLI, and the default must hold when the flag is absent."""
    _run(tmp_path, "init", "T")
    _run(tmp_path, "new", "Task", "slow", "--title", "slow")
    seen = {}

    def fake(root, cid, command, cwd=None, timeout=add.RUN_TIMEOUT, junit=None):
        seen["timeout"] = timeout
        return {"note": "ok", "receipt": {"exit": 0}}

    monkeypatch.setattr(cli.add, "run", fake)
    assert _run(tmp_path, "run", "slow", "--timeout", "1800", "--", "echo") == 0
    assert seen["timeout"] == 1800
    assert _run(tmp_path, "run", "slow", "--", "echo") == 0
    assert seen["timeout"] == add.RUN_TIMEOUT


def test_duplicate_slug_is_an_engine_refusal(tmp_path):
    _run(tmp_path, "init", "T")
    assert _run(tmp_path, "new", "Task", "dup", "--title", "one") == 0
    assert _run(tmp_path, "new", "Task", "dup", "--title", "two") == 1, "a colliding slug is exit 1"


def test_learn_requires_evidence(tmp_path):
    _run(tmp_path, "init", "T")
    assert _run(tmp_path, "learn", "add", "a lesson with no evidence") == 1, "evidence-less learn refuses"
    assert _run(tmp_path, "learn", "add", "a grounded lesson", "--evidence", "runs/1.md") == 0


def test_milestone_done_goal_gate(tmp_path):
    _run(tmp_path, "init", "T")
    add.new(tmp_path, "Milestone", "m1", title="slice")
    path = tmp_path / "milestones" / "m1.md"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(## EXIT\n).*?(\n## )", r"\1- [ ] not yet\2", text, flags=re.DOTALL)
    text = re.sub(r"(?m)^why:.*$", "why: the slice this milestone exists to ship", text)  # required why:
    path.write_text(text, encoding="utf-8")
    assert _run(tmp_path, "milestone-done", "m1") == 1, "an unchecked goal box refuses (exit 1)"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- [ ] not yet", "- [x] done"), encoding="utf-8")
    assert _run(tmp_path, "milestone-done", "m1") == 0, "all boxes checked closes (exit 0)"


def test_advise_cli_dispatches(tmp_path):
    """covers: M1 — `add advise <slug> --persona <p>` records (0) or refuses (1)."""
    _run(tmp_path, "init", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "sec", title="sec", milestone="m", sensitivity="security", scope=["a.py"])
    add.new(tmp_path, "Persona", "sec-rev", title="security lens")
    assert _run(tmp_path, "advise", "sec", "--persona", "sec-rev") == 0
    fm = add.read(tmp_path / "tasks" / "sec.md", "T2")["fm"]
    assert fm.get("advised_by") == "sec-rev"
    assert _run(tmp_path, "advise", "sec", "--persona", "ghost") == 1, "an unknown persona is exit 1"


def test_unknown_verb_is_usage_error(tmp_path):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--root", str(tmp_path), "frobnicate"])
    assert exc.value.code == 2, "an unknown verb is a usage error (exit 2)"


def test_every_advertised_verb_maps_to_a_real_engine_function():
    parser = cli.build_parser()
    subs = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)][0]
    advertised = set(subs.choices)
    assert advertised == WIRED, f"CLI verb set drifted: {advertised ^ WIRED}"
    for verb in WIRED:
        fn = verb.replace("-", "_")
        assert hasattr(add, fn), f"CLI advertises `{verb}` but add.py has no `{fn}` function"
