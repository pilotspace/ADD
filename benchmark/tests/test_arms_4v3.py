"""The ADD 4.0 vs 3.7.0 head-to-head pilot: arms `add-4` and `add-3x`.

What this file binds, and why each matters to the comparison:

* both arms load, and are identical on everything that is not the method — the
  fairness fields, the workspace git baseline, the model the runner pins;
* `add-4` installs THIS worktree's 4.0 with flags the 4.0 CLI accepts (it exits 2
  on `--force` · `--stage` · `--no-skill`), `add-3x` installs the pinned 3.7.0 and
  refuses to install anything else;
* the retired `add` arm fails LOUD before any workspace exists, instead of
  spending a setup on an installer that exits 2 — and archived `add` records stay
  scoreable;
* the two prompt wrappers are the same instruction in two dialects — matched in
  length and in every clause that is not the method's own mechanics.
"""
from __future__ import annotations

import pathlib
import re
import shlex
import subprocess
import sys

import pytest

from benchmark import pilot as pilot_mod
from benchmark.arms.loader import ARM_NAMES, load_arm
from benchmark.runner.core import _wrap_prompt
from benchmark.schema.run_record import BenchError

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ARMS_DIR = REPO_ROOT / "benchmark" / "arms"
ADD37_SHA = "d0af5bb3793e6033394127f0eb7ecd81aca4fd5f"
ADD37_WORKTREE = pathlib.Path(
    "/Users/tindang/workspaces/tind-repo/AIDD-Book/.claude/worktrees/release-3-7")


def _argv(step: str) -> list[str]:
    """How the runner reads a setup line: strip an inline `#` comment, then shlex."""
    return shlex.split(step.split("#", 1)[0].strip())


def _steps(name: str) -> list[list[str]]:
    return [a for a in (_argv(s) for s in load_arm(ARMS_DIR / f"{name}.toml").setup_steps) if a]


# ------------------------------------------------------------------ arms


def test_both_pilot_arms_are_registered_and_load():
    for name in ("add-4", "add-3x"):
        assert name in ARM_NAMES
        assert load_arm(ARMS_DIR / f"{name}.toml").name == name


def test_the_pilot_arms_differ_only_in_the_method():
    a4, a3 = (load_arm(ARMS_DIR / f"{n}.toml") for n in ("add-4", "add-3x"))
    assert (a4.same_model, a4.token_ceiling, a4.turn_ceiling) == \
        (a3.same_model, a3.token_ceiling, a3.turn_ceiling)
    # the SAME workspace git baseline, as the LAST step, in both
    assert _steps("add-4")[-1] == _steps("add-3x")[-1]
    assert _steps("add-4")[-1][-1].endswith("benchmark/arms/workspace_git.py")


def test_add4_installs_this_worktrees_4_0_with_flags_4_0_accepts():
    steps = _steps("add-4")
    install = next(s for s in steps if s[:3] == ["uv", "pip", "install"])
    assert "{REPO_ROOT}/add-method" in install
    init = next(s for s in steps if s[0].endswith("pilotspace-add"))
    assert not {"--force", "--stage", "--no-skill"} & set(init), \
        f"the 4.0 installer exits 2 on these flags: {init}"
    assert load_arm(ARMS_DIR / "add-4.toml").prompt_wrapper == "add-skill"


def test_add3x_installs_only_the_pinned_3_7_0():
    arm = load_arm(ARMS_DIR / "add-3x.toml")
    assert arm.prompt_wrapper == "add-loop"
    assert ADD37_SHA[:8] in arm.pin and "3.7.0" in arm.pin
    steps = _steps("add-3x")
    pin_i = next(i for i, s in enumerate(steps) if s[-2:] == [str(ADD37_WORKTREE), ADD37_SHA]
                 and s[-3].endswith("benchmark/arms/verify_pin.py"))
    install_i = next(i for i, s in enumerate(steps) if s[:3] == ["uv", "pip", "install"])
    assert pin_i < install_i, "the pin must be checked BEFORE anything is installed from it"
    assert str(ADD37_WORKTREE / "add-method") in steps[install_i]
    assert "{REPO_ROOT}/add-method" not in " ".join(steps[install_i]), \
        "the control arm must never install the branch under test"


# ---------------------------------------------------------- retired add


def test_the_add_arm_is_retired_with_a_pointer():
    arm = load_arm(ARMS_DIR / "add.toml")
    assert arm.retired and "add-4" in arm.retired and "add-3x" in arm.retired


def test_other_arms_are_not_retired():
    for name in ARM_NAMES:
        if name != "add":
            assert load_arm(ARMS_DIR / f"{name}.toml").retired == "", name


