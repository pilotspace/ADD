"""`done` counted that a gate HAPPENED; it never asked what the gate DECIDED.

Measured 2026-09-02 against the pre-change engine, CLI only, no flags and no hand-editing:
a Task at the security floor, correctly interviewed, frozen at `human`, whose run EXITED 1,
took `gate HARD-STOP` and then closed:

    add gate sec2 HARD-STOP --by tin --reason "SQL injection in login"
        HARD-STOP recorded; sec2 stays in `direction`      <- the engine's own words
    add done sec2
        /tasks/sec2.md is done                             <- and it left the board

`done` (add.py) counts `s.get("act") == "gate"` and never reads `s.get("outcome")`, so every
verdict in VERDICTS entitles the terminal write equally. `_binds()` returns False for HARD-STOP
on every refusal, by design — add.py's own comment says "It never closes a task, so refusing it
would only stop a finding being written down". That premise is what these checks pin: the
comment is correct about `gate`, and `done` is where it was never true.

The split: HARD-STOP stays unrefused AT THE GATE, so a finding is always writable — a security
finding is always a HARD-STOP and must never be hard to record. It is `done` that must decline
to treat the stop as an entitlement. A node that stops is not a node that shipped.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DIMS = ("who", "which", "when", "absent", "order", "experience")


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _authored(root, slug="t", **fields):
    """A Task every authoring guard accepts, so these checks probe the VERDICT, not authoring."""
    cid, _ = add.new(root, "Task", slug, title=slug, **fields)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>",
                  "- S1 the lister")
    t = t.replace("goal: <one line>", "goal: the fixture's stated one line.")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 the lister returns only the caller's rows\n</must>",
               t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>",
               '<reject>\n- R:LEAK another tenant\'s row is returned -> "LEAK"\n</reject>',
               t, flags=re.S)
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + "".join(
        f"- A{i} [{d}] covers: S1 · the request does not say; taking the plain reading -> minor\n"
        for i, d in enumerate(DIMS, 1)) + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_only_own_rows · covers: M1, R:LEAK · proves isolation\nred-first",
               t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid


def _sealed(root, slug="t", **fields):
    """Authored, frozen and briefed — the state any legitimate gate starts from.

    A security-floored node is interviewed first: `freeze` refuses one that was not
    (R:UNINTERVIEWED), which is the same order the measured CLI walk followed.
    """
    cid = _authored(root, slug, **fields)
    # A bare `interview` COMPILES the open decisions and writes nothing; the ids come off that
    # read, so the fixture asks the engine what it wants rather than hard-coding a census that
    # drifts. Answering every one is what the measured CLI walk did.
    _, questions = add.interview(root, cid)
    open_ids = re.findall(r"^(A\d+|M\d+|R:[A-Z0-9_]+)\b", str(questions), re.M)
    if open_ids:
        _, note = add.interview(root, cid, answers={i: "confirm" for i in open_ids}, by="H")
        assert "recorded" in str(note), f"fixture could not interview: {note!r}"
    node, note = add.freeze(root, cid, by="H", authority="human")
    assert node is not None, f"fixture could not freeze: {note!r}"
    add.brief_stamp(root, cid, by="H")
    return cid


def _green_receipt(root, cid, tmp_path, cmd=None):
    """A receipt whose junit reports the node's one drafted check passing, so `unbound` is empty.

    Written BY the command — a report that predates the run reported nothing about it, and is
    downgraded to `kind: command-exit`, which binds no referent.
    """
    xml = tmp_path / f"{cid.rsplit('/', 1)[-1]}.xml"
    doc = ('<testsuites><testsuite>'
           '<testcase classname="c" name="test_only_own_rows"/>'
           '</testsuite></testsuites>')
    return add.run(root, cid,
                   [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"], junit=xml)


def _msg(result):
    """gate/done return tuples whose LAST element is the operator-facing message."""
    return str(result[-1])


def _outcomes(root, cid):
    fm = add.scan(root)[cid]["fm"] or {}
    return [s.get("outcome") for s in (fm.get("verified") or []) if isinstance(s, dict)]


# ------------------------------------------------- M1 · the stop is not an entitlement

def test_done_refuses_a_node_whose_only_gate_was_a_hard_stop(tmp_path):
    """covers: M1 — the measured walk, stopped at the verb that actually writes `done`."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "stopped")
    add.run(root, cid, ["true"])

    ok, *rest = add.gate(root, cid, "HARD-STOP", by="H", reason="the finding")
    assert ok, f"a HARD-STOP must always be RECORDABLE: {_msg((ok, *rest))}"
    assert "HARD-STOP" in _outcomes(root, cid)

    ok, *rest = add.done(root, cid)
    assert not ok, "a HARD-STOP closed the node — the stop was read as an entitlement"
    assert (add.scan(root)[cid]["fm"] or {}).get("status") != "done"


