"""`neighborhood()` — one bounded, cycle-safe, deterministic walk over both edge families.

Red-first for `/tasks/graph-neighborhood.md`.

The walk is the primitive the read verb prints. Three properties are load-bearing and each has
a check that fails when it is dropped:

* **Termination is proven on the shapes that break naive walks** — a self-edge, a two-node
  cycle, and a diamond — not on the well-behaved bundle the engine happens to have today.
* **`rows is None` is a refusal and `rows == []` is an answer.** A walk that returned `[]` for a
  node that does not exist would make "no neighbours" and "no such node" the same value, which
  is the `unknown reads as clean` class this bundle keeps filing deltas about.
* **The order is total.** Every field of the row participates in the sort key, so no tie can
  fall through to dict or set iteration order and no output is undiffable.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def _set_fm(root, cid: str, key: str, value: str) -> None:
    """Replace (or append) one scalar frontmatter key on a node, as raw text."""
    path = Path(root) / cid.lstrip("/")
    text = path.read_text(encoding="utf-8")
    head, sep, rest = text.partition("\n---\n")
    lines = [ln for ln in head.splitlines() if not ln.startswith(f"{key}:")]
    lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + sep + rest, encoding="utf-8")


def _graph(root):
    return add.scan(Path(root))


@pytest.fixture
def bundle(tmp_path):
    """A milestone, three member tasks, and a receipt-shaped inbound edge."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="neighborhood fixture")
    add.new(root, "Milestone", "m-one", title="the owning milestone")
    for slug in ("t-one", "t-two", "t-three"):
        add.new(root, "Task", slug, title=slug, milestone="m-one")
    return root


# ------------------------------------------------------------------ M1/M2 · families and directions

def test_walk_covers_both_families(bundle):
    """covers: M1 — an untyped node edge and a typed concept edge both appear, distinguishably."""
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-two.md")
    path = Path(bundle) / "specs" / "method.md"
    path.write_text(path.read_text(encoding="utf-8").rstrip("\n")
                    + "\n- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)\n"
                    + "- [ADD · M2 · open · 2026-08-11] another (evidence: /x.md)\n", encoding="utf-8")
    _set_fm(bundle, "/specs/method.md", "relations", "\n  - M1 refines /specs/method.md#M2")

    rows, _note = add.neighborhood(_graph(bundle), "/specs/method.md", 2)
    assert rows, "the spec node has a relations: entry and must have a neighbourhood"
    assert {r[2] for r in rows} >= {"relation"}, f"the typed family is missing: {rows}"

    rows, _note = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 2)
    assert {r[2] for r in rows} >= {"edge"}, f"the untyped family is missing: {rows}"


def test_walk_covers_both_directions(bundle):
    """covers: M2, A2 — the probe. Outbound reaches the milestone, inbound reaches the receipt."""
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-two.md")
    rows, _note = add.neighborhood(_graph(bundle), "/tasks/t-two.md", 1)
    directions = {r[1] for r in rows}
    assert "out" in directions, (
        f"t-two declares `milestone: m-one`, so an outbound row must exist: {rows}")
    assert "in" in directions, (
        f"t-one depends_on t-two, so t-two must be reachable INBOUND — without this the walk "
        f"cannot answer 'what depends on this': {rows}")


# ------------------------------------------------------------------------- M3 · bounded

def test_expand_bounds_the_depth(bundle):
    """covers: M3, A5 — `expand` is the DEEPEST depth emitted, so 1 means immediate neighbours."""
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-two.md")
    _set_fm(bundle, "/tasks/t-two.md", "depends_on", "/tasks/t-three.md")
    for limit in (1, 2, 3):
        rows, _note = add.neighborhood(_graph(bundle), "/tasks/t-one.md", limit)
        assert rows, f"expand={limit} returned nothing on a node with edges"
        assert max(r[0] for r in rows) <= limit, \
            f"expand={limit} emitted a deeper row: {[r for r in rows if r[0] > limit]}"
    near, _ = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 1)
    far, _ = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 3)
    assert len(far) > len(near), \
        "a deeper walk returned no more rows — the bound is not doing anything"


def test_cap_has_one_home():
    """covers: M3 — the ceiling is a named constant, not a literal each caller repeats."""
    assert isinstance(add.NEIGHBORHOOD_MAX, int) and add.NEIGHBORHOOD_MAX > 0
    source = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    assert f"NEIGHBORHOOD_MAX = {add.NEIGHBORHOOD_MAX}" in source, \
        "the cap is not defined as a named constant in the engine"


