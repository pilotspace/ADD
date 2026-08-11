"""Planning is persona-carried (task persona-carried-planning).

The best-fit advisor-flow lens loads BEFORE a milestone proposal or next-task proposal is
drafted — through the EXISTING flow vocabulary, opt-in by fit, additive as ever — and the
live bundle carries a seeded starter roster for anything to load at all.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
BUNDLE_PERSONAS = REPO.parent / ".add" / "personas"

FLOW_VOCAB = "design · build · advisor · verify"


def _read(name: str) -> str:
    return (SKILL / name).read_text(encoding="utf-8")


def test_intake_milestone_lane_loads_lens():
    """covers: M1, A5 — lens load before drafting + the advise record, in the milestone lane."""
    text = _read("intake.md")
    m = re.search(r"^#+ .*Project / milestone.*$", text, re.M)
    assert m, "the Project/milestone lane heading moved"
    sect = text[m.start():]
    assert re.search(r"advisor", sect, re.I), "the advisor-flow lens is not named in the lane"
    assert re.search(r"before (the )?draft", sect, re.I), "load-before-drafting is not stated"
    assert re.search(r"advise", sect), "recording the lens via advise is not stated"


def test_loop_propose_loads_lens():
    """covers: M2 — the Propose step loads the same lens."""
    text = _read("loop.md")
    assert re.search(r"Propose[^#]*persona", text, re.S | re.I), \
        "the Propose step does not load a persona lens"


def test_personas_documents_planning_surface():
    """covers: M3, R:VOCAB_CREEP, A3, A11 — the reading exists; the vocabulary did not grow."""
    text = _read("personas.md")
    for surface in ("intake proposal", "milestone draft", "next-task proposal"):
        assert re.search(surface.replace(" ", r"[\s-]"), text, re.I), \
            f"planning surface not named: {surface}"
    assert FLOW_VOCAB in text, "the flow vocabulary line moved — planning must ride advisor as-is"
    assert not re.search(r"flow:.*\bplan\b", text), "a new flow word crept in"


def test_additivity_promise_survives():
    """covers: R:MANDATORY_LENS, A7, E1 — opt-in/additive verbatim; no-roster skips silently."""
    personas = _read("personas.md")
    assert "opt-in and additive" in personas, "the additivity promise was reworded"
    assert re.search(r"behaves exactly as before", personas), "the no-persona guarantee was lost"
    intake = _read("intake.md")
    assert re.search(r"no persona[s]? (is |are )?seeded|no roster", intake, re.I), \
        "the milestone lane must say a roster-less bundle skips the load silently"


def test_seeded_personas_exist_with_routing():
    """covers: M4, E2 — both personas seeded, routed, four parts present, no invented stat."""
    for slug in ("method-steward", "engine-notary"):
        p = BUNDLE_PERSONAS / f"{slug}.md"
        assert p.is_file(), f"persona not seeded: {slug}"
        text = p.read_text(encoding="utf-8")
        assert re.search(r"^flow:", text, re.M), f"{slug}: no flow: routing"
        assert re.search(r"^use-when:", text, re.M), f"{slug}: no use-when: routing"
        for part in ("Identity", "Critical Rules", "Default Requirement", "Success Metrics"):
            assert part in text, f"{slug}: missing part {part}"
        assert not re.search(r"\+\d+%", text), f"{slug}: invented percentage statistic"


def test_skill_budgets_hold():
    """covers: R:BUDGET — every edited file inside the 350-line budget."""
    for name in ("intake.md", "loop.md", "personas.md"):
        n = len(_read(name).splitlines())
        assert n <= 350, f"{name} is {n} lines (budget 350)"
