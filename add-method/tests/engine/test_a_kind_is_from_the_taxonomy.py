"""A kind the router can never match is recorded as if it routed.

`new` judges exactly one slot — `sensitivity:`, because it computes the authority floor — and
records every other field verbatim. `kind:` looked like a prose slot and is not: it is the Task
side of the routing predicate whose Persona side (`task-kinds:`) IS validated, at add.py:4438.
Two sides of one match, held to different standards.

Measured 2026-09-03, on the incumbent engine:

    $ add new Task probe --kind frontend
    created tasks/probe.md                      <- accepted
    $ add doctor
    no findings                                 <- and nothing ever says otherwise

`frontend` is a plausible word. It is not in the taxonomy, so no seeded persona and no authored
persona can ever match it, and the task silently loses its lens for the rest of its life.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


# ------------------------------------------------------------------ M1/M2 · the refusal

def test_new_refuses_a_kind_outside_the_taxonomy(tmp_path):
    """covers: M1, A3, R:SILENT_KIND — the measured `--kind frontend`."""
    root = _bundle(tmp_path)
    cid, note = add.new(root, "Task", "probe", title="p", kind="frontend")
    assert cid is None, "an unroutable kind was recorded as if it routed"
    assert "frontend" in note, f"the refusal does not name the value it refused: {note}"


def test_the_refusal_names_the_taxonomy(tmp_path):
    """covers: M2, A6 — the fix is to pick a real kind, so the message must list them."""
    root = _bundle(tmp_path)
    _, note = add.new(root, "Task", "probe", title="p", kind="frontend")
    for kind in add.PERSONA_TASK_KINDS:
        assert kind in note, f"the refusal omits `{kind}` from the taxonomy it asks for: {note}"


# ------------------------------------------------------------------ M3/M4 · what stays legal

def test_every_kind_in_the_taxonomy_is_accepted(tmp_path):
    """covers: M3, A2 — enumerated from the CONSTANT the router reads, never a hand list.

    A hand list is how the two sides drifted in the first place; a guard that repeats the
    mistake it fixes is not a guard.
    """
    root = _bundle(tmp_path)
    for i, kind in enumerate(add.PERSONA_TASK_KINDS):
        cid, note = add.new(root, "Task", f"ok{i}", title="p", kind=kind)
        assert cid, f"the taxonomy's own `{kind}` was refused: {note}"


def test_an_absent_kind_is_untouched(tmp_path):
    """covers: M4, A4, E1 — absence is not an unreadable value.

    `kind:` is optional. Refusing None or "" would refuse every node ever created without
    `--kind`, which is most of them.
    """
    root = _bundle(tmp_path)
    assert add.new(root, "Task", "none", title="p")[0], "a node with no kind was refused"
    assert add.new(root, "Task", "empty", title="p", kind="")[0], "an empty kind was refused"
    assert add.new(root, "Task", "nil", title="p", kind=None)[0], "an explicit None was refused"


# ------------------------------------------------------------------ counter-guards

def test_a_refused_kind_writes_nothing(tmp_path):
    """covers: M1, A5, E2 — a refusal that left a file behind is not a refusal.

    E2 is the near-miss: `Feature` differs from `feature` only in case, and the router matches
    on the exact string, so it is exactly as unroutable as `frontend`.
    """
    root = _bundle(tmp_path)
    for bad in ("frontend", "Feature", "SECURITY", "feature "):
        cid, _ = add.new(root, "Task", "ghost", title="p", kind=bad)
        assert cid is None, f"{bad!r} was accepted"
        assert not (Path(root) / "tasks" / "ghost.md").exists(), \
            f"{bad!r} was refused but wrote tasks/ghost.md anyway"
