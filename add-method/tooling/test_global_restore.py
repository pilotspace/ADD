#!/usr/bin/env python3
"""Tests for global-data-restore (installer-polish · global-data-restore).

FROZEN @ v1: the NON-DESTRUCTIVE inverse of the one-way snapshot.
  - `init --from-global-data` runs the managed-layer install AND restores user-data
    from <home>/data/<key> into <target>/.add via install(as_global_data_restore=True).
    Fill-gaps by default (write only ABSENT entries); `--force` overwrites a present
    entry, writing a `<name>.bak` first. Copies only _is_user_data entries; derefs
    symlinks to content. Consume-only: no persist-back, no auto-register. A missing
    snapshot (home present) is an honest skip (exit 0); a missing home is no_global_home.
  - `prune-data` removes orphaned snapshots — a <home>/data/<key> whose key is owned by
    NO LIVE registry entry (unregistered OR registered-but-vanished-on-disk; both
    reclaimed — DIVERGES from `update --global`'s keep-vanished). Dry-run by default
    (lists, removes nothing); `--force` deletes. Corrupt registry = LOUD fail, no removal.

Fully hermetic: home + skill base resolve from the injected `env` (reusing global-install's
hook), so tests touch a tmp home/HOME — never the real ~/.add or ~/.claude. Snapshots are
written directly for precise content control; a valid (stamped) home is made via a real
`--global` install of a throwaway project. npm parity is structural (ParityRestoreTest).

This suite is RED until _restore_data / _prune_data / prune_data / install(as_global_data_restore)
exist — red for the right reason (missing implementation).

Run: python3 -m unittest test_global_restore -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from add_method import _installer            # noqa: E402

CLI_JS = _ADD_METHOD / "bin" / "cli.js"


def _make_bundled(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro\n")
    return root


class _Base(unittest.TestCase):
    def setUp(self):
        # .resolve() up front (matching test_global_update_harden.py's own _Base convention):
        # _restore_data resolves project_abspath internally, but _persist_data does NOT -- its
        # only production caller (install(), which resolves target_path at its own top) always
        # hands it an already-resolved path. A direct unit-level _persist_data(self.home,
        # str(self.proj)) call needs that SAME precondition, or its data_key(...) diverges from
        # _snap_dir()'s (which resolves) on any platform where the tmp dir is itself a symlink
        # (e.g. macOS /var -> /private/var).
        self.tmp = Path(tempfile.mkdtemp(prefix="grestore-")).resolve()
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.home = self.tmp / "home"
        self.userhome = self.tmp / "user"; self.userhome.mkdir()
        self.proj = self.tmp / "proj"; self.proj.mkdir()
        self.other = self.tmp / "other"; self.other.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self):
        return {"ADD_HOME": str(self.home), "HOME": str(self.userhome)}

    def _install(self, target, **kw):
        return _installer.install(target=str(target), bundled=str(self.bundled),
                                  non_interactive=True, env=self._env(), **kw)

    def _valid_home(self):
        """Stamp the home with a real --global install of a throwaway project."""
        self.assertEqual(self._install(self.other, as_global=True), 0,
                         "setup: --global install should stamp the home")

    def _snap_dir(self, proj: Path) -> Path:
        return self.home / "data" / _installer.data_key(str(proj.resolve()))

    def _write_snapshot(self, proj: Path, files: dict) -> Path:
        """Author a snapshot under <home>/data/<key(proj)> with the given {name: content|dict}."""
        snap = self._snap_dir(proj)
        snap.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            target = snap / name
            if isinstance(content, dict):                 # a directory subtree
                target.mkdir(parents=True, exist_ok=True)
                for cn, cc in content.items():
                    (target / cn).write_text(cc)
            else:
                target.write_text(content)
        return snap

    def _seed_add_dir(self, proj: Path, files: dict) -> Path:
        """Author <proj>/.add/ with the given {name: content|dict} -- the PERSIST source side
        (the mirror of _write_snapshot, which authors the RESTORE source side)."""
        add = proj / ".add"
        add.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            target = add / name
            if isinstance(content, dict):
                target.mkdir(parents=True, exist_ok=True)
                for cn, cc in content.items():
                    (target / cn).write_text(cc)
            else:
                target.write_text(content)
        return add

    def _read(self, p: Path) -> str:
        return p.read_text()


# --- persist (crash-safe-persist-restore v1: whole-tree stage-then-commit) -------------------

class PersistStageCommitTest(_Base):
    """_persist_data: whole-tree stage-then-commit (self-heal -> stage -> commit-by-rename ->
    sweep), mirroring _clean_replace's own pattern. Unit-level (direct _persist_data calls),
    matching RestoreUnitTest's own style."""

    def test_persist_fresh_snapshot_stage_then_commit(self):             # M1, M2, M12
        self._seed_add_dir(self.proj, {
            "PROJECT.md": "# project\n", "state.json": "{}", "tasks": {"demo.md": "# a task\n"},
        })
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        self.assertEqual((snap / "PROJECT.md").read_text(), "# project\n")
        self.assertEqual((snap / "state.json").read_text(), "{}")
        self.assertTrue((snap / "tasks" / "demo.md").exists())
        leftovers = [p.name for p in snap.parent.iterdir() if p.name != snap.name]
        self.assertEqual(leftovers, [], "no staging or backup scratch sibling remains next to the snapshot")

    def test_persist_refresh_never_wiped_in_place(self):                 # M1, M2, M12
        self._seed_add_dir(self.proj, {"PROJECT.md": "old", "UNCHANGED.md": "same"})
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        real_rmtree = shutil.rmtree
        wiped_live_dest = {"flag": False}

        def spying_rmtree(path, *a, **kw):
            if Path(path) == snap:
                wiped_live_dest["flag"] = True
            return real_rmtree(path, *a, **kw)

        (self.proj / ".add" / "PROJECT.md").write_text("new")
        with mock.patch.object(_installer.shutil, "rmtree", side_effect=spying_rmtree):
            self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        self.assertFalse(wiped_live_dest["flag"], "home/data/<key> itself must never be rmtree'd in place")
        self.assertEqual((snap / "PROJECT.md").read_text(), "new")
        self.assertEqual((snap / "UNCHANGED.md").read_text(), "same",
                          "an unchanged file is never observed missing mid-refresh")
        leftovers = [p.name for p in snap.parent.iterdir() if p.name != snap.name]
        self.assertEqual(leftovers, [], "no staging or backup scratch sibling remains afterward")

    def test_persist_zero_entries_leaves_existing_snapshot_untouched(self):   # M5
        self._seed_add_dir(self.proj, {"PROJECT.md": "keep me"})
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        before_mtime = snap.stat().st_mtime
        before_content = (snap / "PROJECT.md").read_text()
        (self.proj / ".add" / "PROJECT.md").unlink()             # now .add/ has zero qualifying entries
        self.assertFalse(_installer._persist_data(self.home, str(self.proj)),
                          "zero entries to persist returns False")
        self.assertEqual((snap / "PROJECT.md").read_text(), before_content, "the existing snapshot is byte-unchanged")
        self.assertEqual(snap.stat().st_mtime, before_mtime, "home/data/<key> is not touched AT ALL")

    def test_persist_mid_stage_failure_leaves_snapshot_untouched(self):   # M4, Reject persist_stage_failure_untouched
        self._seed_add_dir(self.proj, {"PROJECT.md": "before"})
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        before = (snap / "PROJECT.md").read_text()
        (self.proj / ".add" / "PROJECT.md").write_text("attempted-update")

        with mock.patch.object(_installer.shutil, "copyfile", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                _installer._persist_data(self.home, str(self.proj))

        self.assertEqual((snap / "PROJECT.md").read_text(), before, "home/data/<key> still holds its exact prior content")
        leftovers = [p.name for p in snap.parent.iterdir() if p.name != snap.name]
        self.assertEqual(leftovers, [], "no partial staging directory survives the call")

    def test_persist_commit_aside_failure_leaves_snapshot_unchanged(self):   # M4, Reject persist_commit_aside_failure_unchanged
        self._seed_add_dir(self.proj, {"PROJECT.md": "before"})
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        before = (snap / "PROJECT.md").read_text()
        (self.proj / ".add" / "PROJECT.md").write_text("attempted-update")

        with mock.patch.object(_installer.os, "replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                _installer._persist_data(self.home, str(self.proj))

        self.assertEqual((snap / "PROJECT.md").read_text(), before, "home/data/<key> is unchanged (the rename never happened)")
        leftovers = [p.name for p in snap.parent.iterdir() if p.name != snap.name]
        self.assertEqual(leftovers, [], "the staged directory is removed before the error propagates")

    def test_persist_commit_land_failure_rolls_back(self):   # M4, Reject persist_commit_land_failure_rolls_back
        self._seed_add_dir(self.proj, {"PROJECT.md": "before"})
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        before = (snap / "PROJECT.md").read_text()
        (self.proj / ".add" / "PROJECT.md").write_text("attempted-update")

        real_replace = os.replace
        call_count = {"n": 0}

        def flaky_replace(src, dst, *a, **kw):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise OSError("boom")
            return real_replace(src, dst, *a, **kw)

        with mock.patch.object(_installer.os, "replace", side_effect=flaky_replace):
            with self.assertRaises(OSError):
                _installer._persist_data(self.home, str(self.proj))

        self.assertEqual((snap / "PROJECT.md").read_text(), before,
                          "home/data/<key> is restored to hold its exact original content")
        leftovers = [p.name for p in snap.parent.iterdir() if p.name != snap.name]
        self.assertEqual(leftovers, [], "no staging or backup scratch sibling survives the call")

    def test_persist_stale_backup_self_heals_next_call(self):   # M3, Reject persist_stale_backup_self_heals_next_call
        self._seed_add_dir(self.proj, {"PROJECT.md": "known-good"})
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        key = _installer.data_key(str(self.proj))
        # simulate a crash BETWEEN the two commit renames of a prior call: the live dir sits
        # renamed-aside at a backup sibling, and nothing occupies dest's path.
        backup = snap.parent / f"{key}.add-bak-deadbeef01"
        snap.rename(backup)
        self.assertFalse(snap.exists())

        (self.proj / ".add" / "PROJECT.md").write_text("fresh-content")
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))

        self.assertEqual((snap / "PROJECT.md").read_text(), "fresh-content",
                          "self-heal restores the backup first, then this call updates to fresh content")
        leftovers = [p.name for p in snap.parent.iterdir() if p.name != snap.name]
        self.assertEqual(leftovers, [], "no backup scratch sibling survives the call")

    def test_persist_stale_staging_swept_before_new_staging(self):   # M3
        self._seed_add_dir(self.proj, {"PROJECT.md": "current"})
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        key = _installer.data_key(str(self.proj))
        stale = snap.parent / f"{key}.add-tmp-leftover01"
        stale.mkdir()
        (stale / "half-copied.txt").write_text("garbage")

        (self.proj / ".add" / "PROJECT.md").write_text("newer")
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))

        self.assertFalse(stale.exists(), "the stale staging leftover is gone after the call")
        self.assertEqual((snap / "PROJECT.md").read_text(), "newer")
        leftovers = [p.name for p in snap.parent.iterdir() if p.name != snap.name]
        self.assertEqual(leftovers, [], "only the fresh snapshot remains")

    def test_persist_two_interleaved_calls_land_one_full_valid_snapshot(self):   # Reject: concurrent runs (out of scope)
        """Two logical callers race on the SAME target with no lock -- a disclosed, deliberate
        non-goal (TASK.md Reject: two lock-less callers get no arbitration guarantee). This
        deterministically interleaves a second, COMPLETE _persist_data call inside the first's
        staging window (a copyfile hook). Self-heal is unaware a sibling call is still
        in-flight and may sweep its live staging dir -- an accepted consequence of the
        disclosed non-goal (the interleaved OUTER call may itself raise), NOT a promise this
        task makes. What DOES hold, and is asserted here: whichever content survives is ONE
        caller's FULL content, never a partial mix, and no scratch sibling is left dangling."""
        self._seed_add_dir(self.proj, {"PROJECT.md": "first"})
        snap = self._snap_dir(self.proj)
        add_dir = self.proj / ".add"
        real_copyfile = shutil.copyfile
        interleaved = {"ran": False}

        def racing_copyfile(src, dst, *a, **kw):
            result = real_copyfile(src, dst, *a, **kw)
            if not interleaved["ran"]:
                interleaved["ran"] = True
                (add_dir / "PROJECT.md").write_text("second")
                self.assertTrue(_installer._persist_data(self.home, str(self.proj)),
                                 "setup: the interleaved caller must land its own full snapshot")
            return result

        with mock.patch.object(_installer.shutil, "copyfile", side_effect=racing_copyfile):
            try:
                _installer._persist_data(self.home, str(self.proj))
            except OSError:
                pass   # an interleaved caller may lose to a sibling's self-heal -- disclosed, not promised

        self.assertTrue(interleaved["ran"], "setup: the interleave hook must have fired")
        content = (snap / "PROJECT.md").read_text()
        self.assertIn(content, ("first", "second"), "the final snapshot is ONE caller's full content, not a mix")
        leftovers = [p.name for p in snap.parent.iterdir() if p.name != snap.name]
        self.assertEqual(leftovers, [], "no scratch sibling (staging or backup) survives once both calls finish")


