#!/usr/bin/env python3
"""Tests for prune-data-update-lock (Prune-Data / Update-Global Lock Race).

FROZEN @ v1: `prune-data`/`prune_data`/`cmdPruneData` now acquire the SAME existing home lock
(`_update_lock`/`acquireUpdateLock`) `update --global` already holds during its own reconcile —
serializing the two so `prune-data` can never rmtree a project's `<home>/data/<key>` snapshot
while `update --global` is mid-refreshing it. Reuses the proven lock verbatim: no new lock file,
no new staleness threshold, no new poll mode (fail-fast only, mirrors `acquireProjectLock`'s own
no-poll philosophy for admin-class commands). A contended run fails with the EXISTING
"update_in_progress" message, byte-identical to `update --global`'s own contention text.

RED until `prune_data`/`cmdPruneData` acquire the lock — red for the right reason (a held lock
never blocking prune-data, i.e. no BlockingIOError / no "update_in_progress" raised).

Run: python3 -m unittest test_prune_data_lock -v
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
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


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="prunelock-")).resolve()
        self.home = self.tmp / "home"
        self.home.mkdir(parents=True)
        self.userhome = self.tmp / "user"; self.userhome.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self, **extra):
        env = {"ADD_HOME": str(self.home), "HOME": str(self.userhome)}
        env.update(extra)
        return env

    def _stamp_home(self):
        (self.home / _installer.STAMP_FILE).write_text("9.9.9\n", encoding="utf-8")

    def _hold_lock(self, age_seconds=None):
        """Simulate a live (or, with age_seconds, stale) lock holder directly."""
        fd = os.open(str(self.home / LOCK_NAME), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        if age_seconds is not None:
            ts = time.time() - age_seconds
            os.close(fd)
            os.utime(str(self.home / LOCK_NAME), (ts, ts))
            return None
        return fd

    def _release(self, fd):
        if fd is not None:
            os.close(fd)
        try:
            os.unlink(str(self.home / LOCK_NAME))
        except OSError:
            pass

    def _prune_data(self, *, force=False, env_extra=None):
        env = self._env(**(env_extra or {}))
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            code = _installer.prune_data(force=force, env=env)
        return code, buf.getvalue()


class BlockedByLiveUpdateGlobalTest(_Base):
    def test_prune_data_blocked_by_live_update_global(self):   # M1
        self._stamp_home()
        fd = self._hold_lock()
        try:
            code, err = self._prune_data(force=True)
            self.assertTrue((self.home / LOCK_NAME).exists(),
                            "the ORIGINAL holder's lock is untouched by the blocked prune-data")
        finally:
            self._release(fd)
        self.assertNotEqual(code, 0, "prune-data must fail while the home lock is live-held")
        self.assertIn("update_in_progress", err)


class UncontendedRegressionTest(_Base):
    def test_prune_data_proceeds_when_uncontended(self):   # M4
        self._stamp_home()
        # an unregistered orphan snapshot dir under <home>/data
        orphan = self.home / "data" / "orphankey"
        orphan.mkdir(parents=True)
        (orphan / "PROJECT.md").write_text("x\n", encoding="utf-8")
        code, err = self._prune_data(force=True)
        self.assertEqual(code, 0, err)
        self.assertFalse(orphan.exists(), "the orphan is removed exactly as before this fix")
        self.assertFalse((self.home / LOCK_NAME).exists(), "the lock is released after")


class StaleLockSelfHealTest(_Base):
    def test_prune_data_reclaims_stale_lock(self):   # M3
        self._stamp_home()
        self._hold_lock(age_seconds=10000)   # far past any staleAfterMs
        code, err = self._prune_data(force=False, env_extra={"ADD_LOCK_STALE_SECONDS": "1"})
        self.assertEqual(code, 0, err)
        self.assertFalse((self.home / LOCK_NAME).exists(),
                        "prune-data reclaimed the stale lock and released it again")


class ConcurrentPruneDataSerializeTest(_Base):
    def test_concurrent_prune_data_runs_serialize(self):   # M1 (extension)
        self._stamp_home()
        orphan = self.home / "data" / "orphankey"
        orphan.mkdir(parents=True)

        entered = threading.Event()
        release_first = threading.Event()
        results = []

        real_prune_data = _installer._prune_data

        def slow_prune_data(home, *, force):
            entered.set()
            release_first.wait(timeout=5)
            return real_prune_data(home, force=force)

        _installer._prune_data = slow_prune_data
        try:
            t = threading.Thread(target=lambda: results.append(self._prune_data(force=True)))
            t.start()
            self.assertTrue(entered.wait(timeout=5), "setup: first run entered its critical section")
            code2, err2 = self._prune_data(force=True)   # second run, lock should be held by the first
            release_first.set()
            t.join(timeout=5)
        finally:
            _installer._prune_data = real_prune_data

        self.assertNotEqual(code2, 0, "a second concurrent prune-data must fail fast, not race")
        self.assertIn("update_in_progress", err2)
        self.assertEqual(results[0][0], 0, "the first run completes normally once unblocked")


class NoNewLockFileTest(unittest.TestCase):
    def test_no_new_lock_file_introduced(self):   # R2
        import inspect
        py_src = inspect.getsource(_installer.prune_data)
        self.assertIn("_update_lock", py_src,
                     "prune_data must acquire the EXISTING _update_lock, not a new primitive")
        self.assertNotRegex(py_src, r'_prune_data_lock|PRUNE_LOCK|prune\.lock',
                            "no new, prune-data-specific lock file/constant may be introduced")

        js = CLI_JS.read_text(encoding="utf-8")
        prune_start = js.index("function cmdPruneData(")
        prune_end = js.index("\n}\n", prune_start)
        prune_fn = js[prune_start:prune_end]
        self.assertIn("acquireUpdateLock", prune_fn,
                     "cmdPruneData must acquire the EXISTING acquireUpdateLock, not a new primitive")
        self.assertNotRegex(prune_fn, r'PRUNE_LOCK|prune\.lock',
                            "no new, prune-data-specific lock file/constant may be introduced")


class NpmParityTest(_Base):
    def test_npm_prune_data_blocked_by_live_update_lock(self):
        if not shutil.which("node"):
            self.skipTest("node not available")
        self._stamp_home()
        fd = self._hold_lock()
        try:
            env = dict(os.environ); env.update(self._env())
            r = subprocess.run(["node", str(CLI_JS), "prune-data", "--force"],
                               capture_output=True, text=True, env=env, timeout=30)
        finally:
            self._release(fd)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("update_in_progress", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
