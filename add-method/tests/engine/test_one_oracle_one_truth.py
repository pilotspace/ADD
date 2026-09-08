"""Red suite for `one-oracle-one-truth` — one placeholder rule, one covers grammar, no stale number.

The placeholder oracle has four readers and two rules: `placeholders_in` and `_placeholder_only`
strip backticked spans before matching, `gives_unauthored` and the milestone EXIT box check do
not. A line written in the engine's own vocabulary therefore reads as unauthored scaffold — it
refused this milestone's own freeze twice.

`covers:` is worse than inconsistent. The ASSUMPTIONS reader takes everything up to the next
separator; the CHECKS reader splits on commas ALONE. So `covers: M1 E1` in CHECKS parses as one
rule named "M1 E1", matches nothing, and binds NOTHING while looking correct — the vacuous-binding
class this whole milestone exists to close.
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

TOKEN_LINE = "- E1 a criterion naming `E<n>` and `A<n>` in the engine's own vocabulary"
SLOT_LINE = "- E1 <a boundary or failure case a check must cover — optional>"


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Oracle")
    return tmp_path


def _exit_reads_authored(root, slug, criterion):
    """The milestone EXIT box check, reached through the refusal it drives."""
    add.new(root, "Milestone", slug, title=slug)
    p = Path(root) / "milestones" / f"{slug}.md"
    s = p.read_text().replace("goal: <one line>", "goal: g") \
                     .replace("why: <why this milestone exists — required>", "why: w") \
                     .replace("- [ ] <criterion>   (← <task>)", f"- [ ] {criterion}   (a task)") \
                     .replace("evidence: <one row per task>", "evidence: e")
    p.write_text(s)
    node, note = add.freeze(root, f"/milestones/{slug}.md", by="plan:x", authority="plan")
    return bool(node), note


def test_all_four_placeholder_readers_agree(bundle):
    """covers: M1, A3, A12, E1 — the defect IS disagreement, so compare them."""
    line = "S1 the `<n>`-indexed slot this publishes"
    verdicts = {
        "placeholders_in": bool(add.PLACEHOLDER.search(re.sub(r"`[^`]*`", "", line))),
        "_placeholder_only": add._placeholder_only(line),
        "gives_unauthored": add.gives_unauthored({"fm": {"gives": [line]}}),
    }
    assert len(set(verdicts.values())) == 1, \
        f"the readers disagree about one line: {verdicts}"
    assert not any(verdicts.values()), \
        f"a backticked engine token was read as a template slot: {verdicts}"
    ok, note = _exit_reads_authored(bundle, "m-token",
                                    "the `add fold --bind` call writes `## Decisions that bind`")
    assert ok, f"A12 — a criterion in the engine's own vocabulary could not freeze:\n{note}"


def test_a_real_placeholder_still_refuses(bundle):
    """covers: M5, R:LOOSENED, A7, E2, E4 — agreement must not become permissiveness."""
    assert add.gives_unauthored({"fm": {"gives": ["S1 <the surface this publishes>"]}}), \
        "R:LOOSENED — a real slot outside backticks was accepted"
    assert add._placeholder_only("- <the first decision that constrains the rest>")
    assert add.gives_unauthored({"fm": {}}), "A7 — an absent gives: stopped reading unauthored"
    assert add.gives_unauthored({"fm": {"gives": []}}), "A7 — an empty gives: was accepted"
    ok, note = _exit_reads_authored(bundle, "m-slot", "<criterion>")
    assert not ok and "scaffold" in note, f"E2 — a real slot froze clean:\n{note}"


def _covers_of(root, slug, checks):
    add.new(root, "Task", slug, title=slug)
    p = Path(root) / "tasks" / f"{slug}.md"
    s = p.read_text()
    s = s[:s.index("## CHECKS")] + "## CHECKS\n" + checks + "\n\n## EVIDENCE\nreceipt: x\n"
    p.write_text(s)
    return add.covers({"path": p})


def test_covers_splits_on_commas_or_whitespace(bundle):
    """covers: M2, A4, A10, E3 — one grammar, or a space-separated list binds nothing."""
    want = {"M1", "E1", "A2"}
    comma = _covers_of(bundle, "c-comma", "- test_x · covers: M1, E1, A2 · proves it")
    space = _covers_of(bundle, "c-space", "- test_x · covers: M1 E1 A2 · proves it")
    mixed = _covers_of(bundle, "c-mixed", "- test_x · covers: M1, E1 A2 · proves it")
    assert set(comma) == want, comma
    assert set(space) == want, f"a space-separated covers: bound {set(space)}, not {want}"
    assert set(mixed) == want, f"a mixed covers: bound {set(mixed)}, not {want}"
    assert list(space) == list(comma), f"A10 — document order was not preserved: {space}"


def test_covers_invents_no_referent(bundle):
    """covers: R:SILENTBIND, A8, E5 — never produce a name no rule could match."""
    empty = _covers_of(bundle, "c-empty", "- test_x · covers:  · proves nothing")
    assert empty == {}, f"an empty covers: produced referents: {empty}"
    assert "" not in empty, "R:SILENTBIND — an empty-string referent was produced"
    absent = _covers_of(bundle, "c-absent", "- test_x · covers: M99 · names a rule that is not there")
    assert set(absent) == {"M99"}, absent
    node = {"path": Path(bundle) / "tasks" / "c-absent.md"}
    assert "M99" not in add.referents_of(node), "E5 — an absent rule was invented as a referent"


def test_the_front_door_guard_states_the_real_output():
    """covers: M3, A5 — a guard that misstates the thing it guards teaches the wrong claim."""
    src = (REPO / "tests" / "skill" / "test_front_door_claims_hold.py").read_text()
    assert "[LENS] spec: text" not in src, "the retired output form is still stated"
    assert "/specs/" in src and "#" in src, "the real address form is stated nowhere"


def test_the_persona_cites_the_pin():
    """covers: M4, R:RECOPIED, A2, A9, A14 — one writer of a number, and it is the test."""
    persona = (REPO.parent / ".add" / "personas" / "method-steward.md").read_text()
    assert "test_surface" in persona, "A9 — the persona cites no pin file"
    for stale in ("150", "176"):
        assert stale not in persona, \
            f"R:RECOPIED — the persona still carries the literal {stale}; cite the test, not its value"
