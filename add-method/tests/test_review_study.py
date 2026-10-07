"""The 6-issue blinded review study is published as what it is: one reviewer, untimed, and a
result that goes against ADD on preference (benchmark/runs-swe/review-answers.json)."""
import json
import re
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
PAGE = PKG / "docs" / "add-results.html"
RESULTS = ROOT / "benchmark" / "results" / "2026-10-add-4.0-low-effort-vs-vanilla.md"
CHANGELOG = PKG / "CHANGELOG.md"
READMES = (ROOT / "README.md", PKG / "README.md")


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _study() -> str:
    text = RESULTS.read_text(encoding="utf-8")
    assert "### One reviewer, six issues" in text, "the results page has no review-study section"
    return " ".join(text.split("### One reviewer, six issues", 1)[1].split("\n### ", 1)[0].split())


def test_results_page_reports_the_study_with_its_limits():
    study = _study()
    for fact in ("preferred vanilla's output in 6 of 6", "easier to decide on in 6 of 6",
                 "5 of 6", "3 of 6", "2 of the 5"):
        assert fact in study, f"the study section lacks {fact!r}"
    for limit in ("one reviewer", "untimed", "anecdot"):
        assert limit in study.lower(), f"the study section does not say {limit!r}"


def test_no_surface_still_calls_the_study_pending():
    for path in (RESULTS, CHANGELOG, PAGE, *READMES):
        assert "review study is pending" not in _flat(path), f"{path}: the study is no longer pending"


def test_page_charts_the_study_and_keeps_its_caveat():
    html = PAGE.read_text(encoding="utf-8")
    data = json.loads(re.search(r'<script type="application/json" id="add-data">(.*?)</script>', html, re.S).group(1))
    assert data["review"] == {"prefer": {"vanilla": 6, "add": 0}, "matched": {"vanilla": 3, "add": 5}, "total": 6}
    assert 'id="bars-prefer"' in html and 'id="bars-matched"' in html
    visible = re.sub(r"<(script|style)\b[^>]*>.*?</\1\s*>", " ", html, flags=re.S | re.I)
    visible = " ".join(re.sub(r"<[^>]+>", " ", visible).split()).lower()
    assert "one reviewer" in visible and "not timed" in visible


def test_readmes_and_changelog_carry_the_study():
    for path in READMES:
        flat = _flat(path)
        assert "6 of 6" in flat and "one reviewer" in flat.lower(), f"{path}: the study result is missing"
    entry = CHANGELOG.read_text(encoding="utf-8").split("## [4.1.0]", 1)[1].split("\n## [", 1)[0]
    assert "6 of 6" in " ".join(entry.split()) and "one reviewer" in entry.lower()
