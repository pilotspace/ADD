#!/usr/bin/env python3
"""Red/green tests for the engine-sourced `next:` footer on mutating verbs
(task next-footer-engine, next-step-seams 1/3).

After every COMPLETING (exit-0) mutating verb the engine prints exactly ONE
`next: <command> — <why>` line, sourced from a single resolver `_next_footer`:
  Arm A — an active IN-FLIGHT task (gate=="none" AND phase!="done") -> the phase
          command (advance, or `gate …` at verify) + the PHASE_GUIDE why.
  Arm B — otherwise -> `_decide_next_base` (the SAME precedence the report renders),
          with the empty-rows branch reshaped command-first; fail-soft to
          `next: add.py status — re-orient` when no milestone / on any error.
The exit-3 HEAL paths (cmd_heal, gate->heal) are a redo signal, not a completion —
they keep their `return_to_build` seam and are OUT of the footer (human-confirmed).

Render-blind: every assertion reads the printed `next:` line, never internals.
Run: python3 -m unittest test_next_footer_engine -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent           # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"
ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")

# the completing (exit-0) mutating verbs the footer must cover (heal is OUT — exit-3 redo)
COMPLETING_VERBS = {
    "init", "lock", "new-milestone", "new-task", "advance", "phase", "use",
    "reopen", "gate", "set-milestone", "milestone-done", "stage",
    "archive-milestone", "compact",
}


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (the scope-gate-enforce idiom)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-next-footer-")).resolve()
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

    def _set_state(self, st: dict):
        (self._root() / "state.json").write_text(json.dumps(st), encoding="utf-8")

    # ---- footer parsing (render-blind) ------------------------------------
    @staticmethod
    def _next_lines(out: str) -> list[str]:
        return [ln.strip() for ln in out.splitlines() if ln.strip().startswith("next:")]

    def _footer(self, out: str) -> str:
        lines = self._next_lines(out)
        self.assertTrue(lines, f"expected a `next:` footer line, got:\n{out}")
        return lines[-1]

    # ---- arrangement (a frozen §3 + red test so tests->build snapshots) ----
    _CONTRACT_BODY = "shape: next footer { command, why }"

    def _write_task(self, slug: str):
        lines = [
            f"# TASK: {slug}",
            f"slug: {slug} · created: 2026-06-12 · stage: mvp",
            "phase: ground",
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_advance · cmd_gate"),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT",
                      "```", self._CONTRACT_BODY, "```",
                      "Status: FROZEN @ v1 — approved by Tester 2026-06-12.",
                      "Least-sure flag surfaced at freeze: [contract] the resolver reuses "
                      "the guide path — accepted as the single source."),
            *_section(4, "TESTS", "Coverage target: behavior", "Tests live in: `./tests/`"),
            *_section(5, "BUILD", "Strategy (ordered batches): 1. build",
                      "Safety rule (feature-specific): none", "Code lives in: `./src/`"),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    def _write_test_file(self, slug: str):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(
            "def test_one():\n    assert 2 + 2 == 4\n", encoding="utf-8")

    def _arm(self, slug: str):
        """Create the task and CROSS tests->build so the tripwire is snapshotted —
        a later `gate` then completes cleanly (nothing tampered)."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug)
        self._write_test_file(slug)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build
        return self._state()["tasks"][slug]

    def _gate(self, slug, outcome="PASS", *flags):
        """advance (build->verify) then gate — returns (out, err, code)."""
        self._silent("advance", slug)            # build -> verify
        return self._run("gate", outcome, slug, *flags)

    def _mark_exit_met(self, mslug: str):
        """Tick every exit criterion so _decide_next_base reads the milestone goal as MET
        (the all-done branch then says 'consolidate … archive-milestone', not 'goal not met')."""
        f = self._root() / "milestones" / mslug / "MILESTONE.md"
        txt = f.read_text(encoding="utf-8")
        head, sep, tail = txt.partition("## Exit criteria")
        f.write_text(head + sep + tail.replace("- [ ]", "- [x]"), encoding="utf-8")


