"""Red suite for `upgrade` (beta-2, W5) — the guided 2.x → 3.0 clean break.

The manual path was proven on the bench: nothing deleted, 2.x state archived whole, a fresh
3.0 bundle initialised beside it. This verb automates exactly that and nothing more. It is
NO-EXEC and non-destructive by construction — one rename, one init, one report file:

  * a 2.x bundle is recognised by its own bones, any of: the `tooling/add_engine/` package
    (3.0's engine is two flat files), `state.json` (3.0 has no state file — files are the
    database), or directory-tasks (`tasks/<slug>/PLAN.md`; 3.0 tasks are flat `.md` nodes);
  * the whole `.add/` is RENAMED to `.add-2x-archive/` — byte-identical, grep-able, never
    edited — and a fresh 3.0 bundle is initialised at `.add/`;
  * `MIGRATION.md` lands in the ARCHIVE (it describes the old world, and the new bundle's
    doctor should not have to classify it): every 2.x task with its phase marker, plus the
    standing fact that nothing was deleted;
  * refusals, not surprises: no bundle, an already-3.0 bundle, or a pre-existing archive
    each refuse with the fix named.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

PLAN = """# PLAN: Transfer money between my accounts

slug: transfer · created: 2026-08-11 · stage: prototype
milestone: transfers
autonomy: auto
phase: build

## 1 · SPECIFY — the rules
- M1 a transfer moves the amount atomically
"""


@pytest.fixture
def legacy(tmp_path):
    """A minimal but honest 2.x bundle: engine package, state.json, one directory-task."""
    root = tmp_path / ".add"
    (root / "tooling" / "add_engine").mkdir(parents=True)
    (root / "tooling" / "add_engine" / "__init__.py").write_text("# 2.x engine package\n")
    (root / "state.json").write_text('{"schema": 3}\n')
    (root / "tasks" / "transfer").mkdir(parents=True)
    (root / "tasks" / "transfer" / "PLAN.md").write_text(PLAN)
    (root / "PROJECT.md").write_text("# Ledger\n\nThe 2.x project charter.\n")
    return tmp_path


def test_upgrade_archives_whole_and_inits_30(legacy):
    """covers: M1 — the clean break: old world renamed intact, new world initialised."""
    report, note = add.upgrade(legacy, by="human:tindang")
    archive = legacy / ".add-2x-archive"
    assert archive.is_dir(), note
    assert (archive / "tasks" / "transfer" / "PLAN.md").read_text() == PLAN, \
        "the archived task drifted — the archive must be byte-identical"
    assert (legacy / ".add" / "index.md").is_file(), "no 3.0 bundle was initialised"
    assert not (legacy / ".add" / "state.json").exists(), "2.x state leaked into the 3.0 bundle"


def test_upgrade_writes_the_migration_report_in_the_archive(legacy):
    """covers: M2 — the report describes the OLD world and lives with it."""
    report, note = add.upgrade(legacy, by="human:tindang")
    assert report is not None and report.is_file(), note
    assert report.parent == legacy / ".add-2x-archive"
    text = report.read_text()
    assert "transfer" in text, "the report must list every 2.x task"
    assert "build" in text, "the report must carry each task's phase marker"
    assert "deleted" in text.lower(), "the report must state the nothing-deleted fact"
    assert "add new Task" in text, "the report must name the re-author verb"


def test_upgrade_carries_the_2x_title_forward(legacy):
    """covers: M3 — the new Project node is named after the old charter, not a stub."""
    add.upgrade(legacy, by="human:tindang")
    project = (legacy / ".add" / "PROJECT.md")
    assert project.is_file()
    assert "Ledger" in project.read_text(), "the 2.x PROJECT.md title was dropped"


def test_upgrade_refuses_when_there_is_nothing_to_upgrade(tmp_path):
    """covers: E1 — no bundle, no upgrade, and the note says what to do instead."""
    report, note = add.upgrade(tmp_path, by="human:tindang")
    assert report is None
    assert "add init" in note, note


def test_upgrade_refuses_an_already_30_bundle(tmp_path):
    """covers: E2 — upgrading 3.0 would archive a live bundle; refuse and say so."""
    add.init(tmp_path / ".add", "code", "Fresh")
    report, note = add.upgrade(tmp_path, by="human:tindang")
    assert report is None
    assert "already" in note.lower(), note
    assert (tmp_path / ".add" / "index.md").is_file(), "the refusal must not have moved anything"


def test_upgrade_refuses_a_second_run(legacy):
    """covers: E3 — an existing archive is a previous upgrade's record; never clobber it."""
    add.upgrade(legacy, by="human:tindang")
    # A second 2.x bundle appearing at .add/ would collide with the archive.
    import shutil
    shutil.rmtree(legacy / ".add")
    (legacy / ".add" / "tooling" / "add_engine").mkdir(parents=True)
    (legacy / ".add" / "state.json").write_text("{}\n")
    report, note = add.upgrade(legacy, by="human:tindang")
    assert report is None
    assert ".add-2x-archive" in note, note


def test_cli_upgrade_dispatches(legacy):
    """covers: M4 — the verb an agent actually types."""
    import cli
    rc = cli.main(["--root", str(legacy / ".add"), "upgrade"])
    assert rc == 0
    assert (legacy / ".add-2x-archive").is_dir()
    assert (legacy / ".add" / "index.md").is_file()
