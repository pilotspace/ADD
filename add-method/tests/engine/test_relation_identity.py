"""A relation is identified by the lesson that declared it.

Red-first for `/tasks/relation-identity-in-the-walk.md`.

`relations()` returns `(src_cid, src_id, rel, ref, target)` — `src_id` being the delta id, the
only field that tells two relations declared by two different lessons apart. `neighborhood()`
threw it away and dedupped on `(family, label, src, ref, target)`, so two lessons refining one
target became ONE row. It is live: `.add/specs/method.md` declares `M8 refines #M4` and
`M31 refines #M4`, and the walk emitted one.

FORMAT §3.4 promises one EDGE emitted once. Two edges are not one edge — the clause is about the
same link seen from both ends, and the code generalised it into "any two relations agreeing on
rel and ref are one fact", which is false.

Every row now carries `origin`: the address of the concept that DECLARED the edge — a lesson
address for a relation, the node's own cid for a node edge. It is an ADDED key, not a redefined
`src`, so a consumer that joined on `src` keeps working.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

TWO = ("relations:\n"
       "  - M8 refines /specs/method.md#M4\n"
       "  - M31 refines /specs/method.md#M4\n")
IDLESS = "relations:\n  - refines /specs/method.md#M4\n"


def _spec(root, lens, rel_block):
    """Put a `relations:` block in a spec's frontmatter and hand back its cid."""
    p = root / "specs" / f"{lens}.md"
    text = p.read_text(encoding="utf-8")
    head, sep, body = text.partition("\n---\n")
    p.write_text(head.rstrip("\n") + "\n" + rel_block + sep + body, encoding="utf-8")
    return f"/specs/{lens}.md"


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / ".add"
    add.init(root, profile="code", title="relation identity fixture")
    add.new(root, "Milestone", "m-one", title="a milestone")
    add.new(root, "Task", "t-one", title="a task", milestone="m-one")
    return root


def _rel_rows(rows):
    return [r for r in rows if r[2] == "relation"]


def test_two_lessons_one_target_emit_two_rows(bundle):
    """M1, R:COLLAPSE, E1 — the live shape: two relations agreeing on rel and ref."""
    cid = _spec(bundle, "method", TWO)
    declared = [r for r in add.relations(add.scan(bundle)) if r[0] == cid]
    assert len(declared) == 2, f"the fixture did not declare two relations: {declared}"
    rows, _note = add.neighborhood(add.scan(bundle), cid, 1)
    out = [r for r in _rel_rows(rows) if r[1] == "out"]
    assert len(out) == 2, \
        f"two declared relations collapsed into {len(out)} row(s) — R:COLLAPSE\n{out}"


def test_every_row_names_its_declaring_concept(bundle):
    """M2, A6, E4 — `origin` on every row: a lesson address for a relation, `src` otherwise."""
    cid = _spec(bundle, "method", TWO)
    rows, _ = add.neighborhood(add.scan(bundle), cid, 2)
    assert rows, "the fixture produced no rows, so this proves nothing"
    for r in rows:
        assert len(r) == 8, f"a row carries no origin field: {r}"
    origins = {r[4] for r in _rel_rows(rows) if r[1] == "out"}
    assert origins == {"/specs/method.md#M8", "/specs/method.md#M31"}, \
        f"the declaring lessons are not named: {origins}"
    # A spec carries no node edges, so the `origin == src` half is measured where they live.
    node_rows = [r for r in add.neighborhood(add.scan(bundle), "/tasks/t-one.md", 2)[0]
                 if r[2] == "edge"]
    assert node_rows, "no node edge in the fixture, so the `origin == src` half proves nothing"
    for r in node_rows:
        assert r[4] == r[5], f"a node edge invented an origin: origin={r[4]} src={r[5]}"


def test_one_edge_is_still_emitted_once(bundle):
    """M3, R:DOUBLEVISIT, E2 — the same link seen from both ends is still ONE fact."""
    graph = add.scan(bundle)
    rows, _ = add.neighborhood(graph, "/tasks/t-one.md", 5)
    keys = [(r[2], r[3], r[4], r[6], r[7]) for r in rows]
    assert keys, "no rows, so no duplication could be observed"
    assert len(keys) == len(set(keys)), \
        f"an edge was emitted twice: {[k for k in keys if keys.count(k) > 1]}"


def test_walk_reconciles_with_relations(bundle):
    """M6, R:PINNEDNUMBER — two COMPUTED values compared; no literal to go stale."""
    cid = _spec(bundle, "method", TWO)
    graph = add.scan(bundle)
    declared = [r for r in add.relations(graph) if r[0] == cid and r[2] is not None]
    rows, _ = add.neighborhood(graph, cid, 1)
    walked = [r for r in _rel_rows(rows) if r[1] == "out"]
    assert declared, "the fixture declared no relations — the reconciliation is vacuous"
    assert len(walked) == len(declared), \
        f"the walk emits {len(walked)} of {len(declared)} declared relations"


def test_format_pins_the_declaring_key():
    """M4 — §11 names `origin`, and §3.4 states identity in terms of the declarer."""
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    assert "`origin`" in fmt, "FORMAT.md does not pin the `origin` edge key"
    s34 = fmt.split("### §3.4")[1].split("\n## ")[0]
    assert "declar" in s34.lower(), \
        "§3.4 still states edge identity without reference to the declaring concept"


def test_prose_render_names_the_lesson(bundle):
    """M5, A3, A9 — two otherwise-identical rows are distinguishable to a human."""
    cid = _spec(bundle, "method", TWO)
    _view, note = add.show(bundle, cid, 1)
    assert "M8" in note and "M31" in note, \
        f"the human render cannot tell the two relations apart:\n{note}"


def test_an_idless_relation_is_malformed_not_degraded(bundle):
    """A5, E3 — the probe refuted the assumption: the id is MANDATORY, so there is no degrade.

    Authoring took an id-less relation for a legacy head that would degrade to the file address,
    the way `delta_address` degrades. `parse_relation` says otherwise, so `origin` always carries
    an id and a degrade branch would be code for a state no producer can create.
    """
    assert add.parse_relation("refines /specs/method.md#M4") == (
        None, None, "refines /specs/method.md#M4"), "the relation grammar now admits no id"
    cid = _spec(bundle, "quality", IDLESS)
    rows, _ = add.neighborhood(add.scan(bundle), cid, 1)
    assert not _rel_rows(rows), \
        f"a malformed relation reached the walk: {_rel_rows(rows)}"
    # Floor: a WELL-FORMED relation in the same file does produce a row, so the emptiness above
    # is the grammar rejecting the entry and not the fixture failing to write one.
    good = _spec(bundle, "domain", "relations:\n  - D1 refines /specs/method.md#M4\n")
    rows, _ = add.neighborhood(add.scan(bundle), good, 1)
    assert _rel_rows(rows), "the floor failed: no relation parses at all in this fixture"


def test_row_order_is_total_and_stable(bundle):
    """A7, A8 — two walks over an unchanged bundle emit identical rows, split rows included."""
    cid = _spec(bundle, "method", TWO)
    first, _ = add.neighborhood(add.scan(bundle), cid, 3)
    second, _ = add.neighborhood(add.scan(bundle), cid, 3)
    assert first and len(_rel_rows(first)) >= 2, "too few rows to observe an ordering"
    assert first == second, "two walks over an unchanged bundle disagree"
