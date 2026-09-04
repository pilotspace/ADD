"""`milestone:` — the membership edge, traversable in both oracles and in neither adjacency.

Red-first for `/tasks/milestone-membership-is-an-edge.md`.

The defect this file pins was measured on the live bundle at 220 nodes: `milestone:` is a member
of `EDGE_KEYS` and is declared on 45 nodes, and `edges()` yielded ZERO edges for it — every value
is a bare slug and both oracles skip any ref without `.md`. A key in the allowlist that can never
produce an edge is a phantom: it reads as wired and traverses nothing.

Three disciplines are inherited from `test_typed_relations.py` and hold here:

* **The validator is a SUBPROCESS, never an import** — importing it would make every parity
  claim true by construction.
* **Every parity claim is asserted across BOTH oracles in ONE test.** Two per-oracle tests each
  pass while the two tools disagree.
* **The floor comes first.** Each test below asserts its SUBJECT exists before it asserts
  anything about the subject's absence, so no assertion can degrade to `0 == 0` and pass over an
  empty bundle.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

VALIDATOR = REPO / "scripts" / "validate_bundle.py"


# ------------------------------------------------------------------------------ helpers

def _validator(root) -> dict:
    """The M0 oracle: `{findings, exit}`. A subprocess, never an import."""
    done = subprocess.run([sys.executable, str(VALIDATOR), str(root), "--json"],
                          capture_output=True, text=True, timeout=60)
    return {"findings": json.loads(done.stdout)["findings"], "exit": done.returncode}


def _codes(findings, code) -> list:
    return [f for f in findings if f["code"] == code]


def _set_fm(root, cid: str, key: str, value: str) -> Path:
    """Replace (or append) one scalar frontmatter key on a node, as raw text.

    Raw text deliberately: the contract under test is what the two PARSERS make of the value a
    human types, so a helper that round-tripped through a serialiser would test the serialiser.
    """
    path = Path(root) / cid.lstrip("/")
    text = path.read_text(encoding="utf-8")
    head, sep, rest = text.partition("\n---\n")
    lines = [ln for ln in head.splitlines() if not ln.startswith(f"{key}:")]
    lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + sep + rest, encoding="utf-8")
    return path


def _membership(root) -> list:
    """Every `(src, ref, target)` the engine yields under the `milestone` key."""
    graph = add.scan(Path(root))
    return [(s, r, t) for s, k, r, t in add.edges(graph) if k == "milestone"]


@pytest.fixture
def bundle(tmp_path):
    """A real bundle with one milestone and two member tasks, built by the engine."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="membership fixture")
    add.new(root, "Milestone", "m-one", title="the owning milestone")
    add.new(root, "Task", "t-one", title="a member", milestone="m-one")
    add.new(root, "Task", "t-two", title="another member", milestone="m-one")
    return root


# --------------------------------------------------------------- M1 · a slug becomes a target

def test_milestone_slug_resolves_to_a_milestone_node(bundle):
    """covers: M1 — a bare-slug `milestone:` yields an edge into `/milestones/`."""
    found = _membership(bundle)
    assert found, ("no `milestone` edge at all — the key is in EDGE_KEYS and declared on both "
                   "fixture tasks, so an empty result is the phantom-key defect itself")
    targets = {src: target for src, _ref, target in found}
    assert targets == {"/tasks/t-one.md": "/milestones/m-one.md",
                       "/tasks/t-two.md": "/milestones/m-one.md"}, targets


def test_second_oracle_resolves_membership_identically(bundle):
    """covers: M1, R:DRIFT — one value, one target, both readers.

    Asserted on the DANGLING case, because that is the only membership outcome either oracle
    reports out loud: a resolving edge is silent in both, so a parity test over resolving edges
    alone would pass while one oracle skipped the key entirely.
    """
    _set_fm(bundle, "/tasks/t-two.md", "milestone", "no-such-milestone")

    engine = {src: target for src, _ref, target in _membership(bundle)}
    assert engine.get("/tasks/t-one.md") == "/milestones/m-one.md", \
        f"the resolving arm regressed: {engine}"
    assert engine.get("/tasks/t-two.md") is None, \
        f"a milestone that does not exist must not resolve: {engine}"

    unresolved = _codes(_validator(bundle)["findings"], "edge_unresolved")
    detail = " ".join(f["detail"] for f in unresolved)
    assert "no-such-milestone" in detail, (
        "the second oracle is silent about a dangling membership the engine reports "
        f"unresolved — the two readers disagree: {unresolved}")
    assert "m-one" not in detail, \
        f"the second oracle reports a membership the engine resolves: {unresolved}"


def test_both_membership_spellings_name_one_target(bundle):
    """covers: M2, E2 — the bare slug and the explicit `.md` ref land on the same cid."""
    _set_fm(bundle, "/tasks/t-two.md", "milestone", "/milestones/m-one.md")
    targets = {src: target for src, _ref, target in _membership(bundle)}
    assert targets.get("/tasks/t-one.md") == targets.get("/tasks/t-two.md") \
        == "/milestones/m-one.md", (
        f"one milestone written two ways resolved two ways: {targets}")


