"""The plain results page explains why ADD writes a plan and tests before code, in ADD's turquoise
(owner, 2026-10-07)."""
import re
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "docs" / "add-results.html"


def test_add_is_turquoise_in_both_themes():
    html = PAGE.read_text(encoding="utf-8")
    adds = re.findall(r"--add:\s*(#[0-9a-fA-F]{6})", html)
    assert len(adds) >= 3, "light, dark-media and dark-attribute themes each set --add"
    for c in adds:
        r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
        assert g > r + 60 and b > r + 40 and abs(g - b) < 70, f"{c} is not a turquoise"


def test_page_explains_plan_and_tests_first():
    html = PAGE.read_text(encoding="utf-8")
    visible = re.sub(r"<(script|style)\b[^>]*>.*?</\1\s*>", " ", html, flags=re.S | re.I)
    visible = " ".join(re.sub(r"<[^>]+>", " ", visible).split())
    assert "Why write the plan and the tests first?" in visible
    for step in ("Plan", "Failing test", "Code", "Passing test", "Evidence"):
        assert step in visible, f"the ADD flow lacks the {step!r} step"
    for reason in ("silent", "proves", "can't be quietly weakened", "next session"):
        assert reason in visible, f"the page does not give the {reason!r} reason"
