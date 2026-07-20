#!/usr/bin/env python3
"""Tests for project-scope-install-lock (install-update-hardening · project-scope-install-lock).

FROZEN @ v1: a NEW, independent per-project-scope lock serializes concurrent install()/cmdInit
and update()/cmdUpdate (non-`--global` path) against the SAME target's own `.add/` tree.
  - _project_lock(add_dir, *, env=None) / acquireProjectLock(addDir, env=process.env): an
    O_EXCL ("wx") sentinel lockfile at <target>/.add/.install.lock — mirrors (but never calls
    into or shares code with) the existing _update_lock/acquireUpdateLock home lock. Different
    function, different file, different default threshold, zero shared code (deliberate).
  - Held + fresh -> "install_in_progress" IMMEDIATELY (no wait, no poll — UNLIKE _update_lock,
    this lock has NO --lock-timeout mode: a live contention never waits, never polls). Held +
    stale (age > ADD_PROJECT_LOCK_STALE_SECONDS, env-overridable, default 120s) -> self-heals
    (unlink + retry the create EXACTLY once). A future/bogus mtime is NEVER treated as stale.
  - install()/cmdInit hold the lock across the WHOLE call (including the as_global sub-block,
    keyed on the FINAL post-interactive-prompt target, not the initial argument); update()/
    cmdUpdate (non-`--global`) hold it from right after the "no ADD project" precondition
    through the end (including the same-version no-op). cmdUpdate's `--check` stays BEFORE the
    lock (JS-only carve-out; Python's update() never sees --check at all).
  - The lock file's exact name is added to _DATA_EXCLUDE/DATA_EXCLUDE so a --global-data persist
    snapshot never captures it, even though it is live on disk during that same locked call.
  - INV (M11): a project-scope lock is ALWAYS acquired BEFORE, never nested inside, the
    home-scoped lock for the SAME call — install(as_global=True)'s EXISTING _update_lock wrap
    (global-lock-followups, merged) sits INSIDE this task's own whole-function project-lock
    wrap. LockOrderingInvariantTest proves this by REAL execution, not a static source read.

Fully hermetic: a synthetic bundled fixture (skill/tooling) + tmp targets; ADD_HOME/HOME
injected via `env=` for the --global-touching scenarios. npm parity is structural (call-sites,
not just defs) + real `node cli.js` subprocess smokes on contention + self-heal.

RED until _project_lock / acquireProjectLock / PROJECT_LOCK_FILE exist — red for the right
reason (an AttributeError on the new _installer.* symbols, or an assertion that the OLD,
lock-less install()/update() ignores a held/stale lockfile it doesn't yet know about — never a
broken harness/import error).

Run: python3 -m unittest test_project_scope_lock -v
"""
import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
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

PROJECT_LOCK_NAME = ".install.lock"     # the frozen §3 CONTRACT literal — used directly so these
                                         # helpers work whether or not _installer.PROJECT_LOCK_FILE
                                         # exists yet (mirrors test_global_update_harden.py's own
                                         # LOCK_NAME convention).
HOME_LOCK_NAME = ".update.lock"          # the EXISTING, unrelated home lock (global-lock-followups)


def _make_bundled(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    return root


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="plock-")).resolve()
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.home = self.tmp / "home"
        self.userhome = self.tmp / "user"; self.userhome.mkdir()
        self.proj = self.tmp / "proj"; self.proj.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self, **extra):
        env = {"ADD_HOME": str(self.home), "HOME": str(self.userhome)}
        env.update(extra)
        return env

    def _install(self, target, *, env_extra=None, **kw):
        """A real, hermetic install() call; returns (code, stderr_text)."""
        env = self._env(**(env_extra or {}))
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            code = _installer.install(target=str(target), bundled=str(self.bundled),
                                      non_interactive=True, env=env, **kw)
        return code, buf.getvalue()

    def _update(self, target, *, env_extra=None, **kw):
        """A real, hermetic update() call; returns (code, stderr_text)."""
        env = self._env(**(env_extra or {}))
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            code = _installer.update(target=str(target), bundled=str(self.bundled), env=env, **kw)
        return code, buf.getvalue()

    def _make_project(self, p: Path):
        """Install p as a real ADD project (creates p/.add/tooling etc)."""
        p.mkdir(parents=True, exist_ok=True)
        code, err = self._install(p)
        self.assertEqual(code, 0, f"setup: install {p.name} failed: {err}")

    def _add_dir(self, target: Path) -> Path:
        return target / ".add"

    def _hold_project_lock(self, target: Path):
        """Simulate a concurrent holder by EXCLUSIVELY creating the lockfile directly."""
        add_dir = self._add_dir(target)
        add_dir.mkdir(parents=True, exist_ok=True)
        return os.open(str(add_dir / PROJECT_LOCK_NAME), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)

    def _release_project_lock(self, fd, target: Path):
        os.close(fd)
        try:
            os.unlink(str(self._add_dir(target) / PROJECT_LOCK_NAME))
        except OSError:
            pass

    def _hold_home_lock(self):
        self.home.mkdir(parents=True, exist_ok=True)
        return os.open(str(self.home / HOME_LOCK_NAME), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)

    def _release_home_lock(self, fd):
        os.close(fd)
        try:
            os.unlink(str(self.home / HOME_LOCK_NAME))
        except OSError:
            pass

    def _write_project_lock(self, target: Path, *, age_seconds, content=""):
        """Drop a lockfile directly (bypassing the real acquire path), backdating (or, for a
        negative age, FUTURE-dating) its mtime — the sole staleness signal."""
        add_dir = self._add_dir(target)
        add_dir.mkdir(parents=True, exist_ok=True)
        lock_path = add_dir / PROJECT_LOCK_NAME
        lock_path.write_text(content)
        ts = time.time() - age_seconds
        os.utime(str(lock_path), (ts, ts))
        return lock_path


