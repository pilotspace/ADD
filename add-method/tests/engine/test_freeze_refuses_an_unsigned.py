"""Red direction check for freeze-refuses-an-unsigned."""
import pytest
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
from conftest import draft_direction  # noqa: E402


def _human_floor_task(root, slug="sensitive"):
    """An authored human-floor task with no separate interview question."""
    cid, _ = add.new(root, "Task", slug, title=slug, scope=["src/auth/token.py"])
    task = draft_direction(root, cid, assumptions="",
                           rules="<must>\n- M1 the fixture reaches freeze (from: fixture)\n</must>\n<reject>\n</reject>",
                           checks="- test_fixture · covers: M1 · fixture")
    task.write_text(task.read_text().replace("## PLAN", "## PLAN\nregression: none · fixture", 1), encoding="utf-8")
    return cid, task


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_default_cli_human_floor_refuses_without_a_write(tmp_path):
    """covers: M1, R:UNSIGNED, E1 — a bare human-floor freeze writes neither bytes nor stamps."""
    root = tmp_path / ".add"
    add.init(root, "code", "unsigned")
    index = add.read(root / "index.md", "T2")
    add.write(root / "index.md", "---\n" + add.set_key(index["raw"], "sensitive_paths", "[src/auth/**]")
              + "\n---\n" + index["body"])
    cid, task = _human_floor_task(root)
    before = task.read_bytes()
    node, note = add.freeze(root, cid, by="cli")
    assert node is None and "R:UNSIGNED" in note, f"a default signer approved a human floor: {note!r}"
    assert task.read_bytes() == before, "R:UNSIGNED wrote a stamp despite refusing"


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_non_lifecycle_freeze_refuses_without_a_write(tmp_path):
    """covers: M2, R:NOTATASK, E2 — a Persona has no lifecycle seal and stays byte-identical."""
    root = tmp_path / ".add"
    add.init(root, "code", "not a task")
    persona, _ = add.new(root, "Persona", "not-a-task", title="not a task")
    path = root / persona.lstrip("/")
    before = path.read_bytes()
    node, note = add.freeze(root, persona, by="human:T", authority="human")
    assert node is None and "R:NOTATASK" in note, f"a non-lifecycle document was frozen: {note!r}"
    assert path.read_bytes() == before, "R:NOTATASK wrote a stamp despite refusing"


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_explicit_empty_or_placeholder_human_signer_refuses_without_a_write(tmp_path):
    """covers: M1 — a human floor needs an explicit non-placeholder signer claim."""
    root = tmp_path / ".add"
    add.init(root, "code", "empty signer")
    index = add.read(root / "index.md", "T2")
    add.write(root / "index.md", "---\n" + add.set_key(index["raw"], "sensitive_paths", "[src/auth/**]")
              + "\n---\n" + index["body"])
    for n, signer in enumerate(("", "human:", "human:<name>", "plan:T")):
        cid, task = _human_floor_task(root, f"signer-{n}")
        before = task.read_bytes()
        node, note = add.freeze(root, cid, by=signer)
        assert node is None and "R:UNSIGNED" in note, f"invalid signer {signer!r} was accepted: {note!r}"
        assert task.read_bytes() == before, f"invalid signer {signer!r} wrote a stamp"


def test_explicit_human_signer_is_recorded_as_a_claim(tmp_path):
    """covers: M1, A1, A3 — a deliberate human claim passes without an authentication claim."""
    root = tmp_path / ".add"
    add.init(root, "code", "named signer")
    index = add.read(root / "index.md", "T2")
    add.write(root / "index.md", "---\n" + add.set_key(index["raw"], "sensitive_paths", "[src/auth/**]")
              + "\n---\n" + index["body"])
    cid, task = _human_floor_task(root)
    node, note = add.freeze(root, cid, by="human:T", authority="human")
    assert node, note
    stamp = add.read(task, "T2")["fm"]["verified"][-1]
    assert stamp["by"] == "human:T" and stamp["authority"] == "human"
    assert "authenticated" not in note.lower(), "the local notary claimed signer authentication"
