"""`replan` — a recorded steering amendment on a frozen task (task replan-verb, dynamic-flow).

One additive act stamp carrying the note; refusals for the unfrozen, the noteless, and the
closed; the seal untouched — body byte-identical, direction sha unchanged, gate indifferent.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402
import argparse  # noqa: E402
import cli  # noqa: E402
from conftest import draft_direction, git  # noqa: E402


def _frozen(tmp_path, slug="steered"):
    root = tmp_path / ".add"
    if not root.exists():
        add.init(root, "code", "T")
    cid, _ = add.new(root, "Task", slug, title="steered", depth="standard", scope=["src/service.py"])
    draft_direction(root, cid)
    ok, note = add.freeze(root, cid, by="human:t", authority="human")
    assert ok, note
    return root, cid


def _fm_raw(root, cid):
    m = re.match(r"\A---\n(.*?)\n---\n", (root / cid.lstrip("/")).read_text(encoding="utf-8"),
                 re.DOTALL)
    return m.group(1) if m else ""


def test_replan_stamps_note_on_frozen_task(tmp_path):
    """covers: M1, A9 — one appended stamp, act replan, process authority, the note carried."""
    root, cid = _frozen(tmp_path)
    ok, note = add.replan(root, cid, note="pivoting to the sorted-merge approach", by="builder")
    assert ok, note
    raw = _fm_raw(root, cid)
    assert re.search(r"act: replan", raw), raw
    assert "sorted-merge" in raw, "the note is not on the trail"
    assert raw.count("act: replan") == 1


def test_replan_refuses_unfrozen(tmp_path):
    """covers: M2, R:SILENT_STEER, A8 — nothing is being steered before the freeze."""
    root = tmp_path / ".add"
    add.init(root, "code", "T")
    cid, _ = add.new(root, "Task", "loose", title="loose", scope=["a.py"])
    ok, note = add.replan(root, cid, note="a note", by="builder")
    assert not ok and "freeze" in note.lower(), note
    assert "act: replan" not in _fm_raw(root, cid)


def test_replan_refuses_empty_note(tmp_path):
    """covers: M2, R:SILENT_STEER, A7 — steering that says nothing records nothing."""
    root, cid = _frozen(tmp_path)
    for empty in ("", "   "):
        ok, note = add.replan(root, cid, note=empty, by="builder")
        assert not ok and "note" in note.lower(), note
    assert "act: replan" not in _fm_raw(root, cid)


def test_replan_refuses_closed_task(tmp_path):
    """covers: E1 — the trail of a done task is closed; the note belongs in LESSONS."""
    root, cid = _frozen(tmp_path)
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")
    ok, note = add.replan(root, cid, note="too late", by="builder")
    assert not ok, note
    assert "act: replan" not in _fm_raw(root, cid)


def test_replan_leaves_seal_and_body_untouched(tmp_path):
    """covers: M3, R:SEAL_TOUCH — additive on the trail, invisible to the body and the seal."""
    root, cid = _frozen(tmp_path)
    path = root / cid.lstrip("/")
    body_before = add.read(path, "T2")["body"]
    sha_before = re.search(r'direction: "sha256:([0-9a-f]+)"', _fm_raw(root, cid)).group(1)
    ok, note = add.replan(root, cid, note="steering note", by="builder")
    assert ok, note
    assert add.read(path, "T2")["body"] == body_before, "the body moved"
    raw = _fm_raw(root, cid)
    assert re.search(rf'direction: "sha256:{sha_before}"', raw), "the freeze seal moved"


def test_replan_multiline_note_stays_single_line(tmp_path):
    """Review fix (PR #197) — a newline in --note must not split the stamp across frontmatter
    lines: the node would become unparseable, taking its freeze and gate history with it."""
    root, cid = _frozen(tmp_path)
    ok, note = add.replan(root, cid, note="pivot to plan B\nkeep the old index", by="builder")
    assert ok, note
    raw = _fm_raw(root, cid)
    stamps = [l for l in raw.splitlines() if "act: replan" in l]
    assert len(stamps) == 1 and "keep the old index" in stamps[0], raw
    fm = add.scan(root)[cid]["fm"]
    assert any(isinstance(s, dict) and s.get("act") == "replan"
               for s in fm["verified"]), "the trail no longer parses"


def test_gate_unaffected_by_replans(tmp_path):
    """covers: M3, A6 — freeze → brief → replan ×2 → run → gate PASS, exactly as with zero."""
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("def f():\n    return True\n")
    root, cid = _frozen(tmp_path)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    add.brief_stamp(root, cid)
    for i in (1, 2):
        ok, note = add.replan(root, cid, note=f"steer {i}", by="builder")
        assert ok, note
    xml = tmp_path / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>'
                    for i in ("test_atomic_admit", "test_no_overadmit"))
    xml.write_text(f"<testsuites><testsuite>{cases}</testsuite></testsuites>")
    add.run(root, cid, [sys.executable, "-c", "pass"], cwd=tmp_path, junit=xml)
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert ok is True, note


def test_replan_is_dispatched():
    """covers: S1, E3 — the cli owns the verb; a stamp nobody can invoke is dead code."""
    sub = [a for a in cli.build_parser()._actions
           if isinstance(a, argparse._SubParsersAction)][0]
    assert "replan" in sub.choices, sorted(sub.choices)
