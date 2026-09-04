"""`add search` — three node-scoped filters beside the free-text grammar.

Red-first for `/tasks/search-structured-filters.md`.

Two shapes measured on the live bundle drive most of these checks, and both are the same
failure: a surface that looks wired and answers wrongly.

* `search()` excludes `Run` nodes WHOLESALE — right for free text, where 122 receipts would
  drown the index, and wrong for an explicit `--type Run`, which would answer zero (R:HIDDENTYPE).
* 135 of 220 nodes carry no `status:` at all. Treating absent as a wildcard would return most
  of the bundle for every `--status` query, so absent matches nothing.

The exclusion report is not decoration: a filter that silently drops the delta half of the
index reports a smaller number, and a smaller number reads as success (R:SILENT_DROP).
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    """Two milestones, tasks split across them, a status-less node, a receipt, and a delta."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="filter fixture")
    add.new(root, "Milestone", "m-one", title="interval milestone")
    add.new(root, "Milestone", "m-two", title="other milestone")
    add.new(root, "Task", "t-one", title="interval task one", milestone="m-one")
    add.new(root, "Task", "t-two", title="interval task two", milestone="m-one")
    add.new(root, "Task", "t-three", title="interval task three", milestone="m-two")
    add.new(root, "Persona", "p-one", title="interval persona")     # carries no status:
    add.learn(root, "method", "an interval lesson worth filing", evidence="/tasks/t-one.md")

    receipt = root / "tasks" / "t-one.d" / "runs"
    receipt.mkdir(parents=True, exist_ok=True)
    (receipt / "1.md").write_text(
        "---\ntype: Run\ntitle: interval receipt\ntask: /tasks/t-one.md\n---\n\n## CARD\n",
        encoding="utf-8")
    return root


def _addresses(hits):
    return sorted(h[0] for h in hits)


# --------------------------------------------------------------------- M1 · select by field

def test_each_filter_selects_by_its_field(bundle):
    """covers: M1, A2 — each flag alone returns exactly the nodes carrying that value."""
    hits, _note = add.search(bundle, None, type="Milestone")
    assert _addresses(hits) == ["/milestones/m-one.md", "/milestones/m-two.md"], hits

    hits, _note = add.search(bundle, None, milestone="m-one")
    assert _addresses(hits) == ["/tasks/t-one.md", "/tasks/t-two.md"], hits

    hits, _note = add.search(bundle, None, status="direction")
    assert hits, "every scaffolded Task and Milestone is `direction`"
    assert all(a.startswith(("/tasks/", "/milestones/")) for a in _addresses(hits)), hits


def test_filters_and_together(bundle):
    """covers: M1, E5 — the intersection, and a subset of either filter alone."""
    both, _ = add.search(bundle, None, type="Task", milestone="m-one")
    by_type, _ = add.search(bundle, None, type="Task")
    by_ms, _ = add.search(bundle, None, milestone="m-one")
    assert _addresses(both) == ["/tasks/t-one.md", "/tasks/t-two.md"], both
    assert set(_addresses(both)) < set(_addresses(by_type)), "not a subset of the type filter"
    assert set(_addresses(both)) <= set(_addresses(by_ms)), "not a subset of the milestone filter"


def test_a_filter_alone_is_a_complete_ask(bundle):
    """covers: M2, A5 — no query, one filter, real hits."""
    hits, note = add.search(bundle, None, type="Task")
    assert hits, f"a filter-only ask returned nothing: {note}"
    assert len(hits) == 3, _addresses(hits)


def test_an_ask_that_names_nothing_still_refuses(bundle):
    """covers: M3, R:REGRESS — making the positional optional must not re-open the hole."""
    for query in (None, "", "   "):
        hits, note = add.search(bundle, query)
        assert hits is None, f"an empty ask answered instead of refusing: {query!r} -> {note}"
        assert "EMPTYQUERY" in note, note


# ------------------------------------------------------- M4 · an unknown must never read clean

def test_off_taxonomy_type_refuses_and_names_the_taxonomy(bundle):
    """covers: M4, R:UNKNOWNCLEAN, E7 — a typo refuses; a real-but-empty type answers []."""
    hits, note = add.search(bundle, None, type="Taks")
    assert hits is None, "an off-taxonomy type returned a hit list, so a typo reads as no matches"
    assert "Task" in note and "Milestone" in note, f"the refusal does not name the taxonomy: {note}"

    empty, _note = add.search(bundle, None, type="Prompt")
    assert empty == [], f"a real type with no members must answer [], not refuse: {empty}"


