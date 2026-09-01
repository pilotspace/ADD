"""The Task node records what the spec did NOT say.

`SKILL.md:66` and `phases/direction.md:29` both instruct the author to record "the one
riskiest assumption ... do not bury it". The Task template had nowhere to put one, and
neither `freeze` nor `gate` ever asked for it — so it cost nothing to skip, and it was
skipped.

Measured, not assumed. The amb1 workload plants one self-contradiction and six SILENCES
(gaps and traps). The live add arm surfaced the contradiction and none of the six, and
the transcript shows why: every ambiguity it met became a Must written in the same
authoritative voice as a requirement the spec had actually stated —

    M4 GET /bookings returns all bookings (any status) as a JSON list.

The spec never says whether a caller sees everyone's bookings. That line is a DECISION
wearing a requirement's clothes, and `test_list_bookings · covers: M4` then bound it to
a passing check. Nothing in the artifact distinguished "we were told this" from "we
decided this".

All four of that node's EDGES were interior boundaries of rules it had already written
(E1/E2 from M9, E3 from M6, E4 from M2+M3). EDGES enumerates the edges of what you
WROTE; it never probes what you were not told. That is the hole this section fills.

Scope, deliberately: `A<n>` ids are NOT bindable by `covers:` (an assumption is a
declared unknown, not a rule to prove) and are NOT in the direction digest. The digest
is scoped by constraint 3 to the Musts, the Rejects and `gives:` — widening it would
retroactively invalidate every seal already recorded.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tooling"))
import add  # noqa: E402


def _scaffold(tmp_path):
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t1", title="t")
    return tmp_path / cid.lstrip("/")


def test_the_template_ships_an_assumptions_section(tmp_path):
    """covers: M1 — the author needs somewhere to write it."""
    body = _scaffold(tmp_path).read_text(encoding="utf-8")
    assert "## ASSUMPTIONS" in body, "the Task template has no slot for a recorded assumption"


def test_assumptions_sits_between_rules_and_plan(tmp_path):
    """covers: M2 — what is stated, then what is not, then the plan built on both."""
    body = _scaffold(tmp_path).read_text(encoding="utf-8")
    assert body.index("## RULES") < body.index("## ASSUMPTIONS") < body.index("## PLAN")


def test_freeze_refuses_an_unfilled_assumptions_slot(tmp_path):
    """covers: M3, R:UNPRICED — an instruction with no checkpoint is one that does not happen.

    This is the whole point. The skill has asked for the riskiest assumption since 3.0
    and the live run recorded none, because skipping cost nothing.
    """
    node = _scaffold(tmp_path)
    body = node.read_text(encoding="utf-8")
    body = body.replace("- M1 <the rule that must hold>", "- M1 a real authored rule")
    body = body.replace('- R:<NAME> <what must never happen> -> "<NAME>"',
                        '- R:REAL a real reject -> "REAL"')
    body = body.replace("- <test_name> · covers: M1 · <what it proves>",
                        "- test_real · covers: M1 · it proves the rule")
    node.write_text(body, encoding="utf-8")          # ASSUMPTIONS left as the template

    found = add.placeholders_in(add.read(node, "T2"))

    assert any("ASSUMPTION" in f.upper() or "spec does not say" in f.lower() or
               "A1" in f for f in found), \
        f"freeze does not notice an unfilled ASSUMPTIONS slot: {found}"


def test_an_authored_assumption_clears_the_freeze(tmp_path):
    """covers: M4 — the gate must be passable, or authors learn to route around it."""
    node = _scaffold(tmp_path)
    body = node.read_text(encoding="utf-8")
    body = body.replace("goal: <one line>", "goal: a real authored goal.")
    body = body.replace("- M1 <the rule that must hold>", "- M1 a real authored rule")
    body = body.replace('- R:<NAME> <what must never happen> -> "<NAME>"',
                        '- R:REAL a real reject -> "REAL"')
    body = body.replace("- <test_name> · covers: M1 · <what it proves>",
                        "- test_real · covers: M1 · it proves the rule")
    body = add.RE_ASSUMPTION_PLACEHOLDER.sub(
        "- A1 the spec never says whether a caller sees other callers' rows; "
        "taking it as own-only -> if wrong, every list response leaks", body)
    node.write_text(body, encoding="utf-8")

    assert not add.placeholders_in(add.read(node, "T2"))


def test_assumption_ids_are_not_bindable_by_covers(tmp_path):
    """covers: R:PROVE_AN_UNKNOWN — an assumption is a declared unknown, not a rule.

    If `A<n>` joined the bindable set, `gate PASS` would demand a passing check for
    every assumption — which would teach authors to record only assumptions they can
    already prove, i.e. the ones that were never risky.
    """
    node = _scaffold(tmp_path)
    body = node.read_text(encoding="utf-8")
    body = add.RE_ASSUMPTION_PLACEHOLDER.sub("- A1 an assumption -> a cost", body)
    node.write_text(body, encoding="utf-8")

    assert "A1" not in add.referents_of(add.read(node, "T2"))


def test_the_assumption_is_not_sealed_by_the_direction_digest(tmp_path):
    """covers: E1 — constraint 3 scopes the seal to Musts, Rejects and `gives:`.

    Widening it here would change the digest of every node already frozen, so every
    existing bundle would report post-freeze drift it never had.
    """
    node = _scaffold(tmp_path)
    n = add.read(node, "T2")
    before = add.direction_digest(n)
    n["body"] = add.RE_ASSUMPTION_PLACEHOLDER.sub("- A1 an assumption -> a cost", n["body"])

    assert add.direction_digest(n) == before


class TestScaffoldCarriesTheRegister:
    """The n=1 probe (runs-amb1-v3): the sweep forced all four blind-spot questions and
    the agent answered every one DECLARATIVELY — "GET /bookings lists every booking",
    "DELETE is permitted for any caller" — the authoritative voice of a stated
    requirement. The section exists to distinguish given from decided, and a reader
    cannot make that distinction from a line that asserts. The register is therefore in
    the SCAFFOLD, at the moment of use (law 4): the slot the author fills starts from
    "the request does not say", so writing an assertion requires deleting the frame
    rather than never seeing it."""

    def test_every_scaffolded_assumption_line_states_the_not_said_register(self, tmp_path):
        body = _scaffold(tmp_path).read_text(encoding="utf-8")
        section = add._section_of(body.split("---", 2)[2], "ASSUMPTIONS")
        lines = [l for l in section.splitlines() if l.startswith("- A")]
        assert len(lines) == len(add.SWEEP_DIMENSIONS)
        for line in lines:
            assert "the request does not say" in line, line

    def test_the_scaffold_separates_reading_from_cost(self, tmp_path):
        # given -> decided -> priced: three slots, so an author states each apart.
        body = _scaffold(tmp_path).read_text(encoding="utf-8")
        for line in add._section_of(body.split("---", 2)[2], "ASSUMPTIONS").splitlines():
            if line.startswith("- A"):
                assert "taking <" in line and "-> <cost if wrong>" in line, line

    def test_the_scaffold_says_one_line_one_silence(self, tmp_path):
        # The probe's A6 bundled three silences into one line covering S2,S3,S4 —
        # unauditable wholesale. The engine cannot police prose density (a notary
        # records), so the rule rides the scaffold's trailing hint instead.
        body = _scaffold(tmp_path).read_text(encoding="utf-8")
        assert "one line, one silence" in add._section_of(body.split("---", 2)[2], "ASSUMPTIONS"), \
            "the bundling rule must be visible at the moment of authoring"
