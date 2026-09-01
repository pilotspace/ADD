"""RISK-ACCEPTED signs for weak EVIDENCE; it must never sign for a missing SEAL.

Every integrity refusal in `gate` is conditioned on `verdict == "PASS"`. Measured 2026-09-01
against the pre-change engine: a Task created seconds earlier, still carrying `goal: <one line>`
and every template section, never frozen and never briefed, reached `done` in three calls —
`run -- true`, `gate RISK-ACCEPTED`, `done`. R:UNSEALED, drift, R:UNBRIEFED, the placeholder
check and R:UNDECLARED_SENSITIVE all read PASS only.

This is #206's own lesson one verdict over: skipping `freeze` did not FAIL the post-freeze
guards, it SWITCHED THEM OFF. That hole was closed for PASS and left open for RISK-ACCEPTED.

The split these checks pin: a refusal that protects the RECORD binds every verdict; a refusal
that judges the EVIDENCE stays PASS-only, because signing for imperfect evidence is what the
verdict is for.
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
    # `freeze` refuses a template `goal:` — the ONE approval is an approval OF the
    # goal, so a fixture that reaches a post-freeze state has to state one.
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
    """Authored, frozen and briefed — the state a legitimate RISK-ACCEPTED starts from."""
    cid = _authored(root, slug, **fields)
    node, note = add.freeze(root, cid, by="H", authority="human")
    assert node is not None, f"fixture could not freeze: {note!r}"
    add.brief_stamp(root, cid, by="H")     # `brief()` COMPILES; `brief_stamp()` records the entry
    return cid


def _receipt(root, cid, cmd=("true",), **kw):
    """A receipt reporting the node's one drafted check, so `unbound` is empty."""
    return add.run(root, cid, list(cmd), **kw)


def _msg(result):
    """gate/done return tuples whose LAST element is the operator-facing message."""
    return str(result[-1])


# ---------------------------------------------------------------- M1 · the seal

def test_risk_accepted_refuses_an_unfrozen_node(tmp_path):
    """covers: M1 — the three-call walk starts here, and this is where it must stop."""
    root = _bundle(tmp_path)
    cid = _authored(root, "unsealed")
    _receipt(root, cid)

    ok, *_rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not ok, "RISK-ACCEPTED recorded on a node the ONE human approval never touched"
    assert "R:UNSEALED" in _msg((ok, *_rest))


def test_refreeze_alone_satisfies_the_seal(tmp_path):
    """covers: E2 — the seal is what matters, not which verb wrote it."""
    root = _bundle(tmp_path)
    cid = _authored(root, "refrozen")
    add.freeze(root, cid, by="H", authority="human")
    p = root / cid.lstrip("/")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "only the caller's rows", "only the caller's own rows"), encoding="utf-8")
    add.freeze(root, cid, by="H", authority="human")   # records a `refreeze`
    add.brief_stamp(root, cid, by="H")
    _receipt(root, cid)

    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert ok, _msg((ok, *rest))


# ---------------------------------------------------------------- M2 · drift

def test_risk_accepted_refuses_a_drifted_contract(tmp_path):
    """covers: M2, E1 — a frozen contract changes by refreezing, under EVERY verdict."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "drifted")
    p = root / cid.lstrip("/")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- M1 the lister returns only the caller's rows",
        "- M1 the lister returns whatever it returns"), encoding="utf-8")
    _receipt(root, cid)

    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not ok, "a silently rewritten Must was accepted under RISK-ACCEPTED"
    assert "drift" in _msg((ok, *rest)).lower() or "refreez" in _msg((ok, *rest)).lower()


# ---------------------------------------------------------------- M3 · placeholders

def test_risk_accepted_refuses_template_placeholders(tmp_path):
    """covers: M3 — a pure scaffold is not a risk anyone can accept; it is an empty record."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "stub", title="stub")
    add.freeze(root, cid, by="H", authority="human")
    _receipt(root, cid)

    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not ok, "a body of template slots was signed for"


