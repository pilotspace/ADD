"""The served announcement pages are byte-copies of the canonical blog/ posts.

`blog/` is canonical (the launch-post claims oracle reads it there);
`docs/announcements/` is what the site serves. Two copies of a post that can drift is the
same seam class as every mirror in this repo, so the parity is guarded, and the nav must
carry exactly the pages that exist — an orphan page is invisible, a nav ghost breaks
`mkdocs build --strict`.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ANNOUNCE = REPO / "docs" / "announcements"
BLOG = REPO.parent / "blog"


def test_served_copies_match_the_canonical_posts():
    pages = sorted(p.name for p in ANNOUNCE.glob("*.md"))
    assert pages, "the announcements section is empty"
    for name in pages:
        assert (BLOG / name).is_file(), f"{name} is served but has no canonical blog/ source"
        assert (ANNOUNCE / name).read_bytes() == (BLOG / name).read_bytes(), \
            f"{name} drifted from its canonical blog/ copy — re-sync the byte copy"


def test_nav_carries_exactly_the_served_pages():
    nav = (REPO.parent / "mkdocs.yml").read_text(encoding="utf-8")
    for page in ANNOUNCE.glob("*.md"):
        assert f"announcements/{page.name}" in nav, f"{page.name} is served but not in the nav"
    for line in nav.splitlines():
        if "announcements/" in line:
            name = line.rsplit("announcements/", 1)[1].strip()
            assert (ANNOUNCE / name).is_file(), f"nav names missing page {name}"
