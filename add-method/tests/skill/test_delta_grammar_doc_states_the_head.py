"""`deltas.md` teaches the grammar the engine enforces — including the id and the interval.

Two guards already run one direction: `test_deltas_never_drop_silently` proves every code the DOC
promises exists in the engine. This one runs the other, which is the direction M8 states and the one
that actually rots: every code the ENGINE can emit must be documented, or an author meets a reject
code the docs never mention and routes around it.

The engine's set is read from `add.DELTA_REJECTS`, not from a hand-kept list here — a literal copy
would be a second source of one truth, which is the defect `_oneline` recorded in method.md.

covers the node `.add/tasks/dated-addressable-deltas.md`.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DELTAS_MD = REPO / "skill" / "add" / "deltas.md"
TERMS_MD = REPO / "skill" / "add" / "terms.md"
PERSONAS_MD = REPO / "skill" / "add" / "personas.md"


def test_deltas_md_states_the_dated_head_and_every_reject_code():
    """covers: M8 — the taught grammar is the enforced grammar, codes included."""
    assert DELTAS_MD.is_file(), f"the grammar doc is missing: {DELTAS_MD}"
    prose = DELTAS_MD.read_text(encoding="utf-8")

    grammar = re.search(r"## The grammar \(frozen\)(.*?)^## ", prose, re.S | re.M)
    assert grammar, "deltas.md no longer has a frozen-grammar section — this guard is stale"
    block = grammar.group(1)
    assert re.search(r"\[<COMPETENCY>\s*·\s*<ID>\s*·\s*<status>\s*·", block), (
        f"the grammar block does not show the id and the valid-from date:\n{block}")
    assert "→" in block, f"the grammar block does not show the interval separator:\n{block}"

    codes_block = re.search(r"<reject_codes>(.*?)</reject_codes>", prose, re.S)
    assert codes_block, "deltas.md no longer declares <reject_codes>"
    documented = set(re.findall(r"^-\s*`([a-z_]+)`", codes_block.group(1), re.M))
    assert documented, "the reject_codes block names no codes"

    emitted = set(add.DELTA_REJECTS)
    assert len(emitted) >= 7, (
        f"the engine's reject set was read as {sorted(emitted)} — too small to be the real one, "
        f"so this guard would pass vacuously")
    undocumented = emitted - documented
    assert not undocumented, (
        f"the engine emits codes deltas.md never documents: {sorted(undocumented)}")


def test_the_head_shape_is_stated_once_across_the_skill():
    """covers: M8 — every place an author meets the head teaches the SAME shape.

    The glossary line and personas.md's persona-delta example are the two other places the head
    appears. personas.md put its hint INSIDE the brackets, which is a second four-field head shape;
    the hint moves to the open tail so exactly one head shape exists in the skill.
    """
    assert TERMS_MD.is_file(), f"the glossary is missing: {TERMS_MD}"
    glossary = [ln for ln in TERMS_MD.read_text(encoding="utf-8").splitlines()
                if "**delta**" in ln]
    assert len(glossary) == 1, f"expected one delta glossary row, found {len(glossary)}"
    assert "<ID>" in glossary[0] and "<valid-from>" in glossary[0], (
        f"the glossary still teaches the undated head:\n{glossary[0]}")

    assert PERSONAS_MD.is_file(), f"the persona guide is missing: {PERSONAS_MD}"
    personas = PERSONAS_MD.read_text(encoding="utf-8")
    examples = re.findall(r"^- \[[A-Z]+ · .*$", personas, re.M)
    assert examples, "personas.md no longer carries a persona-delta example — this guard is stale"
    for ex in examples:
        head = ex[ex.index("[") + 1:ex.index("]")]
        assert "persona:" not in head, (
            f"the persona hint is still inside the head, giving the skill a second "
            f"four-field shape:\n{ex}")
        assert "persona:" in ex, f"the persona-delta claim was deleted rather than moved:\n{ex}"
        assert len([f for f in head.split("·")]) == 4, (
            f"the persona-delta example must use the one dated head shape:\n{ex}")
