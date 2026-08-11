"""Red suite for `freeze-seal` — freeze fails fast, and what it froze stays frozen.

Two defects found by driving 3.0.0-beta.1 cold on a real project and comparing against 2.5.0:

**F1 — freeze regressed.** 3.0's `freeze()` only appended a stamp, so it accepted a node that was
100% unedited scaffold. 2.5.0 refused the same act (`contract_not_drafted`). The detector already
existed — `placeholders_in()` — and was wired into `gate`, where it correctly refuses. So a template
could never reach PASS and the end state was safe, but detection had moved from BEFORE Build to
AFTER it: the agent writes every line of code, then learns direction was never authored. That
inverts constraint 1 ("Direction before speed"), which is the entire purpose of the freeze stamp.

**F2 — freeze sealed nothing.** The stamp carried no digest of what was frozen, so post-freeze edits
to RULES/CHECKS were structurally invisible. Demonstrated on the bench: two frozen checks gutted to
`assert True` (same test names, so the `covers:` binding still matched) gated PASS and auto-closed.

The SEMANTIC half of constraint 3 is not enforceable by a NO-EXEC notary — no static engine can tell
a real assertion from `assert True`, and the skill states it as a rule the agent follows, not a
guarantee the engine makes. The STRUCTURAL half is cheap and is what this closes: the engine already
digests scope for receipts, so it can digest direction for freezes. A deliberate change is still
allowed — it just has to be *recorded*, by refreezing, which §3.5 already models as append-only
history. A silent edit is what stops being possible.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Seal")
    return tmp_path


# --------------------------------------------------------------- M1: freeze fails fast


def test_freeze_refuses_an_unauthored_template(bundle):
    """covers: M1 — the 2.5.0 behaviour, restored: a scaffold cannot be approved."""
    cid, _ = add.new(bundle, "Task", "scaffold", title="Never drafted")

    node, note = add.freeze(bundle, cid, by="human:tindang")

    assert node is None, "freeze stamped a node that is still 100% template"
    assert "placeholder" in note.lower(), f"the refusal must name the cause: {note!r}"
    stamps = add.read(bundle / cid.lstrip("/"), "T0")["fm"].get("verified") or []
    assert not stamps, "a refused freeze must write nothing"


def test_freeze_names_the_placeholders_it_refuses_over(bundle):
    """covers: M1 — an actionable refusal points at the lines to author (the gate already does)."""
    cid, _ = add.new(bundle, "Task", "named", title="Named")
    _, note = add.freeze(bundle, cid, by="human:tindang")
    assert "M1" in note and "test_name" in note, f"the refusal must quote the stub lines: {note!r}"


def test_freeze_accepts_an_authored_node(bundle, draft):
    """covers: M1 — the check must not block the real path."""
    cid, _ = add.new(bundle, "Task", "drafted", title="Drafted")
    draft(bundle, cid)

    node, note = add.freeze(bundle, cid, by="human:tindang")

    assert node is not None, f"an authored node was refused: {note!r}"
    stamps = add.read(bundle / cid.lstrip("/"), "T0")["fm"]["verified"]
    assert any(s.get("act") == "freeze" for s in stamps)


def test_a_non_lifecycle_node_is_unaffected(bundle):
    """covers: M1, E1 — a Milestone carries no RULES/CHECKS; the check must not invent a refusal."""
    cid, _ = add.new(bundle, "Milestone", "ms", title="A milestone")
    node, note = add.freeze(bundle, cid, by="human:tindang")
    assert node is not None, f"freezing a Milestone should not trip the placeholder check: {note!r}"


# --------------------------------------------------------- M2: the stamp seals what it froze


def test_freeze_stamps_a_direction_digest(bundle, draft):
    """covers: M2 — the stamp records WHAT was approved, not merely that approval happened."""
    cid, _ = add.new(bundle, "Task", "sealed", title="Sealed")
    draft(bundle, cid)
    add.freeze(bundle, cid, by="human:tindang")

    stamp = [s for s in add.read(bundle / cid.lstrip("/"), "T0")["fm"]["verified"]
             if s.get("act") == "freeze"][-1]
    assert str(stamp.get("direction", "")).startswith("sha256:"), \
        f"the freeze stamp carries no direction digest: {stamp}"


def test_the_digest_changes_when_checks_change(bundle, draft):
    """covers: M2, R:GREENLIE — a detector that cannot fire is not a gate (mutation check)."""
    cid, _ = add.new(bundle, "Task", "mutates", title="Mutates")
    draft(bundle, cid)
    before = add.direction_digest(add.read(bundle / cid.lstrip("/"), "T2"))

    draft(bundle, cid, checks="- test_atomic_admit · covers: M1 · REWORDED")
    after = add.direction_digest(add.read(bundle / cid.lstrip("/"), "T2"))

    assert before != after, "the digest is blind to a CHECKS edit — it would seal nothing"


def test_the_digest_covers_a_frozen_gives(bundle, draft):
    """covers: M2, E4 — constraint 3 names `gives:` alongside the checks; the seal must too."""
    cid, _ = add.new(bundle, "Task", "publishes", title="Publishes")
    path = draft(bundle, cid)
    # EDIT the scaffolded `gives:`, never inject a second key: since 3.0.0-beta.2 the
    # scaffold ships one, and a duplicate key would leave the parser reading the first —
    # so the edit would be invisible and this test would pass for the wrong reason.
    path.write_text(path.read_text().replace(
        "- S1 admit(token) — the admission decision", "- S1 api.Widget"))
    before = add.direction_digest(add.read(path, "T2"))

    path.write_text(path.read_text().replace("- S1 api.Widget", "- S1 api.WidgetV2"))
    after = add.direction_digest(add.read(path, "T2"))

    assert before != after, "editing a frozen `gives:` left the seal unchanged"


def test_the_digest_ignores_unrelated_body_edits(bundle, draft):
    """covers: M2, E2 — sealing RULES+CHECKS must not make every CARD typo a contract change."""
    cid, _ = add.new(bundle, "Task", "cardedit", title="Card edit")
    path = draft(bundle, cid)
    before = add.direction_digest(add.read(path, "T2"))

    path.write_text(path.read_text().replace("goal: <one line>", "goal: a real goal"))
    after = add.direction_digest(add.read(path, "T2"))

    assert before == after, "a CARD edit changed the direction digest — too broad a seal"


# ------------------------------------------------- M3: the gate refuses post-freeze drift


def test_gate_refuses_a_pass_when_checks_drifted_after_freeze(bundle, draft):
    """covers: M3 — the bench's `assert True` gutting, refused."""
    cid, _ = add.new(bundle, "Task", "drifted", title="Drifted")
    draft(bundle, cid)
    add.freeze(bundle, cid, by="human:tindang")

    draft(bundle, cid, checks="- test_atomic_admit · covers: M1 · GUTTED")
    add.run(bundle, cid, ["python3", "-c", "pass"])
    _, note = add.gate(bundle, cid, "PASS", by="human:tindang")

    assert "drift" in note.lower() or "frozen" in note.lower(), \
        f"a post-freeze CHECKS edit gated PASS anyway: {note!r}"
    assert "freeze" in note, "the refusal must name the remedy — refreeze records the change"


