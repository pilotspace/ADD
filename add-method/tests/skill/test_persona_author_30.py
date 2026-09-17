"""Compatibility suite for persona-author engine truth through the current ADD release.

`references/contract.md` predates the 3.0 clean break and still teaches the 2.5 world:
personas seeded into `.add/personas/` by `init`/`migrate` via `constants.METHOD_PERSONAS`
(a module that does not ship), and a method-lens definition grounded in `PLAN.md` §3
artifacts (files 3.0 does not write). The five phantom-VERB sites were fixed earlier;
this pins the rest of the engine-truth, and ONLY the engine-truth — persona-pattern
vocabulary (the qualification gate, refute-read as a judging stance) is the sub-skill's
teaching voice and deliberately survives. Later approved work made the 3.0 no-seed and
method-lens-only assertions historical; current checks follow the live seed contract.

Driven as dogfood task `.add/tasks/persona-author-30.md` (v3.0.0 hardening tally #1).
"""

from pathlib import Path

SUBSKILL = Path(__file__).resolve().parents[2] / "skill" / "add" / "persona-author"
CONTRACT = (SUBSKILL / "references" / "contract.md").read_text(encoding="utf-8")


def test_contract_names_no_2x_engine_symbols():
    """covers: M1, R:PHANTOM — symbols, files and verbs that do not ship in 3.0."""
    for phantom in ("constants.METHOD_PERSONAS", "PLAN.md", "§3", "`migrate`"):
        assert phantom not in CONTRACT, \
            f"contract.md still teaches the 2.x world: {phantom!r} does not ship in 3.0"


def test_seeding_claim_matches_the_current_engine():
    """Later approved seed work supersedes 3.0's empty-roster claim."""
    assert "seeds **no personas**" not in CONTRACT
    assert "seeds every shipped starting-persona template" in CONTRACT
    assert "never overwrites" in CONTRACT
    assert "add new Persona" in CONTRACT, \
        "the additional-persona authoring path (`add new Persona`) is never named"
    assert "personas-teacher" in CONTRACT or "teacher corpus" in CONTRACT, \
        "the vendored corpus — source material for adaptation — is never named"


def test_starter_lens_line_matches_the_current_templates():
    """The current seed set may contain domain lenses, all owned by the project."""
    assert "Never ship a DOMAIN lens" not in CONTRACT
    assert "starting lenses" in CONTRACT
    assert "adapt" in CONTRACT and "project" in CONTRACT


def test_pattern_vocabulary_survives():
    """covers: A2 (probe) — the scrub is scoped to ENGINE truth, not the teaching voice."""
    patterns = (SUBSKILL / "references" / "patterns.md").read_text(encoding="utf-8")
    skill = (SUBSKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "qualification gate" in patterns, "over-scrub: patterns.md lost its vocabulary"
    assert "qualification gate" in skill, "over-scrub: SKILL.md lost its vocabulary"
