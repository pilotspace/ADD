"""Red suite for `upgrade-working-bundle` — the engine must not archive itself away.

Release-blocker found live in the v3.0.0 updater test (the 2.5 -> 3.0.0 chain): `upgrade`
renames the WHOLE 2.x bundle — including the `.add/tooling/` engine that is executing the
verb — into `.add-2x-archive/`, then inits only the nine starter files. The report's own
`next: add status` then dies on a missing `cli.py`: a guided migration that strands the
user in a bundle with no engine (R:SELFARCHIVE). Beta.2's readiness review verified the
archive was byte-identical; nothing verified the fresh bundle was DRIVABLE.

The fix restores the installer-managed trees (`tooling/`, `personas-teacher/`,
`personas-index/`) by COPY from the archive — the archived engine is by construction the
running 3.0 engine, and the archive must stay the complete record it was promised to be.

Driven as dogfood task `.add/tasks/upgrade-working-bundle.md` (v3.0.0 hardening tally #8).
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


@pytest.fixture
def legacy(tmp_path):
    """A 2.x bundle with the managed trees a real installed project carries."""
    root = tmp_path / ".add"
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# the running engine\n")
    (root / "tooling" / "cli.py").write_text("# the dispatch entry\n")
    (root / "tooling" / "__pycache__").mkdir()
    (root / "tooling" / "__pycache__" / "add.pyc").write_text("noise")
    (root / "personas-teacher" / "eng").mkdir(parents=True)
    (root / "personas-teacher" / "eng" / "backend.md").write_text("---\ndescription: d\n---\n")
    (root / "personas-index").mkdir()
    (root / "personas-index" / "use-when.md").write_text("- `backend`\n")
    (root / "state.json").write_text('{"schema": 3}\n')
    (root / "tasks" / "transfer").mkdir(parents=True)
    (root / "tasks" / "transfer" / "PLAN.md").write_text("# PLAN\n")
    return tmp_path


def test_upgrade_restores_a_runnable_engine(legacy):
    """covers: M1,A1,R:SELFARCHIVE — tooling survives, byte-identical to the archive's."""
    _, note = add.upgrade(legacy, by="human:tindang")
    tooling = legacy / ".add" / "tooling"
    assert (tooling / "cli.py").is_file(), \
        f"the report says `add status` next, but there is no engine to run it: {note!r}"
    archive = legacy / ".add-2x-archive" / "tooling"
    for name in ("add.py", "cli.py"):
        assert (tooling / name).read_bytes() == (archive / name).read_bytes(), \
            f"restored {name} is not the engine that ran the upgrade"
    assert not (tooling / "__pycache__").exists(), "build noise was copied forward"


def test_vendored_trees_are_restored(legacy):
    """covers: M2 — the corpus and its routing index come forward too."""
    add.upgrade(legacy, by="human:tindang")
    assert (legacy / ".add" / "personas-teacher" / "eng" / "backend.md").is_file()
    assert (legacy / ".add" / "personas-index" / "use-when.md").is_file()


def test_archive_stays_complete(legacy):
    """covers: M3 — restoration is copy, never move; the archive keeps every file."""
    before = sorted(p.relative_to(legacy / ".add").as_posix()
                    for p in (legacy / ".add").rglob("*") if p.is_file())
    add.upgrade(legacy, by="human:tindang")
    archive = legacy / ".add-2x-archive"
    after = sorted(p.relative_to(archive).as_posix()
                   for p in archive.rglob("*") if p.is_file() and p.name != "MIGRATION.md")
    assert after == before, "the archive is no longer the complete 2.x bundle"


def test_minimal_bundle_still_upgrades(tmp_path):
    """covers: A4,E1 — no tooling in the old bundle: upgrade succeeds, nothing restored
    FROM THE ARCHIVE. (init vendoring from a live package source, where one exists, is its
    normal behavior and stays untouched — the restore only ever fills from the archive.)"""
    root = tmp_path / ".add"
    root.mkdir()
    (root / "state.json").write_text('{"schema": 3}\n')
    _, note = add.upgrade(tmp_path, by="human:tindang")
    assert (tmp_path / ".add-2x-archive").is_dir(), note
    assert (tmp_path / ".add" / "index.md").is_file(), "the fresh bundle was not initialised"
