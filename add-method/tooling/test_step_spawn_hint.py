#!/usr/bin/env python3
"""Red/green for the per-step spawn hint (task step-spawn-hint, advisor-gated-autonomy).

CONTRACT (frozen @ v1):
  _SPAWN_HINTS: dict[str,str]  phase -> idiom; done ABSENT
    specify:"domain researcher + wide scenario sweep" ·
    plan:"change-plan design sweep" ·
    tests:"red-suite test-author" · build:"independent well-scoped batch" ·
    verify:"earned-green refute-read"  (observe merged into verify)
  _spawn_hint_line(task: dict, autonomy: str) -> str | None   # PURE
    None  if phase ∉ _SPAWN_HINTS  OR  autonomy == "manual"
    else  f"spawn hint: {phase} → {_SPAWN_HINTS[phase]} (tier: {tier})"
    tier := "top" if task risk == "high" else "mid"
  cmd_status / cmd_guide render it for the ACTIVE task only, when non-None.
  Advisory only — never spawns, never mutates state.

Run: python3 -m unittest test_step_spawn_hint -v
"""
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


EXPECTED = {
    "direction": "domain researcher + wide scenario sweep + change-plan design sweep + "
                 "red-suite test-author",
    "build": "independent well-scoped batch",
    "verify": "earned-green refute-read",
}


class PureHelper(unittest.TestCase):
    def test_map_exact(self):
        self.assertEqual(add._SPAWN_HINTS, EXPECTED)

    def test_contract_and_done_absent(self):
        self.assertNotIn("contract", add._SPAWN_HINTS)
        self.assertNotIn("done", add._SPAWN_HINTS)

    def test_mid_tier_default(self):
        line = add._spawn_hint_line({"phase": "build"}, "auto")
        self.assertEqual(line, "spawn hint: build → independent well-scoped batch (tier: mid)")

    def test_top_tier_for_high_risk(self):
        line = add._spawn_hint_line({"phase": "verify", "risk": "high"}, "conservative")
        self.assertEqual(line, "spawn hint: verify → earned-green refute-read (tier: top)")

    def test_none_at_manual(self):
        self.assertIsNone(add._spawn_hint_line({"phase": "build"}, "manual"))

    def test_none_at_unmapped_phase(self):
        self.assertIsNone(add._spawn_hint_line({"phase": "contract"}, "auto"))
        self.assertIsNone(add._spawn_hint_line({"phase": "done"}, "auto"))

    def test_every_mapped_phase_renders(self):
        for ph, idiom in EXPECTED.items():
            line = add._spawn_hint_line({"phase": ph}, "auto")
            self.assertEqual(line, f"spawn hint: {ph} → {idiom} (tier: mid)")


class _CLI(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-spawnhint-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._run("init", "--name", "demo")
        self._run("new-milestone", "v1", "--title", "T", "--goal", "g")
        self._run("milestone-confirm", "v1")
        self._run("new-task", "t", "--title", "Feature")

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit:
            pass
        return buf.getvalue() + err.getvalue()

    def test_status_renders_hint_for_active_specify(self):
        # fresh task t is active at direction under the default (auto) project dial
        out = self._run("status")
        self.assertIn(
            "spawn hint: direction → domain researcher + wide scenario sweep + "
            "change-plan design sweep + red-suite test-author (tier: mid)", out)

    def test_manual_dial_suppresses_hint(self):
        self._run("autonomy", "set", "manual", "--project")
        out = self._run("status")
        self.assertNotIn("spawn hint:", out)

    def test_guide_renders_hint(self):
        out = self._run("guide")
        self.assertIn("spawn hint: direction → domain researcher", out)

    def test_status_does_not_mutate_state(self):
        before = (self.tmp / ".add" / "state.json").read_bytes()
        self._run("status")
        self.assertEqual((self.tmp / ".add" / "state.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
