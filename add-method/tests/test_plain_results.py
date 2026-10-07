"""Results a normal user can read: an animated plain-language page and a plain-words README opening
(.add/tasks/plain-results.md)."""
import json
import re
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
DOCS = PKG / "docs"
PAGE = DOCS / "add-results.html"
READMES = (ROOT / "README.md", PKG / "README.md")
RESULTS = ROOT / "benchmark" / "results" / "2026-10-add-4.0-low-effort-vs-vanilla.md"
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")
BRAG = re.compile(r"cheaper|costs? less|lower cost|more correct|higher oracle|always better|guarantee", re.I)
JARGON = re.compile(r"McNemar|\bp\s*=|P2P|F2P|oracle|mutation|FAIL_TO_PASS|held-out", re.I)


def _flat(text: str) -> str:
    return " ".join(text.split())


def _plain_section(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    assert "## ADD in plain words" in text, f"{path}: no plain-words section"
    return text.split("## ADD in plain words", 1)[1].split("\n## ", 1)[0]


def test_page_is_self_contained_and_respects_motion():
    html = PAGE.read_text(encoding="utf-8")
    for pattern, what in ((r"""\bsrc\s*=\s*["']?(?:https?:)?//""", "a remote src"),
                          (r"""<link[^>]+href\s*=\s*["']?(?:https?:)?//""", "a remote stylesheet"),
                          (r"url\(\s*['\"]?(?:https?:)?//", "a remote url()"), (r"@import", "an @import")):
        assert not re.search(pattern, html, re.I), f"the page loads {what}"
    assert "prefers-reduced-motion" in html
    assert "add-vs-vanilla.html" in html and "2026-10-add-4.0-low-effort-vs-vanilla.md" in html


def test_page_speaks_plainly_and_never_overclaims():
    html = PAGE.read_text(encoding="utf-8")
    visible = re.sub(r"<(script|style)\b[^>]*>.*?</\1\s*>", " ", html, flags=re.S | re.I)
    visible = re.sub(r"<[^>]+>", " ", visible)
    hit = BRAG.search(visible)
    assert not hit, f"the page overclaims ({hit.group(0)})"
    hit = JARGON.search(visible)
    assert not hit, f"the page uses jargon a normal user won't know ({hit.group(0)})"
    for honest in ("not proven", "costs more", "not measured"):
        assert honest in visible.lower(), f"the page does not say {honest!r}"


def test_page_numbers_trace_to_the_results_page():
    html = PAGE.read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="add-data">(.*?)</script>', html, re.S)
    assert m, "no embedded data block"
    numbers = []

    def walk(node):
        if isinstance(node, bool):
            return
        if isinstance(node, (int, float)):
            numbers.append(float(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                if k != "meta":
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(json.loads(m.group(1)))
    assert len(numbers) >= 20
    known = {float(n) for n in NUM.findall(_flat(RESULTS.read_text(encoding="utf-8")))}
    stray = sorted({v for v in numbers if v not in known})
    assert not stray, f"numbers not on the results page: {stray}"


def test_readmes_open_with_plain_words_and_link_the_page():
    for path in READMES:
        text = path.read_text(encoding="utf-8")
        assert text.index("## ADD in plain words") < text.index("Highlights"), f"{path}: plain words must come first"
        section = _plain_section(path)
        assert "add-results.html" in section, f"{path}: the plain section does not link the animated page"
        for fact in ("226", "215", "274", "299", "1.8×"):
            assert fact in section, f"{path}: the plain section lacks {fact!r}"
        hit = JARGON.search(section)
        assert not hit, f"{path}: jargon in the plain section ({hit.group(0)})"


def test_docs_index_links_the_page():
    assert "add-results.html" in (DOCS / "README.md").read_text(encoding="utf-8")
