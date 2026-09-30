"""The repository's own agent pointers lead to the 4.0 method, not to a CLI that no longer exists."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _add_block(name: str) -> str:
    text = (ROOT / name).read_text(encoding="utf-8")
    assert "ADD:BEGIN" in text and "ADD:END" in text, f"{name} has no managed ADD block"
    return text[text.index("ADD:BEGIN"):text.index("ADD:END")]


def test_pointers_orient_on_the_bundle():
    for name in ("AGENTS.md", "CLAUDE.md"):
        block = _add_block(name)
        assert ".add/PROJECT.md" in block, f"{name}'s ADD block does not orient on PROJECT.md"


def test_pointers_name_no_engine():
    for name in ("AGENTS.md", "CLAUDE.md"):
        block = _add_block(name)
        for stale in ("cli.py", "add.py", ".add/tooling", "add-worker", "add-advisor"):
            assert stale not in block, f"{name}'s ADD block still names {stale}"
