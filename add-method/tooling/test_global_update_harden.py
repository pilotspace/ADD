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

    def _install_global(self, target, *, env_extra=None, **kw):
        """A real --global install: stamps the home AND makes <target> a registered ADD project.
        `env_extra` (additive, e.g. ADD_LOCK_STALE_SECONDS) merges over the hermetic base env."""
        env = self._env()
        if env_extra:
            env.update(env_extra)
        return _installer.install(target=str(target), bundled=str(self.bundled),
                                  non_interactive=True, env=env, as_global=True, **kw)

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

    def _update(self, *, env_extra=None, **kw):
        """Invoke `update --global`, capturing stderr; returns (code, stderr_text).
        `env_extra` (additive, e.g. ADD_LOCK_STALE_SECONDS) merges over the hermetic base env."""
        env = self._env()
        if env_extra:
            env.update(env_extra)
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                     version="9.9.9", env=env, as_global=True, **kw)
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
        self.assertFalse(_installer._is_user_data(LOCK_NAME + ".reclaim-123456"),
                         "a leaked home-lock reclaim-ticket sibling is not classified as "
                         "user-data either — inert here (the home is never scanned by "
                         "_persist_data), kept for documentation-consistency with the exact "
                         "same LOCK_FILE precedent this function already carries")


# --- npm / pip parity -------------------------------------------------------

