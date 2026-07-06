#!/usr/bin/env python3
"""Tests for js-reclaim-lock-heartbeat (JS/npm reclaim-lock heartbeat twin fix).

FROZEN @ v1: acquireUpdateLock/acquireProjectLock in cli.js gain a holder-side heartbeat
(`setInterval`-driven `fs.utimesSync` refresh of the lock file's own mtime) — the JS analog of
the Python `_lock_heartbeat` fix (reclaim-ticket-race) — so a live-but-slow holder's lock is
never misjudged genuinely stale purely because wall-clock age crosses `staleAfterMs`. The
existing identity-verified (inode-compared) reclaim-ticket mechanism is UNCHANGED — this only
fixes the staleness *judgment*, never reclaim arbitration.

Driven entirely through a NEW, undocumented, test-only CLI entrypoint —
`node cli.js --internal-acquire-lock <update|project> <lockDir> <holdMs>` — which acquires the
named lock, prints "HELD <epoch-ms>" the instant it holds, sleeps `holdMs` (via a real,
event-loop-yielding delay — NOT the codebase's own `sleepSync`'s `Atomics.wait`, which would
block the very same event loop the heartbeat's `setInterval` needs to fire on, defeating the
mechanism this test exists to prove), prints "RELEASED <epoch-ms>", then exits 0. Chosen
(AskUserQuestion, Tin Dang) over standing up a JS test runner or shipping untested — a real
subprocess race is also MORE representative of production contention (concurrent
`npm install`/`add init` runs are separate OS processes, never threads).

RED until cli.js's `acquireUpdateLock`/`acquireProjectLock` gain the heartbeat AND the
`--internal-acquire-lock` entrypoint exists — red for the right reason (missing entrypoint, or
a misjudged-stale double-hold observed as peak > 1), never a broken harness.

Run: python3 -m unittest test_js_reclaim_lock_heartbeat -v
"""
import os
import re
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
CLI_JS = _ADD_METHOD / "bin" / "cli.js"

_HELD_RE = re.compile(r"^HELD (\d+)$", re.M)
_RELEASED_RE = re.compile(r"^RELEASED (\d+)$", re.M)


def _node_available():
    return shutil.which("node") is not None


