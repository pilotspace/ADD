"""ASSUMPTIONS is swept per SURFACE, not per Must — and progressively, not as a wall.

`freeze` checked that ASSUMPTIONS was non-empty. A non-empty check cannot produce
completeness: three live amb1 reps each recorded 5-7 substantive assumptions and all
three still shipped `A-list-scope` as a silent decision (`M3 GET /bookings lists all
bookings`, stated as fact). Rep1 proves it was coverage, not ability — it interrogated
that endpoint on *which* rows and never on *whose*, and even wrote the words "a caller's
own" while doing it.

The first sweep hung on Musts and demanded 50-60 pairs on real nodes (12 x 5, 10 x 5,
11 x 5). That is not a checklist, it is a toll, and a toll gets paid with blanket lines
that satisfy the gate without doing the work.

A surface is the right unit — the thing a caller touches — and the node already has a
field for it: `gives:`. It was empty in 3 of 3 live runs for the same reason the
assumption was: NOTHING SCAFFOLDED IT. `gives:` appears in neither `BODIES["Task"]` nor
the frontmatter key order, while the engine reads it for the direction digest and for
brief refs. Scaffolding it fixes a third phantom instruction and cuts the matrix to
~5 surfaces x 5 dimensions.

The bypass this opens is closed here too: no surfaces would mean nothing to sweep, so
`freeze` refuses an unauthored `gives:` rather than waving the node through.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tooling"))
import add  # noqa: E402

RULES = """<must>
- M1 the list endpoint returns rows
- M2 the delete endpoint removes a row
</must>
<reject>
- R:LEAK a caller must never see another caller's row -> "LEAK"
</reject>"""

CHECKS = ("- test_list · covers: M1 · rows come back\n"
          "- test_delete · covers: M2 · the row goes\n"
          "- test_leak · covers: R:LEAK · no cross-caller read\n"
          "red-first: every check MUST fail first.")

GIVES = ["S1 GET /bookings — the list", "S2 DELETE /bookings/{id} — cancel"]

FULL = "\n".join(
    f"- A{i} [{d}] covers: S1, S2 · the spec is silent on {d} -> a wrong reading costs"
    for i, d in enumerate(add.SWEEP_DIMENSIONS, 1))


def _node(tmp_path, assumptions: str, *, depth="standard", gives=GIVES):
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t1", title="t", depth=depth, gives=gives)
    path = tmp_path / cid.lstrip("/")
    node = add.read(path, "T2")
    body = node["body"]
    for heading, text in (("RULES", RULES), ("ASSUMPTIONS", assumptions), ("CHECKS", CHECKS)):
        lines = body.splitlines()
        start = next(i for i, l in enumerate(lines) if l.strip() == f"## {heading}")
        end = next((i for i in range(start + 1, len(lines))
                    if lines[i].startswith("## ")), len(lines))
        body = "\n".join(lines[:start + 1] + [text] + lines[end:])
    path.write_text(f"---\n{node['raw']}\n---\n{body}", encoding="utf-8")
    return add.read(path, "T2"), cid


def test_gives_is_scaffolded_so_it_stops_being_a_phantom(tmp_path):
    """covers: M1 — empty in 3/3 live runs because no slot existed to fill."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "fresh", title="t")
    raw = (tmp_path / cid.lstrip("/")).read_text(encoding="utf-8")
    assert "gives:" in raw, "the Task scaffold still has no gives: slot"
    assert "S1" in raw, "the scaffold does not show the S<n> surface id shape"


def test_surfaces_come_from_gives(tmp_path):
    """covers: M2 — the sweep's axis is the contract, not the rule list."""
    node, _ = _node(tmp_path, FULL)
    assert add.surfaces_of(node) == ["S1", "S2"]


def test_a_full_sweep_leaves_nothing_unswept(tmp_path):
    """covers: M3 — the gate must be passable or authors route around it."""
    assert add.assumption_sweep(_node(tmp_path, FULL)[0]) == []


def test_a_surface_missing_one_dimension_is_reported(tmp_path):
    """covers: M4, E1 — the live failure: `which` asked of the list, `who` never."""
    partial = FULL.replace("[who] covers: S1, S2", "[who] covers: S2")
    assert ("who", "S1") in add.assumption_sweep(_node(tmp_path, partial)[0])


def test_a_dimension_can_be_retired_as_not_applicable(tmp_path):
    """covers: M5 — a sweep with no escape hatch is a sweep that gets faked.

    Recording a considered *no* is the work; what is refused is silence.
    """
    text = FULL.replace("[order] covers: S1, S2", "[order] n/a ·").replace(
        "· the spec is silent on order -> a wrong reading costs",
        "this contract exposes no ordered collection")
    assert add.assumption_sweep(_node(tmp_path, text)[0]) == []


def test_freeze_refuses_while_a_pair_is_unswept(tmp_path):
    """covers: M6, R:NONEMPTY_IS_NOT_COMPLETE."""
    partial = FULL.replace("[who] covers: S1, S2", "[who] covers: S2")
    _, cid = _node(tmp_path, partial)
    ok, note = add.freeze(tmp_path, cid, by="T")
    assert not ok and "who" in note and "S1" in note, note


def test_freeze_refuses_an_unauthored_gives(tmp_path):
    """covers: R:BYPASS — no surfaces would mean nothing to sweep, i.e. a free pass.

    Without this, deleting `gives:` is a one-line way to switch the whole gate off.
    """
    _, cid = _node(tmp_path, FULL, gives=None)
    ok, note = add.freeze(tmp_path, cid, by="T")
    assert not ok and "gives" in note, note


def test_quick_depth_is_exempt(tmp_path):
    """covers: E2 — depth tunes ceremony, never the authority floor (SKILL.md)."""
    thin = "- A1 [who] covers: S1 · silent on who -> costs"
    assert add.assumption_sweep(_node(tmp_path, thin, depth="quick")[0]) == []


def test_a_node_without_the_section_is_not_retroactively_refused(tmp_path):
    """covers: E3 — bundles predating the section still freeze (law 3)."""
    node, _ = _node(tmp_path, FULL)
    node["body"] = node["body"].replace("## ASSUMPTIONS", "## NOTHING-HERE")
    assert add.assumption_sweep(node) == []


def test_todo_reports_remaining_pairs_before_freeze(tmp_path):
    """covers: M7, R:WALL — progressive, so freeze confirms work already done.

    Meeting the whole matrix at the moment you expected to be finished is how a gate
    earns a reputation for obstruction rather than for catching things.
    """
    partial = FULL.replace("[who] covers: S1, S2", "[who] covers: S2")
    _node(tmp_path, partial)
    _, note = add.todo(tmp_path)
    assert "unswept" in note.lower(), f"todo gives no progressive signal: {note}"
