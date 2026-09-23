"""Q37's un-run check: the set of `verified[]` stamp readers is ENUMERATED, not described.

`.add/specs/quality.md#Q37` binds the rule — "when a rule quantifies over a set of readers,
its check ENUMERATES that set" — and a folded lesson dated 2026-09-13 records the cost of
leaving it un-run: three T2 reads found `_latest_run_cid`, the test_cmd memory and `_beat_of`
ONE AT A TIME, each the same class the bound suite had proved only for `latest_receipt`.
`quick-lane-tripwire` then paid the same tax eight more times, each round finding the same
defect class one gate to the left.

Every one of those was a MISSED READER. A stamp is written once and re-interpreted at
thirty-odd call sites; nothing failed when a new site read it with the wrong semantics.

This module is the census. It does not judge whether a reader is correct — it refuses to let
the reader SET change silently. Adding a stamp reader is a deliberate act: register it here
and, for a gate reader, declare which of the two questions it answers.

The two questions a gate reader can ask, which are NOT the same question:

* **"was this node EVER gated?"** — an `any(...)` existence test. A later `reopen` does not
  un-ask it, so such a reader is correctly reopen-agnostic.
* **"what verdict stands NOW?"** — the latest gate AFTER the last `reopen`. A reader of this
  shape that ignores `reopen` reports a superseded verdict as the current one.
"""

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "tooling" / "add.py"
sys.path.insert(0, str(REPO / "tooling"))


# ── the census ────────────────────────────────────────────────────────────────
#
# Every function that compares a stamp's `act` against a literal, by the act it reads.
# Regenerate deliberately, never mechanically: a diff here is a new interpreter of a fact
# somebody else wrote.
READERS = {
    "brief": {"_brief_entered"},
    "freeze": {"_brief_entered", "_has_carry_history", "_is_frozen", "_latest_freeze_stamp", "_latest_scope_seal", "_pins_of", "authority_for", "local", "done",
               "freeze", "gate", "_resolve_exit_move", "sealed_binding", "sealed_direction",
               "stamped_gives"},
    "gate": {"_admits", "_anchor", "_effective_gate_stamp", "_last_gate_outcome",
             "checks_verify", "done", "join"},
    "interview": {"_interview_stamps"},
    "refreeze": {"_brief_entered", "_has_carry_history", "_is_frozen", "_latest_freeze_stamp", "_latest_scope_seal", "_pins_of", "authority_for", "local", "done", "freeze", "gate",
                 "_resolve_exit_move", "sealed_binding", "sealed_direction", "stamped_gives"},
    "refute": {"_refute_of"},
    "release": {"show", "status"},
    "reopen": {"_anchor", "_effective_gate_stamp", "done"},
    "run": {"_beat_of", "_brief_entered", "_latest_run_cid"},
}
# B3 adds three readers of freeze-class history: `_has_carry_history` identifies a prior
# non-empty transfer, `authority_for` and its nested `local` retain that transfer's highest
# stamped floor after correction or removal. Both acts have the same lineage semantics.

# Which question each gate reader asks. Every name in READERS["gate"] appears in exactly one
# of these, with the reason it belongs there. A `current-verdict` reader MUST be reopen-aware.
GATE_ASKS_EVER = {
    "_admits": "existence half of the join pre-flight: did this stream work this node at all",
    "checks_verify": "grades a missing cited test as `error` once a gate stamp exists at all",
    "join": "skips a stream node carrying no gate stamp as a stale sibling copy",
}
GATE_ASKS_NOW = {
    "_anchor": "the release stamp anchors the receipt the CLOSING gate cited",
    "_effective_gate_stamp": "the accessor itself — latest gate after the last reopen",
    "_last_gate_outcome": "its docstring says `the last gate` and both callers read it as the "
                          "verdict that stands",
    "done": "closure reads the verdict in force, which a reopen supersedes",
}

# Known divergence, recorded rather than silently tolerated. `_last_gate_outcome` answers the
# current-verdict question with the ever-gated shape: it takes the last gate stamp by append
# order and never looks for a `reopen`, so a node gated PASS and then REOPENED still reports
# PASS. `_effective_gate_stamp` was added beside it with the reopen-aware semantics but its
# two callers (`_admits`, `join`) were not moved. Converting them is an engine behaviour change
# inside `seal-what-you-signed`'s blast radius and belongs to a node that freezes it, not to
# this census. The census's job is to make sure the divergence cannot grow quietly.
REOPEN_BLIND_BY_RECORD = {"_last_gate_outcome"}


