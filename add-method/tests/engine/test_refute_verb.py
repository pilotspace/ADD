"""Red suite for `/tasks/refute-verb.md` — the refute-read becomes a stamp the gate can order.

`verify.md` mandates a refute-read and `add-advisor` has a refute mode, yet nothing on the node
says a green was ever read against. `add refute` records who tried to break the green, against
which receipt, and what they found — a lens on a green exactly as `advise` is a lens on a beat:
NO-EXEC, no verdict, no floor moved. And the readable example (a filled `E<n>`) joins the
interview, so a human confirms it before the freeze, not only the silences and the Rejects.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

CID = "/tasks/refutable.md"

TASK_BODY = """## CARD
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
- A1 [who] covers: S1 · the request does not say who; taking anyone -> cost
- A2 [which] covers: S1 · n/a · fixture
- A3 [when] covers: S1 · n/a · fixture
- A4 [absent] covers: S1 · n/a · fixture
- A5 [order] covers: S1 · n/a · fixture
- A6 [experience] covers: S1 · n/a · fixture

## EDGES
- E1 Given A(owner me, 100) and B(owner me, 0) · When transfer(A→B, 30) · Then A=70, B=30, result ok
- E2 <a boundary or failure case a check must cover — optional>

## CHECKS
- test_one · covers: M1, E1 · acceptance · runs E1 through the port
- test_two · covers: R:BAD · acceptance · the reject, both balances unchanged
red-first: every check MUST fail first.
"""


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _bundle(tmp_path, *, freeze=True):
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")
    root = tmp_path / ".add"
    add.init(root, "code", "Refuting")
    cid, _ = add.new(root, "Task", "refutable", title="A refutable task", depth="standard",
                     sensitivity="data", scope=["src/service.py"])
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    raw = n["raw"].replace("  - S1 <the surface this publishes — an endpoint, function, or section>",
                           "  - S1 transfer(a, b, amount)")
    add.write(path, f"---\n{add.set_key(raw, 'status', 'build')}\n---\n{TASK_BODY}")
    if freeze:
        add.freeze(root, cid, "human:tindang")
        add.brief_stamp(root, cid)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    return tmp_path


@pytest.fixture
def repo(tmp_path):
    return _bundle(tmp_path)


def _receipt(repo, ids=("test_one", "test_two")):
    xml = repo / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>' for i in ids)
    doc = f"<testsuites><testsuite>{cases}</testsuite></testsuites>"
    return add.run(repo / ".add", CID,
                   [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
                   cwd=repo, junit=xml)


def _stamps(repo, act="refute"):
    fm = add.read(repo / ".add/tasks/refutable.md", "T0")["fm"] or {}
    return [s for s in (fm.get("verified") or []) if isinstance(s, dict) and s.get("act") == act]


def _cli(repo, *args):
    return subprocess.run([sys.executable, str(repo / ".add/tooling/cli.py"), *args],
                          cwd=str(repo), capture_output=True, text=True)


# --- M1 / M2: the stamp -------------------------------------------------------------------------

def test_refute_held_appends_stamp_naming_latest_receipt(repo):
    """covers: M1, A2 — one stamp, outcome held, probes recorded, the receipt it read named."""
    _receipt(repo)
    _, want_cid = add.latest_receipt(repo / ".add", CID)
    stamp, note = add.refute(repo / ".add", CID, by="fresh:verifier", held=True, probes=3,
                             note="varied amounts across the boundary; composed R:BAD with M1")
    assert stamp, note
    stamps = _stamps(repo)
    assert len(stamps) == 1, stamps
    s = stamps[0]
    assert s["outcome"] == "held" and int(s["probes"]) == 3 and s["authority"] == "process"
    assert str(s["receipt"]) == want_cid, (s, want_cid)
    assert "add gate refutable PASS" in note, note


def test_refute_found_records_finding_and_names_the_fix(repo):
    """covers: M2 — a refutation names its input, and the next verb is the fix, never a verdict."""
    _receipt(repo)
    stamp, note = add.refute(repo / ".add", CID, by="fresh:verifier", held=False,
                             finding="transfer(A, B, 0) is accepted and A pays a fee", probes=2)
    assert stamp, note
    s = _stamps(repo)[0]
    assert s["outcome"] == "refuted" and "transfer(A, B, 0)" in str(s.get("note", "")), s
    assert "add run refutable" in note and "add refute refutable" in note, note
    assert "gate" not in note.split("next:", 1)[-1], note
    assert not _stamps(repo, act="gate")


# --- Rejects ------------------------------------------------------------------------------------

def test_refute_refuses_without_receipt(repo):
    """covers: R:NORECEIPT — a refute reads a green; nothing has run."""
    stamp, note = add.refute(repo / ".add", CID, by="v", held=True)
    assert stamp is None and "NORECEIPT" in note, note
    assert not _stamps(repo)


def test_refute_refuses_empty_or_double_outcome(repo):
    """covers: R:NOFINDING — one outcome, and a refutation names its input; at the library AND argv."""
    _receipt(repo)
    stamp, note = add.refute(repo / ".add", CID, by="v", held=False, finding="   ")
    assert stamp is None and "NOFINDING" in note, note
    stamp, note = add.refute(repo / ".add", CID, by="v", held=True, finding="but also this")
    assert stamp is None and "NOFINDING" in note, note
    assert not _stamps(repo)
    r = _cli(repo, "refute", "refutable", "--by", "v", "--held", "--found", "x")
    assert r.returncode == 2, r.stdout + r.stderr          # argparse: mutually exclusive
    r = _cli(repo, "refute", "refutable", "--by", "v")
    assert r.returncode == 2, r.stdout + r.stderr          # argparse: one of them is required


def test_refute_refuses_unsealed(tmp_path):
    """covers: R:UNSEALED — no approved intent to read the green against."""
    repo = _bundle(tmp_path, freeze=False)
    stamp, note = add.refute(repo / ".add", CID, by="v", held=True)
    assert stamp is None and "UNSEALED" in note, note


def test_refute_writes_no_verdict(repo):
    """covers: R:NOVERDICT — a lens on a green: no gate stamp, no status move, no floor change."""
    _receipt(repo)
    before = add.read(repo / ".add/tasks/refutable.md", "T0")["fm"]
    graph = add.scan(repo / ".add")
    floor_before = add.authority_for(graph, CID)
    add.refute(repo / ".add", CID, by="v", held=True)
    after = add.read(repo / ".add/tasks/refutable.md", "T0")["fm"]
    assert after["status"] == before["status"]
    assert not _stamps(repo, act="gate")
    assert add.authority_for(add.scan(repo / ".add"), CID) == floor_before


# --- M4: the front door and the registries -------------------------------------------------------

def test_refute_is_wired_and_counted(repo):
    """covers: M4 — a verb is met only at argv (M40); the count pins and FORMAT learned it."""
    import cli
    sub = next(a for a in cli.build_parser()._actions
               if getattr(a, "choices", None) and isinstance(a.choices, dict))
    assert "refute" in sub.choices, sorted(sub.choices)
    assert len(sub.choices) == 28, sorted(sub.choices)
    wired = (REPO / "tests" / "engine" / "test_cli.py").read_text(encoding="utf-8")
    assert '"refute"' in wired[wired.find("WIRED = {"):wired.find("}", wired.find("WIRED = {"))]
    for rel, needle in (("tests/skill/test_search_registry.py", "n == 28"),
                        ("tests/engine/test_show_verb.py", "28 verbs"),
                        ("tests/engine/test_authoring_beat.py", "== 28"),
                        ("README.md", "28 verbs")):
        assert needle in (REPO / rel).read_text(encoding="utf-8"), f"{rel}: pin not re-aimed to 28"
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    assert re.search(r"^### §8\.4 .*refute", fmt, re.M), "FORMAT §8.4 does not state the refute stamp"
    assert "act: refute" in fmt
    _receipt(repo)
    r = _cli(repo, "refute", "refutable", "--by", "v", "--held", "--probes", "1")
    assert r.returncode == 0 and "next:" in r.stdout, r.stdout + r.stderr
    assert _stamps(repo)


# --- M3 / E1: the example joins the interview -------------------------------------------------------

def test_interview_compiles_filled_edges_and_skips_placeholders(tmp_path):
    """covers: M3, E1 — E1 is a question with dim `edge`, after A and before R; the scaffold line is not."""
    repo = _bundle(tmp_path, freeze=False)
    decisions, note = add.interview(repo / ".add", CID)
    ids = [d["id"] for d in decisions]
    assert "E1" in ids and "E2" not in ids, ids
    assert ids.index("A1") < ids.index("E1") < ids.index("R:BAD"), ids
    e1 = next(d for d in decisions if d["id"] == "E1")
    assert e1["dim"] == "edge" and "Given A(owner me, 100)" in e1["reading"], e1
    assert "E1 [edge]" in note, note
    node = add.read(repo / ".add/tasks/refutable.md", "T2")
    _, note2 = add.interview(repo / ".add", CID, answers={"A1": "confirm", "R:BAD": "confirm"}, by="h")
    assert add.interview_gap(node, add.read(repo / ".add/tasks/refutable.md", "T0")["fm"]) == ["E1"]
    add.interview(repo / ".add", CID, answers={"E1": "confirm"}, by="h")
    assert add.interview_gap(node, add.read(repo / ".add/tasks/refutable.md", "T0")["fm"]) == []


# --- E2: chronology stays on the record ------------------------------------------------------------

def test_refute_stamp_survives_a_later_run(repo):
    """covers: E2 — a refute names the run it read; a later run does not rewrite it."""
    _receipt(repo)
    _, first = add.latest_receipt(repo / ".add", CID)
    add.refute(repo / ".add", CID, by="v", held=True)
    _receipt(repo)
    _, second = add.latest_receipt(repo / ".add", CID)
    assert first != second
    assert str(_stamps(repo)[0]["receipt"]) == first
