"""Red suite for e2 `compile-graph` — the engine's one graph.

One test per Must / Reject of tasks/compile-graph, carrying the same `covers:` keys as that
task's CHECKS section. Every test must fail for the right reason before the code exists.

The subject is the graph layer of `add/scripts/add.py`, which does not exist yet: at red time
every test here fails on a missing attribute.
"""

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


# ------------------------------------------------------------------ a bundle to compile


def node(fm: str, body: str = "") -> str:
    return f"---\n{fm}\n---\n{body}"


@pytest.fixture
def bundle(tmp_path):
    """A minimal but honest bundle: a milestone, two tasks, a spec, and one trap per Reject."""
    (tmp_path / "tasks").mkdir()
    (tmp_path / "milestones").mkdir()
    (tmp_path / "specs").mkdir()

    (tmp_path / "index.md").write_text(node(
        "type: Project\ntitle: Test bundle\nabf_version: 1.3\n"
        # R:GUESS traps — path-shaped values that are NOT edges
        "persona_corpus: ../elsewhere/personas\n"
        "sensitive_paths:\n  - templates/task.md.tmpl\n"
    ))
    (tmp_path / "milestones" / "m1.md").write_text(node(
        "type: Milestone\ntitle: M1\nstatus: active\n"
        "tasks:\n  - /tasks/a.md\n  - /tasks/b.md\n"
    ))
    # `a` is done and publishes a frozen interface; `#gives` must resolve to the KEY.
    # It also has a `## Gives` heading, so M2's ordering is actually exercised.
    (tmp_path / "tasks" / "a.md").write_text(node(
        "type: Task\ntitle: A\nstatus: done\nmilestone: /milestones/m1.md\n"
        "gives:\n  - the frontmatter answer\n"
        "scope:\n  - src/whatever.py\n",
        "## Gives\n\nthe body answer — must lose to the frontmatter key\n\n"
        "## Decisions that bind\n\nno cache is authoritative\n",
    ))
    (tmp_path / "tasks" / "b.md").write_text(node(
        "type: Task\ntitle: B\nstatus: build\nmilestone: /milestones/m1.md\n"
        "depends_on:\n  - /tasks/a.md\n"
        "needs:\n  - /tasks/a.md#gives\n  - /specs/s.md#decisions-that-bind\n  - /tasks/a.md#nope\n"
    ))
    (tmp_path / "specs" / "s.md").write_text(node(
        "type: Spec\ntitle: S\nstatus: done\n",
        "## Decisions that bind\n\n- the files are the database\n",
    ))
    return tmp_path


# ------------------------------------------------------------------ scan tiers (M1)


def test_scan_is_t0_only(bundle):
    """covers: M1, R:BODYSCAN — the graph is built without reading a single body."""
    g = add.scan(bundle)
    for cid, n in g.items():
        assert n["body"] == "", f"{cid} carried a body into the graph"
        assert n["card"] == "", f"{cid} carried a card into the graph"


def test_scan_keys_are_bundle_absolute(bundle):
    """covers: M1 — concept IDs are bundle-absolute paths (OKF §2), not filesystem paths."""
    g = add.scan(bundle)
    assert "/tasks/a.md" in g
    assert "/milestones/m1.md" in g
    assert all(cid.startswith("/") for cid in g), "a cid was not bundle-absolute"
    assert not any(str(bundle) in cid for cid in g), "an absolute filesystem path leaked into a cid"


# ------------------------------------------------------------------ edges (M3)


def test_edges_only_from_allowlist(bundle):
    """covers: M3, R:GUESS — `scope:` and `persona_corpus:` are paths, not bundle edges."""
    refs = [e[2] for e in add.edges(add.scan(bundle))]
    assert not any("whatever.py" in r for r in refs), "scope: was mis-read as an edge"
    assert not any("personas" in r for r in refs), "persona_corpus: was mis-read as an edge"
    assert not any("task.md.tmpl" in r for r in refs), "a template path was mis-read as an edge"


def test_edges_are_typed(bundle):
    """covers: M3 — an edge carries the key it came from; `tasks` and `needs` are not the same."""
    es = add.edges(add.scan(bundle))
    kinds = {(src, key, ref) for src, key, ref, _ in es}
    assert ("/tasks/b.md", "depends_on", "/tasks/a.md") in kinds
    assert ("/milestones/m1.md", "tasks", "/tasks/a.md") in kinds
    assert ("/tasks/b.md", "needs", "/tasks/a.md#gives") in kinds


# ------------------------------------------------------- the fragment grammar (M2, §3.3)


def test_resolve_frontmatter_key_wins(bundle):
    """covers: M2 — `a.md` has BOTH a `gives:` key and a `## Gives` heading. The key wins."""
    g = add.scan(bundle)
    cid, value, why = add.resolve(g, "/tasks/a.md#gives")
    assert cid == "/tasks/a.md"
    assert why == "frontmatter"
    assert "frontmatter answer" in str(value)
    assert "body answer" not in str(value), "the ordered grammar resolved two ways"


def test_resolve_falls_back_to_heading_slug(bundle):
    """covers: M2 — no `decisions_that_bind` key exists, so the heading slug is tried."""
    g = add.scan(bundle)
    cid, value, why = add.resolve(g, "/specs/s.md#decisions-that-bind")
    assert cid == "/specs/s.md"
    assert why == "heading"
    assert "files are the database" in str(value)


