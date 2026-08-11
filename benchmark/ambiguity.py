"""bench-ambiguity: surface-vs-guess scoring.

WM1-6 measured methods on prompts that said what they meant, and every arm landed
near 0.97. This scorer asks the question that terrain could not: when the spec is
ambiguous, did the method NAME the problem, or quietly pick a reading?

The rule that gives the track its point — **luck is not judgement**:

    surfaced  >  guessed_right  >  guessed_wrong

An agent that ships the defensible reading without ever naming the ambiguity scores
`guessed_right`. It got the right answer; it did not demonstrate the behaviour the
track measures. Only naming the ambiguity BEFORE writing the code counts as surfacing.

Two deliberate constraints:

1. **No LLM judge.** The honest-fidelity-meter milestone retired the LLM
   `spec_fidelity` score for the probe-based `requirement_coverage` because judge
   scores were not trustworthy. A judge here would re-import that defect.

2. **Arm-neutral markers.** ADD's idiom is saturated with assumption-flagging
   language, so a detector tuned to ADD vocabulary would report ADD winning by
   construction — a mirror, not a measurement. MARKERS is plain English any method
   could produce, and `test_detector_uses_no_arm_specific_token` fails loudly if an
   arm's idiom ever creeps in.

KNOWN LIMIT, stated rather than hidden: this detector cannot distinguish a genuine
recognition of ambiguity from an incidental mention that happens to sit near an
anchor. It is deliberately conservative (same-sentence co-occurrence + a position
gate + an anchor/marker disjointness rule), and every surfaced verdict carries the
matched sentence so a human can audit it. If audit
shows the verdicts do not survive scrutiny, the honest outcome is to refute the
metric and not publish it — not to loosen the detector until the numbers look good.
"""
from __future__ import annotations

import re
from typing import Any, Iterable, Sequence

__all__ = ["MARKERS", "WINDOW", "CODE_SUFFIXES", "AmbiguityError",
           "validate_ambiguities", "is_implementation_write", "classify", "score_all"]

# Prose is where a method THINKS; code is where it COMMITS. The first live run
# showed why the distinction matters: ADD's first "write" was to PROJECT.md — its
# own analysis — which slammed the surfacing window shut before it could record
# the contradiction it had just found. Counting that as commitment penalises every
# method that reasons on disk instead of in chat.
#
# Decided by file KIND, never by directory: an allow-list naming `.add/` or
# `.specify/` would hard-code one method's layout into the meter, and the arm that
# matched the list would win on filing convention rather than judgement.
CODE_SUFFIXES: frozenset[str] = frozenset({
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb", ".java", ".kt",
    ".c", ".h", ".cpp", ".cs", ".php", ".swift", ".sh", ".sql",
})
PROSE_SUFFIXES: frozenset[str] = frozenset({".md", ".rst", ".txt", ".adoc"})


def is_implementation_write(path: str) -> bool:
    """True iff writing `path` is COMMITTING to a reading rather than reasoning.

    Prose never commits; code always does. Anything else (config, data) is
    treated as commitment, since the conservative direction is to CLOSE the
    surfacing window early — a metric should not be able to inflate itself by
    keeping the window open on a technicality.
    """
    suffix = ("." + path.rsplit(".", 1)[-1].lower()) if "." in path else ""
    return suffix not in PROSE_SUFFIXES


class AmbiguityError(Exception):
    """A malformed ambiguity row — fail loud, never score a broken track."""


# Plain-English surfacing vocabulary. Any method could emit these; none is an arm's
# idiom. Two shapes count as surfacing: ASKING ("which of", "should i") and
# RECORDING a chosen reading ("assum", "taking it as"). Silence counts as neither.
MARKERS: tuple[str, ...] = (
    "ambigu",            # ambiguous / ambiguity
    "unclear",
    "clarif",            # clarify / clarification / NEEDS CLARIFICATION
    "contradic",         # contradicts / contradiction
    "underspecif",       # underspecified
    "assum",             # assume / assuming / assumption
    "which of",
    "should i",
    "open question",
    "not specified",
    "does not say",
    "two readings",
    "interpret",
    # --- the DECLARATIVE register, added after the ASSUMPTIONS re-run -------------
    # The list above was drawn from chat-style hedging. A method that writes its
    # recognition into a DOCUMENT phrases it as a statement about the spec, not as a
    # question — "the spec never restricts X", "Y is not stated". Three explicit,
    # pre-code, in-artifact surfacings went uncredited on morphology alone.
    #
    # Every entry here is a variant of a speech act ALREADY above (`does not say` /
    # `not specified`): a contraction, a negation synonym, or another verb for "said".
    # No new speech act is admitted — test_every_addition_is_a_variant_of_an_existing
    # _marker holds that line, and test_a_bare_mention_still_does_not_surface holds
    # that naming a topic without a not-said construction still scores nothing.
    "doesn't say",
    "never says",
    "not stated",
    "does not state",
    "doesn't state",
    "not defined",
    "does not define",
    "doesn't define",
    # NOT "does not specify" / "never specifies": `specify` is a BANNED arm token
    # (spec-kit's `/specify` command), and the fairness guard is a substring check that
    # cannot tell the command from the plain verb. Weakening that guard to fit this
    # expansion would trade a real protection for a marginal one — `not specified` is
    # already in the list above and covers the same construction.
    "does not restrict",
    "doesn't restrict",
    "never restricts",
    "does not give",
    "doesn't give",
    "does not pin",
    "never names",
)

