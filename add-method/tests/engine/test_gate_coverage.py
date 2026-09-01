"""The security coverage floor (A2, task 1): a security PASS needs a named lens.

`gate` refuses a PASS on a `sensitivity: security` node that carries no lens (`persona:`/`advised_by:`)
— R:NOCOVERAGE. A lensed security node passes; a non-security node is untouched (the floor is
security-only, mirroring R:SECURITYFOLD).
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _interview_all(root, cid, by="human:t"):
    """Answer every open decision, so a human-floor freeze is not refused (R:UNINTERVIEWED).

    A fixture that skips the interview tests no real path: `freeze` returns a refusal, the seal is
    never written, and the gate then fails on R:UNSEALED — a green-looking fixture proving nothing.
    """
    qs, _ = add.interview(root, cid)
    if qs:
        add.interview(root, cid, answers={q["id"]: "confirm" for q in qs}, by=by)




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


def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _repo_with_node(tmp_path, sensitivity, lens=None):
    """A git repo + bundle + a scoped task in `build`, given sensitivity and optional lens.

    Returns (repo_root, cid). A green, covers-bound, fresh receipt is recorded so the only open
    question at the gate is the coverage floor under test.
    """
    _git("init", "-q", cwd=tmp_path)
    _git("config", "user.email", "t@example.com", cwd=tmp_path)
    _git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")

    root = tmp_path / ".add"
    add.init(root, "code", "Cov")
    fields = {"sensitivity": sensitivity, "scope": ["src/service.py"]}
    if lens:
        fields.update(lens)
    cid, _ = add.new(root, "Task", "gated", title="A gated task", depth="standard", **fields)
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'build')}\n---\n{TASK_BODY}")
    # The seal, then the brief entry — `gate` refuses a PASS on a node that was never
    # frozen (R:UNSEALED), so a fixture that skips the one approval tests no real path.
    _interview_all(root, cid)
    node, why = add.freeze(root, cid, "human:t")
    assert node is not None, f"fixture could not freeze: {why!r}"
    add.brief_stamp(root, cid)
    _git("add", "-A", cwd=tmp_path)
    _git("commit", "-q", "-m", "init", cwd=tmp_path)

    xml = tmp_path / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>' for i in ("test_one", "test_two"))
    # The command writes the report, so both halves of the receipt come from the same
    # process — a file dropped beside the run no longer earns `kind: test-ids`.
    doc = f"<testsuites><testsuite>{cases}</testsuite></testsuites>"
    add.run(root, cid, [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
            cwd=tmp_path, junit=xml)
    return root, cid


def test_security_pass_without_lens_refuses(tmp_path):
    """covers: R:NOCOVERAGE — a security node with a green bound receipt but no lens refuses PASS."""
    root, cid = _repo_with_node(tmp_path, "security")
    ok, note = add.gate(root, cid, "PASS", by="human:tindang")
    assert ok is False, "a security PASS with no lens must be refused"
    assert "R:NOCOVERAGE" in note or "lens" in note.lower(), note
    fm = add.read(root / cid.lstrip("/"), "T2")["fm"]
    assert not any(s.get("act") == "gate" for s in (fm.get("verified") or []) if isinstance(s, dict)), \
        "a refused gate must record no stamp"


def test_security_pass_with_lens_is_recorded(tmp_path):
    """covers: M1 — the same security node with `advised_by:` set gates PASS."""
    root, cid = _repo_with_node(tmp_path, "security", lens={"advised_by": "sec-rev"})
    ok, note = add.gate(root, cid, "PASS", by="human:tindang")
    assert ok is True, note


def test_nonsecurity_pass_without_lens_is_untouched(tmp_path):
    """covers: M1 — an architecture node with no lens still gates PASS (the floor is security-only)."""
    root, cid = _repo_with_node(tmp_path, "architecture")
    ok, note = add.gate(root, cid, "PASS", by="human:tindang")
    assert ok is True, note
