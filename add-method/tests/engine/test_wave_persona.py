"""`add wave <m> --streams a:persona,b:persona` — persona-assigned waves (A3, task 1).

A wave stream may carry a lens: `slug:persona`. The engine validates the persona resolves to a
Persona node, stamps `persona:` on that stream's task node, and records the lens per stream in the
milestone `active_wave:`. NO-EXEC — the stamp is a record, never an execution. An unknown persona
refuses (R:BADPERSONA) and writes nothing.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _setup(tmp_path):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "a", title="a", milestone="m", scope=["fa.py"])
    add.new(tmp_path, "Task", "b", title="b", milestone="m", scope=["fb.py"])
    add.new(tmp_path, "Persona", "backend-systems", title="backend-systems")
    add.new(tmp_path, "Persona", "security-reviewer", title="security-reviewer")


def _node(root, slug):
    return add.read(root / "tasks" / f"{slug}.md", "T2")


def test_wave_stamps_persona_on_each_stream(tmp_path):
    """covers: M1 — a `a:backend-systems,b:security-reviewer` wave stamps each stream node."""
    _setup(tmp_path)
    picks, note = add.wave(tmp_path, "m", streams=["a:backend-systems", "b:security-reviewer"])
    assert picks is not None, note
    assert (_node(tmp_path, "a")["fm"] or {}).get("persona") == "backend-systems", note
    assert (_node(tmp_path, "b")["fm"] or {}).get("persona") == "security-reviewer", note


def test_active_wave_records_the_lens_per_stream(tmp_path):
    """covers: M2 — the milestone active_wave holds the slug:persona tokens."""
    _setup(tmp_path)
    add.wave(tmp_path, "m", streams=["a:backend-systems", "b:security-reviewer"])
    m = add.read(tmp_path / "milestones" / "m.md", "T2")
    aw = str((m["fm"] or {}).get("active_wave"))
    assert "a:backend-systems" in aw and "b:security-reviewer" in aw, aw


def test_wave_refuses_an_unknown_persona(tmp_path):
    """covers: R:BADPERSONA — an unresolvable lens refuses and writes no active_wave."""
    _setup(tmp_path)
    picks, note = add.wave(tmp_path, "m", streams=["a:backend-systems", "b:no-such-lens"])
    assert picks is None and "R:BADPERSONA" in note, note
    m = add.read(tmp_path / "milestones" / "m.md", "T2")
    assert (m["fm"] or {}).get("active_wave") is None, "a refused wave must not record active_wave"