def _never_execute(*args, **kwargs):
    # Belt AND braces. The first draft of these tests passed no agent_cmd, so before the
    # refusal existed run_pilot fell through to the REAL `claude -p` and spent live tokens
    # on `vanilla` (2026-09-28, ~$0.9). A refusal test must be unable to reach an agent.
    raise AssertionError("execute_wm reached — the refusal did not happen first")


def test_pilot_refuses_a_retired_arm_before_any_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot_mod, "execute_wm", _never_execute)
    runs_root = tmp_path / "runs"
    with pytest.raises(BenchError, match="retired_arm"):
        pilot_mod.run_pilot(arms=["vanilla", "add"], runs_root=runs_root, repo_root=REPO_ROOT,
                            agent_cmd=[sys.executable, "-c", "raise SystemExit(3)"])
    assert not runs_root.exists(), "a refused pilot must not have touched any arm's workspace"


def test_run_cli_refuses_a_retired_arm(tmp_path, capsys, monkeypatch):
    import benchmark.run as run_cli

    monkeypatch.setattr(run_cli, "execute_wm", _never_execute)
    rc = run_cli.main(["run", "--arm", "add", "--wm", "1", "--runs-root", str(tmp_path / "r")])
    assert rc == 2
    assert "retired_arm" in capsys.readouterr().err
    assert not (tmp_path / "r").exists()


def test_archived_add_records_stay_scoreable():
    assert "add" in ARM_NAMES   # score/report gate on ARM_NAMES; history must stay readable


# ---------------------------------------------------------------- pin


def test_add4_pin_resolves_to_the_repo_head():
    from benchmark.runner.pin import resolve_pin

    sha = resolve_pin(load_arm(ARMS_DIR / "add-4.toml").pin, "add-4")
    assert re.fullmatch(r"[0-9a-f]{40}", sha), sha


# ------------------------------------------------------------ wrappers


def test_add_skill_points_at_the_skill_file_not_a_cli():
    out = _wrap_prompt("Build the thing.", "add-skill")
    assert out.endswith("Build the thing.")
    assert ".claude/skills/add/SKILL.md" in out
    assert "cli.py" not in out and ".add/tooling" not in out, "4.0 has no engine to call"
    for token in ("freeze(<slug>)", "verify(<slug>)", "## EVIDENCE", "git diff"):
        assert token in out, token


def test_both_wrappers_carry_the_same_non_method_clauses():
    """covers: fairness — what is not the method must be the same words in both."""
    loop = _wrap_prompt("X", "add-loop").lower()
    skill = _wrap_prompt("X", "add-skill").lower()
    for clause in (
        "drive this repo's add loop for the whole job",
        "headless run with no human available",
        "proxy authority",
        "never end the run waiting for a human reply",
        "the job is done only when the app meets the requirements",
        "cleared, fully-specified benchmark task",
        "one-pass walk",
        "the floor never bends",
        "never skip contract, tests, build, or verify",
        "out of scope for the benchmark",
    ):
        assert clause in loop, f"add-loop lost: {clause!r}"
        assert clause in skill, f"add-skill lacks: {clause!r}"


def test_the_wrappers_are_matched_in_length():
    """covers: fairness — the comparison must measure the method, not prompt pressure."""
    loop = _wrap_prompt("", "add-loop")
    skill = _wrap_prompt("", "add-skill")
    ratio = len(skill) / len(loop)
    assert 0.85 <= ratio <= 1.15, f"add-skill is {ratio:.2f}x add-loop ({len(skill)} vs {len(loop)} chars)"


def test_add_loop_names_the_3_7_brief_step():
    """3.7 refuses `gate` with R:UNBRIEFED unless `brief` entered the build — measured
    2026-09-28 by walking the wrapper's verbs against the pinned 3.7.0 engine."""
    out = _wrap_prompt("X", "add-loop")
    assert "python3 .add/tooling/cli.py brief <slug>" in out


# ------------------------------------------------------- setup helpers