# ------------------------------------------------- M4 · the security floor

def _sensitive_bundle(tmp_path, patterns=("deploy/**",)):
    """A bundle at `<project>/.add`, because `gate` reads `_changed_paths(root.parent)`.

    A bundle whose parent is not the repo makes the guard read an unrelated directory and find
    nothing — which is how a refusal passes for the wrong reason.
    """
    project = tmp_path / "proj"
    project.mkdir()
    root = project / ".add"
    add.init(root, "code", "T")
    idx = root / "index.md"
    block = "sensitive_paths:\n" + "".join(f"  - {p}\n" for p in patterns)
    idx.write_text(re.sub(r"^sensitive_paths:.*\n", block, idx.read_text(encoding="utf-8"),
                          count=1, flags=re.M), encoding="utf-8")
    assert (add.scan(root).get("/index.md", {}).get("fm") or {}).get("sensitive_paths") \
        == list(patterns), "fixture did not declare the sensitive paths"
    for a in (("init", "-q", "."), ("config", "user.email", "t@t"),
              ("config", "user.name", "t"), ("add", "-A"), ("commit", "-qm", "base")):
        add._git(project, *a)
    return root


def test_risk_accepted_refuses_an_undeclared_sensitive_path(tmp_path):
    """covers: M4, E6 — accepting a risk is never the way around the security floor."""
    root = _sensitive_bundle(tmp_path)
    cid = _sealed(root, "floored", scope=["src"])
    (root.parent / "deploy").mkdir(exist_ok=True)
    (root.parent / "deploy" / "prod.yaml").write_text("secret: 1\n", encoding="utf-8")
    assert "deploy/prod.yaml" in add._changed_paths(root.parent), "fixture changed nothing git can see"
    _receipt(root, cid)

    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not ok, "an undeclared sensitive edit was gated through the hatch"
    assert "R:UNDECLARED_SENSITIVE" in _msg((ok, *rest))


# ------------------------------------------------- M5 · evidence stays PASS-only

def test_evidence_refusals_stay_pass_only(tmp_path):
    """covers: M5, A1 — the hatch must still work for what it is FOR.

    A node that is frozen, briefed, unstubbed and scope-clean records RISK-ACCEPTED even
    though its command exited non-zero. If this goes red the fix is in the split, not here.
    """
    root = _bundle(tmp_path)
    cid = _sealed(root, "weak")
    _receipt(root, cid, cmd=("false",))

    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="known flake, signed")
    assert ok, "the escape hatch refused the imperfect evidence it exists to accept: " \
               + _msg((ok, *rest))


def test_every_pass_only_site_is_in_exactly_one_tier(tmp_path):
    """covers: M5, A2 — the split is declared in the source, not scattered inline.

    Sixteen separate `verdict == "PASS"` conditions is how the tiers drifted apart in the first
    place. Each site must read from one of two named lists so the classification is reviewable.
    """
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    gate_src = src[src.index("\ndef gate("):]
    gate_src = gate_src[:gate_src.index("\ndef ", 1)]
    inline = re.findall(r'verdict == "PASS"', gate_src)
    assert len(inline) <= 1, (
        f"{len(inline)} inline PASS conditions remain in gate(); the tiers must be named lists "
        "so a reviewer can see which refusals bind every verdict")
    assert "INTEGRITY_REFUSALS" in src and "EVIDENCE_REFUSALS" in src


def test_risk_accepted_reaches_no_state_pass_could_not(tmp_path):
    """covers: R:HATCH — for a fixed node, RISK-ACCEPTED refuses wherever PASS refuses on integrity."""
    root = _bundle(tmp_path)
    cid = _authored(root, "hatch")          # authored but NEVER frozen
    _receipt(root, cid)

    pass_ok, *pr = add.gate(root, cid, "PASS", by="H")
    risk_ok, *rr = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not pass_ok, "precondition: PASS must refuse an unfrozen node (R:UNSEALED, #206)"
    assert not risk_ok, "PASS refused this node and RISK-ACCEPTED walked past it"


