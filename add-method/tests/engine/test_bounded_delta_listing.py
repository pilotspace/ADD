"""The carried inventory is windowed the way `search` already windows it.

Red-first for `/tasks/bounded-delta-listing.md`.

Measured on the live bundle before this task: `deltas` emitted 27,374 bytes, and 51 of its 66
lines exceeded the 300-character bound `search` is HELD TO BY TEST (`test_search_verb.py`), the
longest at 830. The two verbs render the same records at 409 and 169 bytes each — `search`
windows at `SEARCH_SNIPPET`, `deltas` windowed at nothing.

Safe only because `address-dereferences` landed first: one lesson is now a 608-byte read, so a
truncated row has a cheap way back to the full text. Windowing before that would have stranded
delta prose behind a 13 KB whole-spec read.
"""

import inspect
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

LIVE = REPO.parent / ".add"
BOUND = 300      # the bound `search` is tested against, stated by value here too
LONG = ("- [ADD · Y1 · open · 2026-09-04] " + "an overlong lesson body " * 40
        + "(evidence: /tasks/t-one.md)")
SHORT = "- [ADD · Y2 · open · 2026-09-04] a short lesson (evidence: /tasks/t-one.md)"
BROKEN = "- [ADD · Y3 · opne · 2026-09-04] " + "a malformed line " * 30 + "(evidence: /x.md)"


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / ".add"
    add.init(root, profile="code", title="window fixture")
    add.new(root, "Task", "t-one", title="a task")
    spec = root / "specs" / "method.md"
    spec.write_text(spec.read_text(encoding="utf-8").rstrip()
                    + f"\n\n{LONG}\n{SHORT}\n{BROKEN}\n", encoding="utf-8")
    return root


def _rows(note):
    return [ln for ln in note.splitlines() if ln.strip().startswith("·")]


def test_no_emitted_line_exceeds_the_bound():
    """M1, E1 — the live bundle's longest `deltas` line was 830 characters."""
    note = add.deltas(LIVE, status="open")[1]
    over = [ln for ln in note.splitlines() if len(ln) > BOUND]
    assert not over, (f"{len(over)} line(s) exceed {BOUND}; longest is "
                      f"{max(len(l) for l in over)}: {over[0][:120]!r}")


def test_the_address_survives_truncation(bundle):
    """M2, R:LOSTADDRESS, E3 — the address is the way back to the full text."""
    row = next(r for r in _rows(add.deltas(bundle, status="open")[1]) if "#Y1" in r)
    assert "/specs/method.md#Y1" in row, f"the address was damaged by the cut: {row!r}"


def test_the_window_is_the_search_constant():
    """M3, R:SECONDWINDOW — one constant, or the two verbs drift apart again."""
    src = inspect.getsource(add.deltas)
    assert "SEARCH_SNIPPET" in src or "_snippet(" in src, \
        "`deltas` does not window through the path `search` uses"


def test_a_truncated_row_says_so(bundle):
    """M4, R:SILENTCUT, A10 — a planner must not quote a fragment as the whole lesson."""
    row = next(r for r in _rows(add.deltas(bundle, status="open")[1]) if "#Y1" in r)
    assert "…" in row or "..." in row, f"a cut row looks complete: {row!r}"


def test_a_short_lesson_is_unchanged(bundle):
    """E2, A4 — a lesson under the window keeps its whole text."""
    row = next(r for r in _rows(add.deltas(bundle, status="open")[1]) if "#Y2" in r)
    assert "a short lesson" in row, f"a short lesson lost text: {row!r}"
    assert "…" not in row, f"a short lesson was marked truncated: {row!r}"


def test_the_malformed_report_is_untouched(bundle):
    """M5, E4 — it names a raw LINE; cutting evidence of a break would hide the break."""
    note = add.deltas(bundle, status="open")[1]
    report = [ln for ln in note.splitlines() if ln.strip().startswith("!")]
    assert any("opne" in ln for ln in report), f"the malformed line is not reported:\n{note}"
    assert any(len(ln) > BOUND for ln in report), \
        "the malformed report was windowed too — it must show the raw line whole"


def test_row_order_is_unchanged(bundle):
    """A8 — this windows how a row renders, never which rows there are."""
    items, note = add.deltas(bundle, status="open")
    rows = _rows(note)
    assert len(items) >= 2, f"too few items to observe an order: {items}"
    assert len(rows) == len(items), f"{len(items)} items rendered as {len(rows)} rows"


def test_the_saving_is_recorded():
    """M6, A3, A7, A11 — measured on the live bundle, written down, and smaller.

    The record is the MILESTONE's exit evidence, not a scratch file. This check first read
    `tmp/read-cost/measured.txt`, which `.gitignore` excludes: it passed on the machine that
    produced the number and failed on a fresh checkout, which is the same as not recording it.
    A measurement that does not survive `git clone` was never written down.
    """
    exit_block = (REPO.parent / ".add" / "milestones" / "read-cost.md").read_text(encoding="utf-8")
    # TWO byte figures on one line — that is what a before/after IS. Other evidence lines quote a
    # single measurement ("604 B", "830 B"), so a one-figure line is not the record being asked for.
    sized = [(l, re.findall(r"([\d,]+) B", l)) for l in exit_block.splitlines()]
    line, figures = next(((l, f) for l, f in sized if len(f) >= 2 and "->" in l), (None, None))
    assert line, "the milestone records no before/after intake measurement"
    before, after = (int(n.replace(",", "")) for n in figures[:2])
    assert after < before, f"the intake session did not shrink: {before} -> {after}"