# --- restore (via install env=) ---------------------------------------------

class RestoreTest(_Base):
    def test_restore_rehydrates_fresh_clone(self):                       # Must 1
        self._valid_home()
        self._write_snapshot(self.proj, {
            "PROJECT.md": "# project\n",
            "state.json": json.dumps({"stage": "mvp"}) + "\n",
            "tasks": {"demo.md": "# a task\n"},
        })
        code = self._install(self.proj, as_global_data_restore=True)
        self.assertEqual(code, 0)
        add = self.proj / ".add"
        self.assertEqual(self._read(add / "PROJECT.md"), "# project\n", "PROJECT.md rehydrated byte-identical")
        self.assertEqual(json.loads((add / "state.json").read_text())["stage"], "mvp")
        self.assertTrue((add / "tasks" / "demo.md").exists(), "tasks/ rehydrated")
        self.assertTrue((add / "tooling" / "add.py").exists(), "managed layer installed")

    def test_fill_gaps_never_clobbers_present(self):                     # Must 2
        self._valid_home()
        self._write_snapshot(self.proj, {"PROJECT.md": "HOME", "SOUL.md": "SOULHOME"})
        add = self.proj / ".add"; add.mkdir(exist_ok=True)
        (add / "PROJECT.md").write_text("LOCAL")                          # present locally
        code = self._install(self.proj, as_global_data_restore=True)
        self.assertEqual(code, 0)
        self.assertEqual(self._read(add / "SOUL.md"), "SOULHOME", "absent entry is filled")
        self.assertEqual(self._read(add / "PROJECT.md"), "LOCAL", "present entry is NOT clobbered")
        self.assertFalse((add / "PROJECT.md.bak").exists(), "fill-gaps writes no .bak")

    def test_force_overwrites_with_bak(self):                            # Must 3
        self._valid_home()
        self._write_snapshot(self.proj, {"PROJECT.md": "HOME"})
        add = self.proj / ".add"; add.mkdir(exist_ok=True)
        (add / "PROJECT.md").write_text("LOCAL")
        code = self._install(self.proj, as_global_data_restore=True, force=True)
        self.assertEqual(code, 0)
        self.assertEqual(self._read(add / "PROJECT.md"), "HOME", "--force overwrites the present entry")
        self.assertEqual(self._read(add / "PROJECT.md.bak"), "LOCAL", "the replaced original is backed up first")

    def test_restore_consumes_only(self):                               # Must 6
        self._valid_home()                                              # registry = [other], NOT proj
        snap = self._write_snapshot(self.proj, {"PROJECT.md": "HOME"})
        before = (snap / "PROJECT.md").read_text()
        code = self._install(self.proj, as_global_data_restore=True)
        self.assertEqual(code, 0)
        reg = json.loads((self.home / "registry.json").read_text())
        self.assertNotIn(str(self.proj.resolve()), reg, "restore does NOT auto-register the project")
        self.assertEqual((snap / "PROJECT.md").read_text(), before, "snapshot is byte-unchanged (no persist-back)")

    def test_no_snapshot_is_soft_skip(self):                            # After: honest skip, not reject
        self._valid_home()                                             # home exists, NO snapshot for proj
        code = self._install(self.proj, as_global_data_restore=True)
        self.assertEqual(code, 0, "home present but no per-project snapshot is an honest skip (exit 0)")
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(), "managed layer still installed")

    def test_no_global_home_rejects(self):                             # Reject: no_global_home
        # no install has stamped the home -> ADD_HOME resolves to a non-existent dir
        code = self._install(self.proj, as_global_data_restore=True)
        self.assertNotEqual(code, 0, "restore from a home that isn't there must fail (no_global_home)")
        self.assertFalse((self.proj / ".add" / "PROJECT.md").exists(), "nothing restored on no_global_home")


