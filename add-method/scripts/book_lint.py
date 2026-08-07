#!/usr/bin/env python3
"""book_lint — the acceptance harness for the ADD-3.0 book alignment (milestone book-align).

Two jobs, both pure reads:

  * STRUCTURE (book-toc) — the frozen target-TOC manifest, an internal-link resolver, and a nav
    reader, so the renumber can be asserted complete and link-clean.
  * VOCAB (book-part1..4) — a banned-OKF-token scan + an `add <verb>` command-surface check, so a
    rewritten chapter can be proven to teach only the shipped engine.

The manifest is the single source of truth for chapter identity: `target_chapters()` returns the
ordered new-number → (filename, title) map the book must realize. `book_renumber.py` applies it;
`tests/book/test_toc_structure.py` asserts it.
"""
from __future__ import annotations

import re
from pathlib import Path

# ── the frozen target TOC (new number → filename, title) — approved 2026-08-07 ────────────────
# Ordered. New 12/13 are the two added reference chapters. Filenames stay stable where the number
# is unchanged (00,01,02,14,15,16,17,18) to spare external links; new slugs only where the number moved.
TARGET_CHAPTERS = [
    ("00", "00-introduction.md",            "00 · The shift: why ADD exists"),
    ("01", "01-principles.md",              "01 · Core principles"),
    ("02", "02-the-flow.md",                "02 · The three-beat loop, and what is disposable"),
    ("03", "03-direction.md",               "03 · Direction — rules, plan, checks"),
    ("04", "04-build.md",                   "04 · Build — red to green, inside scope"),
    ("05", "05-verify.md",                  "05 · Verify — evidence, residue lenses, the gate"),
    ("06", "06-the-loop.md",                "06 · The loop — observe, learn, close"),
    ("07", "07-setup-and-lanes.md",         "07 · Setup and the three lanes"),
    ("08", "08-parallel-work.md",           "08 · Parallel work — waves and worktrees"),
    ("09", "09-governance.md",              "09 · Governance"),
    ("10", "10-personas.md",                "10 · Personas — the team as lenses"),
    ("11", "11-adoption.md",                "11 · Adoption"),
    ("12", "12-bundle-format.md",           "12 · The .add/ bundle — ABF-1 format"),
    ("13", "13-command-reference.md",       "13 · The add command reference"),
    ("14", "14-foundation.md",              "14 · The foundation and the five living specs"),
    ("15", "15-foundations-and-lineage.md", "15 · Foundations and lineage"),
    ("16", "16-releasing.md",               "16 · Releasing"),
    ("17", "17-components.md",              "17 · Components — monorepo and multi-repo"),
    ("18", "18-personas.md",                "18 · Personas in practice — the project-fit loop"),
]

# old filename → new filename. A merged trio maps to new 03; the split old-10 maps to its primary
# (new 07); links that were specifically about parallel streams are repointed to 08 by the renumber
# pass on a per-link basis, not here (this is the default owner).
RENAME = {
    "00-introduction.md":            "00-introduction.md",
    "01-principles.md":              "01-principles.md",
    "02-the-flow.md":                "02-the-flow.md",
    "03-step-1-specify.md":          "03-direction.md",
    "05-step-3-plan.md":             "03-direction.md",
    "06-step-4-tests.md":            "03-direction.md",
    "07-step-5-build.md":            "04-build.md",
    "08-step-6-verify.md":           "05-verify.md",
    "09-the-loop.md":                "06-the-loop.md",
    "10-setup-and-stages.md":        "07-setup-and-lanes.md",
    "11-governance.md":              "09-governance.md",
    "12-roles.md":                   "10-personas.md",
    "13-adoption.md":                "11-adoption.md",
    "14-foundation.md":              "14-foundation.md",
    "15-foundations-and-lineage.md": "15-foundations-and-lineage.md",
    "16-releasing.md":               "16-releasing.md",
    "17-components.md":              "17-components.md",
    "18-personas.md":                "18-personas.md",
}

# the two new reference chapters have no source; the renumber writes stubs the part-tasks fill.
NEW_STUBS = ["12-bundle-format.md", "13-command-reference.md"]

# OKF / AIDD-2.x vocabulary the aligned book must NOT teach (vocab check, part-tasks).
BANNED_TOKENS = [
    "autonomy: auto", "autonomy: conservative", "autonomy: manual", "autonomy ladder",
    "--stage", "new-task", "freeze --cross", "add.py", "state.json", "SOUL",
    "graduation", "stage production", "MILESTONE.md", "PROJECT.md", "CONVENTIONS.md",
    "SETUP-REVIEW.md", "dependencies.allowlist", "GEPA", "ship review", "ship-review",
    "refute-read", "self-heal", "delta-append", "graduation-report",
]

LINK_RE = re.compile(r"\]\(\.\/([0-9A-Za-z][0-9A-Za-z._-]*\.md)(?:#[^)]*)?\)")


def target_chapters():
    """The ordered frozen manifest: list of (number, filename, title)."""
    return list(TARGET_CHAPTERS)


def target_filenames():
    return {fn for _, fn, _ in TARGET_CHAPTERS}


def internal_links(text: str):
    """Every ./<file>.md target referenced from a markdown link in `text`."""
    return LINK_RE.findall(text)


def resolve_links(docs_dir) -> list:
    """Return [(chapter_file, bad_target), …] for every internal ./NN link that does not resolve
    to a file that exists in `docs_dir`. README.md is a valid target (mkdocs maps it to the home)."""
    docs = Path(docs_dir)
    present = {p.name for p in docs.glob("*.md")} | {"README.md"}
    bad = []
    for md in sorted(docs.glob("*.md")):
        for target in internal_links(md.read_text(encoding="utf-8")):
            if target not in present:
                bad.append((md.name, target))
    return bad


def nav_chapters(mkdocs_path) -> list:
    """The ordered list of chapter filenames the mkdocs.yml nav references (NN-*.md only, in order)."""
    text = Path(mkdocs_path).read_text(encoding="utf-8")
    # nav entries look like:  "<title>": NN-name.md  — collect the .md targets in file order.
    found = re.findall(r":\s*([0-9]{2}-[0-9A-Za-z._-]*\.md)\s*$", text, flags=re.MULTILINE)
    return found


def banned_hits(text: str) -> list:
    """Every banned OKF token present in `text` (substring match, case-sensitive where it matters)."""
    return [tok for tok in BANNED_TOKENS if tok in text]
