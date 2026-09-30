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


REFERENCES = ("references/format.md", "references/explore.md", "references/evidence.md",
              "references/personas.md")


def test_the_method_is_one_skill_file_and_four_references():
    assert _method_files(SKILL) == {"SKILL.md", *REFERENCES}


def test_references_are_routed_by_a_trigger():
    """A reference the skill never sends the model to is dead weight; each is named in SKILL.md."""
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    missing = [r for r in REFERENCES if f"`{r}`" not in text]
    assert not missing, f"SKILL.md never routes the model to {missing}"


# Each closed-loop invariant (ADD_3_6_Closed_Loop_Research.md §17) and the two Verify semantics it
# adds, with the phrase that states it on the path the model walks — SKILL.md, not a reference.
CLOSED_LOOP = {
    "C1 rule origin": "derived:",
    "C2 forward coverage": "at least one per Must and Reject",
    "C3 verifier potency": "falsifier",
    "C4 independent evidence": "counter-lens",
    "C5 regression floor": "regression:",
    "C6 artifact identity": "Tag only",
    "C7 runtime mapping": "observes:",
    "C8 escape prevention": "prevention",
    "C9 dependency impact": "consumers",
    "C10 historical immutability": "fixes:",
    "C11 ceremony tripwire": "is a Task now",
    "C12 ceremony economics": "yield",
    "§5 second reader before the seal": "second reader",
    "§10.1 PASS is an evidence claim": "PASS means",
}


def test_every_closed_loop_invariant_is_stated():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    missing = [k for k, phrase in CLOSED_LOOP.items() if phrase not in text]
    assert not missing, f"SKILL.md does not state {missing}"


def test_task_template_carries_risks_and_falsifier():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    block = re.search(r"```markdown\n(.*?)```", text, re.S).group(1)
    assert re.search(r"^risks: ", block, re.M), "the task template has no risks: slot"
    assert "falsifier:" in block, "the CHECKS line has no falsifier slot"


def test_round3_gaps_are_stated():
    """benchmark/PILOT-4v3-2026-09-29.md + the task-contract audit: two contracts left a Must with
    no check, `found:` was almost never used, and 5 of 9 apps crashed on a null or number body."""
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for phrase in ("every RULES id", "check the cheap ones now", "malformed or wrong-typed input"):
        assert phrase in text, f"SKILL.md does not state {phrase!r}"


def test_subagents_are_security_only_one_per_beat_foreground():
    """One amb1 run spawned three subagents and one wm1 run slept on a wakeup waiting for one; the
    second reader's measured gain came from security work. SKILL.md and every reference agree."""
    flat = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split())
    assert "one per beat" in flat and "foreground" in flat, "SKILL.md sets no subagent budget"
    stale = ("subagent for security · data · architecture", "security · data · architecture: a fresh subagent",
             "Security · data · architecture: a fresh subagent", "parallel subagents")
    for name in ("SKILL.md", *REFERENCES):
        body = " ".join((SKILL / name).read_text(encoding="utf-8").split())
        hits = [s for s in stale if s in body]
        assert not hits, f"{name} still sends work to subagents beyond the budget: {hits}"


PERSONA_DIRS = (PKG / "personas", REPO / ".add" / "personas")


def _fm(path: Path) -> str:
    return path.read_text(encoding="utf-8").split("---", 2)[1]


def test_starter_personas_carry_routing_fields():
    """covers-risks routes by the task's risks:, evidence names what the lens must prove, and
    counter-lens names the orthogonal lens a refuter loads (ADD_Dynamic_Persona_Research.md §7.2)."""
    problems = []
    for d in PERSONA_DIRS:
        names = {p.stem for p in d.glob("*.md")}
        assert names, f"no personas in {d}"
        for p in sorted(d.glob("*.md")):
            fm = _fm(p)
            for field in ("covers-risks:", "evidence:", "counter-lens:"):
                if not re.search(rf"^{field} *\S", fm, re.M):
                    problems.append(f"{p.relative_to(REPO)} lacks {field}")
            m = re.search(r"^counter-lens: *(.+)$", fm, re.M)
            for name in (re.split(r"[,\s\[\]]+", m.group(1)) if m else []):
                if name and (name not in names or name == p.stem):
                    problems.append(f"{p.relative_to(REPO)} counter-lens {name!r} is not another persona")
    assert not problems, "\n".join(problems)


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