# --- restore (unit _restore_data: filter · symlink · fail-closed) -----------

class RestoreUnitTest(_Base):
    def test_filter_excludes_managed(self):                            # Must 4
        self._write_snapshot(self.proj, {"PROJECT.md": "ok", "tooling": {"add.py": "x"}})
        (self.proj / ".add").mkdir(exist_ok=True)
        restored = _installer._restore_data(self.home, str(self.proj))
        self.assertTrue(restored)
        add = self.proj / ".add"
        self.assertTrue((add / "PROJECT.md").exists(), "user-data restored")
        self.assertFalse((add / "tooling").exists(), "a managed-layer name is filtered out of restore")

    @unittest.skipUnless(hasattr(os, "symlink"), "no symlink support on this platform")
    def test_symlinks_dereferenced(self):                              # Must 5
        snap = self._write_snapshot(self.proj, {"note.md": "NOTE"})
        try:
            os.symlink(snap / "note.md", snap / "link.md")
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        (self.proj / ".add").mkdir(exist_ok=True)
        _installer._restore_data(self.home, str(self.proj))
        link = self.proj / ".add" / "link.md"
        self.assertTrue(link.exists())
        self.assertFalse(link.is_symlink(), "a snapshot symlink lands as a regular file")
        self.assertEqual(link.read_text(), "NOTE", "the dereferenced content is restored")

    def test_nothing_to_restore_returns_false(self):                   # honest skip at the unit
        # home exists but no snapshot dir for this project
        self.home.mkdir(parents=True, exist_ok=True)
        self.assertFalse(_installer._restore_data(self.home, str(self.proj)),
                         "no snapshot dir -> nothing restored (False), not an error")

    def test_unwritable_dest_raises(self):                             # Reject: restore_failed (unit)
        self._write_snapshot(self.proj, {"PROJECT.md": "HOME"})
        (self.proj / ".add").write_text("i am a file, not a dir")      # dest cannot hold entries
        with self.assertRaises(OSError):
            _installer._restore_data(self.home, str(self.proj))

    def test_restore_force_directory_entry_backed_up_and_replaced(self):   # Must 14 (M6, M8)
        self._write_snapshot(self.proj, {"tasks": {"new.md": "NEW"}})
        add = self.proj / ".add"; add.mkdir(exist_ok=True)
        (add / "tasks").mkdir()
        (add / "tasks" / "old.md").write_text("OLD")
        restored = _installer._restore_data(self.home, str(self.proj), force=True)
        self.assertTrue(restored)
        self.assertTrue((add / "tasks" / "new.md").exists(), "tasks/ now holds exactly the snapshot's content")
        self.assertFalse((add / "tasks" / "old.md").exists(), "the old local content is gone from tasks/")
        self.assertEqual((add / "tasks.bak" / "old.md").read_text(), "OLD",
                          "tasks.bak/ holds exactly the original local content, byte-for-byte")
        self.assertFalse((add / "tasks.bak" / "new.md").exists())

    def test_restore_mid_stage_failure_earlier_committed_entries_survive(self):   # Must 9 (restore_entry_stage_failure_untouched)
        self._write_snapshot(self.proj, {"A.md": "A-content", "B.md": "B-content"})
        add = self.proj / ".add"; add.mkdir(exist_ok=True)
        real_copyfile = shutil.copyfile

        def failing_on_b(src, dst, *a, **kw):
            if Path(src).name == "B.md":
                # simulate a crash PARTWAY through the write (not a clean pre-write failure) --
                # whatever path the caller is ACTUALLY writing to (dest directly, pre-hardening,
                # or an isolated staged sibling, post-hardening) gets the partial bytes, so this
                # discriminates "wrote straight onto B's final name" from "staged first".
                Path(dst).write_text("PARTIAL-GARBAGE")
                raise OSError("boom")
            return real_copyfile(src, dst, *a, **kw)

        with mock.patch.object(_installer.shutil, "copyfile", side_effect=failing_on_b):
            with self.assertRaises(OSError):
                _installer._restore_data(self.home, str(self.proj))

        self.assertEqual((add / "A.md").read_text(), "A-content", "entry A is present (already committed, stays committed)")
        self.assertFalse((add / "B.md").exists(), "entry B's final name was never opened for writing -- absent, not corrupted")
        leftovers = [p.name for p in add.iterdir() if p.name != "A.md"]
        self.assertEqual(leftovers, [], "B's partial staging sibling was removed, nothing landed at B's final name")

    def test_restore_commit_land_failure_on_force_entry_rolls_back_bak(self):   # Must 9 (restore_entry_commit_land_failure_rolls_back)
        self._write_snapshot(self.proj, {"PROJECT.md": "HOME"})
        add = self.proj / ".add"; add.mkdir(exist_ok=True)
        (add / "PROJECT.md").write_text("LOCAL")

        real_replace = os.replace
        call_count = {"n": 0}

        def flaky_replace(src, dst, *a, **kw):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise OSError("boom")
            return real_replace(src, dst, *a, **kw)

        with mock.patch.object(_installer.os, "replace", side_effect=flaky_replace):
            with self.assertRaises(OSError):
                _installer._restore_data(self.home, str(self.proj), force=True)

        self.assertEqual((add / "PROJECT.md").read_text(), "LOCAL",
                          "PROJECT.md is restored to hold its exact original content (bak renamed back)")
        self.assertFalse((add / "PROJECT.md.bak").exists(), "the .bak was consumed by the rollback, not left sitting")
        self.assertEqual(list(add.glob("PROJECT.md.add-tmp-*")), [], "no staging sibling of PROJECT.md survives the call")

    def test_restore_stale_per_entry_staging_swept_next_call_rederives(self):   # Must 10 (restore_entry_stale_stage_swept_next_call)
        self._write_snapshot(self.proj, {"PROJECT.md": "snapshot-content"})
        add = self.proj / ".add"; add.mkdir(exist_ok=True)
        stale = add / "PROJECT.md.add-tmp-leftover01"
        stale.write_text("half-copied-garbage")     # a stale FILE-shaped leftover; PROJECT.md itself absent

        restored = _installer._restore_data(self.home, str(self.proj))

        self.assertTrue(restored)
        self.assertFalse(stale.exists(), "the stale staging leftover is gone after the call")
        self.assertEqual((add / "PROJECT.md").read_text(), "snapshot-content",
                          "PROJECT.md ends up holding exactly the snapshot's content via ordinary fill-gaps")

    def test_restore_fresh_force_replaces_stale_bak_never_merges(self):   # edge case, ties M8
        self._write_snapshot(self.proj, {"PROJECT.md": "fresh-snapshot"})
        add = self.proj / ".add"; add.mkdir(exist_ok=True)
        (add / "PROJECT.md").write_text("current-local")
        (add / "PROJECT.md.bak").write_text("stale-old-bak")     # left over from an earlier force-restore

        restored = _installer._restore_data(self.home, str(self.proj), force=True)

        self.assertTrue(restored)
        self.assertEqual((add / "PROJECT.md").read_text(), "fresh-snapshot")
        self.assertEqual((add / "PROJECT.md.bak").read_text(), "current-local",
                          "the stale .bak is REPLACED by a fresh backup of the CURRENT content, not merged")

    def test_restore_zero_qualifying_entries_is_honest_noop(self):   # edge case, ties existing After / no_snapshot behavior
        snap = self._snap_dir(self.proj)
        snap.mkdir(parents=True)
        (snap / "tooling").mkdir()          # a MANAGED name -- excluded by _is_user_data -> 0 qualifying entries
        (snap / "tooling" / "add.py").write_text("x")
        add = self.proj / ".add"
        self.assertFalse(add.exists(), "precondition: .add/ does not exist yet")

        restored = _installer._restore_data(self.home, str(self.proj))

        self.assertFalse(restored, "a snapshot with zero qualifying entries returns False")
        self.assertFalse(add.exists(), ".add/ is left exactly as it was -- never even created")


