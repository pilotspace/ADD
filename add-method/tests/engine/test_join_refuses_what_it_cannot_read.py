"""A path the engine never read is reported as a stream that merged cleanly.

`join` folds N worktree stream bundles back into the main bundle. It iterates
`(d / "tasks").glob("*.md")` for each path it is handed — and `glob` on a directory that does not
exist yields nothing, quietly. Nothing to iterate reads as nothing to merge.

Measured 2026-09-03, on the incumbent engine:

    $ add join /nonexistent/.add
    joined 0 stream(s): —                       <- and exit 0
    next: add status

This is the same class as the fabricated receipt `run` used to write for a typo'd slug: a verb
reporting success over input it never found. A wave script checking exit codes cannot distinguish
a mistyped worktree path from a wave that legitimately merged nothing.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path, name="T"):
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    add.init(root, "code", name)
    return root


# ------------------------------------------------------------------ M1/M2 · the refusal

def test_join_refuses_a_path_that_does_not_exist(tmp_path):
    """covers: M1, A3, R:PHANTOMSTREAM — the measured typo."""
    root = _bundle(tmp_path)
    result, note = add.join(root, ["/nonexistent/.add"])
    assert result is None, "a path the engine never read was reported as a clean merge"


def test_the_refusal_names_the_path(tmp_path):
    """covers: M2, A6 — the fix is to correct the path, so the message must print it."""
    root = _bundle(tmp_path)
    _, note = add.join(root, ["/nonexistent/.add"])
    assert "/nonexistent/.add" in note, f"the refusal does not name the path: {note}"


# ------------------------------------------------------------------ M3/M4 · what stays legal

def test_a_readable_stream_that_merged_nothing_is_a_success(tmp_path):
    """covers: M3, A4 — zero is a real answer.

    A stream bundle with no GATED node contributes nothing, and that is correct behaviour, not
    an error. Refusing it would break every wave that scheduled a stream which did not finish.
    """
    root = _bundle(tmp_path)
    stream = _bundle(tmp_path, "S")
    result, note = add.join(root, [stream])
    assert result is not None, f"a readable but empty stream was refused: {note}"
    assert result["merged"] == [], result

    empty, note = add.join(root, [])
    assert empty is not None, f"an empty stream list was refused: {note}"


def test_nothing_is_merged_when_any_path_is_refused(tmp_path):
    """covers: M4, A5 — all-or-nothing, checked before the first write.

    A partial merge leaves the bundle in a state no receipt describes: some nodes from the wave,
    some not, and nothing recording which.
    """
    root = _bundle(tmp_path)
    stream = _bundle(tmp_path, "S")
    node = stream / "tasks" / "carried.md"
    node.parent.mkdir(parents=True, exist_ok=True)
    node.write_text(
        "---\ntype: Task\ntitle: c\nstatus: done\n"
        "verified:\n  - { by: x, at: 2026-09-03, act: gate, authority: plan, outcome: PASS }\n"
        "---\n## CARD\ngoal: g\n", encoding="utf-8")

    result, _ = add.join(root, [stream, "/nonexistent/.add"])
    assert result is None, "a bad path did not stop the join"
    assert not (root / "tasks" / "carried.md").exists(), \
        "the good stream was merged before the bad path was checked"


# ------------------------------------------------------------------ counter-guards

def test_a_file_or_a_non_bundle_directory_is_refused(tmp_path):
    """covers: M1, A2, E1, E2 — existing is not the same as readable."""
    afile = tmp_path / "notadir"
    afile.write_text("x", encoding="utf-8")
    adir = tmp_path / "nobundle"
    adir.mkdir()

    root = _bundle(tmp_path)
    for bad in (afile, adir):
        result, note = add.join(root, [bad])
        assert result is None, f"{bad} was accepted as a stream bundle"
        assert str(bad) in note, f"the refusal does not name {bad}: {note}"