def test_the_security_walk_that_shipped_is_closed(tmp_path):
    """covers: M2 — the whole measured sequence: security floor, red run, HARD-STOP, done."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "sec2", sensitivity="security")
    add.run(root, cid, ["false"])                      # the run EXITED 1

    add.gate(root, cid, "HARD-STOP", by="H", reason="SQL injection in login")
    ok, *rest = add.done(root, cid)

    assert not ok, "a security task with a failed run and a HARD-STOP reached `done`"
    assert (add.scan(root)[cid]["fm"] or {}).get("status") != "done"


def test_the_refusal_names_the_verdict_and_a_next_verb(tmp_path):
    """covers: M3 — every engine refusal names its fix in the same breath (SKILL.md)."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "named")
    add.run(root, cid, ["true"])
    add.gate(root, cid, "HARD-STOP", by="H", reason="the finding")

    msg = _msg(add.done(root, cid))
    assert "HARD-STOP" in msg, f"the refusal does not name the verdict that caused it: {msg!r}"
    assert "next:" in msg, f"the refusal names no next verb: {msg!r}"


# ------------------------------------------------- M4 · it must not over-refuse

def test_a_pass_after_a_hard_stop_still_closes(tmp_path):
    """covers: M4 — a stop that was RESOLVED is the normal path; the latest gate rules."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "resolved")
    _green_receipt(root, cid, tmp_path)
    add.gate(root, cid, "HARD-STOP", by="H", reason="found it")
    ok, *rest = add.gate(root, cid, "PASS", by="H")
    assert ok, f"fixture could not record the resolving PASS: {_msg((ok, *rest))}"

    ok, *rest = add.done(root, cid)
    assert ok, f"a resolved stop was refused: {_msg((ok, *rest))}"


def test_pass_and_risk_accepted_still_close(tmp_path):
    """covers: M4, E1 — the two closing verdicts are untouched by this change."""
    root = _bundle(tmp_path)
    for slug, verdict in (("p", "PASS"), ("ra", "RISK-ACCEPTED")):
        cid = _sealed(root, slug)
        _green_receipt(root, cid, tmp_path)
        ok, *rest = add.gate(root, cid, verdict, by="H", reason="weak but known")
        assert ok, f"{verdict} fixture: {_msg((ok, *rest))}"
        if verdict == "PASS":
            continue          # PASS auto-closes; `done` is RISK-ACCEPTED's separate call
        ok, *rest = add.done(root, cid)
        assert ok, f"{verdict} no longer closes: {_msg((ok, *rest))}"


def test_a_hard_stop_before_the_reopen_does_not_block_a_later_pass(tmp_path):
    """covers: E2 — `reopen` resets the gate; only gates that POSTDATE it are read."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "reopened")
    _green_receipt(root, cid, tmp_path)
    add.gate(root, cid, "PASS", by="H")
    add.reopen(root, cid, to="build", reason="deepened verify found a gap")
    add.brief_stamp(root, cid, by="H")
    _green_receipt(root, cid, tmp_path)
    add.gate(root, cid, "HARD-STOP", by="H", reason="the gap is a finding")

    ok, *_ = add.done(root, cid)
    assert not ok, "the reopened node closed on a HARD-STOP"

    add.gate(root, cid, "PASS", by="H")
    ok, *rest = add.done(root, cid)
    assert ok, f"the resolving PASS after a reopen was refused: {_msg((ok, *rest))}"


# ============================================================ the human's corrections
#
# Interviewed 2026-09-03. Four readings were marked `correct`, and A1's literal form could not
# be built: a gate's authority is COMPUTED from the node's floor, so on a security task EVERY
# HARD-STOP is stamped `human` — "a human-authority stop closes the node" would have restored
# the exact walk this task exists to close. Resolved by the human: the force-close is a
# DELIBERATE ACT, not something the computed floor grants.


