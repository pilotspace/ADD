#!/usr/bin/env python3
"""Tests for heal/reconcile (installer-experience · heal-reconcile).

FROZEN @ v1: init AND update scan the target's managed layer, RESTORE missing trees +
REFRESH present ones (sweeping orphans) + REPORT it, never touching user data. The
same-version update no-op persists ONLY when nothing is missing.

pip is hermetic via a synthetic bundled source (mirrors test_update.py); install() gains
an optional `bundled` test param (parity with update()). npm uses the real packaged
sources via subprocess and skips honestly without node.

Run: python3 -m unittest test_heal_reconcile -v
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
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
NODE = shutil.which("node")


def _make_bundled(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill v-new\n")
    (root / "tooling" / "templates").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py v-new\n")
    (root / "tooling" / "test_add.py").write_text("# dev-only — must NOT ship\n")
    return root


def _make_project(root: Path) -> Path:
    """An installed project: managed trees + sacred user data."""
    add = root / ".add"
    (add / "tooling").mkdir(parents=True)
    (add / "tooling" / "add.py").write_text("# add.py v-OLD\n")
    (root / ".claude" / "skills" / "add").mkdir(parents=True)
    (root / ".claude" / "skills" / "add" / "SKILL.md").write_text("skill v-OLD\n")
    (add / "state.json").write_text(json.dumps({"project": "demo", "stage": "mvp"}) + "\n")
    (add / "PROJECT.md").write_text("# my foundation — do not touch\n")
    (add / "milestones" / "mvp").mkdir(parents=True)
    (add / "milestones" / "mvp" / "MILESTONE.md").write_text("my milestone\n")
    return root


# --- pip: hermetic via synthetic bundled (install() gains a `bundled` param) ---

class PipReconcileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="heal-pip-"))
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.proj = _make_project(self.tmp / "proj")

    def _install(self, **kw):
        return _installer.install(target=str(self.proj), bundled=str(self.bundled),
                                  non_interactive=True, **kw)

    def test_init_restores_missing_skill_pip(self):                       # H1, H5
        shutil.rmtree(self.proj / ".claude" / "skills" / "add")
        self.assertEqual(self._install(), 0)
        self.assertEqual((self.proj / ".claude" / "skills" / "add" / "SKILL.md").read_text(),
                         "skill v-new\n", "a missing skill tree must be restored on init")
        self.assertEqual(json.loads((self.proj / ".add" / "state.json").read_text())["project"],
                         "demo", "user data must be untouched")

    def test_init_refreshes_present_and_sweeps_orphan_pip(self):          # H1
        (self.proj / ".add" / "tooling" / "zz-orphan.md").write_text("removed upstream\n")
        self.assertEqual(self._install(), 0)
        self.assertFalse((self.proj / ".add" / "tooling" / "zz-orphan.md").exists(),
                         "init must clean-replace a present tree and sweep orphans")
        self.assertEqual((self.proj / ".add" / "tooling" / "add.py").read_text(),
                         "# add.py v-new\n")

    def test_init_reports_status_pip(self):                               # H2
        shutil.rmtree(self.proj / ".claude" / "skills" / "add")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self._install()
        out = buf.getvalue().lower()
        self.assertIn("restored", out, "a missing tree must be reported as restored")
        self.assertIn("refreshed", out, "a present tree must be reported as refreshed")

    def test_update_heals_missing_at_same_version_pip(self):              # H3
        _installer._write_stamp(self.proj / ".add", "9.9.9")
        shutil.rmtree(self.proj / ".add" / "tooling")
        code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                 version="9.9.9")
        self.assertEqual(code, 0)
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(),
                        "update must HEAL a missing tree even at the same version")

    def test_update_noop_when_nothing_missing_pip(self):                  # H4
        _installer.update(target=str(self.proj), bundled=str(self.bundled), version="9.9.9")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                     version="9.9.9")
        self.assertEqual(code, 0)
        self.assertIn("already at 9.9.9", buf.getvalue().lower(),
                      "same version + nothing missing must stay a no-op")

    def test_user_data_sacred_pip(self):                                  # H5
        self._install()
        self.assertEqual((self.proj / ".add" / "PROJECT.md").read_text(),
                         "# my foundation — do not touch\n")
        self.assertTrue((self.proj / ".add" / "milestones" / "mvp" / "MILESTONE.md").exists())

    def test_drops_files_only_pip(self):                                  # H6
        fresh = Path(tempfile.mkdtemp(prefix="heal-fresh-"))
        code = _installer.install(target=str(fresh), bundled=str(self.bundled),
                                  non_interactive=True)
        self.assertEqual(code, 0)
        self.assertFalse((fresh / ".add" / "state.json").exists(),
                         "init must never create state.json")
        self.assertFalse((fresh / ".add" / "tooling" / "test_add.py").exists(),
                         "installed tooling must strip test_*.py")

    def test_missing_source_fails_closed_pip(self):                       # Reject missing_source
        shutil.rmtree(self.bundled / "tooling")
        before = (self.proj / ".add" / "tooling" / "add.py").read_text()
        code = self._install()
        self.assertNotEqual(code, 0, "a missing packaged source must fail closed")
        self.assertEqual((self.proj / ".add" / "tooling" / "add.py").read_text(),
                         before, "a failed precheck must leave the target untouched")


# --- npm: real packaged sources via subprocess ------------------------------

@unittest.skipUnless(NODE, "node not on PATH — npx-side reconcile checks skipped (honest skip)")
class NpmReconcileTest(unittest.TestCase):
    def _init(self, cwd):
        env = dict(os.environ); env.pop("CI", None)
        return subprocess.run([NODE, str(CLI_JS), "init", "--yes"], cwd=cwd,
                              capture_output=True, text=True, timeout=120, env=env)

    def test_init_restores_missing_tree_npm(self):                        # H1, H7
        with tempfile.TemporaryDirectory(prefix="heal-npm-") as tmp:
            self.assertEqual(self._init(tmp).returncode, 0)
            shutil.rmtree(Path(tmp) / ".claude" / "skills" / "add")
            res = self._init(tmp)
            self.assertEqual(res.returncode, 0)
            self.assertTrue((Path(tmp) / ".claude" / "skills" / "add" / "SKILL.md").exists(),
                            "a missing skill tree must be restored on re-init")
            self.assertIn("restored", res.stdout.lower(),
                          "the restored tree must be reported")

    def test_update_heals_missing_at_same_version_npm(self):              # H3, H7
        with tempfile.TemporaryDirectory(prefix="heal-npm-") as tmp:
            self.assertEqual(self._init(tmp).returncode, 0)
            pkg = json.loads((_ADD_METHOD / "package.json").read_text())["version"]
            (Path(tmp) / ".add" / ".add-version").write_text(
                json.dumps({"version": pkg, "channel": "npm"}) + "\n")
            # a real project has state.json (the human ran init) — write it BEFORE removing
            # tooling, because .add/tooling doubles as update's project-detection marker
            (Path(tmp) / ".add" / "state.json").write_text('{"project": "demo"}\n')
            shutil.rmtree(Path(tmp) / ".add" / "tooling")
            env = dict(os.environ); env.pop("CI", None)
            res = subprocess.run([NODE, str(CLI_JS), "update"], cwd=tmp,
                                 capture_output=True, text=True, timeout=120, env=env)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((Path(tmp) / ".add" / "tooling" / "add.py").exists(),
                            "update must heal a missing tooling tree at the same version")


class ParityVocabTest(unittest.TestCase):
    def test_parity_status_vocab(self):                                   # H7 structural
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        for word in ("restored", "refreshed"):
            self.assertIn(word, js, f"cli.js must use the '{word}' status word")
            self.assertIn(word, py, f"_installer.py must use the '{word}' status word")


if __name__ == "__main__":
    unittest.main(verbosity=2)