def test_resolve_unmatched_is_info(bundle):
    """covers: M2 — matching neither namespace reports; it does not raise."""
    g = add.scan(bundle)
    cid, value, why = add.resolve(g, "/tasks/a.md#nope")
    assert why == "edge_unresolved"
    assert value is None


def test_resolve_out_of_bundle_does_not_raise(bundle):
    """covers: M2, M5 — a ref with no target in the bundle is a return value, never an exception."""
    g = add.scan(bundle)
    cid, value, why = add.resolve(g, "/tasks/ghost.md#gives")
    assert why in ("edge_unresolved", "edge_out_of_bundle")
    assert value is None


# --------------------------------------------------------- derived activity (M4, §3.4)


def test_active_is_derived_from_status(bundle):
    """covers: M4, R:POINTER — flipping one status changes `active()` with no other write."""
    g = add.scan(bundle)
    assert "/tasks/b.md" in add.active(g)
    assert "/tasks/a.md" not in add.active(g), "a done task is not active"

    p = bundle / "tasks" / "b.md"
    n = add.read(p, "T0")
    add.write(p, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")
    assert "/tasks/b.md" not in add.active(add.scan(bundle))


def test_no_active_pointer_anywhere(bundle):
    """covers: M4, R:POINTER — no node and no cache key stores what is derivable."""
    add.load(bundle)  # materialise the cache if there is one
    for path in bundle.rglob("*"):
        if not path.is_file():
            continue
        assert "active_task" not in path.read_text(errors="replace"), f"pointer found in {path.name}"
        assert "active_milestone" not in path.read_text(errors="replace")


def test_ready_excludes_blocked(bundle):
    """covers: M4 — `b` depends on `a`. With `a` done, `b` is ready; reopen `a` and it is not."""
    assert "/tasks/b.md" in add.ready(add.scan(bundle))

    p = bundle / "tasks" / "a.md"
    n = add.read(p, "T0")
    add.write(p, f"---\n{add.set_key(n['raw'], 'status', 'build')}\n---\n{n['body']}")
    assert "/tasks/b.md" not in add.ready(add.scan(bundle)), "a blocked task was offered as ready"


# ------------------------------------------------------------ cycles (M5, R:CYCLECRASH)


def test_cycles_reported_not_raised(bundle):
    """covers: M5, R:CYCLECRASH — a 3-cycle is returned as data, not thrown."""
    for a, b in (("c", "d"), ("d", "e"), ("e", "c")):
        (bundle / "tasks" / f"{a}.md").write_text(node(
            f"type: Task\ntitle: {a.upper()}\nstatus: build\ndepends_on:\n  - /tasks/{b}.md\n"))
    found = add.cycles(add.scan(bundle))
    assert found, "a 3-cycle was not reported"
    assert any({"/tasks/c.md", "/tasks/d.md", "/tasks/e.md"} <= set(c) for c in found)


def test_self_edge_terminates(bundle):
    """covers: M5, R:CYCLECRASH — a node depending on itself must not hang or recurse away."""
    (bundle / "tasks" / "loop.md").write_text(node(
        "type: Task\ntitle: Loop\nstatus: build\ndepends_on:\n  - /tasks/loop.md\n"))
    found = add.cycles(add.scan(bundle))
    assert any("/tasks/loop.md" in c for c in found)


# ------------------------------------------------- the cache is not the truth (M6)


def test_cache_never_authoritative(bundle):
    """covers: M6, R:CACHEAUTH — a deliberately WRONG cache must change no answer.

    This is the test that matters: a cache violation looks like a performance win, so the
    suite plants a lie on disk rather than merely deleting the file.
    """
    truth = add.load(bundle)
    cache = bundle / "graph.json"
    cache.write_text(json.dumps({
        "nodes": {"/tasks/ghost.md": {"fm": {"type": "Task", "status": "build"}}},
        "edges": [],
    }))
    assert add.load(bundle) == truth, "graph.json overrode the files"
    assert "/tasks/ghost.md" not in add.load(bundle)
    assert "/tasks/a.md" in add.load(bundle)


def test_corrupt_cache_falls_back(bundle):
    """covers: M6 — an unparseable cache is the engine's problem, never the caller's."""
    truth = add.load(bundle)
    (bundle / "graph.json").write_text("{ not json at all")
    assert add.load(bundle) == truth


# ---------------------------------------------------------- the live bundle (M1, M3)


@pytest.mark.skip(reason="dogfood: asserts add-skill's own dev-bundle magic numbers (>=25 nodes); re-point when add-skill-2 grows its own bundle")
def test_live_bundle_compiles():
    """covers: M1, M3 — this repo's own bundle compiles, and agrees with the M0 oracle.

    The validator is the conformance floor for all of M1. If the engine and the validator
    disagree about how many edges this bundle has, one of them is wrong about the format.
    """
    g = add.scan(REPO / ".add")
    assert len(g) >= 25, f"expected the whole bundle, saw {len(g)}"
    assert not add.cycles(g), "the live bundle has a dependency cycle"

    import subprocess
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate_bundle.py"), str(REPO / ".add")],
        capture_output=True, text=True).stdout
    reported = int([w for w in out.split("·")[1].split() if w.isdigit()][0])
    assert len(add.edges(g)) == reported, f"engine and validator disagree on edge count: {reported}"
