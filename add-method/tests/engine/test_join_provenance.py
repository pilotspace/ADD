"""`join` provenance (A3, task 3).

When a stream was built under a lens (its task node carries `persona:`, stamped by `wave`), the join
stamps `advised_by: <persona>` on the delivered node in main — durable, audit-grade provenance of the
lens the build was advised by. A stream with no lens lands with NO `advised_by:`: provenance is
recorded from the stream, never fabricated at the join.
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
    return main


def _pass_stream(main, name, slug, persona=None):
    """A worktree stream whose owned task is gated PASS; optionally stamped with a `persona:` lens."""
    d = main.parent / name
    shutil.copytree(main, d)
    cid = f"/tasks/{slug}.md"
    if persona:
        npath = d / "tasks" / f"{slug}.md"
        n = add.read(npath, "T2")
        add.write(npath, f"---\n{add.set_key(n['raw'], 'persona', persona)}\n---\n{n['body']}")
    runs = d / "tasks" / f"{slug}.d" / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "1.md").write_text(f"# receipt for {slug}\n", encoding="utf-8")
    add._transition(d, cid, sets={"status": "done"}, appends=[("verified",
        f'{{ by: "x", at: {add._today()}, act: gate, authority: process, '
        f'outcome: PASS, receipt: /tasks/{slug}.d/runs/1.md }}')])
    return d


def _merged_fm(main, slug):
    fm, _ = add.parse((main / "tasks" / f"{slug}.md").read_text(encoding="utf-8"))
    return fm


def test_join_stamps_advised_by_from_lens(tmp_path):
    """covers: M1 — a merged node built under a lens lands in main with advised_by set to that persona."""
    main = _init_main(tmp_path)
    sA = _pass_stream(main, "sA", "sa", persona="backend-systems")
    add.join(main, [sA])
    assert _merged_fm(main, "sa").get("advised_by") == "backend-systems"


def test_join_leaves_unlensed_node_without_provenance(tmp_path):
    """covers: M2, R:FABRICATEDPROVENANCE — an unlensed merged node lands with no advised_by key."""
    main = _init_main(tmp_path)
    sA = _pass_stream(main, "sA", "sa", persona=None)
    add.join(main, [sA])
    assert "advised_by" not in _merged_fm(main, "sa"), "provenance must never be fabricated"
