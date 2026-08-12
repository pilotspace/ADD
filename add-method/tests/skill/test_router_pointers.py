"""The always-loaded router must be honest about profiles, and must not orphan its own refs.

`test_every_wired_verb_is_documented` (test_surface.py) already guards the ORPHAN direction for
VERBS — a verb the engine ships that no doc names. Nothing guarded it for REFS, which is exactly
how `domains.md` shipped unreachable: ten bound checks proved it correct, mirrored and within
budget, and not one asked whether anything named it. A ref nobody loads cannot do its job,
whatever its contents prove.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
ROUTER = SKILL / "SKILL.md"
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402 — the engine is the authority on which profiles exist


def _own_refs():
    """Every ref this router is responsible for surfacing.

    `persona-author/` is a NESTED sub-skill with its own SKILL.md and its own budget — loaded on
    its own terms, never as part of this router's disclosure cost. Same carve-out `_own_docs()`
    makes in test_surface.py; the orphan rule must not fight a deliberate exemption (E1).
    """
    return [p for p in SKILL.rglob("*.md")
            if p.name != "SKILL.md" and "persona-author" not in p.relative_to(SKILL).parts]


def test_router_names_only_shipped_profiles():
    """M1 — `init` silently falls back to `code` on an unknown profile, so an ellipsis lies."""
    text = ROUTER.read_text(encoding="utf-8")
    shipped = set(add.PROFILES)
    named = set()
    for m in re.finditer(r"--profile\s+(?:<([^>]+)>|([a-z]+))", text):
        if m.group(2):
            named.add(m.group(2))
        else:
            named |= {p.strip() for p in m.group(1).split("|")}
    assert named, "SKILL.md names no profile at all"
    stray = named - shipped
    assert not stray, (f"SKILL.md names profiles the engine does not ship: {sorted(stray)} — "
                       f"`init` writes the `code` lenses under any unknown name without refusing")


def test_no_orphan_refs():
    """M2 — a ref the always-loaded router never names is unreachable."""
    text = ROUTER.read_text(encoding="utf-8")
    orphans = sorted(str(p.relative_to(SKILL)) for p in _own_refs()
                     if str(p.relative_to(SKILL)) not in text and p.name not in text)
    assert not orphans, (f"refs no agent will ever load, because SKILL.md names none of them: "
                         f"{orphans}")


def test_router_points_at_the_checker_recipe():
    """M3 — the router must say a checker MAY BE WRITTEN, not merely that one may be run."""
    text = ROUTER.read_text(encoding="utf-8")
    assert "domains.md" in text, "the router never names domains.md"
    assert re.search(r"write (the|a|one)\b", text, re.I), \
        "the router never tells an agent it may WRITE a checker when no runner exists"


def test_orphan_rule_exempts_nested_subskill():
    """E1 — persona-author/ has its own budget and must not be forced into the router."""
    nested = [p for p in SKILL.rglob("*.md") if "persona-author" in p.relative_to(SKILL).parts]
    assert nested, "persona-author/ is gone — E1's premise changed, re-check the exemption"
    assert not any(str(p.relative_to(SKILL)) in {str(q.relative_to(SKILL)) for q in _own_refs()}
                   for p in nested), "the orphan rule swallowed the nested sub-skill"
