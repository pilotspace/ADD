#!/usr/bin/env python3
"""Red/green tests for reopen-transition (v20) - the engine `reopen` action.

`add.py reopen <slug> --to <phase> --reason "<text>"` returns an already-`done`
task to a named earlier phase with a NEVER-SILENT record and a reset gate. It is
the engine-enforced, recorded form of the backward-correction the flow already
permits (book ch02: "any phase may return to an earlier one"), applied to the one
state the diagram draws terminal. The 7-phase lifecycle contract is re-frozen:
`done` is terminal EXCEPT via this recorded action.

Behavior pinned (not words):
  - move done -> <phase>, gate -> "none", append a reopens entry, print it;
  - void a RISK-ACCEPTED verdict coherently: fold the live `waiver` into the
    reopens entry (prior_gate/prior_waiver) and DROP the live key;
  - refuse not-done / empty-reason / invalid-target with named codes;
  - the new verb is census-classified (test_min_pillar LIFECYCLE) and the engine
    re-anchors (md5(add.py) == engine_pin.ENGINE_MD5 across copies).

Arrange-through-CLI-contracts: the board is built with the real `add.main` calls,
so the tests exercise the engine's input contracts, not its internals.
ASCII-safe asserts (house rule).
Run: python3 -m unittest test_reopen_transition -v
"""
from __future__ import annotations

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

_TOOLING = Path(__file__).resolve().parent              # add-method/tooling
_ADD_METHOD = _TOOLING.parent                           # add-method
_REPO = _ADD_METHOD.parent                              # repo root

# Shipped lifecycle-doc surfaces the re-freeze must reach.
BOOK_CH02 = _ADD_METHOD / "docs" / "02-the-flow.md"     # canonical book chapter
LIVE_PROJECT = _REPO / ".add" / "PROJECT.md"            # the foundation survivor line

# add.py copies the shared pin guards (must stay byte-identical and == ENGINE_MD5).
ADD_PY_COPIES = [
    _ADD_METHOD / "tooling" / "add.py",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
]