# Co-occurrence is SENTENCE-scoped, not a character window. A 400-char window scored
# "I assume the server is already running. Then I added conflict handling." as
# surfaced — two unrelated sentences that happen to sit near each other. Requiring
# the marker and the anchor in the SAME sentence kills that false positive while
# keeping every genuine phrasing (asking, or recording a chosen reading).
WINDOW = 400   # max marker-to-anchor distance INSIDE a sentence
# Two boundary kinds: whitespace after end-punctuation (ordinary prose), and a newline
# followed by a list marker or heading. The second exists because a markdown bullet that
# ends without punctuation (`-> <cost if wrong>`) never terminated a sentence, so a whole
# `## ASSUMPTIONS` block fused into one mega-sentence and a per-line document format was
# scored as a single run-on. A wrapped paragraph (newline, next line starts with a word)
# is still ONE sentence — only `-`/`*`/`#` open a new one.
_SENT_SPLIT = re.compile(r"(?<=[.!?;\n])\s+|\n+(?=[-*#])")


def validate_ambiguities(rows: object) -> list[dict]:
    """Validate a track's AMBIGUITIES list, or raise AmbiguityError.

    Every item needs >=2 competing readings, each with a callable probe, and a
    `defensible` key naming one of them — otherwise "which reading shipped" would
    be decided by prose rather than by probing the built app."""
    if not isinstance(rows, list) or not rows:
        raise AmbiguityError("invalid_ambiguity_row: AMBIGUITIES must be a non-empty list")
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise AmbiguityError(f"invalid_ambiguity_row: row {i} is not a mapping")
        for key in ("id", "klass", "anchors", "readings", "defensible"):
            if key not in row:
                raise AmbiguityError(f"invalid_ambiguity_row: row {i} missing {key!r}")
        if row["klass"] not in ("contradiction", "gap", "trap"):
            raise AmbiguityError(f"invalid_ambiguity_row: row {i} bad klass {row['klass']!r}")
        readings = row["readings"]
        if not isinstance(readings, dict) or len(readings) < 2:
            raise AmbiguityError(
                f"invalid_ambiguity_row: row {i} needs >=2 competing readings")
        for name, probe in readings.items():
            if not callable(probe):
                raise AmbiguityError(
                    f"invalid_ambiguity_row: row {i} reading {name!r} probe not callable")
        if row["defensible"] not in readings:
            raise AmbiguityError(
                f"invalid_ambiguity_row: row {i} defensible reading not among readings")
        if not row.get("anchors"):
            raise AmbiguityError(f"invalid_ambiguity_row: row {i} has no anchors")
        # An anchor that is ALSO a marker marks itself: every mention of the item
        # would score as surfacing it, and a silent run would read as a surfaced one.
        # Found by refute-read — "conflict" was both — after 17 green tests missed it.
        for anchor in row["anchors"]:
            low = anchor.lower()
            if any(m in low for m in MARKERS):
                raise AmbiguityError(
                    f"invalid_ambiguity_row: row {i} anchor {anchor!r} collides with the "
                    "marker vocabulary — it would mark itself (anchor_marker_collision)")
    return rows