# --- baseline / M1 ----------------------------------------------------------

class FreshInstallTest(_Base):
    def test_fresh_uncontended_install_releases_lock_transparently(self):   # Scenario 1, M1
        code, err = self._install(self.proj)
        self.assertEqual(code, 0, err)
        self.assertTrue((self.proj / ".add" / "tooling").exists(), "the managed layer landed")
        self.assertFalse((self.proj / ".add" / PROJECT_LOCK_NAME).exists(),
                         ".install.lock does not exist once the call returns")


# --- concurrent install()/update() racing -----------------------------------

class ConcurrentInstallTest(_Base):
    def test_two_concurrent_installs_one_proceeds_one_fails_cleanly(self):   # Scenario 2, M1/M4/Reject
        fd = self._hold_project_lock(self.proj)
        try:
            code, err = self._install(self.proj)
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertNotEqual(code, 0, "the second install fails while the lock is held")
        self.assertIn("install_in_progress", err)
        self.assertFalse((self.proj / ".add" / "tooling").exists(),
                         "nothing was written while the lock was held — no interleaved mix is "
                         "even possible since the blocked writer never wrote anything")
        code2, err2 = self._install(self.proj)               # free now — a fresh call proceeds
        self.assertEqual(code2, 0, err2)
        self.assertTrue((self.proj / ".add" / "tooling").exists())


class ConcurrentUpdateTest(_Base):
    def test_two_concurrent_updates_one_proceeds_one_fails_cleanly(self):   # Scenario 3, M2/M4/Reject
        self._make_project(self.proj)
        (self.proj / ".add" / "tooling" / "add.py").unlink()  # sentinel: reconcile would restore it
        fd = self._hold_project_lock(self.proj)
        try:
            code, err = self._update(self.proj)
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertNotEqual(code, 0, "the second update fails while the lock is held")
        self.assertIn("install_in_progress", err)
        self.assertFalse((self.proj / ".add" / "tooling" / "add.py").exists(), "nothing reconciled while locked")
        code2, err2 = self._update(self.proj)
        self.assertEqual(code2, 0, err2)
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(), "the second, unlocked update reconciles")


# --- the lock keys on the FINAL, post-prompt target -------------------------

class TargetPromptRedirectTest(_Base):
    def test_lock_keys_on_final_post_prompt_target_not_initial_arg(self):   # Scenario 4
        x = self.tmp / "x"; x.mkdir()
        y = self.tmp / "y"; y.mkdir()
        env = self._env()

        def _run(target):
            with mock.patch.dict(os.environ, {"ADD_INSTALLER_FORCE_INTERACTIVE": "1"}), \
                 mock.patch.object(_installer, "_prompt_target", return_value=y), \
                 mock.patch.object(_installer, "_prompt_scope", return_value=False), \
                 mock.patch.object(_installer, "_prompt_intent", return_value=""):
                buf = io.StringIO()
                with contextlib.redirect_stderr(buf):
                    code = _installer.install(target=str(target), bundled=str(self.bundled), env=env)
                return code, buf.getvalue()

        code, err = _run(x)
        self.assertEqual(code, 0, err)
        self.assertTrue((y / ".add" / "tooling").exists(), "installed into Y, the FINAL prompted target")
        self.assertFalse((x / ".add").exists(), "X, the initial argument, was never touched")
        self.assertFalse((y / ".add" / PROJECT_LOCK_NAME).exists())

        # a second call (also redirected to Y) correctly contends when Y — not X — is locked
        fd = self._hold_project_lock(y)
        try:
            code2, err2 = _run(x)
        finally:
            self._release_project_lock(fd, y)
        self.assertNotEqual(code2, 0, "a call redirected to the SAME final target Y correctly contends")
        self.assertIn("install_in_progress", err2)

        # and holding X (never the real target) must NOT block a call that redirects to Y
        fd_x = self._hold_project_lock(x)
        try:
            code3, err3 = _run(x)
        finally:
            self._release_project_lock(fd_x, x)
        self.assertEqual(code3, 0, f"locking X must never block a call keyed on Y: {err3}")