class ParityHardenTest(_Base):
    def test_parity_surface(self):                                   # Must 7 (structural — call-sites, not just defs)
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        self.assertIn("def _update_lock(", py, "_installer.py must define the lock helper")
        self.assertIn("def _valid_registry_path(", py, "_installer.py must define the path validator")
        # v1 (global-lock-followups): _update_lock now threads timeout/env (self-heal + --lock-timeout),
        # so BOTH _update_global and install()'s as_global block share the identical, fuller call site
        # (a bare "with _update_lock(home):" no longer exists anywhere — superseded, not just present).
        self.assertIn("with _update_lock(home, timeout=lock_timeout, env=env_map):", py,
                      "_update_global AND install's as_global block must both run UNDER the lock, "
                      "threading lock_timeout (call-site, not just a def)")
        self.assertEqual(py.count("with _update_lock(home, timeout=lock_timeout, env=env_map):"), 2,
                         "both _update_global and install's as_global block share the identical call site")
        self.assertIn("O_EXCL", py, "the pip lock must be the O_EXCL lockfile (cross-twin compatible)")
        for token in ("update_in_progress", "unsafe_registry_path"):
            self.assertIn(token, py)
        # npm twin: the lock is actually ACQUIRED in cmdUpdateGlobal (not merely defined), via O_EXCL ("wx").
        # v1: acquireUpdateLock now threads { timeout } + env (self-heal + --lock-timeout), so BOTH
        # cmdUpdateGlobal and installGlobal share the identical, fuller call site.
        self.assertIn("acquireUpdateLock(home, { timeout: args.lockTimeout }, process.env)", js,
                      "cmdUpdateGlobal AND installGlobal must both acquire the lock, threading "
                      "lockTimeout (call-site, not just a def)")
        self.assertEqual(js.count("acquireUpdateLock(home, { timeout: args.lockTimeout }, process.env)"), 2,
                         "both cmdUpdateGlobal and installGlobal share the identical call site")
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

    def test_lock_timeout_flag_parity(self):                         # M5 (structural) — global-lock-followups Scenario 13
        js = CLI_JS.read_text(encoding="utf-8")
        py_cli = (_SRC / "add_method" / "_cli.py").read_text(encoding="utf-8")
        py_installer = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        # --lock-timeout parses with the SAME "requires a value" idiom as --stage/--name (JS).
        self.assertIn('a === "--lock-timeout"', js, "cli.js must parse --lock-timeout")
        # both twins thread the flag through to lock_timeout / lockTimeout.
        self.assertEqual(py_cli.count("--lock-timeout"), 2,
                         "_cli.py must register --lock-timeout on BOTH the init and update subparsers")
        self.assertIn("lock_timeout=args.lock_timeout", py_cli)
        self.assertIn("lockTimeout", js)
        # both twins support the SAME env-overridable staleness threshold.
        self.assertIn("ADD_LOCK_STALE_SECONDS", js)
        self.assertIn("ADD_LOCK_STALE_SECONDS", py_installer)

    def test_npm_stale_lock_self_heals(self):                        # M5 (behavioral smoke) — Scenario 13
        if not shutil.which("node"):
            self.skipTest("node not available")
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        lock_path = self.home / LOCK_NAME
        lock_path.write_text("")
        now = time.time()
        os.utime(str(lock_path), (now - 10, now - 10))       # 10s old
        env = dict(os.environ); env.update(self._env())
        env["ADD_LOCK_STALE_SECONDS"] = "1"                   # threshold well under the 10s age
        r = subprocess.run(["node", str(CLI_JS), "update", "--global"],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, "cli.js must self-heal a stale lock (mtime older than the threshold)")
        self.assertNotIn("update_in_progress", r.stdout + r.stderr)

    def test_npm_live_lock_still_fails_fast(self):                   # M5 (behavioral smoke) — Scenario 13
        if not shutil.which("node"):
            self.skipTest("node not available")
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        fd = os.open(str(self.home / LOCK_NAME), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            env = dict(os.environ); env.update(self._env())
            r = subprocess.run(["node", str(CLI_JS), "update", "--global"],
                               capture_output=True, text=True, env=env)
            self.assertNotEqual(r.returncode, 0, "a live (fresh) lock still fails fast — unchanged by default")
            self.assertIn("update_in_progress", r.stdout + r.stderr)
        finally:
            os.close(fd)
            try:
                os.unlink(str(self.home / LOCK_NAME))
            except OSError:
                pass


# --- stale-lock self-heal (global-lock-followups M1) ------------------------

class StaleLockSelfHealTest(_Base):
    """M1: a wedged .update.lock self-heals via mtime-AGE (never PID-liveness — see PLAN.md §0
    Honors on the Windows os.kill(pid,0) hazard); a live lock's fail-fast stays unchanged."""

    def _write_lock(self, *, age_seconds, content=""):
        """Create the lockfile directly (bypassing the real acquire path), backdating (or, for
        a negative age, FUTURE-dating) its mtime — the sole staleness signal."""
        self.home.mkdir(parents=True, exist_ok=True)
        lock_path = self.home / LOCK_NAME
        lock_path.write_text(content)
        ts = time.time() - age_seconds
        os.utime(str(lock_path), (ts, ts))
        return lock_path

    def test_stale_lock_self_heals(self):                            # M1 · Scenario 1
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        lock_path = self._write_lock(age_seconds=10)                 # 10s old, threshold 1s below -> stale
        code, err = self._update(env_extra={"ADD_LOCK_STALE_SECONDS": "1"})
        self.assertEqual(code, 0, "a stale lock self-heals and the run completes")
        self.assertNotIn("update_in_progress", err)
        self.assertFalse(lock_path.exists(), "the reclaimed lock is released again after the run")

    def test_live_lock_not_reclaimed_fails_fast(self):                # M1 regression + Reject · Scenario 2
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        lock_path = self._write_lock(age_seconds=0)                   # fresh -> well within the threshold
        code, err = self._update(env_extra={"ADD_LOCK_STALE_SECONDS": "600"})
        self.assertNotEqual(code, 0, "a live (non-stale) lock still fails fast with no --lock-timeout")
        self.assertIn("update_in_progress", err)
        self.assertTrue(lock_path.exists(), "the held lock is left untouched (not reclaimed)")

    def test_future_mtime_lock_never_stale(self):                     # M1 edge (clock skew) · Scenario 4
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        lock_path = self._write_lock(age_seconds=-3600)                # an hour in the FUTURE
        code, err = self._update(env_extra={"ADD_LOCK_STALE_SECONDS": "1"})   # a tiny threshold
        self.assertNotEqual(code, 0, "a bogus future mtime is never treated as stale")
        self.assertIn("update_in_progress", err)
        self.assertTrue(lock_path.exists(), "a future-mtime lock is left untouched (not reclaimed)")

    def test_empty_stale_lock_self_heals(self):                       # M2 edge · Scenario 5
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        self._write_lock(age_seconds=10, content="")                  # empty + stale (crash before the stamp)
        code, err = self._update(env_extra={"ADD_LOCK_STALE_SECONDS": "1"})
        self.assertEqual(code, 0, "an empty stale lock self-heals exactly like a stamped one")
        self.assertNotIn("update_in_progress", err)

    def test_concurrent_stale_reclaim_exactly_one_wins(self):         # M1 TOCTOU · Scenario 3
        self._write_lock(age_seconds=10)                              # a stale lock every racer observes
        env = self._env()
        env["ADD_LOCK_STALE_SECONDS"] = "8"    # reclaim-ticket-race: widened from "1" — GitHub
        # Actions failed this test twice with a genuine >20x real-time blowup of the 0.05s hold
        # below under CI scheduling load (confirmed via a real CI run, not inferred); "8" keeps
        # the SAME test-only-override intent (well under the 10s backdated age, so still
        # unambiguously stale) while giving ~160x margin instead of ~20x — a test-realism fix,
        # not a prod change (prod's own default is 600s) and NOT a weakening of `peak <= 1`.
        results = []
        results_lock = threading.Lock()
        barrier = threading.Barrier(6)
        # TEMPORAL (not cumulative) proof of "at most one racing create succeeds at any
        # instant" (§3 CONTRACT INV / §1 M1): `active` is incremented the instant a racer is
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
            barrier.wait()                    # start every racer as simultaneously as possible
            try:
                with _installer._update_lock(self.home, env=env):
                    with results_lock:
                        results.append("acquired")
                        active += 1
                        peak = max(peak, active)
                    time.sleep(0.05)           # hold briefly so an overlap would be observable
                    with results_lock:
                        active -= 1
            except BlockingIOError:
                with results_lock:
                    results.append("blocked")
            except Exception as exc:          # pragma: no cover - would fail the assertions below
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
        self.assertFalse((self.home / LOCK_NAME).exists(),
                         "every acquirer released the lock again — none leaked")

    def test_concurrent_stale_reclaim_survives_scheduling_delay(self):   # M1 (new) — CI-observed race
        """reclaim-ticket-race: a CURRENT holder merely delayed by scheduling (not crashed) must
        never have its still-live lock stolen by a sibling racer just because wall-clock age
        exceeds the stale threshold. `age > stale_after` is the ONLY signal `_update_lock` has —
        it cannot distinguish "the holder crashed" from "the holder is still working but slow,"
        because nothing refreshes the lock file's mtime while it is legitimately held. This is
        what GitHub Actions' heavier thread-scheduling reproduced (confirmed via 2 real CI runs,
        not inferred) against the sibling test above: its 0.05s hold blew up past a "1s"
        stale_after under CI contention (a >20x inflation, never seen locally) — the holder-side
        heartbeat below fixes the STRUCTURAL race (a live holder is never mistaken for a crashed
        one), but a heartbeat thread cannot survive whole-PROCESS scheduling starvation any more
        than the holder it protects can, so the test's own stale_after override is ALSO widened
        (test-only, prod default is 600s) to keep realistic margin against CI noise — belt AND
        suspenders, not an either/or (see PLAN.md §1 Reject R1 for why a bigger constant ALONE,
        without the heartbeat, was already rejected as a non-fix)."""
        self._write_lock(age_seconds=10)
        env = self._env()
        env["ADD_LOCK_STALE_SECONDS"] = "8"    # widened from "1" — see docstring + the sibling
                                                # test's own comment for the CI-observed rationale

        first_holder = threading.Event()
        hold_seconds = 10      # > ADD_LOCK_STALE_SECONDS (8) — simulates a scheduler stall on the
                               # CURRENT holder, not a crash: it is still alive, just descheduled.
        results = []
        results_lock = threading.Lock()
        barrier = threading.Barrier(6)
        active = 0
        peak = 0

        def racer():
            nonlocal active, peak
            barrier.wait()
            try:
                # a real second process doesn't give up after one glance — it polls
                # (`--lock-timeout`) for a while before deciding the holder is unreachable. Without
                # a timeout every racer would check staleness exactly ONCE, almost immediately after
                # the barrier (age ~= 0s, nowhere near stale_after) and just fail-fast — never
                # observing the moment the delayed holder's age crosses stale_after. Polling well
                # past `hold_seconds` is what lets a sibling racer's stat land inside that window.
                with _installer._update_lock(self.home, timeout=hold_seconds + 2, env=env):
                    with results_lock:
                        results.append("acquired")
                        active += 1
                        peak = max(peak, active)
                    # only the FIRST racer to actually acquire simulates the scheduler stall —
                    # every later (legitimately sequential) holder just does the normal brief hold.
                    if not first_holder.is_set():
                        first_holder.set()
                        time.sleep(hold_seconds)
                    else:
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
            t.join(timeout=hold_seconds + 10)   # scales with hold_seconds — a fixed 5s budget
                                                 # from the old 1.5s-hold version would truncate
                                                 # the join before a slower racer even finishes

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
        self.assertFalse((self.home / LOCK_NAME).exists(),
                         "every acquirer released the lock again — none leaked")


# --- leaked reclaim-ticket self-heal (post-freeze redo: a fresh adversarial verify pass found ---
# that a ticket file leaked by a crash mid-reclaim — created by a process that won it, then died
# before its own best-effort cleanup a few lines later — would cause an UNBOUNDED LIVELOCK here
# (worse than the sibling project-lock's clean fail-fast wedge): _update_lock LOOPS (it supports
# --lock-timeout), and BOTH the "lost the ticket" and "won the ticket" branches `continue`d
# straight back to the top of the `while fd is None:` loop — pre-fix — WITHOUT ever reaching the
# `if deadline is not None...` / `raise BlockingIOError` code beneath the `if age > stale_after:`
# block, so even an explicit --lock-timeout could never fire once a ticket was orphaned. Fix:
# apply the SAME age-based staleness check already governing the main lock to the ticket file
# too (identity-verified, same as the main lock's own reclaim — never a plain unconditional
# unlink, which would reopen the identical TOCTOU hole one level down), AND restructure the loop
# so the deadline check is reached on every non-reclaiming iteration, never bypassed by a
# ticket-loss branch that used to always `continue` unconditionally (see _installer.py:
# _update_lock for the full reasoning). Independent of, not shared with, this fix's own
# project-lock/JS-twin tests.

class LeakedTicketLivelockTest(_Base):
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

    def _write_lock(self, *, age_seconds, content=""):
        self.home.mkdir(parents=True, exist_ok=True)
        lock_path = self.home / LOCK_NAME
        lock_path.write_text(content)
        ts = time.time() - age_seconds
        os.utime(str(lock_path), (ts, ts))
        return lock_path

    def _run_bounded(self, *, timeout, join_timeout=10.0):
        """Run _update_lock(home, timeout=timeout, ...) on a daemon thread and join with a
        GENEROUS but FINITE bound — proves "self-heals promptly" / "--lock-timeout is honored"
        without ever risking hanging the test suite itself if a future regression reintroduces
        an unbounded spin: the assertion is on thread liveness after the join, not on the call
        ever returning on its own within this test process's lifetime."""
        env = self._env()
        env["ADD_LOCK_STALE_SECONDS"] = "1"
        result = {}

        def _acquire():
            try:
                with _installer._update_lock(self.home, timeout=timeout, env=env):
                    result["outcome"] = "acquired"
            except BlockingIOError:
                result["outcome"] = "blocked"
            except Exception as exc:                # pragma: no cover - would fail the assertions below
                result["outcome"] = f"error:{exc!r}"

        start = time.monotonic()
        t = threading.Thread(target=_acquire, daemon=True)
        t.start()
        t.join(timeout=join_timeout)
        elapsed = time.monotonic() - start
        return t, result, elapsed

    def test_leaked_ticket_self_heals_instead_of_unbounded_livelock(self):
        lock_path = self._write_lock(age_seconds=1000)                       # very stale
        ticket_path = self._leak_ticket(lock_path, ticket_age_seconds=1000)  # leaked long ago too
        t, result, elapsed = self._run_bounded(timeout=3.0)
        self.assertFalse(t.is_alive(),
                         f"a leaked ticket must self-heal PROMPTLY, not livelock unboundedly "
                         f"(still spinning after {elapsed:.1f}s against a 3.0s --lock-timeout "
                         f"budget it should never even need)")
        self.assertEqual(result.get("outcome"), "acquired",
                         f"the lock must be successfully self-healed and acquired, not blocked "
                         f"or errored: {result}")
        self.assertLess(elapsed, 5.0, f"self-heal must be prompt, nowhere near the 3.0s "
                         f"--lock-timeout budget (observed {elapsed:.2f}s) — proves it healed "
                         f"on its own, not merely by waiting out the deadline")
        self.assertFalse(lock_path.exists(), "the reclaimed lock is released again after the run")
        self.assertFalse(ticket_path.exists(), "the leaked ticket itself is cleaned up too")

    def test_lock_timeout_deadline_honored_even_when_a_ticket_cannot_yet_resolve(self):
        # The sharper claim: even in the WORST case — a ticket that never crosses its OWN (short)
        # staleness threshold during this test's own --lock-timeout budget, so neither the main
        # lock's reclaim NOR the ticket's own reclaim can make progress — the deadline must still
        # fire close to its declared budget. This is the exact defect: pre-fix, the deadline check
        # was structurally UNREACHABLE while a ticket stayed contested, regardless of how it got
        # that way.
        lock_path = self._write_lock(age_seconds=1000)
        ticket_path = self._leak_ticket(lock_path, ticket_age_seconds=0)   # "just created" — fresh
        t, result, elapsed = self._run_bounded(timeout=1.0)
        self.assertFalse(t.is_alive(),
                         f"--lock-timeout=1.0 must be honored, not bypassed by a contested "
                         f"ticket (still spinning after {elapsed:.1f}s)")
        self.assertEqual(result.get("outcome"), "blocked",
                         f"expected a clean BlockingIOError once the deadline elapsed: {result}")
        self.assertGreaterEqual(elapsed, 0.9, "the deadline must actually be waited out, not "
                         "short-circuited immediately")
        self.assertLess(elapsed, 3.0, f"--lock-timeout=1.0 must fire close to its own budget "
                         f"(observed {elapsed:.2f}s), never run away past it")
        self.assertTrue(ticket_path.exists(), "a fresh, still-in-flight-looking ticket is left "
                         "completely untouched — no over-eager reclaim")

    def test_npm_leaked_ticket_self_heals_instead_of_livelock(self):
        if not shutil.which("node"):
            self.skipTest("node not available")
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        lock_path = self._write_lock(age_seconds=1000)
        ticket_path = self._leak_ticket(lock_path, ticket_age_seconds=1000)
        env = dict(os.environ); env.update(self._env())
        env["ADD_LOCK_STALE_SECONDS"] = "1"
        start = time.monotonic()
        r = subprocess.run(["node", str(CLI_JS), "update", "--global", "--lock-timeout", "3"],
                           capture_output=True, text=True, env=env, timeout=15)
        elapsed = time.monotonic() - start
        self.assertEqual(r.returncode, 0, f"a leaked ticket must self-heal, not livelock: {r.stderr}")
        self.assertNotIn("update_in_progress", r.stdout + r.stderr)
        self.assertLess(elapsed, 5.0, f"self-heal must be prompt (observed {elapsed:.2f}s), "
                         f"nowhere near the 3s --lock-timeout budget")
        self.assertFalse(lock_path.exists())
        self.assertFalse(ticket_path.exists())


# --- diagnostic stamp (global-lock-followups M2) ----------------------------

class DiagnosticStampTest(_Base):
    """M2: a successful acquire stamps '<PID> <UTC ISO ts>' — informational ONLY, never
    consulted to decide staleness (mtime alone decides — see StaleLockSelfHealTest)."""

    def test_successful_acquire_stamps_pid_and_timestamp(self):      # M2 · Scenario 6
        env = self._env()
        with _installer._update_lock(self.home, env=env):
            content = (self.home / LOCK_NAME).read_text(encoding="utf-8")
        self.assertRegex(content, r"^\d+ \S+\n?$",
                         "the lock's content is '<PID> <timestamp>' on a successful acquire")

    def test_garbage_lock_content_never_errors_or_affects_staleness(self):   # M2 · Scenario 6
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        self.home.mkdir(parents=True, exist_ok=True)
        lock_path = self.home / LOCK_NAME
        lock_path.write_text("totally-not-a-pid-or-a-timestamp")
        now = time.time()
        os.utime(str(lock_path), (now - 10, now - 10))                # stale by mtime alone
        code, err = self._update(env_extra={"ADD_LOCK_STALE_SECONDS": "1"})
        self.assertEqual(code, 0, "staleness is decided by mtime alone — garbage content never errors")
        self.assertNotIn("update_in_progress", err)


# --- install --global under the same lock (global-lock-followups M3) -------

class InstallGlobalLockTest(_Base):
    """M3: install --global shares the SAME home lock as update --global — a lock failure
    aborts install() entirely (no partial home write, no per-project drop)."""

    def _hold_lock(self):
        return os.open(str(self.home / LOCK_NAME), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)

    def _release(self, fd):
        os.close(fd)
        try:
            os.unlink(str(self.home / LOCK_NAME))
        except OSError:
            pass

    def test_install_global_blocked_by_a_held_lock(self):            # M3 · Scenario 7
        self._valid_home()                                            # stamps the home once, uncontended
        fresh_target = self.tmp / "fresh"; fresh_target.mkdir()
        fd = self._hold_lock()
        try:
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                code = _installer.install(target=str(fresh_target), bundled=str(self.bundled),
                                          non_interactive=True, env=self._env(), as_global=True)
            err = buf.getvalue()
        finally:
            self._release(fd)
        self.assertNotEqual(code, 0, "install --global fails fast while the lock is held")
        self.assertIn("update_in_progress", err)
        reg = self._registry()
        self.assertNotIn(str(fresh_target.resolve()), reg, "nothing was registered while blocked")
        self.assertFalse((fresh_target / ".add").exists(),
                         "the per-project managed-layer drop did NOT occur")

    def test_two_concurrent_install_global_no_interleave(self):      # M3 · Scenario 8
        self.home.mkdir(parents=True, exist_ok=True)
        t1 = self.tmp / "race1"; t1.mkdir()
        t2 = self.tmp / "race2"; t2.mkdir()
        fd = self._hold_lock()                                        # simulate the first racer already inside
        try:
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                code1 = _installer.install(target=str(t1), bundled=str(self.bundled),
                                           non_interactive=True, env=self._env(), as_global=True)
        finally:
            self._release(fd)                                         # the first racer finishes / releases
        code2 = _installer.install(target=str(t2), bundled=str(self.bundled),
                                   non_interactive=True, env=self._env(), as_global=True)
        self.assertNotEqual(code1, 0, "the second-to-arrive racer fails fast while the first holds the lock")
        self.assertEqual(code2, 0, "once free, the next racer acquires cleanly")
        reg = self._registry()
        self.assertNotIn(str(t1.resolve()), reg, "the blocked racer never registered — no interleaved write")
        self.assertIn(str(t2.resolve()), reg, "the racer that acquired the free lock did register")

    def test_fresh_install_global_unaffected(self):                  # M3 regression · Scenario 9
        target = self.tmp / "solo"; target.mkdir()
        code = self._install_global(target)
        self.assertEqual(code, 0)
        self.assertTrue((target / ".add" / "tooling").exists(), "the per-project drop ran")
        reg = self._registry()
        self.assertIn(str(target.resolve()), reg)
        self.assertFalse((self.home / LOCK_NAME).exists(), "the lock is released by the time the run returns")


# --- opt-in bounded wait, --lock-timeout (global-lock-followups M4) --------

class LockTimeoutTest(_Base):
    """M4: --lock-timeout is an OPT-IN bounded wait for a LIVE lock; unset/0 stays
    byte-identical to today's immediate fail-fast (M1's self-heal fires regardless)."""

    def _hold_lock(self):
        return os.open(str(self.home / LOCK_NAME), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)

    def _release(self, fd):
        os.close(fd)
        try:
            os.unlink(str(self.home / LOCK_NAME))
        except OSError:
            pass

    def test_lock_timeout_waits_out_a_holder_that_releases_in_time(self):   # M4 · Scenario 10
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        fd = self._hold_lock()
        timer = threading.Timer(0.2, self._release, args=(fd,))
        timer.start()
        try:
            start = time.monotonic()
            code, err = self._update(lock_timeout=2.0)
            elapsed = time.monotonic() - start
        finally:
            timer.cancel()
        self.assertEqual(code, 0, "the waiting run acquires the lock once it is freed")
        self.assertNotIn("update_in_progress", err)
        self.assertGreaterEqual(elapsed, 0.15, "the run actually waited for the release, not an instant fail")

    def test_lock_timeout_expires_still_fails(self):                        # M4 + Reject · Scenario 11
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        fd = self._hold_lock()
        try:
            start = time.monotonic()
            code, err = self._update(lock_timeout=0.3)
            elapsed = time.monotonic() - start
        finally:
            self._release(fd)
        self.assertNotEqual(code, 0, "the wait budget expires and the run still fails")
        self.assertIn("update_in_progress", err)
        self.assertGreaterEqual(elapsed, 0.25, "the run waited roughly the full budget, not instantly")

    def test_lock_timeout_unset_or_zero_is_immediate(self):                 # M4 regression · Scenario 12
        self._valid_home()
        self._make_project(self.proj)
        self._set_registry(self.proj.resolve())
        fd = self._hold_lock()
        try:
            start = time.monotonic()
            code_unset, err_unset = self._update()
            elapsed_unset = time.monotonic() - start
            start2 = time.monotonic()
            code_zero, err_zero = self._update(lock_timeout=0)
            elapsed_zero = time.monotonic() - start2
        finally:
            self._release(fd)
        for code, err, elapsed, label in (
            (code_unset, err_unset, elapsed_unset, "unset"),
            (code_zero, err_zero, elapsed_zero, "zero"),
        ):
            self.assertNotEqual(code, 0, f"--lock-timeout {label} fails immediately")
            self.assertIn("update_in_progress", err)
            self.assertLess(elapsed, 1.0, f"--lock-timeout {label} does not wait")


# --- prune-data's OWN concurrency (CLOSED by prune-data-update-lock) --------

class PruneDataScopeTest(_Base):
    """global-lock-followups' own "deliberate ruling-out" (Scenario 14: prune-data stays
    UNLOCKED) was a CONSCIOUS, disclosed deferral, not a permanent ruling — the sibling task
    prune-data-update-lock (frozen @ v1, 2026-07-05) closes exactly this gap: prune-data now
    acquires the SAME existing home lock update --global already holds. This test's premise is
    inverted accordingly; superseding it here (not silently) is this task's own disclosed §4/§7
    note."""

    def test_prune_data_now_shares_the_home_lock(self):                # prune-data-update-lock
        import inspect
        py_src = inspect.getsource(_installer._prune_data) + inspect.getsource(_installer.prune_data)
        self.assertIn("_update_lock", py_src,
                     "prune-data now acquires the EXISTING _update_lock — the sibling task's "
                     "own fix, not a new primitive")
        js = CLI_JS.read_text(encoding="utf-8")
        prune_start = js.index("function pruneData(")
        prune_end = js.index("function cmdPruneData(")
        prune_fn = js[prune_start:prune_end]
        cmd_start = prune_end
        cmd_end = js.index("\n}\n", cmd_start)
        cmd_fn = js[cmd_start:cmd_end]
        self.assertIn("acquireUpdateLock", cmd_fn,
                     "cli.js's cmdPruneData mirrors the same fix")


if __name__ == "__main__":
    unittest.main(verbosity=2)
