"""Red suite for `persona-author-30` — the sub-skill's contract speaks 3.0.

`references/contract.md` predates the 3.0 clean break and still teaches the 2.5 world:
personas seeded into `.add/personas/` by `init`/`migrate` via `constants.METHOD_PERSONAS`
(a module that does not ship), and a method-lens definition grounded in `PLAN.md` §3
artifacts (files 3.0 does not write). The five phantom-VERB sites were fixed earlier;
this pins the rest of the engine-truth, and ONLY the engine-truth — persona-pattern
vocabulary (the qualification gate, refute-read as a judging stance) is the sub-skill's
teaching voice and deliberately survives (task assumption A2, probed).

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


def test_seeding_claim_matches_the_30_engine():
    """covers: M1 — 3.0 seeds NO personas; the corpus is vendored, the roster is authored.

    `.add/personas/` itself is a REAL 3.0 path (persona nodes live there) — what must
    not survive is any claim that ADD seeds personas INTO it."""
    for line in CONTRACT.splitlines():
        if ".add/personas/" in line:
            assert "seed" not in line.lower(), \
                f"contract.md still claims personas are seeded: {line.strip()!r}"
    assert "seeds exactly three personas" not in CONTRACT
    assert "add new Persona" in CONTRACT, \
        "the 3.0 authoring path (`add new Persona`) is never named"
    assert "personas-teacher" in CONTRACT or "teacher corpus" in CONTRACT, \
        "the vendored corpus — what 3.0 actually ships — is never named"


def test_lens_line_restated_over_30_artifacts():
    """covers: M2 — the method-lens/domain-lens line survives, on 3.0 artifacts."""
    assert "METHOD LENS" in CONTRACT and "DOMAIN lens" in CONTRACT, \
        "the lens line itself was lost in the scrub"
    assert any(t in CONTRACT for t in ("RULES", "`gives:`", "freeze seal")), \
        "the method-lens definition names no 3.0 artifact"
    assert "Twelve preset personas" in CONTRACT, \
        "the scar story is the rationale for the line — it must survive (A3)"


def test_pattern_vocabulary_survives():
    """covers: A2 (probe) — the scrub is scoped to ENGINE truth, not the teaching voice."""
    patterns = (SUBSKILL / "references" / "patterns.md").read_text(encoding="utf-8")
    skill = (SUBSKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "qualification gate" in patterns, "over-scrub: patterns.md lost its vocabulary"
    assert "qualification gate" in skill, "over-scrub: SKILL.md lost its vocabulary"
