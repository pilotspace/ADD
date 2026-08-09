"""A Persona is a living document, not a task — `add new Persona` must not stamp a task lifecycle.

Surfaced while wiring the persona seed flow (2026-08-06): `new()` set `status: direction` and a
`next: add freeze` affordance on every type, so a seeded persona showed in `add status` as
`[direction] Persona` — a node that never freezes wearing a task's lifecycle. Non-lifecycle types
(Persona, Prompt, Run) carry no task status; a Persona gets the four-part scaffold, not the generic CARD.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

PARTS = ("Identity", "Critical Rules", "Default Requirement", "Success Metrics")


def _fm(text: str) -> str:
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def test_persona_carries_no_task_status(tmp_path):
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Persona", "backend-systems", title="backend lens")
    fm = _fm((tmp_path / cid.lstrip("/")).read_text(encoding="utf-8"))
    assert not re.search(r"^status:", fm, re.M), \
        "a Persona is a living doc; it must carry no task-lifecycle status (shows [—] like a Spec)"


def test_persona_next_affordance_is_not_freeze(tmp_path):
    add.init(tmp_path, "code", "T")
    _, note = add.new(tmp_path, "Persona", "sec-rev", title="security lens")
    assert "freeze" not in note, "freeze is meaningless for a Persona — its `next:` must not name it"


def test_persona_scaffold_has_the_four_parts(tmp_path):
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Persona", "frontend-ux", title="ux lens")
    text = (tmp_path / cid.lstrip("/")).read_text(encoding="utf-8")
    for part in PARTS:
        assert re.search(rf"^#+\s*{re.escape(part)}", text, re.M), \
            f"the Persona scaffold omits the `{part}` part (personas.md schema)"


def test_task_still_gets_direction_and_freeze(tmp_path):
    """Regression: the lifecycle types are left exactly as they were."""
    add.init(tmp_path, "code", "T")
    cid, note = add.new(tmp_path, "Task", "add-thing", title="Add thing")
    fm = _fm((tmp_path / cid.lstrip("/")).read_text(encoding="utf-8"))
    assert re.search(r"^status:\s*direction", fm, re.M), "a Task must still start at direction"
    assert "add freeze add-thing" in note, "a Task's `next:` must still name freeze"
