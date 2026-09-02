"""The persona schema owner must describe the keys the roster actually selects on.

Two claims in the shipped skill were false, and each was false in a way that cost the author
something concrete:

  R:UNREADKEY     `personas.md` told the author that `flow:` "and `not-when:` are recommended,
                  hand-authored, and read by nothing" — while `agents/add-worker.md` selects a
                  persona BY `flow:` and BY `task-kinds:`, and `add doctor` reports an invalid
                  value in either. An author told a key is inert leaves it blank, and the tier-1
                  selector then finds nothing to route on. `task-kinds:` was never mentioned at all.
  R:PHANTOMLENS   `seed.md` named `backend-systems` · `security-reviewer` · `frontend-ux` as the
                  corpus's archetypes. None of the three exists: the corpus is `<division>/<slug>`
                  and carries none of those names, so every reader following the guide looked for
                  a file that was never shipped.

The incumbent resolution guard (`test_streams.py::test_roster_points_only_at_personas_that_exist`)
saw neither: it read ONE file and matched only the full `personas-teacher/<path>` form. It is
generalised here to every shipped skill file and to a bare backticked slug.
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
TEACHER = REPO / "personas-teacher"
PERSONAS = SKILL / "personas.md"
SEED = SKILL / "seed.md"
STREAMS = SKILL / "streams.md"
AGENTS = REPO / "agents"

sys.path.insert(0, str(REPO / "tooling"))
import add as engine  # noqa: E402

# The two keys the shipped roster SELECTS on. Read from the engine's own closed vocabularies,
# never restated, so a third routing key added there lands in this guard automatically.
SELECTOR_KEYS = ("flow", "task-kinds")


def _skill_files():
    return sorted(p for p in SKILL.rglob("*.md") if p.is_file())


def _scaffolded_keys() -> set:
    """The frontmatter keys `add new Persona` actually writes — parsed from the scaffold writer.

    A1: the contractual set is whatever the engine scaffolds, so it is read from the source and
    never transcribed. Transcribing it is how the document and the scaffold drifted apart.
    """
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    block = src.split('if node_type == "Persona":', 1)[1].split("fm.update(", 1)[0]
    keys = set(re.findall(r'^\s*\("([a-z-]+)",', block, re.M))
    assert len(keys) >= 5, f"the scaffold parser broke, not the doc — found {keys}"
    return keys


def _executor_names() -> set:
    """Every subagent name that could stand in the roster's EXECUTOR column — the shipped roster
    plus the `<x>-expert` convention the table uses for environment-specific specialists."""
    return {p.stem for p in AGENTS.glob("*.md")}


def _is_executor(slug: str) -> bool:
    """An executor is a shipped roster agent, or a name in the `<domain>-expert` convention the
    table uses for an environment-specific specialist. A RULE, not a list: a new specialist row
    must not need this guard edited. Which executors are real is `roster-named-and-bounded`'s
    question, bound there — never silently re-answered here."""
    return slug in _executor_names() or slug.endswith("-expert")


def _corpus_slugs() -> set:
    """Both resolvable forms: the full `<division>/<slug>` path and the bare `<slug>`."""
    full = {p.relative_to(TEACHER).with_suffix("").as_posix() for p in TEACHER.rglob("*.md")}
    return full | {p.rsplit("/", 1)[-1] for p in full}


# --- M1/A1 — the schema owner states the real set ------------------------------------------

def test_personas_md_states_the_scaffolded_key_set():
    """covers: M1, A1 · the documented set is enumerated from the scaffold source."""
    text = PERSONAS.read_text(encoding="utf-8")
    missing = sorted(k for k in _scaffolded_keys() if f"`{k}:`" not in text)
    assert not missing, (f"personas.md never names the keys `add new Persona` scaffolds: {missing} — "
                         f"an author cannot fill a slot the schema owner does not mention")


def test_the_selector_keys_are_marked_and_the_roster_is_cited():
    """covers: M1, A3 · the sentence cites the roster file that reads the key, by path."""
    text = PERSONAS.read_text(encoding="utf-8")
    for key in SELECTOR_KEYS:
        assert f"`{key}:`" in text, f"personas.md never names `{key}:`"
    assert "add-worker" in text, \
        "personas.md must CITE the roster file that reads the selector keys, not merely assert it"


def test_no_skill_file_calls_a_selector_key_unread():
    """covers: M2, R:UNREADKEY · the false clause is gone everywhere."""
    dead = re.compile(r"read by nothing|reads? (?:by )?nothing|not read by|no(?:thing)? reads")
    offences = []
    for f in _skill_files():
        flat = " ".join(f.read_text(encoding="utf-8").split())
        for m in dead.finditer(flat):
            window = flat[max(0, m.start() - 260):m.end() + 120]
            if any(f"`{k}:`" in window for k in SELECTOR_KEYS):
                offences.append(f"{f.relative_to(REPO)}: …{window[-200:]}")
    assert not offences, "a shipped file calls a key the roster selects on unread:\n" + "\n".join(offences)


def test_the_selector_keys_really_are_read():
    """covers: M2 · the claim's other half — the roster genuinely reads both keys."""
    roster = " ".join((AGENTS / "add-worker.md").read_text(encoding="utf-8").split())
    for key in SELECTOR_KEYS:
        assert f"`{key}:`" in roster, \
            f"personas.md would be right and the ROSTER wrong — add-worker.md never reads `{key}:`"


