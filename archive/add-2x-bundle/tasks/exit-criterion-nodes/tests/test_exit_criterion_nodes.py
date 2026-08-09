"""exit-criterion-nodes — §4 red suite (task: exit-criterion-nodes, milestone signal-graph).

CONTRACT (frozen @ v1): `_exit_criterion_nodes(root)` PURE-reads each MILESTONE.md
`## Exit criteria` section -> per criterion {ms, idx, text, met, delivered_by}. The
`--signals` overlay renders each as `ec_<ms>_<idx>` edged `-.->|delivered-by|` its task
(x_<slug> fallback for an unknown target, no edge when unpointed), classed ec_met/ec_unmet.
Default `graph` (no flag) prints no ec_ node.

Run: python3 -m unittest test_exit_criterion_nodes -v
"""
import hashlib
import re
import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "add-method" / "tooling"))

import add  # noqa: E402
from test_graph_repair import _GraphHarness  # noqa: E402


class ExitCriterionTest(_GraphHarness):

    def _set_exit_criteria(self, ms, body):
        p = self.tmp / ".add" / "milestones" / ms / "MILESTONE.md"
        t = p.read_text(encoding="utf-8")
        new = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                     "## Exit criteria (observable)\n" + body + "\n", t, flags=re.S)
        p.write_text(new, encoding="utf-8")

    def _seed(self):
        self._mk_board()                                  # lock + milestone "m"
        self._silent("new-task", "alpha", "--title", "A", "--milestone", "m")
        self._silent("new-task", "beta", "--title", "B", "--milestone", "m")
        self._set_exit_criteria("m",
                                "- [x] met one  (← alpha)\n"
                                "- [ ] unmet one  (← beta)\n"
                                "- [ ] no pointer here\n"
                                "- [ ] ghost pointer  (← ghosttask)")

    def _root(self):
        return self.tmp / ".add"

    def test_exit_criterion_parse_met_and_pointer(self):            # M1
        self._seed()
        nodes = add._exit_criterion_nodes(self._root())
        got = {(n["idx"], n["met"], n["delivered_by"]) for n in nodes if n["ms"] == "m"}
        self.assertEqual(got, {(1, True, "alpha"), (2, False, "beta"),
                               (3, False, None), (4, False, "ghosttask")})

    def test_graph_exit_criterion_nodes_and_edges(self):            # M2,M3
        self._seed()
        out = self._silent("graph", "--signals").replace("  ", " ")
        self.assertIn("ec_m_1[", out)
        self.assertIn("-.->|delivered-by| t_alpha", out)
        self.assertIn("-.->|delivered-by| t_beta", out)

    def test_exit_criterion_met_unmet_class(self):                  # M4
        self._seed()
        out = self._silent("graph", "--signals")
        self.assertIn("classDef ec_met", out)
        self.assertIn("classDef ec_unmet", out)
        self.assertIn("class ec_m_1 ec_met", out.replace("  ", " "))
        self.assertIn("class ec_m_2 ec_unmet", out.replace("  ", " "))

    def test_exit_criterion_missing_target_fallback(self):          # M3, R:missing_target_fallback
        self._seed()
        out = self._silent("graph", "--signals")
        self.assertIn("x_ghosttask", out)
        self.assertNotIn("|delivered-by| ghosttask", out, "bare dangling id forbidden")

    def test_exit_criterion_no_pointer_no_edge(self):               # M3, R:unpointed_ok
        self._seed()
        out = self._silent("graph", "--signals").replace("  ", " ")
        self.assertIn("ec_m_3[", out)
        self.assertNotIn("ec_m_3 -.->", out, "an unpointed criterion has no delivered-by edge")

    def test_graph_default_no_exit_nodes(self):                     # M5
        self._seed()
        self.assertNotIn("ec_", self._silent("graph"))

    def test_exit_criterion_three_trees_identical(self):            # M6
        trees = [_REPO / "add-method" / "tooling" / "add.py",
                 _REPO / "add-method" / ".add" / "tooling" / "add.py",
                 _REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py"]
        self.assertEqual(len({hashlib.md5(p.read_bytes()).hexdigest() for p in trees}), 1)


if __name__ == "__main__":
    unittest.main()
