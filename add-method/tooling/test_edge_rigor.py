#!/usr/bin/env python3
"""edge-rigor: an enumerated edge case must be covered by a real test or carry a
stated reason, before a completing gate.

WHY. §4's Rigor rule says the GATED floor is one test per Must/Reject, and that
minor behaviours are prose build-guidance. That is a good rule with one hole:
an author can ENUMERATE an edge case in the test_plan — visibly promising it —
and then never write the test. The row reads as coverage to every later reader,
and nothing ever disagrees. Enumerating a case you do not cover is worse than
not enumerating it, because it buys credit for work that was not done.

This is the happy-path problem the milestone exists to fix, in the one place the
engine can actually see it: the plan says the case matters, so either the test
exists or you say, on the record, why it does not.

WHAT IT CANNOT DO. The engine does not run the suite at gate time, so "the test
EXISTS in the declared test files" is the mechanical proxy for "covered". The
suite being GREEN is the §6 evidence floor, and the gate composes the two — this
guard closes the enumerate-and-forget hole, not the write-a-passing-stub hole.

Run:
    python3 -m unittest test_edge_rigor -v
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


def _run(cwd, *args, timeout=120):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=str(cwd),
                          capture_output=True, text=True, timeout=timeout)


class _Project(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.assertEqual(_run(self.root, "init", "--name", "edge", "--stage", "mvp").returncode, 0)
        _run(self.root, "lock")
        _run(self.root, "new-task", "widget", "--title", "Widget")
        self.plan = self.root / ".add" / "tasks" / "widget" / "PLAN.md"
        self.tests = self.root / "tests"
        self.tests.mkdir(exist_ok=True)

    def tearDown(self):
        self._tmp.cleanup()

    def _suite(self, *names):
        (self.tests / "test_widget.py").write_text(
            "".join(f"def {n}():\n    pass\n\n" for n in names) or "def test_main(): pass\n")

    def _to_verify(self, rows: str):
        """Drive widget to verify with `rows` as its §4 test_plan."""
        s = self.plan.read_text()
        s = s.replace(
            "Boundary: <one format-variant per external input shape the tests must speak "
            "— e.g. aware vs naive timestamp · or \"none — no external input\">",
            "Boundary: `int` only — one format variant.")
        s = s.replace("Status: DRAFT", f"Status: DRAFT\n{_FLAG}")
        s = re.sub(r"```\n<METHOD>.*?\n```", "```\ncount(items: list) -> int\n```",
                   s, count=1, flags=re.S)
        s = re.sub(r"(?m)^Target \(measurable\): <.*$",
                   "Target (measurable): count([1,2]) == 2.", s, count=1)
        s = re.sub(r"<test_plan>.*?</test_plan>", f"<test_plan>\n{rows}</test_plan>",
                   s, count=1, flags=re.S)
        s = re.sub(r"(?m)^Tests live in: .*$", "Tests live in: `tests/test_widget.py`", s, count=1)
        self.plan.write_text(s, encoding="utf-8")
        r = _run(self.root, "freeze", "widget", "--by", "Tester", "--cross")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def _gate(self, outcome="PASS"):
        return _run(self.root, "gate", outcome, "widget", "--target-hit", "yes")


class AnEnumeratedEdgeMustBeAccountedFor(_Project):
    def test_an_uncovered_edge_row_refuses_the_gate(self):  # M1 R1
        self._suite("test_main")
        self._to_verify("  - test_main: the primary · covers: M1  [GATED]\n"
                        "  - test_empty_list: an empty input · covers: M1  [edge]\n")
        r = self._gate()
        self.assertNotEqual(r.returncode, 0, "an enumerated-but-unwritten edge case gated")
        self.assertIn("edge_unaccounted", r.stderr + r.stdout)

    def test_the_refusal_names_the_offending_row(self):  # M2
        self._suite("test_main")
        self._to_verify("  - test_main: the primary · covers: M1  [GATED]\n"
                        "  - test_empty_list: an empty input · covers: M1  [edge]\n")
        r = self._gate()
        self.assertIn("test_empty_list", r.stderr + r.stdout,
                      "the refusal must name WHICH edge case is unaccounted")

    def test_a_covered_edge_row_gates(self):  # M3
        self._suite("test_main", "test_empty_list")
        self._to_verify("  - test_main: the primary · covers: M1  [GATED]\n"
                        "  - test_empty_list: an empty input · covers: M1  [edge]\n")
        r = self._gate()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_a_waived_edge_row_gates(self):  # M4
        self._suite("test_main")
        self._to_verify(
            "  - test_main: the primary · covers: M1  [GATED]\n"
            "  - test_empty_list: an empty input · covers: M1  "
            "[edge — waived: the caller cannot construct an empty batch]\n")
        r = self._gate()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_an_empty_waiver_reason_is_refused(self):  # M4 R2
        self._suite("test_main")
        self._to_verify("  - test_main: the primary · covers: M1  [GATED]\n"
                        "  - test_empty_list: an empty input · covers: M1  [edge — waived: ]\n")
        r = self._gate()
        self.assertNotEqual(r.returncode, 0, "a blank waiver cleared the floor")
        self.assertIn("edge_waiver_unreasoned", r.stderr + r.stdout)

    def test_risk_accepted_is_refused_too(self):  # M1 [edge]
        self._suite("test_main")
        self._to_verify("  - test_main: the primary · covers: M1  [GATED]\n"
                        "  - test_empty_list: an empty input · covers: M1  [edge]\n")
        r = _run(self.root, "gate", "RISK-ACCEPTED", "widget", "--owner", "T",
                 "--ticket", "T-1", "--expires", "2027-01-01", "--target-hit", "yes")
        self.assertNotEqual(r.returncode, 0, "the waiver route laundered an unwritten edge case")
        self.assertIn("edge_unaccounted", r.stderr + r.stdout)


class ItLeavesEverythingElseAlone(_Project):
    def test_a_plan_with_no_edge_rows_gates_as_before(self):  # M5
        # Grandfathered: every task already on disk predates the tag.
        self._suite("test_main")
        self._to_verify("  - test_main: the primary · covers: M1\n")
        r = self._gate()
        self.assertEqual(r.returncode, 0,
                         "a §4 with no [edge] rows must gate exactly as before:\n"
                         + r.stderr + r.stdout)

    def test_a_gated_row_is_not_subject_to_the_edge_floor(self):  # M5 [edge]
        # [GATED] rows are the §6 evidence floor's business (the suite must be green),
        # not this guard's — double-enforcing here would refuse on a naming mismatch.
        self._suite("test_main")
        self._to_verify("  - test_main: the primary · covers: M1  [GATED]\n"
                        "  - test_absent_but_gated: x · covers: M2  [GATED]\n")
        r = self._gate()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_an_unreadable_declared_suite_does_not_crash_the_gate(self):  # M5 [edge]
        self._suite("test_main")
        self._to_verify("  - test_main: the primary · covers: M1\n")
        (self.tests / "test_widget.py").unlink()
        r = self._gate()
        self.assertNotIn("Traceback", r.stderr,
                         "a missing declared suite must never traceback at a gate")


if __name__ == "__main__":
    unittest.main()
