"""Cut the `sites:` record that the model did not write; keep the action (.add/tasks/cut-sites-record.md)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
SKILL = PKG / "skill" / "add" / "SKILL.md"


def _quick() -> str:
    flat = " ".join(SKILL.read_text(encoding="utf-8").split())
    return flat.split("**Quick:**", 1)[1].split("## The task loop", 1)[0]


def test_quick_keeps_the_grep_and_drops_the_record():
    q = _quick()
    assert "grep every other site" in q, "the action is gone"
    assert "`sites:" not in q, "the zero-yield record is still asked for"


def test_quick_record_keeps_what_transferred():
    q = _quick()
    for field in ("`lane: quick", "`intent:", "`red→green:", "`suite: unavailable"):
        assert field in q, f"the Quick record lost {field}"


def test_skill_stays_within_budget():
    assert len(SKILL.read_text(encoding="utf-8").splitlines()) <= 200
