"""Shared fixtures for the engine suite.

`freeze` refuses a node whose RULES/CHECKS are still scaffold (see `test_freeze_seal.py`), so every
test that only wants to REACH a post-freeze state has to draft the node first. That is one helper,
not a copy in each file — and keeping it here means the day the scaffold's wording changes, the
suite follows from one place.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

DRAFTED_RULES = """<must>
- M1 the admit path is atomic
</must>
<reject>
- R:OVERADMIT two callers must never both take the last token -> "OVERADMIT"
</reject>"""

DRAFTED_CHECKS = """- test_atomic_admit · covers: M1 · concurrent callers never over-admit
- test_no_overadmit · covers: R:OVERADMIT · the last token goes to exactly one caller"""


def _replace_section(body: str, heading: str, new_text: str) -> str:
    lines = body.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f"## {heading}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[:start + 1] + [new_text] + lines[end:])


def draft_direction(root, cid: str, *, rules: str = DRAFTED_RULES,
                    checks: str = DRAFTED_CHECKS) -> Path:
    """Replace a scaffold's RULES and CHECKS with real content — what a drafted node looks like."""
    path = Path(root) / cid.lstrip("/")
    node = add.read(path, "T2")
    body = _replace_section(node["body"], "RULES", rules)
    body = _replace_section(body, "CHECKS", checks + "\nred-first: every check MUST fail first.")
    path.write_text(f"---\n{node['raw']}\n---\n{body}")
    return path


@pytest.fixture
def draft():
    """Draft a node's direction so it can be frozen."""
    return draft_direction
