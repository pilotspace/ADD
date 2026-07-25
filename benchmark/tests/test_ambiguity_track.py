"""bench-ambiguity: the ambiguity track and its surface-vs-guess scorer.

WM1-6 measured methods on terrain where the prompt said what it meant. This track
plants ambiguity on purpose and asks a different question: did the method NAME the
problem, or did it quietly pick a reading and move on?

The scoring rule that gives the track its point: **luck is not judgement**. An agent
that implements the defensible reading without ever naming the ambiguity scores
`guessed_right` — never `surfaced`. Surfacing means the ambiguity was made visible
BEFORE the code was written.

Determinism is deliberate. The honest-fidelity-meter milestone retired the LLM
`spec_fidelity` judge for the probe-based `requirement_coverage`; an LLM judge here
would re-import exactly the untrustworthiness that meter was built to remove.

The self-flattery risk this suite guards: ADD's own idiom is full of assumption-flagging
language, so a detector tuned to ADD vocabulary would report ADD winning by construction.
test_detector_uses_no_arm_specific_token exists to make that failure loud.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

BENCH = pathlib.Path(__file__).resolve().parents[1]
AMB1 = BENCH / "workload" / "amb1"


def _load_items():
    from benchmark.workload.amb1.ambiguity import AMBIGUITIES
    return AMBIGUITIES


def _classify(**kw):
    from benchmark.ambiguity import classify
    return classify(**kw)


class TestTrackShape:
    def test_amb1_declares_three_classes(self):
        # M1 — one item per ambiguity class; a track missing a class cannot
        # distinguish "asks about contradictions" from "asks about anything".
        classes = {i["klass"] for i in _load_items()}
        assert classes == {"contradiction", "gap", "trap"}, f"got {classes}"

    def test_prompt_plants_every_declared_item(self):
        # M1 — an item the PROMPT never raises is unplantable: the agent cannot
        # surface what it was never shown, and the item would score a free miss.
        prompt = (AMB1 / "PROMPT.md").read_text(encoding="utf-8").lower()
        for item in _load_items():
            assert any(a.lower() in prompt for a in item["anchors"]), \
                f"{item['id']}: no anchor appears in PROMPT.md"

    def test_every_reading_has_an_executable_probe(self):
        # M2 + R:invalid_ambiguity_row — which reading SHIPPED must be decided by
        # probing the built app, never by reading the agent's prose about itself.
        for item in _load_items():
            readings = item["readings"]
            assert len(readings) >= 2, f"{item['id']}: needs >=2 competing readings"
            for name, probe in readings.items():
                assert callable(probe), f"{item['id']}.{name} probe not callable"
            assert item["defensible"] in readings, \
                f"{item['id']}: defensible reading not among the readings"

    def test_invalid_row_is_rejected(self):
        # R:invalid_ambiguity_row
        from benchmark.ambiguity import validate_ambiguities, AmbiguityError
        with pytest.raises(AmbiguityError):
            validate_ambiguities([{"id": "x", "klass": "gap", "anchors": ("a",),
                                   "readings": {"a": lambda *_: True},  # only ONE reading
                                   "defensible": "a"}])


class TestDetectorNeutrality:
    def test_detector_uses_no_arm_specific_token(self):
        # M3 — THE FAIRNESS GUARD. If surfacing required an ADD token, ADD would win
        # by vocabulary rather than by judgement, and the whole track would be a mirror.
        from benchmark.ambiguity import MARKERS
        banned = ("plan.md", "§1", "freeze", "gate", "⚠", "add.py", "specify",
                  "constitution", "spec-kit")
        low = [m.lower() for m in MARKERS]
        for b in banned:
            assert not any(b in m for m in low), f"marker vocabulary carries arm idiom: {b}"

    def test_markers_are_shared_english(self):
        # M3 — every marker must be plain English any method could produce.
        from benchmark.ambiguity import MARKERS
        assert len(MARKERS) >= 5
        assert all(m == m.lower() for m in MARKERS), "markers are matched case-folded"


class TestSurfaceVsGuess:
    """The three-way verdict, on synthetic transcripts — no agent, no spend."""

    ITEM = {
        "id": "A-cancel-window", "klass": "contradiction",
        "anchors": ("cancellation window", "24 hours"),
        "readings": {"a": lambda *_: True, "b": lambda *_: False},
        "defensible": "a",
    }

    def test_silent_transcript_scores_unsurfaced(self):
        # M4 + R:luck_is_not_surfacing
        v = _classify(item=self.ITEM, transcript="wrote the endpoint and shipped it",
                      artifacts=(), shipped="a", edit_pos=10)
        assert v["verdict"] != "surfaced"
        assert v["evidence"] == ""

    def test_naming_transcript_scores_surfaced(self):
        # M4 — an explicit question before the edit is the clearest surfacing shape.
        tx = "the cancellation window is unclear here — should i treat 24 hours as inclusive?"
        v = _classify(item=self.ITEM, transcript=tx, artifacts=(), shipped="a",
                      edit_pos=len(tx) + 50)
        assert v["verdict"] == "surfaced"
        assert v["evidence"], "a surfaced verdict must carry its evidence span"

    def test_recorded_assumption_also_counts_as_surfaced(self):
        # Boundary: the second surfacing SHAPE — chosen and STATED, not asked.
        tx = "assuming the cancellation window excludes the final 24 hours, since that is safer"
        v = _classify(item=self.ITEM, transcript=tx, artifacts=(), shipped="a",
                      edit_pos=len(tx) + 50)
        assert v["verdict"] == "surfaced"

    def test_marker_after_implementing_edit_is_not_surfaced(self):
        # R:post_hoc_rationalisation — explaining a choice after making it is not
        # surfacing; the whole value is naming the problem BEFORE committing to it.
        tx = "shipped it. note: the cancellation window was ambiguous, i assumed 24 hours."
        v = _classify(item=self.ITEM, transcript=tx, artifacts=(), shipped="a", edit_pos=0)
        assert v["verdict"] != "surfaced"

    def test_correct_guess_without_naming_is_guessed_right(self):
        # R:luck_is_not_surfacing — the rule the track exists to enforce.
        v = _classify(item=self.ITEM, transcript="implemented bookings",
                      artifacts=(), shipped="a", edit_pos=10)
        assert v["verdict"] == "guessed_right"

    def test_wrong_guess_without_naming_is_guessed_wrong(self):
        v = _classify(item=self.ITEM, transcript="implemented bookings",
                      artifacts=(), shipped="b", edit_pos=10)
        assert v["verdict"] == "guessed_wrong"

    def test_artifact_text_can_carry_the_surfacing(self):
        # M3 — a method that surfaces in a WRITTEN document (a spec file) rather than
        # in chat must score identically; only the transcript being searched would bias.
        doc = "open question: the cancellation window is ambiguous — 24 hours from when?"
        v = _classify(item=self.ITEM, transcript="", artifacts=(doc,), shipped="a",
                      edit_pos=10_000)
        assert v["verdict"] == "surfaced"

    def test_marker_far_from_anchor_does_not_count(self):
        # A marker somewhere else in a long transcript is not about THIS item.
        tx = "this is ambiguous" + (" filler" * 400) + " cancellation window"
        v = _classify(item=self.ITEM, transcript=tx, artifacts=(), shipped="a",
                      edit_pos=10**6)
        assert v["verdict"] != "surfaced", "marker and anchor must co-occur in a window"


class TestRefuteReadFindings:
    """Two defects the 17-test suite above MISSED, found by adversarially probing the
    real workload item instead of a synthetic one. Kept as tests so they stay dead."""

    def test_anchor_that_is_a_marker_is_rejected(self):
        # DEFECT 1: "conflict" was both an anchor of the contradiction item AND a
        # marker, so the anchor marked itself — every silent run scored `surfaced`.
        from benchmark.ambiguity import validate_ambiguities, AmbiguityError
        with pytest.raises(AmbiguityError, match="anchor_marker_collision"):
            validate_ambiguities([{
                "id": "x", "klass": "gap", "anchors": ("an ambiguous thing",),
                "readings": {"a": lambda *_: True, "b": lambda *_: False},
                "defensible": "a"}])

    def test_incidental_marker_in_another_sentence_is_not_surfaced(self):
        # DEFECT 2: a 400-char window scored this as surfaced. Two unrelated
        # sentences that happen to sit near each other are not a recognition.
        item = dict(TestSurfaceVsGuess.ITEM)
        tx = "I assume the server is already running. Then I added the cancellation window."
        v = _classify(item=item, transcript=tx, artifacts=(), shipped="a", edit_pos=10**6)
        assert v["verdict"] == "guessed_right", "incidental mention must not score surfaced"

    def test_every_arm_phrasing_scores_identically(self):
        # THE FAIRNESS PROOF. Five methods' natural phrasings of the same recognition
        # must all score surfaced; if only ADD's idiom did, the track would be a mirror.
        item = dict(TestSurfaceVsGuess.ITEM)
        phrasings = (
            "assuming the cancellation window excludes the last 24 hours",           # ADD
            "[NEEDS CLARIFICATION: cancellation window - 24 hours from when?]",      # spec-kit
            "The spec contradicts itself on the cancellation window. 24 hours?",     # vanilla
            "Open question: the cancellation window is underspecified at 24 hours.", # gsd
            "It is not specified how the cancellation window treats 24 hours.",      # plain
        )
        for tx in phrasings:
            v = _classify(item=item, transcript=tx, artifacts=(), shipped="a",
                          edit_pos=10**6)
            assert v["verdict"] == "surfaced", f"arm-biased detector: {tx!r}"


class TestHarnessWiring:
    def test_family_amb_is_accepted_by_pilot_and_report(self):
        # M5 — the family seam already exists for wm/hv; amb joins it.
        for mod in ("pilot", "report"):
            src = (BENCH / f"{mod}.py").read_text(encoding="utf-8")
            assert '"amb"' in src, f"{mod}.py does not offer --family amb"

    def test_amb_record_validates(self):
        # M5 — the new metric is ADDITIVE: required metrics untouched, so every
        # existing wm record stays valid and an amb record validates too.
        from benchmark.schema.run_record import validate, REQUIRED_METRICS
        metrics = {k: 0.0 for k in REQUIRED_METRICS}
        metrics["ambiguity_surface_rate"] = 0.67
        rec = validate({
            "arm": "add", "wm": 1, "rep": 1, "status": "done",
            "metrics": metrics,
            "artifacts": {"workspace": "/w", "transcript": "/t", "oracle_report": "/o",
                          "ambiguity_detail": "/a.json"},
        })
        assert rec.metrics["ambiguity_surface_rate"] == 0.67

    def test_detail_artifact_is_json_serialisable(self):
        # M4 — the per-item detail must be inspectable by a human, not a blob.
        v = _classify(item=self.ITEM if hasattr(self, "ITEM") else TestSurfaceVsGuess.ITEM,
                      transcript="the cancellation window is ambiguous",
                      artifacts=(), shipped="a", edit_pos=10_000)
        json.dumps(v)  # raises if not serialisable
        assert {"id", "klass", "shipped", "verdict", "evidence"} <= set(v)
