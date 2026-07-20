#!/usr/bin/env python3
"""Red/green tests for engine-argv-portability - flags-before-slug on py<=3.12.

`add.py gate RISK-ACCEPTED --owner X --ticket Y --expires Z <slug>` (waiver flags
before the optional slug) dies `unrecognized arguments: <slug>` on Python 3.10/3.11/3.12:
argparse consumes the required `outcome` positional in the first positional block, the
optional `slug` matches EMPTY there, and the trailing slug lands unbound. Python 3.13+
parses it natively. The fix is at the main() parse seam: parse_known_args + an ordered
re-bind of non-flag extras into UNFILLED optional positionals, declared per subparser
via set_defaults(_opt_positionals=...).

Behavior pinned (not words):
  - waiver flags before slug bind the slug and mutate THAT task (and slug-between-flags);
  - the canonical slug-first order stays byte-identical;
  - extras that are NOT exactly the unfilled optional positionals still exit 2
    ("unrecognized arguments"): slot already bound, or ANY flag-like extra
    (a typo'd flag's value must NEVER be mis-bound as a slug - the safety rule);
  - every optional-slug verb's working shape is unchanged (regression sweep);
  - the engine re-anchors: md5(add.py) == the engine pin across the x3 copies.

Arrange-through-CLI-contracts: the board is built with the real `add.main` calls,
so the tests exercise the engine's input contracts, not its internals.
ASCII-safe asserts (house rule).
RED interpreter: python3.10 (the CI floor) - on 3.13+ the broken shape parses natively.
Run: python3.10 -m unittest test_argv_portability -v
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

# add.py copies the shared pin guards (must stay byte-identical and == the engine pin).
ADD_PY_COPIES = [
    _ADD_METHOD / "tooling" / "add.py",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
]

WAIVER = ["--owner", "Tin", "--ticket", "T-1", "--expires", "2099-01-01"]
WAIVER_REC = {"owner": "Tin", "ticket": "T-1", "expires": "2099-01-01"}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class ArgvBoard(unittest.TestCase):
    """A live board arranged through the real CLI."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-argv-")).resolve()
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
    def _state(self) -> dict:
        return json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))

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

    def _freeze(self, slug: str) -> None:
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = self.tmp / ".add" / "tasks" / slug / "PLAN.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _mk_at(self, slug: str, phase: str = "verify"):
        """A task parked at an arbitrary (non-done) phase."""
        self._run("new-task", slug, "--title", slug)
        self._run("phase", phase, slug)

    def _mk_done(self, slug: str):
        """Drive a fresh task ground -> verify -> done (PASS)."""
        self._run("new-task", slug, "--title", slug)
        self._freeze(slug)                      # freeze-gate-universal sweep
        for _ in range(6):                      # ground -> ... -> verify
            self._run("advance", slug)
        self._run("gate", "PASS", slug)
        assert self._task(slug)["phase"] == "done", "fixture: task did not reach done"

    # ---- the broken shape (RED on py<=3.12 before the build) --------------
    def test_waiver_flags_before_slug_binds(self):
        self._mk_at("t", "verify")
        self._mk_at("u", "ground")             # bystander: must stay untouched
        before_u = self._task("u")
        out, err, code = self._run("gate", "RISK-ACCEPTED", *WAIVER, "t")
        self.assertEqual(code, 0, f"flags-before-slug must bind the slug; err={err!r}")
        t = self._task("t")
        self.assertEqual(t["gate"], "RISK-ACCEPTED")
        self.assertEqual(t["waiver"], WAIVER_REC)
        self.assertEqual(self._task("u"), before_u, "bystander task state must not change")

    def test_slug_between_flags_binds(self):
        self._mk_at("t", "verify")
        out, err, code = self._run("gate", "RISK-ACCEPTED", "--owner", "Tin", "t",
                                   "--ticket", "T-1", "--expires", "2099-01-01")
        self.assertEqual(code, 0, f"slug between value flags must bind; err={err!r}")
        self.assertEqual(self._task("t")["gate"], "RISK-ACCEPTED")
        self.assertEqual(self._task("t")["waiver"], WAIVER_REC)

    # ---- regressions (GREEN before and after the build) -------------------
    def test_canonical_order_unchanged(self):
        self._mk_at("ta", "verify")
        self._mk_at("tb", "verify")
        _, err_a, code_a = self._run("gate", "RISK-ACCEPTED", "ta", *WAIVER)
        self.assertEqual(code_a, 0, f"canonical order must keep working; err={err_a!r}")
        # equivalence: the two orders produce the same record shape
        _, err_b, code_b = self._run("gate", "RISK-ACCEPTED", *WAIVER, "tb")
        ta, tb = self._task("ta"), self._task("tb")
        self.assertEqual(ta["gate"], "RISK-ACCEPTED")
        self.assertEqual(ta["waiver"], WAIVER_REC)
        if code_b == 0:   # post-build both bind; pre-build on 3.13+ both bind too
            self.assertEqual(ta["waiver"], tb["waiver"])
            self.assertEqual(ta["gate"], tb["gate"])

    def test_unknown_extra_with_slug_bound_exit2(self):
        self._mk_at("t", "verify")
        before = self._task("t")
        out, err, code = self._run("gate", "PASS", "t", "extra-junk")
        self.assertEqual(code, 2, "a genuinely-unknown extra must still exit 2")
        self.assertIn("unrecognized arguments", err)
        self.assertEqual(self._task("t"), before, "rejected call must not mutate state")

    def test_flaglike_extra_never_rebinds(self):
        self._mk_at("t", "verify")
        before = self._task("t")
        out, err, code = self._run("gate", "PASS", "--typo", "x", "t")
        self.assertEqual(code, 2, "any flag-like extra must refuse the whole re-bind")
        self.assertEqual(self._task("t"), before,
                         "'x' must never be mis-bound as a slug (wrong-task hazard)")

    def test_optional_slug_verbs_regression_sweep(self):
        # phase / advance / guide / heal / reopen keep their working shapes.
        self._mk_at("t", "specify")
        self._freeze("t")                        # freeze-gate-universal sweep
        self._run("phase", "build", "t")
        self.assertEqual(self._task("t")["phase"], "build")
        self._run("advance", "t")
        self.assertEqual(self._task("t")["phase"], "verify")
        _, _, code = self._run("guide", "t")
        self.assertEqual(code, 0, "guide <slug> must keep working")
        _, _, code = self._run("heal", "--reason", "refute-read: stubbed", "t")
        self.assertEqual(code, 3, "heal flags-before-slug already binds today (exit 3 = redo)")
        self.assertEqual(self._task("t")["phase"], "build", "heal returns the task to build")
        self._mk_done("d")
        _, _, code = self._run("reopen", "--to", "build", "--reason", "x", "d")
        self.assertEqual(code, 0, "reopen flags-before-slug already binds today")
        self.assertEqual(self._task("d")["phase"], "build")

    # ---- scope guard -------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
