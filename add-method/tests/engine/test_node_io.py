"""Red suite for e1 `port-okf-parse` — the engine's node I/O.

One test per Must / Reject of tasks/port-okf-parse, carrying the same `covers:` keys as
that task's CHECKS section. Every test must fail for the right reason before the engine
exists (red-first, FORMAT §8.3).

The subject is `add/scripts/add.py`, which does not exist yet: at red time every test in
this file fails at import.
"""

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402  — the subject; absent at red time


# --------------------------------------------------------------- parsing (M5, M4)


NODE = """---
type: Task
title: Reject overlapping bookings
goal: >-
  a second booking overlapping an existing one
  returns 409 OVERLAP
status: build
depth: standard
tags: []
scope:                          # the freshness set
  - src/bookings/**
  - src/shared/time.py
generated: { by: claude/opus-5, at: 2026-07-29 }
verified:
  - { by: "human:tindang", at: 2026-07-29, act: freeze, authority: human }
  - { by: "process:pytest", at: 2026-07-29, act: gate, authority: process, outcome: PASS }
---
## CARD
goal: reject overlaps
next: build

## RULES
- M1 overlapping bookings are refused
"""


def test_parse_scalars_and_lists():
    """covers: M5 — scalars, block lists and inline `[]` parse to exact values."""
    fm, _ = add.parse(NODE)
    assert fm["type"] == "Task"
    assert fm["title"] == "Reject overlapping bookings"
    assert fm["status"] == "build"
    assert fm["tags"] == []
    assert fm["scope"] == ["src/bookings/**", "src/shared/time.py"]


def test_parse_inline_map():
    """covers: M5 — an inline flow map is a dict, not a string."""
    fm, _ = add.parse(NODE)
    assert fm["generated"] == {"by": "claude/opus-5", "at": "2026-07-29"}


def test_parse_block_scalar():
    """covers: M5 — `>-` folds to one line, no trailing newline."""
    fm, _ = add.parse(NODE)
    assert fm["goal"] == "a second booking overlapping an existing one returns 409 OVERLAP"


def test_parse_list_of_maps():
    """covers: M5 — `verified:` entries are dicts carrying `act` and `authority`."""
    fm, _ = add.parse(NODE)
    assert [e["act"] for e in fm["verified"]] == ["freeze", "gate"]
    assert fm["verified"][0]["authority"] == "human"
    assert fm["verified"][1]["outcome"] == "PASS"


def test_parse_no_frontmatter_returns_none():
    """covers: M4, R:RAISE — a bare markdown file is not an error, it is a report."""
    text = "# just a heading\n\nsome prose\n"
    fm, body = add.parse(text)
    assert fm is None
    assert body == text


def test_parse_malformed_does_not_raise():
    """covers: M4, R:RAISE — an unterminated frontmatter block returns, never raises."""
    fm, body = add.parse("---\ntype: Task\ntitle: no closing fence\n")
    assert fm is None
    assert "no closing fence" in body


# --------------------------------------------------------------- read tiers (M1)


@pytest.fixture
def node(tmp_path):
    p = tmp_path / "overlap-reject.md"
    p.write_text(NODE)
    return p


def test_read_t0_has_no_body(node):
    """covers: M1, R:TIERLEAK — T0 is frontmatter, and nothing else crosses the boundary."""
    n = add.read(node, "T0")
    assert n["fm"]["type"] == "Task"
    assert n["card"] == ""
    assert n["body"] == ""


def test_read_t1_is_card_only(node):
    """covers: M1, R:TIERLEAK — T1 stops at the end of `## CARD`."""
    n = add.read(node, "T1")
    assert "goal: reject overlaps" in n["card"]
    assert "RULES" not in n["card"], "T1 leaked the section after CARD"
    assert n["body"] == ""


def test_read_t2_is_whole_node(node):
    """covers: M1 — T2 is the whole body, CARD included."""
    n = add.read(node, "T2")
    assert "## RULES" in n["body"]
    assert "M1 overlapping bookings are refused" in n["body"]


# --------------------------------------------------- surgical writes (M3, R:REGEN)


def test_set_key_preserves_comments(node):
    """covers: M3, R:REGEN — changing one key leaves every other byte alone."""
    before = node.read_text()
    n = add.read(node, "T0")
    raw = add.set_key(n["raw"], "status", "verify")
    assert "status: verify" in raw
    assert "# the freshness set" in raw, "a trailing comment was lost"
    for line in before.split("---")[1].splitlines():
        if "status:" not in line:
            assert line in raw, f"line changed or dropped: {line!r}"


def test_set_key_preserves_order(node):
    """covers: M3 — key order is a property of the file, not of a dict."""
    n = add.read(node, "T0")
    raw = add.set_key(n["raw"], "status", "verify")
    keys = [ln.split(":")[0] for ln in raw.splitlines() if ln and not ln[0].isspace()]
    assert keys[:5] == ["type", "title", "goal", "status", "depth"]


