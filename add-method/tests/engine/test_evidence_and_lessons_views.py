"""Red suite for `/tasks/evidence-and-lessons-are-views.md` — the engine writes EVIDENCE and LESSONS.

FORMAT §5 promised "EVIDENCE receipt / gate · LESSONS harvested at done" and the placeholder guard
skipped both sections because "they are filled by the run and the close". Nothing wrote them: on
this bundle 88 of 113 done tasks carried the EVIDENCE scaffold and 64 the LESSONS scaffold beside a
`verified[]` that held the truth. The sections are VIEWS of the record — keyed lines the producing
verb writes, a harvest at close, a `--sync` backfill — never a second store (R:TWOHOMES) and never
invented history (R:MANUFACTURED).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

CID = "/tasks/viewed.md"

BODY = """## CARD
goal: a task whose evidence is written down
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

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
"""


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _bundle(tmp_path, *, sensitivity="mechanical", evidence=None, freeze=True):
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")
    root = tmp_path / ".add"
    add.init(root, "code", "Viewed")
    cid, _ = add.new(root, "Task", "viewed", title="A viewed task", depth="standard",
                     sensitivity=sensitivity, scope=["src/service.py"])
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    raw = n["raw"].replace("  - S1 <the surface this publishes — an endpoint, function, or section>", "  - S1 book()")
    body = BODY if evidence is None else BODY.replace(
        "## EVIDENCE\nreceipt: <runs/<n>.md>\ngate: <PASS | RISK-ACCEPTED | HARD-STOP>\n", evidence)
    add.write(path, f"---\n{raw}\n---\n{body}")
    if freeze:
        ok, note = add.freeze(root, cid, "human:tindang")
        assert ok, note
        add.brief_stamp(root, cid)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    return root


def _receipt(root, ids=("test_one", "test_two")):
    repo = root.parent
    xml = repo / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>' for i in ids)
    doc = f"<testsuites><testsuite>{cases}</testsuite></testsuites>"
    return add.run(root, CID, [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
                   cwd=repo, junit=xml)


def _section(root, name):
    body = add.read(root / "tasks/viewed.md", "T2")["body"]
    return add._section_of(body, name)


SCAFFOLD_RECEIPT = "receipt: <runs/<n>.md>"
SCAFFOLD_GATE = "gate: <PASS | RISK-ACCEPTED | HARD-STOP>"
SCAFFOLD_LESSON = "- <lesson> -> add learn <lens>"


# --- M1 / E1 ---------------------------------------------------------------------------------------

def test_run_writes_the_receipt_line(tmp_path):
    """covers: M1, E1 — the scaffold goes, `receipt:` names the run; a `pending` line is replaced, a foreign line survives."""
    root = _bundle(tmp_path, evidence="## EVIDENCE\nreceipt: pending\ngate: pending\nnote: a human wrote this\n")
    _receipt(root)
    _, rc = add.latest_receipt(root, CID)
    ev = _section(root, "EVIDENCE")
    lines = [l for l in ev.splitlines() if l.strip()]
    receipt_lines = [l for l in lines if l.startswith("receipt:")]
    assert len(receipt_lines) == 1 and rc in receipt_lines[0] and "kind: test-ids" in receipt_lines[0], ev
    assert "receipt: pending" not in ev and SCAFFOLD_RECEIPT not in ev
    assert "note: a human wrote this" in lines, ev
    assert "gate: pending" in lines, "a line the run did not produce must not move"


# --- M2 ------------------------------------------------------------------------------------------------

def test_refute_writes_the_refute_line(tmp_path):
    """covers: M2 — outcome · probes · by · run cid, on one keyed line, replaced on a second refute."""
    root = _bundle(tmp_path)
    _receipt(root)
    _, rc = add.latest_receipt(root, CID)
    add.refute(root, CID, by="fresh:verifier", held=False, finding="book() with no session", probes=2)
    ev = _section(root, "EVIDENCE")
    line = next(l for l in ev.splitlines() if l.startswith("refute:"))
    assert "refuted" in line and "2 probe" in line and "fresh:verifier" in line and rc in line, line
    add.refute(root, CID, by="fresh:verifier", held=True, probes=3)
    ev = _section(root, "EVIDENCE")
    refutes = [l for l in ev.splitlines() if l.startswith("refute:")]
    assert len(refutes) == 1 and "held" in refutes[0] and "3 probe" in refutes[0], ev


# --- M3 / E2 / A5 ----------------------------------------------------------------------------------------

def test_gate_writes_the_gate_line_naming_the_gated_receipt(tmp_path):
    """covers: M3, E2, A5 — two runs, gate PASS: `receipt:` and `gate:` both name run 2."""
    root = _bundle(tmp_path)
    _receipt(root)
    _, first = add.latest_receipt(root, CID)
    _receipt(root)
    _, second = add.latest_receipt(root, CID)
    ok, note = add.gate(root, CID, "PASS", "human:tindang")
    assert ok, note
    ev = _section(root, "EVIDENCE")
    receipt_line = next(l for l in ev.splitlines() if l.startswith("receipt:"))
    gate_line = next(l for l in ev.splitlines() if l.startswith("gate:"))
    assert second in receipt_line and first not in receipt_line, ev
    assert "PASS" in gate_line and second in gate_line and "human:tindang" in gate_line, ev
    assert SCAFFOLD_GATE not in ev


# --- M4 / A2 ----------------------------------------------------------------------------------------------

def test_close_harvests_lessons_that_cite_the_task(tmp_path):
    """covers: M4, A2 — a delta citing `/tasks/<slug>.md` lands; one citing a test file does not; `done` harvests too."""
    root = _bundle(tmp_path)
    _receipt(root)
    ok, _ = add.learn(root, "system", "the citing lesson", evidence="/tasks/viewed.md")
    assert ok
    ok, _ = add.learn(root, "method", "a lesson about a test file", evidence="tests/test_x.py")
    assert ok
    ok, _ = add.learn(root, "quality", "a lesson citing the sidecar", evidence="/tasks/viewed.d/runs/1.md")
    assert ok
    ok, note = add.gate(root, CID, "PASS", "human:tindang")
    assert ok, note
    ls = _section(root, "LESSONS")
    assert "the citing lesson" in ls and "a lesson citing the sidecar" in ls, ls
    assert "a lesson about a test file" not in ls, ls
    assert SCAFFOLD_LESSON not in ls
    assert re.search(r"^- \[system · S\d+ · open\]", ls, re.M), ls


def test_close_with_no_citing_lesson_writes_none_filed(tmp_path):
    """covers: M4 — the scaffold line is gone and the section says why."""
    root = _bundle(tmp_path)
    _receipt(root)
    ok, note = add.gate(root, CID, "PASS", "human:tindang")
    assert ok, note
    ls = _section(root, "LESSONS")
    assert SCAFFOLD_LESSON not in ls and "none filed" in ls, ls


def test_learn_tells_the_caller_how_to_be_harvested(tmp_path):
    """covers: A2 — a lesson whose evidence names no task is told how to land on one."""
    root = _bundle(tmp_path)
    _, note = add.learn(root, "system", "lesson", evidence="tests/test_x.py")
    assert "/tasks/<slug>.md" in note, note


# --- M5 / R:MANUFACTURED / R:TWOHOMES -----------------------------------------------------------------------------

def test_sync_backfills_scaffold_sections_from_the_record(tmp_path):
    """covers: M5 — a done node with scaffold sections and real stamps is repaired and reported."""
    root = _bundle(tmp_path)
    _receipt(root)
    add.refute(root, CID, by="v", held=True, probes=1)
    ok, note = add.gate(root, CID, "PASS", "human:tindang")
    assert ok, note
    # put the scaffold back by hand — the state every pre-3.7 done node is in
    path = root / "tasks/viewed.md"
    n = add.read(path, "T2")
    body = re.sub(r"## EVIDENCE\n(?:.*\n)*?\n", f"## EVIDENCE\n{SCAFFOLD_RECEIPT}\n{SCAFFOLD_GATE}\n\n", n["body"])
    body = re.sub(r"## LESSONS\n(?:.*\n?)*", f"## LESSONS\n{SCAFFOLD_LESSON}\n", body)
    add.write(path, f"---\n{n['raw']}\n---\n{body}")
    assert SCAFFOLD_RECEIPT in _section(root, "EVIDENCE") and SCAFFOLD_LESSON in _section(root, "LESSONS")
    ok, note = add.doctor_sync(root)
    assert ok and "viewed" in note and "EVIDENCE" in note, note
    ev, ls = _section(root, "EVIDENCE"), _section(root, "LESSONS")
    _, rc = add.latest_receipt(root, CID)
    assert rc in ev and "refute: held" in ev and "gate: PASS" in ev, ev
    assert SCAFFOLD_LESSON not in ls and "none filed" in ls, ls


def test_sync_never_manufactures_a_line(tmp_path):
    """covers: R:MANUFACTURED — no refute stamp → no `refute:` line; no run → nothing written; no citing delta → none filed, never a borrowed one."""
    root = _bundle(tmp_path)
    ok, note = add.doctor_sync(root)                       # frozen, never run: entitled to nothing
    assert SCAFFOLD_RECEIPT in _section(root, "EVIDENCE"), note
    _receipt(root)
    add.learn(root, "system", "somebody else's lesson", evidence="/tasks/other.md")
    ok, note = add.gate(root, CID, "PASS", "human:tindang")
    assert ok, note
    ev, ls = _section(root, "EVIDENCE"), _section(root, "LESSONS")
    assert not any(l.startswith("refute:") for l in ev.splitlines()), ev
    assert "somebody else's lesson" not in ls and "none filed" in ls, ls


def test_sync_and_verbs_never_overwrite_authored_lines(tmp_path):
    """covers: R:TWOHOMES — a free-text line in EVIDENCE survives run, gate and sync byte-for-byte."""
    root = _bundle(tmp_path, evidence="## EVIDENCE\nreceipt: <runs/<n>.md>\ngate: <PASS | RISK-ACCEPTED | HARD-STOP>\nreviewer note: the fixture is thin on purpose\n")
    _receipt(root)
    ok, note = add.gate(root, CID, "PASS", "human:tindang")
    assert ok, note
    add.doctor_sync(root)
    ev = _section(root, "EVIDENCE")
    _, rc = add.latest_receipt(root, CID)
    assert rc in ev and "gate: PASS" in ev, "the view was not written — the survival below would be vacuous"
    assert "reviewer note: the fixture is thin on purpose" in ev.splitlines(), ev


# --- M6 ------------------------------------------------------------------------------------------------------

def test_doctor_reports_a_done_node_still_carrying_the_scaffold(tmp_path):
    """covers: M6 — `evidence_scaffold` (info) before sync, none after."""
    root = _bundle(tmp_path)
    _receipt(root)
    ok, note = add.gate(root, CID, "PASS", "human:tindang")
    assert ok, note
    path = root / "tasks/viewed.md"
    n = add.read(path, "T2")
    body = re.sub(r"## LESSONS\n(?:.*\n?)*", f"## LESSONS\n{SCAFFOLD_LESSON}\n", n["body"])
    add.write(path, f"---\n{n['raw']}\n---\n{body}")
    findings = add.doctor(root)
    hits = [f for f in findings if f.get("code") == "evidence_scaffold"]
    assert hits and all(f.get("severity") == "info" for f in hits), findings
    add.doctor_sync(root)
    assert not [f for f in add.doctor(root) if f.get("code") == "evidence_scaffold"]


def test_format_book_and_comment_state_the_sections_as_views():
    """covers: M6 — FORMAT §5, docs 12 and the placeholder guard's comment say who writes them."""
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    sec = fmt[fmt.index("## §5 The Task body"):fmt.index("## §6")]
    assert re.search(r"EVIDENCE.*(view|written by)", sec) and "harvested" in sec, "FORMAT §5 does not state the sections as engine-written views"
    assert "doctor --sync" in sec or "`sync`" in sec, "FORMAT §5 does not name the backfill"
    book = (REPO / "docs" / "12-bundle-format.md").read_text(encoding="utf-8")
    assert re.search(r"`## EVIDENCE`.*(engine|written)", book) and re.search(r"`## LESSONS`.*harvest", book), "docs 12 still describes the sections as authored"
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    assert "EVIDENCE and LESSONS are filled by the run" not in src or "render_evidence" in src, \
        "the placeholder guard still claims a filling that does not exist"


def test_live_bundle_backfill_count(tmp_path):
    """covers: M5 — on this repo's own bundle a sync leaves no done Task carrying either scaffold."""
    live = REPO.parent / ".add"
    assert (live / "tasks").is_dir(), "the dogfood bundle is not where the test expects it"
    root = tmp_path / ".add"
    shutil.copytree(live, root, ignore=shutil.ignore_patterns("graph.json", "__pycache__"))
    before = [p for p in (root / "tasks").glob("*.md")
              if "status: done" in p.read_text(encoding="utf-8")
              and (SCAFFOLD_RECEIPT in p.read_text(encoding="utf-8") or SCAFFOLD_LESSON in p.read_text(encoding="utf-8"))]
    assert before, "the live bundle no longer carries the defect this test measures — retire this check"
    ok, note = add.doctor_sync(root)
    assert ok, note
    after = [p for p in before
             if SCAFFOLD_RECEIPT in p.read_text(encoding="utf-8") or SCAFFOLD_LESSON in p.read_text(encoding="utf-8")]
    assert not after, f"{len(after)} done task(s) still carry a scaffold after sync: {[p.name for p in after][:5]}"
