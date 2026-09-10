"""Red suite for `/tasks/refute-gate-rung.md` — a PASS at a plan-or-higher floor needs a refute
recorded AFTER the gated run.

T4 made the refute a record; a record nothing reads is a note. The gate reads the stamp's
presence and outcome by chronology — a refute cites the receipt it read — exactly as it reads the
brief entry, and it binds PRESENCE only: never the probe count, the note, or who signed (law 3).
Evidence-class: RISK-ACCEPTED and HARD-STOP are never refused by it.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

BODY = """## CARD
goal: a task with a green worth refuting
beat: build · next: add run

## RULES
<must>
- M1 the first rule
</must>
<reject>
- R:BAD something forbidden -> "BAD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · fixture
- A2 [which] covers: S1 · n/a · fixture
- A3 [when] covers: S1 · n/a · fixture
- A4 [absent] covers: S1 · n/a · fixture
- A5 [order] covers: S1 · n/a · fixture
- A6 [experience] covers: S1 · n/a · fixture

## CHECKS
- test_one · covers: M1 · acceptance · the rule
- test_two · covers: R:BAD · acceptance · the reject
red-first: every check MUST fail first.
"""


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _bundle(tmp_path, slug="rung", *, depth="standard", sensitivity="data", kind=None):
    if not (tmp_path / ".git").exists():
        git("init", "-q", cwd=tmp_path)
        git("config", "user.email", "t@example.com", cwd=tmp_path)
        git("config", "user.name", "T", cwd=tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")
        add.init(tmp_path / ".add", "code", "Rung")
    root = tmp_path / ".add"
    cid, _ = add.new(root, "Task", slug, title=f"{slug} task", depth=depth, sensitivity=sensitivity,
                     scope=["src/service.py"], kind=kind)
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    raw = n["raw"].replace("  - S1 <the surface this publishes — an endpoint, function, or section>", "  - S1 book()")
    body = BODY
    if kind == "explore":
        body = BODY.replace("## CHECKS", "## PLAN\nbudget: ~10 tool calls\n\n## FINDINGS\n- F1 (answers M1) · the first rule holds · (evidence: src/service.py:1)\n\n## CHECKS")
    add.write(path, f"---\n{raw}\n---\n{body}")          # status stays `direction`: the beat is DERIVED from stamps
    ok, note = add.freeze(root, cid, "human:tindang")
    assert ok, note
    add.brief_stamp(root, cid)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", slug, cwd=tmp_path)
    return cid


def _receipt(repo, cid, ids=("test_one", "test_two")):
    xml = repo / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>' for i in ids)
    doc = f"<testsuites><testsuite>{cases}</testsuite></testsuites>"
    return add.run(repo / ".add", cid, [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
                   cwd=repo, junit=xml)


def _gate(repo, cid, verdict="PASS", **kw):
    return add.gate(repo / ".add", cid, verdict, "plan:rung", **kw)


def _next(repo, cid):
    return add._next_verb(add.scan(repo / ".add"), cid, root=repo / ".add")


# --- M1 / M2 / M3 -------------------------------------------------------------------------------

def test_pass_refused_unrefuted_at_plan_floor(tmp_path):
    """covers: M1, A4 — no citing refute → R:UNREFUTED; a stamp that cites nothing counts for nothing."""
    cid = _bundle(tmp_path)
    _receipt(tmp_path, cid)
    ok, note = _gate(tmp_path, cid)
    assert ok is None and "R:UNREFUTED" in note and "add refute rung" in note, note
    # a hand-written refute with no `receipt:` cites nothing
    add._transition(tmp_path / ".add", cid, appends=[
        ("verified", '{ by: "x", at: 2026-09-10, act: refute, authority: process, outcome: held, probes: 1 }')])
    ok, note = _gate(tmp_path, cid)
    assert ok is None and "R:UNREFUTED" in note, note


def test_pass_refused_when_latest_refute_is_refuted(tmp_path):
    """covers: M2, A2 — refuted → R:REFUTED naming fix/run/refute; a later held on the same run reads held."""
    cid = _bundle(tmp_path)
    _receipt(tmp_path, cid)
    add.refute(tmp_path / ".add", cid, by="v", held=False, finding="book() with no session", probes=2)
    ok, note = _gate(tmp_path, cid)
    assert ok is None and "R:REFUTED" in note, note
    tail = note.split("next:", 1)[-1]
    assert "add run rung" in tail and "add refute rung" in tail and "gate" not in tail, note
    add.refute(tmp_path / ".add", cid, by="v", held=True, probes=3)
    ok, note = _gate(tmp_path, cid)
    assert ok, note


def test_held_refute_lets_the_pass_through(tmp_path):
    """covers: M3 — held, citing the gated receipt → PASS and done; other rungs unchanged."""
    cid = _bundle(tmp_path)
    _receipt(tmp_path, cid)
    add.refute(tmp_path / ".add", cid, by="v", held=True, probes=0)
    ok, note = _gate(tmp_path, cid)
    assert ok, note
    assert (add.read(tmp_path / ".add/tasks/rung.md", "T0")["fm"] or {}).get("status") == "done"


# --- M4 / E2: exemptions ----------------------------------------------------------------------------

def test_quick_process_and_explore_are_exempt(tmp_path):
    """covers: M4, E2 — quick depth, process floor, and kind explore gate PASS with no refute."""
    quick = _bundle(tmp_path, "q", depth="quick", sensitivity="data")
    proc = _bundle(tmp_path, "p", depth="standard", sensitivity="mechanical")
    expl = _bundle(tmp_path, "x", depth="standard", sensitivity="data", kind="explore")
    for cid in (quick, proc):
        _receipt(tmp_path, cid)
        ok, note = _gate(tmp_path, cid)
        assert ok, f"{cid}: {note}"
    ok, note = _gate(tmp_path, expl)                      # findings path, no receipt
    assert ok, note


# --- E1: chronology ------------------------------------------------------------------------------

def test_refute_of_an_earlier_run_enters_nothing(tmp_path):
    """covers: E1 — a refute citing run 1 says nothing about run 2."""
    cid = _bundle(tmp_path)
    _receipt(tmp_path, cid)
    add.refute(tmp_path / ".add", cid, by="v", held=True, probes=1)
    _receipt(tmp_path, cid)
    ok, note = _gate(tmp_path, cid)
    assert ok is None and "R:UNREFUTED" in note, note


# --- Rejects -----------------------------------------------------------------------------------------

def test_risk_accepted_and_hard_stop_are_never_refused_by_the_rung(tmp_path):
    """covers: R:NOTINTEGRITY — evidence-class: the rung binds PASS only."""
    assert "unrefuted" in add.EVIDENCE_REFUSALS and "unrefuted" not in add.INTEGRITY_REFUSALS
    cid = _bundle(tmp_path)
    _receipt(tmp_path, cid)
    ok, note = _gate(tmp_path, cid, "HARD-STOP", reason="a finding")
    assert ok and "R:UNREFUTED" not in (note or ""), note
    cid2 = _bundle(tmp_path, "rung2")
    _receipt(tmp_path, cid2)
    ok, note = _gate(tmp_path, cid2, "RISK-ACCEPTED", reason="owner · ticket · expiry")
    assert ok and "R:UNREFUTED" not in (note or ""), note


def test_rung_reads_presence_and_outcome_only(tmp_path):
    """covers: R:NOJUDGE — probes 0, no note, any signer satisfies it; the engine never judges a probe."""
    cid = _bundle(tmp_path)
    _receipt(tmp_path, cid)
    add.refute(tmp_path / ".add", cid, by="x", held=True, probes=0)
    ok, note = _gate(tmp_path, cid)
    assert ok, note


# --- M5: the affordance ------------------------------------------------------------------------------

def test_verify_hint_names_refute_first_at_plan_floor(tmp_path):
    """covers: M5 — status/todo point at `add refute` before the gate; process floor goes straight to the gate."""
    cid = _bundle(tmp_path)
    _receipt(tmp_path, cid)
    hint = _next(tmp_path, cid)
    assert hint.startswith("add refute rung") and "--held" in hint and "--found" in hint, hint
    add.refute(tmp_path / ".add", cid, by="v", held=True, probes=1)
    assert _next(tmp_path, cid).startswith("add gate rung PASS"), _next(tmp_path, cid)
    proc = _bundle(tmp_path, "p", depth="standard", sensitivity="mechanical")
    _receipt(tmp_path, proc)
    assert _next(tmp_path, proc).startswith("add gate p PASS"), _next(tmp_path, proc)


# --- M6: stated where it is read ---------------------------------------------------------------------

def test_format_and_skill_name_the_rung():
    """covers: M6 — FORMAT §8.4, verify.md §3 and gate.md each carry the code and the exemptions."""
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    sec = fmt[fmt.index("### §8.4"):fmt.index("## §9")]
    assert "R:UNREFUTED" in sec and "R:REFUTED" in sec, "FORMAT §8.4 does not state the rung"
    assert re.search(r"quick.*process.*explore", " ".join(sec.split())), "FORMAT §8.4 does not state the exemptions"
    verify = (REPO / "skill" / "add" / "phases" / "verify.md").read_text(encoding="utf-8")
    assert "R:UNREFUTED" in verify, "verify.md does not name the rung"
    gate_md = (REPO / "skill" / "add" / "gate.md").read_text(encoding="utf-8")
    assert "R:UNREFUTED" in gate_md, "gate.md does not name the rung"
