"""One grammar, three oracles — FORMAT §6.1, the validator, and the engine.

`scripts/validate_bundle.py:55` has claimed this test by name since it shipped:

    `tests/test_covers_grammar.py` holds these against the `covers-grammar`
    block in FORMAT §6.1 and against the engine's `RULE_ID`.

The file did not exist. A comment naming a parity test that is absent is worse than no
claim at all: it reads as "this is checked" to every subsequent reader, which is exactly
the lying-green shape a `covers:` binding exists to prevent — one level up, in the source
that implements the binding.

F1 (drift between the oracles) is what these tests close. The grammar is stated ONCE, in
FORMAT §6.1, and both implementations are held to that statement rather than to each
other — so a drift shows up as a failure here instead of as two subtly different bundles
that each validate under their own reader.
"""
import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

FORMAT_MD = REPO / "FORMAT.md"
VALIDATOR = REPO / "scripts" / "validate_bundle.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_bundle", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _grammar_block() -> str:
    """The ```covers-grammar fenced block of FORMAT §6.1, verbatim."""
    m = re.search(r"^```covers-grammar\n(.*?)^```", FORMAT_MD.read_text(), re.S | re.M)
    assert m, "FORMAT.md has no ```covers-grammar block — §6.1 is cited by both oracles"
    return m.group(1)


def _validator_source_lines() -> str:
    """The two COVERS_* definition lines as they appear in the validator."""
    src = VALIDATOR.read_text()
    lines = [ln for ln in src.splitlines()
             if ln.startswith(("COVERS_QUICK = ", "COVERS_RULE = "))]
    assert len(lines) == 2, f"expected 2 COVERS_* definitions, found {len(lines)}"
    return "\n".join(lines) + "\n"


def test_format_md_exists():
    """SKILL.md ships to every user pointing at this file; the validator cites §9 for its
    own exit code. A missing normative spec is not a documentation gap, it is two oracles
    with no stated authority between them."""
    assert FORMAT_MD.is_file(), "add-method/FORMAT.md is missing"


def test_grammar_stated_once():
    """The block in FORMAT §6.1 IS the validator's source, byte for byte.

    Not "equivalent" — identical. Equivalence would let the two drift into different
    spellings of the same intent, and the next widening (e15 admitted digits to R:<NAME>)
    would land in one place and not the other.
    """
    assert _grammar_block() == _validator_source_lines()


def test_engine_alternation_matches_the_rule_grammar():
    """The engine states the rule half as `RULE_ALT` and reuses it; FORMAT states it as
    `COVERS_RULE`. Same alternation, or a node the engine binds is one the validator
    reports."""
    block = _grammar_block()
    m = re.search(r'COVERS_RULE = re\.compile\(r"\\A\((.+?)\)\\Z"\)', block)
    assert m, "FORMAT §6.1's COVERS_RULE is not in the expected form"
    assert m.group(1) == add.RULE_ALT


# Corpus: every referent shape the format admits, and the near-misses that must not pass.
LEGAL_RULE = ["M1", "M12", "R:OVERADMIT", "R:BAD_DURATION", "R:A1_B2", "E1", "E7"]
LEGAL_QUICK = ["goal", "G1", "G12"]
ILLEGAL = ["M", "R:", "R:lower", "E", "e1", "m1", "Goal", "G", "M1 ", " M1",
           "M1,E2", "R:has space", "R:has-dash"]


@pytest.mark.parametrize("referent", LEGAL_RULE)
def test_standard_depth_admits_every_rule_shape(referent):
    v = _load_validator()
    assert v.COVERS_RULE.match(referent), referent
    assert add.REFERENT.match(referent), f"engine disagrees on {referent}"


@pytest.mark.parametrize("referent", LEGAL_QUICK)
def test_quick_depth_admits_goal_and_gives(referent):
    v = _load_validator()
    assert v.COVERS_QUICK.match(referent), referent
    assert add.REFERENT.match(referent), f"engine disagrees on {referent}"


@pytest.mark.parametrize("referent", ILLEGAL)
def test_both_oracles_reject_the_same_near_misses(referent):
    """Agreement on rejection matters as much as agreement on acceptance — a referent one
    oracle admits and the other refuses is a bundle that validates under exactly one
    reader."""
    v = _load_validator()
    assert not v.COVERS_RULE.match(referent), f"validator admits {referent!r}"
    assert not v.COVERS_QUICK.match(referent), f"validator admits {referent!r}"
    assert not add.REFERENT.match(referent), f"engine admits {referent!r}"


def test_quick_depth_cannot_cite_a_rule():
    """The depth split is the point: at `quick` a check binds to the goal, not to a Must
    the node never enumerated."""
    v = _load_validator()
    for referent in LEGAL_RULE:
        assert not v.COVERS_QUICK.match(referent), referent


def test_r_name_admits_digits():
    """e15, human:tindang 2026-07-30 — widened to match the engine. Pinned so a future
    narrowing has to argue with a test rather than silently invalidate live bundles."""
    v = _load_validator()
    assert v.COVERS_RULE.match("R:A1")
    assert add.REFERENT.match("R:A1")
