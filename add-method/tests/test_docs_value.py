"""The docs tell the truth about the merged 4.0 skill, and every 4.0 number they quote traces to the
results page (.add/tasks/docs-4-value.md)."""
import json
import re
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
DOCS = PKG / "docs"
READMES = (PKG / "README.md", ROOT / "README.md")
RESULTS = ROOT / "benchmark" / "results" / "2026-09-add-4.0-vs-vanilla.md"
PAGE = DOCS / "add-value.html"
PILOTS = ("PILOT-4v3-2026-09-29.md", "PILOT-4v3-2026-09-30.md", "PILOT-4v3-2026-09-30-r5.md")
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")
BRAG = re.compile(r"cheaper|costs? less|lower cost|more correct|higher oracle", re.I)


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _section(path: Path, heading: str) -> str:
    """The text under the first heading whose title contains `heading`, up to the next heading."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.startswith("#") and heading.lower() in line.lower()), None)
    assert start is not None, f"{path.name} has no heading containing {heading!r}"
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    out = []
    for line in lines[start + 1:]:
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= level:
            break
        out.append(line)
    return " ".join(" ".join(out).split())


def _values(text: str) -> set[float]:
    return {float(n) for n in NUM.findall(text)}


def test_no_page_sends_non_security_work_to_a_subagent():
    for page in sorted(DOCS.glob("*.md")):
        for sentence in re.split(r"(?<=[.!?])\s+", _flat(page)):
            low = sentence.lower()
            if "subagent" not in low:
                continue
            assert not re.search(r"data (?:or|and|·) architecture|floor work", low), \
                f"{page.name} sends non-security work to a subagent: {sentence[:160]}"
            assert not re.search(r"parallel subagents|many subagents|fans? out", low), \
                f"{page.name} tells a lane to fan out subagents: {sentence[:160]}"
    assert re.search(r"subagent[^.]*security work|security work[^.]*subagent", _flat(DOCS / "05-verify.md")), \
        "05-verify.md no longer says when a fresh subagent is used"


def test_direction_pages_state_the_merged_rules():
    direction = _flat(DOCS / "03-direction.md")
    checklist = _section(DOCS / "appendix-e-checklists.md", "Direction")
    for text, name in ((direction, "03-direction.md"), (checklist, "the Direction checklist")):
        for phrase in ("the way a real caller sends", "least-privilege"):
            assert phrase in text, f"{name} does not state {phrase!r}"
    assert "every RULES id" in direction, "03-direction.md does not require every rule to be covered"


def test_report_pages_lead_with_the_costliest_guess():
    assert "costliest" in _section(DOCS / "06-the-loop.md", "The report — "), \
        "06-the-loop.md does not order the assumptions costliest-if-wrong first"
    assert "costliest" in _section(DOCS / "appendix-e-checklists.md", "Learn and report"), \
        "the Learn-and-report checklist does not order the assumptions"


def test_results_page_carries_provenance():
    assert RESULTS.is_file(), "the 4.0 results page is missing"
    text = _flat(RESULTS)
    assert re.search(r"n\s*=\s*3", text), "the results page gives no sample size"
    for disclosure in ("~/.claude", "saturated", "rerun"):
        assert disclosure in text, f"the results page does not disclose {disclosure!r}"
    for pilot in PILOTS:
        assert f"../{pilot}" in text, f"the results page does not link {pilot}"
        assert (ROOT / "benchmark" / pilot).is_file(), f"{pilot} does not exist"


def test_readme_numbers_trace_to_the_results_page():
    known = _values(_flat(RESULTS))
    for path in READMES:
        section = _section(path, "measured on 4.0")
        stray = sorted(v for v in _values(section) if v not in known)
        assert not stray, f"{path}: numbers not on the results page: {stray}"
        assert re.search(r"\d(?:\.\d)?×", section), f"{path}: a gain is quoted with no cost multiple beside it"
        hit = BRAG.search(section)
        assert not hit, f"{path}: the 4.0 section overclaims ({hit.group(0)})"
        assert "add-value.html" in section or "add-value" in section, f"{path}: the section does not link the page"


def test_migration_page_cites_the_4_0_results():
    section = _section(DOCS / "20-whats-new-in-4.md", "Measured on 4.0")
    assert "github.com/pilotspace/ADD/blob/main/benchmark/results/2026-09-add-4.0-vs-vanilla.md" in section, \
        "ch 20 quotes 4.0 numbers without citing the results page"
    stray = sorted(v for v in _values(section) if v not in _values(_flat(RESULTS)) and v not in {4.0, 2.0})
    assert not stray, f"ch 20 quotes numbers not on the results page: {stray}"


def test_changelog_lists_the_post_release_skill_changes():
    entry = _section(PKG / "CHANGELOG.md", "[4.0.0]")
    for phrase in ("least-privilege", "the way a real caller", "security work", "benchmark/quality.py"):
        assert phrase in entry, f"the 4.0.0 entry does not mention {phrase!r}"


def test_value_page_is_self_contained_and_traceable():
    assert PAGE.is_file(), "add-method/docs/add-value.html is missing"
    html = PAGE.read_text(encoding="utf-8")
    for pattern, what in ((r"""\bsrc\s*=\s*["']?(?:https?:)?//""", "a remote src"),
                          (r"""<link[^>]+href\s*=\s*["']?(?:https?:)?//""", "a remote stylesheet or font"),
                          (r"url\(\s*['\"]?(?:https?:)?//", "a remote url()"), (r"@import", "an @import")):
        assert not re.search(pattern, html, re.I), f"the page loads {what}"
    assert "prefers-reduced-motion" in html, "the page ignores reduced motion"
    visible = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    hit = BRAG.search(visible)
    assert not hit, f"the page overclaims ({hit.group(0)})"
    m = re.search(r'<script type="application/json" id="add-data">(.*?)</script>', html, re.S)
    assert m, "the page has no embedded data block"
    data, numbers = json.loads(m.group(1)), []

    def walk(node):
        if isinstance(node, bool):
            return
        if isinstance(node, (int, float)):
            numbers.append(float(node))
        elif isinstance(node, dict):
            for key, value in node.items():
                if key != "meta":
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)
    assert len(numbers) >= 20, "the data block is too thin to back the page's figures"
    known = _values(_flat(RESULTS))
    stray = sorted({v for v in numbers if v not in known})
    assert not stray, f"the page draws numbers that are not on the results page: {stray}"


def test_value_page_is_linked():
    for path in (*READMES, DOCS / "README.md"):
        assert "add-value.html" in path.read_text(encoding="utf-8"), f"{path} does not link the value page"