# ── Arm A: the active in-flight task names its phase command ─────────────────
class FooterArmATest(_Board):

    def test_advance_footer_is_phase_command(self):
        self._silent("new-task", "foo")                  # active, ground
        out, _, _ = self._run("advance", "foo")          # ground -> specify
        footer = self._footer(out)
        self.assertTrue(footer.startswith("next: add.py advance"),
                        f"a front phase points at advance, got: {footer!r}")
        self.assertIn("state every rule", footer,
                      "the why is the specify-phase PHASE_GUIDE copy")
        self.assertIn("phase ground -> specify", out,
                      "the footer is ADDITIVE — the verb's result line survives")

    def test_advance_into_verify_footer_is_gate(self):
        self._silent("new-task", "foo")
        self._silent("phase", "build", "foo")
        out, _, _ = self._run("advance", "foo")          # build -> verify
        footer = self._footer(out)
        self.assertTrue(footer.startswith("next: add.py gate"),
                        f"verify points at the gate, not advance, got: {footer!r}")
        self.assertIn("PASS | RISK-ACCEPTED | HARD-STOP", footer)

    def test_new_task_footer_replaces_tail_no_double(self):
        out, _, _ = self._run("new-task", "foo")
        nxt = self._next_lines(out)
        self.assertEqual(len(nxt), 1, f"exactly one next: line, got {nxt!r}")
        self.assertTrue(nxt[0].startswith("next: add.py advance"),
                        "a fresh task at ground points at advance")
        self.assertIn("gather the real codebase", nxt[0],
                      "the why is the ground-phase PHASE_GUIDE copy")
        self.assertNotIn("then: add.py advance", out,
                         "the old ad-hoc tail converges onto the footer (no double-print)")


# ── Arm B: a gated/done active task hands off to the state-level resolver ─────
class FooterArmBTest(_Board):

    def test_gate_pass_routes_state_arm(self):
        self._arm("alpha")                               # active=alpha at build (in v1)
        self._silent("new-task", "beta")                 # active=beta
        self._silent("phase", "contract", "beta")
        self._silent("use", "alpha")                     # active=alpha again
        out, _, code = self._gate("alpha", "PASS")       # alpha -> done
        self.assertEqual(code, 0, out)
        footer = self._footer(out)
        self.assertIn("approve the contract of beta", footer,
                      "with alpha done, the state arm points at beta's contract")

    def test_gate_pass_all_done_consolidate(self):
        self._arm("alpha")
        self._mark_exit_met("v1")                        # goal met -> archive, not 'goal not met'
        out, _, code = self._gate("alpha", "PASS")       # the only task -> all done
        self.assertEqual(code, 0, out)
        self.assertIn("archive-milestone v1", self._footer(out),
                      "the last task done points at consolidation/archive")

    def test_gate_hardstop_routes_arm_b(self):
        self._arm("alpha")
        out, _, _ = self._gate("alpha", "HARD-STOP")     # gate=HARD-STOP, phase=verify, not done
        nxt = self._next_lines(out)
        self.assertEqual(len(nxt), 1, f"exactly one next: line, got {nxt!r}")
        self.assertEqual(nxt[0], "next: resolve HARD-STOP on alpha [human gate]",
                         "Arm B HARD-STOP is a human decision point (gate-owner-marker fills the slot: [human gate])")
        self.assertNotIn("HARD-STOP recorded", out,
                         "the bespoke return-to-BUILD hint converges, never double-prints")

    def test_new_milestone_empty_names_command(self):
        out, _, _ = self._run("new-milestone", "bar", "--title", "B", "--goal", "g")
        footer = self._footer(out)
        self.assertIn("decompose into tasks", footer)
        self.assertIn("add.py new-task bar", footer,
                      "an empty milestone names the decompose command (not 'none — no tasks yet')")
        self.assertNotIn("none — no tasks yet", out,
                         "the empty-rows branch is reshaped command-first")


# ── fail-soft: a footer never turns a saved mutation into a crash ────────────
class FooterFailSoftTest(_Board):

    def test_failsoft_no_active_milestone(self):
        self._arm("alpha")
        self._gate("alpha", "PASS")                      # alpha done, active=alpha
        st = self._state()
        st["active_milestone"] = None                    # the report path would _die on this
        st["tasks"]["alpha"]["milestone"] = None         # milestone-less -> milestone-aware use stays scalar-only (no re-activation)
        self._set_state(st)
        out, err, code = self._run("use", "alpha")       # a mutating verb, Arm B, no milestone
        self.assertEqual(code, 0, f"the verb still completes: {err}")
        self.assertEqual(self._footer(out), "next: add.py status — re-orient",
                         "no active milestone degrades to the generic re-orient line")


