"""Direction's grounding sweep is instructed to go out in ONE turn.

THE DEFECT THIS CLOSES. The pay1-4 campaign (2026-07-26) folded ADD's own
transcripts into a call-stack flamegraph: across 209 direction turns, ZERO
emitted more than one tool call. 7.3 of direction's 31 minutes went to a
strictly serial chain of Reads, each paying a full turn's context for one
file. The guide already mandates "ONE silent draft" for the WRITE side of
direction and said nothing at all about the READ side.

The guard enumerates the skill trees from the repo layout rather than naming
them, so a fourth tree is covered the day it lands — three hand-mirrored trees
with no parity test is the lock-reclaim failure class, and it has already cost
this project a publish.
"""
from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

# The anchor phrase the clause is identified by. Short and distinctive so a
# reword of the surrounding prose does not silently drop the instruction.
BATCH_ANCHOR = "Batch the sweep"
# The clause must say WHY, not just what — an unexplained rule is the first
# thing a compression pass deletes.
REASON_ANCHOR = "pays a full turn's context"


def direction_guides(root: pathlib.Path) -> list[pathlib.Path]:
    """Every `phases/direction.md` shipped by any skill tree under `root`."""
    found = [
        *root.glob(".claude/skills/add/phases/direction.md"),
        *root.glob("*/skill/add/phases/direction.md"),
        *root.glob("*/src/*/_bundled/skill/add/phases/direction.md"),
    ]
    return sorted(set(found))


def _live_guides() -> list[pathlib.Path]:
    guides = direction_guides(REPO)
    assert len(guides) >= 3, f"expected the three skill trees, found {guides}"
    return guides


@pytest.mark.parametrize("guide", _live_guides(), ids=lambda p: str(p.relative_to(REPO)))
def test_every_skill_tree_direction_guide_carries_the_batch_clause(guide):
    text = guide.read_text()
    assert BATCH_ANCHOR in text, (
        f"batch_clause_drift: {guide.relative_to(REPO)} has no batching instruction — "
        "an install would ship guidance the repo does not have")


@pytest.mark.parametrize("guide", _live_guides(), ids=lambda p: str(p.relative_to(REPO)))
def test_batch_clause_sits_in_the_grounding_section(guide):
    text = guide.read_text()
    head, _, tail = text.partition("### Grounding")
    assert tail, f"{guide} has no '### Grounding' section to anchor to"
    section = tail.split("\n### ", 1)[0]
    assert BATCH_ANCHOR in section, (
        "the clause must live where the grounding sweep is described, not wherever "
        "it happened to be pasted")


@pytest.mark.parametrize("guide", _live_guides(), ids=lambda p: str(p.relative_to(REPO)))
def test_batch_clause_states_the_reason(guide):
    assert REASON_ANCHOR in guide.read_text(), (
        "the clause states an instruction with no mechanism — 'because…' is what "
        "survives the next compression pass")


def test_the_direction_guides_are_byte_identical():
    guides = _live_guides()
    bodies = {g: g.read_bytes() for g in guides}
    first = guides[0]
    drifted = [str(g.relative_to(REPO)) for g in guides[1:] if bodies[g] != bodies[first]]
    assert not drifted, (
        f"batch_clause_drift: {drifted} differ from {first.relative_to(REPO)} — "
        "hand-mirrored trees with no parity test is the lock-reclaim failure class")


def test_guard_enumerates_trees_from_disk(tmp_path):
    # A fourth tree dropped in must be covered without editing this file.
    newcomer = tmp_path / "another-pkg/skill/add/phases/direction.md"
    newcomer.parent.mkdir(parents=True)
    newcomer.write_text("### Grounding\nBatch the sweep\n")
    assert direction_guides(tmp_path) == [newcomer]


def test_enumeration_is_not_vacuous(tmp_path):
    # An empty tree must yield nothing, so the parametrized guards above cannot
    # pass by finding no guides at all.
    assert direction_guides(tmp_path) == []
