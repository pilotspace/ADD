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
import sys
import tempfile
import unittest
from pathlib import Path

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
        self.tmp = Path(tempfile.mkdtemp(prefix="grestore-"))
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

    def _read(self, p: Path) -> str:
        return p.read_text()


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


# --- npm / pip parity (structural) ------------------------------------------

class ParityRestoreTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