def test_type_filter_is_case_insensitive(bundle):
    """covers: E1 — lower case resolves to the canonical taxonomy form."""
    lower, _ = add.search(bundle, None, type="task")
    canonical, _ = add.search(bundle, None, type="Task")
    assert lower and _addresses(lower) == _addresses(canonical)


def test_explicit_run_type_lifts_the_receipt_exclusion(bundle):
    """covers: R:HIDDENTYPE, E2 — an explicit ask is not the blanket free-text case."""
    runs, _note = add.search(bundle, None, type="Run")
    assert _addresses(runs) == ["/tasks/t-one.d/runs/1.md"], (
        f"`--type Run` answered zero because the free-text exclusion still applied: {runs}")
    free, _note = add.search(bundle, "interval")
    assert not any("runs/" in a for a in _addresses(free)), \
        "an unfiltered search must still keep receipts out of the index"


def test_milestone_accepts_a_slug_or_a_cid(bundle):
    """covers: M5, E4 — one value, two spellings."""
    by_slug, _ = add.search(bundle, None, milestone="m-one")
    by_cid, _ = add.search(bundle, None, milestone="/milestones/m-one.md")
    assert by_slug and _addresses(by_slug) == _addresses(by_cid)


def test_absent_status_never_matches(bundle):
    """covers: A7 — 135 of 220 live nodes carry no status; absent is not a wildcard."""
    persona = add.scan(Path(bundle))["/personas/p-one.md"]["fm"]
    assert not persona.get("status"), "the fixture persona must carry no status:"
    for state in ("direction", "done", ""):
        hits, _note = add.search(bundle, None, type="Persona", status=state or "direction")
        assert "/personas/p-one.md" not in _addresses(hits), \
            f"a status-less node matched --status {state!r}"


# ------------------------------------------------------------ M6 · the exclusion is reported

def test_delta_exclusion_is_reported(bundle):
    """covers: M6, R:SILENT_DROP, A6 — the removed hits are counted out loud."""
    unfiltered, _note = add.search(bundle, "interval")
    deltas = [a for a in _addresses(unfiltered) if a.startswith("/specs/")]
    assert deltas, "the fixture delta is not in the unfiltered index, so nothing is excluded below"

    hits, note = add.search(bundle, "interval", type="Task")
    assert not [a for a in _addresses(hits) if a.startswith("/specs/")], hits
    assert str(len(deltas)) in note and "delta" in note.lower(), (
        f"the filter removed {len(deltas)} delta hit(s) and the note does not say so: {note}")


def test_no_exclusion_line_when_nothing_excluded(bundle):
    """covers: A9 — a line reading zero on every search trains the reader to skip it."""
    hits, note = add.search(bundle, "interval")
    assert hits and note.strip(), \
        "no note to inspect — the absence of a line in an empty string proves nothing"
    assert "excluded" not in note.lower(), f"an unfiltered search carries an exclusion line: {note}"


def test_unmatched_status_names_what_exists(bundle):
    """covers: A12, E3 — a typo and an empty slice must not look identical."""
    hits, note = add.search(bundle, None, status="nonesuch")
    assert hits == [], hits
    assert "direction" in note, \
        f"a zero-hit status search does not say which statuses exist: {note}"


# --------------------------------------------------------------- M7 · today's behaviour intact

def test_unfiltered_search_is_unchanged(bundle):
    """covers: M7, A10 — pinned by VALUE, not by re-calling the function under test."""
    hits, note = add.search(bundle, "interval")
    assert _addresses(hits) == [
        "/milestones/m-one.md", "/personas/p-one.md", "/specs/method.md#M1",
        "/tasks/t-one.md", "/tasks/t-three.md", "/tasks/t-two.md",
    ], _addresses(hits)
    assert note.startswith("6 hits for \"interval\""), note
    # NOT alphabetical: `search` orders by TIER — deltas, then node fields, then CARD goals —
    # so asserting `sorted(hits)` would pin an order the function never promised. What A10
    # claims is that filters REMOVE rows and never reorder the survivors.
    assert hits[0][1].startswith("delta:"), f"the tier order changed: {hits[0]}"
    subset, _ = add.search(bundle, "interval", type="Task")
    assert subset == [h for h in hits if h in subset], "filtering reordered the surviving rows"


def test_as_of_and_filter_do_not_double_report(bundle):
    """covers: E6 — one exclusion line, never two counts of the same removed hits."""
    _hits, note = add.search(bundle, "interval", as_of="2026-09-04", type="Task")
    assert "carry no validity interval" not in note, (
        "the --as-of unjudgeable line fired for hits the filter had already removed: " + note)
    assert note.count("\u2014 ") == 1, f"two exclusion lines for one removal: {note}"
    assert "delta" in note.lower(), note
