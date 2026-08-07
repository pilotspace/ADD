"""`advise` records a persona lens on a sequential beat (A1, task 1).

The sequential twin of the lens `wave`/`join` record for a parallel stream: `advise` stamps
`advised_by: <persona>` on a lifecycle node, validated against the roster (R:BADPERSONA), lifecycle-only
(R:NOTATASK), idempotent re-route, and NO-EXEC (it records the chosen lens, never runs the persona).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _fm_raw(root, cid):
    m = re.match(r"\A---\n(.*?)\n---\n", (root / cid.lstrip("/")).read_text(encoding="utf-8"), re.DOTALL)
    return m.group(1) if m else ""


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    cid, _ = add.new(tmp_path, "Task", "a", title="a", milestone="m", sensitivity="security", scope=["a.py"])
    add.new(tmp_path, "Persona", "sec-rev", title="security lens")
    add.new(tmp_path, "Persona", "backend-systems", title="backend lens")
    return cid


def test_advise_stamps_advised_by(tmp_path):
    """covers: M1 — after advise, the node carries `advised_by: <persona>`."""
    cid = _bundle(tmp_path)
    out, note = add.advise(tmp_path, cid, "sec-rev")
    assert out == "sec-rev", note
    assert re.search(r"^advised_by:\s*sec-rev\s*$", _fm_raw(tmp_path, cid), re.M), _fm_raw(tmp_path, cid)


def test_advise_reroute_replaces(tmp_path):
    """covers: M2 — advising twice leaves exactly one `advised_by:`, the latest lens."""
    cid = _bundle(tmp_path)
    add.advise(tmp_path, cid, "sec-rev")
    add.advise(tmp_path, cid, "backend-systems")
    raw = _fm_raw(tmp_path, cid)
    assert raw.count("advised_by:") == 1, raw
    assert re.search(r"^advised_by:\s*backend-systems\s*$", raw, re.M), raw


def test_advise_refuses_unknown_persona(tmp_path):
    """covers: R:BADPERSONA — an unseeded persona refuses and stamps nothing."""
    cid = _bundle(tmp_path)
    out, note = add.advise(tmp_path, cid, "ghost")
    assert out is None and "R:BADPERSONA" in note, note
    assert "advised_by:" not in _fm_raw(tmp_path, cid)


def test_advise_refuses_non_lifecycle_node(tmp_path):
    """covers: R:NOTATASK — advising a Persona (non-lifecycle) refuses."""
    _bundle(tmp_path)
    out, note = add.advise(tmp_path, "/personas/sec-rev.md", "backend-systems")
    assert out is None and "R:NOTATASK" in note, note
