"""Red suite for `run-digest-root` — run and gate resolve `scope:` from the SAME root.

Field finding from hardening tally #1 (2026-08-11): `run` computed `scope_digest` relative
to `--cwd` while `gate` hands `fresh()` the bundle parent. Any cwd other than the bundle
parent therefore recorded an EMPTY digest, the receipt honestly degraded to
`freshness: mtime` — silently — and the gate then refused the PASS with a message that
named neither the cwd cause nor the fix. Honest refusal, opaque experience.

Three commitments, each pinned here:
  * the digest root is `root.parent` — identical to the root `gate` resolves — and `--cwd`
    stays what it says: the command's working directory, nothing more (M1);
  * a declared scope whose run records no digest writes WHY into the receipt's `note:` —
    the degrade is on the record, never silent (M2, R:SILENTDEGRADE);
  * `fresh()`'s no-digest refusal names the candidate causes (M3).

Driven as dogfood task `.add/tasks/run-digest-root.md` (v3.0.0 hardening tally #3).
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


@pytest.fixture
def project(tmp_path):
    """A project-shaped tree: git repo at tmp_path, bundle at tmp_path/.add, code in src/."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    bundle = tmp_path / ".add"
    add.init(bundle, "code", "P")
    cid, _ = add.new(bundle, "Task", "scoped", title="Scoped", scope=["src/a.py"])
    return tmp_path, bundle, cid


def test_digest_root_is_the_bundle_parent_not_the_cwd(project):
    """covers: M1,E1 — the tally-#1 reproduction: run from a project SUBDIR."""
    root_dir, bundle, cid = project
    node = add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root_dir / "src")
    assert node["receipt"]["freshness"] == "content", \
        "a cwd below the project silently dropped the digest — run and gate disagree on the root"
    assert [d["path"] for d in node["receipt"]["scope_digest"]] == ["src/a.py"], \
        "digest paths must be bundle-parent-relative, exactly as gate re-resolves them"


def test_missing_scope_paths_degrade_loudly(project):
    """covers: M2, R:SILENTDEGRADE — a scope of ghosts yields mtime AND says why."""
    root_dir, bundle, _ = project
    cid, _ = add.new(bundle, "Task", "ghosted", title="Ghosted", scope=["ghost.py"])
    node = add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root_dir)
    assert node["receipt"]["freshness"] == "mtime"
    note = node["receipt"]["note"]
    assert "digest" in note and "scope" in note, \
        f"the degrade left no trace on the receipt — note was {note!r}"


def test_degrade_note_never_clobbers_a_failure_note(project):
    """covers: M2 — a timeout's note and the degrade note both survive."""
    root_dir, bundle, _ = project
    cid, _ = add.new(bundle, "Task", "slow", title="Slow", scope=["ghost.py"])
    node = add.run(bundle, cid, [sys.executable, "-c", "import time; time.sleep(30)"],
                   cwd=root_dir, timeout=1)
    note = node["receipt"]["note"]
    assert "timeout" in note, f"the degrade note erased the timeout diagnosis: {note!r}"
    assert "digest" in note, f"the timeout note erased the degrade diagnosis: {note!r}"


def test_gate_refusal_names_the_causes(tmp_path):
    """covers: M3,A2 (probe) — the no-digest refusal names both candidate causes."""
    ok, why = add.fresh({"freshness": "mtime", "scope_digest": []}, tmp_path)
    assert not ok
    assert "git" in why and "scope" in why, \
        f"the refusal still explains nothing a reader can act on: {why!r}"


def test_scopeless_nodes_stay_silent(project):
    """covers: M2 — no scope, no note: the doc lane is untouched."""
    root_dir, bundle, _ = project
    cid, _ = add.new(bundle, "Task", "doclane", title="Doc lane")
    node = add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root_dir)
    assert node["receipt"]["note"] == "", \
        "a node with no `scope:` has nothing to degrade — it must draw no note"