def test_a_human_may_force_close_a_stopped_node_with_a_reason(tmp_path):
    """covers: M6, A1 — the human CAN ship over a finding, and the ledger says they chose to."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "overridden", sensitivity="security")
    add.run(root, cid, ["false"])
    add.gate(root, cid, "HARD-STOP", by="H", reason="SQL injection in login")

    ok, *_ = add.done(root, cid)
    assert not ok, "the stop did not hold without an override"

    ok, *rest = add.done(root, cid, override="in dead code, tracked as SEC-412")
    assert ok, f"a human could not force-close a stopped node: {_msg((ok, *rest))}"
    assert (add.scan(root)[cid]["fm"] or {}).get("status") == "done"


def test_the_override_is_recorded_with_its_reason(tmp_path):
    """covers: M6, A1 — a silent override is the floor granting it again, one flag over."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "recorded", sensitivity="security")
    add.run(root, cid, ["false"])
    add.gate(root, cid, "HARD-STOP", by="H", reason="the finding")
    add.done(root, cid, override="accepted for the release", by="Tin Dang")

    stamps = [s for s in ((add.scan(root)[cid]["fm"] or {}).get("verified") or [])
              if isinstance(s, dict) and s.get("act") == "done"]
    assert stamps, "the override closed the node and wrote no stamp"
    assert "accepted for the release" in str(stamps[-1].get("override", "")), stamps[-1]
    assert stamps[-1].get("by") == "Tin Dang", stamps[-1]


def test_an_override_without_a_reason_is_refused(tmp_path):
    """covers: M6, R:STOPSHIPS — shipping over a finding is exactly what must be explained."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "unreasoned", sensitivity="security")
    add.run(root, cid, ["false"])
    add.gate(root, cid, "HARD-STOP", by="H", reason="the finding")

    ok, *rest = add.done(root, cid, override="")
    assert not ok, "a stopped node was force-closed with no reason recorded"
    assert "reason" in _msg((ok, *rest)).lower(), _msg((ok, *rest))


def test_the_override_does_not_bypass_the_seal(tmp_path):
    """covers: M6, E3, A1 — it answers the VERDICT, never the ONE approval."""
    root = _bundle(tmp_path)
    cid = _authored(root, "unsealed-override")      # never frozen
    add.run(root, cid, ["true"])
    add.gate(root, cid, "HARD-STOP", by="H", reason="the finding")

    ok, *rest = add.done(root, cid, override="shipping anyway")
    assert not ok, "the override waved through a node the ONE human approval never touched"


def test_gate_refuses_a_hard_stop_on_a_node_that_was_never_frozen(tmp_path):
    """covers: M7, A3 — the human's correction: a stop is a RECORD, and a record needs a seal."""
    root = _bundle(tmp_path)
    cid = _authored(root, "nofreeze")
    add.run(root, cid, ["true"])

    ok, *rest = add.gate(root, cid, "HARD-STOP", by="H", reason="a finding")
    assert not ok, "a HARD-STOP was recorded against a node nobody ever approved"
    assert "R:UNSEALED" in _msg((ok, *rest)), _msg((ok, *rest))


def test_a_hard_stop_on_a_sealed_node_is_still_always_recordable(tmp_path):
    """covers: M7, A3 — the counter-guard: writing down a finding must not get hard."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "sealedstop", sensitivity="security")
    add.run(root, cid, ["false"])

    ok, *rest = add.gate(root, cid, "HARD-STOP", by="H", reason="SQL injection")
    assert ok, f"a sealed node could not record its finding: {_msg((ok, *rest))}"


def test_a_gate_stamp_with_no_readable_outcome_still_closes(tmp_path):
    """covers: M8, A4 — the human's correction: an unreadable verdict fails OPEN."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "oldstamp")
    _green_receipt(root, cid, tmp_path)
    add.gate(root, cid, "PASS", by="H")

    p = root / cid.lstrip("/")
    p.write_text(re.sub(r", outcome: PASS", "", p.read_text(encoding="utf-8")), encoding="utf-8")
    add._transition(root, cid, sets={"status": "verify"})

    ok, *rest = add.done(root, cid)
    assert ok, (
        "a stamp written by an engine that recorded no `outcome` was stranded: "
        + _msg((ok, *rest)))


def test_an_interview_sidecar_is_a_conforming_node(tmp_path):
    """covers: M9, R:UNSCANNABLE — found by running this very task's own interview.

    `run` writes its receipt with frontmatter (`task: /tasks/<slug>.md`); `interview` wrote its
    sidecar as bare markdown, so `doctor` reported `error missing_frontmatter` against a file
    the engine had just created correctly. A notary that manufactures its own conformance error
    is the `orphan_receipt` shape one verb over.
    """
    root = _bundle(tmp_path)
    cid = _sealed(root, "sidecar", sensitivity="security")
    findings = add.doctor(root)
    findings = findings[1] if isinstance(findings, tuple) else findings
    bad = [f for f in findings if "interviews/" in str(f)]
    assert not bad, f"`interview` wrote a file its own doctor rejects: {bad}"
