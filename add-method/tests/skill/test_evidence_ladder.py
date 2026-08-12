"""The documented evidence ladder must match the kinds the engine can actually stamp.

`verify.md` promised `test-ids > artifact-hash > command-exit > human-observed`. The engine writes
exactly `test-ids`, `command-exit` (add.py, the run receipt) and `sources` (the explore gate). So
the doc was wrong in BOTH directions: two rungs nothing could ever earn, and one real kind it never
named. An evidence kind that can never be earned is not a ladder, it is a label — the engine's own
comment says so about `test-ids` before e12 made it reachable.

The guard DERIVES the set from `add.py` rather than pinning literals. A pinned list would go stale
exactly the way the prose it replaces did: silently, and only visible to someone who went looking.
"""
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
ENGINE = REPO / "tooling" / "add.py"

# Both shapes ANCHOR on `kind` itself. An earlier version also matched any `"a" if x else "b"`
# ternary, which swept up freshness values (`content`/`mtime`) and unrelated statuses — a derived
# guard is only as honest as its anchor, and an over-broad one manufactures its own failures.
KIND_SITES = (
    re.compile(r'"kind":\s*([^,\n]+)'),   # dict form, incl. a ternary: "test-ids" if ids else ...
    re.compile(r'\bkind:\s*([a-z-]+)\s*,'),   # formatted stamp: ', kind: sources, ...'
)
QUOTED = re.compile(r'"([a-z-]+)"')


def engine_kinds(source: str) -> set:
    """Every evidence kind the given engine source can stamp. Raises on an empty extraction.

    E1: a kind stamped in a branch these patterns cannot see would silently shrink the set, and a
    guard that then passes because it compared against nothing is worse than no guard at all.
    """
    found = set()
    for m in KIND_SITES[0].finditer(source):
        found |= set(QUOTED.findall(m.group(1)))
    found |= set(KIND_SITES[1].findall(source))
    if not found:
        raise AssertionError("extracted no evidence kinds from the engine — the patterns have "
                             "drifted from how receipts are written; fix the extractor, do not "
                             "relax the check")
    return found


def _documented() -> set:
    """Every kind the skill names as an evidence rung, from the whole ladder PARAGRAPH.

    Reading one physical line was wrong: an honest ladder needs a sentence per kind to say what
    earns it, so the prose wraps, and a single-line read silently dropped every rung past the
    first. Shaping the doc back onto one line to suit the parser would have traded readable
    guidance for a lazy regex — the same trade this task exists to undo.
    """
    text = (SKILL / "phases" / "verify.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if "Evidence kinds" in ln), None)
    assert start is not None, "verify.md no longer states an evidence ladder"
    end = next((i for i in range(start, len(lines)) if not lines[i].strip()), len(lines))
    return set(re.findall(r"`([a-z-]+)`", "\n".join(lines[start:end])))


def test_documented_rungs_are_stampable():
    """M1 — no rung the engine cannot earn."""
    phantom = _documented() - engine_kinds(ENGINE.read_text(encoding="utf-8"))
    assert not phantom, (f"the skill documents evidence kinds the engine can never stamp: "
                         f"{sorted(phantom)} — an unearnable rung is a label, not a ladder")


def test_stampable_rungs_are_documented():
    """M2 — the orphan direction: a real kind no doc names."""
    missing = engine_kinds(ENGINE.read_text(encoding="utf-8")) - _documented()
    assert not missing, (f"the engine stamps kinds the skill never names: {sorted(missing)} — "
                         f"a reader cannot recognise a receipt kind nobody told them exists")


def test_rung_set_is_derived_not_pinned():
    """R:PINSTRINGS — prove the extractor reads the engine instead of carrying a literal list."""
    fabricated = 'receipt = {"kind": "totally-made-up-kind", "exit": 0}'
    assert "totally-made-up-kind" in engine_kinds(fabricated), \
        "the extractor did not pick up a fabricated kind — it is pinning literals, so it will go " \
        "stale the same way the prose did"


def test_extractor_fails_loud_on_empty():
    """E1 — an extraction that finds nothing must raise, never pass vacuously."""
    with pytest.raises(AssertionError, match="extracted no evidence kinds"):
        engine_kinds("def run():\n    return 0\n")
