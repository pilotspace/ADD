"""Three scorer defects the first live run exposed — all pointing the same way.

Rep 0 reported add 0.00 and spec-kit 1.00. Both numbers were artifacts:

1. ARTIFACTS WERE NEVER READ. `classify` has always accepted an `artifacts`
   argument, documented as existing so "a method that surfaces in a WRITTEN
   document scores identically to one that asks in chat". The call site passed
   `()`. ADD's PLAN.md said the spec "contains two mutually exclusive rules for
   the identical trigger" and scored zero for it. The guard existed; the wiring
   didn't — the same tested-unit/untested-seam failure this codebase keeps
   producing.

2. ONE SENTENCE CREDITED EVERY ITEM. A spec-kit sentence about the 202-vs-409
   contradiction also contained "priority" and "position", so it was credited to
   all three planted items and a genuine 1/3 was published as a perfect 3/3.

3. WRITING THE PLAN CLOSED THE WINDOW. ADD's first "code write" was to
   PROJECT.md — its own analysis. The surfacing window shut before the
   contradiction it had just found could count.

Defects 1 and 3 penalise methods that think on disk; defect 2 rewards methods
that narrate in chat. ADD writes to disk, spec-kit narrates. Every error pushed
the result the same way, which is exactly why the fix needed to come before any
further spend rather than after.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.ambiguity import best_attribution, classify, is_implementation_write
from benchmark.score import _workspace_artifacts, compute_ambiguity_detail, transcript_prose

RUNS = pathlib.Path(__file__).resolve().parents[1] / "runs-amb-2026-07-26"

_ITEMS = [
    {"id": "A-one", "klass": "contradiction", "anchors": ("waitlist", "409", "202"),
     "readings": {"a": lambda *_: True, "b": lambda *_: False}, "defensible": "a"},
    {"id": "A-two", "klass": "gap", "anchors": ("priority",),
     "readings": {"a": lambda *_: True, "b": lambda *_: False}, "defensible": "a"},
]


class TestImplementationSplit:
    def test_markdown_write_does_not_close_the_window(self):
        # M3 / R:analysis_counted_as_commitment — writing an analysis IS the act
        # of surfacing; treating it as commitment is self-defeating.
        for doc in ("PLAN.md", ".add/PROJECT.md", "specs/spec.md", "notes.txt"):
            assert is_implementation_write(doc) is False, doc

    def test_code_write_closes_the_window(self):
        for code in ("app/__main__.py", "src/main.go", "cli.ts", "run.sh"):
            assert is_implementation_write(code) is True, code

    def test_split_names_no_arm_specific_path(self):
        # M4 / R:arm_specific_path — a list naming .add/ or .specify/ would hand
        # the win to whichever arm files its notes in the expected place.
        import benchmark.ambiguity as amb
        src = pathlib.Path(amb.__file__).read_text(encoding="utf-8")
        # Slice the DEFINITION, then drop comments: the comment above the split
        # explains why `.add/` and `.specify/` are deliberately absent, and a raw
        # scan reads that explanation as the thing it warns against. Prose about a
        # path is not a path — the third time this exact false positive has come up.
        block = src[src.index("CODE_SUFFIXES: frozenset"):
                    src.index("def is_implementation_write")]
        code = "\n".join(l for l in block.splitlines() if not l.lstrip().startswith("#"))
        for token in (".add", ".specify", "constitution", "PLAN.md", "spec.md"):
            assert token not in code, f"file-kind split hard-codes {token}"


class TestAttribution:
    def test_best_anchor_match_wins_attribution(self):
        # M2 — the LIVE rep-0 sentence. It surfaces the contradiction; the other
        # two items merely share its vocabulary.
        sentence = ("items #4-#6 (promotion, priority, position reporting) depend on the "
                    "waitlist being populated; conflicts get waitlisted (202), not 409")
        assert best_attribution(sentence, _ITEMS) == "A-one"

    def test_tie_credits_nobody(self):
        # An unattributable recognition is not evidence about any single item,
        # and guessing between them is the coin-flip this track refuses to reward.
        tied = [{"id": "X", "anchors": ("alpha",)}, {"id": "Y", "anchors": ("beta",)}]
        assert best_attribution("alpha and beta both appear here", tied) is None

    def test_sentence_with_no_anchor_credits_nobody(self):
        assert best_attribution("an unrelated remark", _ITEMS) is None

    def test_one_sentence_credits_at_most_one_item(self):
        # M2 / R:misattributed_surfacing — end to end through classify.
        tx = ("the spec is contradictory: waitlist 202 versus 409, and this affects "
              "priority too. ")
        verdicts = {
            it["id"]: classify(item=it, transcript=tx, artifacts=(), shipped="a",
                               edit_pos=10**6, siblings=_ITEMS)["verdict"]
            for it in _ITEMS
        }
        assert verdicts["A-one"] == "surfaced"
        assert verdicts["A-two"] != "surfaced", "one sentence surfaced two items"


class TestArtifactsAreRead:
    def test_workspace_artifacts_reads_prose_not_code(self, tmp_path):
        # AMENDED 2026-07-26 (D3): artifacts are now the documents the AGENT
        # WROTE, not every prose file present. Reading the whole tree let an ADD
        # workspace's 256 vendored persona files consume the budget and score as
        # the agent's reasoning, so the transcript must vouch for each file.
        (tmp_path / "PLAN.md").write_text("the spec is ambiguous about the waitlist",
                                          encoding="utf-8")
        (tmp_path / "app.py").write_text("print('code')", encoding="utf-8")
        tx = tmp_path / "t.jsonl"
        tx.write_text("\n".join(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write",
             "input": {"file_path": str(tmp_path / name), "content": "..."}}]}})
            for name in ("PLAN.md", "app.py")) + "\n", encoding="utf-8")
        docs = _workspace_artifacts(tmp_path, transcript_path=tx)
        assert any("ambiguous" in d for d in docs)
        # Still excluded — by file KIND, even though the agent wrote it too.
        assert not any("print('code')" in d for d in docs)

    def test_document_only_surfacing_scores(self):
        # M1 — the exact shape that scored 0.00 in rep 0: nothing in chat, the
        # recognition written to a file.
        doc = "the spec is contradictory: waitlist 202 versus 409"
        v = classify(item=_ITEMS[0], transcript="", artifacts=(doc,), shipped="a",
                     edit_pos=10**6, siblings=_ITEMS)
        assert v["verdict"] == "surfaced"


class TestReadableEvidence:
    def test_prose_extraction_strips_json_syntax(self, tmp_path):
        # The evidence span must be READABLE, or the human audit that justifies
        # this detector's known limit is a rubber stamp. Raw JSONL search once
        # returned `...delta-append` -->"]}],"userModified":false...` as evidence.
        tx = tmp_path / "t.jsonl"
        tx.write_text("\n".join(json.dumps(e) for e in [
            {"type": "assistant", "message": {"content": [
                {"type": "text", "text": "The spec contradicts itself on 202 versus 409."}]}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Write",
                 "input": {"file_path": "app/x.py", "content": "print(1)"}}]}},
        ]) + "\n", encoding="utf-8")
        prose, edit_pos = transcript_prose(tx)
        assert "userModified" not in prose and '"]}]' not in prose
        assert "contradicts itself" in prose
        assert 0 < edit_pos <= len(prose)

    def test_prose_includes_a_written_document_payload(self, tmp_path):
        # A method that writes its reasoning into a file surfaces INSIDE a Write
        # payload; excluding those re-introduces the document-first bias.
        tx = tmp_path / "t2.jsonl"
        tx.write_text(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {
                "file_path": "PLAN.md",
                "content": "resolves a contradiction: waitlist 202 vs 409"}}]}}) + "\n",
            encoding="utf-8")
        prose, _ = transcript_prose(tx)
        assert "resolves a contradiction" in prose


class TestLiveRescore:
    """Against the ARCHIVED rep-0 workspaces — free to re-derive, so anyone can
    check these numbers without paying for a run."""

    def _detail(self, arm: str):
        ws = RUNS / arm / "amb1" / "workspace"
        tx = RUNS / arm / "amb1" / "transcript.jsonl"
        if not ws.exists() or not tx.exists():
            import pytest
            pytest.skip("archived rep-0 run not present (runs dirs are gitignored)")
        return compute_ambiguity_detail(ws, tx, 1, "amb")

    def test_rescoring_add_rep0_finds_the_contradiction(self):
        # M5 — ADD scored 0.00 before the fixes despite naming the contradiction.
        rows = {d["id"]: d for d in self._detail("add")}
        row = rows["A-conflict-response"]
        assert row["verdict"] == "surfaced", row
        assert "contradiction" in row["evidence"].lower(), row["evidence"]

    def test_rescoring_speckit_rep0_yields_exactly_one(self):
        # M5 — spec-kit's 3/3 was one sentence credited three times.
        detail = self._detail("spec-kit")
        surfaced = [d for d in detail if d["verdict"] == "surfaced"]
        assert len(surfaced) == 1, [d["id"] for d in surfaced]
        assert "contradict" in surfaced[0]["evidence"].lower()

    def test_every_surfaced_row_carries_readable_evidence(self):
        # The audit promise: a span a human can actually read and judge.
        for arm in ("add", "spec-kit"):
            for row in self._detail(arm):
                if row["verdict"] != "surfaced":
                    continue
                ev = row["evidence"]
                assert ev and len(ev) > 20, (arm, row)
                for junk in ('"]}]', "userModified", '{"type":', "replaceAll"):
                    assert junk not in ev, f"{arm}: unreadable evidence span: {ev[:80]}"

    def test_detail_rows_name_their_source(self):
        for row in self._detail("add"):
            assert "source" in row
            if row["verdict"] == "surfaced":
                assert row["source"] in ("transcript", "artifact"), row


class TestArtifactWiringIsPinned:
    """The D1 fix survived its own mutation, so it was never really pinned.

    Setting `artifacts = ()` back in compute_ambiguity_detail left all 15 tests
    green: the live case is carried by the transcript's Write payload, and the
    document-only test called `classify` DIRECTLY. Unit tested, seam untested —
    the identical shape as the original defect, reproduced inside its own fix.

    This test can only pass if compute_ambiguity_detail actually reads the
    workspace: the recognition exists ONLY in a file on disk, and the transcript
    never mentions it.

    AMENDED 2026-07-26 (D3). Artifacts are now the documents the agent WROTE, so
    the transcript must record the Write — but its PAYLOAD still does not contain
    the recognition. That is the realistic shape: an Edit records a replacement
    slice, and after several edits the file on disk says things no single payload
    ever did. The guard is unchanged in substance — pass only by reading the FILE —
    while matching the contract that stops the scorer from crediting an arm for
    its own installed documentation.
    """

    def test_surfacing_only_on_disk_is_found_by_compute(self, tmp_path, monkeypatch):
        import benchmark.score as score

        root = tmp_path / "repo"
        d = root / "benchmark" / "workload" / "amb9"
        d.mkdir(parents=True)
        (d / "ambiguity.py").write_text(
            "AMBIGUITIES = [{'id': 'A-one', 'klass': 'contradiction',\n"
            " 'anchors': ('waitlist', '409'),\n"
            " 'readings': {'a': lambda *_: True, 'b': lambda *_: False},\n"
            " 'defensible': 'a'}]\n", encoding="utf-8")
        monkeypatch.setattr(score, "REPO_ROOT", root)

        ws = tmp_path / "ws"
        ws.mkdir()
        # The ONLY place the recognition exists.
        (ws / "PLAN.md").write_text(
            "The spec is contradictory: it both waitlists and returns 409.",
            encoding="utf-8")
        # A transcript that records WRITING the file but whose payload says
        # nothing about the recognition — so only reading the file can find it.
        tx = tmp_path / "t.jsonl"
        tx.write_text("\n".join(json.dumps(e) for e in [
            {"type": "assistant", "message": {"content": [
                {"type": "text", "text": "Building the service now."}]}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Write",
                 "input": {"file_path": str(ws / "PLAN.md"),
                           "content": "# PLAN\n(section stub)\n"}}]}},
        ]) + "\n", encoding="utf-8")

        detail = score.compute_ambiguity_detail(ws, tx, 9, "amb")
        assert detail[0]["verdict"] == "surfaced", \
            "compute_ambiguity_detail is not reading the workspace's documents"
        assert detail[0]["source"] == "artifact", detail[0]
