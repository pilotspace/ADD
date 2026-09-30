"""The residue lenses a verify beat examines depend on the task's KIND.

Direct change (`residue-by-kind`, milestone `loop-that-closes`): verify.md froze THREE lenses —
security · concurrency · architecture — for every task alike, so a `ui` task was asked about
concurrency and never about the thing tests miss there, and an `infra` one was never asked for its
rollback path. The three universal lenses stay (security is always a HARD-STOP); a FOURTH is owed
by kind, and the router's review column says so, or the ladder promises a review nobody performs.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

TREES = (REPO / "skill" / "add", REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
         REPO.parent / ".claude" / "skills" / "add")
VERIFY = TREES[0] / "phases" / "verify.md"


def _by_kind() -> dict:
    """`{kind: the lens owed}` as verify.md states it — the ONE reader of the table."""
    body = VERIFY.read_text(encoding="utf-8")
    if "residue by kind" not in body:
        return {}
    block = body.split("residue by kind", 1)[1].split("\n\n", 1)[0]
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"`([a-z]+)`\s*·\s*([^—]+)", block)}


def test_every_kind_the_engine_admits_owes_a_lens():
    """A rule that quantifies over a set must ENUMERATE that set: `kind:` is validated against
    `PERSONA_TASK_KINDS`, so a kind the engine admits and the table omits is a task routed to a
    review nobody wrote. `explore` is the one exemption — it builds nothing to leave residue in."""
    table = _by_kind()
    owed = [k for k in add.PERSONA_TASK_KINDS if k != "explore"]
    missing = [k for k in owed if k not in table]
    assert not missing, f"verify.md names no residue lens for: {', '.join(missing)}"
    assert all(table[k].strip() for k in owed), table
    stray = [k for k in table if k not in add.PERSONA_TASK_KINDS]
    assert not stray, f"verify.md names a kind the engine cannot record: {', '.join(stray)}"


def test_the_three_universal_lenses_are_not_replaced():
    """The fourth lens is ADDED, never a substitution: security stays a HARD-STOP for every kind,
    whatever its own lens says."""
    body = VERIFY.read_text(encoding="utf-8")
    for lens in ("security", "concurrency", "architecture"):
        assert re.search(rf"\*\*{lens}\*\*", body), f"the universal lens {lens} was dropped"
    assert "HARD-STOP" in body.split("## 2")[1].split("## 3")[0], "security stopped being a HARD-STOP"


def test_the_router_names_the_residue_it_owes():
    """The ladder's review column is where a router decides what it still owes: a lens named only
    in verify.md is a lens the direct lane — which never opens verify.md — never performs."""
    intake = (TREES[0] / "intake.md").read_text(encoding="utf-8")
    row = next(line for line in intake.splitlines() if line.startswith("| **mechanical**"))
    assert "residue" in row, f"the direct row owes no residue: {row}"


def test_the_three_trees_carry_one_verify():
    for tree in TREES[1:]:
        assert (tree / "phases" / "verify.md").read_bytes() == VERIFY.read_bytes(), tree
        assert (tree / "intake.md").read_bytes() == (TREES[0] / "intake.md").read_bytes(), tree
