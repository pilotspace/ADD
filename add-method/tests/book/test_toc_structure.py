"""book-toc — the renumber is applied, complete, and link-clean (structural, not content).

Red-first: the book is still at its old numbering, so every check here fails until book_renumber.py
runs. Content-vocab is a separate gate (the part-tasks) — nothing here reads chapter prose for words.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]           # add-method/
sys.path.insert(0, str(REPO / "scripts"))
import book_lint  # noqa: E402

DOCS = REPO / "docs"
MKDOCS = REPO.parent / "mkdocs.yml"                    # repo-root mirror artifact
OLD_ORPHANS = ["05-step-3-plan.md", "06-step-4-tests.md", "10-setup-and-stages.md",
               "03-step-1-specify.md", "07-step-5-build.md", "08-step-6-verify.md",
               "09-the-loop.md", "11-governance.md", "12-roles.md", "13-adoption.md"]


def test_all_target_chapters_present():
    """covers: M1 — every new 00–18 file (incl. 12/13) exists exactly once under docs/."""
    missing = [fn for _, fn, _ in book_lint.target_chapters() if not (DOCS / fn).is_file()]
    assert not missing, f"target chapters missing from docs/: {missing}"


def test_no_orphan_old_numbers():
    """covers: M1, R:ORPHAN, E1, E2 — collapsed/renamed source files no longer exist in docs/."""
    left = [fn for fn in OLD_ORPHANS if (DOCS / fn).is_file()]
    assert not left, f"orphaned old-number files still in docs/ (R:ORPHAN): {left}"


def test_all_internal_links_resolve():
    """covers: M3 — every ./NN-*.md link and nav line in docs/ points at a real docs/ file."""
    bad = book_lint.resolve_links(DOCS)
    assert not bad, f"dangling internal links after renumber: {bad}"


def test_nav_matches_target():
    """covers: M2 — mkdocs.yml nav lists exactly the target chapters, in target order."""
    nav = book_lint.nav_chapters(MKDOCS)
    want = [fn for _, fn, _ in book_lint.target_chapters()]
    assert nav == want, f"mkdocs nav != target order\n nav={nav}\nwant={want}"
