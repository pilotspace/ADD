"""Align the skill with its measured yield (.add/tasks/value-final.md)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
SKILL = PKG / "skill" / "add" / "SKILL.md"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _between(flat: str, start: str, end: str) -> str:
    return flat.split(start, 1)[1].split(end, 1)[0]


def test_quick_test_carries_a_falsifier():
    quick = _between(_flat(SKILL), "**Quick:**", "## The task loop")
    assert "the request's own example" in quick and "falsifier" in quick


def test_no_dead_found_step():
    assumptions = _between(_flat(SKILL), "- **ASSUMPTIONS**", "- **CHECKS**")
    assert "found:" not in assumptions and "check the cheap ones now" not in assumptions


def test_refute_is_required_for_security_work():
    step5 = _between(_flat(SKILL), "5. **Refute**", "6. **Verdict**")
    assert "Security work" in step5 and "`probes: none — <why>`" in step5
    assert "counter-lens" in step5


def test_readmes_value_table_is_measured():
    for path in (ROOT / "README.md", PKG / "README.md"):
        section = _between(_flat(path), "## What ADD gives your project", "## Vanilla Claude vs")
        for fact in ("30 of 30", "7 of 30", "2 of 30", "0.81 vs 0.43"):
            assert fact in section, f"{path}: the value table lacks {fact!r}"
