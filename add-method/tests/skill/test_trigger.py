"""A lightweight trigger sanity check for the router description.

We cannot run the model's skill-selection here, so this asserts the structural signal the
selector reads: the description must carry the cues ADD triggers on, and a small labelled set of
in-scope prompts must share those cues while out-of-scope prompts do not. This is a smoke test for
"the description points at the right work", not a precision/recall claim.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"

# cues the router leans on for discovery + first-contact
CUES = ("add", ".add", "task", "verify", "spec", "resume", "ai-driven")

IN_SCOPE = [
    "use the add method to build this feature",
    "/add start a task for the login endpoint",
    "specify this feature with tests first",
    "resume the ADD task in this .add repo",
    "next phase — verify the payment change",
]
OUT_OF_SCOPE = [
    "what's the capital of France",
    "reformat this paragraph to be friendlier",
    "explain how a hash map works",
]


def _description() -> str:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    fm = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL).group(1)
    m = re.search(r"description:\s*>-?\n(.*?)(?=^\w[\w-]*:)", fm + "\nkeywords:", re.DOTALL | re.M)
    return (m.group(1) if m else "").lower()


def test_description_carries_trigger_cues():
    desc = _description()
    missing = [c for c in CUES if c not in desc]
    assert not missing, f"description is missing trigger cues: {missing}"


def test_in_scope_prompts_share_cues_and_out_do_not():
    cues = set(CUES)

    def hits(prompt: str) -> int:
        p = prompt.lower()
        return sum(1 for c in cues if c in p)

    assert all(hits(p) >= 1 for p in IN_SCOPE), \
        [p for p in IN_SCOPE if hits(p) == 0]
    assert all(hits(p) == 0 for p in OUT_OF_SCOPE), \
        [p for p in OUT_OF_SCOPE if hits(p) > 0]
