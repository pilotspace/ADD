"""`add todo` — the open worklist by beat (B6, recovered verb).

Read-only: `todo(root, milestone)` returns the active Tasks (direction|build|verify), grouped by beat,
each with its next verb — the focused, actionable list `status`'s bounded snapshot does not give.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
import cli  # noqa: E402


def _run(root, *argv):
    return cli.main(["--root", str(root), *argv])


def _snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


def _slugs(items):
    return {cid.rsplit("/", 1)[-1][:-3] for cid, *_ in items}


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m1", title="m1")
    add.new(tmp_path, "Milestone", "m2", title="m2")
    add.new(tmp_path, "Task", "open1", title="open1", milestone="m1", scope=["a.py"])
    add.new(tmp_path, "Task", "open2", title="open2", milestone="m2", scope=["b.py"])
    # a done task: gate it closed via a hand stamp so it must be excluded
    add.new(tmp_path, "Task", "closed", title="closed", milestone="m1", scope=["c.py"])
    add._transition(tmp_path, "/tasks/closed.md", sets={"status": "done"})


def test_todo_lists_active_with_next_verb(tmp_path):
    """covers: M1, E1 — active tasks appear with a next verb; a done task does not."""
    _bundle(tmp_path)
    items, note = add.todo(tmp_path)
    assert _slugs(items) == {"open1", "open2"}, items
    assert "closed" not in _slugs(items), "a done task must not appear in the worklist"
    assert "add freeze" in note, note          # direction-beat tasks point at freeze


def test_todo_filters_by_milestone(tmp_path):
    """covers: M2 — `--milestone` restricts the list to that milestone's tasks."""
    _bundle(tmp_path)
    items, _ = add.todo(tmp_path, milestone="m1")
    assert _slugs(items) == {"open1"}, items


def test_todo_empty_is_clear(tmp_path):
    """covers: E2 — a milestone with no active tasks returns empty items and a clear note."""
    _bundle(tmp_path)
    items, note = add.todo(tmp_path, milestone="m2")
    add._transition(tmp_path, "/tasks/open2.md", sets={"status": "done"})
    items, note = add.todo(tmp_path, milestone="m2")
    assert items == [], items
    assert "nothing open" in note.lower(), note


def test_todo_writes_nothing(tmp_path):
    """covers: M3, R:TODOWRITES — a todo mutates no bundle bytes."""
    _bundle(tmp_path)
    before = _snapshot(tmp_path)
    add.todo(tmp_path)
    assert _snapshot(tmp_path) == before, "todo must write nothing (law 3)"


def test_todo_cli_dispatches(tmp_path):
    """covers: M4 — `add todo` exits 0 and the anti-seam maps `todo`."""
    _bundle(tmp_path)
    assert _run(tmp_path, "todo") == 0
    assert _run(tmp_path, "todo", "--milestone", "m1") == 0
    assert hasattr(add, "todo")