def _find_surfacing(item: dict, texts: Iterable[str], edit_pos: int,
                    siblings: Sequence[dict] | None = None) -> str:
    """Return the matched evidence span, or "" if the item was never surfaced.

    Surfaced iff a marker and one of the item's anchors appear in the SAME SENTENCE,
    and that sentence sits before `edit_pos` (the offset of the first edit to the
    implementing file). A marker after the edit is post-hoc rationalisation:
    explaining a choice already made is not surfacing it.

    With `siblings`, a pairing sentence that attribution assigns to ANOTHER item — or
    to nobody (a tie) — does not stop the search; the scan continues to the first
    sentence that pairs AND is attributable to this item. Returning the first pair
    unconditionally lost real recognitions: ADD's dense opening assumption line cites
    waitlist, 409, priority and position together, so it won the race for several
    items, was vetoed for most of them, and a clean dedicated sentence further down
    the same document was never reached (rep1/rep2, `A-priority-vs-fifo`). The veto
    itself is unweakened — a run whose only pair belongs to a sibling still scores
    nothing, and a tie still credits nobody however many times it is scanned.
    """
    anchors = [a.lower() for a in item["anchors"]]
    for raw in texts:
        if not raw:
            continue
        pos = 0
        for sentence in _SENT_SPLIT.split(raw):
            start = raw.find(sentence, pos)
            if start == -1:
                start = pos
            pos = start + len(sentence)
            if start >= edit_pos:            # post_hoc_rationalisation
                continue
            low = sentence.lower()
            # BOTH guards, because each catches what the other misses: the sentence
            # bound rejects two unrelated adjacent sentences; the character bound
            # rejects a run-on where the marker sits thousands of chars from the
            # anchor (a frozen test caught this when sentence-scoping alone shipped).
            m_at = next((low.find(m) for m in MARKERS if m in low), -1)
            a_at = next((low.find(a) for a in anchors if a in low), -1)
            if m_at != -1 and a_at != -1 and abs(m_at - a_at) <= WINDOW:
                if siblings is not None and \
                        best_attribution(sentence, list(siblings)) != item["id"]:
                    continue             # a sibling's (or nobody's) sentence — keep looking
                return sentence.strip()
    return ""


def _anchor_hits(sentence_low: str, item: dict) -> int:
    return sum(1 for a in item["anchors"] if a.lower() in sentence_low)


def best_attribution(sentence: str, items: Sequence[dict]) -> str | None:
    """Which ONE item a sentence surfaces — or None when it cannot be told.

    The first live run made the need concrete. One spec-kit sentence about the
    202-vs-409 CONTRADICTION also contained the words "priority" and "position",
    so it was credited to all three planted items and a genuine 1/3 was reported
    as a perfect 3/3. A recognition of one ambiguity is not evidence about the
    others that happen to share its vocabulary.

    Most anchor matches wins. A TIE credits nobody: an unattributable sentence is
    not evidence about any single item, and guessing between them would be the
    same coin-flip the whole track exists to refuse to reward.
    """
    low = sentence.lower()
    scored = sorted(((_anchor_hits(low, it), it["id"]) for it in items), reverse=True)
    if not scored or scored[0][0] == 0:
        return None
    if len(scored) > 1 and scored[1][0] == scored[0][0]:
        return None                      # tie -> unattributable
    return scored[0][1]


def classify(*, item: dict, transcript: str, artifacts: Sequence[str],
             shipped: str, edit_pos: int,
             siblings: Sequence[dict] | None = None) -> dict[str, Any]:
    """Score ONE planted ambiguity into surfaced | guessed_right | guessed_wrong.

    `shipped` is the reading the built app actually implements (decided by the
    item's probes, never by prose). `edit_pos` is the offset of the first edit to
    the implementing file — surfacing must precede it.

    Artifacts are searched alongside the transcript so a method that surfaces in a
    WRITTEN document scores identically to one that asks in chat; searching only the
    transcript would quietly penalise document-first methods.
    """
    # M2 (a sentence surfaces at most ONE item) is enforced INSIDE the search:
    # a sibling's sentence is skipped, not fatal, so a dedicated sentence later in
    # the same document still counts.
    evidence = _find_surfacing(item, (transcript, *artifacts), edit_pos,
                               siblings=siblings)
    if evidence:
        verdict = "surfaced"
    elif shipped == item["defensible"]:
        verdict = "guessed_right"      # luck_is_not_surfacing
    else:
        verdict = "guessed_wrong"
    return {
        "id": item["id"],
        "klass": item["klass"],
        "shipped": shipped,
        "verdict": verdict,
        "evidence": evidence,
    }


def score_all(items: Sequence[dict], *, transcript: str, artifacts: Sequence[str],
              shipped_by_id: dict[str, str], edit_pos_by_id: dict[str, int]
              ) -> tuple[float, list[dict]]:
    """Score every planted item -> (ambiguity_surface_rate, per-item detail).

    The rate counts ONLY `surfaced`. A method with a perfect guess record and zero
    surfacing scores 0.0 here — which is the entire point: this metric measures
    whether the ambiguity was made visible, not whether the coin landed well.
    """
    validate_ambiguities(list(items))
    detail = [
        classify(item=it, transcript=transcript, artifacts=artifacts,
                 shipped=shipped_by_id.get(it["id"], "neither"),
                 edit_pos=edit_pos_by_id.get(it["id"], 0),
                 siblings=list(items))
        for it in items
    ]
    surfaced = sum(1 for d in detail if d["verdict"] == "surfaced")
    return (surfaced / len(detail) if detail else 0.0), detail
