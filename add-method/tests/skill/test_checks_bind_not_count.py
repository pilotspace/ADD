"""A check binds a referent; it does not count them.

Direct-lane change under `/milestones/evidence-over-tests.md` (criterion C1).

The gate's rule — `uncovered_obligations()` — is that every Must, Reject, filled edge and probed
assumption is named by at least one PASSING check, and FORMAT §8.3 lets one `covers:` name several
referents. The prose said something narrower and older: "one check per Must and per Reject". Read
literally by an agent it produces a quota — N rules, N tests — which is test COUNT standing in for
evidence. The gate never asked for that. The prose now states the rule the gate enforces, in every
tree that ships it, and says what a check is FOR: to fail on the most plausible wrong implementation.
"""
import re
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parents[2]
REPO = ADD_METHOD.parent

SHIPPED_TREES = [
    ADD_METHOD / "skill" / "add",
    ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add",
    ADD_METHOD / "docs",
]
DOGFOOD_TWIN = REPO / ".claude" / "skills" / "add"     # exists-skip, like test_tree_parity

QUOTA = re.compile(r"one (?:check|test) per (?:`?Must`?|rule)|one per Must", re.I)


def _md_files(tree: Path):
    return sorted(p for p in tree.rglob("*.md") if "node_modules" not in p.parts)


def _flat(p: Path) -> str:
    return " ".join(p.read_text(encoding="utf-8").split())


def test_no_shipped_tree_states_a_check_quota():
    trees = SHIPPED_TREES + ([DOGFOOD_TWIN] if DOGFOOD_TWIN.exists() else [])
    hits = [f"{p.relative_to(REPO)}: {m.group(0)!r}"
            for t in trees for p in _md_files(t)
            for m in [QUOTA.search(_flat(p))] if m]
    assert not hits, "a shipped tree still sizes CHECKS as a quota:\n  " + "\n  ".join(hits)


def test_the_guard_itself_matches_the_quota_phrase():
    """Prove the pattern above can go red: withhold nothing, feed it the old sentence."""
    assert QUOTA.search("one check per `Must` and per `Reject`")
    assert QUOTA.search("one per Must and per Reject")
    assert QUOTA.search("one check per rule and per edge")


def test_direction_states_the_binding_rule_the_gate_enforces():
    """The positive statement, in both places an agent reads it: the router and the beat guide."""
    for rel in ("SKILL.md", "phases/direction.md"):
        text = _flat(ADD_METHOD / "skill" / "add" / rel)
        assert "at least one check" in text, f"{rel}: the ≥1 rule is not stated"
        assert "plausible wrong implementation" in text, f"{rel}: a check is not told what it is FOR"
    direction = _flat(ADD_METHOD / "skill" / "add" / "phases" / "direction.md")
    assert "may cover several" in direction, "direction.md: a shared check is not permitted in words"
