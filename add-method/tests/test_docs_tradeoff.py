"""The READMEs sell ADD by what it gives a project against vanilla Claude — the same request as two
flows, animated from two real round-6 runs, with the price beside every gain
(.add/tasks/docs-value-tradeoff.md)."""
import json
import re
from pathlib import Path

from test_docs_value import BRAG, DOCS, PKG, READMES, RESULTS, ROOT, _flat, _section, _values

FLOW = DOCS / "add-vs-vanilla.html"
R6 = "PILOT-4v3-2026-09-30-r6.md"


def _headings(path: Path) -> list[str]:
    return [line.lower() for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("#")]


def test_results_page_carries_round_6():
    text = _flat(RESULTS)
    assert f"../{R6}" in text and (ROOT / "benchmark" / R6).is_file(), "the results page does not link round 6"
    assert "claude-sonnet-5-5" in text, "round 6 is quoted without its model id"
    r6 = _section(RESULTS, "Round 6")
    for phrase in ("saturat", "owner", "min", "×", "vanilla-amb/rep1", "add-4-amb/rep1"):
        assert phrase in r6, f"the round-6 section does not state {phrase!r}"


def test_readmes_run_one_request_both_ways():
    for path in READMES:
        heads = _headings(path)
        gives = next((i for i, h in enumerate(heads) if "gives your project" in h), None)
        both = next((i for i, h in enumerate(heads) if "same request" in h), None)
        assert gives is not None, f"{path}: no section on what ADD gives your project"
        assert both is not None and gives < both, f"{path}: no same-request section after the value pitch"
        section = _section(path, "same request")
        assert "add-vs-vanilla.html" in section, f"{path}: the two flows do not link the animated page"
        for phrase in ("freeze(", "verify(", "ASSUMPTIONS"):
            assert phrase in section, f"{path}: the ADD flow does not show {phrase!r}"
        low = section.lower()
        assert "vanilla" in low and "contradict" in low, f"{path}: the vanilla flow omits the contradiction it caught"


def test_measured_sections_price_every_gain_in_dollars_and_time():
    known = _values(_flat(RESULTS))
    for path in READMES:
        section = _section(path, "measured on 4.0")
        assert "Sonnet 5.5" in section, f"{path}: the measured section does not quote round 6"
        multiples = set(re.findall(r"(\d+(?:\.\d+)?)×", section))
        assert len(multiples) >= 2, f"{path}: gains are not priced in both dollars and time ({multiples})"
        assert "$" in section and "min" in section, f"{path}: the section gives no dollars or no minutes"
        assert re.search(r"\bties?\b|\bmatch(?:es|ed)?\b|saturat", section), f"{path}: vanilla's ties are left out"
        stray = sorted(v for v in _values(section) if v not in known)
        assert not stray, f"{path}: numbers not on the results page: {stray}"
        hit = BRAG.search(section)
        assert not hit, f"{path}: the section overclaims ({hit.group(0)})"


def test_flow_page_plays_both_runs_and_traces():
    assert FLOW.is_file(), "add-method/docs/add-vs-vanilla.html is missing"
    html = FLOW.read_text(encoding="utf-8")
    for pattern, what in ((r"""\bsrc\s*=\s*["']?(?:https?:)?//""", "a remote src"),
                          (r"""<link[^>]+href\s*=\s*["']?(?:https?:)?//""", "a remote stylesheet or font"),
                          (r"url\(\s*['\"]?(?:https?:)?//", "a remote url()"), (r"@import", "an @import")):
        assert not re.search(pattern, html, re.I), f"the flow page loads {what}"
    assert "prefers-reduced-motion" in html, "the flow page ignores reduced motion"
    assert "<noscript" in html, "the flow page has no state without JavaScript"
    for pane in ('id="pane-vanilla"', 'id="pane-add"'):
        assert pane in html, f"the flow page has no {pane} pane"
    visible = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    for run in ("vanilla-amb/rep1", "add-4-amb/rep1"):
        assert run in visible, f"the flow page does not name its source run {run}"
    vanilla = re.search(r'id="pane-vanilla".*?id="pane-add"', html, re.S)
    assert vanilla and "contradicts" in vanilla.group(0), "the vanilla pane omits the contradiction it caught"
    hit = BRAG.search(visible)
    assert not hit, f"the flow page overclaims ({hit.group(0)})"
    m = re.search(r'<script type="application/json" id="flow-data">(.*?)</script>', html, re.S)
    assert m, "the flow page has no embedded data block"
    numbers = []

    def walk(node):
        if isinstance(node, bool) or isinstance(node, str):
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

    walk(json.loads(m.group(1)))
    assert len(numbers) >= 12, "the data block is too thin to back the page's figures"
    for must in (46, 195, 0.28, 0.63):
        assert float(must) in numbers, f"the data block does not carry the runs' {must}"
    stray = sorted({v for v in numbers if v not in _values(_flat(RESULTS))})
    assert not stray, f"the flow page draws numbers that are not on the results page: {stray}"


def test_ch20_and_changelog_carry_sonnet_5_5():
    section = _section(DOCS / "20-whats-new-in-4.md", "Measured on 4.0")
    assert "Sonnet 5.5" in section, "ch 20 does not carry the Sonnet 5.5 round"
    assert "Sonnet 5.5" in _section(PKG / "CHANGELOG.md", "[4.0.0]"), "the 4.0.0 entry does not carry Sonnet 5.5"


def test_flow_page_is_linked():
    for path in (*READMES, DOCS / "README.md", DOCS / "add-value.html"):
        assert "add-vs-vanilla.html" in path.read_text(encoding="utf-8"), f"{path} does not link the flow page"
