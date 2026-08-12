"""The sixth sweep dimension — who receives this, and what would make it hard for them.

ADD's instruments are all about correctness. RULES is what must be true, EDGES the boundaries,
CHECKS the proof. The `experience` lens ships in both profiles, maps to UDD in the lens table, and
gets a spec file in every bundle — but nothing in the loop ever wrote it. UDD existed only as a
retrospective tag on `add learn`, filed after something had already misled someone. A task could be
provably correct and unusable, and the loop registered nothing.

The sweep is the right place for it and not a new beat, for three reasons: it already refuses (a
prose rule with no engine checkpoint does not happen — the third live demonstration of that is
recorded in `collapsed_surfaces`), it is already domain-neutral, and it already sits in the plan.
The rejected alternative was to restore the 1.7-era wireframe-and-HTML-mock step: screen-shaped, so
it says nothing about a reconciliation, and advisory, which is exactly how it silently disappeared.

`who` and `experience` are DISJOINT and the vocabulary comment says so: `who` is authorization —
whose data, which caller may act. `experience` is audience — who receives the output. Without that
line an author answers the same question twice and retires the new one as a duplicate.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tooling"))
import add  # noqa: E402

from conftest import draft_direction  # noqa: E402

NEW = "experience"

RULES = """<must>
- M1 the close pack lists every unreconciled variance
</must>
<reject>
- R:HIDE a variance must never be summarised away -> "HIDE"
</reject>"""

CHECKS = ("- test_lists_variances · covers: M1 · every unreconciled row appears\n"
          "- test_no_hidden_variance · covers: R:HIDE · nothing is rolled up out of sight\n"
          "red-first: every check MUST fail first.")

GIVES = ["S1 the month-end close pack — the reconciliation output"]


def _swept(dimensions) -> str:
    """An ASSUMPTIONS section covering S1 on exactly the dimensions given."""
    return "\n".join(
        f"- A{i} [{d}] covers: S1 · the request is silent on {d} · taking the conservative "
        f"reading -> if wrong, the close pack misstates the position"
        for i, d in enumerate(dimensions, 1))


def _task(tmp_path, dimensions, *, depth="standard"):
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "close", title="close", depth=depth, gives=GIVES)
    draft_direction(tmp_path, cid, rules=RULES, checks=CHECKS,
                    assumptions=_swept(dimensions))
    return cid


def test_experience_joins_the_closed_vocabulary():
    """covers: M1 — the name is in the engine's list, and last.

    Last because audience is the question you ask once you know what is true, and because
    appending leaves the five existing `A<n>` numbers where a reader of an older bundle
    expects to find them.
    """
    assert NEW in add.SWEEP_DIMENSIONS, (
        f"the sweep vocabulary is still {add.SWEEP_DIMENSIONS} — every dimension it carries asks "
        f"whether the output is CORRECT, and none asks who has to live with it")
    assert add.SWEEP_DIMENSIONS[-1] == NEW, (
        f"{NEW!r} is not last in {add.SWEEP_DIMENSIONS} — inserting it renumbers the scaffold "
        f"under everyone already reading `A4 [absent]` in an existing task")
    assert add.SWEEP_DIMENSIONS.index("who") < add.SWEEP_DIMENSIONS.index(NEW)


def test_freeze_refuses_an_unswept_experience_pair(tmp_path, monkeypatch):
    """covers: M1, A3 — the refusal is real, it names the pair, and it is freeze-time only."""
    older = tuple(d for d in add.SWEEP_DIMENSIONS if d != NEW)
    cid = _task(tmp_path, older)
    ok, note = add.freeze(tmp_path, cid, by="Tin Dang", authority="human")
    assert not ok, (
        "freeze accepted a task swept on every dimension EXCEPT the new one — the refusal is what "
        "makes this a question rather than a suggestion, and a suggestion is what UDD already was")
    assert f"{NEW}:S1" in note, (
        f"the refusal does not name the unswept pair: {note!r} — an author cannot act on "
        f"'something is missing'")

    # A3: the sweep runs at freeze and nowhere else, so an already-frozen task never meets the
    # sixth pair. Freezing under the OLD vocabulary models a task frozen before this upgrade.
    monkeypatch.setattr(add, "SWEEP_DIMENSIONS", older)
    ok, note = add.freeze(tmp_path, cid, by="Tin Dang", authority="human")
    assert ok, f"the same task will not freeze under the older vocabulary either: {note}"
    monkeypatch.undo()
    assert add.brief(tmp_path, cid), (
        "a task frozen before the upgrade stopped briefing once the dimension was added — the "
        "sweep is a freeze-time question, and re-asking it would invalidate in-flight work")


def test_scaffold_frames_both_halves():
    """covers: M2 — the line `new` writes asks for a recipient AND for what would make it hard.

    One half alone is answerable without doing the work. 'The controller' names a recipient and
    stops; 'it should be easy to read' names a quality and no one. The two together are what turn
    the line into a claim someone can be wrong about — which is the whole register of this section.
    """
    line = next((l for l in add.BODIES["Task"].splitlines()
                 if f"[{NEW}]" in l), None)
    assert line, (
        f"the node scaffold has no `[{NEW}]` line — the other five dimensions are scaffolded, and "
        f"the reason recorded for that is that a slot nobody composes is a slot nobody fills")
    assert "does not say" in line, (
        f"the scaffolded line has left the not-said register the other five share: {line!r} — that "
        f"frame is what stops an answer arriving as a declarative requirement")
    assert "receives" in line, f"the line does not ask WHO receives the output: {line!r}"
    assert "hard" in line, (
        f"the line does not ask what would make the output HARD to receive: {line!r} — naming an "
        f"audience without naming the difficulty is the half that can be answered without looking")


def test_depth_exemption_and_authority_floor_unchanged(tmp_path):
    """covers: M4 — this adds a question, not ceremony and not a gate.

    GREEN at freeze by design, and armed through the build: its job is to fail if the change
    widens past its contract.
    """
    cid = _task(tmp_path, (), depth="quick")
    ok, note = add.freeze(tmp_path, cid, by="Tin Dang", authority="human")
    assert ok, (
        f"a quick-depth task no longer freezes without a sweep: {note} — depth tunes ceremony and "
        f"the sweep has always been exempt there; taking that away is a different change")

    assert add.SENSITIVITY_FLOOR == {
        "mechanical": "process", "data": "plan",
        "architecture": "plan", "security": "human",
    }, (
        f"the authority floor moved: {add.SENSITIVITY_FLOOR} — the floor is computed from "
        f"sensitivity, never from how many questions the sweep asks")
