"""Close the two SWE-bench blind spots the round-10 failures showed (.add/tasks/blind-spots.md)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
SKILL = PKG / "skill" / "add" / "SKILL.md"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _between(flat: str, start: str, end: str) -> str:
    return flat.split(start, 1)[1].split(end, 1)[0]


def test_quick_lists_every_site_of_the_change():
    """django-13265: the second emitter was in the agent's own grep output and went unfixed."""
    # cut-sites-record: the `sites:` record transferred in 2 of 30 runs and was cut; the action stays
    quick = _between(_flat(SKILL), "**Quick:**", "## The task loop")
    assert "grep every other site" in quick


def test_quick_has_a_fallback_when_the_suite_cannot_run():
    """matplotlib-24265 / sklearn-14087: no runnable suite, so the fix shipped unexecuted."""
    quick = _between(_flat(SKILL), "**Quick:**", "## The task loop")
    assert "`suite: unavailable" in quick
    assert "repro as written" in quick and "import every file you touched" in quick


def test_verify_never_passes_a_check_it_could_not_run():
    step2 = _between(_flat(SKILL), "2. **Fresh green:**", "3. **Consumers:**")
    assert "cannot run" in step2 and "RISK-ACCEPTED" in step2


def test_skill_stays_within_budget():
    assert len(SKILL.read_text(encoding="utf-8").splitlines()) <= 200