def test_append_item_keeps_indent(node):
    """covers: M3 — an appended item matches the block's existing indentation."""
    n = add.read(node, "T0")
    raw = add.append_item(n["raw"], "scope", "src/api/routes.py")
    assert "  - src/api/routes.py" in raw
    fm, _ = add.parse(f"---\n{raw}\n---\n")
    assert fm["scope"][-1] == "src/api/routes.py"
    assert len(fm["scope"]) == 3


# ------------------------------------------------------ atomic write (M2, R:PARTIAL)


def test_write_is_atomic(node, monkeypatch):
    """covers: M2, R:PARTIAL — a failed write leaves the original whole and no debris."""
    original = node.read_text()

    def boom(src, dst):
        raise OSError("simulated failure at the moment of replace")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        add.write(node, "REPLACED\n")

    assert node.read_text() == original, "the original was damaged by a failed write"
    leftovers = [p for p in node.parent.iterdir() if p != node]
    assert leftovers == [], f"temp debris survived: {leftovers}"


def test_write_temp_is_same_directory(node):
    """covers: M2 — os.replace is only atomic within one filesystem."""
    seen = []
    real = os.replace

    def spy(src, dst):
        seen.append((Path(src).parent, Path(dst).parent))
        return real(src, dst)

    original_replace = os.replace
    os.replace = spy
    try:
        add.write(node, "REPLACED\n")
    finally:
        os.replace = original_replace

    assert seen and seen[0][0] == seen[0][1], "temp file was not in the target's directory"
    assert node.read_text() == "REPLACED\n"


# ----------------------------------------------- the regression floor (M3, R:REGEN)


@pytest.mark.skip(reason="dogfood: asserts add-skill's own dev-bundle (>=20 nodes); re-point when add-skill-2 grows its own bundle")
def test_roundtrip_bundle_byte_identical():
    """covers: M3, R:REGEN — read and rewrite every live node with no change: zero diff.

    This is the floor for all of M1. The engine may not quietly reformat the bundle it
    was built to maintain.
    """
    bundle = REPO / ".add"
    checked = 0
    for path in sorted(bundle.rglob("*.md")):
        original = path.read_text()
        n = add.read(path, "T2")
        if n["fm"] is None:
            continue
        rebuilt = f"---\n{n['raw']}\n---\n{n['body']}"
        assert rebuilt == original, f"round-trip changed {path.relative_to(bundle)}"
        checked += 1
    assert checked >= 20, f"expected the whole bundle, only saw {checked} nodes"


class TestBareApostropheDoesNotOpenAQuote:
    """A live authoring pass wrote `- S2 GET /transfers — the caller's own transfer
    history` into `gives:` and every key BELOW it vanished from the parse — including
    `verified:`, so `sealed_direction` returned None and the freeze seal silently
    stopped verifying. `_open_quote` treated the mid-word apostrophe as an opener;
    in YAML a quote opens a string only at a token boundary, and `caller's` is plain
    content. The docstring on `_open_quote` records this bug's own PRIOR incarnation
    (count → state); this is the second: state that opens mid-word. direction.md's own
    example teaches exactly this shape (`the caller's own sessions`)."""

    RAW = ("---\n"
           "type: Task\n"
           "title: t\n"
           "gives:\n"
           "  - S1 POST /transfers — move an amount\n"
           "  - S2 GET /transfers — the caller's own transfer history\n"
           "generated: { by: add/3.0.0, at: 2026-08-11 }\n"
           "verified:\n"
           '  - { by: "tin", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:aa" }\n'
           "---\nbody")

    def test_keys_after_an_apostrophe_item_survive(self):
        fm, _ = add.parse(self.RAW)
        assert set(fm) >= {"gives", "generated", "verified"}, sorted(fm)
        assert add.sealed_direction(fm) == "sha256:aa"

    def test_the_apostrophe_item_itself_is_intact(self):
        fm, _ = add.parse(self.RAW)
        assert fm["gives"][1] == "S2 GET /transfers — the caller's own transfer history"

    def test_a_genuinely_quoted_wrapped_item_still_continues(self):
        # The case the quote-arm exists for: a quoted value wrapped across lines
        # (its braces balance inside the quote, so the brace arm cannot rescue it).
        raw = ('---\nxs:\n  - "a wrapped }\n    value"\nafter: 1\n---\nbody')
        fm, _ = add.parse(raw)
        assert fm["xs"] == ["a wrapped } value"]
        assert str(fm["after"]) == "1"

    def test_an_apostrophe_inside_double_quotes_still_closes(self):
        # The PRIOR bug's fixture — must stay green.
        raw = ('---\nxs:\n  - "the node\'s own body"\nafter: 1\n---\nbody')
        fm, _ = add.parse(raw)
        assert fm["xs"] == ["the node's own body"]
        assert str(fm["after"]) == "1"
