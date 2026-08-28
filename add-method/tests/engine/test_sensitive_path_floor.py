"""The A17 sensitive-path floor arms the security refusals, not just the authority level.

`authority_for` is `max(sensitivity floor, A17 sensitive-path floor)` — a task whose `scope:` matches
`index.md`'s `sensitive_paths:` is floored at `human` even with no declared `sensitivity:`. Both halves
of the security floor must read that computed floor, not the literal `sensitivity: security` key:

- R:SECURITYFOLD — such a node cannot be signed into a `RISK-ACCEPTED`.
- R:NOCOVERAGE  — such a node cannot be signed `PASS` without a named lens.

Otherwise the bundle's own path classification is advisory: a task editing `src/auth/**` with no
declared sensitivity signs itself away, which is the one path the security floor exists to close.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


TASK_BODY = """## CARD
goal: a task whose rules are all provable
beat: build · next: add run

## RULES
<must>
- M1 the first rule
</must>
<reject>
- R:BAD something forbidden -> "BAD"
</reject>

## CHECKS
- test_one · covers: M1, R:BAD · proves the rule and the reject
red-first: every check MUST fail first.
"""


def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _repo_with_node(tmp_path, scope, sensitive_paths, lens=None):
    """A git repo + bundle + a scoped task in `build` with a green, bound, fresh receipt.

    `sensitive_paths` is written onto `index.md`; the task declares NO `sensitivity:`, so the only
    thing that can floor it is the A17 path match. Returns `(root, cid)`.
    """
    _git("init", "-q", cwd=tmp_path)
    _git("config", "user.email", "t@example.com", cwd=tmp_path)
    _git("config", "user.name", "T", cwd=tmp_path)
    target = tmp_path / scope
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def login():\n    return True\n")

    root = tmp_path / ".add"
    add.init(root, "code", "Floor")

    index = root / "index.md"
    n = add.read(index, "T2")
    listed = "".join(f"\n  - {p}" for p in sensitive_paths)
    raw = n["raw"].replace("sensitive_paths: []", f"sensitive_paths:{listed}")
    add.write(index, f"---\n{raw}\n---\n{n['body']}")

    fields = dict(lens or {})
    cid, _ = add.new(root, "Task", "gated", title="A gated task", depth="standard",
                     scope=[scope], **fields)
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'build')}\n---\n{TASK_BODY}")
    add.freeze(root, cid, "human:t")   # `gate` refuses an unsealed PASS (R:UNSEALED)
    add.brief_stamp(root, cid)
    _git("add", "-A", cwd=tmp_path)
    _git("commit", "-q", "-m", "init", cwd=tmp_path)

    xml = tmp_path / "r.xml"
    doc = ('<testsuites><testsuite>'
           '<testcase classname="c" name="test_one"/>'
           '</testsuite></testsuites>')
    add.run(root, cid, [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
            cwd=tmp_path, junit=xml)
    return root, cid


def _gate_stamped(root, cid):
    fm = add.read(root / cid.lstrip("/"), "T2")["fm"]
    return any(s.get("act") == "gate" for s in (fm.get("verified") or []) if isinstance(s, dict))


def test_path_floored_node_is_human_authority(tmp_path):
    """covers: M1 — the A17 path match alone floors authority at `human`, with no `sensitivity:`."""
    root, cid = _repo_with_node(tmp_path, "src/auth/login.py", ["src/auth/**"])
    graph = add.scan(root)
    assert (graph[cid]["fm"] or {}).get("sensitivity") is None, "the fixture must declare no sensitivity"
    assert add.authority_for(graph, cid) == "human", "an A17 path match floors at human"


def test_path_floored_node_refuses_risk_accepted(tmp_path):
    """covers: R:SECURITYFOLD — a path-floored node cannot be folded into a RISK-ACCEPTED."""
    root, cid = _repo_with_node(tmp_path, "src/auth/login.py", ["src/auth/**"])
    ok, note = add.gate(root, cid, "RISK-ACCEPTED", by="human:tindang", reason="demo")
    assert ok is False, "a path-floored node must not be signed into a RISK-ACCEPTED"
    assert "HARD-STOP" in note or "security" in note.lower(), note
    assert not _gate_stamped(root, cid), "a refused gate must record no stamp"


def test_path_floored_node_refuses_pass_without_lens(tmp_path):
    """covers: R:NOCOVERAGE — a path-floored node needs a named lens to be signed PASS."""
    root, cid = _repo_with_node(tmp_path, "src/auth/login.py", ["src/auth/**"])
    ok, note = add.gate(root, cid, "PASS", by="human:tindang")
    assert ok is False, "a path-floored PASS with no lens must be refused"
    assert "R:NOCOVERAGE" in note or "lens" in note.lower(), note
    assert not _gate_stamped(root, cid), "a refused gate must record no stamp"


def test_path_floored_node_passes_with_a_lens(tmp_path):
    """covers: M2 — the floor binds lens PRESENCE; a lensed path-floored node still passes."""
    root, cid = _repo_with_node(tmp_path, "src/auth/login.py", ["src/auth/**"],
                                lens={"advised_by": "sec-reviewer"})
    ok, note = add.gate(root, cid, "PASS", by="human:tindang")
    assert ok is True, f"a lensed path-floored node must still pass: {note}"


def test_unmatched_scope_is_untouched(tmp_path):
    """covers: E1 — the floor widens to A17 matches ONLY; an unmatched node keeps its old paths."""
    root, cid = _repo_with_node(tmp_path, "src/util/fmt.py", ["src/auth/**"])
    graph = add.scan(root)
    assert add.authority_for(graph, cid) == "process", "an unmatched scope must not be floored"
    ok, note = add.gate(root, cid, "RISK-ACCEPTED", by="human:tindang", reason="demo")
    assert ok is True, f"a non-sensitive node must still accept a signed risk: {note}"
