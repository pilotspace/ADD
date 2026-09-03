"""An advisory nudge names a node you can still advise.

Measured on this repo's own bundle 2026-09-03: 23 of `doctor`'s 25 findings were
`unadvised_sensitive`, and every one named a task already `done`. The advice each carries —
attach a lens — is unreachable on a closed, gated node, so the whole report reads as noise and
the two findings that WERE actionable sat in the middle of it.

The finding is true either way; the question is whether a report is a worklist or an audit log.
It is read as a worklist whether or not it was written as one.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _sensitive(tmp_path, slug, sensitivity="architecture", status=None):
    """A sensitive Task carrying no lens, at whatever status the caller names."""
    if not (tmp_path / ".add").exists():
        add.init(tmp_path, "code", "T")      # returns a TUPLE; nothing here needs it
    cid, _ = add.new(tmp_path, "Task", slug, title=slug, sensitivity=sensitivity)
    node = Path(add.scan(tmp_path)[cid]["path"])
    lines = node.read_text(encoding="utf-8").splitlines()
    # E1 strips the field entirely; otherwise rewrite whatever status `new` chose — it seeds
    # `direction`, not `created`, so a literal replace of the wrong word silently does nothing.
    lines = [l for l in lines if not l.startswith("status:")]
    if status is not None:
        lines.insert(next(i for i, l in enumerate(lines) if l.startswith("type:")) + 1,
                     f"status: {status}")
    node.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return cid


def _codes(tmp_path, cid):
    """Findings doctor reports against one node.

    `doctor` takes the PROJECT root — the parent of `.add` — and returns a list of dicts.
    Handing it the bundle root returns `[]`, which is a green anchor that proves nothing.
    """
    return [f for f in add.doctor(tmp_path) if f["node"] == cid]


def test_a_done_node_is_not_nudged_for_a_lens(tmp_path):
    """covers: M1, A3, A6 — the 23 measured findings."""
    cid = _sensitive(tmp_path, "closed", status="done")
    hits = [f for f in _codes(tmp_path, cid) if f["code"] == "unadvised_sensitive"]
    assert not hits, f"a closed node was told to attach a lens it can no longer attach: {hits}"


def test_an_open_node_is_still_nudged(tmp_path):
    """covers: M2, A2 — the finding must not go silent; `verify` is still advisable."""
    for status in ("created", "direction", "build", "verify"):
        p = tmp_path / status
        p.mkdir()
        cid = _sensitive(p, f"open-{status}", status=status)
        hits = [f for f in _codes(p, cid) if f["code"] == "unadvised_sensitive"]
        assert hits, f"an OPEN ({status}) sensitive node with no lens went unreported"


def test_a_node_with_no_status_is_still_nudged(tmp_path):
    """covers: A4, E1, R:BLINDCLOSE — absent is not closed."""
    cid = _sensitive(tmp_path, "statusless", status=None)
    hits = [f for f in _codes(tmp_path, cid) if f["code"] == "unadvised_sensitive"]
    assert hits, "a node with no `status:` was treated as closed and its finding hidden"


def test_the_severity_split_survives(tmp_path):
    """covers: M3, E2 — security warns while open, and is silent once done like any other."""
    a = tmp_path / "open"; a.mkdir()
    cid = _sensitive(a, "sec-open", sensitivity="security", status="verify")
    hits = [f for f in _codes(a, cid) if f["code"] == "unadvised_sensitive"]
    assert hits and any(f["severity"] == "warn" for f in hits), f"security lost its `warn` severity: {hits}"

    b = tmp_path / "done"; b.mkdir()
    cid = _sensitive(b, "sec-done", sensitivity="security", status="done")
    assert not [f for f in _codes(b, cid) if f["code"] == "unadvised_sensitive"], \
        "M1 does not hold for the HARD floor — a done security node is still unadvisable"


def test_no_other_finding_changed_its_reach(tmp_path):
    """covers: M4 — the exclusion is scoped to ONE finding.

    A done node still carries every other property doctor reports on. Proved by giving the same
    closed node a defect a different finding owns and asserting that one still fires.
    """
    cid = _sensitive(tmp_path, "closed-too", status="done")
    node = Path(add.scan(tmp_path)[cid]["path"])
    node.write_text(node.read_text(encoding="utf-8").replace("---\n", "", 1), encoding="utf-8")
    codes = {f["code"] for f in add.doctor(tmp_path)}
    assert "missing_frontmatter" in codes, (
        "closing a node silenced a finding that was never about the lens: " + str(codes))