# --- install --global still locks the per-project drop ---------------------

class InstallGlobalLockTest(_Base):
    def test_install_global_still_locks_the_per_project_drop(self):   # Scenario 5, M1
        code, err = self._install(self.proj, as_global=True)
        self.assertEqual(code, 0, err)
        self.assertTrue((self.proj / ".add" / "tooling").exists(), "the per-project drop still ran")
        self.assertFalse((self.proj / ".add" / PROJECT_LOCK_NAME).exists())
        self.assertFalse((self.home / HOME_LOCK_NAME).exists())

        fd = self._hold_project_lock(self.proj)
        try:
            code2, err2 = self._install(self.proj, as_global=True)
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertNotEqual(code2, 0, "a 2nd install --global on the SAME target contends on the "
                                       "PROJECT lock, not merely racing the home")
        self.assertIn("install_in_progress", err2)
        reg = _installer._read_registry(self.home)
        self.assertEqual(reg.count(str(self.proj.resolve())), 1, "registered exactly once — the "
                         "blocked 2nd call never re-touched the registry")


# --- update()'s same-version no-op is ALSO serialized -----------------------

class UpdateNoOpRelockTest(_Base):
    def test_update_same_version_noop_is_locked_and_rechecked_fresh(self):   # Scenario 6, M2
        self._make_project(self.proj)
        fd = self._hold_project_lock(self.proj)
        try:
            code, err = self._update(self.proj)
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertNotEqual(code, 0, "even the same-version no-op path is locked")
        self.assertIn("install_in_progress", err)

        code2, err2 = self._update(self.proj)     # same version, nothing missing -> a FRESH no-op
        self.assertEqual(code2, 0, err2)
        self.assertFalse((self.proj / ".add" / PROJECT_LOCK_NAME).exists(),
                         "the lock is released even on the no-op fast-path return")


# --- update --global / --check are unaffected by the (different) project lock

class GlobalAndCheckUnaffectedTest(_Base):
    def test_update_global_unaffected_by_a_held_project_lock(self):   # Scenario 7, M2 boundary
        code0, err0 = self._install(self.proj, as_global=True)    # stamps home + registers proj
        self.assertEqual(code0, 0, err0)
        fd = self._hold_project_lock(self.proj)
        try:
            code, err = self._update(self.proj, as_global=True)
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertEqual(code, 0, f"update --global touches a DIFFERENT resource, unaffected: {err}")

    def test_npm_check_unaffected_by_a_held_project_lock(self):   # Scenario 7, M3 JS-only carve-out
        if not shutil.which("node"):
            self.skipTest("node not available")
        env = dict(os.environ); env.update(self._env())
        r0 = subprocess.run(["node", str(CLI_JS), "init", str(self.proj), "--yes"],
                            capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(r0.returncode, 0, r0.stderr)
        fd = self._hold_project_lock(self.proj)
        try:
            r = subprocess.run(["node", str(CLI_JS), "update", "--check", str(self.proj)],
                               capture_output=True, text=True, env=env, timeout=60)
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertEqual(r.returncode, 0, f"--check stays BEFORE the lock, unaffected: {r.stderr}")
        self.assertNotIn("install_in_progress", r.stdout + r.stderr)


# --- stale-lock self-heal (project scope) -----------------------------------

class StaleProjectLockSelfHealTest(_Base):
    def test_stale_project_lock_self_heals(self):   # Scenario 8, M5
        self._make_project(self.proj)
        (self.proj / ".add" / "tooling" / "add.py").unlink()
        lock_path = self._write_project_lock(self.proj, age_seconds=10)
        code, err = self._update(self.proj, env_extra={"ADD_PROJECT_LOCK_STALE_SECONDS": "1"})
        self.assertEqual(code, 0, err)
        self.assertNotIn("install_in_progress", err)
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(), "the run proceeded to completion")
        self.assertFalse(lock_path.exists(), "the reclaimed lock is released again after the run")


class LiveProjectLockTest(_Base):
    def test_live_project_lock_not_reclaimed_fails_fast(self):   # Scenario 9, M5 regression + Reject
        self._make_project(self.proj)
        lock_path = self._write_project_lock(self.proj, age_seconds=0)
        code, err = self._update(self.proj, env_extra={"ADD_PROJECT_LOCK_STALE_SECONDS": "600"})
        self.assertNotEqual(code, 0)
        self.assertIn("install_in_progress", err)
        self.assertTrue(lock_path.exists(), "the held lock is left untouched (not reclaimed)")


