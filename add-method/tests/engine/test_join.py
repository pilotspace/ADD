"""`add join` — fold N worktree stream bundles back into the main bundle.

Each stream is a git worktree with its own `.add/`; because wave enforced disjoint scope, streams only
ever touch DIFFERENT task nodes, so the build phase never races. The race is only at join, and ABF's
own invariants resolve it: node files are disjoint (copied byte-for-byte), spec deltas are append-only
(union-merged), graph.json is a rebuildable cache (regenerated, never merged). A HARD-STOP stream is
never admitted; a PASS stream is never dropped.
"""
import json
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


def _stream(main, name, slug, outcome, lessons=()):
    """A worktree stream: a copy of main whose owned task is gated `outcome`, plus any lessons filed."""
    d = main.parent / name
    shutil.copytree(main, d)
    cid = f"/tasks/{slug}.md"
    if outcome in ("PASS", "RISK-ACCEPTED"):
        runs = d / "tasks" / f"{slug}.d" / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        (runs / "1.md").write_text(f"# receipt for {slug}\n", encoding="utf-8")
        add._transition(d, cid, sets={"status": "done"}, appends=[("verified",
            f'{{ by: "x", at: {add._today()}, act: gate, authority: process, '
            f'outcome: {outcome}, receipt: /tasks/{slug}.d/runs/1.md }}')])
    else:  # HARD-STOP — gated, but must never merge
        add._transition(d, cid, sets={"status": "verify"}, appends=[("verified",
            f'{{ by: "x", at: {add._today()}, act: gate, authority: process, outcome: HARD-STOP }}')])
    for lesson, ev in lessons:
        add.learn(d, "quality", lesson, evidence=ev)
    return d


def test_join_merges_a_pass_stream_losslessly(tmp_path):
    """covers: M1 — a PASS stream's node + its receipt land byte-for-byte in main."""
    main = _init_main(tmp_path)
    sA = _stream(main, "sA", "sa", "PASS")
    result, note = add.join(main, [sA])
    assert "sa" in result["merged"], note
    fm, _ = add.parse((main / "tasks" / "sa.md").read_text(encoding="utf-8"))
    assert fm.get("status") == "done"
    assert (main / "tasks" / "sa.d" / "runs" / "1.md").read_text(encoding="utf-8") == "# receipt for sa\n"
    assert (main / "tasks" / "sa.md").read_bytes() == (sA / "tasks" / "sa.md").read_bytes(), "node byte-for-byte"


def test_join_unions_spec_deltas(tmp_path):
    """covers: M2 — two streams' distinct delta lines both survive; an identical line dedupes."""
    main = _init_main(tmp_path)
    sA = _stream(main, "sA", "sa", "PASS", lessons=[("A lesson", "a"), ("shared lesson", "s")])
    sB = _stream(main, "sB", "sb", "PASS", lessons=[("B lesson", "b"), ("shared lesson", "s")])
    add.join(main, [sA, sB])
    body = (main / "specs" / "quality.md").read_text(encoding="utf-8")
    assert "A lesson" in body and "B lesson" in body, "both streams' distinct deltas survive the union"
    assert body.count("shared lesson") == 1, "an identical delta line dedupes"


def test_join_skips_a_hardstop_stream(tmp_path):
    """covers: M3, R:MERGEHARDSTOP — a HARD-STOP stream is not merged and is reported skipped."""
    main = _init_main(tmp_path)
    sA = _stream(main, "sA", "sa", "HARD-STOP")
    result, note = add.join(main, [sA])
    assert "sa" not in result["merged"], "a HARD-STOP stream must never merge"
    assert any(s["slug"] == "sa" for s in result["skipped"]), note
    fm, _ = add.parse((main / "tasks" / "sa.md").read_text(encoding="utf-8"))
    assert fm.get("status") != "done", "main must be untouched by a HARD-STOP stream"


def test_join_never_drops_a_pass_stream(tmp_path):
    """covers: R:DROPPASS — every PASS stream appears in the merged result."""
    main = _init_main(tmp_path)
    sA = _stream(main, "sA", "sa", "PASS")
    sB = _stream(main, "sB", "sb", "PASS")
    result, _ = add.join(main, [sA, sB])
    assert set(result["merged"]) == {"sa", "sb"}, f"no PASS stream may be dropped: {result}"


def test_join_regenerates_graph(tmp_path):
    """covers: M4 — graph.json after join reflects the merged nodes (rebuilt, not copied)."""
    main = _init_main(tmp_path)
    sA = _stream(main, "sA", "sa", "PASS")
    add.join(main, [sA])
    graph = json.loads((main / "graph.json").read_text(encoding="utf-8"))
    assert graph["nodes"]["/tasks/sa.md"]["status"] == "done", "graph.json reflects the merged node"
