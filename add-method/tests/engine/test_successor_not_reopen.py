"""Red suite for `successor-not-reopen` — closed history is superseded, never reopened.

`verified[]` is append-only, so a reopen keeps the old PASS; but loop.md called a reopen inside a
closed milestone "incoherent, resolved by hand" and no `status --check` finding ever existed for it.
Now `reopen` refuses it (R:CLOSEDHISTORY) naming `add new Task <slug>-2 --supersedes /tasks/<old>.md`,
`new --supersedes` writes the edge key that had zero live uses, `show` walks it both ways, and the
old node, its receipts and its PASS are never edited.

Driven as `.add/tasks/successor-not-reopen.md` under milestone `loop-that-closes`.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
import cli  # noqa: E402

TREES = (REPO / "skill" / "add", REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
         REPO.parent / ".claude" / "skills" / "add")


def _set_status(bundle, cid, status):
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{add.set_key(n['raw'], 'status', status)}\n---\n{n['body']}")


def _done_task(bundle, slug, **fields):
    cid, _ = add.new(bundle, "Task", slug, title=slug, **fields)
    _set_status(bundle, cid, "done")
    d = bundle / "tasks" / f"{slug}.d" / "runs"
    d.mkdir(parents=True)
    (d / "1.md").write_text("---\ntype: Run\n---\nreceipt\n")
    return cid


@pytest.fixture
def bundle(tmp_path):
    b = tmp_path / ".add"
    add.init(b, "code", "P")
    add.new(b, "Milestone", "m", title="m", goal="ship")
    return b


def _bytes_of(bundle, cid):
    p = bundle / cid.lstrip("/")
    return p.read_bytes(), sorted((q.name, q.read_bytes()) for q in (p.with_suffix(".d") / "runs").glob("*"))


def test_reopen_refuses_inside_a_closed_milestone(bundle):
    """covers: M1, R:CLOSEDHISTORY, E1 — done and archived both refuse, naming the fix; no stamp."""
    t = _done_task(bundle, "t", milestone="m")
    for status in ("done", "archived"):
        _set_status(bundle, "/milestones/m.md", status)
        before = _bytes_of(bundle, t)
        ok, note = add.reopen(bundle, t, "build", "a criterion was unmet")
        assert ok is None and "R:CLOSEDHISTORY" in note, f"{status}: {note!r}"
        assert "/milestones/m.md" in note and status in note and "add new Task t-2 --supersedes /tasks/t.md" in note, note
        assert _bytes_of(bundle, t) == before, "a refused reopen touched the old node"
        assert add.scan(bundle)[t]["fm"]["status"] == "done"


def test_reopen_still_returns_open_history(bundle):
    """covers: M1, A2, A4, E2, E5 — active, no-milestone and an unknown word all reopen."""
    t = _done_task(bundle, "t", milestone="m")
    u = _done_task(bundle, "u")
    add.new(bundle, "Milestone", "s", title="s", goal="ship")
    _set_status(bundle, "/milestones/s.md", "shipped")
    v = _done_task(bundle, "v", milestone="s")
    for cid in (t, u, v):
        ok, note = add.reopen(bundle, cid, "build", "unmet")
        assert ok is True, f"{cid}: {note!r}"
        assert add.scan(bundle)[cid]["fm"]["status"] == "build"
        assert any(s.get("act") == "reopen" for s in add.scan(bundle)[cid]["fm"]["verified"])


def test_new_supersedes_writes_the_edge(bundle):
    """covers: M2, E3 — slug and cid both land as the resolved cid list."""
    t = _done_task(bundle, "t", milestone="m")
    for slug, ref in (("t-2", "t"), ("t-3", "/tasks/t.md")):
        cid, note = add.new(bundle, "Task", slug, title=slug, supersedes=ref)
        assert cid, note
        assert add.scan(bundle)[cid]["fm"]["supersedes"] == ["/tasks/t.md"], add.scan(bundle)[cid]["fm"].get("supersedes")


def test_new_refuses_a_phantom_predecessor(bundle):
    """covers: M2, R:PHANTOMPREDECESSOR, E3 — named, nothing written."""
    cid, note = add.new(bundle, "Task", "t-2", title="t-2", supersedes="ghost")
    assert cid is None and "R:PHANTOMPREDECESSOR" in note and "ghost" in note, note
    assert not (bundle / "tasks" / "t-2.md").exists()


def test_show_walks_supersedes_both_ways(bundle):
    """covers: M3, E4 — ↓ on the successor, ↑ on the predecessor, doctor silent on both."""
    t = _done_task(bundle, "t", milestone="m")
    s, _ = add.new(bundle, "Task", "t-2", title="t-2", supersedes="/tasks/t.md")
    _, out = add.show(bundle, "t-2")
    assert re.search(r"↓ supersedes.*?/tasks/t\.md", out), out
    _, out = add.show(bundle, "t")
    assert re.search(r"↑ supersedes.*?/tasks/t-2\.md", out), out
    # `unauthored_node` fires on both scaffolds whatever their edges — excluded like the other
    # body-shaped findings, and the assertion below keeps this check's own subject: NO finding,
    # of any code, may name the edge.
    finds = [f for f in add.doctor(bundle) if f["node"] in (t, s) and f["code"] not in
             ("card_drift", "okf_conformance", "unadvised_sensitive", "unauthored_node", "evidence_scaffold")]
    assert not finds, finds
    assert not [f for f in add.doctor(bundle) if "supersedes" in f["detail"]], "doctor reads the edge as a defect"


def test_the_past_is_never_rewritten(bundle):
    """covers: M4, R:REWRITTENPAST — old node bytes and receipts identical after a refusal and a successor."""
    t = _done_task(bundle, "t", milestone="m")
    _set_status(bundle, "/milestones/m.md", "done")
    before = _bytes_of(bundle, t)
    add.reopen(bundle, t, "build", "unmet")
    add.new(bundle, "Task", "t-2", title="t-2", supersedes="t")
    assert _bytes_of(bundle, t) == before


def test_cli_new_carries_supersedes(bundle):
    """covers: M2 — the parser has --supersedes and the dispatch writes the edge."""
    _done_task(bundle, "t", milestone="m")
    assert "--supersedes" in cli.build_parser().format_help() or any(
        "--supersedes" in a.format_help() for a in cli.build_parser()._subparsers._group_actions[0].choices.values())
    code = cli.main(["--root", str(bundle), "new", "task", "t-2", "--supersedes", "t"])
    assert code == 0
    assert add.scan(bundle)["/tasks/t-2.md"]["fm"]["supersedes"] == ["/tasks/t.md"]


def test_loop_md_and_format_state_it():
    """covers: M5 — loop.md names the refusal and the successor form; FORMAT names the writer; line-neutral."""
    loop = (REPO / "skill" / "add" / "loop.md").read_text(encoding="utf-8")
    assert "R:CLOSEDHISTORY" in loop and "--supersedes" in loop, "loop.md does not name the refusal or the successor form"
    assert "resolved by hand" not in loop and "incoherent" not in loop, "loop.md still promises a finding the engine never had"
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    assert "new --supersedes" in fmt and "Three of the seven edge keys" not in fmt, "FORMAT still counts supersedes among the unused keys"
    for tree in TREES[1:]:
        assert (tree / "loop.md").read_bytes() == (REPO / "skill" / "add" / "loop.md").read_bytes(), tree
    # TRIPWIRE: the working tree against `HEAD`, so `git commit` satisfies it — it fires while the
    # skill edit is uncommitted, which is exactly when the line-neutral rule is decided.
    head = subprocess.run(["git", "show", "HEAD:add-method/skill/add/loop.md"], cwd=REPO.parent,
                          capture_output=True, text=True, check=True).stdout
    assert len(loop.splitlines()) == len(head.splitlines()), "loop.md is not line-neutral vs HEAD"


def test_a_fragment_is_no_predecessor(bundle):
    """covers: M2, A7, R:PHANTOMPREDECESSOR — a predecessor is a NODE: an edge to a lesson inside
    one is not a history, and `resolve_ref` answers a fragment address happily."""
    _done_task(bundle, "t", milestone="m")
    add.learn(bundle, "method", "a lesson to address", evidence="/tasks/t.md")
    cid, note = add.new(bundle, "Task", "t-2", title="t-2", supersedes="/specs/method.md#M1")
    assert cid is None and "R:PHANTOMPREDECESSOR" in note, note
    assert not (bundle / "tasks" / "t-2.md").exists()


def test_the_state_a_closed_milestone_member_reaches_by_order(bundle):
    """covers: M1, A11, E6 — the rung collides with release-stamp's frozen M3/E12, which needs a
    member reopened AFTER its closing gate inside a milestone that is done at release time. That
    state stays reachable in the legal order — reopen while the milestone is active, then close it
    — so the older contract keeps its claim and this one keeps its refusal."""
    t = _done_task(bundle, "t", milestone="m")
    assert add.reopen(bundle, t, "build", "unmet")[0], "an active milestone must still reopen"
    _set_status(bundle, "/milestones/m.md", "done")
    fm = add.scan(bundle)[t]["fm"]
    assert fm["status"] == "build" and any(s.get("act") == "reopen" for s in fm["verified"])
    _set_status(bundle, t, "done")
    ok, note = add.reopen(bundle, t, "build", "again")
    assert ok is None and "R:CLOSEDHISTORY" in note, f"the closed milestone must refuse the NEXT one: {note!r}"
