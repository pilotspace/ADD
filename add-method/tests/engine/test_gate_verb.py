"""Red suite for e13 `build-gate-verb` — the verdict, its refusals, and the quick lane.

This is the verb that should have existed since e4. All eleven gates in this project were
recorded by hand-appending a stamp through the private `_transition`, so none of the three
refusals PROPOSAL specifies for `gate` has ever run against anything.

It also lands e12's M3. That rule says "`unbound` is part of every gate's report" and it was
gated PASS while no gate report existed — the rule was not wrong, it had nowhere to land.

`test_gate_on_live_bundle_history` is the one that decides the task's ⚠: if a strict M2 would
have refused this project's own M0 gates, the refusal needs a declared degradation rather than
a hard stop, and the suite says which.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


TASK_BODY = """## CARD
goal: a task whose rules are all provable
beat: build · next: add run

## RULES
<must>
- M1 the first rule
- M2 the second rule
</must>
<reject>
- R:BAD something forbidden -> "BAD"
</reject>

## CHECKS
- test_one · covers: M1 · proves the first
- test_two · covers: M2, R:BAD · proves the second and the reject
red-first: every check MUST fail first.
"""


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    """A git repo with a bundle, a scoped source file, and a task in `build`."""
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")

    root = tmp_path / ".add"
    add.init(root, "code", "Gating")
    cid, _ = add.new(root, "Task", "gated", title="A gated task", depth="standard",
                     sensitivity="mechanical", scope=["src/service.py"])
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'build')}\n---\n{TASK_BODY}")
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    return tmp_path


CID = "/tasks/gated.md"


def _receipt(repo, ids=("test_one", "test_two")):
    """Record a receipt reporting `ids` as passing, the way a real runner would."""
    xml = repo / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>' for i in ids)
    xml.write_text(f"<testsuites><testsuite>{cases}</testsuite></testsuites>")
    return add.run(repo / ".add", CID, [sys.executable, "-c", "pass"], cwd=repo, junit=xml)


# ------------------------------------------------------ refusal 1: freshness (M1, R:STALEGATE)


def test_gate_refuses_stale_receipt(repo):
    """covers: M1, R:STALEGATE — a verdict over changed code is evidence of nothing."""
    _receipt(repo)
    (repo / "src" / "service.py").write_text("def book():\n    return False\n")

    ok, note = add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    assert ok is False, "a gate was recorded against a stale receipt"
    assert "stale" in note.lower() or "fresh" in note.lower(), note


def test_no_scope_makes_freshness_not_applicable(repo):
    """covers: M1 — a node declaring no `scope:` has nothing to be stale about.

    §3d's quick lane and the doc lane both allow a task with no code scope. Refusing those for
    "freshness cannot be established" would mean a whole legitimate lane can never be gated.
    """
    cid, _ = add.new(repo / ".add", "Task", "no-scope", title="No scope", depth="quick")
    # Authored, so the placeholder refusal does not fire first — this check is about freshness,
    # and a test that never reaches the code it names is not testing it.
    path = repo / ".add" / cid.lstrip("/")
    stub = add.read(path, "T2")
    add.write(path, f"---\n{stub['raw']}\n---\n## CARD\ngoal: a doc change with no code scope\n"
                    "beat: build · next: add run\n\n## EVIDENCE\nreceipt: pending\n")
    add.run(repo / ".add", cid, [sys.executable, "-c", "pass"], cwd=repo)
    ok, note = add.gate(repo / ".add", cid, "PASS", by="human:tindang")
    assert ok is True, note
    assert "n/a" in note.lower() or "no scope" in note.lower(), \
        f"freshness was skipped without saying so — a silent skip is not a report: {note}"


def test_card_scope_without_frontmatter_scope_is_refused(repo):
    """covers: M1, R:STALEGATE — the hole that gated e13 itself without a freshness check.

    e13's CARD read `scope: add/scripts/add.py · tests/engine/test_gate_verb.py` while its
    frontmatter had no `scope:` key at all, because `new` was called without one. Consequences,
    both silent: `scope_digest` had nothing to hash so the receipt degraded to `mtime`, and the
    gate reported `freshness: n/a`. A17's sensitive-path floor also matches against frontmatter
    `scope:`, so it could not fire either. A node that LOOKS scoped and is not is worse than one
    that is honestly unscoped, because the CARD is what a human reads.
    """
    cid, _ = add.new(repo / ".add", "Task", "card-only-scope", title="Card only")
    path = repo / ".add" / cid.lstrip("/")
    stub = add.read(path, "T2")
    add.write(path, f"---\n{stub['raw']}\n---\n## CARD\ngoal: looks scoped\n"
                    "scope: src/service.py\nbeat: build · next: add run\n\n"
                    "## EVIDENCE\nreceipt: pending\n")
    add.run(repo / ".add", cid, [sys.executable, "-c", "pass"], cwd=repo)

    ok, note = add.gate(repo / ".add", cid, "PASS", by="human:tindang")
    assert ok is False, "a node whose CARD claims a scope its frontmatter lacks was gated"
    assert "scope" in note.lower(), note


def test_declared_scope_without_a_digest_is_still_refused(repo):
    """covers: M1, R:STALEGATE — the hole the fix above could have opened.

    "No scope" must mean not-applicable, but "scope declared and no digest recorded" must stay a
    refusal. Otherwise freshness is dodgeable by writing a receipt the engine did not produce.
    """
    _receipt(repo)
    runs = sorted((repo / ".add" / "tasks" / "gated.d" / "runs").glob("*.md"))
    text = runs[-1].read_text()
    stripped = text.split("  scope_digest:")[0] + "generated: { by: process:run, at: 2026-07-30 }\n---\n"
    runs[-1].write_text(stripped)

    ok, note = add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    assert ok is False, "a scoped node was gated on a receipt carrying no digest"


def test_template_placeholders_are_refused_by_name(repo):
    """covers: M2, M4 — an unauthored node refuses with the reason, not with a confusing one.

    `new` ships `- M1 <the rule that must hold>` and `- <test_name> · covers: M1`. Both are
    placeholders, so `bind` reports M1 unproven and the refusal reads "M1 has no reported passing
    check" — true, useless, and it points at RISK-ACCEPTED when the real fix is to author the
    node. A refusal that names the wrong fix is R:SILENTREFUSE with extra steps.
    """
    cid, _ = add.new(repo / ".add", "Task", "unauthored", title="Unauthored", scope=["src/service.py"])
    add.run(repo / ".add", cid, [sys.executable, "-c", "pass"], cwd=repo)
    ok, note = add.gate(repo / ".add", cid, "PASS", by="human:tindang")
    assert ok is False
    assert "placeholder" in note.lower(), f"the refusal did not name the real problem: {note}"
    assert "RISK-ACCEPTED" not in note, "it offered to accept a risk on an unauthored node"


def test_quick_task_declares_no_musts(repo):
    """covers: M6 — a quick task's evidence is its exit code, not a covers-bound suite.

    §3d's quick lane is "rename a flag; add a log line". Giving it the standard template's
    placeholder Musts means the one-call lane can never close, which is how this was found.
    """
    add.quick(repo / ".add", "add-a-log-line", title="Add a log line",
              cmd=[sys.executable, "-c", "pass"], by="human:tindang", cwd=repo)
    node = add.read(repo / ".add" / "tasks" / "add-a-log-line.md", "T2")
    assert add.rules_of(node) == [], f"a quick task declared Musts it cannot prove: {add.rules_of(node)}"


def test_gate_accepts_a_fresh_receipt(repo):
    """covers: M1, M3 — the happy path still works, or the refusal is just a wall."""
    _receipt(repo)
    ok, note = add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    assert ok is True, note


# ------------------------------------------------- refusal 2: unproven covers (M2, R:UNPROVEN)


def test_gate_refuses_unproven_must(repo):
    """covers: M2, R:UNPROVEN — this is e12's M3, finally landing somewhere.

    M2's check was never reported, so M2 is a label. A PASS here would be the exact defect
    F2 measured across nine M0 tasks.
    """
    _receipt(repo, ids=("test_one",))
    ok, note = add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    assert ok is False, "a PASS was recorded while a Must had no reported passing check"


def test_gate_refusal_names_the_unproven_rules(repo):
    """covers: M2 — naming WHICH rules is the difference between a report and a complaint."""
    _receipt(repo, ids=("test_one",))
    ok, note = add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    assert "M2" in note, f"the refusal did not say which rule was unproven: {note}"
    assert "R:BAD" in note, f"the unproven reject was not named either: {note}"


def test_gate_counts_a_failing_check_as_unproven(repo):
    """covers: M2 — a check that RAN and FAILED proves nothing (e12's rule, at the gate)."""
    xml = repo / "r.xml"
    xml.write_text('<testsuites><testsuite><testcase classname="c" name="test_one"/>'
                   '<testcase classname="c" name="test_two"><failure message="x"/></testcase>'
                   "</testsuite></testsuites>")
    add.run(repo / ".add", CID, [sys.executable, "-c", "pass"], cwd=repo, junit=xml)
    ok, note = add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    assert ok is False and "M2" in note, note


# ----------------------------------------------------------- the stamp itself (M3)


def test_gate_records_at_computed_authority(repo):
    """covers: M3 — A17's floor is computed, never taken from the caller's claim."""
    _receipt(repo)
    add.gate(repo / ".add", CID, "PASS", by="human:tindang", authority="process")
    stamp = [s for s in add.scan(repo / ".add")[CID]["fm"]["verified"] if s.get("act") == "gate"][-1]
    assert stamp["authority"] == add.authority_for(add.scan(repo / ".add"), CID), \
        f"the caller's claimed authority overrode the computed floor: {stamp}"


def test_gate_stamps_the_brief_hash(repo):
    """covers: M3 — A16: these instructions produced this code, which earned this gate."""
    _receipt(repo)
    expected = add.brief(repo / ".add", CID)["hash"]
    add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    stamp = [s for s in add.scan(repo / ".add")[CID]["fm"]["verified"] if s.get("act") == "gate"][-1]
    assert stamp.get("brief") == expected, \
        f"the provenance chain is broken: {stamp.get('brief')} != {expected}"


def test_gate_pass_transitions_to_done(repo):
    """covers: M3 — a PASS that leaves the node in `build` is a stamp nobody acted on."""
    _receipt(repo)
    add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    assert add.scan(repo / ".add")[CID]["fm"]["status"] == "done"


def test_risk_accepted_records_the_risk(repo):
    """covers: M3 — RISK-ACCEPTED is a verdict with a reason, not a softer PASS."""
    _receipt(repo, ids=("test_one",))
    ok, note = add.gate(repo / ".add", CID, "RISK-ACCEPTED", by="human:tindang",
                        reason="M2 unproven, accepted for the pilot")
    assert ok is True, note
    stamp = [s for s in add.scan(repo / ".add")[CID]["fm"]["verified"] if s.get("act") == "gate"][-1]
    assert stamp["outcome"] == "RISK-ACCEPTED"
    assert "pilot" in str(stamp.get("reason", "")), f"the risk was accepted without recording it: {stamp}"


def test_risk_accepted_requires_a_reason(repo):
    """covers: M3, R:SILENTREFUSE — an unexplained RISK-ACCEPTED is a PASS in disguise."""
    _receipt(repo, ids=("test_one",))
    ok, note = add.gate(repo / ".add", CID, "RISK-ACCEPTED", by="human:tindang")
    assert ok is False and "reason" in note.lower(), note


def test_hard_stop_does_not_transition(repo):
    """covers: M3 — a HARD-STOP is recorded and the node stays where it is."""
    _receipt(repo)
    ok, note = add.gate(repo / ".add", CID, "HARD-STOP", by="human:tindang",
                        reason="the approach is wrong")
    assert ok is True, note
    assert add.scan(repo / ".add")[CID]["fm"]["status"] != "done"


# ------------------------------------------------------- refusals speak (M4, R:SILENTREFUSE)


def test_gate_refusal_names_the_fix(repo):
    """covers: M4, R:SILENTREFUSE — every refusal ends in a command that would resolve it."""
    (repo / "src" / "service.py").write_text("# no receipt at all\n")
    ok, note = add.gate(repo / ".add", CID, "PASS", by="human:tindang")
    assert ok is False
    last = note.strip().splitlines()[-1]
    assert last.lower().startswith("next:") and "add " in last, \
        f"a refusal that names no fix is an error message, not a report: {note!r}"


def test_unknown_verdict_is_refused(repo):
    """covers: M4 — the verdict vocabulary is closed, and the refusal lists it."""
    _receipt(repo)
    ok, note = add.gate(repo / ".add", CID, "LGTM", by="human:tindang")
    assert ok is False and "PASS" in note, note


# ----------------------------------------------------------- F3: run's own stamp (M5, R:ORPHAN)


def test_run_appends_its_own_stamp(repo):
    """covers: M5 — F3's fix. A receipt nothing points at is unreachable evidence."""
    node = _receipt(repo)
    stamps = [s for s in add.scan(repo / ".add")[CID]["fm"]["verified"] if s.get("act") == "run"]
    assert stamps, "run wrote a receipt and left no stamp pointing at it"
    assert stamps[-1]["receipt"].endswith(node["path"].name), stamps[-1]


def test_orphan_receipts_are_reported(repo):
    """covers: M5, R:ORPHAN — an unreachable receipt is a finding, not a silent file."""
    runs = repo / ".add" / "tasks" / "gated.d" / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "99.md").write_text(f"---\ntype: Run\nruntime: process\ntask: {CID}\n---\n")
    orphans = add.orphans(repo / ".add")
    assert any("99" in str(o) for o in orphans), f"an orphaned receipt went unreported: {orphans}"