# --- scratch-sibling exclusion (shared by persist + restore) -----------------

class ScratchSiblingTest(_Base):
    def test_is_user_data_excludes_scratch_markers_directly(self):   # Must 11
        self.assertFalse(_installer._is_user_data("myproj-abc123.add-tmp-xyz"))
        self.assertFalse(_installer._is_user_data("myproj-abc123.add-bak-xyz"))
        self.assertTrue(_installer._is_user_data("PROJECT.md"), "an ordinary entry is unaffected")

    def test_scratch_sibling_excluded_from_persist_and_restore_scans(self):   # Must 11, Reject scratch_sibling_excluded_from_user_data
        # persist's scan: a stale scratch dir sitting in .add/ must never be snapshotted
        add = self.proj / ".add"; add.mkdir(parents=True)
        (add / "PROJECT.md").write_text("real content")
        scratch = add / "PROJECT.md.add-tmp-abc123"; scratch.mkdir()
        (scratch / "half.txt").write_text("garbage")
        self.assertTrue(_installer._persist_data(self.home, str(self.proj)))
        snap = self._snap_dir(self.proj)
        self.assertTrue((snap / "PROJECT.md").exists())
        self.assertFalse((snap / "PROJECT.md.add-tmp-abc123").exists(),
                          "the scratch sibling is excluded from persist's entries list")

        # restore's scan: if a scratch-marker name somehow ends up INSIDE a snapshot, restore's
        # own filtered scan excludes it too -- never restored into .add/ as if it were real data.
        (snap / "OTHER.add-bak-def456").mkdir()
        shutil.rmtree(add); add.mkdir()
        restored = _installer._restore_data(self.home, str(self.proj))
        self.assertTrue(restored)
        self.assertTrue((add / "PROJECT.md").exists())
        self.assertFalse((add / "OTHER.add-bak-def456").exists(),
                          "restore's own re-entrant scan likewise never treats a scratch marker as real, present data")


