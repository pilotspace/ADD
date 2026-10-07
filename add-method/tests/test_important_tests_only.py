"""Quick writes only the important tests; evidence proves the rest (.add/tasks/important-tests-only.md)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
SKILL = PKG / "skill" / "add" / "SKILL.md"
TREES = (SKILL, PKG / "src" / "add_method" / "_bundled" / "skill" / "add" / "SKILL.md",
         ROOT / ".claude" / "skills" / "add" / "SKILL.md")
READMES = (ROOT / "README.md", PKG / "README.md")
CHANGELOG = PKG / "CHANGELOG.md"
NOTE = "measured while Quick required a test on every fix"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _quick() -> str:
    return _flat(SKILL).split("**Quick:**", 1)[1].split("## The task loop", 1)[0]


def test_quick_writes_a_test_only_when_it_is_important():
    q = _quick()
    assert "Make the change directly" in q
    assert "a new test only when it is important" in q
    assert "a plausible wrong fix would pass every existing check" in q, "'important' is undefined"
    important = q.split("only when it is important", 1)[1]
    assert "the request's own example" in important and "falsifier" in important
    assert "fail first" in important, "an important test is no longer watched failing"


def test_untested_changes_are_still_proven_by_evidence():
    q = _quick()
    evidence = q.split("Everything else is proven by evidence", 1)[1]
    assert "fails before your change and passes after" in evidence
    assert "run the suite" in evidence and "review your diff" in evidence


def test_record_and_table_name_the_path_taken():
    q = _quick()
    assert "`red→green: <test>`" in q and "`test: none — <what covers it>`" in q
    flat = _flat(SKILL)
    assert "| a red→green test + one commit |" not in flat, "the table still promises a test every time"
    assert "one commit; a test when it is important" in flat


def test_floor_and_task_checks_are_untouched():
    flat = _flat(SKILL)
    assert "at least one per Must and Reject" in flat
    assert "is at least a Task — never Quick" in flat
    assert "the checks **must fail because the behavior is absent**" in flat
    assert "Floor touched, or a check to weaken? It is a Task now." in _quick()


def test_docs_say_what_the_numbers_were_measured_on():
    for path in (*READMES, CHANGELOG):
        assert NOTE in _flat(path), f"{path}: does not say the 300 was {NOTE}"


def test_budget_and_mirror():
    text = SKILL.read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 200
    for tree in TREES[1:]:
        assert tree.read_text(encoding="utf-8") == text, f"{tree} drifted"
