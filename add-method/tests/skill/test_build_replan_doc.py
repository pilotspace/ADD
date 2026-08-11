"""build.md documents the steering-vs-contract split (task replan-verb, dynamic-flow)."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILD = REPO / "skill" / "add" / "phases" / "build.md"


def test_build_documents_replan_split():
    """covers: M4, A4 — replan named; steering keyed on the no-frozen-surface test; a
    frozen gives/check change stays a change-request."""
    text = BUILD.read_text(encoding="utf-8")
    assert re.search(r"\breplan\b", text), "build.md does not name the replan verb"
    assert re.search(r"steering", text, re.I), "the steering class is not named"
    assert re.search(r"no frozen surface|changes NO frozen surface", text, re.I), \
        "the no-frozen-surface steering test is not stated"
    assert re.search(r"change-request", text), "the contract path must remain a change-request"
