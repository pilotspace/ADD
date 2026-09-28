"""`--global` reaches the same place from both twins — and only that place.

A global install puts the skill where Claude Code looks for a user's skills (`~/.claude/skills/add`)
and touches no project. It also retires the 3.x roster the 3.x global install deployed to
`~/.claude/agents/` — but only files that are ours by content (frontmatter `name:` equal to a
retired ADD agent), never a user's own subagent that happens to share a name.
The 3.x global home (`~/.add`) may hold a user's data snapshots: it is reported, never deleted.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not on PATH — the npm twin cannot run")
TWINS = ("npm", "pip")


def run(twin: str, args: list[str], cwd: Path, home: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "HOME": str(home), "PYTHONPATH": str(PKG / "src")}
    env.pop("ADD_HOME", None)
    env.pop("XDG_DATA_HOME", None)
    cmd = ([NODE, str(PKG / "bin" / "cli.js")] if twin == "npm"
           else [sys.executable, "-m", "add_method"])
    return subprocess.run(cmd + args, cwd=str(cwd), env=env, capture_output=True, text=True,
                          timeout=60)


def tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


def setup(tmp_path: Path, twin: str, seed=None) -> tuple[Path, Path]:
    home, proj = tmp_path / twin / "home", tmp_path / twin / "proj"
    home.mkdir(parents=True)
    proj.mkdir()
    if seed:
        seed(home)
    return home, proj


def _agent(name: str) -> str:
    return f"---\nname: {name}\ndescription: The ADD {name}\n---\nbody\n"


def seed_3x_home(home: Path) -> None:
    agents = home / ".claude" / "agents"
    agents.mkdir(parents=True)
    for name in ("add-worker", "add-advisor", "add-design"):
        (agents / f"{name}.md").write_text(_agent(name), encoding="utf-8")
    (agents / "my-agent.md").write_text(_agent("my-agent"), encoding="utf-8")
    (agents / "add-verify.md").write_text("---\nname: my-verify\n---\n", encoding="utf-8")
    old = home / ".claude" / "skills" / "add" / "phases"
    old.mkdir(parents=True)
    (old / "build.md").write_text("3.x\n", encoding="utf-8")
    (home / ".add" / "tooling").mkdir(parents=True)
    (home / ".add" / ".add-version").write_text('{"version": "3.7.0"}\n', encoding="utf-8")
    (home / ".add" / "data").mkdir()
    (home / ".add" / "data" / "snapshot.md").write_text("user data\n", encoding="utf-8")


def test_global_installs_the_skill_for_the_user_and_touches_no_project(tmp_path):
    outs = {}
    for twin in TWINS:
        home, proj = setup(tmp_path, twin)
        proc = run(twin, ["--global"], proj, home)
        assert proc.returncode == 0, proc.stderr
        assert tree(home / ".claude" / "skills" / "add") == tree(PKG / "skill" / "add")
        assert not list(proj.iterdir()), "--global wrote into the current project"
        assert sorted(p.name for p in home.iterdir()) == [".claude"]
        outs[twin] = (tree(home), proc.stdout.replace(str(home), "<home>"))
    assert outs["npm"] == outs["pip"], "the twins' global installs differ"


def test_global_retires_only_our_3x_agents_and_keeps_the_3x_home(tmp_path):
    outs = {}
    for twin in TWINS:
        home, proj = setup(tmp_path, twin, seed_3x_home)
        proc = run(twin, ["--global"], proj, home)
        assert proc.returncode == 0, proc.stderr
        agents = home / ".claude" / "agents"
        assert sorted(p.name for p in agents.iterdir()) == ["add-verify.md", "my-agent.md"], \
            "an ADD roster file survived or a user's agent was removed"
        assert not (home / ".claude" / "skills" / "add" / "phases").exists()
        assert (home / ".add" / "data" / "snapshot.md").is_file(), "the 3.x home was deleted"
        assert str(home / ".add") in proc.stdout, "the unused 3.x home is not reported"
        assert "add-worker.md" in proc.stdout, "the removed roster is not reported"
        outs[twin] = (tree(home), proc.stdout.replace(str(home), "<home>"))
    assert outs["npm"] == outs["pip"]


def test_global_is_idempotent(tmp_path):
    for twin in TWINS:
        home, proj = setup(tmp_path, twin)
        assert run(twin, ["--global"], proj, home).returncode == 0
        first = tree(home)
        assert run(twin, ["--global"], proj, home).returncode == 0
        assert tree(home) == first


def test_global_takes_no_directory(tmp_path):
    for twin in TWINS:
        home, proj = setup(tmp_path, twin)
        proc = run(twin, ["--global", str(proj)], proj, home)
        assert proc.returncode == 2 and "error:" in proc.stderr
        assert not list(home.iterdir()) and not list(proj.iterdir())


def test_a_symlinked_skill_folder_is_left_alone(tmp_path):
    for twin in TWINS:
        home, proj = setup(tmp_path, twin)
        real = tmp_path / twin / "dev-checkout"
        real.mkdir()
        (real / "SKILL.md").write_text("my dev copy\n", encoding="utf-8")
        (home / ".claude" / "skills").mkdir(parents=True)
        os.symlink(real, home / ".claude" / "skills" / "add")
        proc = run(twin, ["--global"], proj, home)
        assert proc.returncode == 0, proc.stderr
        assert (real / "SKILL.md").read_text(encoding="utf-8") == "my dev copy\n"
        assert (home / ".claude" / "skills" / "add").is_symlink()
        assert "symlink" in proc.stdout
