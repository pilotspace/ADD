#!/usr/bin/env python3
"""invariants-publish: a §3 that publishes an invariant must cite the test that
proves it, and the freeze refuses one that does not.

WHY THIS EXISTS. PROJECT.md carries project-wide `invariants:` that bind every
task, but a TASK has no way to publish an invariant of its own — so a downstream
node inherits nothing, and "the payout timeout is bounded" lives in prose that
no build is answerable to. An invariant nobody can fail is a comment.

The refusal is the whole point. A published invariant with no proving test is
exactly the `turn_ceiling` failure mode this project has already paid for once:
declared in every arm, asserted equal by a test, read by nothing. Citing a test
file that does not exist is the same failure wearing a citation.

Grandfathered by absence: a §3 with no `Invariants (published):` block freezes
exactly as it does today. The floor is opt-in, and opting in is what binds you.

Run:
    python3 -m unittest test_invariants_publish -v
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"
REPO = HERE.parents[1]

TEMPLATES = (
    "add-method/tooling/templates/PLAN.md.tmpl",
    ".add/tooling/templates/PLAN.md.tmpl",
    "add-method/.add/tooling/templates/PLAN.md.tmpl",
    "add-method/src/add_method/_bundled/tooling/templates/PLAN.md.tmpl",
)

_FLAG = ("Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none")


def _run(cwd, *args, timeout=120):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=str(cwd),
                          capture_output=True, text=True, timeout=timeout)


class _Project(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        r = _run(self.root, "init", "--name", "inv", "--stage", "mvp")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        _run(self.root, "lock")
        _run(self.root, "new-task", "widget", "--title", "Widget")
        self.task_md = self.root / ".add" / "tasks" / "widget" / "PLAN.md"
        (self.root / "tests").mkdir(exist_ok=True)
        (self.root / "tests" / "test_widget.py").write_text("def test_bound(): pass\n")

    def tearDown(self):
        self._tmp.cleanup()

    def _draft(self, invariants: str = ""):
        """A §3 that satisfies every EXISTING freeze floor, plus `invariants`."""
        s = self.task_md.read_text()
        s = s.replace(
            "Boundary: <one format-variant per external input shape the tests must speak "
            "— e.g. aware vs naive timestamp · or \"none — no external input\">",
            "Boundary: `int` only — one format variant.")
        s = s.replace("Status: DRAFT", f"{invariants}Status: DRAFT\n{_FLAG}")
        # Replace the WHOLE template contract fence — leaving any of it behind trips
        # contract_not_drafted, which fires before the floor under test.
        s = re.sub(r"```\n<METHOD>.*?\n```", "```\ncount(items: list) -> int\n```",
                   s, count=1, flags=re.S)
        s = re.sub(r"(?m)^Target \(measurable\): <.*$",
                   "Target (measurable): count([1,2]) == 2.", s, count=1)
        self.task_md.write_text(s, encoding="utf-8")

    def _freeze(self):
        return _run(self.root, "freeze", "widget", "--by", "Tester")


class TheFloorBites(_Project):
    def test_invariant_without_a_proof_refuses_the_freeze(self):  # M1 R1
        self._draft("Invariants (published):\n"
                    "  - the payout timeout is bounded\n\n")
        r = self._freeze()
        self.assertNotEqual(r.returncode, 0, "an unproven invariant froze")
        self.assertIn("invariant_without_proof", r.stderr + r.stdout)

    def test_invariant_citing_a_missing_test_refuses(self):  # M2 R1
        self._draft("Invariants (published):\n"
                    "  - the payout timeout is bounded (proof: `tests/nope.py::test_x`)\n\n")
        r = self._freeze()
        self.assertNotEqual(r.returncode, 0, "a citation to nothing froze")
        self.assertIn("invariant_without_proof", r.stderr + r.stdout)

    def test_refusal_names_the_offending_invariant(self):  # M1
        self._draft("Invariants (published):\n"
                    "  - the payout timeout is bounded\n\n")
        r = self._freeze()
        self.assertIn("payout timeout", r.stderr + r.stdout,
                      "the refusal must name WHICH invariant is unproven")

    def test_the_freeze_writes_nothing_on_refusal(self):  # M1
        self._draft("Invariants (published):\n  - unproven thing\n\n")
        before = self.task_md.read_bytes()
        self._freeze()
        self.assertEqual(self.task_md.read_bytes(), before,
                         "validate-then-write broken: a refused freeze wrote")


class TheFloorLetsGoodWorkThrough(_Project):
    def test_a_proven_invariant_freezes(self):  # M3
        self._draft("Invariants (published):\n"
                    "  - the payout timeout is bounded (proof: `tests/test_widget.py::test_bound`)\n\n")
        r = self._freeze()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("FROZEN @", self.task_md.read_text())

    def test_no_invariants_block_is_grandfathered(self):  # M4
        # Absence must never become a new refusal — every task on disk predates this.
        self._draft()
        r = self._freeze()
        self.assertEqual(r.returncode, 0,
                         "a §3 with no Invariants block must freeze exactly as before:\n"
                         + r.stderr + r.stdout)

    def test_several_invariants_all_proven(self):  # M3 [edge]
        self._draft("Invariants (published):\n"
                    "  - a (proof: `tests/test_widget.py::test_bound`)\n"
                    "  - b (proof: `tests/test_widget.py::test_bound`)\n\n")
        self.assertEqual(self._freeze().returncode, 0)

    def test_one_bad_apple_among_proven_ones_still_refuses(self):  # M1 [edge]
        self._draft("Invariants (published):\n"
                    "  - a (proof: `tests/test_widget.py::test_bound`)\n"
                    "  - b has no proof at all\n\n")
        r = self._freeze()
        self.assertNotEqual(r.returncode, 0, "a partly-proven block was allowed through")
        self.assertIn("invariant_without_proof", r.stderr + r.stdout)


class TheTemplateOffersIt(unittest.TestCase):
    def test_every_template_twin_carries_the_block(self):  # M5
        digests = set()
        for rel in TEMPLATES:
            p = REPO / rel
            self.assertTrue(p.exists(), f"missing template twin: {rel}")
            text = p.read_text()
            self.assertIn("Invariants (published)", text,
                          f"{rel} never offers the block, so nobody will publish one")
            digests.add(text)
        self.assertEqual(len(digests), 1, "template twins drifted")

    def test_the_template_block_is_commented_out_or_optional(self):  # M4
        # The scaffold must not make every new task publish an invariant — the
        # template's own line has to freeze as-is.
        text = (REPO / TEMPLATES[0]).read_text()
        idx = text.index("Invariants (published)")
        window = text[max(0, idx - 200):idx + 200]
        self.assertTrue("optional" in window.lower() or "<!--" in window,
                        "the template block must read as OPTIONAL, or a bare new task "
                        f"cannot freeze; got: {window!r}")


if __name__ == "__main__":
    unittest.main()
