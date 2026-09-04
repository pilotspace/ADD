"""One concept, one citable address — whichever door a reader came through.

Red-first for `/tasks/one-address-per-concept.md`, which folds X4.

`add search` has always rendered a lesson at `/specs/<lens>.md#<id>` — the concept address a
`relations:` entry can name. `add deltas` rendered the SAME lesson as `[TDD Q14] quality: ...`:
the id is visible, but not as anything a reader can paste. A reader who found a lesson through
the wrong door had to reconstruct the path by hand.

The fix is not two matching renderers — that is how they drifted apart in the first place. It is
ONE builder, `delta_address`, that both readers call (R:DRIFT).
"""

import inspect
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

DATED = ("- [ADD \u00b7 X9 \u00b7 open \u00b7 2026-09-04] a dated lesson with a citable identity"
         " (evidence: /tasks/t-one.md)")
LEGACY = "- [ADD \u00b7 open] a legacy lesson carrying no id at all (evidence: /tasks/t-one.md)"
BROKEN = ("- [ADD \u00b7 X9 \u00b7 opne \u00b7 2026-09-04] a lesson whose status is a typo"
          " (evidence: /tasks/t-one.md)")


@pytest.fixture
def bundle(tmp_path):
    """A method spec carrying a dated delta, a legacy delta, and a malformed one."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="address fixture")
    add.new(root, "Task", "t-one", title="a task to point evidence at")
    spec = root / "specs" / "method.md"
    spec.write_text(spec.read_text(encoding="utf-8").rstrip()
                    + f"\n\n{DATED}\n{LEGACY}\n{BROKEN}\n", encoding="utf-8")
    return root


def _addresses(note: str) -> list:
    """Every `/specs/<lens>.md[#<id>]` token the render emitted, in order."""
    return re.findall(r"/specs/[a-z]+\.md(?:#[A-Za-z0-9]+)?", note)


def test_both_readers_emit_one_address(bundle):
    """M1, M2, A2, R:DRIFT, E1 — one lesson, two verbs, the identical address string."""
    d_note = add.deltas(bundle, status="open")[1]
    s_note = add.search(bundle, "citable identity")[1]
    want = "/specs/method.md#X9"
    d_hit = [a for a in _addresses(d_note) if a.endswith("#X9")]
    s_hit = [a for a in _addresses(s_note) if a.endswith("#X9")]
    assert d_hit, f"`add deltas` emitted no address for the dated lesson:\n{d_note}"
    assert s_hit, f"`add search` emitted no address for the dated lesson:\n{s_note}"
    assert d_hit[0] == s_hit[0] == want, \
        f"the two doors disagree: deltas={d_hit[0]!r} search={s_hit[0]!r} want={want!r}"


def test_address_has_one_builder():
    """M2, A9 — the form is built in ONE place, and both readers call it."""
    assert hasattr(add, "delta_address"), \
        "no `delta_address` — each reader still composes the address itself (R:DRIFT)"
    assert add.delta_address("quality", "Q14") == "/specs/quality.md#Q14"
    for verb in ("deltas", "search"):
        src = inspect.getsource(getattr(add, verb))
        assert "delta_address(" in src, \
            f"`{verb}` does not call `delta_address` — a second copy is how X4 happened"
        assert not re.search(r'f"/specs/\{', src), \
            f"`{verb}` still composes a /specs/ address inline beside the shared builder"


def test_legacy_head_degrades_alike(bundle):
    """M3, E2, A4 — an id-less head renders the BARE file address in both readers."""
    assert add.delta_address("method", None) == "/specs/method.md"
    d_note = add.deltas(bundle, status="open")[1]
    s_note = add.search(bundle, "carrying no id")[1]
    for door, note in (("deltas", d_note), ("search", s_note)):
        # not the header: `search` echoes the query in `N hit for "<q>":`, which is not a row.
        row = next((ln for ln in note.splitlines()
                    if "carrying no id" in ln and not ln[:1].isdigit()), None)
        assert row, f"`add {door}` did not render the legacy lesson:\n{note}"
        assert "/specs/method.md" in row, f"`add {door}` gave the legacy lesson no address: {row}"
        assert "#" not in row, f"`add {door}` invented a fragment for an id-less head: {row}"


def test_lesson_text_is_not_traded_for_the_address(bundle):
    """R:LOSTID, E4 — the address is ADDED; the lesson text survives in full."""
    note = add.deltas(bundle, status="open")[1]
    assert "a dated lesson with a citable identity" in note
    assert "a legacy lesson carrying no id at all" in note


def test_malformed_report_is_unchanged(bundle):
    """E3 — the malformed section names a raw LINE, not a concept, so it keeps its shape."""
    note = add.deltas(bundle, status="open")[1]
    report = [ln for ln in note.splitlines() if ln.strip().startswith("!")]
    assert any("opne" in ln for ln in report), f"the malformed line was not reported:\n{note}"
    assert any("unknown_status" in ln for ln in report), f"the code was not named:\n{note}"


def test_row_order_is_unchanged(bundle):
    """A7 — this task changes how a row RENDERS, never which rows there are or in what order."""
    items, note = add.deltas(bundle, status="open")
    assert len(items) == 2, f"the fixture carries no inventory to order: {items}"
    rows = [ln for ln in note.splitlines() if ln.strip().startswith("·")]
    assert len(rows) == len(items), f"{len(items)} carried items rendered as {len(rows)} rows"
    for row, item in zip(rows, items):
        assert item[2] in row, f"row/item order diverged: {row!r} is not {item[2]!r}"


def test_x4_is_folded_only_when_both_agree():
    """M4, R:HALFFOLD — the delta is folded, and it is folded because the doors now agree."""
    text = (REPO.parent / ".add" / "specs" / "experience.md").read_text(encoding="utf-8")
    x4 = [ln for ln in text.splitlines()
          if re.match(r"- \[UDD · X4 · ", ln.strip())]
    assert x4, "X4 is gone from experience.md — folded means status-folded, never deleted"
    assert "· folded ·" in x4[0], f"X4 is still carried: {x4[0]}"
    # R:HALFFOLD — folded because the doors agree, not merely because someone ran `fold`.
    for verb in ("deltas", "search"):
        assert "delta_address(" in inspect.getsource(getattr(add, verb)), \
            f"X4 is folded while `{verb}` still builds its own address (R:HALFFOLD)"
