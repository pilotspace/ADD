"""Red suite for `refute-tier-floor` — a human-floor PASS refuses a self-refute.

`_refute_of` read presence and outcome only, so a payment task's own builder could refute its own
green with `--tier T1` and pass a human floor. verify.md's ladder — "T1 the building session, after
its own green — a prelude, optional, never the rung's answer" — was prose the gate never read.

At floor `human` the gate now refuses R:SELFREFUTE while the latest refute citing the gated receipt
claims `tier: T1` or no tier; at `plan` the same state is a notice on the success line; at `process`,
quick depth and the explore lane nothing is read. The tier stays a CLAIM: the engine records it
beside `by:` and never judges it (R:TIERJUDGED).

Driven as `.add/tasks/refute-tier-floor.md` under milestone `loop-that-closes`.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

from conftest import DRAFTED_ASSUMPTIONS, DRAFTED_CHECKS, DRAFTED_RULES, draft_direction, git  # noqa: E402

CID = "/tasks/t.md"
TREES = (REPO / "skill" / "add", REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
         REPO.parent / ".claude" / "skills" / "add")


def _bundle(tmp_path, sensitivity, depth="standard"):
    tmp_path.mkdir(parents=True, exist_ok=True)
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    root = tmp_path / ".add"
    add.init(root, "code", "P")
    cid, _ = add.new(root, "Task", "t", title="t", sensitivity=sensitivity,
                     scope=["src/a.py"], depth=depth)
    draft_direction(root, cid, rules=DRAFTED_RULES, checks=DRAFTED_CHECKS,
                    assumptions=DRAFTED_ASSUMPTIONS)
    p = root / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{add.set_key(n['raw'], 'status', 'build')}\n---\n"
              + n["body"].replace("## PLAN", "## PLAN\nregression: none · fixture", 1))
    if sensitivity == "security":
        add.new(root, "Persona", "sec-rev", title="security lens")
        assert add.advise(root, cid, "sec-rev")[0] == "sec-rev"           # a security PASS needs a named lens first
    node = add.read(p, "T2")
    if add.authority_for(add.scan(root), cid) == "human":
        add.interview(root, cid, {d["id"]: "confirm" for d in add._open_decisions(node)}, by="human:x")
    add.freeze(root, cid, "human:x", "human")
    add.brief_stamp(root, cid)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    return root


def _receipt(root, repo):
    xml = repo / "r.xml"
    doc = ('<testsuites><testsuite><testcase classname="c" name="test_atomic_admit"/>'
           '<testcase classname="c" name="test_no_overadmit"/></testsuite></testsuites>')
    return add.run(root, CID, [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
                   cwd=repo, junit=xml)


@pytest.fixture
def human(tmp_path):
    root = _bundle(tmp_path / "h", "security")
    _receipt(root, tmp_path / "h")
    return root


@pytest.fixture
def plan(tmp_path):
    root = _bundle(tmp_path / "p", "data")
    _receipt(root, tmp_path / "p")
    return root


def test_human_floor_refuses_a_t1_or_tierless_refute(human):
    """covers: M1, R:SELFREFUTE, A3, E1 — a T1 claim and a claim nobody made are both refused; the
    refusal names what it read and the exact fresh-session command (A6's reader is the builder who
    just refuted their own green). Swept in the body, not by `parametrize`: pytest reports a
    parametrized case as `name[param]` while the node's CHECKS name `name`, so a parametrized check
    binds NOTHING at the gate."""
    for tier in ("T1", None):
        add.refute(human, CID, by="me", held=True, probes=2, tier=tier)
        ok, note = add.gate(human, CID, "PASS", by="human:x")
        assert ok is None and "R:SELFREFUTE" in note, f"{tier}: {note!r}"
        assert (tier or "no tier") in note and "--tier T2" in note, note


def test_human_floor_passes_t2_and_t3(human):
    """covers: M1, E2 — the tiers the ladder calls independent pass the rung, and the PASS is
    recorded without a notice: the notice belongs to the plan floor alone."""
    for tier in ("T2", "T3"):
        add.refute(human, CID, by="fresh:verifier", held=True, probes=3, tier=tier)
        ok, note = add.gate(human, CID, "PASS", by="human:x")
        assert ok, f"{tier}: {note!r}"
        assert "R:SELFREFUTE" not in note, f"{tier} drew a notice at a human floor: {note!r}"


def test_latest_citing_stamp_decides(human):
    """covers: M1, A2, E3 — a T1 prelude followed by a fresh T2 read passes; a T2 read followed by
    the builder's own T1 re-read refuses. One reader, one answer — the same LATEST `_refute_of`
    already used for the outcome."""
    add.refute(human, CID, by="me", held=True, probes=1, tier="T1")
    add.refute(human, CID, by="fresh:verifier", held=True, probes=4, tier="T2")
    ok, note = add.gate(human, CID, "PASS", by="human:x")
    assert ok, f"a T1 prelude before a T2 read must pass: {note!r}"
    add.refute(human, CID, by="me", held=True, probes=1, tier="T1")
    ok, note = add.gate(human, CID, "PASS", by="human:x")
    assert ok is None and "R:SELFREFUTE" in note, f"the latest stamp was not the one read: {note!r}"


def test_plan_floor_notices_never_refuses(plan):
    """covers: M2, R:NOTICEASREFUSAL, E4 — the promotion is a count's decision, not this task's."""
    add.refute(plan, CID, by="me", held=True, probes=2, tier="T1")
    ok, note = add.gate(plan, CID, "PASS", by="plan:m")
    assert ok, f"a plan floor refused on the tier: {note!r}"
    # M2 states this notice VERBATIM, so the check reads the LITERAL, not three substrings that a
    # reworded notice would still satisfy. The build drifted off it once already, invisibly.
    assert ("notice: the refute of this receipt claims `T1` — a green read by its own builder; "
            "a human floor refuses this (R:SELFREFUTE)") in note, f"the notice drifted off M2: {note!r}"
    # The plan floor needs the SAME decorrelation the human floor got: every plan-floor case here
    # paired `by="me"` with T1 and a fresh name with T2, so an engine reading `by:` to decide
    # whether to notice scored identically on all of them.
    add.refute(plan, CID, by="fresh:verifier", held=True, probes=2, tier="T1")
    ok, note = add.gate(plan, CID, "PASS", by="plan:m")
    assert ok and "R:SELFREFUTE" in note, \
        f"an independent-sounding `by:` suppressed the plan-floor notice: {note!r}"
    add.refute(plan, CID, by="me", held=True, probes=2, tier="T2")
    ok, note = add.gate(plan, CID, "PASS", by="plan:m")
    assert ok and "R:SELFREFUTE" not in note, \
        f"the builder's own name drew a notice over a T2 claim: {note!r}"
    add.refute(plan, CID, by="fresh:verifier", held=True, probes=2, tier="T2")
    ok, note = add.gate(plan, CID, "PASS", by="plan:m")
    assert ok and "R:SELFREFUTE" not in note, f"a T2 read still noticed: {note!r}"


def test_refute_of_returns_the_claim_and_judges_nothing(human):
    """covers: M3, R:TIERJUDGED — the tier is read from the stamp's own key and nothing else: not
    `by:`, not `probes:`, not the note, not who signs the gate. A builder who types `--tier T2` on
    their own read passes, and their name is on it — that is the notary's stance, not a hole."""
    # DECORRELATED, because correlation is what hid the hole: every check in the repo paired a
    # refusal with `by="me"` and a pass with a fresh-sounding name, so an engine that read `by:`
    # instead of `tier:` scored identically on all of them. These two cases cross the wires — the
    # builder's own name with an independent claim, and an independent name with a T1 claim — and
    # only an engine reading the CLAIM gets both right.
    add.refute(human, CID, by="me", held=True, probes=0, tier="T2")
    ok, note = add.gate(human, CID, "PASS", by="human:x")
    assert ok, f"the builder's own name was judged, not the tier it claimed: {note!r}"
    add.refute(human, CID, by="fresh:verifier", held=True, probes=9, tier="T1")
    ok, note = add.gate(human, CID, "PASS", by="human:x")
    assert ok is None and "R:SELFREFUTE" in note, \
        f"an independent-sounding `by:` bought a T1 read a pass: {note!r}"
    add.refute(human, CID, by="human:x", held=True, probes=0, tier="T2")
    ok, note = add.gate(human, CID, "PASS", by="human:x")
    assert ok, f"the engine judged who refuted: {note!r}"
    stamps = [s for s in add.scan(human)[CID]["fm"]["verified"] if s.get("act") == "refute"]
    assert str(stamps[-1]["tier"]) == "T2" and str(stamps[-1]["by"]) == "human:x", stamps[-1]


