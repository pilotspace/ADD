#!/usr/bin/env python3
"""Red/green tests for the bounded self-heal loop (task heal-then-escalate, verify-integrity).

Task 1 (tamper-tripwire) MECHANICALLY detects a cheat; task 2 (earned-green-rubric)
adds the JUDGMENT rubric. This task closes the milestone: a CONFIRMED cheat does not
immediately HARD-STOP — it returns the task to BUILD for an honest redo, the engine
COUNTS the attempts, CAPS at 3, and the 4th confirmed cheat forces a HARD-STOP that
ESCALATES to the human. A gamed green is never auto-passed; the loop is never unbounded.

Two entry points, one router (_heal_or_escalate):
  - MECHANICAL (enforced) — _tamper_guard divergence at a COMPLETING gate.
  - SEMANTIC  (honor-system) — `add.py heal <slug> --reason "..."`, the agent's report of
    an overfit/vacuous/stub finding the engine cannot see; the human gate stays the backstop.

The counter is MONOTONIC: attempts never auto-resets (cmd_phase is unguarded, so a reset
on a tests->build re-cross would be a zero-human cap bypass). An HONEST build (no cheat)
never calls the router -> it PASSes normally, even at attempts==3 (the cap bites a CONTINUED
cheat, never a recovery).

The ×3 add.py parity + the engine_pin bump are guarded by test_shared_engine_pin.

Run: python3 -m unittest test_heal_then_escalate -v
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
HEAL_CAP = 3


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (engine input contracts)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-heal-")).resolve()
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
        return self._root() / "tasks" / slug / "PLAN.md"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _task_state(self, slug: str) -> dict:
        return self._state()["tasks"][slug]

    def _heal(self, slug: str) -> dict:
        return self._task_state(slug).get("heal") or {}

    def _attempts(self, slug: str) -> int:
        return self._heal(slug).get("attempts", 0)

    # ---- arrangement ------------------------------------------------------
    _CONTRACT_BODY = "shape: heal { attempts:int, history:[{at,reason,source}] }"

    def _write_task(self, slug: str, *, frozen=True):
        """A full PLAN.md with a FROZEN, well-formed §3 (so tests->build does not die
        on unflagged_freeze) and a §4 declaring `./tests/`."""
        status = ("Status: FROZEN @ v1 — approved by Tester 2026-06-11."
                  if frozen else "Status: DRAFT")
        flag = ("Least-sure flag surfaced at freeze: [contract] attempts is monotonic "
                "— no auto-reset — accepted as the cap's only honest floor.")
        lines = [
            f"# PLAN: {slug}",
            f"slug: {slug} · created: 2026-06-11 · stage: mvp",
            "phase: ground",
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_gate · _heal_or_escalate"),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT", "```", self._CONTRACT_BODY, "```", status, flag),
            *_section(4, "TESTS", "Coverage target: behavior", "Tests live in: `./tests/`"),
            *_section(5, "BUILD", "code"),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    _RED_TEST = "def test_one():\n    assert compute(2) == 4\n"
    _GUTTED = "def test_one():\n    assert True\n"

    def _write_test_file(self, slug: str, body: str):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(body, encoding="utf-8")

    def _arm(self, slug: str):
        """Create a task, frozen §3 + a real red test file, and CROSS tests->build so
        the tripwire snapshot fires. Leaves the task at phase build."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug)
        self._write_test_file(slug, self._RED_TEST)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build (snapshot seam)

    def _to_verify(self, slug):
        self._silent("advance", slug)            # build -> verify (no re-snapshot)

    def _gate(self, slug, *gate_args):
        outcome, *flags = gate_args or ("PASS",)   # house order: gate <outcome> <slug> [--flags]
        return self._run("gate", outcome, slug, *flags)   # slug-after-flags breaks argparse <=3.12

    def _drive_returns(self, slug, n):
        """Drive n cheat-arrivals that each RETURN to build (cheat persists). Asserts
        each is a return-to-build, not a completing outcome. Leaves phase=build,
        attempts==n (n must be < HEAL_CAP+1 for all to return)."""
        for i in range(1, n + 1):
            self._to_verify(slug)
            out, err, code = self._gate(slug, "PASS")
            self.assertNotEqual(code, 0, f"arrival {i} must not complete")
            self.assertEqual(self._task_state(slug)["phase"], "build",
                             f"arrival {i} returns the task to build")
            self.assertEqual(self._attempts(slug), i, f"attempt {i} recorded")
            self.assertEqual(self._task_state(slug)["gate"], "none",
                             f"arrival {i} records no completing outcome")


