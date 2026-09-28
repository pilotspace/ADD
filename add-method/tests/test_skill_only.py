"""ADD 4.0 ships one skill and no engine.

The method is a markdown skill the model follows; git and the project's own test command are the
only tools it needs. These checks hold that shape: a short skill, no engine files anywhere in the
package, and no instruction that sends the model to a CLI that no longer exists.
"""
import json
import re
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
REPO = PKG.parent
SKILL = PKG / "skill" / "add"

SKILL_TREES = (SKILL,
               PKG / "src" / "add_method" / "_bundled" / "skill" / "add",
               REPO / ".claude" / "skills" / "add")

# The 3.x CLI verbs. A skill sentence that tells the model to run one of these points at nothing.
RETIRED_VERBS = ("status", "init", "new", "brief", "upgrade", "freeze", "interview", "replan",
                 "repair", "run", "gate", "done", "learn", "check", "milestone-done", "deltas",
                 "fold", "drop", "reopen", "milestone-archive", "doctor", "wave", "join", "advise",
                 "refute", "release", "locate", "todo", "show", "search")

SKILL_LINE_CEILING = 200


def _method_files(tree: Path) -> set[str]:
    return {str(p.relative_to(tree)) for p in tree.rglob("*")
            if p.is_file() and "persona-author" not in p.parts and "__pycache__" not in p.parts}


def test_the_method_is_one_skill_file_and_two_references():
    assert _method_files(SKILL) == {"SKILL.md", "references/format.md", "references/explore.md"}


def test_skill_md_stays_short():
    lines = (SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) <= SKILL_LINE_CEILING, f"SKILL.md is {len(lines)} lines"


def test_no_engine_file_ships():
    engine = [PKG / "tooling", PKG / "agents", PKG / "src" / "add_method" / "_bundled" / "tooling",
              PKG / "src" / "add_method" / "_bundled" / "agents", REPO / ".claude" / "agents"]
    present = [str(p.relative_to(REPO)) for p in engine if p.exists()]
    assert not present, f"engine or roster still present: {present}"


def test_npm_package_lists_no_engine_path():
    files = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["files"]
    stale = [f for f in files if f.startswith(("tooling", "agents"))]
    assert not stale, f"package.json still ships {stale}"


def test_skill_prose_sends_the_model_to_no_cli():
    pattern = re.compile(r"`add (" + "|".join(map(re.escape, RETIRED_VERBS)) + r")\b")
    hits = []
    for tree in (SKILL,):
        for md in tree.rglob("*.md"):
            text = md.read_text(encoding="utf-8")
            for n, line in enumerate(text.splitlines(), 1):
                if (pattern.search(line) or any(s in line for s in (
                        "cli.py", "add.py", ".add/tooling", "add-worker", "add-advisor"))):
                    hits.append(f"{md.relative_to(PKG)}:{n}: {line.strip()[:90]}")
    assert not hits, "skill prose still names the engine:\n" + "\n".join(hits)


def test_git_is_the_seal():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "freeze(" in text, "the freeze commit convention is not stated"
    assert "git diff" in text, "verify does not diff the sealed files against the freeze commit"


def test_a_task_needs_no_second_file():
    """The 4.0 pilot spent a whole turn reading references/format.md for the task-file shape
    (benchmark/PILOT-4v3-2026-09-28.md). A Task's template lives inline in SKILL.md."""
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    block = re.search(r"```markdown\n(.*?)```", text, re.S)
    assert block, "SKILL.md carries no inline task template"
    for part in ("type: Task", "status: direction", "## RULES", "## ASSUMPTIONS", "## PLAN",
                 "## CHECKS", "## EVIDENCE"):
        assert part in block.group(1), f"inline template is missing {part!r}"
    assert "shape: `references/format.md`" not in text, "Direction still sends a Task to format.md"


def test_skill_budgets_turns():
    """Tokens scale with turns (each turn re-reads the whole context), not with skill bytes.
    The skill states the batching rule and the per-beat turn shape."""
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "## Turns" in text, "SKILL.md has no turn-budget section"
    section = text.split("## Turns", 1)[1].split("\n## ", 1)[0]
    for phrase in ("re-reads", "one command", "freeze("):
        assert phrase in section, f"turn section does not state {phrase!r}"


def test_shipped_skill_trees_are_identical():
    base = {p: (SKILL / p).read_bytes() for p in (str(q.relative_to(SKILL)) for q in SKILL.rglob("*")
                                                   if q.is_file() and "__pycache__" not in q.parts)}
    for tree in SKILL_TREES[1:]:
        if not tree.exists():
            continue
        other = {str(q.relative_to(tree)): q.read_bytes() for q in tree.rglob("*")
                 if q.is_file() and "__pycache__" not in q.parts}
        assert other == base, f"{tree.relative_to(REPO)} differs from skill/add"
