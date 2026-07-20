#!/usr/bin/env python3
"""updater 2.0 gaps (review finding, pre-2.0.0 tag) — both installer twins.

Three gaps the update review surfaced:

1. GLOBAL ROSTER DRIFT (open since installer-shared-namespace, PR #151): the global
   home mirror (GLOBAL_TREES / _GLOBAL_TREES) never carried `agents/`, so
   `update --global` propagation — which sources registered projects FROM the home —
   soft-skipped the roster forever: no roster refresh, no retired-agent tombstones.
2. 2.0 CROSSING IS SILENT: a 1.x project updating into 2.0 is left with a TASK.md
   board the human must know to migrate, and a stale CLAUDE.md guidance block only
   `add.py sync-guidelines` can regenerate (engine-owned — the updater must NUDGE,
   never regenerate, and never depend on python3 being present).
3. STALE PROSE: the pip updater still logs "docs refreshed" — the docs tree stopped
   shipping at book-stops-shipping.

Node twin covered via subprocess (skips honestly without node); hermetic env
injection throughout — never the real ~/.add or ~/.claude.

Run: cd add-method/tooling && python3 -m unittest test_updater_2_0_gaps -v
"""
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from add_method import _installer            # noqa: E402

CLI_JS = _ADD_METHOD / "bin" / "cli.js"
NODE = shutil.which("node")


def _mk_bundled(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    (root / "agents").mkdir(parents=True)
    (root / "agents" / "add.md").write_text("# the one add agent\n")
    return root


class _Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="upd2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _mk_project(self, stamp_version="1.17.0", task_doc="TASK.md"):
        proj = self.tmp / "proj"
        add = proj / ".add"
        (add / "tooling").mkdir(parents=True)
        (add / "tooling" / "add.py").write_text("# old engine\n")
        (add / "state.json").write_text("{}")
        (add / "tasks" / "t").mkdir(parents=True)
        (add / "tasks" / "t" / task_doc).write_text("# board doc\n")
        (add / ".add-version").write_text(json.dumps({"version": stamp_version, "channel": "pip"}))
        return proj

    def _update(self, proj):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = _installer.update(str(proj), bundled=str(_mk_bundled(self.tmp / "pkg")),
                                   version="2.0.0")
        return rc, buf.getvalue()


class GlobalRosterMirrorTest(_Tmp):
    def test_py_global_home_mirrors_agents(self):
        bundled = _mk_bundled(self.tmp / "pkg")
        home, claude = self.tmp / "home", self.tmp / "claude-skill"
        _installer._reconcile_global(home, claude, bundled, no_skill=True)
        self.assertTrue((home / "agents" / "add.md").exists(),
                        "the home mirror must carry the roster or `update --global` "
                        "propagation soft-skips it forever (roster-drift, PR #151 residue)")

    @unittest.skipUnless(NODE, "node not available")
    def test_js_global_home_mirrors_agents(self):
        home, userhome, proj = self.tmp / "home", self.tmp / "user", self.tmp / "proj"
        userhome.mkdir(); proj.mkdir()
        env = {"ADD_HOME": str(home), "HOME": str(userhome), "PATH": "/usr/bin:/bin:/usr/local/bin"}
        r = subprocess.run([NODE, str(CLI_JS), "init", str(proj), "--global", "--yes"],
                           capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((home / "agents" / "add.md").exists(),
                        "js twin: init --global must mirror agents/ into the home")


class CrossingNudgeTest(_Tmp):
    def test_py_update_nudges_migrate_on_1x_board(self):
        rc, out = self._update(self._mk_project(task_doc="TASK.md"))
        self.assertEqual(rc, 0, out)
        self.assertIn("migrate", out, "a TASK.md-era board crossing into 2.0 must be told "
                                      "the ONE next step — add.py migrate (idempotent)")

    def test_py_no_migrate_nudge_on_plan_board(self):
        rc, out = self._update(self._mk_project(task_doc="PLAN.md"))
        self.assertEqual(rc, 0, out)
        self.assertNotIn("migrate", out)

    def test_py_update_nudges_sync_guidelines_on_version_cross(self):
        rc, out = self._update(self._mk_project(task_doc="PLAN.md"))
        self.assertEqual(rc, 0, out)
        self.assertIn("sync-guidelines", out,
                      "a version-crossing update leaves a stale CLAUDE.md block only the "
                      "engine can regenerate — the updater must say so")

    def test_py_stale_docs_prose_gone(self):
        rc, out = self._update(self._mk_project(task_doc="PLAN.md"))
        self.assertNotIn("docs refreshed", out,
                         "docs stopped shipping at book-stops-shipping — the log must not "
                         "claim otherwise")

    @unittest.skipUnless(NODE, "node not available")
    def test_js_update_prints_migrate_nudge(self):
        userhome = self.tmp / "user"; userhome.mkdir()
        proj = self.tmp / "jsproj"; proj.mkdir()
        env = {"HOME": str(userhome), "PATH": "/usr/bin:/bin:/usr/local/bin"}
        r = subprocess.run([NODE, str(CLI_JS), "init", str(proj), "--no-skill", "--yes"],
                           capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        t = proj / ".add" / "tasks" / "t"
        t.mkdir(parents=True)
        (t / "TASK.md").write_text("# 1.x board doc\n")
        (proj / ".add" / ".add-version").write_text(
            json.dumps({"version": "1.17.0", "channel": "npm"}))
        r = subprocess.run([NODE, str(CLI_JS), "update", str(proj)],
                           capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("migrate", r.stdout)
        self.assertIn("sync-guidelines", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
