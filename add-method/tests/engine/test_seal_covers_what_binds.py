"""What the gate BINDS and what the freeze SEALS were two different sets.

`referents_of` = RULES + `## EDGES` + probed `A<n>`. `direction_digest` seals RULES + CHECKS +
`gives:`. So two of the three bindable classes sat outside the seal, and the repair for a gate
refusal was to DELETE the obligation rather than prove it:

    add gate t2 PASS --by tin
        cannot record `PASS` — these rules have no reported passing check: A1, E1
    (silently delete the E1 line; strip "· probe:" from A1. No refreeze.)
    add gate t2 PASS --by tin
        gate PASS recorded at authority `process`

No drift refusal, no `refreeze` stamp, no doctor finding. That is precisely "never edit a frozen
contract to pass a build", unenforceable for two of three referent kinds.

The repair is a SECOND digest, not a wider `direction:`. Widening the existing one would re-digest
every node this repo has already frozen and strand them, and `test_assumptions_section.py` pins
ASSUMPTIONS out of `direction:` deliberately — that decision was right when `A<n>` bound nothing.
`binding:` seals the REFERENT SET, so deleting an obligation is drift while refining the prose
around it stays free. A node frozen before this shipped carries no `binding:` and stays gateable,
the same stance `sealed_direction` already takes.
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
    """A Task carrying BOTH unsealed referent kinds: a real edge and a probed assumption."""
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
    assumptions = "".join(
        f"- A{i} [{d}] covers: S1 · the request does not say; taking the plain reading -> minor"
        + (" · probe: the lister rejects a cross-tenant id\n" if d == "who" else "\n")
        for i, d in enumerate(DIMS, 1))
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + assumptions
               + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## EDGES\n.*?(?=\n## )",
               "## EDGES\n- E1 the caller's tenant has no rows at all\n", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_only_own_rows · covers: M1, R:LEAK, E1, A1 · proves isolation\n"
               "red-first", t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid


def _sealed(root, slug="t", **fields):
    cid = _authored(root, slug, **fields)
    _, questions = add.interview(root, cid)
    open_ids = re.findall(r"^(A\d+|M\d+|R:[A-Z0-9_]+)\b", str(questions), re.M)
    if open_ids:
        add.interview(root, cid, answers={i: "confirm" for i in open_ids}, by="H")
    node, note = add.freeze(root, cid, by="H", authority="human")
    assert node is not None, f"fixture could not freeze: {note!r}"
    add.brief_stamp(root, cid, by="H")
    return cid


def _green_receipt(root, cid, tmp_path):
    xml = tmp_path / f"{cid.rsplit('/', 1)[-1]}.xml"
    doc = ('<testsuites><testsuite>'
           '<testcase classname="c" name="test_only_own_rows"/>'
           '</testsuite></testsuites>')
    return add.run(root, cid,
                   [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"], junit=xml)


def _edit(root, cid, old, new=""):
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    assert old in t, f"fixture edit found nothing to replace: {old!r}"
    p.write_text(t.replace(old, new), encoding="utf-8")


def _msg(result):
    return str(result[-1])


# ------------------------------------------------- M1 · the seal reaches every bindable class

def test_the_fixture_binds_both_unsealed_classes(tmp_path):
    """covers: M1 — a guard over E<n>/A<n> proves nothing unless the node actually has them."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "shape")
    # `scan` carries no body; the referent readers want a T2 read (edges_of goes to disk itself).
    node = add.read(root / cid.lstrip("/"), "T2")
    node["path"] = root / cid.lstrip("/")
    assert add.edges_of(node) == ["E1"], add.edges_of(node)
    assert add.probed_assumptions(node) == ["A1"], add.probed_assumptions(node)


