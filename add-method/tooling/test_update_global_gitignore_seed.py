#!/usr/bin/env python3
"""Tests for update-global-gitignore-seed (`update --global`'s propagation loop must re-seed
each registered project's `.add/.gitignore`, not just its managed skill/tooling/docs trees).

THE GAP (found while verifying gitignore-vendor-path-fix's blast radius): `_update_global`
(pip) / `cmdUpdateGlobal` (npm) refresh the shared home then, for each registered project,
call `_reconcile`/`reconcile` — but never `_seed_gitignore`/`seedGitignore`. A project that
never runs a direct per-project `update` or fresh `install` keeps a stale `.add/.gitignore`
forever, even after `update --global` refreshes everything else. This is independent of any
specific gitignore-pattern bug — it would exist for ANY future `_GITIGNORE_BODY` change.

Fully hermetic: home + skill base resolve from the injected `env` (global-install's hook), so
tests touch a tmp home/HOME — never the real ~/.add. Mirrors test_global_update_harden.py's
_Base fixture shape; `_make_bundled` here DELIBERATELY includes `templates/gitignore.tmpl`
(the sibling FROZEN fixtures omit it on purpose, so `_seed_gitignore` fail-soft-skips there —
this file needs it present to actually exercise the seed).

RED until `_update_global`/`cmdUpdateGlobal` call `_seed_gitignore`/`seedGitignore` per project.

Run: python3 -m unittest test_update_global_gitignore_seed -v
"""
import io
import contextlib
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


