"""A slug names ONE node, or a receipt crosses nodes and `R:GREENLIE` stops binding.

Three engine facts compose into a hole. `new` refuses a collision with `path.exists()` inside
the TYPE'S OWN directory, so `/tasks/pay.md` and `/milestones/pay.md` coexist. `run` writes to
`tasks/{slug}.d/runs` and `latest_receipt` reads the same path — both from the BARE slug,
whatever directory the cid lives in. And `cli._resolve` returns the first scan-order match,
which puts `/milestones/` ahead of `/tasks/`.

Measured 2026-09-02: a red Task was walked to `done` on a receipt produced by a Milestone that
merely shared its slug. `gate` refused the honest PASS (`the receipt records a failed run`) and
accepted the borrowed one. The refusal was not defeated by an argument; it read a different
node's evidence and could not tell.

The rule pinned here is the cheap one: a slug is unique across the whole bundle, so the receipt
path is unambiguous by construction. Widening the receipt path instead would leave `_resolve`
silently retargeting every other verb.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


# ------------------------------------------------- M1 · one slug, one node

def test_new_refuses_a_slug_taken_by_another_type(tmp_path):
    """covers: M1, R:DUPSLUG — the collision the per-directory check could not see."""
    root = _bundle(tmp_path)
    cid, note = add.new(root, "Task", "pay", title="pay")
    assert cid, note

    clash, note = add.new(root, "Milestone", "pay", title="pay")
    assert clash is None, "a Milestone took a slug a Task already holds"
    assert not (root / "milestones" / "pay.md").exists(), "it reported a refusal and wrote anyway"


def test_the_refusal_names_the_node_that_holds_it(tmp_path):
    """covers: M2 — the fix is to pick another slug, so say which node is in the way."""
    root = _bundle(tmp_path)
    add.new(root, "Task", "pay", title="pay")
    _, note = add.new(root, "Milestone", "pay", title="pay")
    assert "/tasks/pay.md" in str(note), f"the refusal does not name the holder: {note!r}"
    assert "next:" in str(note), note


def test_collision_is_refused_in_both_directions(tmp_path):
    """covers: M1 — the guard is a bundle-wide census, not a Task-vs-Milestone special case."""
    root = _bundle(tmp_path)
    add.new(root, "Milestone", "ship", title="ship")
    clash, _ = add.new(root, "Task", "ship", title="ship")
    assert clash is None, "a Task took a slug a Milestone already holds"

    add.new(root, "Persona", "lens", title="lens")
    clash, _ = add.new(root, "Task", "lens", title="lens")
    assert clash is None, "a Task took a slug a Persona already holds"


def test_distinct_slugs_are_untouched(tmp_path):
    """covers: M3 — the guard refuses collisions, not creation."""
    root = _bundle(tmp_path)
    for t, s in (("Task", "a"), ("Milestone", "b"), ("Persona", "c"), ("Task", "d")):
        cid, note = add.new(root, t, s, title=s)
        assert cid, f"{t} {s} was refused: {note!r}"


# ------------------------------------------------- M4 · the consequence that was measured

def test_a_receipt_cannot_be_earned_by_a_different_node(tmp_path):
    """covers: M4, R:GREENLIE — the measured walk: a red task closing on a borrowed receipt."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "pay", title="pay")
    add.run(root, cid, ["false"])                      # the task's own run is RED

    # The borrowed green receipt can only exist if the slug collision does.
    other, _ = add.new(root, "Milestone", "pay", title="pay")
    assert other is None, "the collision that made the borrowed receipt possible was allowed"

    receipt, receipt_cid = add.latest_receipt(root, cid)
    assert receipt is not None, "the task lost its own receipt"
    assert str(receipt.get("exit")) != "0", (
        f"the task's latest receipt is not its own failed run: {receipt!r} at {receipt_cid}")
