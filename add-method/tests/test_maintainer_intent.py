"""Fix what the maintainers meant, and say it where it is read (.add/tasks/maintainer-intent.md)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
SKILL = PKG / "skill" / "add" / "SKILL.md"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _between(flat: str, start: str, end: str) -> str:
    return flat.split(start, 1)[1].split(end, 1)[0]


def _quick() -> str:
    return _between(_flat(SKILL), "**Quick:**", "## The task loop")


def test_quick_reads_the_conventions_before_the_test():
    """django-15320: the literal fix skipped the clone the neighbours' convention required."""
    q = _quick()
    assert "nearest tests" in q and "conventions" in q
    assert q.index("conventions") < q.index("the request's own example")


def test_the_literal_fix_is_a_candidate_wrong_fix():
    assert "literally suggests" in _quick()


def test_quick_record_is_the_last_lines_of_the_reply():
    """Commit-body records transferred in 7/30 runs and `sites:` in 2/30; the final reply always exists."""
    q = _quick()
    assert "last lines of your reply" in q and "`intent:" in q


def test_non_code_quick_uses_the_check_that_fits():
    assert "non-code" in _quick()


def test_direction_grounds_in_the_nearest_tests():
    ground = _between(_flat(SKILL), "Ground first:", "Write `.add/tasks/<slug>.md`")
    assert "nearest tests" in ground


def test_skill_stays_within_budget():
    assert len(SKILL.read_text(encoding="utf-8").splitlines()) <= 200
