"""The front doors must not send a reader to an engine that no longer exists.

`README.md` and `GETTING-STARTED.md` ship in BOTH artifacts (the npm `files` list and the wheel),
and the README is the landing copy on both registry pages. The repo root carries its own README,
the quickstart pointer, the beyond-code walkthrough, and the contributor docs. ADD 4.0 removed the
CLI engine: `add status`, `add freeze`, `add gate`, `.add/tooling/cli.py` all point at nothing now.
A reader who follows one gets "command not found" — or, worse, a stale vendored copy.

The same detector that holds the book (`scripts/book_lint.py`) holds these pages: no retired verb
stated as a command, and no removed engine file named. The managed ADD block in the repo's own
CLAUDE.md / AGENTS.md / .clinerules — the only ADD text a non-Claude agent reads — must point at the skill, not
at a CLI.
"""
from __future__ import annotations

import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
sys.path.insert(0, str(PKG / "scripts"))
import book_lint  # noqa: E402

FRONT_DOORS = (PKG / "README.md", PKG / "GETTING-STARTED.md", PKG / "BEYOND-CODE.md",
               ROOT / "README.md", ROOT / "GETTING-STARTED.md", ROOT / "CONTRIBUTING.md",
               ROOT / "RELEASING.md")
AGENT_FILES = (ROOT / "CLAUDE.md", ROOT / "AGENTS.md", ROOT / ".clinerules")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def test_front_doors_instruct_no_retired_verb():
    hits = {_rel(p): h for p in FRONT_DOORS
            if (h := book_lint.retired_verb_hits(p.read_text(encoding="utf-8")))}
    assert not hits, f"front-door docs tell the reader to run a retired 3.x verb: {hits}"


def test_front_doors_never_name_the_engine():
    hits = {_rel(p): h for p in FRONT_DOORS
            if (h := book_lint.engine_name_hits(p.read_text(encoding="utf-8")))}
    assert not hits, f"front-door docs name removed engine files or roster agents: {hits}"


def _managed_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    assert "ADD:BEGIN" in text and "ADD:END" in text, f"{_rel(path)} has no managed ADD block"
    begin = text.index("\n", text.index("ADD:BEGIN")) + 1     # the marker line is an opaque key
    return text[begin:text.index("<!-- ADD:END")]


def test_agent_blocks_point_at_the_skill_not_a_cli():
    for path in AGENT_FILES:
        block = _managed_block(path)
        assert not book_lint.retired_verb_hits(block), f"{_rel(path)}: block names a retired verb"
        assert not book_lint.engine_name_hits(block), f"{_rel(path)}: block names the engine"
        assert ".add/PROJECT.md" in block, f"{_rel(path)}: block does not say where to orient"
        assert "SKILL.md" in block, f"{_rel(path)}: block does not point at the skill file"


def test_agent_blocks_carry_the_rules_that_bind():
    for path in AGENT_FILES:
        block = " ".join(_managed_block(path).lower().split())
        for phrase in ("invariants", "never weaken", "hard-stop"):
            assert phrase in block, f"{_rel(path)}: block drops the rule about `{phrase}`"