def test_rung_is_evidence_class_and_ordered(human, plan):
    """covers: M4, A5, E5 — the ORDER: a green nobody read (R:UNREFUTED) and a green that broke
    (R:REFUTED) are the earlier answers and are never restated as a tier refusal; and the tier is
    read only where the refute rung is armed, so an evidence-class verdict signed over a T1 read is
    recorded, notice and all, without argument.

    E5 asks for `RISK-ACCEPTED` at the human floor. That state is unreachable: a `security`
    sensitivity is the only route to a human floor here, and a security risk cannot be folded into
    a RISK-ACCEPTED — the floor is HARD-STOP, and answers first. So the claim is read where each
    half is reachable: `HARD-STOP` at the human floor (M4 names it too) and `RISK-ACCEPTED` at
    plan. Reported at the gate, not papered over."""
    ok, note = add.gate(human, CID, "PASS", by="human:x")
    assert ok is None and "R:UNREFUTED" in note and "R:SELFREFUTE" not in note, note
    add.refute(human, CID, by="me", held=False, finding="breaks on zero", probes=1, tier="T1")
    ok, note = add.gate(human, CID, "PASS", by="human:x")
    assert ok is None and "R:REFUTED" in note and "R:SELFREFUTE" not in note, note
    ok, note = add.gate(human, CID, "HARD-STOP", by="human:x", reason="the finding stands")
    assert ok and "R:SELFREFUTE" not in note, f"an evidence-class verdict was refused for a tier: {note!r}"
    add.refute(plan, CID, by="me", held=True, probes=1, tier="T1")
    ok, note = add.gate(plan, CID, "RISK-ACCEPTED", by="plan:m", reason="shipping knowingly")
    assert ok and "R:SELFREFUTE" not in note, f"the rung was read for a non-PASS verdict: {note!r}"


