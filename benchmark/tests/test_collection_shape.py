"""A collection response's SHAPE is not a requirement any prompt states.

Audit, 2026-07-26. Six FROZEN checklists asserted `isinstance(body, list)` for
endpoints their PROMPTs describe only as "lists bookings". No wm prompt says
"array", "list of", or anything equivalent — checked, not assumed. Re-probing
every archived workspace with an envelope-unwrapping transport flipped 11
failing rows to covered across BOTH arms:

    runs-nbr-session/add   wm4   0.17 -> 0.67     (3 of 6 rows)
    runs-session/*         wm2   0.20 -> 0.40     (both arms)
    runs-session/spec-kit  wm3   0.75 -> 1.00
    runs/{seeded,enforced}-r1/add wm1  0.92 -> 1.00
    runs-amb rep1-2/spec-kit amb1 0.91 -> 1.00

`requirement_coverage` replaced an LLM `spec_fidelity` judge precisely because
judges were not trustworthy and probes were meant to be. A probe encoding an
unstated preference is that same defect wearing a deterministic costume, and it
is worse for being invisible: the run looks like a build failure.

The audit that found this was itself vacuous on the first pass — `_load_checklist`
re-execs the module from file, so patching `sys.modules` changed nothing and the
harness reported a confident "none". It was caught only by a POSITIVE CONTROL: a
case already known to fail on shape, which must flip. Any audit that cannot
detect the thing it is looking for reports zero.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.workload._oracle_lib import records

WORKLOAD = pathlib.Path(__file__).resolve().parents[1] / "workload"


class TestRecordsSemantics:
    def test_bare_array_is_a_collection(self):
        assert records([{"id": 1}]) == [{"id": 1}]

    def test_empty_array_is_a_collection_not_a_miss(self):
        # `records(body) == []` must distinguish "empty collection" from "not a
        # collection"; `if not rows` would conflate them and wm4's empty-window
        # row asserts exactly the empty case.
        assert records([]) == []
        assert records([]) is not None

    @pytest.mark.parametrize("key", ["items", "results", "data", "bookings",
                                     "entries", "records", "waitlist", "tasks"])
    def test_named_envelopes_unwrap(self, key):
        assert records({key: [{"id": 1}]}) == [{"id": 1}]

    def test_unanticipated_envelope_key_still_unwraps(self):
        # The alternative is meeting this same bug again under a new spelling.
        assert records({"reservations": [{"id": 1}], "count": 1}) == [{"id": 1}]

    def test_two_lists_are_ambiguous_and_yield_nothing(self):
        # Guessing which list is "the" collection would re-import the coin-flip
        # this benchmark exists to refuse.
        assert records({"bookings": [], "errors": []}) is not None  # named key wins
        assert records({"alpha": [{"a": 1}], "beta": [{"b": 2}]}) is None

    def test_non_collections_are_none(self):
        for payload in (None, 5, "text", {"id": 1}, {"error": "nope"}):
            assert records(payload) is None, payload

    def test_named_key_beats_the_single_list_fallback(self):
        assert records({"items": [{"id": 1}], "warnings": []}) == [{"id": 1}]


class TestNoChecklistAssertsAShape:
    """Mechanical guard. The prompts fix semantics, never serialization."""

    def _probe_sources(self):
        # Checklists AND oracles. The guard originally globbed only
        # `*/checklist.py`, so six live oracle surfaces kept asserting a bare
        # array — the guard was blind to half the tree it was written to
        # protect, which is the same enumeration gap it exists to prevent.
        for f in sorted(WORKLOAD.glob("*/checklist.py")):
            yield f.name, f.parent.name, f.read_text(encoding="utf-8")
        for f in sorted(WORKLOAD.glob("*/oracle/*.py")):
            yield f"oracle/{f.name}", f.parent.parent.name, f.read_text(encoding="utf-8")

    def test_no_probe_requires_a_bare_json_array(self):
        for name, wm, text in self._probe_sources():
            code = "\n".join(l for l in text.splitlines()
                             if not l.lstrip().startswith("#"))
            for banned in ("isinstance(body, list)", "isinstance(payload, list)",
                           "type(body) is list"):
                assert banned not in code, f"{wm}/{name} asserts a response shape: {banned}"

    def test_every_checklist_that_reads_a_collection_imports_records(self):
        # A checklist could satisfy the guard above by open-coding the same check
        # a different way; requiring the shared helper keeps ONE definition of
        # what a collection is, rather than six drifting twins.
        for name, wm, text in self._probe_sources():
            if "records(" in text:
                tree = ast.parse(text)
                imported = {alias.name for node in ast.walk(tree)
                            if isinstance(node, ast.ImportFrom)
                            for alias in node.names}
                assert "records" in imported, f"{wm}/{name} uses records() unimported"


class TestArchivedRunsRescoreHigher:
    """The audit's own positive control, kept as a test.

    Skips when the archived runs are absent — `benchmark/runs*/` is gitignored,
    so a fresh checkout has nothing to re-probe. Skipping is honest here; the
    unit tests above carry the semantics regardless.
    """

    CASE = ("runs-amb-2026-07-26-rep1/spec-kit/amb1/workspace", 1, "amb", "R-get-list")

    def test_known_envelope_case_now_scores_covered(self):
        from benchmark.score import compute_coverage_detail

        rel, wm, family, row = self.CASE
        ws = pathlib.Path(__file__).resolve().parents[1] / rel
        if not ws.exists():
            pytest.skip("archived run not present (benchmark/runs*/ is gitignored)")
        detail = {d["id"]: d["covered"] for d in compute_coverage_detail(ws, wm, family)}
        assert detail[row] is True, (
            f"{rel} still fails {row}; this app answers "
            '{"bookings": [...]}, which the prompt permits')
