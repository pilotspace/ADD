"""Publish the fresh-300 result at medium effort and recommend medium (.add/tasks/publish-medium.md)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
READMES = (ROOT / "README.md", PKG / "README.md")
RESULTS = ROOT / "benchmark" / "results" / "2026-10-add-4.0-low-effort-vs-vanilla.md"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _between(flat: str, start: str, end: str) -> str:
    return flat.split(start, 1)[1].split(end, 1)[0]


def test_readmes_state_the_medium_result_with_its_price():
    for path in READMES:
        measured = _between(_flat(path), "## Measured on 4.0", "## When vanilla Claude")
        for fact in ("226 of 300", "215 of 300", "p = 0.099", "1.8×"):
            assert fact in measured, f"{path}: the measured section lacks {fact!r}"
        assert "vanilla fixes more" not in measured, f"{path}: states the superseded low-effort loss as current"


def test_readmes_recommend_medium():
    for path in READMES:
        flat = _flat(path)
        assert "Run ADD at `--effort medium`" in flat, f"{path}: no medium recommendation"


def test_value_table_quotes_the_medium_run():
    for path in READMES:
        value = _between(_flat(path), "## What ADD gives your project", "## Vanilla Claude vs")
        for fact in ("274 of 300", "53 of 300", "299 of 300", "17 of 300"):
            assert fact in value, f"{path}: the value table lacks {fact!r}"


def test_results_page_leads_with_the_medium_300_and_keeps_the_low_run():
    flat = _flat(RESULTS)
    assert flat.index("## SWE-bench Lite, fresh 300 at medium effort") < flat.index("## SWE-bench Lite, all 300 issues")
    section = _between(flat, "## SWE-bench Lite, fresh 300 at medium effort", "## SWE-bench Lite, all 300 issues")
    for fact in ("226", "215", "p = 0.099", "held-out", "Not measured"):
        assert fact in section, f"the medium section lacks {fact!r}"
