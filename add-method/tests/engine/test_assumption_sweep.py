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
    # CARD joins the authored set: `freeze` refuses a template `goal:`, and it does so
    # before it reaches the sweep — so without this the sweep refusals under test are
    # masked by a placeholder refusal and these checks probe the wrong guard.
    for heading, text in (("CARD", "goal: the sweep fixture states its one line.\n"
                                   "why: probing the sweep, not authoring."),
                          ("RULES", RULES), ("ASSUMPTIONS", assumptions), ("CHECKS", CHECKS)):
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


# ── surface granularity — the probe-2 evasion ────────────────────────────────

COLLAPSED = ["S1 the booking HTTP surface — POST/GET /bookings, GET/DELETE /bookings/{id}"]
FULL_S1 = "\n".join(
    f"- A{i} [{d}] covers: S1 · the request does not say {d} -> a wrong reading costs"
    for i, d in enumerate(add.SWEEP_DIMENSIONS, 1))


def test_a_surface_naming_several_methods_is_collapsed(tmp_path):
    """covers: M7 — the live probe-2 shape verbatim: five endpoints, one S id."""
    node, _ = _node(tmp_path, FULL_S1, gives=COLLAPSED)
    assert add.collapsed_surfaces(node) == ["S1"]


def test_one_method_per_surface_is_not_collapsed(tmp_path):
    """covers: M7 — the taught shape must pass, or authors route around the gate."""
    node, _ = _node(tmp_path, FULL)
    assert add.collapsed_surfaces(node) == []


def test_a_single_callable_surface_is_not_collapsed(tmp_path):
    """covers: E5 — one `name()` is one surface; the taught function shape must pass.
    (Before beta-2/W3 this test read 'a non-HTTP surface is never judged' — functions
    ARE judged now, and this fixture holds because it names exactly one callable.)"""
    node, _ = _node(tmp_path, FULL_S1,
                    gives=["S1 admit(token) -> Claims | None — the admission decision"])
    assert add.collapsed_surfaces(node) == []


def test_freeze_refuses_a_collapsed_surface(tmp_path):
    """covers: M7, R:SWEEPDODGE — a sweep over one mega-surface asks ~5 questions
    where the request holds ~25; probe 2 answered [who] once, about the loud POST,
    and shipped the GET reads unexamined."""
    node, cid = _node(tmp_path, FULL_S1, gives=COLLAPSED)
    ok, msg = add.freeze(tmp_path, cid, by="t", authority="human")
    assert ok is None
    assert "S1" in msg and "one surface per S id" in msg, msg


def test_quick_depth_is_exempt_from_the_granularity_check(tmp_path):
    """covers: E6 — depth tunes ceremony; quick skips the sweep and its guards."""
    node, cid = _node(tmp_path, FULL_S1, gives=COLLAPSED, depth="quick")
    assert add.assumption_sweep(node) == []
    ok, _ = add.freeze(tmp_path, cid, by="t", authority="human")
    assert ok is not None


def test_todo_names_the_collapsed_surface(tmp_path):
    """covers: M8 — progressive: the author hears 'split S1' while authoring,
    not first at the freeze they expected to pass."""
    _node(tmp_path, FULL_S1, gives=COLLAPSED)
    _, out = add.todo(tmp_path)
    assert "split" in out and "S1" in out, out


# ── surface granularity beyond HTTP (beta-2, W3) ─────────────────────────────
#
# The blog docket's item 5: the one-surface-per-id refusal extends to function and
# document surfaces. The definitional line stays the same as HTTP's: two `name(`
# callable tokens are two things a caller calls, and two BACKTICKED file names are
# two named artifacts. A prose mention without backticks is not judged — a guess
# about prose shape would make the notary a guard.


def test_two_callables_in_one_entry_are_collapsed(tmp_path):
    """covers: M9 — `admit()` and `release()` are two surfaces; one S id hides one."""
    node, _ = _node(tmp_path, FULL_S1,
                    gives=["S1 admit(token) and release(token) — the admission pair"])
    assert add.collapsed_surfaces(node) == ["S1"]


def test_one_callable_named_twice_is_one_surface(tmp_path):
    """covers: M9, E7 — repetition is not multiplicity; DISTINCT names collapse."""
    node, _ = _node(tmp_path, FULL_S1,
                    gives=["S1 admit(token) — admit(token) is the whole decision"])
    assert add.collapsed_surfaces(node) == []


def test_a_parenthetical_is_not_a_callable(tmp_path):
    """covers: E7 — `the list (paginated)` is prose; only `name(` counts."""
    node, _ = _node(tmp_path, FULL_S1,
                    gives=["S1 admit(token) — the decision (idempotent) (cached)"])
    assert add.collapsed_surfaces(node) == []


def test_two_backticked_documents_are_collapsed(tmp_path):
    """covers: M10 — two backticked file names are two named artifacts under one id."""
    node, _ = _node(tmp_path, FULL_S1,
                    gives=["S1 `README.md` + `INSTALL.md` — the quickstart pair"])
    assert add.collapsed_surfaces(node) == ["S1"]


def test_a_prose_document_mention_is_not_judged(tmp_path):
    """covers: E8 — unbackticked prose stays off the heuristic's territory."""
    node, _ = _node(tmp_path, FULL_S1,
                    gives=["S1 `README.md` quickstart — grammar lives in FORMAT.md"])
    assert add.collapsed_surfaces(node) == []


def test_freeze_refuses_a_collapsed_function_surface(tmp_path):
    """covers: M9, R:SWEEPDODGE — the refusal, not just the detector."""
    _, cid = _node(tmp_path, FULL_S1,
                   gives=["S1 admit(token) and release(token) — the admission pair"])
    ok, msg = add.freeze(tmp_path, cid, by="t", authority="human")
    assert ok is None
    assert "S1" in msg and "one surface per S id" in msg, msg
