"""getting-started-descenarios: failing-first ACCEPTANCE checks (kind: docs).

The scenarios->tests fold retired the standalone §2 SCENARIOS section and deleted the
book chapter 04-step-2-scenarios. The GETTING-STARTED walkthrough was missed by that
sweep: it still teaches a "Phase 2 — Scenarios" step linking to the deleted chapter,
and still claims the scaffolded PLAN.md holds "seven" phase sections.

These checks are red against the doc as it stands and green once the step is retired.
Evidence, not a claim: each check reads the shipped file on disk.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / "add-method" / "GETTING-STARTED.md"
DOCS_DIR = ROOT / "add-method" / "docs"
TEMPLATE = ROOT / "add-method" / "tooling" / "templates" / "PLAN.md.tmpl"

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


@pytest.fixture(scope="module")
def doc() -> str:
    assert DOC.exists(), f"the walkthrough must exist at {DOC}"
    return DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def flat(doc: str) -> str:
    """Whitespace-normalized doc — claims wrap across newlines in the source."""
    return re.sub(r"\s+", " ", doc)


def _phase_headings(doc: str) -> list[str]:
    return re.findall(r"^### Phase .*$", doc, flags=re.MULTILINE)


# M1 — the retired step is gone
def test_no_phase2_step(doc: str) -> None:
    offenders = [h for h in _phase_headings(doc) if re.match(r"^### Phase 2\b", h)]
    assert offenders == [], (
        "the 'Phase 2 — Scenarios' walkthrough step was retired by the "
        f"scenarios-into-tests fold but still appears: {offenders}"
    )


# M2 / R:dead_chapter_link — no link to the deleted chapter
def test_no_retired_chapter_link(doc: str) -> None:
    assert "04-step-2-scenarios" not in doc, (
        "the doc links to 04-step-2-scenarios, a chapter deleted from add-method/docs/ "
        "— a live 404 for readers of the npm and PyPI tarballs"
    )


# M3 — the guidance survives where the fold put it: with the tests
def test_gwt_folded_into_phase4(doc: str) -> None:
    sections = re.split(r"^### Phase ", doc, flags=re.MULTILINE)
    phase4 = [s for s in sections if s.startswith("4 ")]
    assert phase4, "the 'Phase 4 — Tests' step must exist"
    body = re.sub(r"\s+", " ", phase4[0])

    assert re.search(r"Given\W{0,3}When\W{0,3}Then", body, flags=re.IGNORECASE), (
        "Given/When/Then guidance must survive inside Phase 4 — the fold moved "
        "scenarios to live WITH the tests, it did not delete them"
    )
    assert re.search(r"unchanged|no balance changes", body, flags=re.IGNORECASE), (
        "the rejection-invariance point (a rejected call leaves state unchanged) "
        "was the substance of the old Phase 2 and must survive the fold"
    )


# M4 / R:stale_section_count — the stated count matches the real template
def test_section_count_matches_template(flat: str) -> None:
    assert TEMPLATE.exists(), f"the scaffold template must exist at {TEMPLATE}"
    actual = len(
        re.findall(r"^## \d+ · ", TEMPLATE.read_text(encoding="utf-8"), flags=re.MULTILINE)
    )

    claim = re.search(r"all (\w+) phase sections", flat)
    assert claim, "the doc must state how many phase sections the scaffold holds"
    stated_word = claim.group(1).lower()
    stated = NUMBER_WORDS.get(stated_word)
    assert stated is not None, f"unparsable section count in the doc: {stated_word!r}"

    assert stated == actual, (
        f"the doc claims {stated_word} ({stated}) phase sections but "
        f"{TEMPLATE.name} has {actual} — §2 was retired by the fold"
    )


# M5 / After — every chapter link points at a chapter that still ships
def test_every_chapter_link_resolves(doc: str) -> None:
    slugs = set(re.findall(r"pilotspace\.github\.io/ADD/(\d{2}-[a-z0-9-]+)/", doc))
    assert slugs, "the walkthrough must link to book chapters"

    dead = sorted(s for s in slugs if not (DOCS_DIR / f"{s}.md").exists())
    assert dead == [], f"chapter links with no file in add-method/docs/: {dead}"