# --- M3/R:PHANTOMLENS — every named archetype resolves --------------------------------------

def _cited_archetypes(text: str) -> set:
    """Every teacher reference in a file: the full path form AND a bare backticked slug.

    A bare slug is only read as an archetype claim when the sentence is ABOUT the corpus — an
    example the guide labels hypothetical is not a reference (E3), and neither is an EXECUTOR
    subagent name. The roster table names both columns on one line: a teacher archetype (which
    must resolve to the corpus) and the executor that adopts it (which must resolve to an agent,
    a different question with its own guard). Conflating them is how the first widening read
    `backend-expert` as a missing persona.
    """
    full = set(re.findall(r"personas-teacher/([a-z0-9-]+(?:/[a-z0-9-]+)*)", text))
    bare = set()
    for line in text.splitlines():
        if "personas-teacher" not in line and "corpus" not in line.lower():
            continue
        low = line.lower()
        # A name the sentence itself marks as not-a-live-reference is not a claim that a file
        # exists: a labelled example, or a retired preset cited for provenance. The corpus path
        # such a line ALSO cites stays bound by the full-path branch above.
        if any(w in low for w in ("hypothetical", "e.g.", "for example", "retired", "promoted from")):
            continue
        bare |= {s for s in re.findall(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`", line)
                 if "/" not in s and not _is_executor(s)}
    return {c for c in full | bare if c not in {"personas-teacher", "personas-index", "use-when"}}


def test_every_named_archetype_resolves():
    """covers: M3, R:PHANTOMLENS · enumerated across the whole skill tree."""
    have, missing = _corpus_slugs(), {}
    for f in _skill_files():
        gone = sorted(_cited_archetypes(f.read_text(encoding="utf-8")) - have)
        if gone:
            missing[str(f.relative_to(REPO))] = gone
    assert not missing, f"shipped files name teacher archetypes with no corpus file: {missing}"


def test_the_guard_scans_the_seed_guide():
    """covers: M4, E2 · a bare backticked slug in seed.md is caught."""
    assert SEED in _skill_files(), "the generalised guard must reach seed.md"
    injected = "The corpus at `.add/personas-teacher/` ships `no-such-lens` among others."
    assert "no-such-lens" in _cited_archetypes(injected), \
        "the guard still matches only the full path form — a bare slug slips through"


def test_the_streams_roster_still_resolves():
    """covers: E1 · the incumbent case is unchanged."""
    cited = _cited_archetypes(STREAMS.read_text(encoding="utf-8"))
    assert cited, "streams.md's roster names no teacher persona"
    assert not cited - _corpus_slugs()


def test_a_hypothetical_example_is_not_flagged():
    """covers: E3 · the guard scopes to real references."""
    hypo = "For example, a corpus might ship `made-up-lens` — a hypothetical name."
    assert not _cited_archetypes(hypo), "the guard demands a file for a labelled example"


def test_the_persona_author_references_agree():
    """covers: E4, A3 · no reference contradicts the corrected schema."""
    refs = sorted((SKILL / "persona-author" / "references").rglob("*.md"))
    assert refs, "the persona-author references are missing"
    for f in refs:
        flat = " ".join(f.read_text(encoding="utf-8").split())
        for key in SELECTOR_KEYS:
            assert not re.search(rf"`{key}:`[^.]{{0,160}}read by nothing", flat), \
                f"{f.relative_to(REPO)} contradicts the corrected personas.md about `{key}:`"


def test_this_task_changed_prose_and_a_guard_only():
    """covers: A2 · this task changes prose and a guard only, never the selector.

    A2 took an ABSENT routing key as "routes nothing, and that is a finding" — deliberately NOT
    a silent generic, because making the selector cope is the sibling task's engine work. The
    failure it names is the two tasks disagreeing about the same key, which happens the moment
    this one also edits the selector. So the probe reads the SELECTOR's own vocabularies and
    asserts this task left them exactly as the sibling defined them.
    """
    assert engine.PERSONA_FLOWS == ("design", "build", "advisor", "verify"), \
        "this task moved the flow vocabulary — that is the sibling task's surface"
    assert "explore" in engine.PERSONA_TASK_KINDS, \
        "the task-kind taxonomy changed shape here instead of in the sibling task"

    # The absent key is a FINDING, not a default: doctor stays silent on an unauthored slot and
    # speaks on an authored-but-invalid one. Neither branch invents a generic lens.
    import tempfile
    root = Path(tempfile.mkdtemp())
    engine.init(root, "code", "T")
    cid, _ = engine.new(root, "Persona", "probe-lens", title="Probe lens")
    node = root / cid.lstrip("/")
    assert not [f for f in engine.doctor(root) if f["code"] == "persona_routing_key"], \
        "an UNTOUCHED scaffold slot is reported — a guard fired on a missing thing"
    node.write_text(re.sub(r"^flow: .*$", "flow: nonsense", node.read_text(encoding="utf-8"),
                           flags=re.M), encoding="utf-8")
    found = [f for f in engine.doctor(root) if f["code"] == "persona_routing_key"]
    assert found and found[0]["severity"] == "info", \
        "an authored-but-invalid key is not reported as a finding"
