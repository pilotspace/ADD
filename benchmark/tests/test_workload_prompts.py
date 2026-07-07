"""Scenario: identical prompts with regression bait (M1)."""
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENTRY_CONTRACT_SNIPPETS = ("python -m app", "$PORT")


def _read_prompt(wm: int) -> str:
    path = ROOT / "workload" / f"wm{wm}" / "PROMPT.md"
    if not path.exists():
        pytest.fail(f"missing {path}")
    return path.read_text()


def test_prompts_identical_contract_and_bait():
    texts = {wm: _read_prompt(wm) for wm in (1, 2, 3)}
    for wm, text in texts.items():
        for snippet in ENTRY_CONTRACT_SNIPPETS:
            assert snippet in text, f"wm{wm} PROMPT.md missing entry-contract snippet {snippet!r}"
    # WM3 must name a breaking change to a WM1-frozen shape (the regression bait).
    assert "wm1" in texts[3].lower() or "task/booking" in texts[3].lower() or "breaking" in texts[3].lower()
    assert "breaking" in texts[3].lower() or "refactor" in texts[3].lower()
