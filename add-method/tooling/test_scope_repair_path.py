#!/usr/bin/env python3
"""Red/green tests for the scope-gate repair path (task scope-gate-repair-path,
frozen contract v1): a scope_violation names its own exact repair, and the
tests->build crossing warns when §5 Scope is still the template default.

  M1 — _build_entry prints a warning when the declared §5 Scope line still
       carries the template placeholder ("<fill before the §3 freeze") — the
       `./src/` token resolves to the TASK dir, not the project, so the default
       silently arms a guaranteed scope_violation. Crossing behavior otherwise
       byte-identical (exit, snapshot, state).
  M2 — a scope_violation heal (source "scope") prints the exact 3-step repair:
       edit the §5 Scope line · add.py re-cross --by <name> · advance + gate.
  M3 — tamper advice stays as today; HEAL_CAP/exit-code mechanics untouched.

Message layer ONLY — every enforcement assert here pins today's behavior.
Run: python3 -m unittest test_scope_repair_path -v
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

SCOPED_SRC = "Scope (may touch): `src/`"
TEMPLATE_SCOPE = ("Scope (may touch): `./src/`   <fill before the §3 freeze — "
                  "every file the build may write>")


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board through the real CLI — the test_scope_violation_heal idiom,
    duplicated per this repo's one-harness-per-file norm."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-scope-repair-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")
        for rel, body in (("src/app.py", "APP = 1\n"),
                          ("other/readme.txt", "hello\n")):
            p = self.tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")

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

    def _task_state(self, slug: str) -> dict:
        return self._state()["tasks"][slug]

    _CONTRACT_BODY = "shape: scope repair { message, recipe }"

    def _write_task(self, slug: str, *, scope_line=None):
        five = ["Strategy (ordered batches): 1. build",
                "Safety rule (feature-specific): none",
                "Code lives in: `./src/`"]
        if scope_line is not None:
            five.insert(0, scope_line)
        lines = [
            f"# TASK: {slug}",
            f"slug: {slug} · created: 2026-07-10 · stage: mvp",
            "phase: ground",
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_advance · cmd_gate"),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT",
                      "```", self._CONTRACT_BODY, "```",
                      "Status: FROZEN @ v1 — approved by Tester 2026-07-10.",
                      "Least-sure flag surfaced at freeze: [contract] message layer "
                      "only — accepted."),
            *_section(4, "TESTS",
                      "Coverage target: behavior",
                      "Tests live in: `./tests/`"),
            *_section(5, "BUILD", *five),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    def _write_test_file(self, slug: str):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(
            "def test_one():\n    assert compute(2) == 4\n", encoding="utf-8")

    def _cross(self, slug: str, scope_line):
        """Create the task with the given §5 Scope line and cross tests->build,
        capturing the crossing's stdout+stderr."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug, scope_line=scope_line)
        self._write_test_file(slug)
        self._silent("phase", "tests", slug)
        return self._silent("advance", slug)     # tests -> build

    def _to_verify_and_gate(self, slug):
        self._silent("advance", slug)
        return self._run("gate", "PASS", slug)


# ── M1: the crossing warns on a template-default scope line ──────────────────
class DefaultScopeWarningTest(_Board):

    def test_default_scope_crossing_warns(self):
        out, err = self._cross("alpha", TEMPLATE_SCOPE)
        blob = out + err
        self.assertIn("template default", blob,
                      f"crossing must name the still-default §5 line: {blob!r}")
        self.assertIn("re-cross --by", blob,
                      "the warning must carry the repair command")
        st = self._task_state("alpha")
        self.assertEqual(st["phase"], "build", "the warning never blocks the crossing")
        self.assertIn("scope", st, "the snapshot is still taken exactly as today")

    def test_real_scope_crossing_silent(self):
        out, err = self._cross("beta", SCOPED_SRC)
        self.assertNotIn("template default", out + err,
                         "a real declaration draws no warning")

    def test_undeclared_scope_crossing_silent(self):
        out, err = self._cross("gamma", None)
        self.assertNotIn("template default", out + err,
                         "UNDECLARED stays grandfathered and silent")


# ── M2: the violation names its own repair ───────────────────────────────────
class ViolationRepairRecipeTest(_Board):

    def test_scope_violation_names_repair(self):
        self._cross("alpha", SCOPED_SRC)
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha")
        blob = out + err
        self.assertEqual(code, 3, "exit code unchanged (redo signal)")
        self.assertIn("scope_violation", blob)
        self.assertIn("§5 Scope", blob, "step 1: edit the §5 Scope line")
        self.assertIn("re-cross --by", blob, "step 2: the exact re-snapshot command")
        self.assertIn("gate PASS", blob, "step 3: advance + gate")
        heal = self._task_state("alpha").get("heal") or {}
        self.assertEqual(heal.get("attempts"), 1, "heal counter mechanics untouched")


# ── M3: tamper advice unchanged ──────────────────────────────────────────────
class TamperAdviceUnchangedTest(_Board):

    def test_tamper_advice_unchanged(self):
        self._cross("alpha", SCOPED_SRC)
        # tamper the tripwired red test file (the tripwire, not the scope, fires)
        (self._root() / "tasks" / "alpha" / "tests" / "test_demo.py").write_text(
            "def test_one():\n    assert True\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha")
        blob = out + err
        self.assertEqual(code, 3)
        self.assertIn("return_to_build", blob)
        self.assertIn("Revert the tampered file", blob,
                      "non-scope advice is byte-identical to today")
        self.assertNotIn("re-cross --by", blob,
                         "the scope recipe never leaks into tamper advice")


if __name__ == "__main__":
    unittest.main(verbosity=2)
