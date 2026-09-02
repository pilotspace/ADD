"""A section the gate binds is a section the direction guide teaches.

Red-first for `/tasks/edges-documented.md`.

`## EDGES` is scaffolded into every Task and is a first-class gate referent: `referents_of`
returns rules + edges + probed assumptions, and `unbound()` iterates it, so a filled-in `E1`
with no passing check refuses the PASS. The direction guide headed its list "The four sections"
and named RULES · ASSUMPTIONS · PLAN · CHECKS — and documented an `After` part that exists
nowhere in the format or the engine, occupying the line where the real gate-binding section
belonged. The stated `covers:` grammar omitted both `E<n>` and `A<n>`, which the engine admits.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
DIRECTION = SKILL / "phases" / "direction.md"
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def _flat(p: Path) -> str:
    return " ".join(p.read_text(encoding="utf-8").split())


def _scaffold_sections() -> list:
    """The `## ` headings the Task scaffold actually writes — the set the guide must teach."""
    return re.findall(r"^## ([A-Z]+)$", add.BODIES["Task"], re.M)


def _referent_forms() -> set:
    """Every form the engine's `REFERENT` pattern admits, read FROM the pattern.

    The first cut of this ran a regex over the compiled pattern STRING, matched nothing, and
    silently fell through to a second helper — which was the only one anything called. One
    reader now, probing each token by membership in the pattern, which is what the engine
    actually encodes.
    """
    pat = add.REFERENT.pattern
    out = set()
    for token, label in (("M\\d+", "M<n>"), ("E\\d+", "E<n>"), ("A\\d+", "A<n>"),
                         ("R:[A-Z0-9_]+", "R:<CODE>"), ("G\\d+", "G<n>"), ("goal", "goal")):
        if token in pat:
            out.add(label)
    return out


def test_the_direction_guide_lists_every_scaffolded_section():
    """covers: M1, A4, R:UNTAUGHTBINDING · sections enumerated from the scaffold."""
    flat = _flat(DIRECTION)
    missing = [s for s in _scaffold_sections()
               if s not in ("CARD", "EVIDENCE", "LESSONS") and f"## {s}" not in flat]
    assert not missing, f"the direction guide teaches no section: {missing}"
    assert "EDGES" in flat, "the guide never names EDGES, which the gate binds"


def test_the_guide_does_not_undercount_its_own_sections():
    """covers: M1 · a heading that says `four` while listing five teaches the wrong shape."""
    flat = _flat(DIRECTION)
    assert "The four sections" not in flat, \
        "the section list still calls itself `four` while EDGES makes it five"


def test_the_covers_grammar_matches_the_engine():
    """covers: M2, M3, A1 · both directions — no form missing, none invented."""
    flat = _flat(DIRECTION)
    for label in _referent_forms():
        assert label in flat, f"the guide never teaches the referent form `{label}`"


def test_the_guide_does_not_miscount_the_referent_forms():
    """covers: M2 · a grammar line that says `five` while listing six teaches the wrong shape.

    The sibling check catches an undercounted SECTION list. This is the same defect one
    paragraph later, and it shipped in the very commit that fixed the first one: the corrected
    grammar named six forms and called them five. Bind the written number to the engine's count.
    """
    flat = _flat(DIRECTION)
    n = len(_referent_forms())
    words = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}
    assert n in words, f"the engine admits {n} referent forms — extend this check's number words"
    assert f"hose {words[n]} forms" in flat, (
        f"the guide states a referent-form count that is not {words[n]} — the engine admits "
        f"{n}: {sorted(_referent_forms())}")
    stale = [w for k, w in words.items() if k != n and f"hose {w} forms" in flat]
    assert not stale, f"the guide also states a stale count: {stale}"


def test_the_probed_assumption_form_is_taught():
    """covers: E3 · `A<n>` is admitted by the engine and must appear in the stated grammar."""
    assert "A<n>" in _flat(DIRECTION)


def test_the_quick_depth_referents_are_stated_correctly():
    """covers: E2 · the depth split holds."""
    flat = _flat(DIRECTION)
    assert "quick" in flat and "goal" in flat


def test_an_untouched_edge_placeholder_owes_nothing(tmp_path):
    """covers: A2, E1 · a scaffolded node's untouched E1 is not a gate-bound referent."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="edges probe")
    add.new(root, "Task", "e", depth="quick")
    node = add.read(root / "tasks" / "e.md", "T2")
    assert not [r for r in add.edges_of(node) if r.startswith("E")], \
        "an untouched EDGES placeholder became a gate-bound referent"


def test_the_guide_names_no_phantom_node_part():
    """covers: M4 · `After` appears in neither the format nor the engine."""
    flat = _flat(DIRECTION)
    assert "`After`" not in flat and "(post-conditions)" not in flat, \
        "the guide still documents an `After` part that no scaffold or engine surface has"


def test_the_skill_summary_does_not_nest_edges_in_rules():
    """covers: M5, E5 · EDGES is its own section, not prose inside RULES."""
    flat = _flat(SKILL / "SKILL.md")
    assert "EDGES are the boundaries of those rules" not in flat, \
        "SKILL.md still presents EDGES as prose within the RULES bullet"
    assert len((SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines()) <= 176


def test_format_md_and_the_guide_agree():
    """covers: E4 · FORMAT.md documents EDGES correctly; the guide must not contradict it."""
    fmt = " ".join((REPO / "FORMAT.md").read_text(encoding="utf-8").split())
    assert "## EDGES" in fmt
    assert "E<n>" in _flat(DIRECTION)


def test_the_binding_consequence_is_stated_at_authoring():
    """covers: A3 · the guide says what a filled edge costs, where the author writes it."""
    flat = _flat(DIRECTION)
    assert "EDGES" in flat and ("gate" in flat.split("EDGES", 1)[1][:600]), \
        "the guide names EDGES but never says the gate binds it"
