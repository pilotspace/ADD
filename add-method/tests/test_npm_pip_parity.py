"""The npm launcher and the pip installer are twins: same flags, same files, same output.

ADD 4.0 ships a skill, not an engine, so the installer only copies files and writes one managed
block. `bin/cli.js` and `src/add_method/_installer.py` do that by two routes; these checks run BOTH
against the same inputs and require byte-identical trees and identical stdout. A behaviour held
only by reading one twin's source would drift the first time someone edits the other.

Covers: fresh install · re-run idempotence · refresh-ours / keep-yours · the 3.x upgrade path ·
`--help` · unknown flags · failure reporting · zero runtime dependencies · the packaged payload.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "src"))

from add_method import _installer  # noqa: E402

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not on PATH — the npm twin cannot run")
TWINS = ("npm", "pip")
LINE_CEILING = 350


def run(twin: str, args: list[str], cwd: Path, home: Path | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "HOME": str(home or cwd.parent / "home"), "PYTHONPATH": str(PKG / "src")}
    env.pop("ADD_HOME", None)
    env.pop("XDG_DATA_HOME", None)
    cmd = ([NODE, str(PKG / "bin" / "cli.js")] if twin == "npm"
           else [sys.executable, "-m", "add_method"])
    return subprocess.run(cmd + list(args), cwd=str(cwd), env=env, capture_output=True,
                          text=True, timeout=60)


def tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


def both(tmp_path: Path, args: list[str], seed=None) -> dict:
    """Run each twin in its own copy of the same starting project; return per-twin results."""
    out = {}
    for twin in TWINS:
        project = tmp_path / twin / "proj"
        project.mkdir(parents=True)
        if seed:
            seed(project)
        proc = run(twin, args, project)
        out[twin] = (project, proc)
    return out


def same(results: dict) -> None:
    (a, pa), (b, pb) = results["npm"], results["pip"]
    assert pa.returncode == pb.returncode, (pa.stderr, pb.stderr)
    ta, tb = tree(a), tree(b)
    assert set(ta) == set(tb), f"npm-only {sorted(set(ta) - set(tb))} · pip-only {sorted(set(tb) - set(ta))}"
    diff = [k for k in ta if ta[k] != tb[k]]
    assert not diff, f"twins wrote different bytes: {diff}"
    assert pa.stdout.replace(str(a), "<dir>") == pb.stdout.replace(str(b), "<dir>"), \
        f"twins print different summaries:\n--npm--\n{pa.stdout}\n--pip--\n{pb.stdout}"


# --- fresh install ----------------------------------------------------------------------------

@needs_node
def test_fresh_install_is_identical_across_twins(tmp_path):
    results = both(tmp_path, ["init"])
    same(results)
    assert results["pip"][1].returncode == 0, results["pip"][1].stderr


@needs_node
@pytest.mark.parametrize("twin", TWINS)
def test_fresh_install_lands_the_skill_only_layout(tmp_path, twin):
    project = tmp_path / "my-app"
    project.mkdir()
    proc = run(twin, [], project)
    assert proc.returncode == 0, proc.stderr
    assert sorted(p.name for p in project.iterdir()) == [".add", ".claude", "AGENTS.md", "CLAUDE.md"]
    assert sorted(p.name for p in (project / ".add").iterdir()) == [
        ".gitignore", "PROJECT.md", "milestones", "personas", "personas-index", "personas-teacher",
        "specs", "tasks"]
    assert sorted(p.name for p in (project / ".claude").iterdir()) == ["skills"]
    assert tree(project / ".claude" / "skills" / "add") == tree(PKG / "skill" / "add")
    assert tree(project / ".add" / "personas-teacher") == tree(PKG / "personas-teacher")
    assert tree(project / ".add" / "personas-index") == tree(PKG / "personas-index")
    assert tree(project / ".add" / "personas") == tree(PKG / "personas")
    for d in ("specs", "milestones", "tasks"):
        assert [p.name for p in (project / ".add" / d).iterdir()] == [".gitkeep"]
    text = (project / ".add" / "PROJECT.md").read_text(encoding="utf-8")
    assert text.startswith("---\ntype: Project\ntitle: my-app\n"), text[:80]
    for key in ("goal:", "invariants:", "test_cmd:", "stage:", "## CARD", "state:", "next:"):
        assert key in text, f"PROJECT.md lacks {key}"
    assert "/add" in proc.stdout, "the summary never names the next step"


# --- re-run -----------------------------------------------------------------------------------

@needs_node
@pytest.mark.parametrize("twin", TWINS)
def test_rerun_is_idempotent(tmp_path, twin):
    project = tmp_path / "proj"
    project.mkdir()
    assert run(twin, [], project).returncode == 0
    first = tree(project)
    second = run(twin, ["update"], project)
    assert second.returncode == 0, second.stderr
    assert tree(project) == first, "a second run changed the project"
    assert not [k for k in first if k.endswith(".bak")], "a no-op run left a backup file"


def _dirty(project: Path) -> None:
    skill = project / ".claude" / "skills" / "add"
    (skill / "SKILL.md").write_text("edited by hand\n", encoding="utf-8")
    (skill / "stray.md").write_text("left over\n", encoding="utf-8")
    (project / ".add" / "PROJECT.md").write_text("my project\n", encoding="utf-8")
    (project / ".add" / "personas" / "task-planner.md").write_text("my lens\n", encoding="utf-8")
    (project / ".add" / "personas-teacher" / "stray.md").write_text("x\n", encoding="utf-8")
    claude = project / "CLAUDE.md"
    claude.write_text("my rules\n\n" + claude.read_text(encoding="utf-8") + "\nmore rules\n",
                      encoding="utf-8")


@needs_node
def test_rerun_refreshes_ours_and_keeps_yours(tmp_path):
    def seed(project):
        assert run("pip", [], project).returncode == 0
        _dirty(project)
    results = both(tmp_path, [], seed)
    same(results)
    project, proc = results["npm"]
    assert proc.returncode == 0, proc.stderr
    assert tree(project / ".claude" / "skills" / "add") == tree(PKG / "skill" / "add"), \
        "the skill tree is ours — a re-run must restore it exactly"
    assert tree(project / ".add" / "personas-teacher") == tree(PKG / "personas-teacher")
    assert (project / ".add" / "PROJECT.md").read_text(encoding="utf-8") == "my project\n"
    assert (project / ".add" / "personas" / "task-planner.md").read_text(encoding="utf-8") == "my lens\n"
    claude = (project / "CLAUDE.md").read_text(encoding="utf-8")
    assert claude.startswith("my rules\n") and claude.endswith("\nmore rules\n")
    assert claude.count("<!-- ADD:BEGIN") == 1


# --- the 3.x upgrade --------------------------------------------------------------------------

LEGACY_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"


def _agent(name: str) -> str:
    return f"---\nname: {name}\ndescription: The ADD {name}\nmodel: inherit\n---\nbody\n"


def seed_3x(project: Path) -> None:
    add = project / ".add"
    (add / "tooling" / "templates").mkdir(parents=True)
    (add / "tooling" / "cli.py").write_text("# engine\n", encoding="utf-8")
    (add / "tooling" / "add.py").write_text("# engine\n", encoding="utf-8")
    (add / "tooling" / "templates" / "TASK.md.tmpl").write_text("t\n", encoding="utf-8")
    (add / "state.json").write_text('{"v": 3}\n', encoding="utf-8")
    (add / "PROJECT.md").write_text("---\ntype: Project\ntitle: old\n---\n3.x project\n", encoding="utf-8")
    (add / "tasks" / "login.d").mkdir(parents=True)
    (add / "tasks" / "login.md").write_text("a task\n", encoding="utf-8")
    (add / ".gitignore").write_text("tooling/\ndocs/\n", encoding="utf-8")
    (add / ".add-version").write_text('{"version": "3.7.0"}\n', encoding="utf-8")
    agents = project / ".claude" / "agents"
    agents.mkdir(parents=True)
    for name in ("add-worker", "add-advisor", "add"):
        (agents / f"{name}.md").write_text(_agent(name), encoding="utf-8")
    (agents / "my-reviewer.md").write_text(_agent("my-reviewer"), encoding="utf-8")
    old_skill = project / ".claude" / "skills" / "add" / "phases"
    old_skill.mkdir(parents=True)
    (old_skill / "build.md").write_text("3.x phase guide\n", encoding="utf-8")
    (project / "AGENTS.md").write_text(
        "team notes\n\n" + LEGACY_BEGIN + "\nrun `python3 .add/tooling/cli.py status`\n"
        "<!-- ADD:END -->\n\nmore notes\n", encoding="utf-8")


@needs_node
def test_3x_upgrade_removes_the_engine_and_roster_and_keeps_user_state(tmp_path):
    results = both(tmp_path, [], seed_3x)
    same(results)
    project, proc = results["npm"]
    assert proc.returncode == 0, proc.stderr
    add = project / ".add"
    assert not (add / "tooling").exists(), "the vendored 3.x engine survived the upgrade"
    for name in ("add-worker", "add-advisor", "add"):
        assert not (project / ".claude" / "agents" / f"{name}.md").exists(), f"{name}.md survived"
    assert (project / ".claude" / "agents" / "my-reviewer.md").is_file(), "a user's agent was removed"
    assert (add / "state.json").read_text(encoding="utf-8") == '{"v": 3}\n'
    assert (add / "PROJECT.md").read_text(encoding="utf-8").endswith("3.x project\n")
    assert (add / "tasks" / "login.md").is_file() and (add / "tasks" / "login.d").is_dir()
    assert (add / ".add-version").is_file(), "3.x history is left in place"
    assert not (add / "tasks" / ".gitkeep").exists(), ".gitkeep lands only in an empty folder"
    assert not (project / ".claude" / "skills" / "add" / "phases").exists(), "3.x skill files linger"
    gi = (add / ".gitignore").read_text(encoding="utf-8")
    assert gi.startswith("tooling/\ndocs/\n") and "personas-teacher/" in gi
    agents_md = (project / "AGENTS.md").read_text(encoding="utf-8")
    assert agents_md.startswith("team notes\n\n") and agents_md.endswith("\n\nmore notes\n")
    assert agents_md.count("<!-- ADD:BEGIN") == 1 and "cli.py" not in agents_md
    for reported in (".add/tooling/", ".claude/agents/add-worker.md", ".claude/agents/add-advisor.md"):
        assert reported in proc.stdout, f"the summary never reports removing {reported}"


LEGACY_POINTERS = (".clinerules", "GEMINI.md", ".cursorrules", ".windsurfrules",
                   ".github/copilot-instructions.md")


@needs_node
def test_3x_blocks_in_other_pointer_files_are_refreshed_never_created(tmp_path):
    """3.x wrote the block to .clinerules too; after the upgrade no file may still point at the engine."""
    stale = "top\n\n" + LEGACY_BEGIN + "\nrun `python3 .add/tooling/cli.py status`\n<!-- ADD:END -->\n\nend\n"

    def seed(project):
        (project / ".clinerules").write_text(stale, encoding="utf-8")
        (project / ".github").mkdir()
        (project / ".github" / "copilot-instructions.md").write_text(stale, encoding="utf-8")
        (project / ".cursorrules").write_text("my rules, no ADD block\n", encoding="utf-8")
        (project / "GEMINI.md").write_text("half\n" + LEGACY_BEGIN + "\nno end\n", encoding="utf-8")
    results = both(tmp_path, [], seed)
    same(results)
    project, proc = results["npm"]
    assert proc.returncode == 0, proc.stderr
    for name in (".clinerules", ".github/copilot-instructions.md"):
        text = (project / name).read_text(encoding="utf-8")
        assert text == "top\n\n" + _installer._pointer_block() + "\n\nend\n", name
        assert name in proc.stdout, f"the summary never reports refreshing {name}"
    assert (project / ".cursorrules").read_text(encoding="utf-8") == "my rules, no ADD block\n"
    assert (project / "GEMINI.md").read_text(encoding="utf-8") == "half\n" + LEGACY_BEGIN + "\nno end\n", \
        "a legacy file without a whole block must be left alone, never appended to"
    assert not (project / ".windsurfrules").exists(), "a legacy pointer file was created fresh"
    for name in LEGACY_POINTERS + ("CLAUDE.md", "AGENTS.md"):
        path = project / name
        if path.is_file():
            assert "cli.py" not in path.read_text(encoding="utf-8") or name == "GEMINI.md", name


@needs_node
def test_an_agent_file_that_is_not_ours_is_kept(tmp_path):
    def seed(project):
        agents = project / ".claude" / "agents"
        agents.mkdir(parents=True)
        (agents / "add-worker.md").write_text("---\nname: my-worker\n---\nmine\n", encoding="utf-8")
        (agents / "add-advisor.md").write_text("no frontmatter, still mine\n", encoding="utf-8")
    results = both(tmp_path, [], seed)
    same(results)
    project = results["pip"][0]
    assert (project / ".claude" / "agents" / "add-worker.md").read_text(encoding="utf-8").endswith("mine\n")
    assert (project / ".claude" / "agents" / "add-advisor.md").is_file()


@needs_node
def test_a_tooling_folder_without_the_engine_is_kept(tmp_path):
    def seed(project):
        (project / ".add" / "tooling").mkdir(parents=True)
        (project / ".add" / "tooling" / "notes.md").write_text("mine\n", encoding="utf-8")
    results = both(tmp_path, [], seed)
    same(results)
    assert (results["pip"][0] / ".add" / "tooling" / "notes.md").is_file()


# --- flags ------------------------------------------------------------------------------------

@needs_node
@pytest.mark.parametrize("twin", TWINS)
@pytest.mark.parametrize("flag", ["--help", "-h", "help"])
def test_help_prints_and_installs_nothing(tmp_path, twin, flag):
    proc = run(twin, [flag], tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "usage:" in proc.stdout and "--global" in proc.stdout
    assert not list(tmp_path.iterdir()), "--help installed something"


@needs_node
@pytest.mark.parametrize("twin", TWINS)
@pytest.mark.parametrize("args", [["--bogus"], ["--force"], ["--no-skill"], ["--stage", "mvp"],
                                  ["--name"], ["prune-data"], ["a", "b"]])
def test_bad_usage_exits_2_and_installs_nothing(tmp_path, twin, args):
    proc = run(twin, args, tmp_path)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "error:" in proc.stderr
    assert not list(tmp_path.iterdir()), f"{args} installed something"


@needs_node
@pytest.mark.parametrize("twin", TWINS)
def test_name_and_target_are_honoured(tmp_path, twin):
    target = tmp_path / "elsewhere"
    target.mkdir()
    proc = run(twin, ["init", str(target), "--name", "Payments API", "--yes"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "title: Payments API\n" in (target / ".add" / "PROJECT.md").read_text(encoding="utf-8")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["elsewhere"]


@needs_node
@pytest.mark.parametrize("twin", TWINS)
def test_version_flag(tmp_path, twin):
    proc = run(twin, ["--version"], tmp_path)
    assert proc.returncode == 0
    assert proc.stdout.strip() == json.loads((PKG / "package.json").read_text())["version"]


# --- failure is loud --------------------------------------------------------------------------

@needs_node
@pytest.mark.parametrize("twin", TWINS)
def test_a_missing_target_fails(tmp_path, twin):
    proc = run(twin, [str(tmp_path / "nope")], tmp_path)
    assert proc.returncode == 1 and "error:" in proc.stderr
    assert not (tmp_path / "nope").exists()


@needs_node
@pytest.mark.parametrize("twin", TWINS)
def test_a_partial_install_reports_and_exits_nonzero(tmp_path, twin):
    (tmp_path / ".claude").write_text("a file where a folder must go\n", encoding="utf-8")
    proc = run(twin, [], tmp_path)
    assert proc.returncode == 1, proc.stdout
    assert "error:" in proc.stderr and ".claude/skills/add" in proc.stderr
    assert "re-run" in proc.stderr, "the failure does not say how to recover"


@needs_node
@pytest.mark.parametrize("twin", TWINS)
def test_a_read_only_target_fails_loudly(tmp_path, twin):
    target = tmp_path / "ro"
    target.mkdir()
    os.chmod(target, stat.S_IRUSR | stat.S_IXUSR)
    try:
        if os.access(target, os.W_OK):
            pytest.skip("running as root — a read-only folder is still writable")
        proc = run(twin, [str(target)], tmp_path)
    finally:
        os.chmod(target, stat.S_IRWXU)
    assert proc.returncode == 1 and "error:" in proc.stderr


# --- no dependencies, small twins -------------------------------------------------------------

def _js() -> str:
    return (PKG / "bin" / "cli.js").read_text(encoding="utf-8")


def test_the_npm_twin_needs_only_node_builtins():
    mods = set(re.findall(r'require\(\s*"([^"]+)"\s*\)', _js()))
    assert mods <= {"fs", "path", "os"}, f"cli.js requires more than builtins: {sorted(mods)}"
    assert "import(" not in _js(), "cli.js lazy-imports a module"
    pkg = json.loads((PKG / "package.json").read_text(encoding="utf-8"))
    assert not pkg.get("dependencies"), f"package.json still declares {pkg.get('dependencies')}"
    lock = (PKG / "package-lock.json").read_text(encoding="utf-8")
    assert "@clack" not in lock, "package-lock.json still pins @clack/prompts"


def test_the_pip_twin_needs_only_the_stdlib():
    text = (PKG / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r"(?m)^dependencies = \[\]$", text), "pyproject declares runtime dependencies"


def test_each_twin_stays_small():
    for path in (PKG / "bin" / "cli.js", PKG / "src" / "add_method" / "_installer.py"):
        n = len(path.read_text(encoding="utf-8").splitlines())
        assert n <= LINE_CEILING, f"{path.name} is {n} lines (ceiling {LINE_CEILING})"


def test_npm_reads_its_version_from_package_json():
    assert re.search(r'require\(\s*path\.join\(\s*PKG_ROOT\s*,\s*"package\.json"\s*\)\s*\)\.version', _js())
    declared = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["version"]
    assert f'"{declared}"' not in _js(), "cli.js hard-codes its version"


def test_the_markers_are_byte_identical():
    for name in ("GUIDE_BEGIN", "GUIDE_END"):
        m = re.search(rf'^const {name} = "((?:[^"\\]|\\.)*)";', _js(), re.M)
        assert m, f"cli.js defines no const {name}"
        assert m.group(1) == getattr(_installer, "_" + name), f"{name} differs between twins"


# --- the packaged payload ---------------------------------------------------------------------

PAYLOAD = ("skill", "personas", "personas-teacher", "personas-index")


def test_npm_ships_the_skill_payload_and_nothing_retired():
    files = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["files"]
    for needed in ("bin/", "skill/", "personas/", "personas-teacher/", "personas-index/",
                   "THIRD_PARTY_NOTICES.md"):
        assert needed in files, f"package.json `files` omits {needed}"
    stale = [f for f in files if f.startswith(("tooling", "agents"))]
    assert not stale, f"package.json still ships {stale}"
    scripts = json.dumps(json.loads((PKG / "package.json").read_text())["scripts"])
    assert "tooling" not in scripts, f"npm scripts reference the deleted engine: {scripts}"


def test_the_pip_bundle_mirrors_the_npm_payload():
    bundled = PKG / "src" / "add_method" / "_bundled"
    for sub in PAYLOAD:
        src = PKG / (sub + "/add" if sub == "skill" else sub)
        dst = bundled / (sub + "/add" if sub == "skill" else sub)
        assert tree(dst) == tree(src), f"_bundled/{sub} differs from {sub}"
    assert sorted(p.name for p in bundled.iterdir() if p.name != "__pycache__") == sorted(
        PAYLOAD + ("THIRD_PARTY_NOTICES.md",)), "the pip bundle ships something the npm package does not"
    assert (bundled / "THIRD_PARTY_NOTICES.md").read_bytes() == (PKG / "THIRD_PARTY_NOTICES.md").read_bytes()


def test_the_plugin_ships_the_skill_only():
    plugin = json.loads((PKG / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert "agents" not in plugin and plugin.get("skills") == "./skill/"