# --------------------------------------------------------------------- M4 · cycle-safe

def test_a_cycle_terminates_and_visits_once(bundle):
    """covers: M4, E1, E2, R:UNBOUNDED — a self-edge and a two-node cycle both terminate."""
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-one.md")
    rows, _note = add.neighborhood(_graph(bundle), "/tasks/t-one.md", add.NEIGHBORHOOD_MAX)
    assert rows is not None, "a self-edge refused instead of walking"
    assert len([r for r in rows if r[2] == "edge" and r[3] == "depends_on"]) == 1, \
        f"a self-edge was emitted more than once: {rows}"

    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-two.md")
    _set_fm(bundle, "/tasks/t-two.md", "depends_on", "/tasks/t-one.md")
    rows, _note = add.neighborhood(_graph(bundle), "/tasks/t-one.md", add.NEIGHBORHOOD_MAX)
    assert rows is not None
    assert len(rows) == len(set(rows)), f"a cycle produced duplicate rows: {rows}"


def test_a_diamond_emits_both_edges_once(bundle):
    """covers: E3, A4 — two paths to one node: both edges shown, the node expanded once."""
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-two.md")
    _set_fm(bundle, "/tasks/t-three.md", "depends_on", "/tasks/t-two.md")
    rows, _note = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 3)
    into_two = [r for r in rows if r[6] == "/tasks/t-two.md" and r[3] == "depends_on"]
    assert len(into_two) == 2, \
        f"a diamond must show BOTH links into the shared node, once each: {into_two}"
    assert len(rows) == len(set(rows)), f"the shared node was expanded twice: {rows}"


# ------------------------------------------------------------------------ M5 · total order

def test_rows_are_totally_ordered(bundle):
    """covers: M5, A9, R:SILENTORDER — two calls over one bundle return identical rows."""
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-two.md")
    graph = _graph(bundle)
    first, _ = add.neighborhood(graph, "/tasks/t-one.md", 3)
    second, _ = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 3)
    assert first, "no rows to order"
    assert first == second, "two walks over an unchanged bundle differed"
    assert first == sorted(first), \
        "the rows are not in their own sort order, so a tie can fall through to dict order"


# -------------------------------------------------------- M6 · a refusal is not an empty answer

def test_absent_node_refuses_rather_than_empties(bundle):
    """covers: M6, R:EMPTYISUNKNOWN, E6 — None for no such node, [] for no neighbours."""
    rows, note = add.neighborhood(_graph(bundle), "/tasks/no-such-task.md", 3)
    assert rows is None, "a cid naming no node returned a list — 'no neighbours' and 'no such " \
                         "node' became the same answer"
    assert "no-such-task" in note, note

    add.new(bundle, "Persona", "lonely", title="no edges at all")
    rows, note = add.neighborhood(_graph(bundle), "/personas/lonely.md", 3)
    assert rows == [], f"a real node with no edges must answer [], not refuse: {rows}"


def test_unresolved_edge_is_emitted_not_expanded(bundle):
    """covers: A7, E4 — a dangling link is information about this node, not a silence."""
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/gone.md")
    rows, _note = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 3)
    dangling = [r for r in rows if r[3] == "depends_on" and r[6] is None]
    assert len(dangling) == 1, f"a dangling edge vanished from the view built to show links: {rows}"


def test_expand_zero_is_an_answer_not_a_refusal(bundle):
    """covers: E5 — the node exists; its neighbourhood was simply not asked for."""
    rows, note = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 0)
    assert rows == [], f"expand=0 must answer [], never refuse: {rows}"
    assert note, "an empty answer still owes the reader a note"


def test_walk_never_reads_the_cache(bundle):
    """covers: R:CACHEREAD — law 1: the walk reads the graph it is handed, never graph.json."""
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-two.md")
    add.load(bundle)                       # writes graph.json
    cache = Path(bundle) / add.CACHE_NAME
    with_cache, _ = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 3)
    assert cache.exists(), "the cache was never written, so its absence proves nothing below"
    cache.unlink()
    without_cache, _ = add.neighborhood(_graph(bundle), "/tasks/t-one.md", 3)
    assert with_cache == without_cache, "the walk changed when the cache was removed"


def test_format_states_the_walk_contract():
    """covers: A12 — stated in terms of families and directions, not of today's two families."""
    text = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "neighbourhood" in lowered or "neighborhood" in lowered, \
        "FORMAT does not document the walk at all"
    assert "both families" in lowered or "each family" in lowered, \
        "FORMAT states the walk over the two families that exist rather than over families"