# ── ENTRY 1 — the mechanical loop ─────────────────────────────────────────────
class MechanicalLoopTest(_Board):

    def test_first_mechanical_cheat_returns_to_build(self):
        self._arm("alpha")
        self._write_test_file("alpha", self._GUTTED)      # tamper after the snapshot
        self._to_verify("alpha")
        out, err, code = self._gate("alpha", "PASS")
        self.assertNotEqual(code, 0, "a cheat must not complete the gate")
        st = self._task_state("alpha")
        self.assertEqual(st["phase"], "build", "first cheat returns to build")
        self.assertEqual(self._attempts("alpha"), 1)
        self.assertEqual(st["gate"], "none", "no PASS is recorded on a cheat")
        self.assertIn("return_to_build", out + err)

    def test_fourth_cheat_hard_stops(self):
        self._arm("alpha")
        self._write_test_file("alpha", self._GUTTED)
        self._drive_returns("alpha", HEAL_CAP)            # attempts -> 3, all return to build
        self._to_verify("alpha")
        out, err, code = self._gate("alpha", "PASS")      # the 4th confirmed cheat
        self.assertNotEqual(code, 0)
        st = self._task_state("alpha")
        self.assertEqual(st["gate"], "HARD-STOP", "the 4th cheat HARD-STOPs")
        self.assertNotEqual(st["gate"], "PASS", "a gamed green is never auto-passed")
        self.assertIn("heal_exhausted", out + err)

    def test_honest_fix_within_budget_passes(self):
        self._arm("alpha")
        self._write_test_file("alpha", self._GUTTED)
        self._drive_returns("alpha", 1)                   # attempts -> 1, phase build
        self._write_test_file("alpha", self._RED_TEST)    # revert to the snapshot baseline
        self._to_verify("alpha")
        out, err, code = self._gate("alpha", "PASS")
        self.assertEqual(code, 0, "an honest fix passes")
        st = self._task_state("alpha")
        self.assertEqual(st["gate"], "PASS")
        self.assertEqual(st["phase"], "done")
        self.assertEqual(self._attempts("alpha"), 1, "the counter only moves on a cheat")

    def test_honest_build_passes_at_attempts_3(self):
        self._arm("alpha")
        self._write_test_file("alpha", self._GUTTED)
        self._drive_returns("alpha", HEAL_CAP)            # attempts -> 3
        self._write_test_file("alpha", self._RED_TEST)    # fully revert
        self._to_verify("alpha")
        out, err, code = self._gate("alpha", "PASS")
        self.assertEqual(code, 0, "the cap bites a continued cheat, never a recovery")
        self.assertEqual(self._task_state("alpha")["gate"], "PASS")
        self.assertEqual(self._task_state("alpha")["phase"], "done")

    def test_cheat_not_launderable_via_risk_accepted(self):
        self._arm("alpha")
        self._write_test_file("alpha", self._GUTTED)
        self._drive_returns("alpha", HEAL_CAP)            # attempts -> 3
        self._to_verify("alpha")
        out, err, code = self._gate("alpha", "RISK-ACCEPTED", *WAIVER)
        self.assertNotEqual(code, 0)
        st = self._task_state("alpha")
        self.assertEqual(st["gate"], "HARD-STOP", "a cheat is never RISK-ACCEPTED-launderable")
        self.assertNotIn("waiver", st, "no waiver is recorded on an escalated cheat")

    def test_attempt_is_durable(self):
        """A re-arrival re-runs the gate; the increment persisted, so no free attempt."""
        self._arm("alpha")
        self._write_test_file("alpha", self._GUTTED)
        self._drive_returns("alpha", 1)
        self.assertEqual(self._attempts("alpha"), 1)
        self._to_verify("alpha")
        self._gate("alpha", "PASS")                       # second arrival
        self.assertEqual(self._attempts("alpha"), 2, "the attempt is durable across re-runs")


# ── monotonicity — the cap cannot be cleared without a recorded human action ──
class MonotonicTest(_Board):

    def test_monotonic_no_reset_on_recross(self):
        self._arm("alpha")
        self._write_test_file("alpha", self._GUTTED)
        self._drive_returns("alpha", HEAL_CAP)            # attempts -> 3, phase build
        # a tests->build re-cross re-snapshots the tripwire (task 1's accepted ceiling),
        # but it must NOT reset the heal counter (cmd_phase is unguarded).
        self._silent("phase", "tests", "alpha")
        self._silent("advance", "alpha")                  # re-cross -> re-snapshot
        self.assertEqual(self._attempts("alpha"), HEAL_CAP,
                         "the counter survives a re-cross — monotonic, no reset")
        # a FRESH cheat after the re-cross gets no fresh budget: it HARD-STOPs at once.
        self._write_test_file("alpha", self._GUTTED + "\ndef test_two():\n    assert True\n")
        self._to_verify("alpha")
        out, err, code = self._gate("alpha", "PASS")
        self.assertEqual(self._task_state("alpha")["gate"], "HARD-STOP",
                         "no fresh 3-attempt budget after a re-cross")


