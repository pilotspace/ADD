"""The beat `status` and `brief` report is the beat the stamps derive.

Red-first for `/tasks/beat-read-truth.md`. The `covers:` citations live in each test's docstring.

Reproduced 2026-09-01: one `status` call after a freeze printed `[direction]` beside
`next: add brief <slug>`, while `todo` grouped the same node under `build:` and `doctor`
reported `card_drift`. Three verbs, three answers, one node. `freeze` calls `_transition`
with `appends=` and no `sets=`, so the stored `status:` field never advances.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

from conftest import draft_direction  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / ".add"
    add.init(root, profile="code", title="beat fixture")
    return root


def _author(root, slug):
    """A node authored far enough to freeze — the suite's one shared drafting helper."""
    return draft_direction(root, f"/tasks/{slug}.md")


def _status_line(text, slug):
    return next(l for l in str(text).splitlines() if slug in l)


def test_status_reports_the_derived_beat_after_a_freeze(bundle):
    """covers: M1, A5, R:BEATLIE · a frozen node reads `build`, never `direction`."""
    add.new(bundle, "Task", "sealed", depth="quick")
    _author(bundle, "sealed")
    add.freeze(bundle, "/tasks/sealed.md", by="t", authority="human")
    line = _status_line(add.status(bundle), "sealed")
    assert "[build]" in line, line
    assert "[direction]" not in line


def test_status_and_todo_agree_on_every_node(bundle):
    """covers: M5, A6 · the beat words match for every node in a fixture bundle."""
    for slug in ("alpha", "beta"):
        add.new(bundle, "Task", slug, depth="quick")
        _author(bundle, slug)
    add.freeze(bundle, "/tasks/alpha.md", by="t", authority="human")
    st, td = str(add.status(bundle)), str(add.todo(bundle))
    for slug, beat in (("alpha", "build"), ("beta", "direction")):
        assert f"[{beat}]" in _status_line(st, slug)
        assert f"{beat}:" in td


def test_brief_phases_the_build_beat_on_a_frozen_node(bundle):
    """covers: M2 · the composed prompt declares `phase="build"`."""
    add.new(bundle, "Task", "sealed", depth="quick")
    _author(bundle, "sealed")
    add.freeze(bundle, "/tasks/sealed.md", by="t", authority="human")
    assert 'phase="build"' in str(add.brief(bundle, "/tasks/sealed.md"))


def test_brief_still_honours_an_explicit_phase(bundle):
    """covers: A3 · an explicit argument wins over the derivation."""
    add.new(bundle, "Task", "sealed", depth="quick")
    _author(bundle, "sealed")
    add.freeze(bundle, "/tasks/sealed.md", by="t", authority="human")
    assert 'phase="verify"' in str(add.brief(bundle, "/tasks/sealed.md", phase="verify"))


def test_orientation_reads_no_node_body(bundle):
    """covers: M3, R:T2SCAN · the derivation is proved to touch frontmatter only."""
    add.new(bundle, "Task", "sealed", depth="quick")
    _author(bundle, "sealed")
    add.freeze(bundle, "/tasks/sealed.md", by="t", authority="human")
    node = {"fm": (add.load(bundle)["/tasks/sealed.md"]["fm"])}
    assert add._beat_of(node) == "build"


def test_a_scaffold_reports_the_scaffold_beat(bundle):
    """covers: A4, E4 · a never-authored node is not reported as direction-in-progress."""
    add.new(bundle, "Task", "untouched", depth="quick")
    assert "[scaffold]" in _status_line(add.status(bundle), "untouched")


def test_a_reopened_task_reports_its_reset_beat(bundle):
    """covers: E1 · reopen's beat survives the derivation."""
    add.new(bundle, "Task", "cycled", depth="quick")
    _author(bundle, "cycled")
    add.freeze(bundle, "/tasks/cycled.md", by="t", authority="human")
    p = bundle / "tasks" / "cycled.md"
    p.write_text(p.read_text().replace("status: direction", "status: build", 1))
    assert "[build]" in _status_line(add.status(bundle), "cycled")


def test_a_refrozen_task_reads_the_newest_seal(bundle):
    """covers: E2 · the latest freeze governs."""
    add.new(bundle, "Task", "twice", depth="quick")
    _author(bundle, "twice")
    add.freeze(bundle, "/tasks/twice.md", by="t", authority="human")
    add.freeze(bundle, "/tasks/twice.md", by="t", authority="human")
    assert "[build]" in _status_line(add.status(bundle), "twice")


def test_non_beat_node_types_are_unchanged(bundle):
    """covers: M4, A2, E3 · Spec/Persona/Project lines keep their own status field."""
    text = str(add.status(bundle))
    for slug in ("domain", "PROJECT"):
        assert "[build]" not in _status_line(text, slug)


def test_a_done_task_still_reads_done(bundle):
    """covers: E5 · a closed task is not re-derived into a beat."""
    add.new(bundle, "Task", "closed", depth="quick")
    _author(bundle, "closed")
    p = bundle / "tasks" / "closed.md"
    p.write_text(p.read_text().replace("status: direction", "status: done", 1))
    assert "[done]" in _status_line(add.status(bundle, all=True), "closed")
