#!/usr/bin/env python3
"""fast-lane-intake-heuristic (add-lean-loop task 4): intake proposes
`new-task --fast` for fast-fit tasks; the flag stays human-owned.

Run:
    python3 -m unittest test_fast_lane_heuristic -v
"""
from __future__ import annotations

import hashlib
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
INTAKE = HERE.parent / "skill" / "add" / "intake.md"


class FastFitHeuristic(unittest.TestCase):
    def setUp(self):
        self.text = INTAKE.read_text()

    def test_names_the_three_conditions(self):  # M1
        self.assertIn("Fast-fit test", self.text)
        self.assertIn("single behavior", self.text)
        self.assertIn("contract surface", self.text)
        self.assertIn("mechanical", self.text)

    def test_proposes_the_fast_command(self):  # M1
        self.assertIn("new-task <slug> --fast", self.text)

    def test_flag_stays_human_owned(self):  # M2
        self.assertIn("human-owned", self.text)
        self.assertIn("confirm", self.text.split("Fast-fit test", 1)[1][:600],
                      "the heuristic itself must say the human's confirm picks the flag")

    def test_doubt_routes_to_full_lane(self):  # M2 (fail-safe direction)
        after = self.text.split("Fast-fit test", 1)[1][:600]
        self.assertIn("full lane", after)


class IntakeTreesStayIdentical(unittest.TestCase):
    def test_parity(self):
        trees = (INTAKE,
                 REPO / ".claude" / "skills" / "add" / "intake.md",
                 HERE.parent / "src" / "add_method" / "_bundled" / "skill" / "add" / "intake.md")
        digests = {hashlib.md5(t.read_bytes()).hexdigest() for t in trees if t.exists()}
        self.assertEqual(1, len(digests), "intake.md trees diverged")


if __name__ == "__main__":
    unittest.main(verbosity=2)