class _Base(unittest.TestCase):
    def setUp(self):
        if not _node_available():
            self.skipTest("node not available")
        self.tmp = Path(tempfile.mkdtemp(prefix="jslock-")).resolve()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _spawn(self, kind, lock_dir, hold_ms, env_extra=None):
        env = dict(os.environ)
        env.update(env_extra or {})
        return subprocess.Popen(
            ["node", str(CLI_JS), "--internal-acquire-lock", kind, str(lock_dir), str(hold_ms)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

    def _run(self, kind, lock_dir, hold_ms, env_extra=None, timeout=30):
        env = dict(os.environ)
        env.update(env_extra or {})
        return subprocess.run(
            ["node", str(CLI_JS), "--internal-acquire-lock", kind, str(lock_dir), str(hold_ms)],
            capture_output=True, text=True, env=env, timeout=timeout)

    def _wait_for_held(self, proc, timeout=10):
        """Block until proc's stdout has printed its HELD line (or it exited without one)."""
        deadline = time.time() + timeout
        buf = ""
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            buf += line
            if line.startswith("HELD "):
                return buf
        return buf

    def _finish(self, proc, buf_so_far="", timeout=15):
        out, err = proc.communicate(timeout=timeout)
        return buf_so_far + out, err, proc.returncode

    def _intervals(self, stdout):
        """[(held_ms, released_ms_or_None)] parsed from one process's stdout."""
        held = [int(x) for x in _HELD_RE.findall(stdout)]
        released = [int(x) for x in _RELEASED_RE.findall(stdout)]
        return [(h, released[i] if i < len(released) else None) for i, h in enumerate(held)]

    def _peak_overlap(self, all_intervals):
        """Max number of simultaneously-open [held, released) intervals across all processes.
        An unreleased (None) end counts as still open when the race ended."""
        events = []
        for h, r in all_intervals:
            events.append((h, 1))
            events.append((r if r is not None else float("inf"), -1))
        # a release at the same instant as a new hold must sort BEFORE the hold (-1 before +1)
        # so a genuine hand-off is never miscounted as an overlap
        events.sort(key=lambda e: (e[0], e[1]))
        cur = peak = 0
        for _, delta in events:
            cur += delta
            peak = max(peak, cur)
        return peak


class SlowHolderSurvivesContentionTest(_Base):
    def test_slow_holder_survives_contention(self):   # M1
        lock_dir = self.tmp / "home"
        env = {"ADD_LOCK_STALE_SECONDS": "0.3"}   # 300ms — tight but realistic test threshold
        a = self._spawn("update", lock_dir, 3000, env_extra=env)
        buf_a = self._wait_for_held(a)
        self.assertIn("HELD", buf_a, "process A must acquire the lock first")
        time.sleep(0.7)   # > staleAfterMs (0.3s) while A still legitimately holds (3s total)
        b = self._run("update", lock_dir, 50, env_extra=env, timeout=10)
        out_a, err_a, code_a = self._finish(a, buf_a)
        self.assertEqual(code_a, 0, err_a)
        self.assertNotIn("HELD", b.stdout,
                         "B must never acquire A's still-legitimately-held lock just because "
                         "wall-clock age crossed staleAfterMs — the heartbeat must have kept "
                         "A's mtime refreshed")
        self.assertIn("update_in_progress", b.stdout + b.stderr)
        peak = self._peak_overlap(self._intervals(out_a) + self._intervals(b.stdout))
        self.assertLessEqual(peak, 1,
                             f"at most one process may hold the lock at any instant "
                             f"(observed peak: {peak})")


class ExitBoundednessTest(_Base):
    def test_heartbeat_does_not_block_exit(self):   # M2, R2
        for kind, lock_name in (("update", "home"), ("project", "addDir")):
            with self.subTest(kind=kind):
                lock_dir = self.tmp / lock_name
                start = time.time()
                try:
                    r = self._run(kind, lock_dir, 100, timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail(f"{kind} lock's process hung past 5s — the heartbeat timer must "
                              f"be .unref()'d so it never blocks natural process exit")
                elapsed = time.time() - start
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn("HELD", r.stdout)
                self.assertIn("RELEASED", r.stdout)
                self.assertLess(elapsed, 5)


class GenuineCrashStillReclaimsTest(_Base):
    def test_genuine_crash_still_reclaims(self):   # M3
        lock_dir = self.tmp / "home"
        lock_dir.mkdir(parents=True)
        lock_path = lock_dir / ".update.lock"
        # simulate a crash: a lock file left behind, real staleness, no heartbeat ever ran
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        old = time.time() - 1000
        os.utime(str(lock_path), (old, old))
        env = {"ADD_LOCK_STALE_SECONDS": "1"}
        r = self._run("update", lock_dir, 50, env_extra=env, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("HELD", r.stdout,
                       "a genuinely stale (crashed, no heartbeat) lock must still self-heal via "
                       "the existing identity-verified reclaim-ticket mechanism, unchanged")


class ConcurrentStaleReclaimTest(_Base):
    def test_concurrent_stale_reclaim_exactly_one_wins(self):   # M4
        lock_dir = self.tmp / "home"
        env = {"ADD_LOCK_STALE_SECONDS": "0.4"}
        a = self._spawn("update", lock_dir, 3000, env_extra=env)
        buf_a = self._wait_for_held(a)
        self.assertIn("HELD", buf_a)
        time.sleep(0.8)   # > staleAfterMs while A still holds
        contenders = [self._spawn("update", lock_dir, 100, env_extra=env) for _ in range(5)]
        results = [c.communicate(timeout=15) for c in contenders]
        out_a, err_a, code_a = self._finish(a, buf_a)
        self.assertEqual(code_a, 0, err_a)
        all_intervals = self._intervals(out_a)
        for out, _err in results:
            all_intervals += self._intervals(out)
        peak = self._peak_overlap(all_intervals)
        self.assertLessEqual(peak, 1,
                             f"at most one process may hold the lock at any instant across the "
                             f"whole 6-process race (observed peak: {peak})")


class HeartbeatIntervalFormulaTest(unittest.TestCase):
    def test_heartbeat_interval_always_below_threshold(self):   # R1
        src = CLI_JS.read_text(encoding="utf-8")
        self.assertRegex(src, r"Math\.max\(50,\s*Math\.min\(staleAfterMs\s*/\s*4,\s*5000\)\)",
                          "the heartbeat interval formula must match the frozen contract's "
                          "max(50ms, min(staleAfterMs/4, 5000ms)) shape")

        def interval(stale_after_ms):
            return max(50, min(stale_after_ms / 4, 5000))

        # realistic thresholds only — production defaults are 600s/120s; this session's own
        # tests override down to ~300-400ms. Below ~200ms the fixed 50ms floor can equal or
        # exceed staleAfterMs itself (a separate, already-accepted floor-vs-ceiling tradeoff,
        # inherited unchanged from the Python fix's own identical formula) — R1 guards against
        # an interval too LARGE relative to staleAfterMs, not an unrealistically tiny one no
        # real caller would ever configure.
        for stale_ms in (200, 300, 1000, 5000, 30000, 120000, 600000, 3600000):
            with self.subTest(stale_ms=stale_ms):
                self.assertLess(interval(stale_ms), stale_ms,
                                f"heartbeat interval must stay strictly below staleAfterMs="
                                f"{stale_ms}ms so a refresh always lands before the threshold "
                                f"elapses")


class ProjectLockHeartbeatParityTest(_Base):
    """Must #1 requires BOTH acquireUpdateLock and acquireProjectLock protected — a second,
    independent race against the project-scope twin (no shared code with acquireUpdateLock, per
    this file's own existing convention)."""
    def test_project_lock_slow_holder_survives_contention(self):
        lock_dir = self.tmp / "addDir"
        env = {"ADD_PROJECT_LOCK_STALE_SECONDS": "0.3"}
        a = self._spawn("project", lock_dir, 3000, env_extra=env)
        buf_a = self._wait_for_held(a)
        self.assertIn("HELD", buf_a)
        time.sleep(0.7)
        b = self._run("project", lock_dir, 50, env_extra=env, timeout=10)
        out_a, err_a, code_a = self._finish(a, buf_a)
        self.assertEqual(code_a, 0, err_a)
        self.assertNotIn("HELD", b.stdout,
                         "acquireProjectLock must carry the IDENTICAL heartbeat protection as "
                         "acquireUpdateLock — a live holder must never be misjudged stale")
        self.assertIn("install_in_progress", b.stdout + b.stderr)


if __name__ == "__main__":
    unittest.main()
