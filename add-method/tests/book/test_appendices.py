"""book-appendices — the appendices teach only the shipped ADD 3.0 method.

The part-tasks (test_part1..4) gate chapters 00–18. Nothing gated the appendices, which is
exactly why all eight drifted: they still teach the 2.x six-step loop (Specify → Scenarios →
Contract → Tests → Build → Verify) over a document set the ABF-1 bundle does not have
(`SPEC.md`, `contracts/`, `playbook/`, `CONVENTIONS.md`, `MODEL_REGISTRY.md`).

Appendices are discovered by glob, so CUTTING one is a legitimate way to go green — an appendix
that no longer exists cannot teach the old method. `test_every_appendix_is_navigable` keeps that
honest: whatever survives must be reachable from the mkdocs nav, and the nav must not point at a
file that was removed.

G (references & lineage) and H (vs spec-kit) are held to the core banned-token list only: both
legitimately NAME prior art and the superseded method as history. They are NOT exempt from it —
a current-tense claim about `add.py` or GEPA is an overclaim wherever it appears.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import book_lint  # noqa: E402

DOCS = REPO / "docs"
MKDOCS = REPO.parent / "mkdocs.yml"

# The 2.x method surface the appendices still teach. None of these are in book_lint.BANNED_TOKENS
# (that list was written for the chapters, which never carried the document set), so the appendix
# gate carries its own: the retired per-feature documents, the playbook, and the six-step names.
RETIRED_SURFACE = [
    "SPEC.md", "MODEL_REGISTRY.md", "contracts/", "playbook/",
    "Step 1 — Specify", "Step 2 — Scenarios", "Step 3 — Contract",
    "Step 4 — Tests", "Step 5 — Build", "Step 6 — Verify",
    "six-step", "six step", "1_specify", "2_scenarios", "3_contract",
    "4_tests", "5_build", "6_observe",
]

# G and H narrate prior art / the superseded method; they carry the core list only.
HISTORY_APPENDICES = {"appendix-g-references.md", "appendix-h-add-vs-spec-kit.md"}

PHANTOM_VERBS = ["add audit", "add heal", "add graduate", "add stage ", "add delta-append",
                 "add guide", "add migrate", "add waves", "add check "]

NAV_RE = re.compile(r":\s*(appendix-[0-9A-Za-z._-]*\.md)\s*$", flags=re.MULTILINE)


def appendices():
    """Every appendix that still exists, in order. Cutting one removes it from the gate."""
    return sorted(DOCS.glob("appendix-*.md"))


def test_appendices_teach_no_okf_vocabulary():
    """covers: M1 — no 2.x token in any surviving appendix."""
    hits = {}
    for md in appendices():
        text = md.read_text(encoding="utf-8")
        found = book_lint.banned_hits(text)
        if md.name not in HISTORY_APPENDICES:
            found += [t for t in RETIRED_SURFACE if t in text]
        if found:
            hits[md.name] = sorted(set(found))
    assert not hits, f"2.x method still taught in the appendices: {hits}"


def test_appendices_advertise_no_phantom_verbs():
    """covers: M2, R:OVERCLAIM — an appendix must not name a verb the engine does not ship."""
    phantom = {}
    for md in appendices():
        text = md.read_text(encoding="utf-8")
        found = [v for v in PHANTOM_VERBS if v in text]
        if found:
            phantom[md.name] = found
    assert not phantom, f"appendices advertise verbs the engine lacks: {phantom}"


def test_every_appendix_is_navigable():
    """covers: M3 — the nav and the docs dir agree, in both directions.

    This is what makes CUT a legitimate green: removing an appendix is only complete when its nav
    entry goes with it, and `mkdocs build --strict` would otherwise fail on the dangling target.
    """
    nav = set(NAV_RE.findall(MKDOCS.read_text(encoding="utf-8")))
    present = {p.name for p in appendices()}
    assert not (nav - present), f"mkdocs nav points at removed appendices: {sorted(nav - present)}"
    assert not (present - nav), f"appendices exist but are unreachable from nav: {sorted(present - nav)}"


def test_appendix_links_resolve():
    """covers: M4 — every ./<file>.md link out of an appendix resolves (no orphan cross-reference)."""
    present = {p.name for p in DOCS.glob("*.md")} | {"README.md"}
    bad = []
    for md in appendices():
        for target in book_lint.internal_links(md.read_text(encoding="utf-8")):
            if target not in present:
                bad.append((md.name, target))
    assert not bad, f"appendix links do not resolve: {bad}"
