"""A relation joins the two concepts it was written between, so a walk finds it from either end.

Demonstrated on the live bundle before this task: `.add/specs/method.md` declares

    M8  refines /specs/method.md#M4
    M31 refines /specs/method.md#M4

and `add show /specs/method.md#M4` answered "related: none within 3 level(s)". The two lessons
that refine M4 were invisible from M4, while `add show /specs/method.md` rendered both as
`refines /specs/method.md` — a row reading as a self-loop, naming a file where the author wrote
a concept.

walk-truth repaired the ORIGIN end. The TARGET end ran through `_norm`, which strips the
fragment BY DESIGN, because a node edge like `needs: /specs/x.md#gives` must resolve to the
file. So the fix is scoped to the typed relation family alone: `_norm` does not move, node
edges do not move, and the containment codes `doctor` and the standalone validator report stay
byte-for-byte what they were.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

M4 = "/specs/method.md#M4"
SPEC = "/specs/method.md"


def _triangle(tmp_path):
    """Two lessons refining one concept, in one spec — the live M4/M8/M31 shape."""
    add.init(tmp_path, "code", "T")
    p = Path(tmp_path) / "specs" / "method.md"
    text = p.read_text(encoding="utf-8")
    lessons = "\n".join((
        "- [ADD · M4 · open · 2026-01-01] the refined lesson (evidence: /x.md)",
        "- [ADD · M8 · open · 2026-01-02] a refinement (evidence: /x.md)",
        "- [ADD · M31 · open · 2026-01-03] another refinement (evidence: /x.md)",
    ))
    text = text.replace("## Deltas\n", "## Deltas\n" + lessons + "\n", 1)
    text = text.replace("\n---\n", "\nrelations:\n"
                        "  - M8 refines /specs/method.md#M4\n"
                        "  - M31 refines /specs/method.md#M4\n---\n", 1)
    p.write_text(text, encoding="utf-8")
    graph = add.scan(tmp_path)
    rels = [r for r in add.relations(graph) if r[2] == "refines"]
    assert len(rels) == 2, f"fixture: two relations should parse, got {rels}"
    return tmp_path, graph


def test_a_concept_finds_what_refines_it(tmp_path):
    """covers: M3, A4, E3, A11 — from M4 the walk reaches M8 and M31, both of them."""
    _, graph = _triangle(tmp_path)
    rows, note = add.neighborhood(graph, M4, 3)
    assert rows is not None, f"a concept address was refused as a start node: {note}"
    origins = sorted(r[4] for r in rows if r[2] == "relation")
    assert origins == ["/specs/method.md#M31", "/specs/method.md#M8"], \
        f"the lessons refining M4 are not reachable from M4: {origins}"
    assert all(r[1] == "in" for r in rows if r[2] == "relation"), \
        "a lesson that refines M4 must arrive at M4 as an INBOUND edge"

    # …and the RENDER a reader actually sees (S3): both refiners, marked as inbound.
    view, note = add.show(tmp_path, M4)
    assert view is not None, note
    block = note.split("related")[1]
    assert "\u2191 refines  /specs/method.md#M8" in block, f"M8 is missing from `related:`\n{note}"
    assert "\u2191 refines  /specs/method.md#M31" in block, f"M31 is missing from `related:`\n{note}"


def test_a_relation_targets_the_concept_it_names(tmp_path):
    """covers: M1, R:FILEASCONCEPT, A3 — the row's target is the address, not the file."""
    _, graph = _triangle(tmp_path)
    rows, _ = add.neighborhood(graph, SPEC, 1)
    rel = [r for r in rows if r[2] == "relation"]
    assert len(rel) == 2, f"the file walk lost a relation: {rel}"
    for r in rel:
        assert r[7] == M4, f"a relation row names `{r[7]}` where the author wrote `{M4}`"


def test_a_file_still_reaches_all_its_relations(tmp_path):
    """covers: M4, A5, E4 — a file walk keeps its relations and costs no extra level."""
    _, graph = _triangle(tmp_path)
    rows, _ = add.neighborhood(graph, SPEC, 1)
    assert len([r for r in rows if r[2] == "relation"]) == 2, \
        "a file no longer reaches the relations declared in it"
    assert all(r[0] == 1 for r in rows if r[2] == "relation"), \
        "descending into a file's concepts cost the walk a level -> A5"
    # …and a concept walk does NOT spill into every relation its file declares (E4).
    m8, _ = add.neighborhood(graph, "/specs/method.md#M8", 1)
    assert sorted(r[7] for r in m8 if r[2] == "relation") == [M4], \
        f"the walk from M8 spilled beyond what M8 declares: {m8}"


