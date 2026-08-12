"""Shared fixtures for the engine suite.

`freeze` refuses a node whose RULES/CHECKS are still scaffold (see `test_freeze_seal.py`), so every
test that only wants to REACH a post-freeze state has to draft the node first. That is one helper,
not a copy in each file — and keeping it here means the day the scaffold's wording changes, the
suite follows from one place.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def git(*args, cwd):
    """Run git in a test sandbox — one helper, not a copy in each file."""
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)

DRAFTED_RULES = """<must>
- M1 the admit path is atomic
</must>
<reject>
- R:OVERADMIT two callers must never both take the last token -> "OVERADMIT"
</reject>"""

DRAFTED_CHECKS = """- test_atomic_admit · covers: M1 · concurrent callers never over-admit
- test_no_overadmit · covers: R:OVERADMIT · the last token goes to exactly one caller"""

# A COMPLETE sweep of the one drafted Must (M1) across every dimension — generated from
# the engine's own list so the suite cannot drift from it when a dimension is added.
_SILENCES = {
    "who": "whether a non-admitting caller may release someone else's token",
    "which": "whether expired tokens are counted against the limit",
    "when": "whether the limit resets on a boundary or a rolling window",
    "absent": "what a request with no token at all is admitted as",
    "order": "what breaks a tie between two simultaneous admits",
    "experience": "who reads a refused admission, or what tells them why it was refused",
}
DRAFTED_GIVES = "gives:\n  - S1 admit(token) — the admission decision"
DRAFTED_ASSUMPTIONS = "\n".join(
    f"- A{i} [{d}] covers: S1 · the spec never says {_SILENCES[d]}; taking the "
    f"conservative reading -> if wrong, the admit limit is defeated"
    for i, d in enumerate(add.SWEEP_DIMENSIONS, 1))


def _author_gives(raw: str) -> str:
    """Replace the scaffolded `gives:` placeholder with a real surface.

    `gives:` is scaffolded from 3.0.0-beta.2 on, and `freeze` refuses while it is still
    template — otherwise deleting it would switch the sweep off in one line.
    """
    if "gives:" in raw and "<" not in raw.split("gives:", 1)[1].split("\n\n")[0]:
        return raw          # the caller authored its own surfaces — never clobber them
    out, skipping = [], False
    for line in raw.splitlines():
        if line.startswith("gives:"):
            skipping = True
            out.append(DRAFTED_GIVES)
            continue
        if skipping:
            if line.startswith("  - "):
                continue
            skipping = False
        out.append(line)
    return "\n".join(out) if any(l.startswith("gives:") for l in out) \
        else "\n".join(out + [DRAFTED_GIVES])


def _replace_section(body: str, heading: str, new_text: str) -> str:
    lines = body.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f"## {heading}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[:start + 1] + [new_text] + lines[end:])


def draft_direction(root, cid: str, *, rules: str = DRAFTED_RULES,
                    checks: str = DRAFTED_CHECKS,
                    assumptions: str = DRAFTED_ASSUMPTIONS) -> Path:
    """Replace a scaffold's RULES, ASSUMPTIONS and CHECKS with real content.

    ASSUMPTIONS joined the drafted set when `freeze` started refusing an unfilled slot —
    which is why this helper is shared: eight suites reached a post-freeze state through
    it and all eight followed from this one edit.
    """
    path = Path(root) / cid.lstrip("/")
    node = add.read(path, "T2")
    body = _replace_section(node["body"], "RULES", rules)
    body = _replace_section(body, "ASSUMPTIONS", assumptions)
    body = _replace_section(body, "CHECKS", checks + "\nred-first: every check MUST fail first.")
    path.write_text(f"---\n{_author_gives(node['raw'])}\n---\n{body}")
    return path


@pytest.fixture
def draft():
    """Draft a node's direction so it can be frozen."""
    return draft_direction
