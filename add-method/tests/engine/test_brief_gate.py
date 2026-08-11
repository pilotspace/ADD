"""Red suite for `brief-gate` (beta-2, W1) — the brief is Build's ENTRY, not the verdict's garnish.

3.0.0-beta.1 compiles the XML brief and stamps its hash at GATE time (A16), which records what
the instructions *would have been* — after the build is over. Using the brief during Build was
recommended prose, and three probe campaigns documented what happens to recommended prose: it
gets routed around. This suite makes the brief a checkpoint:

  * `add brief` on a FROZEN task records an `act: brief` stamp carrying the compiled hash —
    the moment the sealed direction became a working prompt.
  * `gate PASS` refuses when no brief stamp sits between the latest (re)freeze and the run
    stamp of the gated receipt. Stamps are append-only, so their order is chronological fact.
  * A brief compiled AFTER the receipt is a decoration, not an entry — refused, with the fix
    naming the re-run.

Exempt, deliberately (same shape as the sweep's exemptions):
  * `depth: quick` — ceremony is tuned by depth; a one-file mechanical edit earns no XML prompt.
  * an unsealed node — a pre-seal freeze is unverifiable, so it is not refusable (R:RETROBREAK).
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Briefed")
    return tmp_path


def _frozen_task(bundle, draft, slug="briefed", **kw):
    cid, _ = add.new(bundle, "Task", slug, title=slug.title(), **kw)
    draft(bundle, cid)
    node, note = add.freeze(bundle, cid, by="human:tindang")
    assert node is not None, f"fixture could not freeze: {note!r}"
    return cid


def _green_receipt(bundle, cid, tmp_path):
    """A receipt whose junit reports both drafted checks passing, so `unbound` is empty."""
    xml = tmp_path / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{n}"/>'
                    for n in ("test_atomic_admit", "test_no_overadmit"))
    xml.write_text(f"<testsuites><testsuite>{cases}</testsuite></testsuites>")
    return add.run(bundle, cid, [sys.executable, "-c", "pass"], junit=xml)


def _stamps(bundle, cid):
    return [s for s in (add.read(bundle / cid.lstrip("/"), "T0")["fm"].get("verified") or [])
            if isinstance(s, dict)]


# ------------------------------------------------------------- M1: the stamp exists and is real


def test_brief_stamp_records_on_a_frozen_task(bundle, draft):
    """covers: M1 — briefing a frozen task appends `act: brief` carrying the compiled hash."""
    cid = _frozen_task(bundle, draft)
    digest, note = add.brief_stamp(bundle, cid, by="cli")
    assert digest and str(digest).startswith("sha256:"), note
    briefs = [s for s in _stamps(bundle, cid) if s.get("act") == "brief"]
    assert briefs, "no `act: brief` stamp was appended"
    assert str(briefs[-1].get("brief", "")).startswith("sha256:"), briefs[-1]


def test_brief_stamp_hash_matches_the_compiler(bundle, draft):
    """covers: M1 — the stamp records THE brief, not a brief: same hash `add brief` prints."""
    cid = _frozen_task(bundle, draft)
    digest, _ = add.brief_stamp(bundle, cid, by="cli")
    assert digest == add.brief(bundle, cid)["hash"], \
        "the stamped hash and the compiled brief diverge — the record is of nothing"


def test_brief_stamp_refuses_an_unfrozen_task(bundle, draft):
    """covers: M1, E1 — before the freeze there is no sealed direction to enter the build."""
    cid, _ = add.new(bundle, "Task", "open", title="Open")
    draft(bundle, cid)
    digest, note = add.brief_stamp(bundle, cid, by="cli")
    assert digest is None, "an unfrozen task recorded a build entry"
    assert not [s for s in _stamps(bundle, cid) if s.get("act") == "brief"], \
        "a refused brief_stamp must write nothing"
    assert "frozen" in note.lower() or "freeze" in note.lower(), note


# --------------------------------------------------- M2: the gate refuses an unbriefed build


def test_gate_pass_refuses_when_no_brief_entered_the_build(bundle, draft, tmp_path):
    """covers: M2, R:UNBRIEFED — sealed direction that never became the working prompt."""
    cid = _frozen_task(bundle, draft)
    _green_receipt(bundle, cid, tmp_path)
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is False, "an unbriefed build was gated PASS"
    assert "brief" in note.lower(), note
    assert f"add brief" in note, f"the refusal must name the fix: {note!r}"


def test_gate_pass_accepts_brief_then_build(bundle, draft, tmp_path):
    """covers: M2 — the real path: freeze → brief → run → gate. Must not block it."""
    cid = _frozen_task(bundle, draft)
    add.brief_stamp(bundle, cid, by="cli")
    _green_receipt(bundle, cid, tmp_path)
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is True, note


def test_a_brief_after_the_receipt_is_not_an_entry(bundle, draft, tmp_path):
    """covers: M2, R:GARNISH — briefing after the build is the beta-1 behaviour, refused."""
    cid = _frozen_task(bundle, draft)
    _green_receipt(bundle, cid, tmp_path)
    add.brief_stamp(bundle, cid, by="cli")
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is False, "a post-hoc brief bought a PASS — the entry must precede the evidence"
    assert "add run" in note, f"the fix is a re-run under the brief: {note!r}"


def test_a_refreeze_resets_the_entry(bundle, draft, tmp_path):
    """covers: M2, E2 — a re-sealed direction is a NEW direction; the old brief did not enter it."""
    cid = _frozen_task(bundle, draft)
    add.brief_stamp(bundle, cid, by="cli")
    draft(bundle, cid, checks="- test_atomic_admit · covers: M1 · reworded\n"
                              "- test_no_overadmit · covers: R:OVERADMIT · reworded")
    node, note = add.freeze(bundle, cid, by="human:tindang")
    assert node is not None, note
    _green_receipt(bundle, cid, tmp_path)
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is False, "a pre-refreeze brief satisfied the post-refreeze build"


def test_non_pass_verdicts_are_never_blocked(bundle, draft, tmp_path):
    """covers: M3 — a verdict is how a node LEAVES a bad state (same stance as R:TRAP)."""
    cid = _frozen_task(bundle, draft)
    _green_receipt(bundle, cid, tmp_path)
    ok, note = add.gate(bundle, cid, "RISK-ACCEPTED", by="human:tindang",
                        reason="shipping the spike as-is")
    assert ok is True, note


# ------------------------------------------------------------------------- E: the exemptions


def test_quick_depth_is_exempt(bundle, draft, tmp_path):
    """covers: E3 — depth tunes ceremony; a quick lane task earns no XML prompt demand."""
    cid = _frozen_task(bundle, draft, slug="quickie", depth="quick")
    _green_receipt(bundle, cid, tmp_path)
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is True, note


def test_an_unsealed_node_is_exempt(bundle, draft, tmp_path):
    """covers: E4, R:RETROBREAK — no seal, nothing verifiable, nothing refusable."""
    cid = _frozen_task(bundle, draft, slug="legacy")
    path = bundle / cid.lstrip("/")
    stripped = "\n".join(l.split(", direction:")[0] + " }" if ", direction:" in l else l
                         for l in path.read_text().splitlines())
    path.write_text(stripped)
    _green_receipt(bundle, cid, tmp_path)
    ok, note = add.gate(bundle, cid, "PASS", by="human:tindang")
    assert ok is True, note


# ------------------------------------------------------- M4: taught at the moment of use


def test_freeze_note_points_at_the_brief(bundle, draft):
    """covers: M4 — the freeze's `next:` is the brief, not a bare `add run`."""
    cid, _ = add.new(bundle, "Task", "pointed", title="Pointed")
    draft(bundle, cid)
    _, note = add.freeze(bundle, cid, by="human:tindang")
    assert "add brief" in note, f"freeze must hand the author the entry verb: {note!r}"


def test_todo_hints_brief_for_a_frozen_unbriefed_task(bundle, draft):
    """covers: M4 — the build beat's next verb is `add brief` until the entry is recorded."""
    cid = _frozen_task(bundle, draft, slug="hinted")
    items, _ = add.todo(bundle)
    verbs = {c.rsplit("/", 1)[-1][:-3]: nxt for c, _, nxt in items}
    assert "add brief" in verbs["hinted"], verbs
    add.brief_stamp(bundle, cid, by="cli")
    items, _ = add.todo(bundle)
    verbs = {c.rsplit("/", 1)[-1][:-3]: nxt for c, _, nxt in items}
    assert "add run" in verbs["hinted"], f"once briefed, the hint moves on: {verbs}"


def test_cli_brief_records_the_stamp(bundle, draft, capsys):
    """covers: M5 — the CLI verb an agent actually types records the entry."""
    sys.path.insert(0, str(REPO / "tooling"))
    import cli
    cid = _frozen_task(bundle, draft, slug="typed")
    rc = cli.main(["--root", str(bundle), "brief", "typed"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "<task" in out, "the brief text itself must still print"
    assert [s for s in _stamps(bundle, cid) if s.get("act") == "brief"], \
        "the CLI compiled without recording the entry"
