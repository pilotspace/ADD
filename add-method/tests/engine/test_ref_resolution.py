"""A name an operator actually types resolves, and the refusal that lists alternatives is bounded.

Red-first for `/tasks/ref-resolution-accepts-what-an-operator-types.md`. Two review findings:

* `resolve_ref` routed anything ending `.md` to the cid branch with no fallback, so
  `add show okf-graph-lookup.md` REFUSED a node that exists. The refusal asserted something
  false about the bundle — the exact failure the function's own docstring says it was written
  to end. Tab-completing a filename is the likeliest way to type it.
* the ambiguity refusal listed every candidate uncapped. On the live bundle `add show 1` printed
  78 lines and grew with the task count, on a verb whose sibling path is capped precisely so one
  read cannot cost unbounded context (R:DEPTHCAP).
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

BOUND = 8        # the candidate ceiling, BY VALUE — never read from the module under test


@pytest.fixture
def bundle(tmp_path):
    """One milestone, one task, and a deliberate basename collision across directories."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="ref fixture")
    add.new(root, "Milestone", "m-one", title="a milestone")
    add.new(root, "Task", "t-one", title="a task", milestone="m-one")
    add.new(root, "Persona", "twin", title="a persona named twin")
    # Written directly: `new` REFUSES a slug already taken, so the collision cannot be built
    # through the verb. The collision is across DIRECTORIES, which is the real shape.
    (root / "tasks" / "twin.md").write_text(
        (root / "personas" / "twin.md").read_text(encoding="utf-8").replace(
            "type: Persona", "type: Task"), encoding="utf-8")
    return root


def test_a_filename_that_names_one_node_resolves(bundle):
    """M1, R:FALSEREFUSAL, E1 — the node exists; the old code said it did not."""
    cid, note = add.resolve_ref(bundle, "t-one.md")
    assert cid == "/tasks/t-one.md", f"a filename naming a real node was refused: {note}"


def test_a_filename_naming_several_still_refuses(bundle):
    """R:GUESSAGAIN, E2 — a collision refuses and shows what it collided with."""
    cid, note = add.resolve_ref(bundle, "twin.md")
    assert cid is None, "an ambiguous filename resolved to one node"
    assert "/tasks/twin.md" in note and "/personas/twin.md" in note, \
        f"the refusal does not list the candidates:\n{note}"


def test_a_filename_naming_nothing_still_refuses(bundle):
    """M2, E3 — the fallback adds answers; it never invents one."""
    cid, note = add.resolve_ref(bundle, "no-such-file.md")
    assert cid is None, "a filename naming nothing resolved"
    assert "next:" in note, f"the refusal names no fix:\n{note}"


def test_a_ref_with_a_separator_is_a_path(bundle):
    """A2, E4 — a value carrying `/` was meant literally; second-guessing it reopens guessing."""
    cid, note = add.resolve_ref(bundle, "elsewhere/t-one.md")
    assert cid is None, "a path-shaped ref fell back to basename matching"


def test_the_candidate_list_is_bounded(bundle):
    """M3, R:UNBOUNDED, E5, A5 — `add show 1` printed 78 lines on the live bundle."""
    seed = (bundle / "tasks" / "t-one.md").read_text(encoding="utf-8")
    for i in range(BOUND + 4):
        d = bundle / "tasks" / f"c{i}"
        d.mkdir(exist_ok=True)
        (d / "same.md").write_text(seed, encoding="utf-8")
    cid, note = add.resolve_ref(bundle, "same")
    assert cid is None, "the collision resolved, so the bound could not be observed"
    # cid lines only: the truncation line is not a candidate, however it is bulleted.
    listed = [ln for ln in note.splitlines()
              if ln.strip().startswith("\u00b7") and "/" in ln]
    assert len(listed) == BOUND, f"the refusal listed {len(listed)} candidates, not {BOUND}"
    assert "and 4 more" in note, f"the refusal truncated without counting the rest:\n{note}"


def test_the_bound_is_pinned_by_value():
    """M4 — stated here as a literal, never read out of the module it guards (R:SELFPIN)."""
    assert add.RESOLVE_CANDIDATES == BOUND, \
        f"the candidate bound moved to {add.RESOLVE_CANDIDATES}; this check states {BOUND}"


def test_refs_that_resolved_before_resolve_the_same(bundle):
    """M5, A4 — the fallback only ever ADDS answers; it changes none."""
    assert add.resolve_ref(bundle, "t-one")[0] == "/tasks/t-one.md"
    assert add.resolve_ref(bundle, "/tasks/t-one.md")[0] == "/tasks/t-one.md"
    assert add.resolve_ref(bundle, "")[0] is None
    assert add.resolve_ref(bundle, "nothing-at-all")[0] is None
