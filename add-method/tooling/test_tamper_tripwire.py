#!/usr/bin/env python3
"""Red/green tests for the mechanical tamper tripwire (task tamper-tripwire, verify-integrity).

The method's FIRST mechanically-enforced HARD-STOP. At `tests->build` the engine
SNAPSHOTS the md5 of the resolved red test files + the frozen §3 contract into
state["tasks"][slug]["tripwire"]; at the verify gate it RE-CHECKS, and any edit
to a tracked test or the frozen contract since the red run refuses the completing
outcome (PASS / RISK-ACCEPTED). A tamper finding is HARD-STOP-class — never
launderable through RISK-ACCEPTED. Tri-state, co-witnessed by flag_verified:
  present + match  -> pass through
  present + diverge-> HARD-STOP (build_tampered / contract_tampered)
  absent + flag_verified true  -> HARD-STOP (tripwire_missing, suspicious-absent)
  absent + flag_verified false -> skip (legacy / never crossed tests->build)
Tool-agnostic: hashes file bytes only, never runs tests or measures coverage.
The ×3 add.py parity + the engine pin bump are guarded by test_shared_engine_pin.

Run: python3 -m unittest test_tamper_tripwire -v
"""
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

WAIVER = ["--owner", "Tin", "--ticket", "T-1", "--expires", "2099-01-01"]


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (engine input contracts)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-tw-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- CLI helpers ------------------------------------------------------
    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(list(argv))
        return buf.getvalue(), err.getvalue()

    def _run(self, *argv):
        """Run a CLI command capturing exit code (SystemExit) + streams."""
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _task_md(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "TASK.md"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _task_state(self, slug: str) -> dict:
        return self._state()["tasks"][slug]

    # ---- arrangement ------------------------------------------------------
    _CONTRACT_BODY = "shape: tripwire { contract_md5, tests:{path:md5} }"

    def _write_task(self, slug: str, *, frozen=True, contract_extra=""):
        """A full TASK.md with a FROZEN, well-formed §3 (so tests->build does not
        die on unflagged_freeze) and a §4 declaring `./tests/`."""
        status = ("Status: FROZEN @ v1 — approved by Tester 2026-06-11."
                  if frozen else "Status: DRAFT")
        flag = ("Least-sure flag surfaced at freeze: [contract] the snapshot lives "
                "in agent-writable state.json — accepted as an honest ceiling.")
        lines = [
            f"# TASK: {slug}",
            f"slug: {slug} · created: 2026-06-11 · stage: mvp",
            "phase: ground",          # kept in sync by the CLI (_sync_task_marker)
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_advance · cmd_gate"),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT",
                      "```",
                      self._CONTRACT_BODY + contract_extra,
                      "```",
                      status,
                      flag),
            *_section(4, "TESTS",
                      "Coverage target: behavior",
                      "Tests live in: `./tests/`"),
            *_section(5, "BUILD", "code"),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    def _write_test_file(self, slug: str, body: str):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(body, encoding="utf-8")

    _RED_TEST = "def test_one():\n    assert compute(2) == 4\n"

    def _arm(self, slug: str, *, frozen=True):
        """Create a task, give it a frozen §3 + a real red test file, and CROSS
        tests->build so the snapshot fires (under whatever engine is live)."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug, frozen=frozen)
        self._write_test_file(slug, self._RED_TEST)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build (the snapshot seam)

    def _to_verify_and_gate(self, slug, *gate_args):
        self._silent("advance", slug)            # build -> verify
        outcome, *flags = gate_args or ("PASS",)   # house order: gate <outcome> <slug> [--flags]
        return self._run("gate", outcome, slug, *flags)   # slug-after-flags breaks argparse <=3.12

    def _assert_blocked(self, out, err, code, slug, code_token=None):
        # heal-then-escalate (verify-integrity): a first mechanical tamper now enters the
        # bounded self-heal loop — it RETURNS TO BUILD (phase=build) rather than dying on
        # sight; an erased baseline (tripwire_missing) still HARD-STOPs in place at verify.
        # Either way the gate is REFUSED and records NO completing outcome (the strict
        # invariant). The return-to-build itself is positively covered by test_heal_then_escalate.
        self.assertNotEqual(code, 0, "a tampered gate must refuse")
        if code_token:
            self.assertIn(code_token, out + err)
        st = self._task_state(slug)
        self.assertIn(st["phase"], ("verify", "build"),
                      "a refused tamper returns to build (heal) or stays at verify (escalation)")
        self.assertEqual(st["gate"], "none", "refusal records no completing outcome")


class SnapshotTest(_Board):
    """At tests->build the snapshot is persisted into state.json."""

    def test_snapshot_taken_on_tests_to_build(self):
        self._arm("alpha")
        tw = self._task_state("alpha").get("tripwire")
        self.assertIsInstance(tw, dict, "tripwire snapshot must be recorded")
        self.assertIn("contract_md5", tw)
        self.assertTrue(tw.get("tests"), "the resolved test files must be hashed")
        self.assertTrue(self._task_state("alpha").get("flag_verified"),
                        "flag_verified is the co-witness, set in the same block")

    def test_snapshot_overwrites_on_recross(self):
        self._arm("alpha")
        first = dict(self._task_state("alpha")["tripwire"]["tests"])
        # a legit change: the test file is updated, then tests->build re-crossed
        self._write_test_file("alpha", self._RED_TEST + "\ndef test_two():\n    assert compute(3) == 9\n")
        self._silent("phase", "tests", "alpha")
        self._silent("advance", "alpha")         # re-cross -> overwrite
        second = self._task_state("alpha")["tripwire"]["tests"]
        self.assertNotEqual(first, second, "the snapshot must overwrite on re-cross")


class TamperBlocksGateTest(_Board):
    """A post-red edit to a tracked test or the frozen §3 refuses the gate."""

    def test_weakened_test_blocks_gate(self):
        self._arm("alpha")
        self._write_test_file("alpha", "def test_one():\n    assert True\n")  # gutted
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self._assert_blocked(out, err, code, "alpha", "build_tampered")

    def test_deleted_test_blocks_gate(self):
        self._arm("alpha")
        (self._root() / "tasks" / "alpha" / "tests" / "test_demo.py").unlink()
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self._assert_blocked(out, err, code, "alpha", "build_tampered")

    def test_contract_edit_blocks_gate(self):
        self._arm("alpha")
        # edit the frozen §3 body after the snapshot (Status stays FROZEN)
        p = self._task_md("alpha")
        p.write_text(p.read_text(encoding="utf-8").replace(
            self._CONTRACT_BODY, self._CONTRACT_BODY + " ;tampered"), encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self._assert_blocked(out, err, code, "alpha", "contract_tampered")

    def test_fail_closed_on_unreadable_file(self):
        self._arm("alpha")
        # the tracked file becomes unreadable/missing -> treated as DIVERGED, never a crash
        (self._root() / "tasks" / "alpha" / "tests" / "test_demo.py").unlink()
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertNotEqual(code, 0)
        self.assertNotIn("Traceback", out + err, "fail-closed must not crash")


class NotLaunderableTest(_Board):
    """A tamper finding is HARD-STOP-class — never RISK-ACCEPTED-waived."""

    def test_tamper_not_launderable_via_risk_accepted(self):
        self._arm("alpha")
        self._write_test_file("alpha", "def test_one():\n    assert True\n")
        out, err, code = self._to_verify_and_gate("alpha", "RISK-ACCEPTED", *WAIVER)
        self._assert_blocked(out, err, code, "alpha")
        self.assertNotIn("waiver", json.dumps(self._task_state("alpha")),
                         "a tampered RISK-ACCEPTED records no waiver")

    def test_clean_risk_accepted_records_waiver(self):
        # the tamper check sits just before the waiver-write block; a CLEAN
        # RISK-ACCEPTED must still record its signed waiver (placement guard)
        self._arm("alpha")
        out, err, code = self._to_verify_and_gate("alpha", "RISK-ACCEPTED", *WAIVER)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self._task_state("alpha")["gate"], "RISK-ACCEPTED")
        self.assertEqual(self._task_state("alpha")["waiver"]["owner"], "Tin")


class TriStateTest(_Board):
    """The absent-snapshot split, co-witnessed by flag_verified."""

    def test_clean_build_passes_gate(self):
        self._arm("alpha")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self._task_state("alpha")["gate"], "PASS")
        self.assertEqual(self._task_state("alpha")["phase"], "done")

    def test_legacy_absent_skips(self):
        # never crossed tests->build (jumped) -> flag_verified false, no tripwire -> skip
        self._silent("new-task", "beta", "--title", "beta")
        self._write_task("beta")
        self._silent("phase", "verify", "beta")
        out, err, code = self._run("gate", "PASS", "beta")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self._task_state("beta")["gate"], "PASS")

    def test_suspicious_absent_blocks(self):
        # crossed tests->build (flag_verified true) then the snapshot was erased
        self._arm("alpha")
        st = self._state()
        st["tasks"]["alpha"].pop("tripwire", None)        # erase, keep flag_verified
        (self._root() / "state.json").write_text(json.dumps(st), encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self._assert_blocked(out, err, code, "alpha", "tripwire_missing")


class StandingMonitorTest(_Board):
    """check WARNs on a non-done tampered task but stays never-red."""

    def test_standing_warn_never_red(self):
        self._arm("alpha")                                 # present snapshot
        self._silent("advance", "alpha")                   # build -> verify (non-done)
        self._write_test_file("alpha", "def test_one():\n    assert True\n")  # diverge
        out, err, code = self._run("check")
        self.assertEqual(code, 0, "the standing monitor is never-red")
        self.assertIn("tamper", (out + err).lower(),
                      "check must WARN on a diverged non-done task")


if __name__ == "__main__":
    unittest.main(verbosity=2)