class FutureMtimeProjectLockTest(_Base):
    def test_future_mtime_project_lock_never_stale(self):   # Scenario 10, M5 edge (clock skew)
        self._make_project(self.proj)
        lock_path = self._write_project_lock(self.proj, age_seconds=-3600)     # an hour in the FUTURE
        code, err = self._update(self.proj, env_extra={"ADD_PROJECT_LOCK_STALE_SECONDS": "1"})
        self.assertNotEqual(code, 0, "a bogus future mtime is never treated as stale")
        self.assertIn("install_in_progress", err)
        self.assertTrue(lock_path.exists(), "a future-mtime lock is left untouched (not reclaimed)")


class EmptyStaleProjectLockTest(_Base):
    def test_crash_before_stamp_leaves_self_healable_empty_lock(self):   # Scenario 11, M6 edge
        self._make_project(self.proj)
        self._write_project_lock(self.proj, age_seconds=10, content="")   # empty + stale
        code, err = self._update(self.proj, env_extra={"ADD_PROJECT_LOCK_STALE_SECONDS": "1"})
        self.assertEqual(code, 0, err)
        self.assertNotIn("install_in_progress", err)


# --- leaked reclaim-ticket self-heal (post-freeze redo: a fresh adversarial verify pass found ---
# that a ticket file leaked by a crash mid-reclaim — created by a process that won it, then died
# before its own best-effort cleanup a few lines later — would PERMANENTLY wedge this lock: the
# ticket's name is deterministically keyed to the stale main lock's own (unchanging) inode, so
# EVERY future contender recomputes the IDENTICAL ticket path, loses the identical EEXIST race,
# and (this lock never polls/waits — M7) fails "install_in_progress" forever, with no
# --lock-timeout escape hatch to even ask for. Fix: apply the SAME age-based staleness check
# already governing the main lock to the ticket file too, with the SAME identity-verified
# (re-stat-immediately-before-unlink) discipline — never a plain unconditional unlink, which would
# reopen the identical TOCTOU hole one level down (see _installer.py:_project_lock for the full
# reasoning). Independent of, not shared with, this file's own JS/`_update_lock` twins' tests.

