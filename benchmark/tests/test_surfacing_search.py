"""Two search defects the amb1 miss-partition exposed — and what fixing them cannot do.

Partitioning all 21 post-intervention item-runs by failure stage (2026-08-11) found the
scorer losing recognitions that exist, verbatim and pre-edit, in the prose:

1. THE FIRST-MATCH RACE. `_find_surfacing` returned the FIRST marker+anchor pair and
   `classify` then vetoed it if attribution assigned it to a sibling — it never continued
   searching for an attributable one. ADD's opening assumption line is long and cites
   waitlist, 409, promotion, priority and position together, so it wins the race for
   several items and is then vetoed for most of them, while a clean dedicated sentence
   sits further down the same document. rep1 and rep2 each lose `A-priority-vs-fifo`
   exactly this way.

2. THE SPLITTER GLUE. `_SENT_SPLIT` breaks at whitespace PRECEDED by `[.!?;\n]` — so a
   markdown list item that ends without punctuation (`-> <cost if wrong>`) never
   terminates a sentence, and an entire `## ASSUMPTIONS` block fuses into one
   mega-sentence. A per-line document format is scored as a single run-on.

THE HAZARD, SAME AS THE MARKER WIDENING: both changes were designed after seeing which
way they move the number. Three things keep them on the right side, asserted here rather
than argued:

  * The baselines DO NOT MOVE. Re-scored across the archived runs, vanilla stays 1/7 and
    pre-ASSUMPTIONS add stays 1/7 under both fixes — there is no attributable sentence
    for a deeper search to find in a run that never wrote one.
  * A recognition that exists nowhere still scores nothing: continuing the search past a
    veto finds only sentences that were always in the prose. The tie rule is untouched —
    an unattributable sentence still credits nobody, however many times it is scanned.
  * Measured before merging: the race fix recovers exactly 2 of 16 misses and the
    splitter fix recovers 0 on every archived run (the glued block's pairs are
    unattributable even once split). The commit claims mechanism correctness for the
    splitter, not a number.
"""
from __future__ import annotations

import collections
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.ambiguity import _SENT_SPLIT, classify
from benchmark.score import compute_ambiguity_detail

B = pathlib.Path(__file__).resolve().parents[1]

_ITEMS = [
    {"id": "A-conflict", "klass": "contradiction", "anchors": ("waitlist", "409", "202"),
     "readings": {"a": lambda *_: True, "b": lambda *_: False}, "defensible": "a"},
    {"id": "A-priority", "klass": "gap", "anchors": ("priority", "fifo"),
     "readings": {"a": lambda *_: True, "b": lambda *_: False}, "defensible": "a"},
]