# --- prune-data --------------------------------------------------------------

class PruneTest(_Base):
    def _register(self, *projects):
        _installer._write_registry(self.home, [str(p.resolve()) for p in projects])

    def test_dry_run_lists_removes_nothing(self):                      # Must 7
        self._valid_home()
        self._register(self.proj)                                      # proj registered + exists
        snap_a = self._write_snapshot(self.proj, {"state.json": "{}"})
        snap_b = self.home / "data" / "orphan-bbbbbbbbbbbb"; snap_b.mkdir(parents=True)
        (snap_b / "state.json").write_text("{}")
        orphans, removed = _installer._prune_data(self.home, force=False)
        self.assertIn("orphan-bbbbbbbbbbbb", orphans, "an unowned snapshot is an orphan")
        self.assertNotIn(_installer.data_key(str(self.proj.resolve())), orphans, "a live owner is not an orphan")
        self.assertEqual(removed, [], "dry-run removes nothing")
        self.assertTrue(snap_a.exists() and snap_b.exists(), "both snapshots survive a dry-run")

    def test_force_removes_orphan_keeps_live(self):                    # Must 8 + Must 9
        self._valid_home()
        self._register(self.proj)
        snap_a = self._write_snapshot(self.proj, {"state.json": "{}"})
        snap_b = self.home / "data" / "orphan-bbbbbbbbbbbb"; snap_b.mkdir(parents=True)
        (snap_b / "state.json").write_text("{}")
        orphans, removed = _installer._prune_data(self.home, force=True)
        self.assertIn("orphan-bbbbbbbbbbbb", removed, "the unowned orphan is removed under --force")
        self.assertFalse(snap_b.exists(), "orphan dir deleted")
        self.assertTrue(snap_a.exists(), "the live (registry-path-exists) snapshot is kept")

    def test_reclaims_registered_but_vanished(self):                   # orphan = unregistered OR vanished
        self._valid_home()
        vanished = self.tmp / "gone"                                   # a path that does NOT exist
        snap_v = self._write_snapshot(vanished, {"state.json": "{}"})  # keyed on the vanished path
        snap_a = self._write_snapshot(self.proj, {"state.json": "{}"})
        self._register(vanished, self.proj)                            # both registered; only proj exists
        orphans, removed = _installer._prune_data(self.home, force=True)
        self.assertFalse(snap_v.exists(), "a registered-but-vanished snapshot is reclaimed (no LIVE owner)")
        self.assertTrue(snap_a.exists(), "a live owner is kept")

    def test_corrupt_registry_loud_no_removal(self):                   # Reject: registry_corrupt
        self._valid_home()
        snap_b = self.home / "data" / "orphan-bbbbbbbbbbbb"; snap_b.mkdir(parents=True)
        (snap_b / "state.json").write_text("{}")
        reg = self.home / "registry.json"
        reg.write_text("}{ not json")                                  # corrupt
        with self.assertRaises(ValueError):
            _installer._prune_data(self.home, force=True)
        self.assertEqual(reg.read_text(), "}{ not json", "corrupt registry left byte-intact")
        self.assertTrue(snap_b.exists(), "no snapshot removed on a corrupt-registry read")

    def test_prune_data_no_global_home_rejects(self):                  # Reject: no_global_home (command)
        code = _installer.prune_data(force=True, env=self._env())       # home never stamped
        self.assertNotEqual(code, 0, "prune-data with no home must fail (no_global_home)")

    def test_prune_data_command_force_removes(self):                   # prune_data command happy path
        self._valid_home()
        self._register(self.proj)
        self._write_snapshot(self.proj, {"state.json": "{}"})
        snap_b = self.home / "data" / "orphan-bbbbbbbbbbbb"; snap_b.mkdir(parents=True)
        (snap_b / "state.json").write_text("{}")
        code = _installer.prune_data(force=True, env=self._env())
        self.assertEqual(code, 0)
        self.assertFalse(snap_b.exists(), "prune_data --force removes the orphan")


