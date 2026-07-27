#!/usr/bin/env python3
"""design-at-build: a node that PUBLISHES invariants cannot record a completing
gate without a DESIGN.md beside its PLAN.md.

WHY IT IS TIED TO PUBLISHING. PLAN.md deliberately persists the INTERFACE and
nothing else — "reason everything else in-context, don't write essays". That is
right for most tasks and wrong for exactly one kind: a node that publishes an
invariant its dependents inherit. Someone will later be told "you must not break
this" with no way to learn WHY, and the reasoning that produced it is gone with
the conversation that had it.

So the floor is not "every task writes a design doc" — that is the ceremony ADD
spent whole milestones removing. It is: if you bind your neighbours, you leave
them the reasoning. Publish nothing and nothing changes.

Written at BUILD, not at direction, on purpose: the design that survives is the
one the implementation actually took, and demanding it before the build is how
you get a document that describes a plan nobody followed.

Run:
    python3 -m unittest test_design_at_build -v
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

_FLAG = "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none"
INV = "the payout timeout is bounded"


def _run(cwd, *args, timeout=120):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=str(cwd),
                          capture_output=True, text=True, timeout=timeout)


class _Project(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.assertEqual(_run(self.root, "init", "--name", "dsn", "--stage", "mvp").returncode, 0)
        _run(self.root, "lock")
        _run(self.root, "new-task", "widget", "--title", "Widget")
        self.task_dir = self.root / ".add" / "tasks" / "widget"
        self.plan = self.task_dir / "PLAN.md"
        (self.root / "tests").mkdir(exist_ok=True)
        (self.root / "tests" / "test_widget.py").write_text("def test_bound(): pass\n")

    def tearDown(self):
        self._tmp.cleanup()

    def _to_verify(self, publish: bool):
        """Drive widget to the verify phase, optionally publishing an invariant."""
        s = self.plan.read_text()
        s = s.replace(
            "Boundary: <one format-variant per external input shape the tests must speak "
            "— e.g. aware vs naive timestamp · or \"none — no external input\">",
            "Boundary: `int` only — one format variant.")
        block = (f"Invariants (published):\n"
                 f"  - {INV} (proof: `tests/test_widget.py::test_bound`)\n\n") if publish else ""
        s = s.replace("Status: DRAFT", f"{block}Status: DRAFT\n{_FLAG}")
        s = re.sub(r"```\n<METHOD>.*?\n```", "```\ncount(items: list) -> int\n```",
                   s, count=1, flags=re.S)
        s = re.sub(r"(?m)^Target \(measurable\): <.*$",
                   "Target (measurable): count([1,2]) == 2.", s, count=1)
        self.plan.write_text(s, encoding="utf-8")
        r = _run(self.root, "freeze", "widget", "--by", "Tester", "--cross")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def _design(self, text="## Why\nThe provider applies payouts out of band.\n"):
        (self.task_dir / "DESIGN.md").write_text(text, encoding="utf-8")

    def _gate(self, outcome="PASS"):
        return _run(self.root, "gate", outcome, "widget", "--target-hit", "yes")


class ThePublisherOwesADesign(_Project):
    def test_publisher_cannot_pass_without_a_design(self):  # M1 R1
        self._to_verify(publish=True)
        r = self._gate()
        self.assertNotEqual(r.returncode, 0, "a publisher gated with no DESIGN.md")
        self.assertIn("design_missing", r.stderr + r.stdout)

    def test_the_refusal_names_the_path_to_create(self):  # M1
        self._to_verify(publish=True)
        r = self._gate()
        self.assertIn("DESIGN.md", r.stderr + r.stdout,
                      "the refusal must name the file the human has to write")

    def test_publisher_passes_once_the_design_exists(self):  # M2
        self._to_verify(publish=True)
        self._design()
        r = self._gate()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_an_empty_design_does_not_satisfy_it(self):  # M3 R2
        # A touched file is not reasoning; this floor is trivially satisfiable
        # otherwise, and a floor you can satisfy by accident is not a floor.
        self._to_verify(publish=True)
        self._design("   \n\n")
        r = self._gate()
        self.assertNotEqual(r.returncode, 0, "an empty DESIGN.md satisfied the floor")
        self.assertIn("design_empty", r.stderr + r.stdout)

    def test_risk_accepted_is_refused_too(self):  # M1 [edge]
        # A completing outcome is a completing outcome — the waiver route must not
        # launder a missing design.
        self._to_verify(publish=True)
        r = _run(self.root, "gate", "RISK-ACCEPTED", "widget", "--owner", "T",
                 "--ticket", "T-1", "--expires", "2027-01-01", "--target-hit", "yes")
        self.assertNotEqual(r.returncode, 0, "RISK-ACCEPTED laundered a missing design")
        self.assertIn("design_missing", r.stderr + r.stdout)


class TheNonPublisherOwesNothing(_Project):
    def test_a_task_publishing_nothing_gates_as_before(self):  # M4
        # The floor must not become "every task writes a design doc" — that is the
        # ceremony this method spent whole milestones removing.
        self._to_verify(publish=False)
        r = self._gate()
        self.assertEqual(r.returncode, 0,
                         "a non-publisher was made to write a design:\n" + r.stderr + r.stdout)

    def test_a_non_publisher_needs_no_design_file_on_disk(self):  # M4 [edge]
        self._to_verify(publish=False)
        self._gate()
        self.assertFalse((self.task_dir / "DESIGN.md").exists(),
                         "nothing should have created a DESIGN.md for a non-publisher")


if __name__ == "__main__":
    unittest.main()