def test_a_refreeze_reseals_and_the_gate_proceeds(bundle, draft):
    """covers: M3, E3 — a deliberate change is allowed; it just has to be recorded."""
    cid, _ = add.new(bundle, "Task", "resealed", title="Resealed")
    draft(bundle, cid)
    add.freeze(bundle, cid, by="human:tindang")
    draft(bundle, cid, checks="- test_atomic_admit · covers: M1 · a deliberate rewording")

    node, note = add.freeze(bundle, cid, by="human:tindang")
    assert node is not None, f"a refreeze of an authored node was refused: {note!r}"

    stamp = [s for s in add.read(bundle / cid.lstrip("/"), "T0")["fm"]["verified"]
             if s.get("act") in ("freeze", "refreeze")][-1]
    assert add.direction_digest(add.read(bundle / cid.lstrip("/"), "T2")) == stamp.get("direction"), \
        "the refreeze did not re-seal to the current content"


def test_an_undrifted_node_still_gates(bundle, draft):
    """covers: M3 — the seal must not block the happy path (R:FALSEPOSITIVE)."""
    cid, _ = add.new(bundle, "Task", "clean", title="Clean")
    draft(bundle, cid)
    add.freeze(bundle, cid, by="human:tindang")
    add.run(bundle, cid, ["python3", "-c", "pass"])

    _, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert "drift" not in note.lower(), f"an unedited frozen node was refused as drifted: {note!r}"


def test_a_legacy_stamp_without_a_digest_still_gates(bundle, draft):
    """covers: R:RETROBREAK — bundles frozen by an older engine must not become ungateable."""
    cid, _ = add.new(bundle, "Task", "legacy", title="Legacy")
    draft(bundle, cid)
    add.freeze(bundle, cid, by="human:tindang")

    path = bundle / cid.lstrip("/")
    raw = path.read_text()
    stripped = "\n".join(l.split(", direction:")[0] + " }" if ", direction:" in l else l
                         for l in raw.splitlines())
    path.write_text(stripped)
    assert "direction:" not in path.read_text(), "the fixture failed to strip the digest"

    add.run(bundle, cid, ["python3", "-c", "pass"])
    _, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert "drift" not in note.lower(), \
        f"a pre-seal bundle was refused — the check must skip what it cannot verify: {note!r}"
