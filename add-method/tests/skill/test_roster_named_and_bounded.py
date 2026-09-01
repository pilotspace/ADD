"""The roster must name agents that exist, and each agent must know which verbs it may run.

Two failures, both invisible until an orchestrator followed the guide literally:

  R:PHANTOMAGENT  `streams.md`'s roster table named `backend-expert` · `python-expert` ·
                  `security-expert` · `frontend-expert` in its executor column. This package
                  ships exactly two agents — `add-worker` and `add-advisor` — and the skill's
                  delegation text named NEITHER. A reader with no such subagent installed was
                  told to spawn four things they do not have, and never told about the two they
                  do. The persona column was already bound to the corpus; the executor column
                  was bound to nothing.
  R:SELFSEAL      Each agent file forbids "marking a freeze, gate, or lock" in prose but never
                  names the VERBS. A cold agent that must infer a verb name invents one, and the
                  verbs that mark a human seam are exactly the ones it must never call. The
                  boundary is now an explicit list on both sides — MAY and NEVER.

`add-worker` also gained an `explore` mode: `phases/explore.md` shipped with no mode pointing at it.
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
AGENTS = REPO / "agents"
STREAMS = SKILL / "streams.md"
WORKER = AGENTS / "add-worker.md"
ADVISOR = AGENTS / "add-advisor.md"

sys.path.insert(0, str(REPO / "tooling"))
import cli  # noqa: E402

# The verbs that MARK A HUMAN SEAM. Never inferable from prose; an agent must be told the names.
SEAM_VERBS = ("freeze", "gate", "done", "milestone-done", "check")


def _shipped_agents() -> set:
    """The roster the INSTALLER lands on a user's disk — the authority on what is spawnable (A2)."""
    return {p.stem for p in AGENTS.glob("*.md")}


def _engine_verbs() -> set:
    sub = next(a for a in cli.build_parser()._actions
               if getattr(a, "choices", None) and isinstance(a.choices, dict))
    return set(sub.choices)


def _executor_cells() -> list:
    """The `Suggested agentType` column of the roster table, one cell per row."""
    out = []
    for line in STREAMS.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or "agentType" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 3 and "personas-teacher" in cells[1]:
            out.append(cells[2])
    return out


def _named_agents(cell: str) -> set:
    return set(re.findall(r"`([a-z][a-z0-9-]+)`", cell))


# --- M1/M2 — the roster names what ships ----------------------------------------------------

def test_the_roster_names_only_shipped_agents():
    """covers: M1, A2, R:PHANTOMAGENT · bound to the installer's roster tree."""
    cells = _executor_cells()
    assert cells, "the roster table's executor column did not parse — the parser is broken"
    shipped, phantom = _shipped_agents(), {}
    for i, cell in enumerate(cells, 1):
        gone = sorted(_named_agents(cell) - shipped)
        if gone:
            phantom[f"row {i}"] = gone
    assert not phantom, (f"the roster tells the reader to spawn agents this package does not "
                         f"ship: {phantom} — shipped: {sorted(shipped)}")


def test_a_specialist_stays_an_optional_upgrade():
    """covers: A4, E1 · the table permits without requiring."""
    text = STREAMS.read_text(encoding="utf-8")
    assert re.search(r"\bupgrade\b|\bif you have\b|\boptional\b", text, re.I), \
        "the roster must still PERMIT an environment-specific specialist, as an upgrade"
    for cell in _executor_cells():
        assert _named_agents(cell) & _shipped_agents(), \
            "every row must name a DEFAULT that ships, not only a specialist a reader may lack"


def test_the_skill_names_the_shipped_roster():
    """covers: M2 · the delegation text names both agents."""
    text = STREAMS.read_text(encoding="utf-8")
    for agent in sorted(_shipped_agents()):
        assert agent in text, f"the delegation guide never names `{agent}`, which it ships"


# --- M3/M4/A1/A5/A6 — the verb boundary is explicit -----------------------------------------

def test_each_agent_states_its_permitted_verbs():
    """covers: M3, A1, A6 · derived from the phase guides, named literally."""
    for agent in ("add-worker.md", "add-advisor.md"):
        _assert_permitted_verbs(agent)


def _assert_permitted_verbs(agent):
    text = (AGENTS / agent).read_text(encoding="utf-8")
    assert re.search(r"\bMAY RUN\b", text), f"{agent} never states which verbs it MAY run"
    named = set(re.findall(r"`add ([a-z][a-z-]+)`", text))
    assert named & _engine_verbs(), f"{agent}'s permitted list names no real engine verb"
    unknown = named - _engine_verbs()
    assert not unknown, f"{agent} names verbs the engine does not have: {sorted(unknown)}"


