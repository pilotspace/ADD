"""Red suite for `freeze-binds-what-you-authored` — the R:UNCOVERED rung.

M31 recorded three tasks in one milestone gating red on an authored edge or a probed assumption
with no covering check. M38 recorded the FOURTH, on the milestone that exists to stop it — caught
after a full build, a brief and three receipts. The gate is the last place in the loop, so the cost
of learning there is the whole build. This moves the refusal to where the obligation is created.

It began NARROW on purpose (M3, R:WIDENED) — filled edges and probed assumptions only, because
the cost of widening to Musts and Rejects was estimated and not measured. `uncovered-widens-to-
rules` measured it (0 of 105 nodes) and widened the rung; the fixtures below cover their rules so
that only the obligation each check is about can fire.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

SWEEP = "\n".join(
    f"- A{i} [{d}] covers: S1 · the request does not say a thing about {d}; taking a reading "
    f"-> a cost if wrong"
    for i, d in enumerate(("who", "which", "when", "absent", "order", "experience"), start=1))

BODY = """## CARD
goal: a goal that is authored
why: a reason that is authored
beat: direction · next: add freeze {slug}

## RULES
<must>
- M1 a rule that must hold
</must>
<reject>
- R:THING a thing that must never happen -> "THING"
</reject>

## ASSUMPTIONS
{sweep}{probe}

## PLAN
contract: the shape this publishes

## EDGES
{edges}

## CHECKS
{checks}
red-first: every check MUST fail first.

## EVIDENCE
receipt: pending
gate: pending

