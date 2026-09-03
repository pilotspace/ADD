"""A verb reads the flag it accepts, and refuses a node it cannot find. Never silently neither.

Two measured drops, one shape: the engine took input, reported success, and did nothing with it.

    $ add gate close-acct PASS --by "Ada" --authority human
    gate PASS recorded at authority `process`          <- the flag was parsed and discarded

`cli.py` declares `--authority` on `gate` and passes it into `add.gate(..., authority=...)`;
`gate` then reassigns its own parameter from `authority_for(graph, cid)` before any read. The
flag has never done anything. GETTING-STARTED teaches this exact flag on `freeze`, with the
reason a reader carries straight to `gate`: "a ledger of process stamps cannot be told apart
from an agent approving its own work".

    $ add run auth-fx -- true          # the user typo'd `auth-fix`
    receipt 1 recorded (exit 0)
    next: add gate auth-fx

`run` is the only verb whose node lookup is `scan(root).get(cid) or {}`. Every other verb
returns `no such node`. It fabricates a receipt for a node that does not exist, prints a green
line and a `next:` pointing at nothing — and `doctor` afterwards reports the `orphan_receipt`
it just manufactured, one verb too late.

`init` already set the stance both of these break: it REFUSES an unknown `--profile` rather
than guess. Accepting-and-dropping is the one option that misleads.
"""
import re
import subprocess
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
    cid = _authored(root, slug, **fields)
    _, questions = add.interview(root, cid)
    ids = re.findall(r"^(A\d+|M\d+|R:[A-Z0-9_]+)\b", str(questions), re.M)
    if ids:
        add.interview(root, cid, answers={i: "confirm" for i in ids}, by="H")
    node, note = add.freeze(root, cid, by="H", authority="human")
    assert node is not None, f"fixture could not freeze: {note!r}"
    add.brief_stamp(root, cid, by="H")
    return cid