class LeakedTicketWedgeTest(_Base):
    def _leak_ticket(self, lock_path: Path, *, ticket_age_seconds):
        """Simulate a crash that WON the per-generation reclaim ticket but never cleaned it up
        (died between the ticket-open and its own `finally: unlink` a few lines later): an
        orphaned ticket file at the EXACT deterministic path a real reclaimer would compute
        (keyed to `lock_path`'s own current inode), with no corresponding live process."""
        ino = lock_path.stat().st_ino
        ticket_path = lock_path.with_name(lock_path.name + f".reclaim-{ino}")
        ticket_path.write_text("")
        ts = time.time() - ticket_age_seconds
        os.utime(str(ticket_path), (ts, ts))
        return ticket_path

    def test_leaked_ticket_self_heals_instead_of_permanent_wedge(self):
        self._make_project(self.proj)
        (self.proj / ".add" / "tooling" / "add.py").unlink()  # sentinel: reconcile would restore it
        lock_path = self._write_project_lock(self.proj, age_seconds=1000)      # very stale
        ticket_path = self._leak_ticket(lock_path, ticket_age_seconds=1000)    # leaked long ago too
        code, err = self._update(self.proj, env_extra={"ADD_PROJECT_LOCK_STALE_SECONDS": "1"})
        self.assertEqual(code, 0, f"a leaked ticket must self-heal, not wedge permanently: {err}")
        self.assertNotIn("install_in_progress", err)
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(), "the run proceeded to completion")
        self.assertFalse(lock_path.exists(), "the reclaimed lock is released again after the run")
        self.assertFalse(ticket_path.exists(), "the leaked ticket itself is cleaned up too — "
                         "no residue left to re-wedge a future call")

    def test_project_lock_direct_leaked_ticket_self_heals(self):
        # mechanism-level proof, bypassing install()/update() entirely: a bare _project_lock()
        # call against a leaked-ticket state must acquire cleanly (no BlockingIOError), not
        # reproduce "install_in_progress" — the exact call shape a fresh adversarial verify pass
        # used to find and confirm this defect against the unmodified code.
        add_dir = self._add_dir(self.proj)
        add_dir.mkdir(parents=True, exist_ok=True)
        lock_path = add_dir / PROJECT_LOCK_NAME
        lock_path.write_text("")
        ts = time.time() - 1000
        os.utime(str(lock_path), (ts, ts))
        self._leak_ticket(lock_path, ticket_age_seconds=1000)
        env = self._env()
        env["ADD_PROJECT_LOCK_STALE_SECONDS"] = "1"
        with _installer._project_lock(add_dir, env=env):
            pass   # must not raise BlockingIOError
        self.assertFalse(lock_path.exists(), "released cleanly after a successful self-heal")

    def test_fresh_ticket_is_never_reclaimed_no_new_hole_introduced(self):
        # A ticket that is NOT yet stale (a genuine, still-in-flight reclaimer) must still be
        # treated as live — fail fast, no reclaim attempt — so THIS fix does not itself become a
        # NEW TOCTOU hole one level down (a too-eager ticket reclaim could let a second party
        # destroy a legitimate in-flight reclaimer's fresh ticket, reintroducing the exact
        # double-hold bug the ticket mechanism was built to prevent — see _installer.py's own
        # reasoning). Regression guard for the identity-verified discipline, not just the fix.
        self._make_project(self.proj)
        lock_path = self._write_project_lock(self.proj, age_seconds=1000)
        ticket_path = self._leak_ticket(lock_path, ticket_age_seconds=0)   # "just created" — fresh
        code, err = self._update(self.proj, env_extra={"ADD_PROJECT_LOCK_STALE_SECONDS": "1"})
        self.assertNotEqual(code, 0, "a fresh (not-yet-stale) ticket is treated as a live, "
                             "legitimate in-flight reclaimer — fail fast, never reclaimed")
        self.assertIn("install_in_progress", err)
        self.assertTrue(ticket_path.exists(), "a fresh ticket is left completely untouched")
        self.assertTrue(lock_path.exists(), "the main (stale) lock is untouched too — the ticket "
                         "contention was never won, so the main lock's own reclaim never even ran")

    def test_npm_leaked_ticket_self_heals_instead_of_permanent_wedge(self):
        if not shutil.which("node"):
            self.skipTest("node not available")
        lock_path = self._write_project_lock(self.proj, age_seconds=1000)
        ticket_path = self._leak_ticket(lock_path, ticket_age_seconds=1000)
        env = dict(os.environ); env.update(self._env())
        env["ADD_PROJECT_LOCK_STALE_SECONDS"] = "1"
        r = subprocess.run(["node", str(CLI_JS), "init", str(self.proj), "--yes"],
                           capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(r.returncode, 0, f"a leaked ticket must self-heal, not wedge: {r.stderr}")
        self.assertNotIn("install_in_progress", r.stdout + r.stderr)
        self.assertFalse(lock_path.exists())
        self.assertFalse(ticket_path.exists())


# --- the lock file is excluded from a --global-data persist snapshot --------

class DataExcludeLockFileTest(_Base):
    def test_is_user_data_excludes_the_project_lock_by_name(self):   # Scenario 12, M8 (direct)
        self.assertFalse(_installer._is_user_data(_installer.PROJECT_LOCK_FILE))

    def test_lock_file_excluded_from_a_global_data_persist_snapshot(self):   # Scenario 12, M8 (e2e)
        self._make_project(self.proj)
        (self.proj / ".add" / "PROJECT.md").write_text("hello\n")   # real user-data to persist
        code, err = self._install(self.proj, as_global_data=True)
        self.assertEqual(code, 0, err)
        key = _installer.data_key(str(self.proj.resolve()))
        snap_dir = self.home / "data" / key
        self.assertTrue(snap_dir.exists())
        names = {p.name for p in snap_dir.iterdir()}
        self.assertIn("PROJECT.md", names)
        self.assertNotIn(_installer.PROJECT_LOCK_FILE, names,
                         "the lock file — live on disk during the SAME locked call's own "
                         "persist scan — is never snapshotted as user-data")


# --- both twins guarantee the same observable behavior ----------------------

class TwinParityTest(_Base):
    def test_parity_surface(self):   # Scenario 13, M9 (structural — call-sites, not just defs)
        py_src = Path(_installer.__file__).read_text(encoding="utf-8")
        js_src = CLI_JS.read_text(encoding="utf-8")
        self.assertIn("def _project_lock(", py_src, "_installer.py must define the project lock")
        self.assertIn("function acquireProjectLock(", js_src, "cli.js must define the JS twin")
        self.assertEqual(_installer.PROJECT_LOCK_FILE, ".install.lock")
        self.assertIn(_installer.PROJECT_LOCK_FILE, _installer._DATA_EXCLUDE,
                     "the lock file's exact name must be excluded from user-data scans")
        m = re.search(r"const DATA_EXCLUDE = \[[^\]]*\]", js_src)
        self.assertIsNotNone(m, "DATA_EXCLUDE array literal must be present")
        self.assertIn("PROJECT_LOCK_FILE", m.group(0), "cli.js's DATA_EXCLUDE must carry it too")
        self.assertEqual(py_src.count("with _project_lock(add_dir, env=env_map):"), 2,
                         "both install() and update() must share the identical call site")
        self.assertEqual(js_src.count("acquireProjectLock(addDir)"), 2,
                         "both cmdInit and cmdUpdate must share the identical call site")
        self.assertIn("install_in_progress", py_src)
        self.assertIn("install_in_progress", js_src)
        self.assertIn("O_EXCL", py_src)
        self.assertIn('openSync(lockPath, "wx")', js_src)

    def test_npm_fresh_install_unaffected(self):   # Scenario 13 (regression, uncontended)
        if not shutil.which("node"):
            self.skipTest("node not available")
        env = dict(os.environ); env.update(self._env())
        r = subprocess.run(["node", str(CLI_JS), "init", str(self.proj), "--yes"],
                           capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.proj / ".add" / "tooling").exists())
        self.assertFalse((self.proj / ".add" / PROJECT_LOCK_NAME).exists())

    def test_npm_contended_install_fails_fast(self):   # Scenario 13, behavioral
        if not shutil.which("node"):
            self.skipTest("node not available")
        env = dict(os.environ); env.update(self._env())
        fd = self._hold_project_lock(self.proj)
        try:
            r = subprocess.run(["node", str(CLI_JS), "init", str(self.proj), "--yes"],
                               capture_output=True, text=True, env=env, timeout=60)
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("install_in_progress", r.stdout + r.stderr)
        self.assertFalse((self.proj / ".add" / "tooling").exists(), "nothing written while contended")

    def test_npm_stale_project_lock_self_heals(self):   # Scenario 13, behavioral (self-heal parity)
        if not shutil.which("node"):
            self.skipTest("node not available")
        self._write_project_lock(self.proj, age_seconds=10)
        env = dict(os.environ); env.update(self._env())
        env["ADD_PROJECT_LOCK_STALE_SECONDS"] = "1"
        r = subprocess.run(["node", str(CLI_JS), "init", str(self.proj), "--yes"],
                           capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("install_in_progress", r.stdout + r.stderr)
        self.assertTrue((self.proj / ".add" / "tooling").exists())


# --- composes with, never duplicates, _clean_replace's own crash-safety ----

class ComposesWithCleanReplaceTest(_Base):
    def test_lock_release_is_independent_of_a_reconcile_crash(self):   # Scenario 14
        with mock.patch.object(_installer, "_reconcile",
                              side_effect=RuntimeError("simulated mid-copy crash")):
            with self.assertRaises(RuntimeError):
                self._install(self.proj)
        self.assertFalse((self.proj / ".add" / PROJECT_LOCK_NAME).exists(),
                         "the project lock releases even when _reconcile (which drives "
                         "_clean_replace) raises mid-call — the two guarantees are independent")
        code, err = self._install(self.proj)          # a SUBSEQUENT call is not wedged
        self.assertEqual(code, 0, err)


# --- no bounded wait: contention always fails immediately -------------------

class NoBoundedWaitTest(_Base):
    def test_contention_always_fails_immediately_never_polls(self):   # Scenario 15, M7
        self._make_project(self.proj)
        fd = self._hold_project_lock(self.proj)
        try:
            start = time.monotonic()
            code, err = self._update(self.proj)
            elapsed = time.monotonic() - start
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertNotEqual(code, 0)
        self.assertIn("install_in_progress", err)
        self.assertLess(elapsed, 1.0, "no --lock-timeout mode exists — contention never waits/polls")


# --- every other touched function stays byte-identical ----------------------

class ByteIdenticalRegressionTest(_Base):
    def test_untouched_lock_and_reconcile_call_sites_are_unchanged(self):   # Scenario 16, M10
        py_src = Path(_installer.__file__).read_text(encoding="utf-8")
        js_src = CLI_JS.read_text(encoding="utf-8")
        self.assertEqual(py_src.count("with _update_lock(home, timeout=lock_timeout, env=env_map):"), 2,
                         "the EXISTING global-lock call sites must be untouched by this task")
        self.assertEqual(js_src.count('acquireUpdateLock(home, { timeout: args.lockTimeout }, process.env)'), 2)
        self.assertIn("_reconcile(target_path, bundled_root)", py_src)
        self.assertIn("reconcile(args, target)", js_src)

    def test_is_user_data_baseline_and_new_exclusion(self):   # Scenario 16, M10 (behavioral)
        self.assertTrue(_installer._is_user_data("PROJECT.md"), "ordinary user-data unaffected")
        self.assertFalse(_installer._is_user_data(".update.lock"), "the EXISTING exclusion unaffected")
        self.assertFalse(_installer._is_user_data(".install.lock"), "the NEW exclusion this task adds")
        self.assertFalse(_installer._is_user_data(".install.lock.reclaim-123456"),
                         "a leaked project-lock reclaim-ticket sibling is never bogusly "
                         "snapshotted as user-data (leaked-ticket wedge fix)")


# --- M11: a project-scope lock is ALWAYS acquired BEFORE, never nested ------
# inside, any home-scoped lock acquisition for the same call. Not one of the 16 named §2
# scenarios verbatim — required explicitly by this task's own §0 Issue/Risk #5 and §3's own
# INV block, proven here by REAL execution (install(as_global=True) with both locks live),
# never by a static re-read of the source.

class LockOrderingInvariantTest(_Base):
    def test_project_lock_blocks_before_the_home_lock_is_ever_touched(self):
        fd = self._hold_project_lock(self.proj)
        try:
            code, err = self._install(self.proj, as_global=True)
        finally:
            self._release_project_lock(fd, self.proj)
        self.assertNotEqual(code, 0)
        self.assertIn("install_in_progress", err, "the OUTER project lock is what contends first")
        self.assertNotIn("update_in_progress", err, "the inner home lock was never even reached")
        self.assertFalse((self.home / HOME_LOCK_NAME).exists(), "the home lock was never created")
        self.assertFalse(_installer._stamp_path(self.home).exists(), "the home was never stamped")

    def test_home_lock_contention_surfaces_independently_when_project_lock_is_free(self):
        code0, err0 = self._install(self.proj, as_global=True)     # establish the home + register
        self.assertEqual(code0, 0, err0)
        target2 = self.tmp / "second"; target2.mkdir()
        fd = self._hold_home_lock()
        try:
            code, err = self._install(target2, as_global=True)
        finally:
            self._release_home_lock(fd)
        self.assertNotEqual(code, 0)
        self.assertIn("update_in_progress", err, "the INNER home lock's own contention surfaces")
        self.assertNotIn("install_in_progress", err, "the OUTER project lock was never contended")
        self.assertFalse((target2 / ".add" / PROJECT_LOCK_NAME).exists(),
                         "the outer project lock — acquired fine — released correctly despite "
                         "the inner (home-lock) failure, proving no deadlock and correct nesting")

    def test_fresh_install_global_releases_both_locks_no_deadlock(self):
        start = time.monotonic()
        code, err = self._install(self.proj, as_global=True)
        elapsed = time.monotonic() - start
        self.assertEqual(code, 0, err)
        self.assertLess(elapsed, 10.0, "no deadlock — the nested acquire/release completes promptly")
        self.assertFalse((self.proj / ".add" / PROJECT_LOCK_NAME).exists())
        self.assertFalse((self.home / HOME_LOCK_NAME).exists())


# --- bonus defensive coverage: TOCTOU-safe reclaim under real thread races --
# Beyond the 16 named scenarios + M11 — mirrors global-lock-followups' own
# test_concurrent_stale_reclaim_exactly_one_wins, directly proving M4/M5's own stated
# invariant ("the O_EXCL create is the SOLE mutual-exclusion primitive... at most one racing
# create succeeds at any instant") against _project_lock specifically.

class ProjectLockConcurrencySafetyTest(_Base):
    def test_concurrent_stale_reclaim_exactly_one_wins(self):
        self._write_project_lock(self.proj, age_seconds=10)
        add_dir = self._add_dir(self.proj)
        env = self._env()
        env["ADD_PROJECT_LOCK_STALE_SECONDS"] = "8"    # reclaim-ticket-race: widened from "1" —
        # mirrors the home-lock twin's own widening; GitHub Actions failed the home-lock version
        # of this exact test twice via a real >20x scheduling blowup of a 0.05s hold under CI
        # load. "8" keeps the same test-only-override intent (well under the 10s backdated age)
        # while giving ~160x margin — test-realism fix, not a prod change (prod default: 120s).
        results = []
        results_lock = threading.Lock()
        barrier = threading.Barrier(6)
        # TEMPORAL (not cumulative) proof of "at most one racing create succeeds at any
        # instant" (§3 CONTRACT INV / §1 M5): `active` is incremented the instant a racer is
        # INSIDE the critical section and decremented the instant before it leaves; `peak`
        # latches the highest value `active` ever reached, across every racer, under the SAME
        # lock protecting `results`. A late-scheduled racer legitimately acquiring AFTER an
        # earlier one released is normal sequential mutual exclusion — it never bumps `peak`
        # above 1 because the earlier holder already decremented before releasing. Only a
        # genuine overlap (two racers simultaneously "inside") can push `peak` to 2+. This is
        # the real, non-flaky proof; a bare `results.count("acquired") == 1` would falsely fail
        # on correct code whenever scheduling staggers racers across the release boundary.
        active = 0
        peak = 0

        def racer():
            nonlocal active, peak
            barrier.wait()
            try:
                with _installer._project_lock(add_dir, env=env):
                    with results_lock:
                        results.append("acquired")
                        active += 1
                        peak = max(peak, active)
                    time.sleep(0.05)
                    with results_lock:
                        active -= 1
            except BlockingIOError:
                with results_lock:
                    results.append("blocked")
            except Exception as exc:            # pragma: no cover - would fail the assertions below
                with results_lock:
                    results.append(f"error:{exc!r}")

        threads = [threading.Thread(target=racer) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        errors = [r for r in results if r.startswith("error:")]
        self.assertEqual(errors, [], f"no racer hit an unexpected exception: {errors}")
        self.assertEqual(len(results), 6, "every racer reported an outcome (none hung)")
        self.assertGreaterEqual(results.count("acquired"), 1,
                                "at least one racer reclaims the stale lock and proceeds")
        self.assertLessEqual(peak, 1,
                             f"at most one racer may be INSIDE the critical section at any "
                             f"given instant (observed peak concurrent holders: {peak}) — a "
                             f"higher peak proves 2+ racers held the reclaimed lock "
                             f"simultaneously, violating mutual exclusion (TOCTOU on the "
                             f"stale-reclaim path)")
        self.assertFalse((add_dir / PROJECT_LOCK_NAME).exists(), "every acquirer released again — none leaked")

    def test_project_lock_concurrent_reclaim_survives_scheduling_delay(self):   # M4 (reclaim-ticket-race)
        """Mirrors global-lock-followups' own scheduling-delay repro (test_global_update_harden's
        test_concurrent_stale_reclaim_survives_scheduling_delay) against `_project_lock`, whose
        ticket-orphan branch shares the byte-for-byte identical create-once, never-refreshed
        shape. `_project_lock` itself has NO --lock-timeout/poll mode (Held+fresh -> immediate
        BlockingIOError, always) — so unlike the home lock, the retry that lets a sibling racer's
        stat land AFTER the delayed holder's age crosses stale_after has to live at the CALLER,
        exactly as a real retry-on-`install_in_progress` script would: this test's racers loop
        their own acquire attempts until they succeed or a generous deadline elapses, rather than
        a single one-shot call each."""
        self._write_project_lock(self.proj, age_seconds=10)
        add_dir = self._add_dir(self.proj)
        env = self._env()
        env["ADD_PROJECT_LOCK_STALE_SECONDS"] = "8"    # widened from "1" — see the sibling test's
                                                        # own comment for the CI-observed rationale

        first_holder = threading.Event()
        hold_seconds = 10      # > ADD_PROJECT_LOCK_STALE_SECONDS (8) — a live, merely-delayed holder
        retry_deadline = hold_seconds + 2
        results = []
        results_lock = threading.Lock()
        barrier = threading.Barrier(6)
        active = 0
        peak = 0

        def racer():
            nonlocal active, peak
            barrier.wait()
            start = time.monotonic()
            while True:
                try:
                    with _installer._project_lock(add_dir, env=env):
                        with results_lock:
                            results.append("acquired")
                            active += 1
                            peak = max(peak, active)
                        if not first_holder.is_set():
                            first_holder.set()
                            time.sleep(hold_seconds)
                        else:
                            time.sleep(0.05)
                        with results_lock:
                            active -= 1
                    return
                except BlockingIOError:
                    if time.monotonic() - start >= retry_deadline:
                        with results_lock:
                            results.append("blocked")
                        return
                    time.sleep(0.05)
                except Exception as exc:            # pragma: no cover - would fail the assertions below
                    with results_lock:
                        results.append(f"error:{exc!r}")
                    return

        threads = [threading.Thread(target=racer) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=retry_deadline + 5)

        errors = [r for r in results if r.startswith("error:")]
        self.assertEqual(errors, [], f"no racer hit an unexpected exception: {errors}")
        self.assertEqual(len(results), 6, "every racer reported an outcome (none hung)")
        self.assertGreaterEqual(results.count("acquired"), 1,
                                "at least one racer reclaims the stale lock and proceeds")
        self.assertLessEqual(peak, 1,
                             f"at most one racer may be INSIDE the critical section at any given "
                             f"instant even when the current holder is merely scheduler-delayed, "
                             f"not crashed (observed peak concurrent holders: {peak}) — a higher "
                             f"peak proves a sibling racer reclaimed a lock whose holder was still "
                             f"legitimately working, not dead")
        self.assertFalse((add_dir / PROJECT_LOCK_NAME).exists(),
                         "every acquirer released the lock again — none leaked")


if __name__ == "__main__":
    unittest.main(verbosity=2)
