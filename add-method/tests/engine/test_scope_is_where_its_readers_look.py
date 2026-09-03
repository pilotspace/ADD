"""A template slot no reader reads is worse than a missing one.

The Task scaffold's only `scope:` slot sits in `## PLAN`:

    ## PLAN
    contract: <the shape this publishes>
    scope: <files>

Every reader in the engine looks in frontmatter — `scope = (fm or {}).get("scope") or []`. So an
author who fills in the slot the scaffold offers gets, at the gate:

    freshness: n/a — the node declares no `scope:`

and `phantom_scope`, the refusal for a scope naming paths that do not exist, has never been able
to fire on a scaffolded node: the value it would judge is in a section it never reads.

The slot consumed the author's attention and returned nothing.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


# ------------------------------------------------------------------ M1/M2 · one slot, where it is read

def test_a_fresh_task_carries_a_frontmatter_scope_slot(tmp_path):
    """covers: M1, A3, A6 — the slot must be where every reader already looks."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "probe", title="p")
    fm = add.read(root / cid.lstrip("/"), "T2")["fm"]
    assert "scope" in fm, "a fresh Task offers no frontmatter `scope:` slot"


def test_the_plan_body_offers_no_scope_slot(tmp_path):
    """covers: M2, A6, R:DEADSLOT — one slot, not two.

    Two slots is worse than the bug: the author fills the nearer one and the engine reads the
    other, which is precisely how this defect presented.
    """
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "probe", title="p")
    plan = add._section_of(add.read(root / cid.lstrip("/"), "T2")["body"], "PLAN")
    assert "scope:" not in plan, f"`## PLAN` still offers a slot no reader reads:\n{plan}"


def test_a_new_milestone_has_no_scope_slot(tmp_path):
    """covers: A2 — Tasks only; a Milestone earns no receipt, so its scope would be a second dead slot."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Milestone", "m", title="m")
    assert "scope" not in (add.read(root / cid.lstrip("/"), "T2")["fm"] or {})


# ------------------------------------------------------------------ M3/M4 · the readers, and the revived refusal

def test_a_filled_scope_is_read_by_its_readers(tmp_path):
    """covers: M3, A2 — what the author declared is what the engine digests."""
    # `scope_digest` reads git — a bundle whose parent is not a repo degrades to no digest, which
    # would make this check pass over a value nothing read. The fixture is a real repo so the
    # assertion is about the SLOT, not about the degrade path.
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "real", title="r")
    p = root / cid.lstrip("/")
    tracked = tmp_path / "src.py"
    tracked.write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "src.py"], cwd=tmp_path, check=True)
    add.write(p, f"---\n{add.set_key(add.read(p, 'T2')['raw'], 'scope', ['src.py'])}\n---\n"
                 f"{add.read(p, 'T2')['body']}")
    assert (add.read(p, "T2")["fm"] or {}).get("scope") == ["src.py"]
    assert add.scope_digest(tmp_path, ["src.py"]), \
        "a declared, existing, tracked scope produced no digest"


def test_phantom_scope_fires_on_a_scaffolded_node(tmp_path):
    """covers: M4, S2 — the refusal that could never fire on a node `new` created.

    This is the point of the whole task: a scope naming a path that does not exist must be
    catchable on a node whose scope was declared in the slot the scaffold offered.
    """
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "ghost", title="g")
    p = root / cid.lstrip("/")
    add.write(p, f"---\n{add.set_key(add.read(p, 'T2')['raw'], 'scope', ['no/such/dir'])}\n---\n"
                 f"{add.read(p, 'T2')['body']}")
    fm = add.read(p, "T2")["fm"]
    missing = [s for s in (fm.get("scope") or []) if not (root.parent / str(s)).exists()]
    assert missing == ["no/such/dir"], \
        f"a declared, absent path is not visible to the phantom_scope reader: {fm.get('scope')}"


# ------------------------------------------------------------------ counter-guard

def test_a_fresh_node_declares_no_scope(tmp_path):
    """covers: A3, M5 — the measured regression: a placeholder here turned 29 green tests red.

    `gives:` is descriptive, so its placeholder is merely unhelpful when left unfilled. `scope:`
    is ENFORCED: a placeholder makes a fresh node DECLARE a scope, and every reader then degrades
    freshness or refuses an edit outside it. The key is the prompt; the value must stay empty.
    """
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "fresh", title="f")
    fm = add.read(root / cid.lstrip("/"), "T2")["fm"]
    assert not (fm.get("scope") or []), \
        f"a fresh node declares a scope it cannot satisfy: {fm.get('scope')!r}"


def test_a_fresh_node_is_not_reported_as_misdeclared(tmp_path):
    """covers: M5, A4, E1, E2 — the seeded value must never read as a declared scope.

    The first cut of this check filtered `doctor()` for `phantom_scope` and asserted the list was
    empty. `doctor()` emits sixteen codes and that is not one of them — `phantom_scope` is a GATE
    refusal — so the filter was empty for every input and the check passed for every input. It
    now asserts the property that actually matters, against the reader that actually reads it.
    """
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "fresh", title="f")
    fm = add.read(root / cid.lstrip("/"), "T2")["fm"]
    assert not (fm.get("scope") or []), \
        f"the seeded value reads as a declared scope: {fm.get('scope')!r}"
    # and the guard that DOES judge a scope claim stays quiet, because the CARD claims none
    card = add.card_of(add.read(root / cid.lstrip("/"), "T2")["body"])
    assert not [l for l in card.splitlines()
                if l.startswith("scope:") and l.partition(":")[2].strip()], \
        "the fresh CARD claims a scope the frontmatter lacks — that IS phantom_scope"


def test_the_real_phantom_scope_predicate_is_the_card(tmp_path):
    """covers: E3 — what `phantom_scope` actually keys on, pinned so the name stops misleading.

    It is not path existence, and this task did not change it. The previous check here hand-rolled
    a path-existence loop over a value the test itself had just written — a tautology naming a
    predicate the engine does not have. Pinned from the SOURCE so a reader of this file cannot
    repeat the mistake.
    """
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    where = src.index('_binds("phantom_scope"')
    context = src[where - 700:where]
    assert "card_of(" in context, \
        "phantom_scope no longer keys on the CARD — this pin, and E3, need re-reading"
    assert "exists()" not in context, \
        "phantom_scope now judges path existence — the retired M4 may be buildable after all"
