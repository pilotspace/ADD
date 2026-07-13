#!/usr/bin/env python3
"""Behavioral proof of the setup lock-down (task: setup-lock-state, v12).

CONTRACT (frozen @ v1):
  - `lock [--by NAME] [--layers a,b,c] [--force] [--json]` sets state.setup.locked=true in ONE
    atomic write, stamping locked_at/_now(), locked_by, layers (default foundation,scope,contract).
    Re-lock without --force -> "already_locked"; empty --layers -> "layers_invalid".
  - `init --await-lock` seeds setup={locked:false,...}; plain init writes NO "setup" key.
  - Grandfather: a state with no "setup" key is treated as locked (legacy projects never gated).
  - Gating fires ONLY when "setup" in state AND setup.locked is false:
      new-task (>=1 task already) / advance (into build|verify|observe|done) / gate  -> "setup_unlocked".

  AMENDED (first-call-ergonomics, v2, 2026-07-09): a re-lock without --force is no longer a hard
  error — it is an exit-0 no-op (restates "already locked" on stdout, writes zero bytes); --force
  re-lock is unchanged. "layers_invalid" and the gating errors above are unchanged.

One test per SCENARIO. Run: python3 -m unittest test_setup_lock -v
"""
import contextlib
import getpass
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add


def _run(argv):
    """Run add.main(argv), capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class SetupLockTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-setup-lock-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------
    def _state(self):
        return add.load_state(add.find_root())

    def _freeze(self, slug):
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _init_await(self):
        add.main(["init", "--name", "demo", "--await-lock"])

    def _init_plain(self):
        add.main(["init", "--name", "demo"])

    # --- scenarios -----------------------------------------------------------
    def test_lock_sets_and_signs_state(self):
        self._init_await()
        code, out, _ = _run(["lock", "--by", "Tin"])
        self.assertEqual(code, 0)
        s = self._state()["setup"]
        self.assertTrue(s["locked"])
        self.assertEqual(s["locked_by"], "Tin")
        self.assertTrue(s["locked_at"])
        self.assertEqual(s["layers"], ["foundation", "scope", "contract"])
        # guard the FROZEN text format, not just that the path executed — AND the
        # engine-sourced next: footer (next-footer-engine): at lock-time there is no
        # active milestone, so the resolver yields the deterministic fail-soft line.
        self.assertEqual(out.strip(),
                         f"locked setup (foundation,scope,contract) by Tin @ {s['locked_at']}\n"
                         "next: add.py status — re-orient")

    def test_lock_json_prints_exactly_one_object(self):
        self._init_await()
        code, out, _ = _run(["lock", "--by", "Tin", "--json"])
        self.assertEqual(code, 0)
        self.assertTrue(out.strip(), "stdout was empty")
        d = json.loads(out)  # raises on trailing junk / non-json
        self.assertIsInstance(d, dict)
        for k in ("locked", "locked_at", "locked_by", "layers"):
            self.assertIn(k, d)
        self.assertTrue(d["locked"])

    def test_plain_init_is_grandfathered(self):
        self._init_plain()
        self.assertNotIn("setup", self._state())
        # full unchanged flow: many tasks, advance into build, record a gate
        self.assertEqual(_run(["new-task", "a"])[0], 0)
        self.assertEqual(_run(["new-task", "b"])[0], 0)
        add.main(["phase", "tests", "a"])
        self._freeze("a")  # freeze-gate-universal: §3 must be FROZEN before tests->build crossing
        self.assertEqual(_run(["advance", "a"])[0], 0)          # tests -> build, ungated
        self.assertEqual(self._state()["tasks"]["a"]["phase"], "build")
        add.main(["phase", "verify", "a"])
        self.assertEqual(_run(["gate", "PASS", "a"])[0], 0)
        self.assertEqual(self._state()["tasks"]["a"]["gate"], "PASS")
        self.assertNotIn("setup", self._state())

    def test_await_lock_init_starts_unlocked(self):
        self._init_await()
        self.assertIn("setup", self._state())
        self.assertFalse(self._state()["setup"]["locked"])

    def test_first_task_allowed_second_refused(self):
        self._init_await()
        self.assertEqual(_run(["new-task", "a"])[0], 0)
        code, _, err = _run(["new-task", "b"])
        self.assertEqual(code, 1)
        self.assertIn("setup_unlocked", err)
        self.assertEqual(set(self._state()["tasks"]), {"a"})

    def test_front_advances_but_build_blocked(self):
        self._init_await()
        add.main(["new-task", "a"])                      # phase=specify (plan-phase-core seed)
        self.assertEqual(_run(["advance", "a"])[0], 0)   # specify -> scenarios
        self.assertEqual(_run(["advance", "a"])[0], 0)   # scenarios -> plan
        # plan-phase-core: the plan->tests crossing is now freeze-gated — freeze §3 here so
        # this test isolates the setup_unlocked block at tests->build, not contract_not_frozen.
        self._freeze("a")
        self.assertEqual(_run(["advance", "a"])[0], 0)   # plan -> tests
        self.assertEqual(self._state()["tasks"]["a"]["phase"], "tests")
        code, _, err = _run(["advance", "a"])            # tests -> build : BLOCKED
        self.assertEqual(code, 1)
        self.assertIn("setup_unlocked", err)
        self.assertEqual(self._state()["tasks"]["a"]["phase"], "tests")

    def test_gate_blocked_pre_lock(self):
        self._init_await()
        add.main(["new-task", "a"])
        add.main(["phase", "verify", "a"])               # isolate my gate from the verify-phase guard
        code, _, err = _run(["gate", "PASS", "a"])
        self.assertEqual(code, 1)
        self.assertIn("setup_unlocked", err)
        self.assertEqual(self._state()["tasks"]["a"]["gate"], "none")

    def test_after_lock_build_and_gate_proceed(self):
        self._init_await()
        add.main(["new-task", "a"])
        _run(["lock", "--by", "Tin"])
        add.main(["phase", "tests", "a"])
        self._freeze("a")  # freeze-gate-universal: §3 must be FROZEN before tests->build crossing
        self.assertEqual(_run(["advance", "a"])[0], 0)   # tests -> build now allowed
        self.assertEqual(self._state()["tasks"]["a"]["phase"], "build")
        add.main(["phase", "verify", "a"])
        self.assertEqual(_run(["gate", "PASS", "a"])[0], 0)
        self.assertEqual(self._state()["tasks"]["a"]["gate"], "PASS")

    def test_relock_is_exit0_noop(self):
        # first-call-ergonomics M2: an exact already-locked retry (no --force) is now
        # an exit-0 no-op — it restates locked-ness on stdout and writes zero bytes;
        # --force still re-locks unchanged.
        self._init_await()
        _run(["lock", "--by", "Tin"])
        before = self._state()
        code, out, _ = _run(["lock", "--by", "Tin"])
        self.assertEqual(code, 0)
        self.assertIn("already locked", out)
        self.assertEqual(self._state(), before)
        self.assertEqual(_run(["lock", "--by", "Tin", "--force"])[0], 0)

    def test_empty_layers_rejected(self):
        self._init_await()
        code, _, err = _run(["lock", "--layers", ""])
        self.assertEqual(code, 1)
        self.assertIn("layers_invalid", err)
        self.assertFalse(self._state()["setup"]["locked"])

    def test_lock_on_grandfathered_is_exit0_noop(self):
        self._init_plain()                                  # no "setup" key == grandfathered-locked
        code, out, _ = _run(["lock"])                       # bare lock -> already-locked no-op
        self.assertEqual(code, 0)
        self.assertIn("already locked", out)
        self.assertNotIn("setup", self._state())            # no-op wrote nothing
        self.assertEqual(_run(["lock", "--force"])[0], 0)   # --force writes a fresh block
        self.assertTrue(self._state()["setup"]["locked"])
        self.assertEqual(self._state()["setup"]["locked_by"], getpass.getuser())  # --by default


if __name__ == "__main__":
    unittest.main()