def test_exempt_rungs_read_nothing(tmp_path):
    """covers: M2, E6 — quick depth is ceremony-tuned out of the whole refute rung, so a security
    task at `--depth quick` with a T1 refute gates PASS with no refusal and no notice. The tier is
    read exactly where the rung is armed and nowhere else (`_rung_bound`)."""
    root = _bundle(tmp_path / "q", "security", depth="quick")
    _receipt(root, tmp_path / "q")
    add.refute(root, CID, by="me", held=True, probes=1, tier="T1")
    ok, note = add.gate(root, CID, "PASS", by="human:x")
    assert ok, f"quick depth read the rung: {note!r}"
    assert "R:SELFREFUTE" not in note, f"quick depth drew a tier notice: {note!r}"


def test_verify_md_and_format_state_it():
    """covers: M5 — verify.md names the refusal at a human floor and the notice at plan; FORMAT
    says the gate reads `tier:`; the three trees are identical."""
    v = (TREES[0] / "phases" / "verify.md").read_text(encoding="utf-8")
    assert "R:SELFREFUTE" in v, "verify.md's ladder does not name the refusal"
    # Scoped to §8.4 and with no disjunct: `tier:` appears in FORMAT four times from the EARLIER
    # `refute-tier-and-changed` task, so `… or "tier:" in fmt` was satisfied before this task wrote
    # a word — M5's whole sentence could be deleted and the suite stayed green (second T2 read).
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    sec = fmt.split("### §8.4", 1)[1].split("\n### ", 1)[0]
    assert "R:SELFREFUTE" in sec, "FORMAT §8.4 does not name the refusal the gate now raises"
    assert re.search(r"human.*floor|floor.*human", sec), "§8.4 does not say WHICH floor refuses"
    for tree in TREES[1:]:
        assert (tree / "phases" / "verify.md").read_bytes() == \
            (TREES[0] / "phases" / "verify.md").read_bytes(), tree


