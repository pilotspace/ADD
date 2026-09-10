"""The closed probe derivation list and the tier ladder — stated once, parity-pinned.

Direct-lane change under `/milestones/evidence-over-tests.md` (criterion C6).

A probe is a test the builder never saw as a target. What a refuter may derive one from is a
CLOSED list — instantiate, compose, walk a boundary, vary a swept dimension — and the one thing it
may never do is invent a requirement: a probe whose expected answer is not derivable from frozen
RULES, EDGES and interviewed ASSUMPTIONS is a spec silence, routed back to Direction, never a
verdict. The list is read by two parties who must agree — the worker at Verify (`verify.md`) and
the advisor in `refute` mode (`add-advisor.md`) — so it is pinned byte-identical in both, the
`test_grammar_stated_once` pattern. The tier ladder says who refutes at which floor and admits
what a CLI-only method cannot do (a protected holdout is a CI recipe, not a feature).
"""
import re
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parents[2]
REPO = ADD_METHOD.parent
VERIFY = ADD_METHOD / "skill" / "add" / "phases" / "verify.md"
ADVISOR = ADD_METHOD / "agents" / "add-advisor.md"
DOC05 = ADD_METHOD / "docs" / "05-verify.md"
TWINS = [ADD_METHOD / "src" / "add_method" / "_bundled" / "agents" / "add-advisor.md",
         REPO / ".claude" / "agents" / "add-advisor.md"]

DERIVATION = re.compile(r"<!-- probe-derivation -->\n((?:.*\n)*?)<!-- /probe-derivation -->")


def _text(p: Path) -> str:
    assert p.exists(), f"{p} does not exist"
    return p.read_text(encoding="utf-8")


def _derivation(p: Path) -> str:
    m = DERIVATION.search(_text(p))
    assert m, f"{p.name}: no `<!-- probe-derivation -->` block"
    return m.group(1)


def test_derivation_list_stated_once_and_identical_in_guide_and_advisor():
    guide, advisor = _derivation(VERIFY), _derivation(ADVISOR)
    assert guide == advisor, "verify.md and add-advisor.md state different derivation lists"
    assert len(DERIVATION.findall(_text(VERIFY))) == 1 and len(DERIVATION.findall(_text(ADVISOR))) == 1


def test_derivation_list_is_closed_and_forbids_invention():
    d = _derivation(VERIFY)
    for verb in ("instantiate", "compose", "boundary", "vary"):
        assert verb in d, f"derivation list lacks `{verb}`"
    assert re.search(r"never invent", d, re.I), "the forbidden move is not stated"
    assert "change-request" in d, "an underivable probe is not routed back to Direction"


def test_tier_ladder_stated_in_guide_and_book():
    for p in (VERIFY, DOC05):
        t = _text(p)
        for tier in ("T0", "T1", "T2", "T3", "T4"):
            assert re.search(rf"\b{tier}\b", t), f"{p.name}: tier {tier} missing"
        assert re.search(r"T4[^\n]*(recipe|not shipped|CI)", t), f"{p.name}: T4 does not admit it is a recipe"
        assert "floor" in t


def test_advisor_refute_mode_returns_the_verb_line():
    t = _text(ADVISOR)
    assert "add refute" in t and "--held" in t and "--found" in t, "the advisor does not return the verb line"


def test_advisor_twins_carry_the_same_text():
    canon = _text(ADVISOR)
    for twin in TWINS:
        if twin.exists():
            assert _text(twin) == canon, f"{twin} drifted from agents/add-advisor.md"
