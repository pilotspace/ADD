#!/usr/bin/env python3
"""Tests for global-update-harden (installer-polish · global-update-harden).

FROZEN @ v2: make `update --global` concurrency-safe + reject unsafe registry paths.
  - A home file-lock at <home>/.update.lock wraps the whole run — an O_EXCL lockfile in BOTH
    twins (presence = held, so a pip-held lock blocks an npm run and vice-versa; v1's
    flock-pip/O_EXCL-npm split did NOT serialize cross-twin). A concurrent run fails fast with
    "update_in_progress", reconciling nothing; the lock is unlinked on success OR failure
    (a follow-up run re-acquires). A hard crash may leave a stale lockfile to remove by hand.
  - PRE-SCAN: the ONLY LOUD case is a NON-ABSOLUTE (relative) registry path — the true
    traversal vector → "unsafe_registry_path", exit 1, nothing reconciled, registry intact.
  - Each ABSOLUTE entry is NORMALIZED (os.path.normpath); then a vanished path → prune,
    an existing non-ADD-project (no .add/) → warn + DROP (the is-project security backstop:
    a reconcile NEVER lands in a dir without .add/), an existing ADD project → reconcile +
    re-persist opted-in. A non-normalized legit entry is HEALED (registry rewritten with the
    normalized form). Preserved: corrupt registry → LOUD; no home → no_global_home.

Fully hermetic: home + skill base resolve from the injected `env` (global-install's hook),
so tests touch a tmp home/HOME — never the real ~/.add. The home is stamped via a real
`--global` install; registries are then written directly for precise control. The O_EXCL
lockfile is cross-platform (no POSIX-only fcntl). npm parity is structural (call-sites, not
just defs) + node subprocess smokes on the relative-path reject AND cross-twin lock blocking.

RED until _update_lock / _valid_registry_path / the hardened _update_global exist — red for
the right reason (missing implementation).

Run: python3 -m unittest test_global_update_harden -v
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

LOCK_NAME = ".update.lock"


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
        self.tmp = Path(tempfile.mkdtemp(prefix="gupdate-")).resolve()
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.home = self.tmp / "home"
        self.userhome = self.tmp / "user"; self.userhome.mkdir()
        self.proj = self.tmp / "proj"; self.proj.mkdir()
        self.other = self.tmp / "other"; self.other.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self):
        return {"ADD_HOME": str(self.home), "HOME": str(self.userhome)}

    def _install_global(self, target, **kw):
        """A real --global install: stamps the home AND makes <target> a registered ADD project."""
        return _installer.install(target=str(target), bundled=str(self.bundled),
                                  non_interactive=True, env=self._env(), as_global=True, **kw)

    def _valid_home(self):
        self.assertEqual(self._install_global(self.other), 0, "setup: --global stamps the home")

    def _make_project(self, p: Path):
        """Install p as a registered ADD project (creates p/.add/tooling/add.py)."""
        p.mkdir(parents=True, exist_ok=True)
        self.assertEqual(self._install_global(p), 0, f"setup: install {p.name} as an ADD project")

    def _set_registry(self, *entries):
        """Write the registry verbatim (entries may be str or Path) — bypasses normalization."""
        (self.home / "registry.json").write_text(
            json.dumps([str(e) for e in entries], indent=2) + "\n", encoding="utf-8")

    def _registry(self):
        return json.loads((self.home / "registry.json").read_text())

    def _update(self, **kw):
        """Invoke `update --global`, capturing stderr; returns (code, stderr_text)."""
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                     version="9.9.9", env=self._env(), as_global=True, **kw)
        return code, buf.getvalue()

    def _stamp_text(self):
        return _installer._stamp_path(self.home).read_text(encoding="utf-8")


# --- locking (v2: an O_EXCL lockfile in BOTH twins — presence = held) -------

class LockTest(_Base):
    def _hold_lock(self):
        """Simulate an in-flight run by EXCLUSIVELY creating the lockfile (the impl's mechanism)."""
        return os.open(str(self.home / LOCK_NAME), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)

    def _release(self, fd):
        os.close(fd)
        try:
            os.unlink(str(self.home / LOCK_NAME))
        except OSError:
            pass

    def test_runs_under_lock_then_releases(self):                    # Must 1
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        shutil.rmtree(self.proj / ".add" / "docs")                   # sentinel: reconcile restores it
        code, _ = self._update()
        self.assertEqual(code, 0)
        self.assertTrue((self.proj / ".add" / "docs" / "00-introduction.md").exists(),
                        "the project was reconciled under the lock")
        self.assertFalse((self.home / LOCK_NAME).exists(), "the lockfile is unlinked after a successful run")
        code2, _ = self._update()                                    # lock was released -> a 2nd run acquires it
        self.assertEqual(code2, 0, "the lock is free after the run (a second update succeeds)")

    def test_concurrent_update_fails_fast(self):                     # Must 2 + Reject update_in_progress
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        shutil.rmtree(self.proj / ".add" / "docs")                   # sentinel: must NOT be restored on fail-fast
        fd = self._hold_lock()
        try:
            code, err = self._update()
        finally:
            self._release(fd)
        self.assertNotEqual(code, 0, "a held lock fails the second run fast")
        self.assertIn("update_in_progress", err)
        self.assertFalse((self.proj / ".add" / "docs").exists(),
                         "nothing reconciled while the lock was held")

    def test_lock_released_after_failure(self):                      # Must 1 (release-on-failure)
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry("rel/proj", self.proj.resolve())          # a relative path -> unsafe -> exit 1
        code, err = self._update()
        self.assertNotEqual(code, 0)
        self.assertIn("unsafe_registry_path", err)
        self.assertFalse((self.home / LOCK_NAME).exists(), "the lockfile is unlinked even on a failed run")
        self._set_registry(self.proj.resolve())                      # fix the registry
        code2, _ = self._update()
        self.assertEqual(code2, 0, "the lock was released on the failed run (a later run acquires it)")

    def test_cross_twin_lockfile_blocks_both(self):                  # v2: cross-twin serialization (refute-read Finding 1)
        # An existing .update.lock (whoever created it) must fail-fast BOTH twins — proving they
        # share the SAME O_EXCL mechanism (the v1 flock-pip/O_EXCL-npm split let pip ignore an
        # npm-created lockfile and run concurrently).
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        (self.home / LOCK_NAME).write_text("")                       # a held lock = the file exists
        code, err = self._update()                                   # pip
        self.assertNotEqual(code, 0, "pip must see a pre-existing lockfile (not just a pip-held flock)")
        self.assertIn("update_in_progress", err)
        if shutil.which("node"):
            env = dict(os.environ); env.update(self._env())
            r = subprocess.run(["node", str(CLI_JS), "update", "--global"],
                               capture_output=True, text=True, env=env)
            self.assertNotEqual(r.returncode, 0, "npm must see the same pre-existing lockfile")
            self.assertIn("update_in_progress", r.stdout + r.stderr)
        self.assertEqual((self.home / LOCK_NAME).read_text(), "",
                         "a fail-fast on a held lock does NOT remove the holder's lockfile")


# --- path validation --------------------------------------------------------

class ValidationTest(_Base):
    def test_valid_registry_path_predicate(self):                    # Must 3
        self._valid_home()
        self._make_project(self.proj)                                # proj/.add exists -> an ADD project
        nonproj = self.tmp / "plain"; nonproj.mkdir()
        bent = str(self.proj.parent / "x" / ".." / self.proj.name)   # normpath -> proj
        self.assertTrue(_installer._valid_registry_path(str(self.proj.resolve())), "a real ADD project is valid")
        self.assertTrue(_installer._valid_registry_path(bent), "a non-normalized path to the project is valid")
        self.assertFalse(_installer._valid_registry_path(str(nonproj)), "a dir without .add/ is not valid")

    def test_relative_path_aborts_loud(self):                        # Must 4 + Reject unsafe_registry_path
        self._valid_home()
        self._make_project(self.proj)
        shutil.rmtree(self.proj / ".add" / "docs")                   # sentinel
        self._set_registry("rel/proj", self.proj.resolve())
        before = (self.home / "registry.json").read_text()           # capture the exact bytes we expect intact
        code, err = self._update()
        self.assertNotEqual(code, 0)
        self.assertIn("unsafe_registry_path", err)
        self.assertEqual((self.home / "registry.json").read_text(), before, "registry left byte-intact")
        self.assertFalse((self.proj / ".add" / "docs").exists(), "the valid sibling was NOT reconciled")
        self.assertNotIn("9.9.9", self._stamp_text(), "the home was NOT re-stamped (failed before refresh)")

    def test_absolute_nonnormalized_nonproject_dropped(self):        # Must 5 (benign, not loud)
        self._valid_home()
        self._make_project(self.proj)
        gone = self.tmp / "gone-nonproject"; gone.mkdir()            # exists, NO .add/
        bent = str(self.tmp / "area" / ".." / "gone-nonproject")     # normpath -> gone
        self._set_registry(self.proj.resolve(), bent)
        code, _ = self._update()
        self.assertEqual(code, 0, "an absolute non-normalized non-project is benign (NOT unsafe_registry_path)")
        self.assertFalse((gone / ".add").exists(), "never reconciled into a dir without .add/")
        reg = self._registry()
        self.assertIn(str(self.proj.resolve()), reg, "the valid project is kept")
        self.assertNotIn(bent, reg, "the non-project entry is dropped")
        self.assertEqual(len([r for r in reg if "gone-nonproject" in r]), 0, "no gone-nonproject form survives")

    def test_absolute_nonnormalized_project_healed(self):            # Must 5 (heal)
        self._valid_home()
        self._make_project(self.proj)
        bent = str(self.proj.parent / "sub" / ".." / self.proj.name)  # normpath -> proj.resolve()
        self._set_registry(bent)
        code, _ = self._update()
        self.assertEqual(code, 0)
        reg = self._registry()
        self.assertIn(str(self.proj.resolve()), reg, "registry healed to the normalized project path")
        self.assertNotIn(bent, reg, "the ../-containing form is gone")

    def test_existing_nonproject_dropped(self):                      # Must 5
        self._valid_home()
        self._make_project(self.proj)
        plain = self.tmp / "plain"; plain.mkdir()                    # exists, no .add/
        self._set_registry(self.proj.resolve(), plain.resolve())
        code, _ = self._update()
        self.assertEqual(code, 0)
        self.assertFalse((plain / ".add").exists(), "no .add/ created in the non-project dir")
        reg = self._registry()
        self.assertIn(str(self.proj.resolve()), reg)
        self.assertNotIn(str(plain.resolve()), reg, "the non-project dir is dropped from the registry")


# --- preserved behavior -----------------------------------------------------

class PreservedTest(_Base):
    def test_vanished_pruned(self):                                  # Must 6 (preserved)
        self._valid_home()
        self._make_project(self.proj)
        gone = self.tmp / "vanished"                                 # absolute, never created
        self._set_registry(self.proj.resolve(), str(gone))
        code, _ = self._update()
        self.assertEqual(code, 0)
        reg = self._registry()
        self.assertIn(str(self.proj.resolve()), reg)
        self.assertNotIn(str(gone), reg, "a vanished registered path is pruned")

    def test_corrupt_registry_loud(self):                            # Must 6 + Reject registry_corrupt
        self._valid_home()
        (self.home / "registry.json").write_text("}{ not json")
        code, err = self._update()
        self.assertNotEqual(code, 0)
        self.assertIn("registry_corrupt", err)
        self.assertEqual((self.home / "registry.json").read_text(), "}{ not json",
                         "a corrupt registry is left byte-intact")

    def test_no_home_fails(self):                                    # Reject no_global_home
        code, err = self._update()                                   # home never stamped
        self.assertNotEqual(code, 0)
        self.assertIn("no_global_home", err)

    def test_lockfile_never_leaks(self):                             # INV / Must 5
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        self._update()
        leaks = list((self.proj / ".add").rglob(LOCK_NAME))
        self.assertEqual(leaks, [], "the home lockfile never lands inside a reconciled project")
        self.assertFalse(_installer._is_user_data(LOCK_NAME),
                         "the lockfile name is not classified as user-data (never snapshotted)")


# --- npm / pip parity -------------------------------------------------------

class ParityHardenTest(_Base):
    def test_parity_surface(self):                                   # Must 7 (structural — call-sites, not just defs)
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        self.assertIn("def _update_lock(", py, "_installer.py must define the lock helper")
        self.assertIn("def _valid_registry_path(", py, "_installer.py must define the path validator")
        self.assertIn("with _update_lock(home):", py, "_update_global must run UNDER the lock (call-site, not just a def)")
        self.assertIn("O_EXCL", py, "the pip lock must be the O_EXCL lockfile (cross-twin compatible)")
        for token in ("update_in_progress", "unsafe_registry_path"):
            self.assertIn(token, py)
        # npm twin: the lock is actually ACQUIRED in cmdUpdateGlobal (not merely defined), via O_EXCL ("wx").
        self.assertIn("acquireUpdateLock(home)", js, "cmdUpdateGlobal must acquire the lock (call-site)")
        self.assertIn('openSync(lockPath, "wx")', js, "the npm lock must be the O_EXCL lockfile (wx flag)")
        for token in ("update.lock", "update_in_progress", "unsafe_registry_path", "validRegistryPath(np)"):
            self.assertIn(token, js, f"cli.js must carry the {token} surface")

    def test_npm_relative_path_rejected(self):                       # Must 7 (behavioral smoke)
        if not shutil.which("node"):
            self.skipTest("node not available")
        # stamp the home + make proj a project via the pip installer, then poison the registry
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry("rel/proj", self.proj.resolve())
        env = dict(os.environ); env.update(self._env())
        r = subprocess.run(["node", str(CLI_JS), "update", "--global"],
                           capture_output=True, text=True, env=env)
        self.assertNotEqual(r.returncode, 0, "cli.js must reject a relative registry path")
        self.assertIn("unsafe_registry_path", (r.stdout + r.stderr))


if __name__ == "__main__":
    unittest.main(verbosity=2)
