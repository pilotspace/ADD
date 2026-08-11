"""The Explore lane: a research/spike request has a first-class lane on the existing Task
lifecycle — scoped questions + budget in, a compressed cited ## FINDINGS brief out, closed by a
sufficiency gate. No new node type, no new verb, no lowered floor.

Red-first for task `explore-lane` (milestone dynamic-flow). Every test here must fail while
phases/explore.md does not exist and intake.md / SKILL.md do not name the lane.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
EXPLORE = SKILL / "phases" / "explore.md"
sys.path.insert(0, str(REPO / "tooling"))

import argparse  # noqa: E402
import cli  # noqa: E402


def _cli_verbs():
    sub = [a for a in cli.build_parser()._actions if isinstance(a, argparse._SubParsersAction)][0]
    return set(sub.choices)


def _explore_text() -> str:
    assert EXPLORE.is_file(), "phases/explore.md does not exist yet"
    return EXPLORE.read_text(encoding="utf-8")


def test_explore_guide_exists_within_budget():
    """covers: M2 — the guide exists, fits the T3 budget, and names all four loop stages."""
    text = _explore_text()
    n = len(text.splitlines())
    assert n <= 350, f"explore.md is {n} lines (T3 budget 350)"
    for stage in ("budget", "reflect", "compress", "sufficiency"):
        assert re.search(stage, text, re.I), f"loop stage not named: {stage}"


def test_explore_guide_keeps_floors():
    """covers: R:FLOOR_DROP (probes A1) — the lane never lowers a floor."""
    text = _explore_text()
    assert re.search(r"security.*HARD-STOP|HARD-STOP.*security", text, re.I | re.S), \
        "security HARD-STOP not stated"
    assert re.search(r"freeze", text), "the freeze seam (questions + budget approval) not stated"


def test_explore_guide_names_stop_conditions():
    """covers: M2 (probes A5) — sufficiency judgment + hard budget backstop, both present."""
    text = _explore_text()
    assert re.search(r"sufficien", text, re.I), "sufficiency stop condition not named"
    assert re.search(r"budget.*(backstop|hard|cap|ceiling)|(backstop|hard|cap|ceiling).*budget",
                     text, re.I), "hard budget backstop not named"


def test_intake_names_explore_lane():
    """covers: M1 — intake.md carries the 4th lane with routing criteria and the human veto."""
    text = (SKILL / "intake.md").read_text(encoding="utf-8")
    assert re.search(r"^#+ .*Explore", text, re.M), "no Explore lane heading in intake.md"
    sect = text[re.search(r"^#+ .*Explore", text, re.M).start():]
    assert re.search(r"veto", sect, re.I), "the human veto not stated in the Explore lane entry"


def test_router_names_explore_within_budget():
    """covers: M3, R:BUDGET — SKILL.md names the lane and stays inside 150 lines."""
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert re.search(r"\bExplore\b", text), "SKILL.md does not name the Explore lane"
    n = len(text.splitlines())
    assert n <= 150, f"SKILL.md is {n} lines (budget 150) — fund the lane by compressing"


def test_explore_guide_uses_only_wired_verbs():
    """covers: R:PHANTOM_VERB — every `add <verb>` in explore.md is a real dispatch verb."""
    text = _explore_text()
    named = {m.group(1) for m in re.finditer(r"`?add\s+([a-z][a-z-]{1,22})\b", text)}
    unknown = named - _cli_verbs()
    assert not unknown, f"explore.md names verbs with no dispatch: {sorted(unknown)}"


def test_findings_fragment_contract_documented():
    """covers: M4 — downstream consumption via needs: …#findings is documented."""
    text = _explore_text()
    assert re.search(r"##\s*FINDINGS|## FINDINGS", text), "the ## FINDINGS section not documented"
    assert re.search(r"needs:.*#findings", text), \
        "the needs: /tasks/<slug>.md#findings consumption pattern not documented"
