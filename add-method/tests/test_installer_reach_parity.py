"""The two installer twins must reach the same places — and the roster must land where the host looks.

Two independent defects, one root: nothing read BOTH twins' global tree declarations, and nothing
asked whether the global roster was DISCOVERABLE after it landed.

  R:TWINDRIFT          `personas-index` was added to the JS `GLOBAL_TREES` and never to the Python
                       `_GLOBAL_TREES`. A pip global install silently shipped no routing index; an
                       npm one did. Both twins' lists were hand-written and neither is a copy.
  R:UNREACHABLEROSTER  Both twins mirrored `agents` into `<home>/agents` — a path Claude Code never
                       reads. The skill was deployed to `~/.claude/skills/add`; the roster it names
                       was deployed nowhere, so every `add-worker` spawn a global install advertised
                       resolved to nothing.

The twins are held equal by PARSING both declarations (E5) — a restated list rots on the next entry.
"""
import re
import sys
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "src"))

from add_method import _installer  # noqa: E402


def _js() -> str:
    return (PKG / "bin" / "cli.js").read_text(encoding="utf-8")


def _js_global_trees() -> set:
    """The `sub` keys of cli.js's GLOBAL_TREES, read from the source — never restated here."""
    m = re.search(r"const\s+GLOBAL_TREES\s*=\s*\[(.*?)\n\];", _js(), re.S)
    assert m, "cli.js no longer declares a GLOBAL_TREES array — the parser is broken, not the twin"
    return set(re.findall(r'^\s*\["([^"]+)"', m.group(1), re.M))


def _py_global_trees() -> set:
    return {sub for sub, _dest, _strip in _installer._GLOBAL_TREES}


@pytest.fixture()
def bundled(tmp_path):
    """A synthetic package root carrying every tree the global mirror knows about."""
    root = tmp_path / "bundled"
    for sub in sorted(_py_global_trees() | _js_global_trees()):
        d = root / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / "seed.md").write_text(f"# {sub}\n", encoding="utf-8")
    (root / "agents" / "add-worker.md").write_text("# add-worker\n", encoding="utf-8")
    (root / "agents" / "add-advisor.md").write_text("# add-advisor\n", encoding="utf-8")
    return root


def _homes(tmp_path):
    """(<add home>, <claude skills dir>) — the skills dir shaped as the resolver builds it."""
    return tmp_path / "home", tmp_path / "hostcfg" / ".claude" / "skills" / "add"


def _agents_dir(claude_dir: Path) -> Path:
    """Where the host looks for subagents, derived from where the skill lands."""
    return claude_dir.parent.parent / "agents"


# --- M1/M2/E5/A1 — the twins declare the same set ------------------------------------------

def test_the_global_tree_sets_are_equal():
    """covers: M1, M2, R:TWINDRIFT · both declarations parsed and compared."""
    py, js = _py_global_trees(), _js_global_trees()
    assert py == js, (f"global tree sets drifted — python-only: {sorted(py - js)} · "
                      f"js-only: {sorted(js - py)}")


def test_the_parity_test_reads_both_twins():
    """covers: E5, A1 · no restated list."""
    src = Path(__file__).read_text(encoding="utf-8")
    assert "_installer._GLOBAL_TREES" in src, "the python side must be READ, not restated"
    assert "GLOBAL_TREES" in _js(), "the js side must be READ from cli.js"
    # a literal tree name written into an assertion is exactly the rot this guards against
    body = src.split("def test_the_parity_test_reads_both_twins", 1)[0]
    assert "personas-index" not in body.split('"""', 3)[-1], \
        "a tree name is hard-coded above the parser — the guard will rot on the next entry"


def test_no_existing_tree_entry_is_removed():
    """covers: A1 · the union is the target."""
    union = {"skill/add", "agents", "tooling", "personas-teacher", "personas-index"}
    assert union <= _py_global_trees(), f"python lost {sorted(union - _py_global_trees())}"
    assert union <= _js_global_trees(), f"js lost {sorted(union - _js_global_trees())}"