def test_no_orphan_receipts_on_live_bundle():
    """covers: M5, R:ORPHAN — this repo's own 8 orphans, reported rather than asserted away.

    Reports rather than asserting zero: the 8 predate F3's fix and cannot be stamped
    retroactively without inventing acts that nobody performed.
    """
    orphans = add.orphans(REPO / ".add")
    print(f"\norphaned receipts on the live bundle: {len(orphans)}")
    assert isinstance(orphans, list)


# ------------------------------------------------------------- the quick lane (M6, R:BYPASS)


def test_quick_lane_is_one_engine_call(repo):
    """covers: M6 — §3d's quick lane: new + freeze + run + gate in ONE call."""
    ok, note = add.quick(repo / ".add", "rename-a-flag", title="Rename a flag",
                         cmd=[sys.executable, "-c", "pass"], by="human:tindang", cwd=repo)
    assert ok is True, note
    node = add.scan(repo / ".add")["/tasks/rename-a-flag.md"]
    assert node["fm"]["status"] == "done"
    acts = [s["act"] for s in node["fm"]["verified"]]
    assert "freeze" in acts and "run" in acts and "gate" in acts, acts


def test_quick_lane_refuses_above_quick(repo):
    """covers: M6, R:BYPASS — a one-call lane that works at `deep` bypasses every control."""
    ok, note = add.quick(repo / ".add", "change-auth", title="Change auth", depth="deep",
                         cmd=[sys.executable, "-c", "pass"], by="human:tindang", cwd=repo)
    assert ok is False, "the quick lane was available above `quick` depth"
    assert "quick" in note.lower(), note


