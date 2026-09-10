"""For code, the default frozen check is an acceptance check, and only BOUND checks are frozen.

Direct-lane change under `/milestones/evidence-over-tests.md` (criterion C2).

The book said acceptance form was for non-code work and that "the two modes never mix within one
task" — so a coding task was told to freeze a unit suite by default. The gate cannot tell the two
apart; it reads test ids from a JUnit report. What the human CAN tell apart is a Given/When/Then
example they can confirm versus a test id with a caption. So: the readable example is a filled
E-edge, an acceptance check covers it, the mode word is a closed list stated once in the guide and
once in the book (parity-pinned, the `test_grammar_stated_once` pattern), and Build freezes only the
checks `## CHECKS` names — every other test is the builder's to write and delete.
"""
import re
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parents[2]
SKILL = ADD_METHOD / "skill" / "add"
DIRECTION = SKILL / "phases" / "direction.md"
BUILD = SKILL / "phases" / "build.md"
DOC03 = ADD_METHOD / "docs" / "03-direction.md"
DOC04 = ADD_METHOD / "docs" / "04-build.md"

MODES = re.compile(r"`acceptance · property · contract · static · unit · e2e · manual`")


def _flat(p: Path) -> str:
    return " ".join(p.read_text(encoding="utf-8").split())


def test_the_book_no_longer_forbids_mixing_check_forms():
    for p in (DOC03, DIRECTION):
        assert "never mix" not in _flat(p), f"{p.name}: still forbids acceptance checks on code"


def test_mode_vocabulary_stated_once_in_guide_and_once_in_book():
    """One closed list, byte-identical in both places an agent or a reader learns it."""
    for p in (DIRECTION, DOC03):
        found = MODES.findall(p.read_text(encoding="utf-8"))
        assert len(found) == 1, f"{p.name}: mode vocabulary appears {len(found)} times, want exactly 1"


def test_acceptance_is_the_default_for_code():
    for p in (DIRECTION, DOC03):
        t = _flat(p)
        assert "default frozen check" in t and "acceptance" in t, f"{p.name}: no default stated"
        assert "through the port" in t or "through the application's port" in t, \
            f"{p.name}: acceptance is not tied to the port"


def test_the_readable_example_is_a_filled_edge():
    t = _flat(DIRECTION)
    assert re.search(r"Given .*? · When .*? · Then ", t), "direction.md: no Given/When/Then edge form"
    assert "covers at least one filled edge" in t, "direction.md: acceptance checks are not bound to an example"


def test_red_is_narrowed_to_absence():
    t = _flat(DIRECTION)
    assert "never proves the reading" in t, "direction.md: red is still read as proof of the oracle"


def test_plan_offers_a_port_line():
    assert "port:" in _flat(DIRECTION), "direction.md: PLAN has no optional port line"


def test_build_freezes_only_bound_checks():
    for p in (BUILD, DOC04):
        t = _flat(p)
        assert "Change no check." not in t, f"{p.name}: still freezes every test"
        assert re.search(r"[Cc]hange no \*{0,2}bound\*{0,2} check", t), f"{p.name}: does not say BOUND"
        assert "yours" in t, f"{p.name}: unbound tests are not given to the builder"
