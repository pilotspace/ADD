"""The explore floors, engine-enforced (task sources-receipt, dynamic-flow).

Freeze refuses a budgetless explore; gate PASS on a kind-explore task binds every Must to an
evidence-carrying FINDINGS line and refuses naming the open questions; a passing findings-only
explore records evidence kind `sources` with the closed tally. Non-explore tasks byte-identical.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402
from conftest import draft_direction  # noqa: E402


def _set_section(root, cid, heading, text):
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    lines = n["body"].splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == f"## {heading}")
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
                   len(lines))
        body = "\n".join(lines[:start + 1] + [text] + lines[end:])
    except StopIteration:
        body = n["body"].rstrip() + f"\n\n## {heading}\n{text}\n"
    add.write(path, f"---\n{n['raw']}\n---\n{body}")


def _explore(tmp_path, *, budget=True, slug="probe"):
    root = tmp_path / ".add"
    if not root.exists():
        add.init(root, "code", "T")
    cid, _ = add.new(root, "Task", slug, title="an explore", depth="standard",
                     kind="explore", scope=["notes.md"])
    draft_direction(root, cid)
    if budget:
        _set_section(root, cid, "PLAN", "contract: answers\nbudget: ~20 tool calls\nscope: notes.md")
    return root, cid


def _freeze(root, cid):
    return add.freeze(root, cid, by="human:t", authority="human")


def test_freeze_refuses_explore_without_budget(tmp_path):
    """covers: M1, R:UNBOUNDED, A8 — no budget line, no freeze; the refusal names it."""
    root, cid = _explore(tmp_path, budget=False)
    ok, note = _freeze(root, cid)
    assert not ok and "budget" in note.lower(), note


def test_freeze_accepts_explore_with_budget(tmp_path):
    """covers: M1, A4 — any authored budget text unlocks the normal freeze."""
    root, cid = _explore(tmp_path, budget=True)
    ok, note = _freeze(root, cid)
    assert ok, note


def test_gate_refuses_open_questions_naming_them(tmp_path):
    """covers: M2, R:HOLLOW_EXPLORE, A12 — an unanswered Must holds the PASS by name."""
    root, cid = _explore(tmp_path)
    ok, note = _freeze(root, cid)
    assert ok, note
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert not ok, "a PASS with zero findings must refuse"
    assert "M1" in note and re.search(r"open", note, re.I), note


def test_gate_requires_evidence_ref_per_finding(tmp_path):
    """covers: M2, R:HOLLOW_EXPLORE, A5 — found without evidence does not close a question."""
    root, cid = _explore(tmp_path)
    _freeze(root, cid)
    _set_section(root, cid, "FINDINGS", "- F1 (answers M1) · the admit path is atomic in impl")
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert not ok and "M1" in note, note


def test_gate_pass_records_sources_kind_and_tally(tmp_path):
    """covers: M3, A6 — a fully-answered explore passes: kind sources, tally on the stamp."""
    root, cid = _explore(tmp_path)
    _freeze(root, cid)
    _set_section(root, cid, "FINDINGS",
                 "- F1 (answers M1) · the admit path is atomic · (evidence: src/svc.py:42)")
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert ok is True, note
    raw = (root / cid.lstrip("/")).read_text(encoding="utf-8")
    stamp = [l for l in raw.splitlines() if "act: gate" in l][-1]
    assert "sources" in stamp, stamp
    assert "1/1" in stamp, stamp
    assert add.scan(root)[cid]["fm"]["status"] == "done"


def test_extra_findings_are_ignored(tmp_path):
    """covers: E1 — an F line answering an unfrozen question neither binds nor blocks."""
    root, cid = _explore(tmp_path)
    _freeze(root, cid)
    _set_section(root, cid, "FINDINGS",
                 "- F1 (answers M1) · the admit path is atomic · (evidence: src/svc.py:42)\n"
                 "- F2 (answers M9) · a stray answer · (evidence: nowhere)")
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert ok is True, note


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def test_explore_with_run_receipt_still_gates(tmp_path):
    """covers: E3 — a recorded run receipt keeps the normal receipt path in charge."""
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "notes.md").write_text("notes\n")
    root, cid = _explore(tmp_path)
    ok, note = _freeze(root, cid)
    assert ok, note
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    add.brief_stamp(root, cid)
    xml = tmp_path / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>'
                    for i in ("test_atomic_admit", "test_no_overadmit"))
    xml.write_text(f"<testsuites><testsuite>{cases}</testsuite></testsuites>")
    add.run(root, cid, [sys.executable, "-c", "pass"], cwd=tmp_path, junit=xml)
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert ok is True, note


def test_non_explore_freeze_and_gate_unchanged(tmp_path):
    """covers: M4, R:REGRESS, A11 — a normal task is untouched, budget line or not."""
    root = tmp_path / ".add"
    add.init(root, "code", "T")
    cid, _ = add.new(root, "Task", "plain", title="plain", depth="standard", scope=["a.py"])
    draft_direction(root, cid)
    ok, note = add.freeze(root, cid, by="human:t", authority="human")
    assert ok, note  # no budget line demanded
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert not ok and "receipt" in note.lower(), note  # still the receipt path, verbatim