def test_deleting_a_frozen_edge_is_drift(tmp_path):
    """covers: M1, E1 — the measured repair: delete the obligation instead of proving it."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "edge")
    _edit(root, cid, "- E1 the caller's tenant has no rows at all\n")
    _green_receipt(root, cid, tmp_path)

    ok, *rest = add.gate(root, cid, "PASS", by="H")
    assert not ok, "a frozen edge was deleted after the freeze and the gate did not notice"
    assert "drift" in _msg((ok, *rest)).lower() or "refreez" in _msg((ok, *rest)).lower()


def test_unprobing_a_frozen_assumption_is_drift(tmp_path):
    """covers: M1, E2 — stripping `· probe:` retires a referent; that is a contract change."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "probe")
    _edit(root, cid, " · probe: the lister rejects a cross-tenant id")
    _green_receipt(root, cid, tmp_path)

    ok, *rest = add.gate(root, cid, "PASS", by="H")
    assert not ok, "a probed assumption was silently unprobed and the gate did not notice"
    assert "drift" in _msg((ok, *rest)).lower() or "refreez" in _msg((ok, *rest)).lower()


def test_the_drift_refusal_binds_every_verdict(tmp_path):
    """covers: M2 — a refusal that protects the RECORD is not PASS-only (the 3.3.0 split)."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "ra")
    _edit(root, cid, "- E1 the caller's tenant has no rows at all\n")
    _green_receipt(root, cid, tmp_path)

    ok, *rest = add.gate(root, cid, "RISK-ACCEPTED", by="H", reason="probing")
    assert not ok, "RISK-ACCEPTED signed for a silently deleted obligation"


# ------------------------------------------------- M3 · it must not over-seal

def test_refining_the_prose_around_a_referent_is_not_drift(tmp_path):
    """covers: M3 — `binding:` seals the referent SET, so ordinary editing stays free.

    This is why `direction:` was scoped narrowly in the first place: a seal authors refreeze
    reflexively is a rubber stamp. Rewording an edge without retiring it must stay quiet.
    """
    root = _bundle(tmp_path)
    cid = _sealed(root, "reword")
    _edit(root, cid, "the caller's tenant has no rows at all", "the tenant has no rows")
    _edit(root, cid, "the request does not say", "the ticket does not say")
    _green_receipt(root, cid, tmp_path)

    ok, *rest = add.gate(root, cid, "PASS", by="H")
    assert ok, f"a reword that retired nothing was refused as drift: {_msg((ok, *rest))}"


def test_a_refreeze_records_the_change_and_clears_it(tmp_path):
    """covers: M4 — a frozen contract changes BY REFREEZING; that path must work."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "refrozen")
    _edit(root, cid, "- E1 the caller's tenant has no rows at all\n")
    _edit(root, cid, ", E1", "")                       # the check no longer cites it
    node, note = add.freeze(root, cid, by="H", authority="human")
    assert node is not None, f"the repair path is blocked: {note!r}"
    add.brief_stamp(root, cid, by="H")
    _green_receipt(root, cid, tmp_path)

    ok, *rest = add.gate(root, cid, "PASS", by="H")
    assert ok, f"a recorded, refrozen change was still refused: {_msg((ok, *rest))}"


def test_a_node_frozen_before_the_seal_still_gates(tmp_path):
    """covers: M5, E3 — None means "cannot verify", never "verified dirty"."""
    root = _bundle(tmp_path)
    cid = _sealed(root, "presealed")
    p = root / cid.lstrip("/")
    # strip the new field from the freeze stamp, leaving a pre-change record shape
    p.write_text(re.sub(r", binding: \"[^\"]*\"", "", p.read_text(encoding="utf-8")),
                 encoding="utf-8")
    fm = add.scan(root)[cid]["fm"] or {}
    assert add.sealed_binding(fm) is None, "the fixture did not reach the pre-seal shape"
    _green_receipt(root, cid, tmp_path)

    ok, *rest = add.gate(root, cid, "PASS", by="H")
    assert ok, f"a node frozen by a pre-seal engine was stranded: {_msg((ok, *rest))}"


def test_the_direction_digest_is_unchanged(tmp_path):
    """covers: M5 — every node already frozen keeps verifying; this adds a field, moves none."""
    root = _bundle(tmp_path)
    cid = _authored(root, "stable")
    node = add.read((root / cid.lstrip("/")), "T2")
    before = add.direction_digest(node)

    node["body"] = node["body"].replace(
        "- E1 the caller's tenant has no rows at all", "- E1 something else entirely")
    assert add.direction_digest(node) == before, (
        "`direction:` now moves with EDGES — every node frozen before this change is stranded")
