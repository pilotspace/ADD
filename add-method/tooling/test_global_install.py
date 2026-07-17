#!/usr/bin/env python3
"""Tests for the global ADD home (installer-experience · global-install).

FROZEN @ v1: an OPT-IN `--global` installs the managed layer ONCE to a shared home
(ADD_HOME → XDG_DATA_HOME/add → ~/.add), skill → ~/.claude/skills/add, registers each
opting project in <home>/registry.json, and `update --global` refreshes the home then
propagates to every registered+existing project (pruning vanished ones). The per-project
self-contained/git-tracked DEFAULT is untouched.

Fully hermetic: home + skill base are resolved from the injected `env` (reusing agent-detect's
env hook), so tests touch a tmp home/HOME — never the real ~/.add or ~/.claude. npm uses
subprocess with the same env injected (skips honestly without node).

Run: python3 -m unittest test_global_install -v
"""
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
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    (root / "tooling" / "test_add.py").write_text("# dev-only\n")
    return root


# --- home resolution (pure) -------------------------------------------------

class ResolveHomeTest(unittest.TestCase):
    def test_resolve_home_precedence(self):                       # G1
        self.assertEqual(_installer.resolve_global_home({"ADD_HOME": "/h"}), Path("/h"))
        self.assertEqual(_installer.resolve_global_home({"XDG_DATA_HOME": "/x"}), Path("/x") / "add")
        self.assertEqual(_installer.resolve_global_home({"HOME": "/u"}), Path("/u") / ".add")
        # ADD_HOME wins over XDG
        self.assertEqual(_installer.resolve_global_home({"ADD_HOME": "/h", "XDG_DATA_HOME": "/x"}),
                         Path("/h"))


# --- global install / update (hermetic via injected env) --------------------

class GlobalInstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="global-"))
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.home = self.tmp / "home"          # ADD_HOME
        self.userhome = self.tmp / "user"      # HOME (for ~/.claude/skills/add)
        self.userhome.mkdir()
        self.proj = self.tmp / "proj"
        self.proj.mkdir()

    def _env(self):
        return {"ADD_HOME": str(self.home), "HOME": str(self.userhome)}

    def _install(self, target, **kw):
        return _installer.install(target=str(target), bundled=str(self.bundled),
                                  non_interactive=True, env=self._env(), as_global=True, **kw)

    def _registry(self):
        return json.loads((self.home / "registry.json").read_text())

    def test_global_install_populates_home(self):                 # G2
        self.assertEqual(self._install(self.proj), 0)
        self.assertTrue((self.home / "tooling" / "add.py").exists())
        self.assertFalse((self.home / "tooling" / "test_add.py").exists(),
                         "installed tooling must strip test_*.py")
        self.assertTrue((self.userhome / ".claude" / "skills" / "add" / "SKILL.md").exists(),
                        "skill must land at ~/.claude/skills/add")
        # v2: the home MIRRORS the bundled layer — skill/add is the CANONICAL source the
        # update-propagation reads (reconcile(p, source=<home>) reuses the standard MANAGED map).
        self.assertTrue((self.home / "skill" / "add" / "SKILL.md").exists(),
                        "home must hold skill/add as the canonical mirror source (v2)")
        stamp = json.loads((self.home / ".add-version").read_text())
        self.assertEqual(stamp.get("channel"), "global")

    def test_global_install_registers_and_drops(self):            # G3
        self._install(self.proj)
        self.assertEqual(self._registry(), [str(self.proj.resolve())],
                         "the project must be registered once")
        self._install(self.proj)                                  # re-run
        self.assertEqual(self._registry().count(str(self.proj.resolve())), 1,
                         "re-registering must not duplicate")
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(),
                        "the project still gets its self-contained drop")

    def test_global_no_state(self):                               # G5
        self._install(self.proj)
        self.assertFalse((self.home / "state.json").exists())
        self.assertFalse((self.proj / ".add" / "state.json").exists())
        self.assertNotIn("spawnSync", CLI_JS.read_text(encoding="utf-8"))

    def test_update_global_refreshes_all_projects(self):          # G4
        proj2 = self.tmp / "proj2"; proj2.mkdir()
        self._install(self.proj)
        self._install(proj2)
        # gut a managed tree in proj1; update --global must heal it from the home
        shutil.rmtree(self.proj / ".add" / "tooling")
        code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                 version="9.9.9", env=self._env(), as_global=True)
        self.assertEqual(code, 0)
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(),
                        "update --global must propagate to registered project 1")
        self.assertTrue((proj2 / ".add" / "tooling" / "add.py").exists(),
                        "registered project 2 stays intact/refreshed")
        # the home mirror is the propagation SOURCE — it must hold a complete managed layer
        # (skill/add+tooling) for reconcile(p, source=<home>) to have anything to read.
        self.assertTrue((self.home / "skill" / "add" / "SKILL.md").exists()
                        and (self.home / "tooling" / "add.py").exists(),
                        "the home must remain a complete mirror after update --global")

    def test_update_global_prunes_missing(self):                  # G4
        self._install(self.proj)
        gone = self.tmp / "gone"; gone.mkdir()
        self._install(gone)
        shutil.rmtree(gone)                                       # vanish a registered project
        code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                 version="9.9.9", env=self._env(), as_global=True)
        self.assertEqual(code, 0)
        self.assertNotIn(str(gone.resolve()), self._registry(),
                         "a vanished registered project must be pruned")
        self.assertIn(str(self.proj.resolve()), self._registry())

    def test_update_global_no_home_fails(self):                   # Reject no_global_home
        code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                 version="9.9.9", env=self._env(), as_global=True)
        self.assertNotEqual(code, 0, "update --global with no home install must fail closed")

    def test_registry_corrupt_fails_loud(self):                   # Reject registry_corrupt
        self._install(self.proj)
        (self.home / "registry.json").write_text("{not json")
        code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                 version="9.9.9", env=self._env(), as_global=True)
        self.assertNotEqual(code, 0, "a corrupt registry must fail loudly, not silently skip")
        self.assertEqual((self.home / "registry.json").read_text(), "{not json",
                         "a corrupt registry must be left for the user, not emptied")

    def test_home_unwritable_fails(self):                         # Reject home_unwritable
        self.home.write_text("i am a file, not a dir")            # mkdir(home) impossible
        code = self._install(self.proj)
        self.assertNotEqual(code, 0, "an unwritable home must fail closed")
        self.assertFalse((self.proj / ".add").exists(),
                         "a global failure must abort BEFORE the per-project drop (fail-closed)")

    def test_plain_install_untouched_by_global(self):             # G7
        code = _installer.install(target=str(self.proj), bundled=str(self.bundled),
                                  non_interactive=True, env=self._env())   # NO as_global
        self.assertEqual(code, 0)
        self.assertFalse(self.home.exists(), "a plain install must not create the global home")
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(),
                        "a plain install is the self-contained drop, as today")