def _green_receipt(root, cid, tmp_path):
    xml = tmp_path / f"{cid.rsplit('/', 1)[-1]}.xml"
    doc = ('<testsuites><testsuite>'
           '<testcase classname="c" name="test_only_own_rows"/></testsuite></testsuites>')
    return add.run(root, cid,
                   [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"], junit=xml)


def _stamps(root, cid):
    fm = add.scan(root)[cid]["fm"] or {}
    return [s for s in (fm.get("verified") or []) if isinstance(s, dict)]


# ------------------------------------------------- M1 · run refuses a phantom node

def test_run_refuses_a_node_that_does_not_exist(tmp_path):
    """covers: M1, R:PHANTOMRECEIPT — the measured typo, and the debris it left behind."""
    root = _bundle(tmp_path)
    add.new(root, "Task", "auth-fix", title="auth-fix")

    result = add.run(root, "/tasks/auth-fx.md", ["true"])
    note = str(result["note"])                 # `run` returns a dict; the refusal keeps its shape
    assert "no such node" in note, f"a receipt was fabricated for a node that does not exist: {note}"
    assert not (root / "tasks" / "auth-fx.d").exists(), "it refused and wrote the receipt anyway"


def test_run_still_records_for_a_real_node(tmp_path):
    """covers: M2 — the guard refuses phantoms, not runs."""
    root = _bundle(tmp_path)
    cid = _authored(root, "real")
    add.run(root, cid, ["true"])
    receipt, _ = add.latest_receipt(root, cid)
    assert receipt is not None, "a real node lost its receipt"


def test_the_phantom_refusal_leaves_no_orphan_for_doctor(tmp_path):
    """covers: M1, E1 — the engine must not manufacture the debris it later reports."""
    root = _bundle(tmp_path)
    add.run(root, "/tasks/ghost.md", ["true"])
    findings = add.doctor(root)
    orphans = [f for f in (findings[1] if isinstance(findings, tuple) else findings)
               if "orphan_receipt" in str(f)]
    assert not orphans, f"`run` created the orphan `doctor` then reports: {orphans}"


# ------------------------------------------------- M3 · gate reads or refuses --authority

def test_the_cli_refuses_a_gate_authority_it_will_not_honour(tmp_path):
    """covers: M3, R:SILENTDROP — the engine keeps frozen M3; the CLI stops pretending.

    M3 (test_gate_verb.py:224) freezes the gate's authority as COMPUTED, never the caller's
    claim, and that rule is right — a claim at the gate is the agent approving its own work.
    So the repair is not to honour the flag. It is to stop accepting one the engine discards.
    """
    root = _bundle(tmp_path)
    cid = _sealed(root, "flagged")
    _green_receipt(root, cid, tmp_path)

    proc = subprocess.run(
        [sys.executable, str(REPO / "tooling" / "cli.py"), "--root", str(root),
         "gate", "flagged", "PASS", "--by", "H", "--authority", "human"],
        capture_output=True, text=True)
    assert proc.returncode != 0, (
        f"`--authority human` was accepted at the gate: {proc.stdout}{proc.stderr}")
    assert "authority" in proc.stdout.lower(), proc.stdout
    assert "next:" in proc.stdout, f"the refusal names no next verb: {proc.stdout}"
    assert not [s for s in _stamps(root, cid) if s.get("act") == "gate"], \
        "it refused and stamped anyway"


def test_the_engine_still_computes_the_gate_floor(tmp_path):
    """covers: M3 — frozen M3 is untouched: a claim passed to the library is still ignored."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "computed")
    _green_receipt(root, cid, tmp_path)

    ok, note = add.gate(root, cid, "PASS", by="H", authority="process")
    assert ok, note
    stamp = [s for s in _stamps(root, cid) if s.get("act") == "gate"][-1]
    assert stamp["authority"] == add.authority_for(add.scan(root), cid)


def test_gate_without_the_flag_still_uses_the_computed_floor(tmp_path):
    """covers: M4 — the floor is what governs; the flag may claim, never lower."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "unflagged")
    _green_receipt(root, cid, tmp_path)

    ok, note = add.gate(root, cid, "PASS", by="H")
    assert ok, note
    stamp = [s for s in _stamps(root, cid) if s.get("act") == "gate"][-1]
    assert stamp.get("authority") == add.authority_for(add.scan(root), cid)


def test_freeze_refuses_an_authority_below_the_computed_floor(tmp_path):
    """covers: M5, R:FLOORDIVE — the long-open hole: `--authority process` on a security freeze.

    `freeze` had the opposite bug to `gate`: it honoured ANY value the caller passed, so the
    one verb that carries the ONE human approval could be talked down to `process`.
    """
    root = _bundle(tmp_path)
    cid = _authored(root, "sec", sensitivity="security")
    _, questions = add.interview(root, cid)
    ids = re.findall(r"^(A\d+|M\d+|R:[A-Z0-9_]+)\b", str(questions), re.M)
    add.interview(root, cid, answers={i: "confirm" for i in ids}, by="H")

    floor = add.authority_for(add.scan(root), cid)
    assert floor == "human", f"the fixture is not security-floored: {floor}"

    node, note = add.freeze(root, cid, by="H", authority="process")
    assert node is None, "a security freeze was downgraded to `process`"
    assert "floor" in str(note).lower(), note
    assert "next:" in str(note), note


def test_freeze_still_accepts_a_claim_at_or_above_the_floor(tmp_path):
    """covers: M5, E3 — a claim may rise; the guard refuses downgrades, not freezes."""
    root = _bundle(tmp_path)
    cid = _authored(root, "ok")
    node, note = add.freeze(root, cid, by="H", authority="human")
    assert node is not None, f"a claim above the floor was refused: {note}"
    stamp = [s for s in _stamps(root, cid) if s.get("act") == "freeze"][-1]
    assert stamp["authority"] == "human"


def test_freeze_with_no_claim_uses_the_computed_floor(tmp_path):
    """covers: M5 — the default path is unchanged."""
    root = _bundle(tmp_path)
    cid = _authored(root, "bare")
    add.freeze(root, cid, by="H")
    stamp = [s for s in _stamps(root, cid) if s.get("act") == "freeze"][-1]
    assert stamp["authority"] == add.authority_for(add.scan(root), cid)