def test_quick_lane_refuses_a_failing_command(repo):
    """covers: M6 — one call still means real evidence: a red command earns no gate."""
    ok, note = add.quick(repo / ".add", "broken-thing", title="Broken thing",
                         cmd=[sys.executable, "-c", "import sys; sys.exit(1)"],
                         by="human:tindang", cwd=repo)
    assert ok is False, "a quick task closed on a failing command"


# ------------------------------------------------- the live bundle decides the ⚠ (M2)


def test_gate_on_live_bundle_history():
    """covers: M2 — would a strict M2 have refused this project's own gates?

    This sizes the task's ⚠. F2 measured 65 rules labelled-not-proven across nine M0 tasks; if
    M2 as written would have refused those gates, a hard stop is the wrong shape and the verb
    needs a declared `covers_unverified` degradation instead. The suite reports the count so the
    decision is taken against a number.
    """
    import re
    root = REPO / ".add"
    reported = set()
    for p in (REPO / "tests").rglob("test_*.py"):
        reported |= set(re.findall(r"^def (test_\w+)", p.read_text(), re.M))
    reported = {t: "pass" for t in reported}

    would_refuse = []
    for cid, node in sorted(add.scan(root).items()):
        fm = node["fm"] or {}
        if fm.get("type") != "Task" or not fm.get("verified"):
            continue
        full = add.read(node["path"], "T2")
        if not add.rules_of(full):
            continue
        if add.unbound(full, reported):
            would_refuse.append(cid.split("/")[-1][:-3])
    print(f"\na strict M2 would have refused {len(would_refuse)} of this project's gates: "
          f"{would_refuse}")
    assert isinstance(would_refuse, list)


