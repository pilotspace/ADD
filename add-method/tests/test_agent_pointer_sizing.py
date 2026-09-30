"""The managed block is the only ADD text a Cursor/Codex/Copilot user's agent reads before it acts.

It must send the agent to the skill file and the bundle, carry the sizing rule (so a one-line fix
does not get the full loop), name no retired engine command, and be rewritten in place — never
duplicated, never touching the user's own text around it. A 3.x block (whose BEGIN marker named
the retired `sync-guidelines` verb) is recognized and replaced, not appended beside.
"""
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "src"))
from add_method import _installer  # noqa: E402

LEGACY_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"
RETIRED = ("cli.py", "add.py", ".add/tooling", "add-worker", "add-advisor", "sync-guidelines",
           "add learn", "add status", "graph.json")


def block() -> str:
    return _installer._pointer_block()


def test_the_block_points_at_the_skill_and_the_bundle():
    text = block()
    assert text.startswith(_installer._GUIDE_BEGIN + "\n") and text.endswith(_installer._GUIDE_END)
    assert ".claude/skills/add/SKILL.md" in text
    assert ".add/PROJECT.md" in text
    assert "/add" in text


def test_the_block_carries_the_sizing_rule_and_the_floor():
    text = block()
    assert re.search(r"[^.\n]*3 adjacent files[^.\n]*\.", text), "no sizing sentence"
    assert re.search(r"security.{0,5}data.{0,5}architecture", text, re.I), "the floor is not named"
    assert "Task" in text


def test_the_block_names_no_retired_engine_command():
    hits = [w for w in RETIRED if w in block()]
    assert not hits, f"the managed block still names {hits}"
    assert "sync-guidelines" not in _installer._GUIDE_BEGIN


def test_the_block_carries_the_rules_that_bind():
    """The same rules the repo's own blocks carry (tests/test_shipped_docs.py)."""
    text = block().lower()
    for phrase in ("invariants", "never weaken", "hard-stop"):
        assert phrase in text, f"the managed block drops the rule about `{phrase}`"


def test_the_block_passes_the_book_linter():
    sys.path.insert(0, str(PKG / "scripts"))
    import book_lint
    assert not book_lint.retired_verb_hits(block()), "the managed block names a retired verb"
    assert not book_lint.engine_name_hits(block()), "the managed block names the engine"


def test_the_block_stays_short():
    assert len(block().splitlines()) <= 16


def test_a_new_file_gets_the_block(tmp_path):
    path = tmp_path / "AGENTS.md"
    assert _installer._write_pointer(path) == "created"
    assert path.read_text(encoding="utf-8") == block() + "\n"
    assert _installer._write_pointer(path) == "unchanged"


def test_user_text_outside_the_markers_survives(tmp_path):
    path = tmp_path / "CLAUDE.md"
    path.write_text("before\n" + _installer._GUIDE_BEGIN + "\nold\n" + _installer._GUIDE_END
                    + "\nafter\n", encoding="utf-8")
    assert _installer._write_pointer(path) == "updated"
    text = path.read_text(encoding="utf-8")
    assert text == "before\n" + block() + "\nafter\n"
    assert (tmp_path / "CLAUDE.md.bak").is_file(), "a real change keeps a rollback copy"


def test_a_3x_block_is_replaced_in_place(tmp_path):
    path = tmp_path / "AGENTS.md"
    path.write_text("mine\n\n" + LEGACY_BEGIN + "\nrun `python3 .add/tooling/cli.py status`\n"
                    "<!-- ADD:END -->\n\nalso mine\n", encoding="utf-8")
    assert _installer._write_pointer(path) == "updated"
    assert path.read_text(encoding="utf-8") == "mine\n\n" + block() + "\n\nalso mine\n"


def test_a_dangling_begin_never_swallows_user_text(tmp_path):
    path = tmp_path / "AGENTS.md"
    path.write_text("top\n" + _installer._GUIDE_BEGIN + "\nhalf a block\nuser text\n", encoding="utf-8")
    assert _installer._write_pointer(path) == "updated"
    first = path.read_text(encoding="utf-8")
    assert first.startswith("top\n" + _installer._GUIDE_BEGIN + "\nhalf a block\nuser text\n")
    assert first.endswith(block() + "\n")
    assert _installer._write_pointer(path) == "unchanged", "a second run moved or ate text"
    assert path.read_text(encoding="utf-8") == first