# --- npm / pip parity (structural + real behavioral — M13 + M15) ------------
# ParityRestoreTest's original test_parity_surface was 6 bare assertIn string checks with zero
# subprocess/node invocation (Ground: confirmed). This task's own M15 replaces/extends it with a
# real npm behavioral smoke, and M13 adds a call-site (not just token-presence) structural check.

class ParityRestoreTest(_Base):
    def test_parity_surface(self):
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        cli = (_SRC / "add_method" / "_cli.py").read_text(encoding="utf-8")
        # python core surface
        self.assertIn("_restore_data", py, "_installer.py must define _restore_data")
        self.assertIn("_prune_data", py, "_installer.py must define _prune_data")
        self.assertIn("as_global_data_restore", py, "_installer.py must thread as_global_data_restore")
        # pip CLI wiring
        self.assertIn("from-global-data", cli, "_cli.py must accept --from-global-data")
        self.assertIn("prune-data", cli, "_cli.py must wire the prune-data command")
        # npm twin
        self.assertIn("from-global-data", js, "cli.js must accept --from-global-data")
        self.assertIn("prune-data", js, "cli.js must wire the prune-data command")

    def test_parity_call_site_shape(self):                     # M13 (structural half)
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        # both twins must carry the SAME staged-commit call-site shape, not just the same
        # function names -- the scratch marker names, staging via a fresh unique same-parent
        # sibling, and landing via a same-parent rename.
        for token in (".add-tmp-", ".add-bak-"):
            self.assertIn(token, py, f"_installer.py must use the {token} scratch marker")
            self.assertIn(token, js, f"cli.js must use the {token} scratch marker")
        self.assertIn("tempfile.mkdtemp(dir=", py, "_persist_data/_restore_data must stage via mkdtemp(dir=...)")
        self.assertIn("fs.mkdtempSync(path.join(", js, "persistData/restoreData must stage via mkdtempSync in the SAME parent")
        self.assertIn("os.replace(str(staged)", py, "_installer.py's commit must rename the staged sibling into place")
        self.assertIn("fs.renameSync(staged", js, "cli.js's commit must rename the staged sibling into place")

    def test_npm_restore_and_prune_behavioral_smoke(self):      # M15 + M13 (happy-path half)
        if not shutil.which("node"):
            self.skipTest("node not available")
        self._valid_home()                                     # a real --global install stamps home
        self._write_snapshot(self.proj, {"PROJECT.md": "npm-snapshot-content"})
        env = dict(os.environ); env.update(self._env())

        r = subprocess.run(["node", str(CLI_JS), "init", "--from-global-data", "--yes"],
                            cwd=str(self.proj), capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.proj / ".add" / "PROJECT.md").read_text(), "npm-snapshot-content",
                          "the restore subprocess's real filesystem effect is asserted, not merely "
                          "that 'restoreData' appears as a substring in cli.js")

        orphan = self.home / "data" / "orphan-npmbehavioral01"; orphan.mkdir(parents=True)
        (orphan / "x").write_text("y")
        r2 = subprocess.run(["node", str(CLI_JS), "prune-data"],
                             capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertIn("orphan-npmbehavioral01", r2.stdout, "dry-run lists the real orphan by name")
        self.assertTrue(orphan.exists(), "dry-run removes nothing")

        r3 = subprocess.run(["node", str(CLI_JS), "prune-data", "--force"],
                             capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(r3.returncode, 0, r3.stderr)
        self.assertFalse(orphan.exists(), "--force actually deletes the orphan from the real filesystem")


if __name__ == "__main__":
    unittest.main(verbosity=2)
