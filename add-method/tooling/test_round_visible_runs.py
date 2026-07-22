#!/usr/bin/env python3
"""Red/green tests for round-visible runs (task round-visible-runs).

A dynamic verify→fix workflow bounces a task verify→build repeatedly. Today only the
CHEAT-classed subset of those bounces is engine-visible (the bounded self-heal loop);
ordinary honest rounds are free play. This task records EVERY verify→build return trip
as a "round" — uncapped, observational, zero new verbs:

  - `add.py phase build` from verify increments tasks[slug].rounds {count, history}
    atomically with the phase write; `--note "finding"` annotates the round (M1/M2).
  - `--note` on a non-build target is refused: phase_note_build_only (R1).
  - a NON-exhausted heal return also counts a round with its source; the heal attempts
    counter/cap/exit semantics are byte-for-byte unchanged (M3).
  - `status` names `round N` when count > 0, silent at 0 (M4); the route-outcomes.jsonl
    gate trace carries "rounds" beside "heals" (M5).
  - rounds are monotonic and survive a `new-task --force` re-create (the F8
    force-preserve pattern); forward transitions never create the key.

Run: python3 -m unittest test_round_visible_runs -v
"""
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_ROUND_RE = re.compile(r"\bround \d+\b")


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (engine input contracts)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-rounds-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")

    def tearDown(self):
        os.chdir(self._cwd)

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
        return self._root() / "tasks" / slug / "PLAN.md"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _task_state(self, slug: str) -> dict:
        return self._state()["tasks"][slug]

    def _rounds(self, slug: str) -> dict:
        return self._task_state(slug).get("rounds") or {}

    _CONTRACT_BODY = "shape: rounds { count:int, history:[{at,source,note}] }"

    def _write_task(self, slug: str):
        flag = ("Least-sure flag surfaced at freeze: [contract] rounds are observational "
                "— they never gate — accepted as the visibility floor.")
        lines = [
            f"# PLAN: {slug}",
            f"slug: {slug} · created: 2026-06-11 · stage: mvp",
            "phase: ground",
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_phase · _heal_or_escalate"),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT", "```", self._CONTRACT_BODY, "```",
                      "Status: FROZEN @ v1 — approved by Tester 2026-06-11.", flag),
            *_section(4, "TESTS", "Coverage target: behavior", "Tests live in: `./tests/`"),
            *_section(5, "BUILD", "code"),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    _RED_TEST = "def test_one():\n    assert compute(2) == 4\n"

    def _write_test_file(self, slug: str):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(self._RED_TEST, encoding="utf-8")

    def _arm(self, slug: str):
        """Task with a frozen §3 + red test file, crossed tests->build (phase build)."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug)
        self._write_test_file(slug)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build (snapshot seam)

    def _to_verify(self, slug):
        self._silent("advance", slug)            # build -> verify

    def _bounce(self, slug, *extra):
        """One verify->build return trip via the admin phase verb."""
        return self._run("phase", "build", slug, *extra)


class RecordingTest(_Board):

    # M1 — the verify->build transition IS the round
    def test_phase_verify_to_build_records_round(self):
        self._arm("alpha")
        self._to_verify("alpha")
        out, err, code = self._bounce("alpha")
        self.assertEqual(code, 0, f"the return trip itself must succeed: {out}{err}")
        r = self._rounds("alpha")
        self.assertEqual(r.get("count"), 1, "one return trip == one round")
        self.assertEqual(len(r.get("history", [])), 1)
        entry = r["history"][0]
        self.assertEqual(entry.get("source"), "phase")
        self.assertIn("at", entry, "a round is timestamped")

    # M2 — the optional annotation (verbatim, padding included — §1 Boundary)
    def test_phase_note_stored_on_round(self):
        self._arm("alpha")
        self._to_verify("alpha")
        out, err, code = self._bounce("alpha", "--note", "  3 api tests red  ")
        self.assertEqual(code, 0, f"an annotated return must succeed: {out}{err}")
        self.assertEqual(self._rounds("alpha")["history"][0].get("note"),
                         "  3 api tests red  ", "the note is stored VERBATIM")

    # R1 — the flag is refused off the build target (contracted exit 2; whitespace counts)
    def test_note_refused_off_build_target(self):
        self._arm("alpha")
        before = self._task_state("alpha")
        for bad_note in ("x", "   "):
            out, err, code = self._run("phase", "verify", "alpha", "--note", bad_note)
            self.assertEqual(code, 2, f"--note {bad_note!r} off build must exit 2 (§3)")
            self.assertIn("phase_note_build_only", out + err,
                          "the refusal names its error code")
            self.assertEqual(self._task_state("alpha"), before,
                             "a refused entry leaves the task state byte-unchanged")

    # M3 — a heal return counts a round; the cheat cap is untouched
    def test_heal_return_counts_a_round_cap_unchanged(self):
        self._arm("alpha")
        self._to_verify("alpha")
        out, err, code = self._run("heal", "alpha", "--reason", "overfit to fixture")
        self.assertEqual(self._task_state("alpha")["phase"], "build",
                         "heal still returns the task to build")
        heal = self._task_state("alpha").get("heal") or {}
        self.assertEqual(heal.get("attempts"), 1, "heal attempts semantics unchanged")
        r = self._rounds("alpha")
        self.assertEqual(r.get("count"), 1, "a heal return is also a visible round")
        self.assertEqual(r["history"][0].get("source"), "refute-read",
                         "the round carries the heal source")

    # After — forward motion never creates the key
    def test_forward_transition_records_nothing(self):
        self._arm("alpha")                        # tests -> build crossed
        self._to_verify("alpha")                  # build -> verify
        self.assertNotIn("rounds", self._task_state("alpha"),
                         "a task that never bounced has NO rounds key")

    # After — the F8 force-preserve mirror
    def test_force_recreate_preserves_rounds(self):
        self._arm("alpha")
        self._to_verify("alpha")
        self._bounce("alpha")
        self.assertEqual(self._rounds("alpha").get("count"), 1)
        self._silent("new-task", "alpha", "--title", "alpha", "--force")
        self.assertEqual(self._rounds("alpha").get("count"), 1,
                         "rounds survive a --force re-create (F8 mirror)")


class SurfacingTest(_Board):

    # M4 — status names the round count (and only then)
    def test_status_surfaces_round_count(self):
        self._arm("alpha")
        out, _ = self._silent("status")
        self.assertIsNone(_ROUND_RE.search(out),
                          "an un-bounced task shows no round marker")
        self._to_verify("alpha")
        self._bounce("alpha")
        out, _ = self._silent("status")
        m = _ROUND_RE.search(out)
        self.assertIsNotNone(m, "a bounced active task surfaces its round count")
        self.assertEqual(m.group(0), "round 1")

    # M5 — the route trace carries rounds beside heals
    def test_route_trace_carries_rounds(self):
        self._arm("alpha")
        self._to_verify("alpha")
        self._bounce("alpha")                     # one visible round
        self._to_verify("alpha")
        self._run("gate", "PASS", "alpha")
        trace = self._root() / "traces" / "route-outcomes.jsonl"
        self.assertTrue(trace.is_file(), "gate writes the route trace")
        row = json.loads(trace.read_text(encoding="utf-8").strip().splitlines()[-1])
        self.assertEqual(row.get("rounds"), 1, "the trace row carries the round count")
        self.assertIn("heals", row, "rounds sits beside the existing heals field")


if __name__ == "__main__":
    unittest.main(verbosity=2)
