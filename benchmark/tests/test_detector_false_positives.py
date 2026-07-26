"""Three defects that made add-enumerate's first run report 3/7 when it earned 1/7.

All three found by READING the evidence spans of a result that moved in the
direction I was hoping for. The rate alone looked like a clean win.

D1 — ANCHORS MATCH INSIDE LONGER WORDS. "position" is a substring of
     "composition", so a sentence about image composition surfaced
     A-position-ordering.

D2 — A CLOSING XML TAG IS A MARKER. "assum" is a substring of "</assumptions>",
     so the tag that ENDS ADD's assumptions block marks whatever sentence follows
     it — in the live case, the opening line of the contract body.

D3 — THE ARTIFACT BUDGET READS SHIPPED DOCUMENTATION. `_workspace_artifacts`
     takes the first 40 prose files in sort order. An ADD workspace contains 302,
     of which 256 are the vendored `personas-teacher` library, so the budget is
     consumed entirely by ADD's own product documentation — and PLAN.md, the
     agent's actual reasoning, sorts at index 270 and is never read at all.

     The live false positive came from
     `.add/personas-teacher/design/design-image-prompt-engineer.md`, whose
     boilerplate says "Avoid ambiguous language that could be interpreted multiple
     ways". That sentence ships in every ADD workspace. It is not a run's output;
     scoring it credits an arm for the contents of its own installer.

D3 is the same defect as the original `artifacts = ()` bug wearing the opposite
sign: that one read none of the agent's documents, this one reads everything
EXCEPT them. Both were invisible because the surrounding tests exercised
`classify` directly and never the seam that chooses what to feed it.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.ambiguity import _anchor_hits, _find_surfacing
from benchmark.score import _workspace_artifacts

# The LIVE strings, verbatim from runs-enum-2026-07-26-rep0's record.
COMPOSITION = ("- Consider aspect ratio and composition in every prompt\n"
               "- Avoid ambiguous language that could be interpreted multiple ways")
CLOSING_TAG = ('</assumptions>\n```\nPOST /bookings   body: { title, start_time, '
               'end_time, room_id, priority? }')

_POSITION = {"id": "A-position-ordering", "klass": "trap",
             "anchors": ("position", "promoted next", "position 1"),
             "readings": {}, "defensible": ""}
_PRIORITY = {"id": "A-priority-vs-fifo", "klass": "gap",
             "anchors": ("priority", "promoted"),
             "readings": {}, "defensible": ""}


class TestAnchorsRespectWordBoundaries:
    def test_composition_does_not_surface_position_ordering(self):
        assert not _find_surfacing(_POSITION, (COMPOSITION,), 10**9), (
            "'position' matched inside 'composition'")

    def test_anchor_hits_does_not_count_a_substring_match(self):
        # best_attribution ranks on this count, so a phantom hit can also STEAL
        # a genuine surfacing away from the item that earned it.
        assert _anchor_hits(COMPOSITION.lower(), _POSITION) == 0

    def test_a_real_mention_still_counts(self):
        # Needs a MARKER as well as the anchor — "never says" is not in MARKERS,
        # and a sentence without one is not a surfacing by this detector's rules.
        real = "It is unclear whether position 1 tracks arrival order or priority."
        assert _anchor_hits(real.lower(), _POSITION) > 0
        assert _find_surfacing(_POSITION, (real,), 10**9)

    def test_boundaries_do_not_break_punctuated_or_multiword_anchors(self):
        item = {"id": "X", "anchors": ("409", "end_time is exclusive", "back-to-back"),
                "klass": "gap", "readings": {}, "defensible": ""}
        for text in ("it returns 409 on conflict", "assume end_time is exclusive here",
                     "unclear whether back-to-back bookings collide"):
            assert _anchor_hits(text.lower(), item) > 0, text


class TestClosingTagsAreNotMarkers:
    def test_assumptions_close_tag_does_not_mark_the_next_sentence(self):
        assert not _find_surfacing(_PRIORITY, (CLOSING_TAG,), 10**9), (
            "'</assumptions>' acted as an uncertainty marker")

    def test_prose_inside_an_assumptions_block_still_counts(self):
        # The BLOCK is where ADD records uncertainty; only the TAG is noise.
        # Stripping tags must not silence what they wrap.
        inside = ("<assumptions>\n  We assume priority overrides arrival order; "
                  "the spec does not say.\n</assumptions>")
        assert _find_surfacing(_PRIORITY, (inside,), 10**9)

    def test_tag_stripping_leaves_comparison_operators_alone(self):
        # "start < other.end AND end > other.start" is prose about a boundary, not
        # markup — a greedy <...> strip would delete the substance of the sentence.
        item = {"id": "Y", "anchors": ("overlap",), "klass": "trap",
                "readings": {}, "defensible": ""}
        text = ("Assume overlap means start < other.end AND end > other.start, "
                "which the spec never states.")
        ev = _find_surfacing(item, (text,), 10**9)
        assert ev and "other.end" in ev, ev


class TestArtifactsAreTheAgentsOwnWriting:
    """D3 — the budget must not be spent on the arm's installed documentation."""

    def _workspace(self, tmp_path):
        ws = tmp_path / "ws"
        # 60 shipped docs that sort BEFORE the agent's own file, exactly as
        # `.add/personas-teacher/**` does against `.add/tasks/**/PLAN.md`.
        shipped = ws / ".add" / "personas-teacher"
        shipped.mkdir(parents=True)
        for i in range(60):
            (shipped / f"aaa-{i:03d}.md").write_text(
                "Avoid ambiguous language that could be interpreted multiple ways. "
                "Consider aspect ratio and composition in every prompt.",
                encoding="utf-8")
        plan = ws / ".add" / "tasks" / "t"
        plan.mkdir(parents=True)
        (plan / "PLAN.md").write_text(
            "The spec is contradictory about the waitlist: 202 versus 409.",
            encoding="utf-8")
        return ws, plan / "PLAN.md"

    def _transcript(self, tmp_path, wrote: pathlib.Path):
        tx = tmp_path / "t.jsonl"
        tx.write_text(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write",
             "input": {"file_path": str(wrote), "content": "..."}}]}}) + "\n",
            encoding="utf-8")
        return tx

    def test_agent_written_document_is_read_even_when_it_sorts_last(self, tmp_path):
        ws, plan = self._workspace(tmp_path)
        docs = _workspace_artifacts(ws, transcript_path=self._transcript(tmp_path, plan))
        assert any("contradictory" in d for d in docs), (
            "the agent's own PLAN.md was crowded out by shipped documentation")

    def test_shipped_documentation_is_not_read(self, tmp_path):
        ws, plan = self._workspace(tmp_path)
        docs = _workspace_artifacts(ws, transcript_path=self._transcript(tmp_path, plan))
        assert not any("aspect ratio" in d for d in docs), (
            "an installed persona library is being scored as the agent's reasoning")

    def test_no_transcript_means_no_artifacts_rather_than_all_of_them(self, tmp_path):
        # Fail CLOSED. Falling back to "read everything" is what produced the
        # false positives, so absence of evidence must not become evidence.
        ws, _ = self._workspace(tmp_path)
        assert _workspace_artifacts(ws, transcript_path=tmp_path / "missing.jsonl") == []