def _act_readers(source: str) -> dict:
    """act literal -> {enclosing function names} for every direct `act` comparison.

    Walks into nested functions from the parent too, so a reader hidden in a closure is
    attributed to both and cannot be introduced by nesting it out of sight.
    """
    def literals(node):
        out = set()
        if not isinstance(node, ast.Compare):
            return out
        left = node.left
        names = isinstance(left, ast.Call) and isinstance(left.func, ast.Attribute) \
            and left.func.attr == "get" and left.args \
            and isinstance(left.args[0], ast.Constant) and left.args[0].value == "act"
        subs = isinstance(left, ast.Subscript) and isinstance(left.slice, ast.Constant) \
            and left.slice.value == "act"
        if not (names or subs):
            return out
        for comparator in node.comparators:
            if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                out.add(comparator.value)
            elif isinstance(comparator, (ast.Tuple, ast.List, ast.Set)):
                for element in comparator.elts:
                    if isinstance(element, ast.Constant) and isinstance(element.value, str):
                        out.add(element.value)
        return out

    found = {}
    for fn in ast.walk(ast.parse(source)):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            for act in literals(node):
                found.setdefault(act, set()).add(fn.name)
    return found


@pytest.fixture(scope="module")
def census():
    return _act_readers(ENGINE.read_text(encoding="utf-8"))


def test_the_reader_set_is_enumerated(census):
    """M1 — a new interpreter of `verified[]` cannot enter the engine unannounced."""
    assert set(census) == set(READERS), (
        "a stamp `act` the census does not list is read somewhere in add.py.\n"
        f"  engine reads: {sorted(census)}\n"
        f"  census lists: {sorted(READERS)}\n"
        "Q37: when a rule quantifies over a set of readers, its check ENUMERATES that set.")
    for act in sorted(READERS):
        added = sorted(census[act] - READERS[act])
        dropped = sorted(READERS[act] - census[act])
        assert not (added or dropped), (
            f"the reader set for `act: {act}` moved.\n"
            f"  new readers:  {added or 'none'}\n"
            f"  gone readers: {dropped or 'none'}\n"
            "A new reader re-interprets a fact another writer recorded — the class that cost "
            "quick-lane-tripwire eight refute rounds. Register it above, and for a gate reader "
            "declare in GATE_ASKS_EVER or GATE_ASKS_NOW which question it asks.")


def test_every_gate_reader_declares_which_question_it_asks(census):
    """M2 — `ever gated?` and `what stands now?` are different questions, declared apart."""
    classified = set(GATE_ASKS_EVER) | set(GATE_ASKS_NOW)
    overlap = set(GATE_ASKS_EVER) & set(GATE_ASKS_NOW)
    assert not overlap, f"a gate reader asks one question, not both: {sorted(overlap)}"
    assert census["gate"] == classified, (
        "every gate reader declares its shape.\n"
        f"  unclassified: {sorted(census['gate'] - classified)}\n"
        f"  stale entries: {sorted(classified - census['gate'])}")


def test_a_current_verdict_reader_survives_a_reopen(census):
    """M3 — a reader of the verdict in force looks past the last `reopen`, or is on record."""
    source = ENGINE.read_text(encoding="utf-8")
    bodies = {fn.name: ast.get_source_segment(source, fn) or ""
              for fn in ast.walk(ast.parse(source))
              if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))}
    blind = {name for name in GATE_ASKS_NOW
             if "reopen" not in bodies.get(name, "")
             and "_effective_gate_stamp" not in bodies.get(name, "")}
    assert blind == REOPEN_BLIND_BY_RECORD, (
        "a reader of the verdict in force ignores `reopen`, and is not the one on record.\n"
        f"  reopen-blind now: {sorted(blind)}\n"
        f"  on record:        {sorted(REOPEN_BLIND_BY_RECORD)}\n"
        "Either read the gate through `_effective_gate_stamp`, or reclassify the reader into "
        "GATE_ASKS_EVER with the reason existence is the question it actually asks.")


def test_the_census_fails_on_a_reader_it_was_not_told_about():
    """M4 — withhold the subject: the guard is red on a reader nobody registered.

    A census that cannot fail is a census of nothing. This injects one extra reader into a
    COPY of the engine source and proves the parser sees it.
    """
    source = ENGINE.read_text(encoding="utf-8")
    injected = source + (
        '\n\ndef _a_reader_nobody_registered(fm):\n'
        '    return [s for s in (fm or {}).get("verified") or [] if s.get("act") == "gate"]\n')
    after = _act_readers(injected)
    assert "_a_reader_nobody_registered" in after["gate"]
    assert after["gate"] - READERS["gate"] == {"_a_reader_nobody_registered"}, (
        "the census must notice exactly the injected reader and nothing else")