# ---------------------------------------------------------------- M6 · done

def test_done_refuses_a_gate_that_no_freeze_precedes(tmp_path):
    """covers: M6, A3 — `done` is the terminal write and owns the last look at the seal."""
    root = _bundle(tmp_path)
    cid = _authored(root, "walked")
    _receipt(root, cid)
    # forge the stamp the pre-change gate would have written, so `done` is tested in isolation.
    # `_receipt` has already turned `verified: []` into a list, so APPEND rather than replace.
    node = root / cid.lstrip("/")
    lines = node.read_text(encoding="utf-8").splitlines(keepends=True)
    at = max(i for i, ln in enumerate(lines) if ln.startswith("  - { by:")) + 1
    lines.insert(at, '  - { by: "H", at: 2026-09-01, act: gate, authority: human, '
                     'outcome: RISK-ACCEPTED, reason: "probing" }\n')
    node.write_text("".join(lines), encoding="utf-8")
    assert any(s.get("act") == "gate" for s in add.read(node, "T0")["fm"]["verified"]), \
        "fixture did not forge a parseable gate stamp"

    ok, *rest = add.done(root, cid)
    assert not ok, "a node the ONE approval never touched was walked to `done`"
    assert "freeze" in _msg((ok, *rest))


def test_done_still_closes_a_properly_frozen_risk_accepted(tmp_path):
    """covers: M6, E3 — the legitimate hatch still closes. M6 is about the seal, not the date."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "legit")
    _receipt(root, cid, cmd=("false",))
    add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="known flake, signed")

    ok, *rest = add.done(root, cid)
    assert ok, _msg((ok, *rest))


def test_a_receiptless_gate_still_hears_the_receipt_message(tmp_path):
    """covers: A10 — the first-time experience is unchanged; no security refusal out of nowhere."""
    root = _bundle(tmp_path)
    cid = _authored(root, "fresh")

    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not ok
    assert "receipt" in _msg((ok, *rest)).lower(), _msg((ok, *rest))


# ---------------------------------------------------------------- M7 · path segments

def test_paths_touch_matches_whole_segments():
    """covers: M7, E4 — over-match in the EXEMPTION direction defeats R:UNDECLARED_SENSITIVE.

    The guard exempts a changed path when any `scope:` entry touches it. `srcfoo/secret.yaml`
    starting with the string `src` is not the same fact as it living under `src/`, and treating
    it as one lets `scope: src` sign for a directory the node never declared.
    """
    assert add._paths_touch("src/auth.py", "src") is True
    assert add._paths_touch("src", "src/**") is True
    assert add._paths_touch("srcfoo/secret.yaml", "src") is False
    assert add._paths_touch("secrets_public/x", "secrets/**") is False
    assert add._paths_touch("deployX/prod.yaml", "deploy") is False


def test_paths_touch_empty_matches_nothing():
    """covers: M7, A4 — an empty entry that matched everything would fire A17 on every node."""
    assert add._paths_touch("", "src/**") is False
    assert add._paths_touch("src", "") is False


def test_paths_touch_leaves_a_backslash_entry_unmatched():
    """covers: A14 — `/` is the only segment separator; a backslash entry is left alone."""
    assert add._paths_touch("src\\auth.py", "src") is False


# ---------------------------------------------------------------- M8 · the floor

def test_new_refuses_an_unrecognised_sensitivity(tmp_path):
    """covers: M8, R:SILENT_FLOOR — `sensitivity: high` floored to `process` on two real nodes."""
    root = _bundle(tmp_path)
    cid, msg = add.new(root, "Task", "bad", title="bad", sensitivity="high")
    assert cid is None, "an unrecognised sensitivity was accepted and silently floored"
    for known in ("mechanical", "data", "architecture", "security"):
        assert known in str(msg), f"the refusal must list `{known}`"


def test_authority_for_reads_an_unknown_sensitivity_as_human(tmp_path):
    """covers: M8, E5 — an EXISTING node written before M8 floors up, not down."""
    root = _bundle(tmp_path)
    cid = _authored(root, "legacy")
    p = root / cid.lstrip("/")
    # anchor on a key `new` actually writes — `depth:` is omitted unless supplied, so the
    # first cut of this fixture was a silent no-op and the check passed against nothing.
    p.write_text(p.read_text(encoding="utf-8").replace(
        "type: Task", "type: Task\nsensitivity: high", 1), encoding="utf-8")
    assert (add.scan(root)[cid]["fm"] or {}).get("sensitivity") == "high", "fixture did not land"

    assert add.authority_for(add.scan(root), cid) == "human"


# ---------------------------------------------------------------- order & wording

def test_integrity_refusals_precede_evidence_refusals(tmp_path):
    """covers: A5 — send the operator to the missing seal, not to the stale receipt."""
    root = _bundle(tmp_path)
    cid = _authored(root, "both", scope=["src"])
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    _receipt(root, cid)
    (root / "src" / "a.py").write_text("x = 2\n", encoding="utf-8")   # receipt now stale

    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not ok
    assert "R:UNSEALED" in _msg((ok, *rest)), \
        "the missing seal outranks the stale receipt: " + _msg((ok, *rest))


def test_every_new_refusal_names_a_next_verb(tmp_path):
    """covers: A6 — the reader is an agent mid-loop that will act on the `next:` line."""
    root = _bundle(tmp_path)
    cid = _authored(root, "advice")
    _receipt(root, cid)
    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not ok
    assert re.search(r"next: add \w", _msg((ok, *rest))), _msg((ok, *rest))


def test_hard_stop_is_still_recordable_on_an_unfrozen_node(tmp_path):
    """covers: A13 — a HARD-STOP never closes a task; refusing it only loses the finding."""
    root = _bundle(tmp_path)
    cid = _authored(root, "stopped")
    _receipt(root, cid)

    ok, *rest = add.gate(root, cid, "HARD-STOP", by="H", reason="found a leak")
    assert ok, "the security finding could not be written down: " + _msg((ok, *rest))


def test_no_existing_refusal_was_narrowed():
    """covers: R:WIDEN — the tiers RECLASSIFY refusals; they must never drop one.

    Rewriting sixteen inline conditions into two named tuples is exactly the edit where a refusal
    quietly disappears: delete a name from both tuples and `_binds` is never called for it, so the
    site it guarded goes unreachable with nothing red. So count them, and prove the classification
    is total — `_binds` raises rather than defaulting, in either direction.
    """
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    gate_src = src[src.index("\ndef gate("):]
    gate_src = gate_src[:gate_src.index("\ndef ", 1)]
    used = set(re.findall(r'_binds\("([a-z_]+)"', gate_src))
    classified = set(add.INTEGRITY_REFUSALS) | set(add.EVIDENCE_REFUSALS)

    assert used == classified, f"declared-but-unused {classified - used}, unclassified {used - classified}"
    # An explicit set, not a count. The count in the first cut of this check was my own
    # arithmetic (14), and running it found the real reason it was wrong: R:UNFROZEN_EXPLORE
    # refuses unconditionally and is not dispatched through `_binds` at all. Naming the members
    # pins strictly more than counting them, and a dropped refusal fails by name.
    assert classified == {
        "unsealed", "drift", "placeholders", "undeclared_sensitive", "phantom_scope",
        "explore_drift", "explore_placeholders",
        "stale_receipt", "failed_run", "unbound_covers", "hollow_explore", "no_security_lens",
        "unbriefed",
    }, f"a refusal was dropped or added: {sorted(classified)}"
    assert not (set(add.INTEGRITY_REFUSALS) & set(add.EVIDENCE_REFUSALS)), "a refusal is in both tiers"
    try:
        add._binds("invented_refusal", "PASS")
    except KeyError:
        pass
    else:
        raise AssertionError("an unclassified refusal silently inherited a tier")
