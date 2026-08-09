"""The AI-team surface: the advisor pipeline stays command-honest, the teacher corpus is
well-formed, and the roster points only at personas that exist.

Two load-bearing checks mirror test_surface.py's anti-seam test:
- every `add <verb>` streams.md tells an agent to run is a real dispatch verb, and
- every persona the roster names exists in the teacher corpus.
A subagent that a skill promises but an engine can't feed is the same silent seam, one layer up.
"""
import pytest
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
# The package corpus is the rich 256-file tree NESTED by division at the package root — not
# add-skill-2's flat `templates/personas-teacher/`. Persona files are the ones carrying frontmatter;
# README/VENDOR/examples are prose that ships alongside them (the engine's `scan()` excludes the
# whole tree as vendored material for the same reason).
TEACHER = REPO / "personas-teacher"
STREAMS = SKILL / "streams.md"
SEED = SKILL / "seed.md"
sys.path.insert(0, str(REPO / "tooling"))

import argparse  # noqa: E402
import cli  # noqa: E402  — the real ABF-1 CLI the surface must stay honest to


def _cli_verbs():
    sub = [a for a in cli.build_parser()._actions if isinstance(a, argparse._SubParsersAction)][0]
    return set(sub.choices)

# The four machine-readable parts every persona carries (personas.md §"machine-readable parts").
REQUIRED_PARTS = ("Identity", "Critical Rules", "Default Requirement", "Success Metrics")


def _frontmatter(text: str) -> str:
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def test_streams_ref_exists_and_within_split_threshold():
    assert STREAMS.exists(), "skill/streams.md (the advisor pipeline) is missing"
    n = len(STREAMS.read_text(encoding="utf-8").splitlines())
    assert n <= 350, f"streams.md is {n} lines — split it (T3 rule)"


def test_streams_commands_are_real_dispatch_verbs():
    """Every `add <verb>` streams.md names maps to a real CLI verb — no promised seam."""
    text = STREAMS.read_text(encoding="utf-8")
    verbs = {m.group(1) for line in text.splitlines()
             if (m := re.match(r"add\s+([a-z-]+)", line.strip()))}
    assert verbs, "streams.md names no `add <verb>` — the pipeline must cite the real engine"
    unknown = verbs - _cli_verbs()
    assert not unknown, f"streams.md names commands with no dispatch verb: {sorted(unknown)}"


def test_streams_wraps_the_real_subagent_brief():
    """The pipeline must build on the engine's actual standalone-brief flag, not a fiction."""
    text = STREAMS.read_text(encoding="utf-8")
    assert "--for-subagent" in text, "streams.md must wrap `add brief --for-subagent` (the real flag)"
    assert "--for-subagent" in Path(REPO / "tooling" / "cli.py").read_text(), \
        "the --for-subagent flag vanished from the CLI — the surface now cites a fiction"


def test_streams_keeps_the_gate_floors():
    """A subagent is hands + lens; the surface must not let it gate, freeze, or soften security."""
    text = STREAMS.read_text(encoding="utf-8").lower()
    assert "hard-stop" in text, "streams.md must restate security = HARD-STOP (un-persona-negotiable)"
    assert "never" in text and "gate" in text, "streams.md must state a subagent never owns the gate"


def test_streams_documents_the_rule5_envelope():
    """The skill wraps the engine brief in the Rule-5 shape — the envelope parts must be named."""
    text = STREAMS.read_text(encoding="utf-8").lower()
    for part in ("objective", "persona", "success", "confidence"):
        assert part in text, f"streams.md's subagent envelope omits `{part}` (Rule-5 shape)"


def _teacher_personas():
    """Corpus files that are personas — the ones carrying frontmatter, found recursively."""
    return sorted(p for p in TEACHER.rglob("*.md") if _frontmatter(p.read_text(encoding="utf-8", errors="replace")))


def test_teacher_corpus_has_worked_personas():
    assert TEACHER.is_dir(), "personas-teacher/ (the seed source) is missing"
    personas = _teacher_personas()
    assert len(personas) >= 3, f"teacher corpus has {len(personas)} personas (want >= 3 archetypes)"


