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


def test_todo_beat_is_stamp_derived(tmp_path, draft):
    """covers: M5, E3 — the beat comes from the stamps, not the `status` field.

    `status` stays `direction` from creation until done, so reading it made every open task report
    the direction beat: a frozen task awaiting a run, and a task with a receipt awaiting its gate,
    were both listed as `direction · add freeze`. A cold resume followed that back to the start.
    """
    _bundle(tmp_path)
    draft(tmp_path, "/tasks/open1.md")
    add.freeze(tmp_path, "/tasks/open1.md", by="human:t")
    items, note = add.todo(tmp_path)
    beats = {cid.rsplit("/", 1)[-1][:-3]: st for cid, st, _ in items}
    verbs = {cid.rsplit("/", 1)[-1][:-3]: nxt for cid, _, nxt in items}
    assert beats["open1"] == "build", f"a frozen task is at the build beat: {beats}"
    assert beats["open2"] == "direction", f"an unfrozen task stays at direction: {beats}"
    assert "add run" in verbs["open1"], f"the build beat points at the run: {verbs}"
    assert "add freeze" in verbs["open2"], f"the direction beat points at the freeze: {verbs}"
    assert "build:" in note, note


def test_todo_receipt_moves_the_beat_to_verify(tmp_path, draft):
    """covers: M5 — a recorded receipt puts the task at verify, pointing at the gate."""
    _bundle(tmp_path)
    draft(tmp_path, "/tasks/open1.md")
    add.freeze(tmp_path, "/tasks/open1.md", by="human:t")
    add.run(tmp_path, "/tasks/open1.md", [sys.executable, "-c", "pass"], cwd=tmp_path.parent)
    items, note = add.todo(tmp_path)
    beats = {cid.rsplit("/", 1)[-1][:-3]: st for cid, st, _ in items}
    verbs = {cid.rsplit("/", 1)[-1][:-3]: nxt for cid, _, nxt in items}
    assert beats["open1"] == "verify", f"a task with a receipt is at verify: {beats}"
    assert "add gate" in verbs["open1"], f"the verify beat points at the gate: {verbs}"


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
