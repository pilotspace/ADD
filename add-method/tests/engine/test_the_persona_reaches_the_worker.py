"""`advise` records a lens the brief never reads, so the spawned worker gets no expertise.

`advise()` stamps `advised_by: <persona>`. `brief()` injects the `<persona>` block only under
`if fm.get("persona")`. Two different keys, so `add advise <slug> --persona <p>` can never
populate a brief — the documented way to put a lens on a sequential beat writes to a field the
one consumer does not read.

The gate already treats them as equals: R:NOCOVERAGE accepts EITHER `persona:` or `advised_by:`
as "who reviewed the security". So a security node can carry a lens that satisfies the gate and
still hand its worker a brief with no lens in it — and the brief prints a cost and marks itself
`standalone="true"`, so nothing in the output says the expertise is missing.

Personas carry the expertise, the agent carries the discipline. A brief that drops the persona
silently ships the discipline alone.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _a_seeded_persona(root):
    personas = sorted((root / "personas").glob("*.md"))
    assert personas, "`init` seeded no personas — the fixture cannot probe the lens path"
    return personas[0].stem


def test_advise_and_persona_reach_the_brief_identically(tmp_path):
    """covers: M1, R:LENSLOST — the two keys the gate already treats as equals."""
    root = _bundle(tmp_path)
    lens = _a_seeded_persona(root)

    by_field, _ = add.new(root, "Task", "viafield", title="viafield", persona=lens)
    by_advise, _ = add.new(root, "Task", "viaadvise", title="viaadvise")
    ok, note = add.advise(root, by_advise, persona=lens)
    assert ok, note

    field_brief = str(add.brief(root, by_field)["text"])
    advise_brief = str(add.brief(root, by_advise)["text"])
    assert lens in field_brief, f"the `persona:` path lost the lens too: {field_brief[:400]}"
    assert lens in advise_brief, (
        "`add advise` recorded a lens the brief never reads — the spawned worker gets the "
        f"discipline with none of the expertise:\n{advise_brief[:400]}")


def test_a_brief_with_no_lens_says_so(tmp_path):
    """covers: M2, A3 — a silent omission reads exactly like a lens that had nothing to add."""
    root = _bundle(tmp_path)
    # A NEUTRAL slug. The first cut used `unlensed`, and the brief echoes the slug in its
    # `<task id=...>` and `<objective>` — so the regex matched the fixture's own name and the
    # check passed while the engine said nothing at all. Re-run with `zzz` it matched nothing.
    cid, _ = add.new(root, "Task", "zzz", title="a task with no lens")
    text = str(add.brief(root, cid)["text"])
    assert "zzz" not in r"no (persona|lens)|generic", "the pattern must not contain the slug"
    assert re.search(r"no (persona|lens)|generic", text, re.I), (
        f"a lensless brief is indistinguishable from a lensed one:\n{text[:400]}")


def test_the_gate_and_the_brief_agree_on_what_counts_as_a_lens(tmp_path):
    """covers: M1, E1 — R:NOCOVERAGE accepts either key; the brief must not accept fewer."""
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    gate_keys = set(re.findall(r'sfm\.get\("(persona|advised_by)"\)', src))
    assert gate_keys == {"persona", "advised_by"}, gate_keys
    # Scoped to `brief`'s own body, not the whole module — `doctor` also reads both keys, and
    # a module-wide grep would have gone green while the brief still dropped the lens.
    import ast
    fn = [n for n in ast.walk(ast.parse(src))
          if isinstance(n, ast.FunctionDef) and n.name == "brief"][0]
    body = ast.get_source_segment(src, fn) or ""
    assert "advised_by" in body, (
        "the gate accepts `advised_by:` as a named lens but `brief` never reads it")
