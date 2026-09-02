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
import ast
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
    """covers: E5, A1 · no restated list.

    The first cut split the source at this function's own name and then discarded everything
    before the third triple-quote — 1768 characters, all of it ABOVE this definition, and
    starting mid-sentence inside an unrelated docstring at that. It could not see the
    hard-coded tree set twelve lines below, and reordering the
    two functions flipped its verdict with no change to what the file asserts: it measured
    source layout, not the property it names. Scan the whole module instead, minus the strings
    that are allowed to mention a tree by name (the docstrings that EXPLAIN the rule).
    """
    src = Path(__file__).read_text(encoding="utf-8")
    assert "_installer._GLOBAL_TREES" in src, "the python side must be READ, not restated"
    assert "GLOBAL_TREES" in _js(), "the js side must be READ from cli.js"

    # The rot shape is a COLLECTION LITERAL restating the declaration — `{"skill/add", ...}`.
    # A bare `"agents"` used as a path segment (`claude_dir / "agents"`) restates nothing and
    # must stay legal, or the guard forbids the fixtures it needs.
    names, offenders = _installer_tree_names(), []
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, (ast.Set, ast.List, ast.Tuple)):
            continue
        for el in node.elts:
            if isinstance(el, ast.Constant) and el.value in names:
                offenders.append(f"line {el.lineno}: {el.value!r}")
    assert not offenders, (
        "a tree name is restated in a collection literal — the guard rots on the next "
        "entry:\n  " + "\n  ".join(offenders))


def _installer_tree_names() -> set:
    """The tree names, from the engine — so this check needs no list of its own either."""
    return _py_global_trees() | _js_global_trees()


def test_no_existing_tree_entry_is_removed():
    """covers: A1 · the union is the target — read from git, never restated here.

    The union was a literal set, which is the very thing the guard above forbids: it would need
    hand-editing on the next entry, and it silently encoded today's answer as the requirement.
    The committed declarations are the baseline instead — an entry present at HEAD must still
    be present in both twins.
    """
    import subprocess
    head = subprocess.run(["git", "show", "HEAD:add-method/src/add_method/_installer.py"],
                          cwd=str(PKG.parent), capture_output=True, text=True)
    if head.returncode != 0:
        pytest.skip("not a git checkout — nothing to compare the baseline against")
    block = head.stdout.split("_GLOBAL_TREES = (", 1)[1].split("\n)", 1)[0]
    baseline = set(re.findall(r'\(\s*"([^"]+)"', block))
    assert baseline, "the baseline parser found no committed tree entries"
    for name, have in (("python", _py_global_trees()), ("js", _js_global_trees())):
        assert baseline <= have, f"{name} lost {sorted(baseline - have)}"


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


def test_an_unwritable_roster_dir_does_not_fail_the_install(tmp_path, bundled, capsys):
    """covers: M5 · the third write target never masquerades as the first.

    `_reconcile_global` gained a THIRD write target while the caller kept ONE `except OSError`
    that reports `cannot write global home <home>`. On a machine where `~/.claude/agents` is
    owned by another user — plausible, it is a namespace other tools write — the install aborted
    naming a home that was perfectly writable, after the mirror and the skill had both landed.
    """
    import os
    import stat

    home, claude_dir = _homes(tmp_path)
    landed = _agents_dir(claude_dir)
    landed.mkdir(parents=True)
    mode = landed.stat().st_mode
    os.chmod(landed, stat.S_IRUSR | stat.S_IXUSR)          # r-x: readable, not writable
    try:
        if os.access(landed, os.W_OK):
            pytest.skip("running as root — an unwritable directory is still writable")
        _installer._reconcile_global(home, claude_dir, bundled)   # must NOT raise
    finally:
        os.chmod(landed, mode)

    out = capsys.readouterr().out
    assert (claude_dir / "seed.md").is_file(), "the skill must still be deployed"
    assert "global home" not in out, \
        "a roster failure was reported as the HOME being unwritable — it names the wrong path"
    assert str(landed) in out and "NOT deployed" in out, \
        f"the roster failure was silent; output was:\n{out}"


def test_both_twins_treat_the_roster_write_as_non_fatal():
    """covers: M5, R:TWINDRIFT · the JS twin degrades the same way."""
    js = _js()
    block = js.split("const roster = path.join(home,", 1)[1].split("\n  }", 1)[0]
    assert "try {" in block and "catch" in block, \
        "cli.js still lets a roster write abort the whole global install"
    assert "NOT deployed" in block, "the JS twin does not report the degraded roster"