def test_each_teacher_persona_is_identifiable():
    """Every corpus persona carries the identity the roster and `seed.md` route on.

    NOTE — this is deliberately weaker than add-skill-2's `test_each_teacher_persona_is_well_formed`,
    which additionally required `flow:` and the four `personas.md` body parts. The package corpus is
    a different, larger body of material on the 2.x agent-definition schema
    (`name`/`description`/`color`/`emoji`/`vibe`): 0 of its 232 persona files carry `flow:` and only
    51 carry `Success Metrics`. Asserting the add-skill-2 schema here would be red on 232 files, and
    weakening it to a vacuous glob is how it passed silently before. Routing is checked instead by
    `test_corpus_carries_the_documented_routing_metadata` below, against the sidecar index.
    """
    for path in _teacher_personas():
        fm = _frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        rel = path.relative_to(TEACHER).as_posix()
        assert re.search(r"^name:", fm, re.M), f"{rel}: frontmatter missing `name:`"
        assert re.search(r"^description:", fm, re.M), f"{rel}: frontmatter missing `description:`"


def test_corpus_carries_the_documented_routing_metadata():
    """Every teacher persona is routable by a `use-when:` — from the sidecar, not from its frontmatter.

    This was a recorded, skipped gap: `personas.md` documents `use-when:` routing, but the corpus
    carries none of it. The resolution is NOT to add the key to those files. `personas-teacher/` is
    a byte-verbatim third-party snapshot (`VENDOR.md`, `THIRD_PARTY_NOTICES.md`) that
    `scripts/update_teacher.py` replaces wholesale — an in-tree edit would fork the vendor AND be
    erased on the next refresh. So the routing metadata lives in `personas-index/use-when.md`, generated
    beside the snapshot by `scripts/build_persona_index.py` and vendored into every bundle.

    `flow:` is deliberately not asserted anywhere: which beats a lens applies to is authored
    judgment (the roster above), not something derivable from a description. Synthesizing one per
    persona would be routing metadata nobody authored.
    """
    index = TEACHER.parent / "personas-index" / "use-when.md"
    assert index.is_file(), "the persona routing index is missing — run scripts/build_persona_index.py"
    text = index.read_text(encoding="utf-8")

    missing = [path.relative_to(TEACHER).with_suffix("").as_posix()
               for path in _teacher_personas()
               if f"`{path.relative_to(TEACHER).with_suffix('').as_posix()}`" not in text]
    assert not missing, (f"{len(missing)} teacher personas have no `use-when:` in the index "
                         f"(regenerate it), e.g. {missing[:3]}")


def test_the_routing_index_is_not_inside_the_vendored_snapshot():
    """R:VENDORFORK — the sidecar must stay a sibling; in-tree, a teacher refresh would erase it."""
    assert not list(TEACHER.rglob("use-when.md")), \
        "the routing index is inside the verbatim snapshot — update_teacher.py would erase it"


def test_seed_ref_is_command_honest_and_cites_the_teacher():
    """The setup-time seed flow names only real verbs and distils from the real corpus."""
    assert SEED.exists(), "skill/seed.md (the setup-time seed flow) is missing"
    text = SEED.read_text(encoding="utf-8")
    verbs = {m.group(1) for line in text.splitlines()
             if (m := re.match(r"add\s+([a-z-]+)", line.strip()))}
    unknown = verbs - _cli_verbs()
    assert not unknown, f"seed.md names commands with no dispatch verb: {sorted(unknown)}"
    assert "new Persona" in text, "seed.md must scaffold via `add new Persona`"
    assert "personas-teacher" in text, "seed.md must cite the teacher corpus it distils from"


def test_seed_keeps_the_no_lifecycle_invariant():
    """A persona never freezes/gates — seed.md must say so, so the loop can't drift back to it."""
    text = SEED.read_text(encoding="utf-8").lower()
    assert "no lifecycle" in text or "never freeze" in text, \
        "seed.md must state a persona has no task lifecycle (never freezes/gates)"


def test_roster_points_only_at_personas_that_exist():
    """Every persona slug the roster table names resolves to a real teacher-corpus file."""
    text = STREAMS.read_text(encoding="utf-8")
    # The nested corpus is cited by its full `<division>/<slug>` path, so resolve the whole path —
    # a stricter check than the flat `<slug>` form: a right slug under a wrong division still fails.
    have = {p.relative_to(TEACHER).with_suffix("").as_posix() for p in TEACHER.rglob("*.md")}
    cited = set(re.findall(r"personas-teacher/([a-z0-9-]+(?:/[a-z0-9-]+)*)", text))
    assert cited, "streams.md's roster names no teacher persona — the roster must cite the corpus"
    missing = cited - have
    assert not missing, f"roster names personas with no corpus file: {sorted(missing)}"
