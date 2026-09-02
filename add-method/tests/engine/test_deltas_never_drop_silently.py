"""A delta the engine cannot parse is REPORTED, never dropped from the inventory.

`deltas` is "the carried inventory the loop reads to propose the next tasks" (add.py) and the
front door's whole Judgment faculty. A line whose status is typo'd matches nothing in
`DELTA_LINE`'s status group, so it vanished — no warning, no `doctor` finding, no exit code:

    - [TDD · opne] the lesson someone actually wrote        <- gone from `add deltas` entirely

Meanwhile `deltas.md` documents three reject codes for exactly this — `unknown_competency`,
`no_evidence`, `unknown_status` — and `grep -c` for all three in the engine returns 0. The
author has a documented promise that a malformed delta cannot pass silently, and it can.

Two halves, and the second is the one that matters: reporting a malformed line is worth little
if the CODES the docs promise still name nothing. A guard over the prose enumerates them.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DELTAS_MD = REPO / "skill" / "add" / "deltas.md"


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _append(root, lens, *lines):
    p = root / "specs" / f"{lens}.md"
    p.write_text(p.read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(lines) + "\n",
                 encoding="utf-8")


# ------------------------------------------------- M1 · nothing disappears

def test_a_malformed_status_is_reported_not_dropped(tmp_path):
    """covers: M1, R:SILENTDROP — the loop must not read a silently truncated inventory."""
    root = _bundle(tmp_path)
    _append(root, "domain",
            "- [TDD · open] a well formed one (evidence: abc1234)",
            "- [TDD · opne] a typo'd status nobody will ever see again (evidence: abc1234)")

    items, note = add.deltas(root)
    assert any("well formed" in t for _, _, t in items), note
    assert "opne" in note or "typo'd status" in note, (
        f"a delta line vanished from the inventory with no warning:\n{note}")


def test_an_unknown_competency_is_reported(tmp_path):
    """covers: M2 — `unknown_competency` is a documented code; it must name something."""
    root = _bundle(tmp_path)
    _append(root, "domain", "- [XYZ · open] a bogus competency tag (evidence: abc1234)")
    _, note = add.deltas(root)
    assert "XYZ" in note, f"an unknown competency passed silently:\n{note}"


def test_a_well_formed_inventory_stays_quiet(tmp_path):
    """covers: M3 — the report is for malformed lines only, not noise on every read."""
    root = _bundle(tmp_path)
    _append(root, "domain", "- [TDD · open] a perfectly good lesson (evidence: abc1234)")
    _, note = add.deltas(root)
    assert "malformed" not in note.lower(), f"a clean inventory reported a problem:\n{note}"


def test_an_unknown_status_query_is_refused(tmp_path):
    """covers: M4, E1 — `--status bogus` read as an empty result, not as a bad question."""
    root = _bundle(tmp_path)
    _append(root, "domain", "- [TDD · open] a lesson (evidence: abc1234)")
    items, note = add.deltas(root, status="bogus")
    assert not items
    assert "bogus" in note and ("open" in note and "folded" in note), (
        f"an unknown status reads as 'no results' rather than a refusal naming the set:\n{note}")


# ------------------------------------------------- M5 · the documented codes exist

def test_every_reject_code_deltas_md_documents_is_real():
    """covers: M5, R:PHANTOMCODE — enumerated from the doc, so a new promise cannot skip it."""
    prose = DELTAS_MD.read_text(encoding="utf-8")
    block = re.search(r"<reject_codes>(.*?)</reject_codes>", prose, re.S)
    assert block, "deltas.md no longer declares <reject_codes> — this guard is stale"
    codes = re.findall(r"^-\s*`([a-z_]+)`", block.group(1), re.M)
    assert codes, "the reject_codes block names no codes"
    engine = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    missing = [c for c in codes if c not in engine]
    assert not missing, (
        f"deltas.md promises reject codes the engine does not have: {missing}")