def test_the_floor_is_the_computed_one(tmp_path):
    """covers: M1, A3 — M1 says "computed floor `human` (`authority_for`)", and `authority_for` is
    `max(sensitivity floor, A17 sensitive-path floor)`. Every other check in this file drives the
    floor through `sensitivity:` alone, so they prove only `SENSITIVITY_FLOOR` — the clause M1
    actually names was bound by nothing, and a mutant reading the DECLARED floor instead of the
    computed one survived the whole suite (the T2 read's eighth mutant, verified against a clean
    control). Here the node declares `sensitivity: data` — a plan floor on its own — and reaches
    `human` only because its `scope:` matches `index.md`'s `sensitive_paths:`."""
    root = _bundle(tmp_path / "a17", "data")
    idx = root / "index.md"
    n = add.read(idx, "T2")
    add.write(idx, f"---\n{add.set_key(n['raw'], 'sensitive_paths', '[src/*.py]')}\n---\n" + n["body"])
    graph = add.scan(root)
    assert add.sensitivity_floor("data") != "human", "the fixture no longer isolates the A17 route"
    assert add.authority_for(graph, CID) == "human", "A17 did not lift this node to a human floor"
    add.new(root, "Persona", "sec-rev", title="security lens")
    assert add.advise(root, CID, "sec-rev")[0] == "sec-rev"   # a human floor needs a named lens
    _receipt(root, tmp_path / "a17")
    add.refute(root, CID, by="me", held=True, probes=1, tier="T1")
    ok, note = add.gate(root, CID, "PASS", by="human:x")
    assert ok is None and "R:SELFREFUTE" in note, f"the rung read the DECLARED floor, not the computed one: {note!r}"
    assert "notice:" not in note, f"a human floor emitted the plan floor's notice: {note!r}"


ILLEGIBLE_TIERS = ('"T1 "', "[T1]", "T4", "t2", "T0", "0", "null", "TRUE", "T1x", "{a: b}")


def test_an_unreadable_tier_floors_up(human):
    """covers: M1, R:SELFREFUTE, A3 — the rung is an ALLOWLIST. The frozen CHECKS swept only
    legible tiers, so a denylist (`tier in (None, "", "T1")`) sent every value it had not
    enumerated to the permissive branch. `tier: "T1 "` — one trailing space, inside quotes — then
    rendered in the engine's own `## EVIDENCE` view as `tier T1`, drew nothing from `doctor`, and
    recorded a human-floor PASS: a ledger attesting `T1` beside a control that read the same field
    and said yes. `sensitivity_floor` settled this law twelve hundred lines up (R:SILENT_FLOOR) —
    an unreadable declaration floors UP — and a control reads the same way (security lens)."""
    for raw in ILLEGIBLE_TIERS:
        add.refute(human, CID, by="me", held=True, probes=1, tier="T2")
        p = human / CID.lstrip("/")
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw'].replace('tier: T2', f'tier: {raw}')}\n---\n" + n["body"])
        ok, note = add.gate(human, CID, "PASS", by="human:x")
        assert ok is None and "R:SELFREFUTE" in note, f"tier {raw} passed a human floor: {note!r}"
        assert "--tier T2" in note, note


def test_a_legible_tier_still_passes(human):
    """covers: M1, E2 — the allowlist refuses what it cannot read and nothing more: the two tiers
    M1's pass-clause names still gate clean, so closing the silence did not narrow the contract."""
    for tier in ("T2", "T3"):
        add.refute(human, CID, by="me", held=True, probes=1, tier=tier)
        ok, note = add.gate(human, CID, "PASS", by="human:x")
        assert ok, f"{tier} was refused by the allowlist: {note!r}"