# ── the reserved driver-marker slot is now FILLED by the sibling gate-owner-marker ──
class FooterMarkerTest(_Board):

    def test_marker_slot_filled(self):
        # gate-owner-marker filled the slot next-footer-engine reserved: `new-task foo`
        # lands at ground (owner ai) under the default `auto` rung -> the AI drives.
        out, _, _ = self._run("new-task", "foo")
        footer = self._footer(out)
        self.assertTrue(footer.endswith(" [you drive]"),
                        f"the reserved slot now names the driver, got: {footer!r}")


# ── the exit-criterion sweep: every completing verb ends in one next: line ───
class FooterSweepTest(_Board):

    def _fresh(self, *init_args) -> str:
        """init in a throwaway dir and return the verb's stdout; restore cwd."""
        d = Path(tempfile.mkdtemp(prefix="add-sweep-")).resolve()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        prev = Path.cwd()
        os.chdir(d)
        try:
            out, _, _ = self._run("init", "--name", "x", *init_args)
            return d, out
        finally:
            os.chdir(prev)

    def test_every_completing_verb_prints_one_next(self):
        covered: dict[str, str] = {}

        # --- lightweight verbs in the main board (v1 active) ---
        covered["new-milestone"] = self._run("new-milestone", "m2", "--title", "M2", "--goal", "g")[0]
        covered["new-task"] = self._run("new-task", "t1")[0]          # active t1 (m2), ground
        covered["advance"] = self._run("advance", "t1")[0]            # ground -> specify
        covered["phase"] = self._run("phase", "scenarios", "t1")[0]
        self._silent("new-task", "t2")                               # active t2
        covered["use"] = self._run("use", "t1")[0]                   # active t1
        covered["set-milestone"] = self._run("set-milestone", "t2", "m2")[0]
        covered["stage"] = self._run("stage", "poc")[0]

        # --- gate + reopen via a proper cross-to-build ---
        self._silent("new-milestone", "mg", "--title", "MG", "--goal", "g")
        self._arm("ag")
        covered["gate"] = self._gate("ag", "PASS")[0]               # ag -> done
        covered["reopen"] = self._run("reopen", "ag", "--to", "build", "--reason", "redo")[0]

        # --- milestone-done + archive + compact via a met-goal done milestone ---
        self._silent("new-milestone", "md", "--title", "MD", "--goal", "g")
        self._arm("md1")
        self._gate("md1", "PASS")                                   # md1 -> done
        self._mark_exit_met("md")
        covered["milestone-done"] = self._run("milestone-done", "md")[0]
        covered["archive-milestone"] = self._run("archive-milestone", "md")[0]
        covered["compact"] = self._run("compact", "md")[0]

        # --- init + lock in fresh dirs ---
        _, covered["init"] = self._fresh()
        ld = Path(tempfile.mkdtemp(prefix="add-sweep-lock-")).resolve()
        self.addCleanup(shutil.rmtree, ld, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        prev = Path.cwd()
        os.chdir(ld)
        try:
            self._run("init", "--name", "x", "--await-lock")
            covered["lock"] = self._run("lock")[0]
        finally:
            os.chdir(prev)

        # every covered verb prints EXACTLY one next: line
        for verb, out in covered.items():
            nxt = self._next_lines(out)
            self.assertEqual(len(nxt), 1,
                             f"verb '{verb}' must end with exactly one next: line, got {nxt!r}\n{out}")

        # …and the sweep covers the FULL completing-verb list (never silently shrinks)
        self.assertEqual(set(covered), COMPLETING_VERBS,
                         "the sweep must exercise every completing mutating verb")


# ── the discipline: ×3 parity + pin re-aimed at this task ────────────────────
class EnginePinTest(unittest.TestCase):
    def test_mirrors_and_pin(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1, "add.py trio diverged")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "engine_pin.ENGINE_MD5 must track the live engine")

    def test_pin_annotation_names_this_task(self):
        src = (HERE / "engine_pin.py").read_text(encoding="utf-8")
        self.assertIn("re-aimed @ next-footer-engine", src,
                      "the pin annotation records this task's deliberate re-aim")


if __name__ == "__main__":
    unittest.main(verbosity=2)