## LESSONS
- pending
"""


def task(root, slug, *, edges="- E1 a boundary case a check must cover",
         checks="- test_one · covers: M1 · what it proves",
         probe=False, depth="standard", drop_checks=False, unswept=False):
    """A node that clears every EARLIER rung of the freeze ladder, so only the new one can fire."""
    add.new(root, "Task", slug, title=f"Task {slug}", depth=depth)
    path = Path(root) / "tasks" / f"{slug}.md"
    raw = path.read_text().split("---")[1]
    # `set_key` replaces one SCALAR; `gives:` is a list, so author it by replacing the slot.
    raw = raw.replace("  - S1 <the surface this publishes — an endpoint, function, or section>",
                      "  - S1 one authored surface this task publishes")
    assert "<" not in raw.split("gives:")[1].split("generated:")[0], raw
    sweep = SWEEP
    if unswept:
        sweep = "\n".join(sweep.splitlines()[:3])
    body = BODY.format(
        slug=slug, sweep=sweep, edges=edges, checks=checks,
        probe=("\n- A7 [which] covers: S1 · the request does not say which rows are in; taking a "
               "reading · probe: what shipped behaviour must show" if probe else ""))
    if drop_checks:
        body = body.split("## CHECKS")[0] + "## EVIDENCE\nreceipt: pending\ngate: pending\n"
    path.write_text(f"---{raw}\n---\n{body}")
    return f"/tasks/{slug}.md"


def _freeze(root, cid):
    return add.freeze(root, cid, by="plan:t", authority="plan")


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Bind")
    return tmp_path


def test_freeze_refuses_an_uncovered_edge(bundle):
    """covers: M1, A9, A11, E1 — named, sorted, and binding is the FIRST way out."""
    cid = task(bundle, "uncovered-edge",
               edges="- E2 a second boundary case\n- E1 a first boundary case")
    ok, note = _freeze(bundle, cid)
    assert not ok and "UNCOVERED" in note, note
    assert "E1" in note and "E2" in note, note
    assert note.index("E1") < note.index("E2"), f"A9 — the ids were not sorted:\n{note}"
    nxt = note.split("next:", 1)[1]
    assert "covers:" in nxt, f"R:DELETEPAST — the way out never names binding:\n{nxt}"
    assert nxt.index("covers:") < len(nxt), nxt
    assert "delet" not in nxt.split("covers:")[0].lower(), \
        f"R:DELETEPAST — deleting the edge was offered first:\n{nxt}"


DEPTHS = ("standard", "quick")


def test_freeze_refuses_an_uncovered_probe(bundle):
    """covers: M1, A2, E5 — a probe is an obligation at every depth, quick included.

    NOT parametrized, deliberately: JUnit reports a parametrized case as `name[param]`, and the
    gate resolves a `covers:` citation by the BARE function name — so a parametrized check binds
    nothing and this task gated red on exactly that. The cases loop from a module constant.
    """
    for depth in DEPTHS:
        cid = task(bundle, f"uncovered-probe-{depth}", probe=True, depth=depth,
                   edges="- E1 a boundary case", checks="- test_one · covers: M1, E1 · proves it")
        ok, note = _freeze(bundle, cid)
        assert not ok and "UNCOVERED" in note and "A7" in note, f"depth={depth}: {note}"


def test_the_rung_and_the_gate_agree(bundle):
    """covers: M2, R:SECOND_TRUTH — one definition of an obligation, not two."""
    cid = task(bundle, "agree", probe=True, edges="- E1 a boundary case")
    node = add.read(Path(bundle) / "tasks" / "agree.md", "T2")
    node["path"] = Path(bundle) / "tasks" / "agree.md"
    ours = add.uncovered_obligations(node)
    # RE-AIMED (uncovered-widens-to-rules): this filtered to `E`/`A` ids because the rung
    # deliberately excluded Musts and Rejects. It no longer does, and a filter that outlives its
    # reason is what makes two definitions of one thing.
    theirs = [r for r in add.referents_of(node) if r not in add.covers(node)]
    assert sorted(ours) == sorted(theirs), \
        f"the rung and the gate disagree about what an obligation is:\n  {ours}\n  {theirs}"
    assert ours, "the fixture produced no obligation, so this proves nothing"


# RETIRED: test_the_rung_does_not_widen_to_musts (M3, R:WIDENED, E4)
#
# It held a real line — an unmeasured blast radius is not shipped on a guess — and it held it
# until the measurement existed. `uncovered-widens-to-rules` ran it over this bundle: 0 of 105
# nodes carrying RULES have an uncovered Must or Reject, and 21 carry no RULES at all. They
# cannot be uncovered, because the GATE already refuses one.
#
# So the widening cost nothing and bought the timing, and a check asserting the rung must NOT
# widen now asserts against its own condition being met. Retired by `uncovered-widens-to-rules`;
# what replaces it is tests/engine/test_uncovered_widens_to_rules.py, which pins the exemptions
# the rung still grants.


def test_a_template_edge_is_not_an_obligation(bundle):
    """covers: M4, A3, E2 — an untouched slot owes nothing; only a FILLED line binds."""
    armed = task(bundle, "armed-filled", edges="- E1 a FILLED boundary case")
    assert "UNCOVERED" in _freeze(bundle, armed)[1], "the rung never fires, so this proves nothing"

    cid = task(bundle, "template-edge",
               edges="- E1 <a boundary or failure case a check must cover — optional>",
               checks="- test_one · covers: M1, R:THING · the rules, so only the edge is at issue")
    ok, note = _freeze(bundle, cid)
    assert ok, f"an untouched template edge was read as an obligation:\n{note}"
    no_probe = task(bundle, "no-probe", edges="- E1 x",
                    checks="- t · covers: M1, R:THING, E1 · p")
    assert _freeze(bundle, no_probe)[0], "an assumption declaring no probe was read as one"


def test_the_unswept_refusal_still_comes_first(bundle):
    """covers: M5, A5, E3 — the ladder order is tuned; a new rung does not jump it."""
    cid = task(bundle, "both-wrong", unswept=True, edges="- E1 a boundary case")
    ok, note = _freeze(bundle, cid)
    assert not ok and "unswept" in note, f"the new rung jumped the sweep:\n{note}"
    assert "UNCOVERED" not in note, note
    # And it was queued behind the sweep, not absent: clear the sweep and the SAME node refuses.
    swept = task(bundle, "swept-now", edges="- E1 a boundary case")
    ok, note = _freeze(bundle, swept)
    assert not ok and "UNCOVERED" in note, \
        f"the sweep was merely first because nothing came after it:\n{note}"


def test_an_absent_checks_section_still_refuses(bundle):
    """covers: A7 — exempting the empty case makes deletion the way past the rung."""
    cid = task(bundle, "no-checks", drop_checks=True, edges="- E1 a boundary case")
    ok, note = _freeze(bundle, cid)
    assert not ok and "UNCOVERED" in note, f"zero covers: lists covered an obligation:\n{note}"


def test_todo_names_the_uncovered_count(bundle):
    """covers: M6, A4, A6, A8 — the count rides the hint chain; zero shows nothing.

    RE-AIMED (uncovered-widens-to-rules): the rule is unchanged — ONE uncovered obligation reads
    as `1 uncovered`. What expired is the premise that the default fixture carries exactly one:
    the widened rung also counts R:THING, so the fixture now covers its Reject and the single
    uncovered edge is again the only thing the count can be about.
    """
    task(bundle, "dirty", edges="- E1 a boundary case",
         checks="- test_one · covers: M1, R:THING · the rules, so only the edge is uncovered")
    _, note = add.todo(bundle)
    assert "1 uncovered" in note, f"todo did not name the count:\n{note}"

    clean = task(bundle, "clean", edges="- E1 a boundary case",
                 checks="- test_one · covers: M1, R:THING, E1 · proves it")
    _, note = add.todo(bundle)
    assert "clean" in note and "0 uncovered" not in note, f"A8 — a zero count was shown:\n{note}"

    assert _freeze(bundle, clean)[0]
    _, note = add.todo(bundle)
    row = next((l for l in note.splitlines() if "clean" in l), "")
    assert "uncovered" not in row, f"A4 — a sealed node was told to edit its CHECKS:\n{row}"


def test_the_refusal_addresses_the_author(bundle):
    """covers: A1, A12 — it names a section to edit, never a person; the row gains no verb."""
    cid = task(bundle, "author-facing", edges="- E1 a boundary case")
    _, note = _freeze(bundle, cid)
    assert "CHECKS" in note, f"the refusal never named the section to edit:\n{note}"
    _, todo_note = add.todo(bundle)
    row = next(l for l in todo_note.splitlines() if "author-facing" in l)
    assert row.count("add ") <= 1, f"A12 — the hint added a second verb to the row:\n{row}"