def test_the_seam_verbs_stay_forbidden():
    """covers: M4, A5, R:SELFSEAL · the NEVER list is explicit and complete."""
    for agent in ("add-worker.md", "add-advisor.md"):
        _assert_seam_forbidden(agent)


def _assert_seam_forbidden(agent):
    text = (AGENTS / agent).read_text(encoding="utf-8")
    assert "NEVER RUN" in text, f"{agent} has no explicit NEVER list — a verb is forbidden by prose only"
    never = text.split("NEVER RUN", 1)[1].split("\n\n", 1)[0]
    missing = [v for v in SEAM_VERBS if f"`add {v}`" not in never]
    assert not missing, f"{agent}'s NEVER list omits the seam verbs {missing}"
    assert re.search(r"security", text, re.I), f"{agent} must keep security a HARD-STOP"


def test_a_verb_absent_from_both_lists_is_forbidden(): 
    """covers: A10 · the default is closed, and the file says so."""
    for agent in (WORKER, ADVISOR):
        text = agent.read_text(encoding="utf-8")
        assert re.search(r"not (?:on|in) (?:the |either )?(?:MAY|list)|forbidden by default"
                         r"|anything not listed", text, re.I), \
            f"{agent.name} never states that an unlisted verb is forbidden"


# --- M5 — the explore lane is reachable -----------------------------------------------------

def test_the_worker_carries_an_explore_mode():
    """covers: M5 · the mode points at the explore guide."""
    assert (SKILL / "phases" / "explore.md").is_file(), "the explore guide is missing"
    text = WORKER.read_text(encoding="utf-8")
    assert re.search(r"\*\*explore\*\*", text), "add-worker has no `explore` mode"
    assert "phases/explore.md" in text, "the explore mode must point at its guide"


# --- M6/E2/E3 — the vocabulary is current and the tree is linted ----------------------------

# A `§n` is retired vocabulary only when it numbers a NODE section — the 2.x TASK.md format
# addressed its contract, scope and suite by number, and the current format addresses them by
# NAME (`## RULES` · `scope:` · `## CHECKS`). An agent file numbering ITS OWN headings ("the
# advisor trigger in §4") is self-reference and stays legal, so the discriminator is whether a
# node noun rides the same line — not the marker alone.
NODE_NOUN = r"scope|suite|contract|checks|tests|scenarios|section"
RETIRED = re.compile(rf"§\d[^\n]*\b(?:{NODE_NOUN})\b|\b(?:{NODE_NOUN})\b[^\n]*§\d"
                     r"|\bSpecify\b|\bScenarios section\b|\bnew-task\b|\badvance\b", re.I)


def test_no_agent_file_names_a_retired_section():
    """covers: M6, E3 · the 2.x vocabulary is gone or defined."""
    for agent in ("add-worker.md", "add-advisor.md"):
        _assert_no_retired_section(agent)


def _assert_no_retired_section(agent):
    hits = []
    for i, line in enumerate((AGENTS / agent).read_text(encoding="utf-8").splitlines(), 1):
        if RETIRED.search(line):
            hits.append(f"{agent}:{i}  {line.strip()[:110]}")
    assert not hits, "an agent file names a section the current format does not have:\n" + "\n".join(hits)


def test_refute_read_is_defined_where_it_is_used():
    """covers: E3 · a load-bearing term the reader can resolve."""
    if "refute-read" not in WORKER.read_text(encoding="utf-8"):
        pytest.skip("the term was renamed away — nothing to define")
    verify = (SKILL / "phases" / "verify.md").read_text(encoding="utf-8")
    assert "refute-read" in verify, \
        "add-worker sends the reader to phases/verify.md for the refute-read, which never defines it"


def test_the_agent_files_are_under_the_shipped_doc_lint():
    """covers: M6, E2 · the roster tree is swept."""
    lint = (REPO / "tests" / "test_shipped_docs.py").read_text(encoding="utf-8")
    assert '"agents"' in lint or "/ \"agents\"" in lint, \
        "test_shipped_docs.py never sweeps agents/ — a phantom verb in the roster ships unchecked"


def test_the_orchestrator_owns_node_creation():
    """covers: A3 · the agent file states the node exists at spawn."""
    text = WORKER.read_text(encoding="utf-8")
    assert re.search(r"node already exists|the orchestrator (?:has )?(?:already )?creat", text, re.I), \
        "add-worker never says who created the node — two actors can race to create it"


def test_the_persona_mode_writes_nothing():
    """covers: E4 · the service mode's total prohibition is unchanged."""
    text = WORKER.read_text(encoding="utf-8")
    assert "never overwrite an existing persona file" in text, \
        "the persona service mode lost its total write prohibition"
