#!/usr/bin/env python3
"""Red/green tests for the spec-dialect floor (task spec-dialect-floor,
frozen contract v1, quality-floors milestone): when a frozen §3 carries a
value in a recognized format dialect (v1: aware ISO-8601 timestamps) and no
declared §4 test file speaks it, the tests->build crossing WARNS (print-only,
never refuses) and `add.py check` names the task in a `dialect_gap` audit.

Evidence class this closes (benchmark WV1 wm2 root cause): an arm's own suite
stayed green on NAIVE timestamps while the spec's own examples were Z-suffixed
— the aware/naive crash shipped green at 0.80 fidelity.

  M1 — _DIALECT_CLASSES closed registry in add_engine.constants (in __all__).
  M2 — _dialect_gaps PURE helper: §3 raw body vs declared §4 test files.
  M3 — the crossing warns per gap class, exit 0, state byte-identical (R1).
  M4 — bare dates (no T separator) never match (R2 dialect_false_positive).
  M5 — cmd_check lists gapped ACTIVE tasks under `dialect_gap`.

Run: python3 -m unittest test_spec_dialect_floor -v
"""
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

AWARE_CONTRACT = 'shape: booking { start_time: "2028-01-01T09:00:00Z" }'
NAIVE_CONTRACT = "shape: booking { created_on: 2028-01-01, note: plain date }"
NAIVE_TEST = 'def test_one():\n    assert create("2028-01-01 09:00") == 1\n'
AWARE_TEST = 'def test_one():\n    assert create("2028-01-01T09:00:00Z") == 1\n'


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board through the real CLI — the test_scope_repair_path idiom,
    duplicated per this repo's one-harness-per-file norm."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-dialect-floor-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")

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

    def _write_task(self, slug: str, contract_body: str):
        lines = [
            f"# TASK: {slug}",
            f"slug: {slug} · created: 2026-07-10 · stage: mvp",
            "phase: ground",
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_advance"),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT",
                      "```", contract_body, "```",
                      "Status: FROZEN @ v1 — approved by Tester 2026-07-10.",
                      "Least-sure flag surfaced at freeze: [contract] message "
                      "layer only — accepted."),
            *_section(4, "TESTS",
                      "Coverage target: behavior",
                      "Tests live in: `./tests/`"),
            *_section(5, "BUILD",
                      "Scope (may touch): `src/`",
                      "Safety rule (feature-specific): none",
                      "Code lives in: `./src/`"),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    def _cross(self, slug: str, contract_body: str, test_body: str):
        """Create a task with the given §3 fence + §4 test file and cross
        tests->build, capturing the crossing's output."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug, contract_body)
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(test_body, encoding="utf-8")
        self._silent("phase", "tests", slug)
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["advance", slug])      # tests -> build
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code


# ── M1: the registry is a named, closed trust surface ────────────────────────
class DialectRegistryTest(unittest.TestCase):
    def test_registry_shape_and_export(self):
        from add_engine import constants

        self.assertIn("_DIALECT_CLASSES", constants.__all__,
                      "a new trust surface must be named in __all__")
        names = [name for name, _ in constants._DIALECT_CLASSES]
        self.assertIn("aware-iso-timestamp", names)


# ── M3: gapped crossing warns but succeeds ────────────────────────────────────
class GappedCrossingTest(_Board):
    def test_gapped_crossing_warns_but_succeeds(self):
        out, err, code = self._cross("gapped", AWARE_CONTRACT, NAIVE_TEST)
        combined = out + err
        self.assertEqual(code, 0, "R1 floor_overreach: the crossing must NOT refuse")
        self.assertIn("aware-iso-timestamp", combined,
                      "the warning must name the dialect class")
        self.assertIn("re-cross", combined,
                      "the warning must carry the repair command")
        self.assertEqual(
            json.loads((self._root() / "state.json").read_text())
            ["tasks"]["gapped"]["phase"], "build",
            "state must be byte-identical to a clean crossing (phase advanced)")

    def test_covered_suite_is_silent(self):
        out, err, _ = self._cross("covered", AWARE_CONTRACT, AWARE_TEST)
        self.assertNotIn("aware-iso-timestamp", out + err,
                         "a suite speaking the dialect must not warn")


# ── M4: no-dialect contracts and bare dates stay silent ──────────────────────
class FalsePositiveTest(_Board):
    def test_no_dialect_contract_is_silent(self):
        out, err, _ = self._cross("plain", NAIVE_CONTRACT, NAIVE_TEST)
        self.assertNotIn("aware-iso-timestamp", out + err,
                         "R2 dialect_false_positive: bare dates must never match")


# ── M5: check names the gap in a dialect_gap audit ───────────────────────────
class CheckAuditTest(_Board):
    def test_check_names_dialect_gap_audit(self):
        self._cross("gapped", AWARE_CONTRACT, NAIVE_TEST)
        out, err, _ = self._run("check")
        combined = out + err
        self.assertIn("dialect_gap", combined, "check must expose the audit")
        self.assertIn("gapped", combined, "the gapped task must be named")

    def test_check_silent_when_covered(self):
        self._cross("covered", AWARE_CONTRACT, AWARE_TEST)
        out, err, _ = self._run("check")
        for line in (out + err).splitlines():
            if "dialect_gap" in line:
                self.assertNotIn("covered", line,
                                 "a covered task must not be audit-listed")


if __name__ == "__main__":
    unittest.main()