class TestSearchContinuesPastAVeto:
    def test_a_later_attributable_sentence_surfaces(self):
        # The live rep1/rep2 shape: the dense opener pairs marker+anchor for BOTH items
        # and attributes to the contradiction; the dedicated sentence comes later.
        tx = ("The spec never says how to reconcile the waitlist, the 409, and the "
              "priority field together. "
              "Separately: the spec does not say whether priority beats fifo ordering. ")
        v = classify(item=_ITEMS[1], transcript=tx, artifacts=(), shipped="a",
                     edit_pos=10**6, siblings=_ITEMS)
        assert v["verdict"] == "surfaced", v
        assert "fifo" in v["evidence"].lower(), v["evidence"]

    def test_the_veto_itself_is_not_weakened(self):
        # Only the dense opener exists: the sibling keeps the credit, this item
        # scores nothing. Continuing the search must find nothing to continue TO.
        tx = ("The spec never says how to reconcile the waitlist, the 409, and the "
              "priority field together. ")
        v = classify(item=_ITEMS[1], transcript=tx, artifacts=(), shipped="a",
                     edit_pos=10**6, siblings=_ITEMS)
        assert v["verdict"] != "surfaced", "a vetoed pair with no successor still scored"

    def test_a_tie_sentence_is_skipped_not_credited(self):
        # A tie credits nobody (existing rule) — but it must also not TERMINATE the
        # search, or the race just moves one veto over.
        tied = [{"id": "X", "klass": "gap", "anchors": ("alpha",),
                 "readings": {"a": lambda *_: True, "b": lambda *_: False},
                 "defensible": "a"},
                {"id": "Y", "klass": "gap", "anchors": ("beta",),
                 "readings": {"a": lambda *_: True, "b": lambda *_: False},
                 "defensible": "a"}]
        tx = ("the spec does not say anything about alpha and beta together. "
              "the spec also does not say what alpha alone should default to. ")
        v = classify(item=tied[0], transcript=tx, artifacts=(), shipped="a",
                     edit_pos=10**6, siblings=tied)
        assert v["verdict"] == "surfaced", v
        assert "alone" in v["evidence"], v["evidence"]

    def test_the_window_still_closes_at_the_first_code_edit(self):
        # Continuing the search must not continue past edit_pos: a post-edit
        # attributable sentence is still post-hoc rationalisation.
        tx = ("The spec never says how to reconcile the waitlist, the 409, and the "
              "priority field together. "
              "Separately: the spec does not say whether priority beats fifo ordering. ")
        v = classify(item=_ITEMS[1], transcript=tx, artifacts=(), shipped="a",
                     edit_pos=len(tx) // 2, siblings=_ITEMS)
        assert v["verdict"] != "surfaced", "surfacing credited after the window closed"


class TestListItemsAreSentenceBoundaries:
    def test_unpunctuated_bullets_split(self):
        # The live ASSUMPTIONS shape: lines end in `>` — no [.!?;] before the newline.
        block = ("- A1 [who] covers: S1 · identity left open -> <cost if wrong>\n"
                 "- A2 [which] covers: S1 · inclusion left open -> <cost if wrong>\n"
                 "- A3 [when] covers: S1 · boundaries left open -> <cost if wrong>")
        assert len(_SENT_SPLIT.split(block)) >= 3, _SENT_SPLIT.split(block)

    def test_a_heading_starts_a_new_sentence(self):
        glued = "beat: direction -> next\n## ASSUMPTIONS\n- A1 the spec does not say"
        parts = _SENT_SPLIT.split(glued)
        assert len(parts) >= 3, parts

    def test_two_bullets_no_longer_share_one_sentence(self):
        # End to end: marker in bullet 1, anchor in bullet 2 — MUST NOT pair.
        tx = ("- the spec does not say what happens on submit\n"
              "- the priority field orders the queue")
        v = classify(item=_ITEMS[1], transcript=tx, artifacts=(), shipped="b",
                     edit_pos=10**6, siblings=_ITEMS)
        assert v["verdict"] != "surfaced", "marker and anchor paired across two bullets"

    def test_prose_wrapping_is_not_split(self):
        # A wrapped paragraph (newline mid-sentence, next line starts with a word)
        # is ONE sentence — only list markers and headings are boundaries.
        wrapped = "the spec does not say whether\npriority beats fifo ordering"
        v = classify(item=_ITEMS[1], transcript=wrapped, artifacts=(), shipped="a",
                     edit_pos=10**6, siblings=[_ITEMS[1]])
        assert v["verdict"] == "surfaced", "a wrapped sentence stopped pairing"


class TestBaselinesDoNotMove:
    """The fairness floor: a deeper search cannot lift a run that never wrote the
    sentence. Frozen against the archived runs (skipped where the gitignored runs
    directories are absent)."""

    CASES = [
        ("runs-amb1/vanilla/amb1", 1),   # vanilla baseline
        ("runs-amb1/add/amb1", 1),       # add before ## ASSUMPTIONS existed
        ("runs-amb1-v2/rep0/add/amb1", 2),
        ("runs-amb1-v2/rep1/add/amb1", 2),   # +1: the race fix (A-priority-vs-fifo)
        ("runs-amb1-v2/rep2/add/amb1", 3),   # +1: the race fix (A-priority-vs-fifo)
    ]

    @pytest.mark.parametrize("rel,expected", CASES)
    def test_archived_run_scores_exactly(self, rel, expected):
        d = B / rel
        if not (d / "workspace").exists() or not (d / "transcript.jsonl").exists():
            pytest.skip("archived run not present (runs dirs are gitignored)")
        detail = compute_ambiguity_detail(d / "workspace", d / "transcript.jsonl", 1, "amb")
        c = collections.Counter(r["verdict"] for r in detail)
        assert c["surfaced"] == expected, (rel, dict(c))