# ── ENTRY 2 — the semantic (honor-system) verb ───────────────────────────────
class SemanticHealTest(_Board):

    def test_semantic_heal_enters_loop(self):
        self._arm("alpha")
        self._to_verify("alpha")                          # clean (no tamper)
        out, err, code = self._run("heal", "alpha", "--reason",
                                   "overfit: src special-cases the literal test inputs")
        self.assertNotEqual(code, 0, "a reported cheat returns to build, not a completion")
        st = self._task_state("alpha")
        self.assertEqual(st["phase"], "build")
        self.assertEqual(self._attempts("alpha"), 1)
        hist = self._heal("alpha").get("history") or []
        self.assertTrue(hist and hist[-1].get("source") == "refute-read",
                        "a semantic finding is sourced 'refute-read'")

    def test_heal_requires_reason(self):
        self._arm("alpha")
        self._to_verify("alpha")
        out, err, code = self._run("heal", "alpha")       # no --reason
        self.assertNotEqual(code, 0)
        self.assertIn("heal_reason_required", out + err)
        self.assertEqual(self._attempts("alpha"), 0, "a rejected heal records no attempt")
        self.assertEqual(self._task_state("alpha")["phase"], "verify", "phase unchanged")

    def test_heal_requires_verify_phase(self):
        self._arm("alpha")                                # leaves phase=build
        out, err, code = self._run("heal", "alpha", "--reason", "x")
        self.assertNotEqual(code, 0)
        self.assertIn("heal_not_at_verify", out + err)
        self.assertEqual(self._attempts("alpha"), 0)
        self.assertEqual(self._task_state("alpha")["phase"], "build", "phase unchanged")


# ── the loop is documented in its home (run.md) ──────────────────────────────
class LoopDocumentedTest(unittest.TestCase):

    def test_loop_documented_in_run_md(self):
        run_md = (Path(__file__).resolve().parent.parent
                  / "skill" / "add" / "run.md").read_text(encoding="utf-8")
        low = " ".join(run_md.split()).lower()             # collapse hard-wraps
        self.assertIn("self-heal", low, "run.md must name the bounded self-heal loop")
        self.assertIn("escalat", low, "run.md must describe the escalation")
        # tie the cap to its context — a bare "3" is trivially true anywhere; the cap must be
        # STATED as the honest-redo limit (refute-read nit, strengthened before the gate).
        self.assertIn("3 honest", low,
                      "run.md must state the cap as '3 honest ...' re-build attempts")


class ForcePreservesHeal(_Board):
    """F8 (force-preserve-heal): `new-task --force` re-creates a task's record, but the
    MONOTONIC heal counter must survive — else a task that accrued heal attempts (or was
    HARD-STOP escalated) could launder the cap to zero by re-creating itself."""

    def _poke_heal(self, slug: str, heal: dict) -> None:
        p = self._root() / "state.json"
        st = json.loads(p.read_text(encoding="utf-8"))
        st["tasks"][slug]["heal"] = heal
        p.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")

    def test_force_preserves_heal_counter(self):
        self._silent("new-task", "t")
        self._poke_heal("t", {"attempts": 2,
                              "history": [{"at": "2026-06-25", "reason": "tamper", "source": "scope-tamper"}]})
        self._silent("new-task", "t", "--force")
        self.assertEqual(self._attempts("t"), 2,
                         "the monotonic heal counter must survive a --force re-create")
        self.assertEqual(len(self._heal("t").get("history", [])), 1, "heal history preserved")
        self.assertEqual(self._task_state("t")["phase"], "direction",  # phase-collapse-3 seed
                         "the rest of the record still resets on a --force overwrite")

    def test_force_over_fresh_task_adds_no_heal(self):
        self._silent("new-task", "t")
        self._silent("new-task", "t", "--force")
        self.assertNotIn("heal", self._task_state("t"),
                         "--force must not fabricate a zero-counter on a task that never healed")

    def test_new_task_no_force_still_refuses_existing(self):
        self._silent("new-task", "t")
        _, err, code = self._run("new-task", "t")
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
