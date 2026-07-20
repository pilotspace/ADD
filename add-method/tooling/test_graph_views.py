#!/usr/bin/env python3
"""graph-views red suite (task-graph-native W4 — the rendered DAG + planned-drift).

`add.py graph` renders the live board as a mermaid flowchart — deterministic,
read-only, print-only. Milestone = the scope ROOT: each milestone is a subgraph
wrapping its tasks; depth lives in EDGES, never nesting. Edge styles carry the
edge semantics (depends-on solid `-->` · extends dashed `-.->` · relates-to open
dashed `-.-`); node classes carry phase (done · live · planned). A milestone's
COMPILED plan is rendered too: a planned-but-never-created node appears dashed —
the drift is visible before it is a warning.

The same drift is measured: `add.py check` WARNS (never red — mid-milestone a
planned-not-yet-created node is normal flow, not a defect) naming each planned
slug with no live task and no archived record.

Run: cd add-method/tooling && python3 -m unittest test_graph_views -v
"""
import json
import unittest

import add
from test_graph_repair import _GraphHarness
from test_edge_truth import _fill_confirm_floor, TASKS_SECTION


class _ViewHarness(_GraphHarness):
    def _mk_confirmed(self, tasks_section=TASKS_SECTION):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp",
                     "--await-confirm")
        mfile = self.tmp / ".add" / "milestones" / "m" / "MILESTONE.md"
        mfile.write_text(_fill_confirm_floor(mfile.read_text(encoding="utf-8"),
                                             tasks_section), encoding="utf-8")
        self._silent("milestone-confirm", "m")


class MermaidRenderTest(_GraphHarness):
    def test_graph_renders_flowchart(self):
        self._mk_board()
        self._silent("new-task", "a", "--title", "A")
        out = self._silent("graph")
        self.assertIn("flowchart TD", out)

    def test_milestone_is_a_subgraph_wrapping_its_tasks(self):
        self._mk_board()
        self._silent("new-task", "a", "--title", "A")
        out = self._silent("graph")
        self.assertIn("subgraph", out)
        self.assertIn('"m', out.split("subgraph", 1)[-1],
                      "the milestone slug labels the subgraph — the scope ROOT")

    def test_depends_edge_solid_extends_dashed_relates_open(self):
        self._mk_board()
        self._silent("new-task", "a", "--title", "A")
        self._silent("new-task", "b", "--title", "B", "--depends-on", "a")
        self._silent("new-task", "d", "--title", "D")
        self._silent("relate", "d", "--extends", "a")
        self._silent("new-task", "e", "--title", "E")
        self._silent("relate", "e", "--relates-to", "a")
        out = self._silent("graph")
        self.assertIn("t_b -->|depends-on| t_a", out)
        self.assertIn("t_d -.->|extends| t_a", out)
        self.assertIn("t_e -.-|relates-to| t_a", out)

    def test_done_phase_classed_and_labeled(self):
        self._mk_board()
        self._silent("new-task", "a", "--title", "A")
        self._mark_done("a")
        out = self._silent("graph")
        self.assertIn("done", out)
        self.assertIn("class t_a done", out)

    def test_archived_dep_target_annotated(self):
        self._mk_board()
        self._silent("new-task", "b", "--title", "B", "--depends-on", "old-core")
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text())
        st.setdefault("archived", []).append({"slug": "done-ms", "task_slugs": ["old-core"]})
        sp.write_text(json.dumps(st, indent=2))
        out = self._silent("graph")
        self.assertIn("archived", out)
        self.assertIn("t_b -->|depends-on|", out)

    def test_milestone_filter(self):
        self._mk_board()
        self._silent("new-task", "a", "--title", "A")
        self._silent("new-milestone", "other", "--goal", "g2", "--stage", "mvp")
        self._silent("new-task", "z", "--title", "Z", "--milestone", "other")
        out = self._silent("graph", "--milestone", "m")
        self.assertIn("t_a", out)
        self.assertNotIn("t_z", out)


class PlannedDriftTest(_ViewHarness):
    def test_planned_never_created_rendered_as_planned_node(self):
        self._mk_confirmed()
        self._silent("new-task", "api-core", "--title", "API")
        out = self._silent("graph")
        self.assertIn("p_auth-rules", out, "a compiled-but-never-created node renders dashed")
        self.assertIn("planned", out)

    def test_check_warns_planned_never_created(self):
        self._mk_confirmed()
        self._silent("new-task", "api-core", "--title", "API")
        out, code = self._run("check")
        self.assertEqual(code, 0, "planned-not-yet-created is flow, not a defect — warn only")
        self.assertIn("auth-rules", out)
        self.assertIn("never created", out)

    def test_check_silent_once_all_planned_created(self):
        self._mk_confirmed()
        for slug in ("api-core", "auth-rules", "search"):
            self._silent("new-task", slug, "--title", slug)
        out, _ = self._run("check")
        self.assertNotIn("never created", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