def test_a_concept_address_starts_a_walk(tmp_path):
    """covers: M2, A8 — an unknown concept address refuses in the grammar an unknown cid gets."""
    _, graph = _triangle(tmp_path)
    ok_rows, _ = add.neighborhood(graph, M4, 1)
    assert ok_rows is not None, "a KNOWN concept address must not refuse"
    for bad in ("/specs/method.md#M99", "/specs/nope.md#M4"):
        rows, note = add.neighborhood(graph, bad, 1)
        assert rows is None, f"`{bad}` should refuse, got {rows}"
        assert "R:NOSUCHNODE" in note and "next:" in note, \
            f"the refusal for `{bad}` is not the grammar an unknown cid gets: {note!r}"


def test_node_edges_did_not_move(tmp_path):
    """covers: M5, R:NODEEDGEDRIFT, A2, E1 — only the typed relation family gained the fragment."""
    root, graph = _triangle(tmp_path)
    assert add._norm("/tasks/t.md", "/specs/x.md#gives") == "/specs/x.md", \
        "_norm moved; every node edge and every brief ref resolves through it"
    cid, _ = add.new(root, "Task", "t", title="t", scope="f.py")
    # `#decisions-that-bind` is the fragment `brief` compiles every spec through, and the one
    # ref shape that resolves today — so it is the one that proves the node-edge path unmoved.
    ncid, _, why = add.resolve(add.scan(root), "/specs/method.md#decisions-that-bind", cid)
    assert why == "heading", f"a node edge with a fragment stopped resolving: {why}"
    assert ncid == SPEC, f"a node edge's fragment leaked into its cid: {ncid}"
    # E1 — a relation with NO fragment still resolves to the file.
    sp = Path(root) / "specs" / "quality.md"
    sp.write_text(sp.read_text().replace(
        "\n---\n", "\nrelations:\n  - Q1 refines /specs/method.md\n---\n", 1), encoding="utf-8")
    bare = [r for r in add.relations(add.scan(root)) if r[1] == "Q1"]
    assert bare and bare[0][4] == SPEC, f"a fragment-less relation stopped resolving: {bare}"


def test_an_unresolvable_concept_is_not_invented(tmp_path):
    """covers: R:PHANTOMTARGET, E2, A7 — a fragment naming no lesson leaves the target alone."""
    root, _ = _triangle(tmp_path)
    p = Path(root) / "specs" / "method.md"
    p.write_text(p.read_text().replace("M31 refines /specs/method.md#M4",
                                       "M31 refines /specs/method.md#M404"), encoding="utf-8")
    graph = add.scan(root)
    rows, _ = add.neighborhood(graph, SPEC, 1)
    targets = [r[7] for r in rows if r[2] == "relation"]
    assert "/specs/method.md#M404" not in targets, \
        "the walk invented a concept address for a lesson that does not exist"
    assert M4 in targets, "the surviving real relation was lost with the phantom one"


def test_the_walk_is_still_totally_ordered(tmp_path):
    """covers: A9 — two walks over an unchanged bundle are byte-identical."""
    _, graph = _triangle(tmp_path)
    a = add.neighborhood(graph, SPEC, 3)
    b = add.neighborhood(add.scan(Path(graph[SPEC]["path"]).parent.parent), SPEC, 3)
    assert a[0] == b[0], "two walks over an unchanged bundle disagree"
    assert len(a[0]) > 1, "a single-row walk cannot demonstrate an order"


def test_format_says_what_a_relation_row_means():
    """covers: M6, A10, A12 — §11 describes `src` and `target` for a relation row."""
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    parts = fmt.split("## \u00a711 ")
    assert len(parts) == 2, "FORMAT.md has no §11 heading — the guard would be vacuous"
    s11 = parts[1].split("\n## ")[0]
    assert "concept address" in s11, \
        "§11 does not say a relation's target is a concept address"
    assert "file" in s11 and "no fragment" in s11.replace("no  fragment", "no fragment"), \
        "§11 does not say what a relation with no fragment resolves to -> A15"