WAIVER = ["--owner", "Tin", "--ticket", "T-1", "--expires", "2099-01-01"]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class ReopenBoard(unittest.TestCase):
    """A live board arranged through the real CLI."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-reopen-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["init", "--name", "demo"])
            add.main(["lock", "--force"])
            add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _task(self, slug: str) -> dict:
        return self._state()["tasks"][slug]

    def _run(self, *argv):
        """Run an add.main call; return (stdout, stderr, exit-code)."""
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _mk_done(self, slug: str, risk_accepted: bool = False):
        """Drive a fresh task ground -> verify -> done (PASS or RISK-ACCEPTED)."""
        self._run("new-task", slug, "--title", slug)
        for _ in range(6):                      # ground -> ... -> verify
            self._run("advance", slug)
        if risk_accepted:
            self._run("gate", "RISK-ACCEPTED", slug, *WAIVER)
        else:
            self._run("gate", "PASS", slug)
        assert self._task(slug)["phase"] == "done", "fixture: task did not reach done"

    def _mk_at(self, slug: str, phase: str):
        """A task parked at an arbitrary (non-done) phase."""
        self._run("new-task", slug, "--title", slug)
        self._run("phase", phase, slug)

    # ---- happy path -------------------------------------------------------
    def test_reopen_moves_done_task_to_phase(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "build",
                                   "--reason", "wiring check failed post-merge")
        self.assertEqual(code, 0, f"reopen should succeed; err={err!r}")
        self.assertEqual(self._task("t")["phase"], "build")
        # PHASES tuple is unchanged: done stays a state, not removed
        self.assertEqual(add.PHASES[-1], "done")
        self.assertEqual(len(add.PHASES), 9)

    def test_reopen_resets_gate_to_none(self):
        self._mk_done("t")
        self._run("reopen", "t", "--to", "build", "--reason", "x")
        t = self._task("t")
        self.assertEqual(t["gate"], "none")
        self.assertFalse(add._task_done(t), "a reopened task must not read as done")

    def test_reopen_records_reason_never_silent(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "build", "--reason", "criterion unmet")
        entry = self._task("t")["reopens"][-1]
        self.assertEqual(entry["from"], "done")
        self.assertEqual(entry["to"], "build")
        self.assertEqual(entry["reason"], "criterion unmet")
        self.assertTrue(entry.get("at"), "reopen entry must carry a timestamp")
        # announced on stdout (the never-silent surface beyond the data seam)
        low = out.lower()
        self.assertIn("reopen", low)
        self.assertIn("build", low)

    def test_reopen_appends_history(self):
        self._mk_done("t")
        self._run("reopen", "t", "--to", "verify", "--reason", "first")
        self._run("gate", "PASS", "t")          # re-complete: verify -> done
        self._run("reopen", "t", "--to", "build", "--reason", "second")
        reopens = self._task("t")["reopens"]
        self.assertEqual(len(reopens), 2, "reopens must append, never overwrite")
        self.assertEqual(reopens[0]["reason"], "first")
        self.assertEqual(reopens[1]["reason"], "second")

    def test_reopen_voids_and_records_waiver(self):
        self._mk_done("t", risk_accepted=True)
        self.assertIn("waiver", self._task("t"), "fixture: RISK-ACCEPTED must stamp a waiver")
        self._run("reopen", "t", "--to", "verify", "--reason", "waiver criterion unmet")
        t = self._task("t")
        self.assertNotIn("waiver", t, "the live waiver must be dropped (no verdict, no live waiver)")
        entry = t["reopens"][-1]
        self.assertEqual(entry["prior_gate"], "RISK-ACCEPTED")
        self.assertEqual(entry["prior_waiver"]["owner"], "Tin")
        self.assertEqual(entry["prior_waiver"]["ticket"], "T-1")

    # ---- rejections (named codes, state untouched) ------------------------
    def test_reopen_rejects_not_done(self):
        self._mk_at("t", "build")
        out, err, code = self._run("reopen", "t", "--to", "specify", "--reason", "x")
        self.assertNotEqual(code, 0)
        self.assertIn("reopen_not_done", err)
        self.assertEqual(self._task("t")["phase"], "build")  # unchanged

    def test_reopen_rejects_empty_reason(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "build", "--reason", "   ")
        self.assertNotEqual(code, 0)
        self.assertIn("reopen_reason_required", err)
        self.assertEqual(self._task("t")["phase"], "done")   # still done
        self.assertEqual(self._task("t")["gate"], "PASS")    # gate unchanged

    def test_reopen_rejects_invalid_target(self):
        self._mk_done("t")
        for bad in ("done", "bogus"):
            out, err, code = self._run("reopen", "t", "--to", bad, "--reason", "x")
            self.assertNotEqual(code, 0, f"--to {bad} must be refused")
            self.assertIn("reopen_target_invalid", err)
        self.assertEqual(self._task("t")["phase"], "done")   # still done

    # ---- the lifecycle re-freeze is documented ----------------------------
    def test_lifecycle_refreeze_documented(self):
        book = BOOK_CH02.read_text(encoding="utf-8").lower()
        self.assertIn("reopen", book, "book ch02 must name the reopen back-edge")
        self.assertIn("terminal", book, "book ch02 must state done is terminal except via reopen")
        proj = LIVE_PROJECT.read_text(encoding="utf-8").lower()
        self.assertIn("reopen", proj, "the PROJECT.md survivor line must name the reopen back-edge")

    # ---- instrument reaction + engine re-anchor ---------------------------
    def test_reopen_in_lifecycle_census(self):
        parser = add.build_parser()
        import argparse
        sub = [a for a in parser._actions
               if isinstance(a, argparse._SubParsersAction)][0]
        self.assertIn("reopen", set(sub.choices), "the parser must expose `reopen`")
        import test_min_pillar
        census = {argv[0] for argv in test_min_pillar.LIFECYCLE}
        self.assertIn("reopen", census, "reopen must be classified in the LIFECYCLE census")

    def test_engine_repinned(self):
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match the re-aimed engine_pin.ENGINE_MD5")


if __name__ == "__main__":
    unittest.main(verbosity=2)
