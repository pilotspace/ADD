#!/usr/bin/env python3
"""Red/green for guide-fold (orientation-honesty, frozen §3 v1).

A COMPLETING `advance` that lands an agent INTO a working phase folds the landed
phase's guide chapter — the ONE `add.py guide` line the `next:` footer lacks (the
footer already carries command + short why) — as a `guide: .add/docs/<chapter>`
line right ABOVE the footer, plus a "don't re-run `add.py guide`" cue. This kills
the re-run-guide orientation habit WITHOUT duplicating the footer. Landing in
`done` folds nothing (Arm B owns that juncture); a bundle fast-forward folds only
once (the final landing).

Render-blind: every assertion reads printed stdout, never internals.
Run: python3 -m unittest test_guide_fold -v
"""
import hashlib
import io
import os
import shutil
import tempfile
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


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (the next-footer idiom)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-guide-fold-")).resolve()
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

    def _freeze(self, slug: str) -> None:
        p = self._task_md(slug)
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-07-14.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _write_test_file(self, slug: str):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(
            "def test_one():\n    assert 2 + 2 == 4\n", encoding="utf-8")

    @staticmethod
    def _fold_lines(out: str) -> list[str]:
        return [ln.strip() for ln in out.splitlines()
                if ln.strip().startswith("guide:") and ".add/docs/" in ln]

    @staticmethod
    def _next_lines(out: str) -> list[str]:
        return [ln.strip() for ln in out.splitlines() if ln.strip().startswith("next:")]


class GuideFoldTest(_Board):

    def test_advance_folds_landed_phase_chapter(self):
        self._silent("new-task", "foo")                  # active @ direction
        self._freeze("foo")                              # freeze-gate-universal sweep
        out, _, _ = self._run("advance", "foo")          # direction -> build (the ONE crossing)
        folds = self._fold_lines(out)
        self.assertEqual(len(folds), 1, f"exactly one guide-fold line, got: {folds!r}\n{out}")
        self.assertIn(".add/docs/07-step-5-build.md", folds[0],
                      "the fold carries the LANDED phase's chapter (build)")
        self.assertIn("add.py guide", folds[0],
                      "the fold names `add.py guide` as the thing not to re-run")
        # the footer is untouched — still exactly one next: line, still below the fold
        nxt = self._next_lines(out)
        self.assertEqual(len(nxt), 1, f"exactly one next: footer, got {nxt!r}")
        self.assertLess(out.index(folds[0]), out.index(nxt[0]),
                        "the fold prints ABOVE the next: footer")

    def test_fold_tracks_the_phase_it_lands_in(self):
        # a second landing folds a DIFFERENT chapter — build -> verify folds verify's chapter
        self._silent("new-task", "bar")
        self._freeze("bar")
        self._silent("advance", "bar")                   # direction -> build
        out, _, _ = self._run("advance", "bar")          # build -> verify
        folds = self._fold_lines(out)
        self.assertEqual(len(folds), 1, f"one fold, got {folds!r}\n{out}")
        self.assertIn(".add/docs/08-step-6-verify.md", folds[0],
                      "landing in verify folds verify's chapter, not build's")

    def test_landing_in_done_folds_nothing(self):
        # arm a task through to build, then advance build->verify and gate PASS (-> done)
        self._silent("new-task", "baz")
        self._freeze("baz")
        self._write_test_file("baz")
        self._silent("phase", "build", "baz")
        out_v, _, _ = self._run("advance", "baz")        # build -> verify (a fold IS expected here)
        self.assertTrue(self._fold_lines(out_v), "verify landing still folds a chapter")
        out_done, _, code = self._run("gate", "PASS", "baz")   # verify -> done
        self.assertEqual(code, 0, out_done)
        self.assertEqual(self._fold_lines(out_done), [],
                         "landing in done folds nothing — Arm B footer owns that juncture")


if __name__ == "__main__":
    unittest.main(verbosity=2)