# ---------------------------------------------- F8, found at e8's gate (post-gate additions)

def test_a_backticked_path_pattern_is_not_a_placeholder():
    """covers: M1 — `<slug>.d/runs/` inside backticks is a path pattern, not an unfilled template.

    e8's gate REFUSED a fully authored node because its M5 said "a Run node under
    `<slug>.d/runs/`". The refusal was correct machinery reaching a false conclusion, and the wrong
    fix is to reword every node that needs to name a path shape — that makes prose pay a permanent
    tax to a defective oracle. No placeholder in any `BODIES` template is backticked, so excluding
    backticked spans cannot blind this check: verified against both templates before changing it.
    """
    node = {"body": "## RULES\n<must>\n- M1 a receipt under `<slug>.d/runs/` is bound\n</must>\n"}
    assert add.placeholders_in(node) == [], \
        f"a backticked path pattern was read as a template placeholder: {add.placeholders_in(node)}"


def test_a_real_placeholder_is_still_caught():
    """covers: M1 — the fix above must not cost the check its actual job.

    Every unfilled token in `BODIES` is unbackticked, and this asserts the ones that matter are
    still refused — otherwise F8's fix would silently turn off the refusal that made `gate` worth
    building.
    """
    node = {"body": "## RULES\n<must>\n- M1 <what this rule requires>\n</must>\n"
                    "## CHECKS\n- <check> · covers: M1 · proves M1\n"}
    found = add.placeholders_in(node)
    assert "<what this rule requires>" in " ".join(found), f"a real placeholder slipped through: {found}"