# --- npm: real packaged sources via subprocess ------------------------------

@unittest.skipUnless(NODE, "node not on PATH — npx-side global checks skipped (honest skip)")
class NpmGlobalTest(unittest.TestCase):
    def _env(self, home, userhome):
        env = dict(os.environ)
        env.pop("CI", None)
        env["ADD_HOME"] = str(home)
        env["HOME"] = str(userhome)
        return env

    def test_global_install_npm(self):                            # G2, G3, G6
        with tempfile.TemporaryDirectory(prefix="global-npm-") as tmp:
            tmp = Path(tmp)
            home, userhome, proj = tmp / "home", tmp / "user", tmp / "proj"
            userhome.mkdir(); proj.mkdir()
            res = subprocess.run([NODE, str(CLI_JS), "init", "--global", "--yes"], cwd=proj,
                                 capture_output=True, text=True, timeout=120,
                                 env=self._env(home, userhome))
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((home / "tooling" / "add.py").exists(), "global home tooling")
            self.assertTrue((userhome / ".claude" / "skills" / "add").exists(), "global skill")
            reg = json.loads((home / "registry.json").read_text())
            self.assertIn(str(proj.resolve()), reg, "project registered")
            self.assertTrue((proj / ".add" / "tooling" / "add.py").exists(), "self-contained drop")

    def test_update_global_npm(self):                             # G4, G6
        with tempfile.TemporaryDirectory(prefix="global-npm-") as tmp:
            tmp = Path(tmp)
            home, userhome, proj = tmp / "home", tmp / "user", tmp / "proj"
            userhome.mkdir(); proj.mkdir()
            env = self._env(home, userhome)
            self.assertEqual(subprocess.run([NODE, str(CLI_JS), "init", "--global", "--yes"],
                             cwd=proj, capture_output=True, text=True, timeout=120, env=env).returncode, 0)
            shutil.rmtree(proj / ".add" / "tooling")
            res = subprocess.run([NODE, str(CLI_JS), "update", "--global"], cwd=proj,
                                 capture_output=True, text=True, timeout=120, env=env)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((proj / ".add" / "tooling" / "add.py").exists(),
                            "update --global must propagate to the registered project")


class ParityGlobalTest(unittest.TestCase):
    def test_parity_global(self):                                 # G6 structural
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        self.assertIn("resolveGlobalHome", js)
        self.assertIn("resolve_global_home", py)
        for token in ("registry.json", "ADD_HOME", "XDG_DATA_HOME"):
            self.assertIn(token, js, f"cli.js must mention '{token}'")
            self.assertIn(token, py, f"_installer.py must mention '{token}'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