def _make_bundled(root: Path, extra_pattern: str | None = None) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    tdir = root / "tooling" / "templates"
    tdir.mkdir(parents=True)
    body = "# transient artifacts\nscope-snapshot.json\n\n# managed vendor trees\nsentinel-tree/\n"
    if extra_pattern:
        body += extra_pattern.rstrip("\n") + "/\n"
    (tdir / "gitignore.tmpl").write_text(body)
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro\n")
    return root


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gupdate-gi-")).resolve()
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.home = self.tmp / "home"
        self.userhome = self.tmp / "user"; self.userhome.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self):
        return {"ADD_HOME": str(self.home), "HOME": str(self.userhome)}

    def _install_global(self, target, bundled=None, **kw):
        return _installer.install(target=str(target), bundled=str(bundled or self.bundled),
                                  non_interactive=True, env=self._env(), as_global=True, **kw)

    def _valid_home(self):
        seed = self.tmp / "seed"; seed.mkdir()
        self.assertEqual(self._install_global(seed), 0, "setup: --global stamps the home")

    def _make_project(self, p: Path):
        p.mkdir(parents=True, exist_ok=True)
        self.assertEqual(self._install_global(p), 0, f"setup: install {p.name} as an ADD project")

    def _set_registry(self, *entries):
        import json
        (self.home / "registry.json").write_text(
            json.dumps([str(e) for e in entries], indent=2) + "\n", encoding="utf-8")

    def _gi(self, proj: Path) -> Path:
        return proj / ".add" / ".gitignore"

    def _update(self, bundled=None, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            code = _installer.update(target=str(self.tmp / "unused"),
                                     bundled=str(bundled or self.bundled),
                                     version="9.9.9", env=self._env(), as_global=True, **kw)
        return code, buf.getvalue()


class PipGlobalUpdateSeedsGitignore(_Base):
    def test_stale_project_gets_gitignore_refreshed(self):    # M1/M3/R1
        self._valid_home()
        proj = self.tmp / "proj"
        self._make_project(proj)
        # simulate "registered a while ago, never ran a direct per-project update since":
        # blank the file so it lacks the current managed pattern entirely.
        self._gi(proj).write_text("", encoding="utf-8")
        self._set_registry(proj.resolve())
        code, _ = self._update()
        self.assertEqual(code, 0)
        body = self._gi(proj).read_text(encoding="utf-8")
        self.assertIn("sentinel-tree/", body,
                      "update --global alone must re-seed a stale project's .gitignore "
                      "(gitignore_seed_skipped_on_global_propagation)")

    def test_custom_line_survives(self):                      # M4/R3
        self._valid_home()
        proj = self.tmp / "proj"
        self._make_project(proj)
        self._gi(proj).write_text("my-secret.local\nscope-snapshot.json\n", encoding="utf-8")
        self._set_registry(proj.resolve())
        code, _ = self._update()
        self.assertEqual(code, 0)
        body = self._gi(proj).read_text(encoding="utf-8")
        lines = body.splitlines()
        self.assertEqual(lines[0], "my-secret.local", "custom line keeps its original position")
        self.assertIn("sentinel-tree/", body)
        self.assertEqual(body.count("sentinel-tree/"), 1, "no duplicate pattern line")

    def test_already_current_project_is_noop(self):           # M5
        self._valid_home()
        proj = self.tmp / "proj"
        self._make_project(proj)                              # already seeded from self.bundled
        before = self._gi(proj).read_text(encoding="utf-8")
        self._set_registry(proj.resolve())
        code, _ = self._update()
        self.assertEqual(code, 0)
        self.assertEqual(self._gi(proj).read_text(encoding="utf-8"), before,
                         "an already-current project's .gitignore must be byte-unchanged")

    def test_seed_failure_does_not_abort_propagation(self):   # R2
        self._valid_home()
        healthy = self.tmp / "healthy"; self._make_project(healthy)
        broken = self.tmp / "broken"; self._make_project(broken)
        self._set_registry(healthy.resolve(), broken.resolve())
        bundled2 = _make_bundled(self.tmp / "pkg2", extra_pattern="new-managed-tree")

        real_write_text = Path.write_text
        broken_gi = self._gi(broken).resolve()

        def _flaky_write_text(self_path, *a, **kw):
            if self_path.resolve() == broken_gi:
                raise OSError("simulated write failure")
            return real_write_text(self_path, *a, **kw)

        with mock.patch.object(Path, "write_text", _flaky_write_text):
            code, _ = self._update(bundled=bundled2)
        self.assertEqual(code, 0,
                         "one project's gitignore-seed failure must not abort the whole run")
        self.assertIn("new-managed-tree/", self._gi(healthy).read_text(encoding="utf-8"),
                      "the healthy project was still seeded despite the sibling's failure")


class NpmGlobalUpdateSeedsGitignore(_Base):
    def test_stale_project_gets_gitignore_refreshed(self):    # M2/M3/R1
        if not shutil.which("node"):
            self.skipTest("node not available")
        self._valid_home()
        proj = self.tmp / "proj"
        self._make_project(proj)
        self._gi(proj).write_text("", encoding="utf-8")
        self._set_registry(proj.resolve())
        env = dict(os.environ); env.update(self._env())
        r = subprocess.run(["node", str(CLI_JS), "update", "--global"],
                           capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(r.returncode, 0, f"npm update --global failed: {r.stdout}{r.stderr}")
        body = self._gi(proj).read_text(encoding="utf-8")
        self.assertIn("tooling/", body,
                      "npm update --global alone must re-seed a stale project's .gitignore "
                      "(uses the real cli.js bundled tooling/templates/gitignore.tmpl)")


class ParityCallSiteTest(unittest.TestCase):
    def test_pip_call_site_present(self):                     # M1, structural
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        import re
        m = re.search(r"def _update_global\([\s\S]*?\n(?=def _update_global|\Z)", py)
        self.assertIsNotNone(m, "could not locate _update_global")
        self.assertIn("_seed_gitignore(Path(np), home)", m.group(0),
                      "_update_global must call _seed_gitignore per registered project (call-site)")

    def test_npm_call_site_present(self):                     # M2, structural
        js = CLI_JS.read_text(encoding="utf-8")
        import re
        m = re.search(r"function cmdUpdateGlobal\([\s\S]*?\n\}", js)
        self.assertIsNotNone(m, "could not locate cmdUpdateGlobal")
        self.assertIn("seedGitignore(np)", m.group(0),
                      "cmdUpdateGlobal must call seedGitignore per registered project (call-site)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
