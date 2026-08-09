"""`add wave <milestone>` — the DAG-derived parallel plan.

A wave is only safe to run concurrently when its streams are BOTH mutually independent (no
dependency path between them — an antichain in the task DAG) AND write-disjoint (no shared `scope:`
path). `wave` proves both from the graph: it derives topological levels (each a maximal antichain),
and refuses a cycle (R:CYCLE), an intra-wave dependency (R:INTRADEP), or overlapping scope (R:OVERLAP).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _task(root, slug, milestone, deps=(), scope=()):
    add.new(root, "Task", slug, title=slug, milestone=milestone, scope=list(scope))
    if deps:
        p = root / "tasks" / f"{slug}.md"
        n = add.read(p, "T2")
        val = "[" + ", ".join(f"{d}.md" for d in deps) + "]"  # edges() needs a `.md` ref
        add.write(p, f"---\n{add.set_key(n['raw'], 'depends_on', val)}\n---\n{n['body']}")


def _milestone(root):
    add.init(root, "code", "T")
    add.new(root, "Milestone", "m", title="m")


def test_wave_levels_are_topological(tmp_path):
    """covers: M1 — a chain a→b→c yields ordered singleton levels; an independent task shares level 0."""
    _milestone(tmp_path)
    _task(tmp_path, "a", "m")
    _task(tmp_path, "b", "m", deps=["a"])
    _task(tmp_path, "c", "m", deps=["b"])
    _task(tmp_path, "x", "m")  # independent of the chain
    levels, note = add.wave(tmp_path, "m")
    assert levels is not None, note
    assert set(levels[0]) == {"a", "x"}, f"a and x are independent → same first level: {levels}"
    assert levels[1] == ["b"] and levels[2] == ["c"], f"the chain must sequence: {levels}"


def test_explicit_wave_sets_active_wave(tmp_path):
    """covers: M2 — a valid antichain records `active_wave:` on the milestone so join can find it."""
    _milestone(tmp_path)
    _task(tmp_path, "a", "m", scope=["a.py"])
    _task(tmp_path, "x", "m", scope=["x.py"])
    picks, note = add.wave(tmp_path, "m", streams=["a", "x"])
    assert picks == ["a", "x"], note
    fm, _ = add.parse((tmp_path / "milestones" / "m.md").read_text(encoding="utf-8"))
    assert fm.get("active_wave") == ["a", "x"], f"the wave must be recorded on the milestone: {fm.get('active_wave')}"


def test_intra_wave_dependency_refused(tmp_path):
    """covers: M3, R:INTRADEP — two streams with a dependency path between them cannot share a wave."""
    _milestone(tmp_path)
    _task(tmp_path, "a", "m", scope=["a.py"])
    _task(tmp_path, "b", "m", deps=["a"], scope=["b.py"])
    picks, note = add.wave(tmp_path, "m", streams=["a", "b"])
    assert picks is None and "R:INTRADEP" in note, note


def test_overlapping_scope_refused(tmp_path):
    """covers: M4, R:OVERLAP — independence is not enough; two streams must not write the same file."""
    _milestone(tmp_path)
    _task(tmp_path, "a", "m", scope=["shared.py"])
    _task(tmp_path, "x", "m", scope=["shared.py"])  # independent, but both write shared.py
    picks, note = add.wave(tmp_path, "m", streams=["a", "x"])
    assert picks is None and "R:OVERLAP" in note, note


def test_dependency_cycle_refused(tmp_path):
    """covers: M5, R:CYCLE — a cyclic graph has no defined parallel plan."""
    _milestone(tmp_path)
    _task(tmp_path, "a", "m", deps=["b"], scope=["a.py"])
    _task(tmp_path, "b", "m", deps=["a"], scope=["b.py"])
    picks, note = add.wave(tmp_path, "m", streams=["a", "b"])
    assert picks is None and "R:CYCLE" in note, note
