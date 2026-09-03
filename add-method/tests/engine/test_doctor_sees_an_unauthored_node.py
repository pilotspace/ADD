"""A bundle nobody has authored is reported as conformant.

`placeholders_in` finds template tokens still standing in a node's RULES, ASSUMPTIONS or CHECKS.
It is correct, it is trusted, and exactly one caller uses it: the gate. So the failure only ever
surfaces at the end of the loop, to someone who has already done the work — and never to the
newcomer who runs `doctor` to ask whether their bundle is in good shape.

Measured 2026-09-03, on the incumbent engine, on a bundle whose only task is 100% scaffold:

    $ add doctor
    no findings                                 <- over a node with nothing written in it
    next: add status

An oracle wired to one caller is a guard for one caller.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

CODE = "unauthored_node"


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _findings(root, code=CODE):
    return [f for f in add.doctor(root) if f.get("code") == code]


# ------------------------------------------------------------------ M1/M2 · the finding

def test_doctor_reports_a_fully_template_node(tmp_path):
    """covers: M1, A3, R:GREENBUNDLE — the measured "no findings"."""
    root = _bundle(tmp_path)
    add.new(root, "Task", "probe", title="p")
    found = _findings(root)
    assert found, "doctor reported no finding for a node that is 100% scaffold"
    assert found[0]["severity"] == "warn", \
        f"a fresh scaffold is unwritten, not broken: {found[0]}"


def test_the_finding_names_the_node_and_a_token(tmp_path):
    """covers: M2, A6 — the fix is to write the node, so the finding must say where."""
    root = _bundle(tmp_path)
    add.new(root, "Task", "probe", title="p")
    f = _findings(root)[0]
    assert "probe" in str(f.get("node")), f"the finding does not name the node: {f}"
    assert "<" in f.get("detail", ""), \
        f"the finding names no standing token, so the author cannot see what to replace: {f}"


# ------------------------------------------------------------------ M3 · what stays quiet

def test_an_authored_node_produces_no_finding(tmp_path):
    """covers: M3 — the guard reports scaffolds, not nodes."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "written", title="w")
    p = root / cid.lstrip("/")
    body = p.read_text(encoding="utf-8")
    for hole, real in (
            ("- M1 <the rule that must hold>", "- M1 the rule that must hold"),
            ('- R:<NAME> <what must never happen> -> "<NAME>"', '- R:Z it must never happen -> "Z"'),
            ("- <test_name> · covers: M1 · <what it proves>", "- test_x · covers: M1, R:Z · it proves"),
            ("goal: <one line>", "goal: the fixture's stated one line."),
    ):
        assert hole in body, f"the scaffold no longer ships {hole!r} — re-aim this fixture"
        body = body.replace(hole, real)
    import re
    body = re.sub(r"^- A\d+ \[(\w+)\].*$", r"- A\1 [\1] covers: S1 · n; taking r -> c",
                  body, flags=re.M)
    body = body.replace("- S1 <the surface this publishes — an endpoint, function, or section>",
                        "- S1 x")
    p.write_text(body, encoding="utf-8")
    assert not _findings(root), f"an authored node was reported: {_findings(root)}"


# ------------------------------------------------------------------ counter-guards

def test_a_partly_authored_node_is_still_reported(tmp_path):
    """covers: M1, E1 — one standing token is enough; a half-written node is not written."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "half", title="h")
    p = root / cid.lstrip("/")
    p.write_text(p.read_text(encoding="utf-8")
                 .replace("- M1 <the rule that must hold>", "- M1 a real rule"), encoding="utf-8")
    assert _findings(root), "a node with RULES written and CHECKS still template was not reported"


def test_doctor_and_the_gate_read_the_same_oracle(tmp_path):
    """covers: M4, A4, A2, E2 — one detector, not two.

    A2/E2: a Persona has no RULES to author, so it must never earn this finding — there would be
    nothing an author could do to clear it. A seeded bundle ships four of them.
    """
    root = _bundle(tmp_path)
    add.new(root, "Task", "probe", title="p")

    # `scan()` nodes carry NO body and `placeholders_in` reads the body — so the oracle must be
    # given a node that has one. That asymmetry is exactly what made doctor's first wiring a
    # guard that could never fire, so the check states the input shape explicitly.
    node = add.read(root / "tasks" / "probe.md", "T2")
    standing = add.placeholders_in(node)
    assert standing, "the fixture is not actually a scaffold — re-aim it"
    detail = _findings(root)[0]["detail"]
    assert any(tok in detail for tok in standing), \
        "doctor's finding does not report what placeholders_in found — two oracles, not one"

    personas = [f for f in _findings(root) if "/personas/" in str(f.get("node"))]
    assert personas == [], f"a Persona has no RULES to author and cannot clear this: {personas}"