# ------------------------------------------------- M3 · and enters no dependency adjacency

def test_membership_never_enters_cycle_adjacency(bundle):
    """covers: M3, E5, R:SILENTCYCLE — a Task/Milestone loop is not a dependency cycle.

    The floor is the loop itself: both directions are asserted to RESOLVE before the absence of
    a cycle is asserted, so a bundle where the membership edge silently vanished cannot pass
    this test by having no loop to find.
    """
    _set_fm(bundle, "/milestones/m-one.md", "tasks", "/tasks/t-one.md")
    graph = add.scan(Path(bundle))
    pairs = {(s, k, t) for s, k, _r, t in add.edges(graph)}
    assert ("/tasks/t-one.md", "milestone", "/milestones/m-one.md") in pairs, \
        "the Task -> Milestone leg is missing, so there is no loop to prove acyclic"
    assert ("/milestones/m-one.md", "tasks", "/tasks/t-one.md") in pairs, \
        "the Milestone -> Task leg is missing, so there is no loop to prove acyclic"

    assert add.cycles(graph) == [], (
        "membership entered the dependency adjacency and invented a Task/Milestone cycle — "
        "45 of them on the live bundle")


def test_cycles_still_finds_a_real_dependency_cycle(bundle):
    """covers: M3, R:SILENTCYCLE — the guard above is not vacuous.

    Without this, narrowing `cycles()` to nothing at all would make the previous test pass.
    """
    _set_fm(bundle, "/tasks/t-one.md", "depends_on", "/tasks/t-two.md")
    _set_fm(bundle, "/tasks/t-two.md", "depends_on", "/tasks/t-one.md")
    found = add.cycles(add.scan(Path(bundle)))
    assert found == [["/tasks/t-one.md", "/tasks/t-two.md"]], (
        f"a real depends_on cycle is no longer reported, so the acyclic claim above proves "
        f"nothing: {found}")


def test_wave_levels_unchanged_by_membership(bundle):
    """covers: M3, E6 — two independent members stay ONE parallel level."""
    levels, _note = add.wave(bundle, "m-one")
    assert levels, "no wave plan at all — the milestone has two member tasks"
    assert levels == [["t-one", "t-two"]], (
        f"membership became a dependency and serialised an antichain: {levels}")


# ---------------------------------------------------- R:GENERALISE · one key, one directory

def test_only_the_milestone_key_resolves_a_bare_slug(bundle):
    """covers: R:GENERALISE, E1, A2 — the probe, enumerated over the WHOLE allowlist.

    Enumerated from `add.EDGE_KEYS` rather than from a hand list: a rule that quantifies over a
    set must have its check enumerate that set, or the next key added is silently uncovered.
    """
    assert "milestone" in add.EDGE_KEYS, "the key under test left the allowlist"
    resolving = []
    for key in add.EDGE_KEYS:
        _set_fm(bundle, "/tasks/t-one.md", key, "m-one")
        graph = add.scan(Path(bundle))
        if any(s == "/tasks/t-one.md" and k == key and t for s, k, _r, t in add.edges(graph)):
            resolving.append(key)
        _set_fm(bundle, "/tasks/t-one.md", key, "")
    assert resolving == ["milestone"], (
        f"a bare slug resolved under {resolving} — only `milestone` names an implied directory; "
        f"every other key may point at more than one node type")


def test_membership_value_cannot_escape_the_bundle(bundle):
    """covers: R:ESCAPE, E4 — containment is decided on the mapped target, in both oracles."""
    _set_fm(bundle, "/tasks/t-one.md", "milestone", "../../outside")
    targets = [t for _s, _r, t in _membership(bundle)]
    assert all(t is None or t.startswith("/milestones/") for t in targets), (
        f"a membership value escaped its directory: {targets}")
    escapes = _codes(_validator(bundle)["findings"], "edge_out_of_bundle")
    assert not escapes or all("outside" not in f["detail"] for f in escapes), escapes


def test_missing_milestone_is_unresolved_not_error(bundle):
    """covers: A5, E3 — a named-but-missing milestone is info, never an error, never a raise."""
    _set_fm(bundle, "/tasks/t-one.md", "milestone", "archived-long-ago")
    report = _validator(bundle)
    unresolved = _codes(report["findings"], "edge_unresolved")
    assert any("archived-long-ago" in f["detail"] for f in unresolved), (
        f"a dangling membership went unreported: {report['findings']}")
    fatal = [f for f in report["findings"]
             if f["severity"] == "error" and "archived-long-ago" in f["detail"]]
    assert not fatal, f"a dangling membership must not be fatal: {fatal}"


def test_format_states_the_membership_rule():
    """covers: M4 — FORMAT §3.2 names the key and the directory it resolves into."""
    text = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    assert "§3.2" in text or "### §3.2" in text, "FORMAT lost the section this rule lives in"
    lowered = text.lower()
    assert "milestone" in lowered and "/milestones/" in text, \
        "FORMAT does not state which key resolves a bare slug, nor into which directory"
    assert "bare slug" in lowered, \
        "FORMAT does not name the bare-slug form the membership rule turns into an edge"
