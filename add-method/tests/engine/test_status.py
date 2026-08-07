"""Red suite for e6 `build-orient` — status, and the three flags A3 restored.

One test per Must / Reject of tasks/build-orient. M5's checks close the defect e4 created:
a transition that changed `status:` left the CARD asserting the old beat, so one file held
two contradicting facts.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Orient")
    add.new(tmp_path, "Milestone", "m-one", title="Milestone One")
    add.new(tmp_path, "Task", "alpha-task", title="Reject overlapping bookings",
            milestone="/milestones/m-one.md")
    add.new(tmp_path, "Task", "beta-task", title="Send confirmation email",
            milestone="/milestones/m-one.md")
    return tmp_path


# ------------------------------------------------------------------ bounded, T0 (M1)


def test_status_is_t0_only(bundle, monkeypatch):
    """covers: M1, R:T2SCAN — building a report must not read a single body."""
    real = add.read
    leaks = []

    def spy(path, tier="T0"):
        if tier != "T0":
            leaks.append((str(path), tier))
        return real(path, tier)

    monkeypatch.setattr(add, "read", spy)
    add.status(bundle)
    assert leaks == [], f"status read past T0: {leaks}"


def test_status_is_bounded(tmp_path):
    """covers: M1, R:UNBOUNDED — 100 nodes must not print 100 lines (A12)."""
    add.init(tmp_path, "code", "Big")
    for i in range(100):
        add.new(tmp_path, "Task", f"task-{i:03d}", title=f"Task {i}")
    out = add.status(tmp_path)
    node_lines = [l for l in out.splitlines() if l.strip().startswith("·")]
    assert len(node_lines) <= 20, f"printed {len(node_lines)} node lines — unbounded"
    import re as _re
    assert _re.search(r"\d+ more of \d+", out), f"the count of omitted nodes was not reported:\n{out}"


def test_status_excludes_done_by_default(bundle):
    """covers: M1 — a finished node is not orientation (A12)."""
    cid, _ = add.new(bundle, "Task", "finished", title="Finished thing")
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T0")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")

    assert "finished" not in add.status(bundle)
    assert "finished" in add.status(bundle, all=True)


# ------------------------------------------------------------------- next: (M2, law 4)


def test_status_ends_with_next(bundle):
    """covers: M2 — the engine teaches at the moment of use."""
    out = add.status(bundle)
    assert out.strip().splitlines()[-1].lower().startswith("next:")


def test_next_on_empty_bundle(tmp_path):
    """covers: M2 — a bundle with no tasks still names a defensible step, never invents one."""
    add.init(tmp_path, "code", "Empty")
    out = add.status(tmp_path)
    last = out.strip().splitlines()[-1]
    assert last.lower().startswith("next:")
    assert "add " in last, f"next: named nothing runnable: {last!r}"


def test_next_names_the_blocking_gate(bundle):
    """covers: M2 — a task in verify awaiting a gate should point at the gate."""
    cid, _ = add.new(bundle, "Task", "awaiting", title="Awaiting gate")
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T0")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'verify')}\n---\n{n['body']}")
    out = add.status(bundle)
    assert "gate" in out.lower(), "a task awaiting a gate produced no gate hint"


# --- WITHDRAWN 2026-08-05 by `cut-status-flags` (D-12) -------------------------------
# Four checks lived here, proving `build-orient`'s M1, M3 and M4:
#   test_locate_by_slug_fragment · test_locate_by_title_fragment
#   test_graph_is_per_milestone  · test_since_uses_stamps_not_mtime
# They were removed with the features they proved, not because they were wrong. e6's
# node keeps those Musts exactly as its human gate accepted them (§3.6) — a gate records
# what was accepted, never what still ships. The reason is in
# `.add/tasks/cut-status-flags.md` under `## RETIRED`.
# -----------------------------------------------------------------------------------

# ------------------------------------------------- the drift e4 created (M5, R:SILENTDRIFT)


def test_card_drift_detected(bundle):
    """covers: M5, R:SILENTDRIFT — frontmatter says done, the CARD says build."""
    cid = "/tasks/alpha-task.md"
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")

    drift = add.card_drift(add.scan(bundle))
    assert any(cid == d[0] for d in drift), f"the contradiction e4 created went unreported: {drift}"


def test_render_card_repairs_one_line(bundle):
    """covers: M5 — the repair is surgical: exactly one line changes."""
    cid = "/tasks/alpha-task.md"
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")
    before = path.read_text().splitlines()

    changed, note = add.render_card(bundle, cid)
    assert changed is True
    after = path.read_text().splitlines()
    diff = [(a, b) for a, b in zip(before, after) if a != b]
    assert len(diff) == 1, f"the repair changed {len(diff)} lines, expected 1: {diff}"
    assert add.card_drift(add.scan(bundle)) == [] or cid not in [d[0] for d in add.card_drift(add.scan(bundle))]


def test_render_card_is_idempotent(bundle):
    """covers: M5 — a CARD already correct is not rewritten."""
    cid = "/tasks/alpha-task.md"
    add.render_card(bundle, cid)
    before = (bundle / cid.lstrip("/")).read_bytes()
    changed, note = add.render_card(bundle, cid)
    assert changed is False
    assert (bundle / cid.lstrip("/")).read_bytes() == before


# ------------------------------------------------------------------- notary (M6, law 3)


def test_notary_never_raises(bundle):
    """covers: M6 — a malformed node is a line in the report, never an exception."""
    (bundle / "tasks" / "broken.md").write_text("---\nthis: is: not: parseable\n")
    out = add.status(bundle)  # must not raise
    assert isinstance(out, str) and out


def test_live_bundle_status():
    """covers: M1, M2 — this repo's own bundle orients in a bounded report."""
    out = add.status(REPO / ".add")
    assert out.strip().splitlines()[-1].lower().startswith("next:")
    node_lines = [l for l in out.splitlines() if l.strip().startswith("·")]
    assert len(node_lines) <= 20


def test_status_excludes_receipts(bundle):
    """covers: M1, R:UNBOUNDED — Run nodes are evidence, not orientation.

    Found by running `status` on this repo's own bundle: 10 of 20 lines were receipt nodes
    named `1`, `2`, `3`. Bounded but not orienting — the report hit its line budget while
    telling the reader nothing about the work.
    """
    add.freeze(bundle, "/tasks/alpha-task.md", by="human:tindang")
    (bundle / "tasks" / "alpha-task.d" / "runs").mkdir(parents=True)
    for i in (1, 2):
        (bundle / "tasks" / "alpha-task.d" / "runs" / f"{i}.md").write_text(
            f"---\ntype: Run\nruntime: pytest\ntask: /tasks/alpha-task.md\n---\n")

    out = add.status(bundle)
    assert "Run" not in out, f"receipt nodes crowded out the work:\n{out}"


def test_status_shows_work_before_reference(bundle):
    """covers: M1, M2 — Milestones and Tasks come before Specs in a bounded report."""
    out = add.status(bundle)
    lines = [l for l in out.splitlines() if l.strip().startswith("·")]
    kinds = [l.split("]")[-1].strip() for l in lines]
    work = [i for i, k in enumerate(kinds) if k in ("Milestone", "Task")]
    ref = [i for i, k in enumerate(kinds) if k == "Spec"]
    assert not work or not ref or max(work) < min(ref), \
        f"reference nodes outranked work in the report:\n{out}"
