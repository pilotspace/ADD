"""A fresh bundle loads a persona, and a project with none reaches the corpus.

Red-first for `/tasks/persona-tier-live.md`. The `covers:` citations live in each test's docstring.

Measured 2026-09-01: `.add/personas/` is empty on every fresh bundle (3.0 seeds none), ZERO of
232 teacher personas carry `flow:` or `task-kinds:`, and neither agent file names the corpus or
its routing index — so the roster's selector had nothing to search and the generic fallback was
the steady state, unrecorded in any receipt. The three planner templates that DO carry both keys
sat in `tooling/templates/personas/` and were seeded by nothing, while the changelog said they
were seeded at init.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

WORKER = REPO / "agents" / "add-worker.md"
ADVISOR = REPO / "agents" / "add-advisor.md"
ROSTER = (WORKER, ADVISOR)

# The surfaces the roster names for its beats: direction→design · build→build · verify→verify.
ROSTER_BEATS = ("design", "build", "verify")


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / ".add"
    add.init(root, profile="code", title="persona fixture")
    return root


def _seeded(root):
    return sorted((root / "personas").glob("*.md"))


def test_init_seeds_selectable_personas(bundle):
    """covers: M1, A2 · a fresh bundle holds Persona nodes carrying both routing keys."""
    files = _seeded(bundle)
    assert files, "a fresh bundle seeded no personas"
    graph = add.load(bundle)
    personas = [n for n in graph.values() if (n["fm"] or {}).get("type") == "Persona"]
    assert personas, "the seeded files are not Persona nodes"
    for n in personas:
        fm = n["fm"]
        assert fm.get("flow"), f"{fm.get('title')} carries no flow:"
        assert fm.get("task-kinds"), f"{fm.get('title')} carries no task-kinds:"


def test_every_roster_beat_has_a_seeded_match(bundle):
    """covers: M2, R:DEADTIER · each named beat matches at least one seeded persona on flow:."""
    flows = set()
    for n in add.load(bundle).values():
        fm = n["fm"] or {}
        if fm.get("type") == "Persona":
            flows |= {v.strip() for v in str(fm.get("flow", "")).split(",") if v.strip()}
    missing = [b for b in ROSTER_BEATS if b not in flows]
    assert not missing, f"no seeded persona serves the roster beat(s): {missing}"


def test_the_seeded_personas_are_in_taxonomy(bundle):
    """covers: M1 · a seeded persona satisfies the routing-key check it ships beside."""
    assert not [f for f in add.doctor(bundle) if f.get("code") == "persona_routing_key"]


def test_init_never_overwrites_an_existing_persona(bundle, tmp_path):
    """covers: M5, A5, E1, E4 · existing files are byte-identical after re-init."""
    target = _seeded(bundle)[0]
    target.write_text("---\ntype: Persona\ntitle: mine\nflow: build\ntask-kinds: docs\n---\n## Identity\nmine.\n")
    before = target.read_bytes()
    add.init(bundle, profile="code", title="persona fixture")
    assert target.read_bytes() == before


def test_init_names_what_it_seeded(tmp_path_factory):
    """covers: A9 · the note names the seeded personas.

    A root of its OWN — a bundle created beneath the `bundle` fixture's tree is refused by
    the ancestor guard, which is correct behaviour and not what this test is about.
    """
    fresh = tmp_path_factory.mktemp("standalone") / ".add"
    _, _, note = add.init(fresh, profile="code", title="standalone")
    assert "persona" in note.lower()
    assert "build-craftsman" in note


def test_both_agents_name_the_corpus_tier():
    """covers: M3, R:SILENTGENERIC · both route through the index before the generic."""
    for f in ROSTER:
        text = f.read_text(encoding="utf-8")
        assert "personas-index" in text, f"{f.name} never names the routing index"
        assert "personas-teacher" in text, f"{f.name} never names the teacher corpus"


def test_the_corpus_tier_routes_through_the_index():
    """covers: A3 · the tier names the index, never a corpus glob."""
    for f in ROSTER:
        flat = " ".join(f.read_text(encoding="utf-8").split())
        i, g = flat.index("personas-index"), flat.index("personas-teacher")
        assert i < g, f"{f.name} reaches the corpus before the index that routes it"


def test_a_project_persona_beats_a_corpus_lens():
    """covers: A4 · tier order holds — the project's own roster is searched first."""
    for f in ROSTER:
        flat = " ".join(f.read_text(encoding="utf-8").split())
        assert flat.index(".add/personas/") < flat.index("personas-index"), \
            f"{f.name} reaches the corpus before the project's own roster"


def test_the_generic_fallback_survives_and_is_last():
    """covers: M4, E3 · an unmatched task proceeds, and the fallback is last."""
    for f in ROSTER:
        flat = " ".join(f.read_text(encoding="utf-8").split())
        assert "generic fallback" in flat
        assert flat.index("personas-index") < flat.index("generic fallback"), \
            f"{f.name} falls back before it has searched the corpus"


def test_a_missing_corpus_soft_skips():
    """covers: A6, E2 · a lean install with no corpus still selects and proceeds."""
    for f in ROSTER:
        flat = " ".join(f.read_text(encoding="utf-8").split()).lower()
        assert "not installed" in flat or "absent" in flat or "no corpus" in flat, \
            f"{f.name} never says what to do when the corpus is not on disk"


def test_the_corpus_tier_states_its_tie_break():
    """covers: A7 · the order is documented in the agent file."""
    for f in ROSTER:
        flat = " ".join(f.read_text(encoding="utf-8").split()).lower()
        assert "tie" in flat or "nearest" in flat, f"{f.name} states no tie-break"


def test_the_agent_return_names_its_tier():
    """covers: A8 · the return distinguishes project, corpus and generic."""
    for f in ROSTER:
        flat = " ".join(f.read_text(encoding="utf-8").split()).lower()
        assert "tier" in flat, f"{f.name} never reports which tier its persona came from"
