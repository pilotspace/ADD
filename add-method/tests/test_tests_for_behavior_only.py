"""Quick skips the test only when no behavior changes (.add/tasks/tests-for-behavior-only.md)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
SKILL = PKG / "skill" / "add" / "SKILL.md"
TREES = (PKG / "src" / "add_method" / "_bundled" / "skill" / "add" / "SKILL.md",
         ROOT / ".claude" / "skills" / "add" / "SKILL.md")
READMES = (ROOT / "README.md", PKG / "README.md")
CHANGELOG = PKG / "CHANGELOG.md"
RESULTS = ROOT / "benchmark" / "results" / "2026-10-add-4.0-low-effort-vs-vanilla.md"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _quick() -> str:
    return _flat(SKILL).split("**Quick:**", 1)[1].split("## The task loop", 1)[0]


def test_a_behavior_change_gets_a_test():
    q = _quick()
    assert "A change to behavior (a bug fix, a new case) gets a test" in q
    rule = q.split("gets a test", 1)[1].split("No new behavior", 1)[0]
    assert "the request's own example" in rule and "falsifier" in rule and "watch it fail" in rule


def test_no_new_behavior_needs_no_new_test():
    q = _quick()
    skip = q.split("No new behavior", 1)[1]
    for example in ("typo", "rename", "config value", "already-failing test"):
        assert example in skip.split("needs no new test", 1)[0], f"{example} is not named"
    assert "`test: none — <what covers it>`" in q and "`red→green: <test>`" in q
    assert "run the suite" in q and "review your diff" in q


def test_the_importance_judgement_is_gone():
    flat = _flat(SKILL)
    assert "only when it is important" not in flat and "when it is important" not in flat
    assert "one commit; a test when behavior changes" in flat


def test_docs_carry_the_remeasure():
    results = _flat(RESULTS)
    assert "resolved 78 of 101" in results and "83" in results
    for path in (*READMES, CHANGELOG):
        flat = _flat(path)
        assert "every bug fix keeps its test" in flat, f"{path}: does not say bug fixes keep their test"
        assert "measured while Quick required a test on every fix" not in flat, f"{path}: stale note"
    assert "78 of 101" in _flat(CHANGELOG)


def test_floor_budget_and_mirror():
    text = SKILL.read_text(encoding="utf-8")
    flat = _flat(SKILL)
    assert "at least one per Must and Reject" in flat and "is at least a Task — never Quick" in flat
    assert "Floor touched, or a check to weaken? It is a Task now." in _quick()
    assert len(text.splitlines()) <= 200
    for tree in TREES:
        assert tree.read_text(encoding="utf-8") == text, f"{tree} drifted"
