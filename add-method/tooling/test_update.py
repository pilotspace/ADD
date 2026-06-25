#!/usr/bin/env python3
"""Behavioral proof of `update` — re-materialize the managed layer without re-install.

The gap this closes: the launchers (bin/cli.js · _installer.py) only had `init`, which
DROPS FILES. To pull a new ADD version into an existing project you had to re-install,
and `init`'s tooling/docs copy MERGES (never removes), so a file deleted in a new version
lingered forever. `update` is the discoverable, version-aware, state-safe path.

CONTRACT (frozen @ v1):
  - `update` re-materializes the three MANAGED trees (skill · tooling · docs) by
    CLEAN-REPLACE, so a file removed upstream leaves no orphan behind.
  - It NEVER touches user data: state.json, PROJECT.md, milestones/, tasks/, archive/.
  - It writes a version stamp (.add/.add-version) and is IDEMPOTENT: same version twice
    is a no-op (unless --force).
  - It backs up state (.add/pre-update-state.bak.json) before any change (design-for-failure).
  - It fails closed when there is no .add/ project to update.
  - npm ↔ pip parity: bin/cli.js exposes the same `update` verb as the pip twin.

Behavioral where Python-runnable (the pip twin), text-invariant for bin/cli.js (no node
in the test env) — same split as test_v8_install.
Run: python3 -m unittest test_update -v
"""
import json
import os
import sys
import tempfile
import shutil
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
    """A synthetic packaged source: skill/add · tooling (with a test_*.py to prove stripping) · docs."""
    (root / "skill" / "add" / "phases").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill v-new\n")
    (root / "skill" / "add" / "phases" / "1-specify.md").write_text("specify v-new\n")
    (root / "tooling" / "templates").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py v-new\n")
    (root / "tooling" / "templates" / "TASK.md.tmpl").write_text("task tmpl v-new\n")
    (root / "tooling" / "test_add.py").write_text("# dev-only test — must NOT ship\n")
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro v-new\n")
    return root


def _make_project(root: Path) -> Path:
    """A project that looks like an OLD install: managed trees + user data + a stale orphan."""
    add = root / ".add"
    (add / "tooling").mkdir(parents=True)
    (add / "tooling" / "add.py").write_text("# add.py v-OLD\n")
    (add / "tooling" / "OLD_ORPHAN.py").write_text("# removed upstream — must be swept\n")
    (add / "docs").mkdir(parents=True)
    (add / "docs" / "zz-removed-chapter.md").write_text("deleted upstream — must be swept\n")
    (root / ".claude" / "skills" / "add").mkdir(parents=True)
    (root / ".claude" / "skills" / "add" / "SKILL.md").write_text("skill v-OLD\n")
    # user data — sacred
    (add / "state.json").write_text(json.dumps({"project": "demo", "stage": "mvp"}) + "\n")
    (add / "PROJECT.md").write_text("# my foundation — do not touch\n")
    (add / "milestones").mkdir()
    (add / "milestones" / "mvp").mkdir()
    (add / "milestones" / "mvp" / "MILESTONE.md").write_text("my milestone\n")
    return root


class UpdateBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-update-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.proj = _make_project(self.tmp / "proj")

    def _update(self, **kw):
        return _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                 version=kw.pop("version", "2.0.0"), **kw)

    def test_fails_closed_without_a_project(self):
        empty = self.tmp / "empty"
        empty.mkdir()
        code = _installer.update(target=str(empty), bundled=str(self.bundled), version="2.0.0")
        self.assertNotEqual(code, 0)

    def test_clean_replace_sweeps_orphans(self):
        self.assertEqual(self._update(), 0)
        self.assertFalse((self.proj / ".add" / "tooling" / "OLD_ORPHAN.py").exists(),
                         "a file removed upstream must not survive update (orphan)")
        self.assertFalse((self.proj / ".add" / "docs" / "zz-removed-chapter.md").exists())
        # and the new content landed
        self.assertEqual((self.proj / ".add" / "tooling" / "add.py").read_text(), "# add.py v-new\n")
        self.assertEqual((self.proj / ".claude" / "skills" / "add" / "SKILL.md").read_text(),
                         "skill v-new\n")

    def test_tests_are_stripped_from_the_installed_tooling(self):
        self._update()
        self.assertFalse((self.proj / ".add" / "tooling" / "test_add.py").exists(),
                         "dev-only test_*.py must never land in an installed project")

    def test_user_data_is_never_touched(self):
        self._update()
        self.assertEqual(json.loads((self.proj / ".add" / "state.json").read_text())["project"], "demo")
        self.assertEqual((self.proj / ".add" / "PROJECT.md").read_text(), "# my foundation — do not touch\n")
        self.assertTrue((self.proj / ".add" / "milestones" / "mvp" / "MILESTONE.md").exists())

    def test_stamp_written_and_idempotent(self):
        self.assertEqual(self._update(version="2.0.0"), 0)
        stamp = json.loads((self.proj / ".add" / ".add-version").read_text())
        self.assertEqual(stamp["version"], "2.0.0")
        # same version again -> no-op (engine of idempotency)
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = self._update(version="2.0.0")
        self.assertEqual(code, 0)
        self.assertIn("already at 2.0.0", buf.getvalue().lower())

    def test_state_backed_up_before_change(self):
        self._update()
        self.assertTrue((self.proj / ".add" / "pre-update-state.bak.json").exists(),
                        "state must be backed up before update (design-for-failure)")

    def test_force_remateralizes_even_when_current(self):
        self._update(version="2.0.0")
        # corrupt a managed file, then --force should restore it though version is unchanged
        (self.proj / ".add" / "tooling" / "add.py").write_text("# hand-edited\n")
        self.assertEqual(self._update(version="2.0.0", force=True), 0)
        self.assertEqual((self.proj / ".add" / "tooling" / "add.py").read_text(), "# add.py v-new\n")


class UpdateCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-check-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.proj = _make_project(self.tmp / "proj")

    def test_check_reports_drift_without_writing(self):
        import io
        import contextlib
        # stamp the project at an OLDER version, then check against a newer package
        _installer._write_stamp(self.proj / ".add", "1.0.0")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _installer.update_check(target=str(self.proj), version="2.0.0")
        self.assertEqual(code, 0)
        self.assertIn("update available", buf.getvalue().lower())
        # check is read-only: it must NOT advance the stamp
        stamp = json.loads((self.proj / ".add" / ".add-version").read_text())
        self.assertEqual(stamp["version"], "1.0.0")


class TwinParityTest(unittest.TestCase):
    """bin/cli.js must expose the same `update` verb (npm ↔ pip parity)."""
    def test_cli_js_has_update_verb(self):
        src = CLI_JS.read_text(encoding="utf-8")
        self.assertIn('case "update"', src, "cli.js must route an `update` subcommand")
        self.assertIn(".add-version", src, "cli.js update must write the version stamp")

    def test_cli_js_update_is_pure_file_copy(self):
        # parity with the install invariant: no subprocess, never runs add.py init.
        src = CLI_JS.read_text(encoding="utf-8")
        for spawn in ("spawnSync", "execSync", "child_process"):
            self.assertNotIn(spawn, src, f"cli.js must stay pure file-copy (found {spawn})")


if __name__ == "__main__":
    unittest.main()
