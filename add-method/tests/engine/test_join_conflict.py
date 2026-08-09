"""`add join` — same-identity delta divergence is FLAGGED, and a dropped stream leaves no trace.

The join-merge union assumed streams only ever add DISTINCT deltas. When two streams reach a different
disposition on the SAME lesson (same learning text, different status/evidence), keeping both silently
would let a rejected lesson survive next to an accepted one — the one lossy path the method forbids.
join flags it for the human instead. And dropping a stream (excluded or HARD-STOP) must leave every
other stream's merge byte-intact, with the dropped stream's node and deltas absent (rollback isolation).
"""
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _init_main(tmp_path):
    main = tmp_path / "main"
    add.init(main, "code", "T")
    add.new(main, "Milestone", "m", title="m")
    add.new(main, "Task", "sa", title="sa", milestone="m", scope=["a.py"])
    add.new(main, "Task", "sb", title="sb", milestone="m", scope=["b.py"])
    return main


def _pass_stream(main, name, slug):
    d = main.parent / name
    shutil.copytree(main, d)
    runs = d / "tasks" / f"{slug}.d" / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "1.md").write_text(f"# receipt for {slug}\n", encoding="utf-8")
    add._transition(d, f"/tasks/{slug}.md", sets={"status": "done"}, appends=[("verified",
        f'{{ by: "x", at: {add._today()}, act: gate, authority: process, '
        f'outcome: PASS, receipt: /tasks/{slug}.d/runs/1.md }}')])
    return d


def _append_delta(bundle, line):
    """Append a raw delta line under specs/quality.md's ## Deltas (bypasses learn's fixed status)."""
    p = bundle / "specs" / "quality.md"
    body = p.read_text(encoding="utf-8")
    if "## Deltas" not in body:
        body += "\n## Deltas\n\n"
    p.write_text(body + line + "\n", encoding="utf-8")


def test_join_flags_divergent_deltas(tmp_path):
    """covers: M1, R:SILENTCONFLICT — same lesson, different status → reported as a conflict."""
    main = _init_main(tmp_path)
    sA = _pass_stream(main, "sA", "sa")
    sB = _pass_stream(main, "sB", "sb")
    _append_delta(sA, "- [QUALITY · open] retry backoff needs a jitter cap (evidence: a)")
    _append_delta(sB, "- [QUALITY · rejected] retry backoff needs a jitter cap (evidence: b)")
    result, note = add.join(main, [sA, sB])
    conflicts = result.get("conflicts") or []
    assert any("retry backoff needs a jitter cap" in c["identity"] for c in conflicts), \
        f"a same-lesson/different-disposition divergence must be flagged: {result}"


def test_conflict_variants_are_not_auto_inserted(tmp_path):
    """covers: M2 — neither divergent variant is written; a distinct lesson still unions."""
    main = _init_main(tmp_path)
    sA = _pass_stream(main, "sA", "sa")
    sB = _pass_stream(main, "sB", "sb")
    _append_delta(sA, "- [QUALITY · open] jitter cap needed (evidence: a)")
    _append_delta(sB, "- [QUALITY · rejected] jitter cap needed (evidence: b)")
    _append_delta(sA, "- [QUALITY · open] a distinct clean lesson (evidence: c)")
    add.join(main, [sA, sB])
    body = (main / "specs" / "quality.md").read_text(encoding="utf-8")
    assert "jitter cap needed" not in body, "a flagged conflict's variants must NOT be auto-inserted"
    assert "a distinct clean lesson" in body, "a non-conflicting delta still unions"


def test_rollback_leaves_other_streams_intact(tmp_path):
    """covers: M3, R:ROLLBACKLEAK — dropping a stream leaves the survivor byte-intact, the dropped absent."""
    main = _init_main(tmp_path)
    sA = _pass_stream(main, "sA", "sa")
    _append_delta(sA, "- [QUALITY · open] the survivor lesson (evidence: a)")
    # sB is "rolled back": simply not passed to join (the worktree was dropped).
    result, _ = add.join(main, [sA])
    assert "sa" in result["merged"] and "sb" not in result["merged"]
    body = (main / "specs" / "quality.md").read_text(encoding="utf-8")
    assert "the survivor lesson" in body, "the surviving stream's delta must land"
    # the dropped stream never touched main: sb is still an ungated direction node
    fm, _ = add.parse((main / "tasks" / "sb.md").read_text(encoding="utf-8"))
    assert fm.get("status") != "done", "a rolled-back stream must leave no trace in main"
