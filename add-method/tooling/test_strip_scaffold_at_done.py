#!/usr/bin/env python3
"""Red/green tests for strip-scaffold-at-done (drift-guard M3/2) — tidy a closed TASK.md.

A live TASK.md carries `<!-- … -->` instruction comments that guide the active phase; once the
task is `done` they are dead weight (PR40 audit). Frozen shape (§3 @ v1):
  - `_strip_live_scaffold(text)` removes `<!-- … -->` spans OUTSIDE fenced code blocks (```…```
    pass through byte-exact — the frozen §3 is never mutated), trims the trailing whitespace a
    removal leaves, collapses 3+ blank lines; idempotent;
  - cmd_gate calls it as the LAST step of a COMPLETING gate (PASS/RISK-ACCEPTED), atomic + degrade-safe;
  - INVARIANTS: add.py ×3 == re-pinned ENGINE_MD5; phases pool untouched.

Run: cd add-method/tooling && python3 -m unittest test_strip_scaffold_at_done -v
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ADD_PY_COPIES = [
    HERE / "add.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
]
_CANON_SKILL = HERE.parent / "skill" / "add"
PHASES_POOL = [
    "phases/0-setup.md", "phases/1-specify.md",
    "phases/2-scenarios.md", "phases/3-plan.md", "phases/4-tests.md",
    "phases/5-build.md", "phases/6-verify.md", "phases/7-observe.md",
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-strip-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

    def _silent(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                if e.code:
                    raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        buf = io.StringIO()
        code = 0
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), code

    def _task_md(self, slug: str) -> Path:
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _ready_to_gate(self, slug="t1"):
        self._silent("new-task", slug, "--title", "T")
        self._silent("phase", "verify", slug)

    def _ready_to_gate_pinned(self, slug="t1"):
        """new-task → freeze §3 → advance ground..verify, so a tamper TRIPWIRE is established
        (the snapshot is taken at tests→build). Needed to exercise the tripwire normalization."""
        self._silent("new-task", slug, "--title", "T")
        p = self._task_md(slug)
        p.write_text(p.read_text(encoding="utf-8").replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-30.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture — cost: none",
        ), encoding="utf-8")
        for _ in range(6):                      # ground → specify → … → verify
            self._silent("advance", slug)


class CompletingGateStrips(_Board):
    def test_pass_strips_instruction_comments(self):             # M1
        self._ready_to_gate("t1")
        p = self._task_md("t1")
        self.assertIn("<!--", p.read_text(encoding="utf-8"), "precondition: a live TASK.md has comments")
        self._silent("gate", "PASS", "t1")
        txt = p.read_text(encoding="utf-8")
        self.assertNotIn("<!--", txt, "a completing gate must strip the `<!-- -->` instruction comments")
        self.assertIn("## 1 ", txt, "authored content (section headings) must remain")
        self.assertIn("# TASK:", txt)

    def test_fenced_block_left_untouched(self):                  # M2, R:strip_corrupts_content
        self._ready_to_gate("t1")
        p = self._task_md("t1")
        txt = p.read_text(encoding="utf-8")
        # inject a fence containing a comment, plus a comment outside it
        txt += "\n## scratch\n<!-- strip-me -->\n```\n<!-- keep-me-in-fence -->\n```\n"
        p.write_text(txt, encoding="utf-8")
        self._silent("gate", "PASS", "t1")
        out = p.read_text(encoding="utf-8")
        self.assertIn("<!-- keep-me-in-fence -->", out, "a `<!-- -->` inside a fence must survive byte-exact")
        self.assertNotIn("strip-me", out, "a `<!-- -->` outside the fence must be removed")


class NonCompletingGateLeavesScaffold(_Board):
    def test_hard_stop_does_not_strip(self):                     # R:strip_on_noncompleting
        self._ready_to_gate("t1")
        self._silent("gate", "HARD-STOP", "t1")
        self.assertIn("<!--", self._task_md("t1").read_text(encoding="utf-8"),
                      "a HARD-STOP (task not done) must NOT strip the comments")


class ReopenReGateNotTampered(_Board):
    def test_reopen_regate_is_clean(self):                       # M5, R:strip_trips_tamper
        # gate once (strips the §3 instruction comment), reopen, re-gate — the tamper guard
        # must NOT read contract_tampered just because the comment was stripped.
        self._ready_to_gate_pinned("t1")        # establishes a tamper tripwire
        self._silent("gate", "PASS", "t1")
        self.assertNotIn("<!--", self._task_md("t1").read_text(encoding="utf-8"))
        self._silent("reopen", "t1", "--to", "verify", "--reason", "recheck")
        _, code = self._run("gate", "PASS", "t1")
        self.assertEqual(code, 0, "a reopened, re-gated stripped task must not be falsely tampered")


class StripHelperProperties(unittest.TestCase):
    def test_idempotent_and_content_safe(self):                  # M3
        strip = add._strip_live_scaffold
        live = "# T\nphase: x   <!-- marker -->\n\n<!-- block\nspanning -->\n\nkept line\n```\n<!-- fenced -->\n```\n"
        once = strip(live)
        self.assertNotIn("<!-- marker", once)
        self.assertNotIn("<!-- block", once)
        self.assertIn("<!-- fenced -->", once, "fenced comment is preserved")
        self.assertIn("kept line", once)
        self.assertNotIn("   \n", once, "trailing whitespace from a removal must be trimmed")
        self.assertEqual(strip(once), once, "strip must be idempotent")

    def test_inline_backtick_comment_survives(self):              # M1
        strip = add._strip_live_scaffold
        live = ("# T\nescape a literal `<!--...-->` in your text\n\n"
                "<!-- a real live comment -->\n\nkept line\n")
        out = strip(live)
        self.assertIn("`<!--...-->`", out, "an inline backtick-quoted comment must survive")
        self.assertNotIn("<!-- a real live comment", out,
                          "a genuine (non-backtick) comment must still be stripped")
        self.assertIn("kept line", out)

    def test_real_comment_still_stripped(self):                   # M2
        strip = add._strip_live_scaffold
        live = "# T\n<!-- EXIT: ground rules -->\n\nkept line\n"
        out = strip(live)
        self.assertNotIn("<!-- EXIT", out, "a genuine live comment is stripped exactly as before")
        self.assertIn("kept line", out)

    def test_stray_backtick_does_not_swallow_content(self):       # R1
        strip = add._strip_live_scaffold
        live = "# T\na stray ` backtick with no close on this line\n<!-- real comment -->\nkept line\n"
        out = strip(live)
        self.assertNotIn("<!-- real comment", out,
                          "a real comment after a stray backtick must still be stripped")
        self.assertIn("kept line", out)


class EnginePinnedAndPoolUntouched(unittest.TestCase):
    def test_engine_byte_identical_to_pin(self):                 # M4, R:engine_pin_drift
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match the re-pinned engine_pin.ENGINE_MD5")

    def test_phases_pool_untouched(self):                        # M4
        from test_skill_lean import POOLS
        phases = next(p for p in POOLS if p["name"] == "phases")
        target = int(phases["baseline"] * phases["ratio"])
        nbytes = sum(len((_CANON_SKILL / g).read_bytes())
                     for g in PHASES_POOL if (_CANON_SKILL / g).exists())
        self.assertLessEqual(nbytes, target, f"phases pool {nbytes} B must stay ≤ {target}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
