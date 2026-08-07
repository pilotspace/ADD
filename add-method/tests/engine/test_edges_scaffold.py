"""The Task scaffold offers an optional EDGES section (C7, task 2).

`new Task` scaffolds a `## EDGES` section with a placeholder edge — prompting authors to enumerate
edge cases — but the placeholder is inert: `edges_of` excludes it, so a freshly scaffolded task owes
no edge coverage and gates exactly as before.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def test_new_task_has_edges_section(tmp_path):
    """covers: M1 — a freshly created Task body has a `## EDGES` heading with a placeholder edge."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    body = add.read(tmp_path / cid.lstrip("/"), "T2")["body"]
    assert "## EDGES" in body, body
    assert "E1" in body


def test_scaffolded_edge_is_no_obligation(tmp_path):
    """covers: M2, R:SCAFFOLDOBLIGATION, E1 — the fresh node has no real edge."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    node = add.read(tmp_path / cid.lstrip("/"), "T2")
    assert add.edges_of(node) == [], "the scaffold placeholder must not be an obligating edge"
