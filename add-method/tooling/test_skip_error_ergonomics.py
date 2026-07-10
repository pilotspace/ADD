#!/usr/bin/env python3
"""Red/green tests for skip-error ergonomics (task skip-error-ergonomics, frozen
contract v1): the two remaining bare orientation errors teach their own fix.

  M1 — a malformed `skips:` declaration dies naming the RAW declared value, the
       specific bad token(s), the computed allowed set (_SKIPPABLE_PHASES, not
       hardcoded), and the fix — keeping the `skip_not_allowed` prefix. The
       fail-closed whole-declaration discard is byte-identical.
  M2 — the no-project error hands the exact init command with flags.
  M3 — the read-only status degrade path stays silent.

Message layer ONLY. Run: python3 -m unittest test_skip_error_ergonomics -v
"""
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """Live board via the real CLI (sibling-suite idiom, one harness per file)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-skip-ergo-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue(), err.getvalue(), code

    def _silent(self, *argv):
        out, err, code = self._run(*argv)
        if code:
            raise AssertionError(f"{argv} exited {code}: {out}{err}")
        return out

    def _init_project(self):
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-milestone", "m1", "--title", "T", "--goal", "g")
        self._silent("milestone-confirm", "m1")

    def _task_md(self, slug):
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _write_task(self, slug, *, skips_line, rationale=""):
        ground = ["Anchors the contract cites: cmd_advance"]
        if rationale:
            ground.append(rationale)
        lines = [
            f"# TASK: {slug}",
            f"slug: {slug} · created: 2026-07-10 · stage: mvp · {skips_line}" if skips_line
            else f"slug: {slug} · created: 2026-07-10 · stage: mvp",
            "phase: ground",
            "",
            *_section(0, "GROUND", *ground),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT", "```", "GET /x -> 200", "```",
                      "Status: FROZEN @ v1 — approved by Tester.",
                      "Least-sure flag surfaced at freeze: [contract] smoke."),
            *_section(4, "TESTS", "Coverage target: behavior", "Tests live in: `./tests/`"),
            *_section(5, "BUILD", "Strategy (ordered batches): 1. build",
                      "Safety rule (feature-specific): none", "Code lives in: `./src/`"),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")


# ── M1: malformed skips names its repair ─────────────────────────────────────
class MalformedSkipsTest(_Board):

    def test_malformed_skips_names_repair(self):
        self._init_project()
        self._silent("new-task", "t1", "--title", "T")
        self._write_task("t1", skips_line="skips: specify,scenarios")
        self._silent("phase", "specify", "t1")
        out, err, code = self._run("advance", "t1")   # specify -> scenarios (skippable)
        blob = out + err
        self.assertNotEqual(code, 0, "fail-closed discard unchanged")
        self.assertIn("skip_not_allowed", blob, "the code prefix survives")
        self.assertIn("specify", blob, "the bad token is named")
        self.assertIn("skips: specify,scenarios", blob, "the raw declaration is echoed")
        for allowed in sorted(add._SKIPPABLE_PHASES):
            self.assertIn(allowed, blob, f"the allowed set names {allowed}")
        self.assertIn("remove", blob.lower(), "the fix (correct-or-remove) is stated")

    def test_valid_skip_unaffected(self):
        # UNDECLARED (no skips line) crossing — the universal default stays silent
        self._init_project()
        self._silent("new-task", "t2", "--title", "T")
        self._write_task("t2", skips_line=None)
        self._silent("phase", "specify", "t2")
        out, err, code = self._run("advance", "t2")
        self.assertEqual(code, 0, out + err)
        self.assertNotIn("skip_not_allowed", out + err)


# ── M2: the no-project error hands the exact init command ────────────────────
class NoProjectErrorTest(_Board):

    def test_no_project_error_hands_init(self):
        out, err, code = self._run("status")
        blob = out + err
        self.assertNotEqual(code, 0)
        self.assertIn("no .add/ project found", blob, "the recognizable lead survives")
        self.assertIn("add.py init --name", blob, "the exact command with flags")
        self.assertIn("--stage", blob)
        self.assertIn("mvp", blob, "the stage choices are enumerated")


# ── M3: read-only status degrades silently on a malformed declaration ────────
class StatusDegradeTest(_Board):

    def test_status_degrades_silently(self):
        self._init_project()
        self._silent("new-task", "t3", "--title", "T")
        self._write_task("t3", skips_line="skips: specify,scenarios")
        out, err, code = self._run("status")
        self.assertEqual(code, 0, "status never raises on a malformed declaration")
        self.assertNotIn("skip_not_allowed", out + err,
                         "the degrade path stays silent (advance is the enforcement point)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
