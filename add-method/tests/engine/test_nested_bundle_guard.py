"""A bundle that exists above you is a bundle `status` sends you to, never one `init` replaces.

Red-first for `/tasks/nested-bundle-guard.md`. The `covers:` citations live in each test's
docstring, which is where `checks_of` reads them.

Reproduced 2026-09-01 before this file existed: `cd add-method/src && cli.py status` printed
`no bundle here — run `add init` to create one` / `next: add init`, and following that exact
line created a second `index.md` beside the real one. `grep -c ancestor` over add.py and cli.py
returned 0 — the guard had never existed.
"""

import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

CLI = REPO / "tooling" / "cli.py"


@pytest.fixture
def nested(tmp_path):
    """A real bundle at the top, and a deep bundle-less directory beneath it."""
    top = tmp_path / "proj"
    (top / "src" / "deep").mkdir(parents=True)
    add.init(top / ".add", profile="code", title="ancestor fixture")
    return top


def test_ancestor_bundle_finds_the_nearest_bundle_above(nested):
    """covers: M1, A2 · a directory two levels under a bundle resolves to that bundle."""
    found = add.ancestor_bundle(nested / "src" / "deep" / ".add")
    assert found is not None
    assert Path(found).resolve() == (nested / ".add").resolve()


def test_ancestor_bundle_is_none_at_the_top(tmp_path):
    """covers: M1, E4 · a tree with no bundle anywhere returns None."""
    d = tmp_path / "lonely" / "deeper"
    d.mkdir(parents=True)
    assert add.ancestor_bundle(d / ".add") is None


def test_ancestor_bundle_ignores_a_marker_that_is_not_a_bundle(tmp_path):
    """covers: A2 · a file named `index.md` is not a bundle unless it declares `abf_version:`.

    The first cut of this check only ever wrote `graph.json` — a file `ancestor_bundle` does not
    read — so it could not fail whatever the function did, and it passed straight over the real
    defect: the walk treated ANY directory holding a file called `index.md` as a bundle root.
    `index.md` is the most common filename in documentation tooling, so a plain MkDocs homepage
    made `init` refuse a legitimate project and `status` announce an ADD project that never
    existed. Both shapes are exercised here now.
    """
    top = tmp_path / "proj"
    (top / ".add").mkdir(parents=True)
    (top / ".add" / "graph.json").write_text("{}")     # a file the walk never reads
    (top / "sub").mkdir()
    assert add.ancestor_bundle(top / "sub" / ".add") is None

    # the shape that actually bit: a docs homepage, one directory up
    docs = tmp_path / "site" / "docs"
    (docs / "guide").mkdir(parents=True)
    (docs / "index.md").write_text("# Welcome\n\nOur documentation.\n", encoding="utf-8")
    assert add.ancestor_bundle(docs / "guide" / ".add") is None, \
        "a MkDocs homepage was read as an ADD bundle root"

    # …and the same name INSIDE a `.add/`, still without the marker
    fake = tmp_path / "faux"
    (fake / ".add").mkdir(parents=True)
    (fake / ".add" / "index.md").write_text("# not a bundle\n", encoding="utf-8")
    (fake / "sub").mkdir()
    assert add.ancestor_bundle(fake / "sub" / ".add") is None


def test_ancestor_bundle_finds_a_real_bundle_by_its_marker(tmp_path):
    """covers: A2 · the discriminator is `abf_version:`, and a real bundle still resolves."""
    top = tmp_path / "proj"
    add.init(top, "code", "T")
    assert "abf_version:" in (top / "index.md").read_text(encoding="utf-8"), \
        "init no longer writes the marker this guard keys on"
    (top / "sub").mkdir()
    assert add.ancestor_bundle(top / "sub" / ".add") == top


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads an unreadable directory anyway")
def test_ancestor_bundle_stops_on_an_unreadable_parent(tmp_path):
    """covers: M5, A3, E3 · the walk returns None rather than raising."""
    top = tmp_path / "proj"
    (top / "sub").mkdir(parents=True)
    mode = top.stat().st_mode
    os.chmod(top, 0o000)
    try:
        assert add.ancestor_bundle(top / "sub" / ".add") is None
    finally:
        os.chmod(top, stat.S_IMODE(mode))


def test_status_names_the_ancestor_and_sends_you_there(nested):
    """covers: M2, A6 · the output names the ancestor and its `next:` is a runnable cd + status."""
    out = add.status(nested / "src" / "deep" / ".add")
    text = out if isinstance(out, str) else str(out)
    assert str(nested) in text
    assert "next: cd " in text
    assert "add status" in text
    assert "next: add init" not in text


def test_status_without_an_ancestor_is_unchanged(tmp_path):
    """covers: A4, E1, R:MISDIRECT · the incumbent line is printed verbatim."""
    d = tmp_path / "lonely"
    d.mkdir()
    out = add.status(d / ".add")
    text = out if isinstance(out, str) else str(out)
    assert "no bundle here — run `add init` to create one" in text
    assert "next: add init" in text


def test_status_prefers_the_2x_message(nested):
    """covers: A5, E2 · the 2.x branch fires ahead of the ancestor branch."""
    here = nested / "src" / "deep" / ".add"
    here.mkdir(parents=True)
    (here / "state.json").write_text("{}")
    text = str(add.status(here))
    assert "2.x bundle" in text
    assert "next: cd " not in text


def test_init_refuses_under_an_ancestor_bundle(nested):
    """covers: M3, R:RIVALBUNDLE · the refusal names the ancestor and no file is written."""
    target = nested / "src" / "deep" / ".add"
    graph, created, note = add.init(target, profile="code", title="rival")
    assert graph is None and created == []
    assert "R:RIVALBUNDLE" in note
    assert str(nested) in note
    assert "--nested" in note


def test_init_refuses_before_it_writes_anything(nested):
    """covers: A12, A16 · the candidate root holds no `index.md` after the refusal."""
    target = nested / "src" / "deep" / ".add"
    add.init(target, profile="code", title="rival")
    assert not (target / "index.md").exists()


def test_init_nested_creates_and_says_so(nested):
    """covers: M4, A1 · the bundle is created and the note states two bundles now exist."""
    target = nested / "src" / "deep" / ".add"
    graph, created, note = add.init(target, profile="code", title="deliberate", nested=True)
    assert graph is not None and created
    assert (target / "index.md").is_file()
    assert "two bundles" in note.lower()


def test_init_without_an_ancestor_is_unchanged(tmp_path):
    """covers: A14, E5 · a normal init, and an init on an existing bundle, behave as today."""
    root = tmp_path / "fresh" / ".add"
    graph, created, note = add.init(root, profile="code", title="fresh")
    assert graph is not None and (root / "index.md").is_file()
    again, created_again, _ = add.init(root, profile="code", title="fresh")
    assert again is not None
    assert created_again == []


def test_the_cli_exposes_nested(nested):
    """covers: M4 · `init --nested` is reachable from the command line."""
    target = nested / "src" / "deep"
    done = subprocess.run(
        [sys.executable, str(CLI), "--root", str(target / ".add"), "init", "--nested"],
        capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    assert (target / ".add" / "index.md").is_file()