# --- M3/A2 — the roster lands where the host looks -----------------------------------------

def test_a_global_install_lands_the_roster_where_the_host_looks(tmp_path, bundled):
    """covers: M3, A2, R:UNREACHABLEROSTER · the roster sits beside the skill."""
    home, claude_dir = _homes(tmp_path)
    _installer._reconcile_global(home, claude_dir, bundled)
    landed = _agents_dir(claude_dir)
    assert (landed / "add-worker.md").is_file(), \
        f"the roster never reached {landed} — a global install advertises agents the host cannot find"
    assert (landed / "add-advisor.md").is_file()
    assert landed.parent == claude_dir.parent.parent, "the roster must sit beside the skill"


def test_a_global_update_refreshes_the_roster(tmp_path, bundled):
    """covers: A3 · the roster moves with the skill."""
    home, claude_dir = _homes(tmp_path)
    _installer._reconcile_global(home, claude_dir, bundled)
    (bundled / "agents" / "add-worker.md").write_text("# add-worker v2\n", encoding="utf-8")
    _installer._reconcile_global(home, claude_dir, bundled)
    assert "v2" in (_agents_dir(claude_dir) / "add-worker.md").read_text(encoding="utf-8"), \
        "the roster went stale while the skill moved"


def test_the_install_names_the_roster_path(tmp_path, bundled, capsys):
    """covers: A7 · the output reports it."""
    home, claude_dir = _homes(tmp_path)
    _installer._reconcile_global(home, claude_dir, bundled)
    out = capsys.readouterr().out
    assert str(_agents_dir(claude_dir)) in out, \
        f"the install never named where the roster landed — output was:\n{out}"


# --- M5/M4 — the failure modes --------------------------------------------------------------

def test_a_lean_package_still_installs(tmp_path, bundled):
    """covers: M5, A4, E1 · optional trees soft-skip."""
    import shutil
    for sub in sorted(_installer.OPTIONAL):
        shutil.rmtree(bundled / sub, ignore_errors=True)
    home, claude_dir = _homes(tmp_path)
    _installer._reconcile_global(home, claude_dir, bundled)   # must not raise
    assert (claude_dir / "seed.md").is_file(), "the core skill must land without the optional trees"
    assert not _agents_dir(claude_dir).exists() or not list(_agents_dir(claude_dir).iterdir())


def test_a_missing_host_directory_is_created(tmp_path, bundled):
    """covers: A5, E2 · a first-ever install succeeds."""
    home, claude_dir = _homes(tmp_path)
    assert not claude_dir.parent.parent.exists(), "fixture precondition: no host config dir yet"
    _installer._reconcile_global(home, claude_dir, bundled)
    assert _agents_dir(claude_dir).is_dir()


def test_a_retired_agent_is_removed(tmp_path, bundled):
    """covers: M4, E3 · the replace tombstones it."""
    home, claude_dir = _homes(tmp_path)
    landed = _agents_dir(claude_dir)
    landed.mkdir(parents=True)
    retired = _installer._RETIRED_AGENTS[0]
    (landed / retired).write_text("# stale\n", encoding="utf-8")
    (landed / "my-own-agent.md").write_text("# mine\n", encoding="utf-8")
    _installer._reconcile_global(home, claude_dir, bundled)
    assert not (landed / retired).exists(), f"{retired} survived a global install"
    assert (landed / "my-own-agent.md").is_file(), "a user's own subagent was swept — data loss"


def test_a_second_install_is_idempotent(tmp_path, bundled):
    """covers: M4, E4, A6 · no duplication, fully reconciled home."""
    home, claude_dir = _homes(tmp_path)
    _installer._reconcile_global(home, claude_dir, bundled)
    first = sorted(p.name for p in _agents_dir(claude_dir).iterdir())
    _installer._reconcile_global(home, claude_dir, bundled)
    assert sorted(p.name for p in _agents_dir(claude_dir).iterdir()) == first
    # A6: host deployment reads a fully reconciled home, never the package directly
    assert (home / "agents" / "add-worker.md").is_file()
