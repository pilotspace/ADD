"""bench-ambiguity-authorship: the artifact corpus is what the ARM WROTE, not what shipped.

`_workspace_artifacts` rglobbed every prose file in the workspace. For an arm that
installs a vendored corpus that is catastrophic in BOTH directions, and the first live
amb1 run demonstrated both at once:

  FALSE POSITIVE. The `add` arm was credited `surfaced` on A-cancel-authority, evidence:
  "most incidents aren't caused by bad code, they're caused by missing observability,
  unclear ownership, and undocumented dependencies" — a sentence from
  `.add/personas-teacher/engineering/engineering-incident-response-commander.md`, a file
  the installer shipped and the agent never read, let alone wrote. Marker "unclear" and
  an anchor met in one sentence of boilerplate. The headline metric read add 0.286 vs
  vanilla 0.143; corrected, both arms surfaced exactly one item.

  FALSE NEGATIVE. 299 prose files, `limit=40`, sorted — so 35 of the 40 scored files were
  `personas-teacher/`, and `.add/tasks/*.md`, where ADD does its actual direction
  reasoning, sorted after the corpus and was NEVER READ. The arm's real work was crowded
  out by its own vendored dependency.

The bias is one-sided by construction: `vanilla` installs nothing, so it has no
boilerplate to be credited for and nothing to crowd out its own documents.

The rule is authorship, established from the transcript's write targets, and it is
arm-neutral in the sense ambiguity.py demands — it names no directory and no method's
layout. A path-based exclusion (`skip .add/`) would hard-code one arm's filing
convention into the meter, which is the defect, not the fix.

This suite exists so the tightening cannot silently over-correct: the document-first
guarantee — a method that surfaces in a WRITTEN document scores like one that asks in
chat — is defended by test_authored_prose_is_still_scored.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.score import _workspace_artifacts, authored_prose_paths  # noqa: E402

MARKER_SENTENCE = (
    "Most incidents are caused by unclear ownership rather than by bad code.\n")
AUTHORED_SENTENCE = (
    "The spec is ambiguous about ownership: it never says whether another caller "
    "may cancel a booking.\n")


def _transcript(tmp_path: pathlib.Path, write_paths: list[str]) -> pathlib.Path:
    """A minimal JSONL transcript whose tool_use blocks write `write_paths`."""
    lines = []
    for p in write_paths:
        lines.append(json.dumps({"message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {"file_path": p}}]}}))
    t = tmp_path / "transcript.jsonl"
    t.write_text("\n".join(lines) + ("\n" if lines else ""))
    return t


def test_vendored_prose_is_not_scored_as_the_arms_own_words(tmp_path):
    """covers: M1 — a file the arm never wrote is not evidence of what the arm thought."""
    ws = tmp_path / "ws"
    (ws / ".add" / "personas-teacher").mkdir(parents=True)
    (ws / ".add" / "personas-teacher" / "incident-commander.md").write_text(MARKER_SENTENCE)
    transcript = _transcript(tmp_path, [])          # the arm wrote nothing

    docs = _workspace_artifacts(ws, authored=authored_prose_paths(transcript))

    assert not any("unclear ownership" in d for d in docs), (
        "vendored corpus text is being scored as the arm's own reasoning")


def test_authored_prose_is_still_scored(tmp_path):
    """covers: M2 — the document-first guarantee survives the tightening.

    The whole reason `_workspace_artifacts` exists is that ADD writes its analysis to
    disk. If this regressed, the fix would have re-introduced the bug it was built for.
    """
    ws = tmp_path / "ws"
    (ws / ".add" / "tasks").mkdir(parents=True)
    node = ws / ".add" / "tasks" / "booking-api.md"
    node.write_text(AUTHORED_SENTENCE)
    transcript = _transcript(tmp_path, [str(node)])

    docs = _workspace_artifacts(ws, authored=authored_prose_paths(transcript))

    assert any("never says whether another caller" in d for d in docs), (
        "prose the arm demonstrably wrote must still be scored")


def test_vendored_bulk_cannot_crowd_out_authored_prose(tmp_path):
    """covers: M3, E1 — the `limit` truncation must not be spendable by a dependency.

    60 vendored files sorting BEFORE the authored node, which is exactly the live
    shape: `personas-teacher/` < `tasks/`, and limit=40 never reached the tasks.
    """
    ws = tmp_path / "ws"
    (ws / ".add" / "aaa-corpus").mkdir(parents=True)
    for i in range(60):
        (ws / ".add" / "aaa-corpus" / f"p{i:03d}.md").write_text(MARKER_SENTENCE)
    (ws / ".add" / "tasks").mkdir(parents=True)
    node = ws / ".add" / "tasks" / "booking-api.md"
    node.write_text(AUTHORED_SENTENCE)
    transcript = _transcript(tmp_path, [str(node)])

    docs = _workspace_artifacts(ws, authored=authored_prose_paths(transcript))

    assert any("never says whether another caller" in d for d in docs), (
        "authored prose was truncated away by vendored bulk")


def test_a_heredoc_written_document_counts_as_authored(tmp_path):
    """covers: M4, R:MIRROR_BIAS — the fix must not create the bias it removes.

    Heredocs are asymmetric across arms (add 23 of 118 archived transcripts, spec-kit
    1), which is why edit_pos counts them. If authorship counted only Write/Edit, the
    arm that heredocs its documents would lose credit for prose it demonstrably wrote —
    the exact mirror of the vendored-corpus inflation.
    """
    ws = tmp_path / "ws"
    (ws / ".add").mkdir(parents=True)
    (ws / ".add" / "notes.md").write_text(AUTHORED_SENTENCE)
    t = tmp_path / "transcript.jsonl"
    t.write_text(json.dumps({"message": {"content": [
        {"type": "tool_use", "name": "Bash",
         "input": {"command": "cat > .add/notes.md <<'EOF'\nwhatever\nEOF"}}]}}) + "\n")

    docs = _workspace_artifacts(ws, authored=authored_prose_paths(t))

    assert any("never says whether another caller" in d for d in docs), (
        "a heredoc-written document was not credited as the arm's own prose")


def test_authorship_ignores_code_writes(tmp_path):
    """covers: E2 — the corpus is PROSE; a written .py is commitment, not reasoning."""
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "app.py").write_text("# " + MARKER_SENTENCE)
    transcript = _transcript(tmp_path, [str(ws / "app.py")])

    assert not _workspace_artifacts(ws, authored=authored_prose_paths(transcript))


def test_a_missing_transcript_scores_no_artifacts(tmp_path):
    """covers: R:INFLATE — fail CLOSED, matching first_code_write_offset's convention.

    A missing transcript must never mean "credit everything on disk"; that would let a
    harness failure inflate the metric for whichever arm ships the most prose.
    """
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "notes.md").write_text(MARKER_SENTENCE)

    assert authored_prose_paths(tmp_path / "absent.jsonl") == frozenset()
    assert not _workspace_artifacts(ws, authored=frozenset())
