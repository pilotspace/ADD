"""Red direction check for doctor-sees-a-moved-scope."""
import pytest
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
from conftest import draft_direction  # noqa: E402


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_doctor_names_a_scope_moved_after_its_seal_without_repairing_it(tmp_path):
    """covers: M1, M3, R:SCOPE_SILENCE, R:REPAIRAWAY, E1, E2 — doctor reports scope drift and writes nothing."""
    root = tmp_path / ".add"
    add.init(root, "code", "doctor scope")
    cid, _ = add.new(root, "Task", "owner", title="owner", scope=["src/a.py"])
    task = draft_direction(root, cid)
    task.write_text(task.read_text().replace("## PLAN", "## PLAN\nregression: none · fixture", 1), encoding="utf-8")
    assert add.freeze(root, cid, by="plan:T", authority="plan")[0]
    path = root / cid.lstrip("/")
    before = path.read_text(encoding="utf-8")
    node = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(node['raw'], 'scope', ['src/b.py'])}\n---\n{node['body']}")
    moved = path.read_text(encoding="utf-8")

    findings = add.doctor(root)
    matches = [f for f in findings if f["code"] == "scope_moved_after_seal" and f["node"] == cid]
    assert matches, f"R:SCOPE_SILENCE — doctor hid the moved scope: {findings!r}"
    assert path.read_text(encoding="utf-8") == moved and moved != before, "R:REPAIRAWAY — doctor changed the record"


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_doctor_names_legacy_and_malformed_scope_seals(tmp_path):
    """covers: M2, M3, R:LEGACY_SILENCE, R:REPAIRAWAY, E2, E3 — unsealed migration is visible."""
    root = tmp_path / ".add"
    add.init(root, "code", "legacy doctor")
    for slug, suffix in (("legacy", ""), ("malformed", ", scope: nope")):
        cid, _ = add.new(root, "Task", slug, title=slug, scope=[f"src/{slug}.py"])
        path = root / cid.lstrip("/")
        node = add.read(path, "T2")
        stamp = ("verified:\n  - { by: \"human:T\", at: 2026-09-14, act: freeze, "
                 f"authority: human{suffix} }}")
        raw = node["raw"].replace("verified: []", stamp)
        add.write(path, f"---\n{raw}\n---\n{node['body']}")
    before = {p.name: p.read_bytes() for p in (root / "tasks").glob("*.md")}
    findings = add.doctor(root)
    missing = {f["node"]: f for f in findings if f["code"] == "scope_seal_missing"}
    for cid in ("/tasks/legacy.md", "/tasks/malformed.md"):
        assert cid in missing and "add freeze" in missing[cid]["detail"], (
            f"R:LEGACY_SILENCE — doctor hid {cid}: {findings!r}")
    after = {p.name: p.read_bytes() for p in (root / "tasks").glob("*.md")}
    assert after == before, "R:REPAIRAWAY — doctor changed a legacy record"
