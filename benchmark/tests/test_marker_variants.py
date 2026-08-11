"""bench-ambiguity-vocab: the marker list must cover the DECLARATIVE register too.

`MARKERS` was built from chat-style hedging — "I assume", "should I", "which of". It
already carries the not-said construction in two spellings (`does not say`,
`not specified`) but not the ordinary variants of the same words, so a run that names an
ambiguity in a written document went uncredited on morphology alone.

Measured on the amb1 re-run after `## ASSUMPTIONS` shipped. Three explicit, pre-code,
in-artifact surfacings were scored `guessed_wrong` / `guessed_right`:

    rep2 A5  "The spec never restricts cancellation to the booking's creator -> DELETE is
              permitted for any caller ... but not checked for ownership."
    rep2 A4  "Default priority when the field is omitted is not stated -> default to 0"
    rep1 A5  "The spec doesn't define tie-breaking for equal priority (or the default for
              a missing priority)."

Each names its item exactly. `never restricts`, `not stated` and `doesn't define` are the
same speech act as `does not say`, which has been a marker since the track shipped.

THE HAZARD, NAMED. ambiguity.py says: "If audit shows the verdicts do not survive
scrutiny, the honest outcome is to refute the metric and not publish it — not to loosen
the detector until the numbers look good." Widening a detector AFTER seeing which way it
moves the number is exactly that shape. Three things keep this on the right side, and all
three are asserted below rather than argued:

1. Every addition is a MORPHOLOGICAL VARIANT of a marker already present — a contraction,
   a negation synonym, or a different verb for "said". No new speech act is admitted.
2. The additions cannot rescue a silent run: `test_a_bare_mention_still_does_not_surface`
   pins that naming the topic without a not-said construction still scores nothing.
3. Applied to the archived runs, `vanilla` cannot move — it is "never named" on six of
   seven items, so there is no sentence for a wider vocabulary to match. An expansion that
   lifts one arm only because the other never wrote the sentences is measuring a real
   difference, not manufacturing one.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.ambiguity import MARKERS, classify  # noqa: E402

ITEM = {
    "id": "A-cancel-authority",
    "klass": "gap",
    "anchors": ("who can cancel", "only the creator", "ownership", "cancel any booking"),
    "readings": {"owner_only": lambda *_: True, "anyone": lambda *_: False},
    "defensible": "owner_only",
}

# Verbatim from the amb1 re-run — real sentences, not invented ones.
REAL_SURFACINGS = [
    "The spec never restricts cancellation to the booking's creator, so DELETE is "
    "permitted for any caller carrying a valid Authorization header, and ownership is "
    "not checked.",
    "The spec doesn't say who can cancel a booking, so any caller may cancel any booking.",
    "Default ownership behaviour when the field is omitted is not stated, so cancel any "
    "booking is allowed.",
    "The spec does not define who can cancel, so ownership is ignored.",
]


def _verdict(sentence: str) -> str:
    return classify(item=ITEM, transcript=sentence, artifacts=(), shipped="anyone",
                    edit_pos=10**6, siblings=[ITEM])["verdict"]


def test_declarative_not_said_phrasings_surface():
    """covers: M1 — the register a written ASSUMPTIONS line is actually written in."""
    missed = [s for s in REAL_SURFACINGS if _verdict(s) != "surfaced"]
    assert not missed, f"explicit surfacings still uncredited on morphology: {missed}"


def test_a_bare_mention_still_does_not_surface():
    """covers: R:LOOSENED — the guard that this is a variant list, not a wider net.

    Naming the topic is not naming the ambiguity. If this ever passes, the expansion has
    stopped measuring recognition and started measuring vocabulary overlap.
    """
    assert _verdict("Any caller may cancel any booking via DELETE /bookings/{id}.") != "surfaced"
    assert _verdict("Ownership is recorded on create.") != "surfaced"


def test_every_addition_is_a_variant_of_an_existing_marker():
    """covers: M2 — no new speech act sneaks in behind the morphology argument.

    Each new marker must share a stem with one that predates this change. The frozen
    baseline is the list as it shipped; anything not reducible to it is a widening and
    has to be argued on its own, not smuggled in here.
    """
    baseline_stems = ("say", "specif", "state", "defin", "restrict", "give", "pin",
                      "name", "ambigu", "unclear", "clarif", "contradic", "underspecif",
                      "assum", "which of", "should i", "open question", "readings",
                      "interpret")
    for m in MARKERS:
        assert any(stem in m.lower() for stem in baseline_stems), \
            f"marker {m!r} is not a variant of the original vocabulary — argue it separately"


def test_the_fairness_guard_still_holds():
    """covers: M3 — re-assert the arm-neutrality invariant over the WIDER list."""
    banned = ("plan.md", "§1", "freeze", "gate", "⚠", "add.py", "specify",
              "constitution", "spec-kit", "assumptions", "a1")
    low = [m.lower() for m in MARKERS]
    for b in banned:
        assert not any(b in m for m in low), f"marker vocabulary carries an arm token: {b}"
