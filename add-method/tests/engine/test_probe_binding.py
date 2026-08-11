"""Red suite for `probe-binding` (beta-2, W2) — answer correctness via gate probes.

The sweep makes agents ASK the right questions; nothing makes the answers right, and the
campaign record is blunt about it: two of seven planted items took the wrong reading in
every run. A NO-EXEC notary cannot judge an answer — but it can refuse to call a checkable
answer proven when no check reports on it. That is the same move as covers-binding, applied
to ASSUMPTIONS (blog docket item 4):

  * an assumption line opts in with `· probe: <what shipped behavior must show>` — the
    author declaring "this reading is checkable against the running code";
  * a probed `A<n>` becomes a first-class covers referent, exactly like a Must or an edge:
    some CHECKS line must cite it, and the gate's existing unbound refusal holds the PASS
    until a runner reports that check passing;
  * an unprobed assumption stays what it always was — a priced guess on the record. Opting
    in is the author's honesty; the engine only enforces what was declared checkable.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402
from conftest import DRAFTED_CHECKS, DRAFTED_ASSUMPTIONS  # noqa: E402

PROBED_ASSUMPTIONS = DRAFTED_ASSUMPTIONS.replace(
    "- A1 [who] covers: S1 ·",
    "- A1 [who] covers: S1 · probe: a foreign caller's release is rejected by the shipped API ·",
    1)

PROBED_CHECKS = DRAFTED_CHECKS + "\n- test_foreign_release_rejected · covers: A1 · the probe"


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Probed")
    return tmp_path


def _task(bundle, draft, slug, assumptions, checks):
    cid, _ = add.new(bundle, "Task", slug, title=slug.title())
    draft(bundle, cid, assumptions=assumptions, checks=checks)
    node, note = add.freeze(bundle, cid, by="human:tindang")
    assert node is not None, f"fixture could not freeze: {note!r}"
    add.brief_stamp(bundle, cid, by="cli")
    return cid


def _receipt(bundle, cid, tmp_path, names):
    xml = tmp_path / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{n}"/>' for n in names)
    xml.write_text(f"<testsuites><testsuite>{cases}</testsuite></testsuites>")
    return add.run(bundle, cid, [sys.executable, "-c", "pass"], junit=xml)


GREEN = ("test_atomic_admit", "test_no_overadmit", "test_foreign_release_rejected")


# ----------------------------------------------------------------- M1: the grammar


def test_probed_assumptions_parses_the_opt_in(bundle, draft):
    """covers: M1 — `· probe:` marks the id; unmarked lines stay out."""
    cid = _task(bundle, draft, "parsed", PROBED_ASSUMPTIONS, PROBED_CHECKS)
    node = add.read(bundle / cid.lstrip("/"), "T2")
    assert add.probed_assumptions(node) == ["A1"]


def test_a_probed_assumption_is_a_referent(bundle, draft):
    """covers: M1 — probed ids bind exactly like Musts and edges (C7's move, again)."""
    cid = _task(bundle, draft, "referent", PROBED_ASSUMPTIONS, PROBED_CHECKS)
    node = add.read(bundle / cid.lstrip("/"), "T2")
    assert "A1" in add.referents_of(node)
    assert add.REFERENT.match("A1"), "the checks compiler must accept an A id as a citation"


def test_an_unprobed_assumption_is_not_a_referent(bundle, draft):
    """covers: M2, E1 — opting in is the author's; the engine never conscripts a guess."""
    cid = _task(bundle, draft, "guessy", DRAFTED_ASSUMPTIONS, DRAFTED_CHECKS)
    node = add.read(bundle / cid.lstrip("/"), "T2")
    assert add.probed_assumptions(node) == []
    assert not [r for r in add.referents_of(node) if r.startswith("A")]


# ----------------------------------------------------------------- M2: the gate holds it


def test_gate_refuses_a_probed_assumption_with_no_passing_check(bundle, draft, tmp_path):
    """covers: M2 — declared checkable, checked by nothing: the PASS waits."""
    cid = _task(bundle, draft, "unproven", PROBED_ASSUMPTIONS, DRAFTED_CHECKS)
    _receipt(bundle, cid, tmp_path, GREEN[:2])
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is False, "a probed assumption with no covering check was gated PASS"
    assert "A1" in note, f"the refusal must name the unproven probe: {note!r}"


def test_gate_refuses_when_the_probe_check_did_not_pass(bundle, draft, tmp_path):
    """covers: M2 — cited but not reported passing is not proven (bind's own rule)."""
    cid = _task(bundle, draft, "redprobe", PROBED_ASSUMPTIONS, PROBED_CHECKS)
    _receipt(bundle, cid, tmp_path, GREEN[:2])          # probe check never reported
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is False
    assert "A1" in note, note


def test_gate_passes_a_probed_assumption_with_a_passing_probe(bundle, draft, tmp_path):
    """covers: M3 — the real path: probe declared, cited, reported passing."""
    cid = _task(bundle, draft, "proven", PROBED_ASSUMPTIONS, PROBED_CHECKS)
    _receipt(bundle, cid, tmp_path, GREEN)
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is True, note


def test_unprobed_lines_do_not_block_the_gate(bundle, draft, tmp_path):
    """covers: E1 — the beta-1 shape still gates: assumptions without probes bind nothing."""
    cid = _task(bundle, draft, "plain", DRAFTED_ASSUMPTIONS, DRAFTED_CHECKS)
    _receipt(bundle, cid, tmp_path, GREEN[:2])
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is True, note


# ----------------------------------------------------------------- E: honest edges


def test_a_placeholder_probe_never_reaches_the_gate(bundle, draft):
    """covers: E2 — `probe: <what to check>` is a scaffold stub; freeze already refuses it."""
    cid, _ = add.new(bundle, "Task", "stubbed", title="Stubbed")
    draft(bundle, cid, assumptions=DRAFTED_ASSUMPTIONS.replace(
        "- A1 [who] covers: S1 ·",
        "- A1 [who] covers: S1 · probe: <what shipped behavior must show> ·", 1))
    node, note = add.freeze(bundle, cid, by="human:tindang")
    assert node is None, "a placeholder probe was frozen"
    assert "placeholder" in note.lower(), note


def test_scaffold_teaches_the_probe(bundle):
    """covers: M4 — taught at the moment of use: the ASSUMPTIONS scaffold names the opt-in."""
    cid, _ = add.new(bundle, "Task", "taught", title="Taught")
    body = add.read(bundle / cid.lstrip("/"), "T2")["body"]
    section = add._section_of(body, "ASSUMPTIONS")
    assert "probe:" in section, "the scaffold never mentions the probe opt-in"