def _git(ws: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(ws), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


HELPERS = REPO_ROOT / "benchmark" / "arms"


def test_workspace_git_gives_a_nested_workspace_its_own_repo(tmp_path):
    """covers: the benchmark shape — runs/ lives INSIDE the harness repo, so without
    its own repo every `git commit` an arm makes lands in the harness's history."""
    parent = tmp_path / "harness"
    parent.mkdir()
    _git(parent, "init", "-q")
    ws = parent / "runs" / "add-4" / "wm1" / "workspace"
    (ws / ".venv").mkdir(parents=True)
    (ws / ".venv" / "junk").write_text("x")
    (ws / "CLAUDE.md").write_text("hi\n")
    rc = subprocess.run([sys.executable, str(HELPERS / "workspace_git.py")], cwd=ws).returncode
    assert rc == 0
    assert pathlib.Path(_git(ws, "rev-parse", "--show-toplevel")).resolve() == ws.resolve()
    assert _git(ws, "log", "--format=%s") == "chore(bench): workspace baseline"
    assert ".venv" not in _git(ws, "ls-files")
    assert _git(ws, "config", "--local", "commit.gpgsign") == "false"
    assert _git(ws, "config", "--local", "user.name")
    # idempotent: a second run on a clean tree adds no commit
    assert subprocess.run([sys.executable, str(HELPERS / "workspace_git.py")], cwd=ws).returncode == 0
    assert _git(ws, "rev-list", "--count", "HEAD") == "1"


def test_verify_pin_accepts_the_pinned_head_and_refuses_another(tmp_path):
    repo = tmp_path / "wt"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@e.invalid", "-c", "commit.gpgsign=false",
         "commit", "-q", "--allow-empty", "-m", "one")
    head = _git(repo, "rev-parse", "HEAD")
    script = str(HELPERS / "verify_pin.py")
    ok = subprocess.run([sys.executable, script, str(repo), head], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    bad = subprocess.run([sys.executable, script, str(repo), "0" * 40], capture_output=True, text=True)
    assert bad.returncode == 1 and "pin mismatch" in (bad.stdout + bad.stderr)
    gone = subprocess.run([sys.executable, script, str(tmp_path / "nope"), head],
                          capture_output=True, text=True)
    assert gone.returncode == 1


def test_verify_pin_reads_a_linked_worktree(tmp_path):
    """The control arm installs from a `git worktree` — a `.git` FILE, not a dir."""
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "-c", "user.name=t", "-c", "user.email=t@e.invalid", "-c", "commit.gpgsign=false",
         "commit", "-q", "--allow-empty", "-m", "one")
    _git(main, "branch", "rel")
    _git(main, "worktree", "add", "-q", str(tmp_path / "wt"), "rel")
    head = _git(tmp_path / "wt", "rev-parse", "HEAD")
    out = subprocess.run([sys.executable, str(HELPERS / "verify_pin.py"), str(tmp_path / "wt"), head],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


def test_the_real_3_7_worktree_is_at_its_pin():
    if not ADD37_WORKTREE.exists():
        pytest.skip(f"3.7.0 worktree absent at {ADD37_WORKTREE} — the add-3x arm cannot run here")
    out = subprocess.run([sys.executable, str(HELPERS / "verify_pin.py"), str(ADD37_WORKTREE), ADD37_SHA],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


# -------------------------------------------- setup, end to end (slow)


def _fake_agent_ok(tmp_path: pathlib.Path) -> list[str]:
    script = tmp_path / "fake_ok.py"
    script.write_text(
        "import json, sys\n"
        "print(json.dumps({'type': 'result', 'total_cost_usd': 0.0, 'usage': "
        "{'input_tokens': 1, 'output_tokens': 1, 'cache_creation_input_tokens': 0, "
        "'cache_read_input_tokens': 0}}))\n")
    return [sys.executable, str(script)]


@pytest.mark.slow
@pytest.mark.parametrize("name", ["add-4", "add-3x"])
def test_pilot_arm_setup_succeeds_in_a_bare_sandbox(tmp_path, name):
    import shutil

    if shutil.which("uv") is None:
        pytest.skip("uv not found on PATH — loud skip, never a silent pass")
    if name == "add-3x" and not ADD37_WORKTREE.exists():
        pytest.skip(f"3.7.0 worktree absent at {ADD37_WORKTREE}")
    from benchmark.runner.core import execute_wm

    arm = pilot_mod.resolve_setup_steps(load_arm(ARMS_DIR / f"{name}.toml"), REPO_ROOT)
    runs_root = tmp_path / "runs"
    record = execute_wm(arm, 1, agent_cmd=_fake_agent_ok(tmp_path), timeout_s=300.0,
                        retries=0, runs_root=runs_root)
    transcript = (runs_root / name / "wm1" / "transcript.jsonl").read_text()
    setup = [ln for ln in transcript.splitlines() if ln.startswith("setup:")]
    assert len(setup) == len(_steps(name))
    assert all("exit 0" in ln for ln in setup), setup
    ws = pathlib.Path(record.artifacts["workspace"])
    assert pathlib.Path(_git(ws, "rev-parse", "--show-toplevel")).resolve() == ws.resolve()
    if name == "add-4":
        installed = ws / ".claude" / "skills" / "add" / "SKILL.md"
        assert installed.read_bytes() == (REPO_ROOT / "add-method/skill/add/SKILL.md").read_bytes(), \
            "the arm installed a stale bundled skill, not this worktree's"
        assert not (ws / ".add" / "tooling").exists(), "4.0 ships no engine"
    else:
        assert (ws / ".add" / "tooling" / "cli.py").is_file()
        version = subprocess.run(
            [str(ws / ".venv/bin/python"), "-c", "import add_method; print(add_method.__version__)"],
            capture_output=True, text=True).stdout.strip()
        assert version == "3.7.0", version
