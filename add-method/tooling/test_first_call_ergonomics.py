#!/usr/bin/env python3
"""Red/green tests for first-call ergonomics (task first-call-ergonomics, frozen
contract v1): a headless agent's FIRST attempt at each engine verb succeeds or
is redirected in the same stdout, never via a repair loop.

  M1 — post-freeze, every next-command surface (the freeze footer, plain status,
       and `guide`'s `then:` line) names `add.py advance`, never `freeze --by`
       again — while a still-DRAFT §3 at `contract` keeps teaching freeze.
  M2 — an exact-state retry (freeze on an already-FROZEN §3 · lock on an
       already-locked setup without --force · advance on a task already `done`)
       is an exit-0 no-op: it restates the state + the true next command and
       writes ZERO bytes to state.json / TASK.md.
  M3 — `init`'s success stdout ends with a copy-pasteable `kickoff:` hand-off
       (new-milestone -> new-task -> advance --to contract, flags included).

One test per §2 scenario. Run: python3 -m unittest test_first_call_ergonomics -v
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

_DRAFT_FLAGGED = (
    "\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\n"
    "Status: DRAFT\n"
    "Least-sure flag surfaced at freeze:\n"
    "  ⚠ [contract] the id encoding is the least-sure part — cost if wrong: a reparse.\n"
)


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Harness(unittest.TestCase):
    """A live board arranged through the real CLI (matches the sibling suites'
    own fixture conventions — test_freeze_command.py's _Harness + test_next_footer
    _engine.py's _Board — duplicated here per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fce-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")

    # ---- CLI helpers -------------------------------------------------------
    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))

    def _state_bytes(self):
        return (self.tmp / ".add" / "state.json").read_bytes()

    def _task_md(self, slug):
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _task_md_bytes(self, slug):
        return self._task_md(slug).read_bytes()

    def _section3(self, slug):
        return add._phase_spans(self._task_md(slug).read_text(encoding="utf-8")).get(3, "")

    def _set_section3(self, slug, body):
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(## 3 · PLAN[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        new = re.sub(r"(?m)^Boundary: <[^\n]*$",
                     "Boundary: none — no external input", new, count=1)
        p.write_text(new, encoding="utf-8")

    def _new_task_at_contract(self, slug="t", drafted=_DRAFT_FLAGGED):
        """Lock, a milestone + task, jump to `plan` (plan-phase-core: ground+contract
        collapsed into ONE `plan` phase), and replace §3 with `drafted`."""
        self._silent("lock", "--force")
        if "m" not in self._state().get("milestones", {}):
            self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "plan", slug)
        if drafted is not None:
            self._set_section3(slug, drafted)

    # ---- full-lifecycle scaffold (mirrors test_next_footer_engine.py's _Board) --
    _CONTRACT_BODY = "shape: next footer { command, why }"

    def _write_full_task(self, slug):
        lines = [
            f"# TASK: {slug}",
            f"slug: {slug} · created: 2026-07-09 · stage: mvp",
            "phase: ground",
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_advance · cmd_gate"),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT",
                      "```", self._CONTRACT_BODY, "```",
                      "Status: FROZEN @ v1 — approved by Tester 2026-07-09.",
                      "Least-sure flag surfaced at freeze: [contract] the resolver reuses "
                      "the guide path — accepted as the single source."),
            *_section(4, "TESTS", "Coverage target: behavior", "Tests live in: `./tests/`"),
            *_section(5, "BUILD", "Strategy (ordered batches): 1. build",
                      "Safety rule (feature-specific): none", "Code lives in: `./src/`"),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    def _write_test_file(self, slug):
        d = self.tmp / ".add" / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(
            "def test_one():\n    assert 2 + 2 == 4\n", encoding="utf-8")

    def _drive_to_done(self, slug):
        """new-task -> ... -> build -> verify -> gate PASS -> done, via the real CLI."""
        self._silent("lock", "--force")
        self._silent("new-task", slug, "--title", slug)
        self._write_full_task(slug)
        self._write_test_file(slug)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build
        self._silent("advance", slug)            # build -> verify
        self._silent("gate", "PASS", slug)        # verify -> done


