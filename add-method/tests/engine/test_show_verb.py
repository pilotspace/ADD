"""`add show` — one node read whole, with its neighbourhood, bounded and read-only.

Red-first for `/tasks/show-verb.md`.

The verb exists because nothing in the engine READS a node: `search` returns an address and a
bounded snippet, `brief` returns a phase-scoped prompt. The two failure shapes it must never
have are both "answers a different question and reads as success":

* a ref that does not resolve must REFUSE, never fall back to a substring search (R:FALLBACK);
* an `--expand` above the cap must REFUSE, never clamp to the cap and report success (R:CLAMP).

`cli._resolve` best-guesses `/tasks/<ref>.md` for anything it cannot find, which is the exact
shape R:GUESS forbids reaching the new verb.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

CLI = REPO / "tooling" / "cli.py"
SKILL_TREES = (REPO / "skill" / "add",
               REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
               REPO.parent / ".claude" / "skills" / "add")


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / ".add"
    add.init(root, profile="code", title="show fixture")
    add.new(root, "Milestone", "m-one", title="the owning milestone")
    add.new(root, "Task", "t-one", title="a member", milestone="m-one")
    add.new(root, "Task", "t-two", title="another", milestone="m-one")
    return root


def _cli(root, *args):
    done = subprocess.run([sys.executable, str(CLI), "--root", str(root), *args],
                          capture_output=True, text=True, timeout=60)
    return done.returncode, done.stdout + done.stderr


def _tree(root) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(Path(root).rglob("*")) if p.is_file()}


# ---------------------------------------------------------------------- M1 · the whole node

def test_show_prints_the_whole_body(bundle):
    """covers: M1, A3 — a reader gets the contract, not a summary of it."""
    view, _note = add.show(bundle, "t-one")
    assert view is not None, "a real slug refused"
    body = view["body"]
    headings = [ln for ln in Path(bundle, "tasks/t-one.md").read_text(encoding="utf-8")
                .splitlines() if ln.startswith("## ")]
    assert headings, "the fixture node has no sections, so this proves nothing"
    for heading in headings:
        assert heading in body, f"`show` dropped {heading!r} — that is a summary, not the node"
    assert view["fm"].get("type") == "Task", view["fm"]


def test_show_walks_to_the_default_depth(bundle):
    """covers: M2, A10 — the flag's default and the primitive's default are ONE number."""
    view, _note = add.show(bundle, "t-one")
    assert view["rows"], "a member task has a milestone edge and must have neighbours"
    assert max(r[0] for r in view["rows"]) <= add.NEIGHBORHOOD_DEFAULT
    assert add.NEIGHBORHOOD_DEFAULT == 3, "the ratified default walk is three levels"


# ------------------------------------------------------------------- M3 · refuse, never clamp

def test_over_cap_expand_refuses_and_names_the_cap(bundle):
    """covers: M3, R:CLAMP, E6 — the cap itself succeeds; one past it refuses."""
    at_cap, _note = add.show(bundle, "t-one", add.NEIGHBORHOOD_MAX)
    assert at_cap is not None, "the cap is INCLUSIVE — the documented depth must not refuse"

    over, note = add.show(bundle, "t-one", add.NEIGHBORHOOD_MAX + 1)
    assert over is None, (
        "an over-cap expand returned a view — a clamp that reports success answers a question "
        "nobody asked")
    assert str(add.NEIGHBORHOOD_MAX) in note, \
        f"the refusal does not tell the caller what the cap IS: {note}"


# ------------------------------------------------------ M4 · resolve exactly one, or refuse

def test_unresolvable_ref_refuses_without_searching(bundle):
    """covers: M4, R:FALLBACK, E3 — a read must not silently become a search."""
    view, note = add.show(bundle, "nothing-by-this-name")
    assert view is None, "an unresolvable ref returned a view"
    assert "hit" not in note.lower(), \
        f"the refusal looks like search output — the read fell back: {note}"
    assert "nothing-by-this-name" in note, note


def test_ambiguous_ref_lists_candidates(bundle):
    """covers: M4, R:GUESS, E4 — several matches refuse and name them all.

    Built by writing the duplicate directly: `new` refuses a slug already taken bundle-wide
    (task slug-is-unique-across-types), so this state is reachable only by a hand edit — which
    is exactly the state a resolver must not paper over.
    """
    dup = Path(bundle) / "personas" / "t-one.md"
    dup.parent.mkdir(exist_ok=True)
    dup.write_text(Path(bundle, "tasks/t-one.md").read_text(encoding="utf-8")
                   .replace("type: Task", "type: Persona"), encoding="utf-8")
    cid, note = add.resolve_ref(bundle, "t-one")
    assert cid is None, f"an ambiguous slug was silently resolved to {cid}"
    assert "/tasks/t-one.md" in note and "/personas/t-one.md" in note, \
        f"the refusal must name every candidate: {note}"


def test_slug_resolves_for_any_node_type(bundle):
    """covers: A2, E1, E2 — the probe. A Milestone slug resolves with no type hint."""
    cid, _note = add.resolve_ref(bundle, "m-one")
    assert cid == "/milestones/m-one.md", \
        f"a bare slug resolved Task-shaped instead of by node: {cid}"
    same, _note = add.resolve_ref(bundle, "/milestones/m-one.md")
    assert same == cid, "a full cid did not resolve to itself"


# ------------------------------------------------------------------------- M5 · read-only

def test_show_writes_nothing(bundle):
    """covers: M5 — every byte in the bundle is unchanged, and no stamp is recorded."""
    before = _tree(bundle)
    add.show(bundle, "t-one")
    add.show(bundle, "no-such-node")
    after = _tree(bundle)
    assert before == after, (
        "`show` changed the bundle: "
        f"{sorted(set(before) ^ set(after)) or [k for k in before if before[k] != after.get(k)]}")


def test_expand_zero_shows_the_node(bundle):
    """covers: E5, A9 — a lonely neighbourhood is an answer; only a missing node refuses."""
    view, _note = add.show(bundle, "t-one", 0)
    assert view is not None, "expand=0 refused — the node exists"
    assert view["rows"] == [], view["rows"]
    assert view["body"], "the node's content must still be there"


# ----------------------------------------------------------------- M6 · every registry knows

def test_show_is_wired_and_advertised(bundle):
    """covers: M6, R:PHANTOM — advertised == wired, and both contain the new verb."""
    sys.path.insert(0, str(REPO / "tooling"))
    import cli
    advertised = set(cli.build_parser()._subparsers._group_actions[0].choices)
    assert "show" in advertised, "the verb is not advertised by the CLI"
    code, out = _cli(bundle, "show", "t-one")
    assert code == 0, f"the advertised verb is not wired: {out}"
    assert "t-one" in out, out


def test_every_registry_learned_the_show_verb():
    """covers: M6, A4 — the five sites, enumerated because a count pin names no verb."""
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "26 verbs" in readme, "the package README still claims the old verb count"

    pin = (REPO / "tests" / "engine" / "test_authoring_beat.py").read_text(encoding="utf-8")
    assert "== 26" in pin, "the CLI-surface count pin was not re-aimed"

    reference = (REPO / "docs" / "13-command-reference.md").read_text(encoding="utf-8")
    assert "add show" in reference, "the book command reference does not name the verb"

    for tree in SKILL_TREES:
        if not tree.exists():
            continue                      # a gitignored twin — exists-skip, never a false green
        text = (tree / "SKILL.md").read_text(encoding="utf-8")
        assert "add show" in text, f"{tree}/SKILL.md does not name the verb"


def test_non_integer_expand_is_a_usage_error(bundle):
    """covers: E7 — argparse judges the type; the engine judges the value.

    The FLOOR comes first. Without it this check passes vacuously before the verb exists at
    all: an unknown subcommand is also an argparse exit 2, so `deep` would look rejected for
    its type while nothing had parsed it.
    """
    ok, out = _cli(bundle, "show", "t-one", "--expand", "3")
    assert ok == 0, f"the verb does not work at all, so exit 2 below proves nothing: {out}"
    code, _out = _cli(bundle, "show", "t-one", "--expand", "deep")
    assert code == 2, "a non-integer --expand must be a usage error, not an engine refusal"


def test_show_refusal_names_a_runnable_next(bundle):
    """covers: A14 — a refusal that does not say what IS available is a dead end."""
    for ref, expand in (("no-such-node", 3), ("t-one", add.NEIGHBORHOOD_MAX + 1)):
        _view, note = add.show(bundle, ref, expand)
        assert "next:" in note, f"refusal for {ref!r} has no next: line — {note}"
        verb = note.split("next:")[1].split()[0].strip("`")
        sys.path.insert(0, str(REPO / "tooling"))
        import cli
        advertised = set(cli.build_parser()._subparsers._group_actions[0].choices)
        assert verb == "add" or verb in advertised, f"the next: names no real verb: {note}"
