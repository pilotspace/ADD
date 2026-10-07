"""Publish the full SWE-bench Lite trade-off, losses included (.add/tasks/publish-300.md)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
READMES = (ROOT / "README.md", PKG / "README.md")
RESULTS = ROOT / "benchmark" / "results" / "2026-10-add-4.0-low-effort-vs-vanilla.md"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _between(flat: str, start: str, end: str) -> str:
    return flat.split(start, 1)[1].split(end, 1)[0]


def test_readmes_state_the_300_result_with_the_loss():
    # publish-medium supersedes the README claim; the low-effort loss stays on the results page
    section = _between(_flat(RESULTS), "## SWE-bench Lite, all 300 issues", "## Round 10")
    for fact in ("201 of 300", "215 of 300", "p = 0.016", "Vanilla fixes more issues"):
        assert fact in section, f"the results page lost {fact!r}"


def test_value_table_quotes_the_300_test_discipline():
    # publish-medium moves the README to the medium run; the low-effort figures stay on the results page
    section = _between(_flat(RESULTS), "## SWE-bench Lite, all 300 issues", "## Round 10")
    for fact in ("255 of 300", "42 of 300", "298 of 300", "14 of 300"):
        assert fact in section, f"the results page lost {fact!r}"


def test_results_page_leads_with_the_300_and_names_what_was_not_measured():
    flat = _flat(RESULTS)
    assert flat.index("## SWE-bench Lite, all 300 issues") < flat.index("## Round 10")
    section = _between(flat, "## SWE-bench Lite, all 300 issues", "## Round 10")
    for fact in ("201", "215", "p = 0.016", "human review time", "Not measured"):
        assert fact in section, f"the 300 section lacks {fact!r}"


def test_vanilla_call_drops_the_contaminated_speed_claim():
    for path in READMES:
        call = _between(_flat(path), "## When vanilla Claude is the right call", "ADD works with the agent")
        assert "4–5× faster" not in call, f"{path}: still quotes the plugin-contaminated speed gap"