# ── M1: post-freeze next-command truth on every surface ──────────────────────
class PostFreezeNextCommandTest(_Harness):
    def test_post_freeze_footer_names_advance(self):
        self._new_task_at_contract("t")
        freeze_out = self._silent("freeze")
        status_out = self._silent("status")
        guide_out = self._silent("guide")
        for label, out in (("freeze footer", freeze_out), ("status", status_out),
                           ("guide", guide_out)):
            self.assertIn("add.py advance", out, f"{label} must name advance: {out!r}")
            self.assertNotIn("freeze --by", out, f"{label} must not re-teach freeze: {out!r}")

    def test_pre_freeze_contract_still_teaches_freeze(self):
        self._new_task_at_contract("t")          # §3 stays DRAFT (never frozen)
        status_out = self._silent("status")
        guide_out = self._silent("guide")
        for label, out in (("status", status_out), ("guide", guide_out)):
            self.assertIn("add.py freeze --by <name>", out,
                          f"{label} must still teach freeze pre-freeze: {out!r}")


# ── M2: exact-state retries are exit-0 no-ops, zero bytes written ────────────
class ExactRetryNoopTest(_Harness):
    def test_refreeze_is_exit0_noop(self):
        self._new_task_at_contract("t")
        self._silent("freeze")
        state_before = self._state_bytes()
        task_before = self._task_md_bytes("t")
        out, code = self._run("freeze")
        self.assertEqual(code, 0, out)
        self.assertIn("v1", out)
        self.assertIn("change request", out)
        self.assertIn("next: add.py advance", out)
        self.assertEqual(self._state_bytes(), state_before, "state.json must be byte-identical")
        self.assertEqual(self._task_md_bytes("t"), task_before, "TASK.md must be byte-identical")

    def test_relock_is_exit0_noop(self):
        # explicit await-lock -> explicit first lock, so the retry below targets a
        # REAL prior lock (not the grandfathered-locked default the harness setUp seeds).
        self._silent("init", "--name", "demo", "--await-lock", "--force")
        self._silent("lock", "--by", "Tin")
        state_before = self._state_bytes()
        out, code = self._run("lock", "--by", "Tin")
        self.assertEqual(code, 0, out)
        self.assertIn("already locked", out)
        self.assertEqual(self._state_bytes(), state_before, "state.json must be byte-identical")
        # --force still re-locks
        out2, code2 = self._run("lock", "--by", "Tin", "--force")
        self.assertEqual(code2, 0, out2)
        self.assertTrue(self._state()["setup"]["locked"])

    def test_advance_at_done_is_exit0_noop(self):
        self._drive_to_done("t")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")
        state_before = self._state_bytes()
        out, code = self._run("advance", "t")
        self.assertEqual(code, 0, out)
        self.assertIn("task 't' is done", out)
        self.assertIn("next:", out)
        self.assertEqual(self._state_bytes(), state_before, "bare advance must write nothing")
        out2, code2 = self._run("advance", "t", "--fill", "/nonexistent/path/should-not-be-read")
        self.assertEqual(code2, 0, out2)
        self.assertIn("task 't' is done", out2)
        self.assertEqual(self._state_bytes(), state_before, "--fill advance must write nothing")


# ── M3: init hands off the kickoff sequence ──────────────────────────────────
class InitKickoffTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fce-init-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def test_init_prints_kickoff_handoff(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["init", "--name", "X", "--stage", "mvp"])
        out = buf.getvalue()
        # kickoff-truth v1 STRENGTHENED this pin: the hand-off is now lane-aware —
        # the single-task lane leads (the cheapest measured benchmark run skipped
        # the milestone), the multi-task milestone lines follow, same command set.
        self.assertIn("kickoff (single task):", out)
        self.assertIn("--oneshot", out)
        self.assertIn("kickoff (multi-task milestone):", out)
        self.assertIn("new-milestone", out)
        self.assertIn("--title", out)
        self.assertIn("--goal", out)
        self.assertIn("new-task", out)
        self.assertIn("--milestone", out)
        # phase-collapse-3: the handoff teaches the 3-call walk, not a --to bundle step
        self.assertIn("freeze --by <name> --cross", out)
        self.assertIn("gate PASS", out)


# ── R1: the floor guards stay loud errors ────────────────────────────────────
class FloorGuardsStillDieTest(_Harness):
    def test_undrafted_freeze_still_dies(self):
        self._new_task_at_contract("t", drafted=None)   # §3 still the unfilled template
        out, code = self._run("freeze")
        self.assertNotEqual(code, 0)
        self.assertIn("contract_not_drafted", out)
        self.assertNotIn("freeze", self._state()["tasks"]["t"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
