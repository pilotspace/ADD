"""Red suite for `uncovered-widens-to-rules` — the freeze demands what the gate would.

`uncovered_obligations` binds filled edges and probed assumptions, and its own docstring said
Musts and Rejects stay out "until the cost of widening is MEASURED rather than estimated". The
measurement, run at direction over this bundle: **0 of 105** nodes carrying RULES have an
uncovered Must or Reject. They cannot — the GATE already refuses one, so nothing could ship.

So the widening costs nothing and buys the timing. The gate is the wrong place to learn a Must
has no check: by then the whole build is done, and the fix is one line of authoring that should
have been asked for while the author was still holding the pen.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

BODY = """## CARD
goal: a real authored goal
beat: direction

## RULES
<must>
- M1 the first thing holds
{extra_must}</must>
<reject>
- R:BAD the bad thing never happens -> "BAD"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · one caller, this repo
- A2 [which] n/a · one case
- A3 [when] n/a · no boundary
- A4 [absent] n/a · no optional value
- A5 [order] n/a · one item
- A6 [experience] n/a · no human reads it

## PLAN
contract: S1 a surface

## CHECKS
{checks}red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
"""


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Widen")
    return tmp_path


def _task(root, slug, checks, extra_must="", **fields):
    cid, _ = add.new(root, "Task", slug, title=slug, depth="standard", **fields)
    path = Path(root) / cid.lstrip("/")
    n = add.read(path, "T2")
    raw = add.set_key(n["raw"], "gives", ["S1 a surface other code calls"])
    add.write(path, f"---\n{raw}\n---\n" + BODY.format(checks=checks, extra_must=extra_must))
    return cid


COVERS_ALL = "- test_one · covers: M1, R:BAD · proves both\n"


def test_freeze_refuses_an_uncovered_must(bundle):
    """covers: M1, M2, M5, R:LATEREFUSAL, A5, A6, E1 — named at the freeze, not at the gate."""
    cid = _task(bundle, "t-bare", "- test_one · covers: M1 · proves the must\n")
    node, note = add.freeze(bundle, cid, "human:t")
    assert node is None, (
        "R:LATEREFUSAL — a Reject with no covering check sealed direction; the author learns at "
        "the GATE, after the whole build")
    assert "R:BAD" in note, f"the refusal did not name the uncovered reject:\n{note}"
    assert "M1" not in note.replace("R:BAD", ""), \
        f"a COVERED must was reported as uncovered:\n{note}"
    assert "covers" in note, f"M5 — the refusal names no edit that satisfies it:\n{note}"

    # E1 both ways round: an uncovered Must is an obligation exactly as a Reject is.
    cid = _task(bundle, "t-must", "- test_one · covers: R:BAD · proves the reject\n",
                extra_must="- M2 the second thing holds\n")
    node, note = add.freeze(bundle, cid, "human:t")
    assert node is None, "an uncovered Must sealed direction"
    assert "M1" in note and "M2" in note, f"the refusal did not name both musts:\n{note}"

    # And a node that covers everything still freezes — the rung refuses, it does not block.
    cid = _task(bundle, "t-full", COVERS_ALL)
    node, note = add.freeze(bundle, cid, "human:t")
    assert node is not None, f"a fully covered node was refused:\n{note}"


def test_the_rung_reads_one_definition_of_a_rule(bundle):
    """covers: M2, R:SECOND_TRUTH — freeze and gate resolve the same ids for the same node."""
    cid = _task(bundle, "t-same", "- test_one · covers: M1 · proves the must\n")
    node_dict = add.scan(bundle)[cid]
    assert set(add.rules_of(node_dict)) <= set(add.referents_of(node_dict)), \
        "R:SECOND_TRUTH — `rules_of` is not what `referents_of` composes"
    uncovered = add.uncovered_obligations(node_dict)
    assert "R:BAD" in uncovered, (
        "R:SECOND_TRUTH — the freeze rung does not see the obligation the gate binds; two "
        f"readings of what a rule is. uncovered: {uncovered}")


def test_the_exemptions_are_unchanged(bundle):
    """covers: M4, A4, E2, E3 — nothing to cover is not something to refuse."""
    cid = _task(bundle, "t-explore", "- test_one · covers: M1 · proves the must\n", kind="explore")
    node, note = add.freeze(bundle, cid, "human:t")
    assert "R:UNCOVERED" not in str(note), f"E2 — an explore node was held to a task's shape:\n{note}"

    mcid, _ = add.new(bundle, "Milestone", "m-plain", title="M")
    node, note = add.freeze(bundle, mcid, "human:t")
    assert "R:UNCOVERED" not in str(note), f"E3 — a Milestone was refused for uncovered rules:\n{note}"

    # A4: a node with no RULES at all has nothing to cover.
    cid, _ = add.new(bundle, "Task", "t-norules", title="no rules")
    assert not add.uncovered_obligations(add.scan(bundle)[cid]), \
        "A4 — a node carrying no RULES reported uncovered obligations"


def test_the_gate_still_refuses_a_deleted_check(bundle):
    """covers: M3, A3, E4 — freeze runs EARLIER; it does not replace the gate."""
    cid = _task(bundle, "t-deleted", COVERS_ALL)
    node, note = add.freeze(bundle, cid, "human:t")
    assert node is not None, f"fixture could not freeze: {note}"

    path = Path(bundle) / cid.lstrip("/")
    body = path.read_text().replace(COVERS_ALL, "- test_one · covers: M1 · proves the must\n")
    path.write_text(body)
    assert "R:BAD" in add.uncovered_obligations(add.scan(bundle)[cid]), (
        "M3 — a check deleted AFTER the seal is invisible; the gate rung must still catch it, "
        "because freeze runs earlier and cannot see the future")
