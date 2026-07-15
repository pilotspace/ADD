"""Scenario: identical prompts with regression bait (M1)."""
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENTRY_CONTRACT_SNIPPETS = ("python -m app", "$PORT")


def _read_prompt(wm: int, family: str = "wm") -> str:
    path = ROOT / "workload" / f"{family}{wm}" / "PROMPT.md"
    if not path.exists():
        pytest.fail(f"missing {path}")
    return path.read_text()


def test_prompts_identical_contract_and_bait():
    texts = {wm: _read_prompt(wm) for wm in (1, 2, 3)}
    for wm, text in texts.items():
        for snippet in ENTRY_CONTRACT_SNIPPETS:
            assert snippet in text, f"wm{wm} PROMPT.md missing entry-contract snippet {snippet!r}"
    # WM3 must name the concrete regression bait `test_refactor.py` actually oracles:
    # the `duration_minutes` -> `end_time` field removal (M10 tightening, not a
    # loose keyword or-chain over "wm1"/"task/booking"/"breaking").
    wm3_lower = texts[3].lower()
    assert "duration_minutes" in wm3_lower, "wm3 PROMPT.md must name the removed duration_minutes field"
    assert "end_time" in wm3_lower, "wm3 PROMPT.md must name the replacement end_time field"


def test_hv_prompts_carry_the_entry_contract():
    # the hv hard cross-domain track shares the fixed `python -m app` on $PORT
    # entry contract, so oracle boot resolution is identical to the wm track.
    for wm in (1, 2):
        text = _read_prompt(wm, family="hv")
        for snippet in ENTRY_CONTRACT_SNIPPETS:
            assert snippet in text, f"hv{wm} PROMPT.md missing entry-contract snippet {snippet!r}"
