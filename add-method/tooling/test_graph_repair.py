#!/usr/bin/env python3
"""graph-repair red suite (task-graph-native W2, ATG failure-location + minimal repair).

`add.py locate <ref>` is the deterministic failure-location verb — no LLM, read-only,
print-only. Two modes by what <ref> resolves to:

- a TEST PATH -> the OWNING node (which task's §4 `Tests live in:` declaration — or,
  fallback, whose frozen §5 scope snapshot — covers that file) plus the failure CLASS:
  `in-node` when the owner is still live (fix inside the node; its frozen suite is the
  floor) vs `interface-regression` when the owner is DONE (a live change broke a
  settled contract — the figure's red-dot crossing a node boundary).
- a task SLUG -> the MINIMAL DEPENDENT CLOSURE: every task reachable over REVERSE
  depends-on/extends edges (the set that must re-verify if this node's contract
  changes). relates_to is context, not interface — never in the closure. DONE
  dependents stay listed: settled work re-verifies when its foundation moves.

Floors (bind after green): unowned path reports cleanly (exit 0, a finding not an
error) · closure of a leaf says so explicitly · deterministic output order.

Run: cd add-method/tooling && python3 -m unittest test_graph_repair -v
"""
import json
import unittest

import add
from test_freeze_command import _Harness


class _GraphHarness(_Harness):
    def _mk_board(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")

    def _mark_done(self, slug):
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text())
        st["tasks"][slug]["phase"] = "done"
        st["tasks"][slug]["gate"] = "PASS"
        sp.write_text(json.dumps(st, indent=2))

    def _seed_task_test(self, slug, fname="test_seed.py"):
        """Drop a real test file inside the task's own tests/ dir — the template's
        default §4 declaration (`./tests/`) resolves there."""
        p = self.tmp / ".add" / "tasks" / slug / "tests" / fname
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("def test_seed():\n    assert True\n", encoding="utf-8")
        return p.relative_to(self.tmp).as_posix()


class OwnerModeTest(_GraphHarness):
    def test_declared_test_file_maps_to_owner(self):
        self._mk_board()
        self._silent("new-task", "api-core", "--title", "API")
        rel = self._seed_task_test("api-core")
        out = self._silent("locate", rel)
        self.assertIn("owner", out)
        self.assertIn("api-core", out)

    def test_live_owner_classed_in_node(self):
        self._mk_board()
        self._silent("new-task", "api-core", "--title", "API")
        rel = self._seed_task_test("api-core")
        out = self._silent("locate", rel)
        self.assertIn("in-node", out)

    def test_done_owner_classed_interface_regression(self):
        self._mk_board()
        self._silent("new-task", "api-core", "--title", "API")
        rel = self._seed_task_test("api-core")
        self._mark_done("api-core")
        out = self._silent("locate", rel)
        self.assertIn("interface-regression", out)
        self.assertIn("api-core", out)

    def test_done_owner_locate_prints_its_closure(self):
        # the repair set rides along: a settled contract under pressure names who
        # else re-verifies if it moves
        self._mk_board()
        self._silent("new-task", "api-core", "--title", "API")
        rel = self._seed_task_test("api-core")
        self._mark_done("api-core")
        self._silent("new-task", "search", "--title", "S", "--depends-on", "api-core")
        out = self._silent("locate", rel)
        self.assertIn("search", out)

    def test_scope_snapshot_fallback(self):
        # no §4 declaration covers the file, but the frozen §5 scope snapshot does
        self._mk_board()
        self._silent("new-task", "worker", "--title", "W")
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text())
        st["tasks"]["worker"]["scope"] = {"declared": ["src/jobs/"]}
        sp.write_text(json.dumps(st, indent=2))
        out = self._silent("locate", "src/jobs/test_queue.py")
        self.assertIn("worker", out)
        self.assertIn("scope", out, "fallback provenance is named, not silent")

    def test_unowned_path_reports_cleanly(self):
        self._mk_board()
        self._silent("new-task", "api-core", "--title", "API")
        out, code = self._run("locate", "tests/test_nobody_declares_me.py")
        self.assertEqual(code, 0, "unowned is a finding, not an error")
        self.assertIn("unowned", out)
        self.assertNotIn("Traceback", out)


class ClosureModeTest(_GraphHarness):
    def _chain(self):
        # a <- b (depends) <- c (depends); d extends a; e relates_to a
        self._mk_board()
        self._silent("new-task", "a", "--title", "A")
        self._silent("new-task", "b", "--title", "B", "--depends-on", "a")
        self._silent("new-task", "c", "--title", "C", "--depends-on", "b")
        self._silent("new-task", "d", "--title", "D")
        self._silent("relate", "d", "--extends", "a")
        self._silent("new-task", "e", "--title", "E")
        self._silent("relate", "e", "--relates-to", "a")

    def test_transitive_dependents_listed(self):
        self._chain()
        out = self._silent("locate", "a")
        self.assertIn("b", out.split("closure", 1)[-1])
        self.assertIn("c", out.split("closure", 1)[-1],
                      "closure is transitive — c re-verifies through b")

    def test_extends_edge_joins_closure(self):
        self._chain()
        out = self._silent("locate", "a")
        self.assertIn("d", out.split("closure", 1)[-1])

    def test_relates_to_stays_out_of_closure(self):
        self._chain()
        out = self._silent("locate", "a")
        body = out.split("closure", 1)[-1]
        self.assertNotIn("'e'", body)
        self.assertNotRegex(body, r"(?m)^\s+e\s")

    def test_leaf_says_no_dependents(self):
        self._mk_board()
        self._silent("new-task", "solo", "--title", "Solo")
        out = self._silent("locate", "solo")
        self.assertIn("no dependents", out)

    def test_done_dependent_still_listed(self):
        self._mk_board()
        self._silent("new-task", "a", "--title", "A")
        self._silent("new-task", "b", "--title", "B", "--depends-on", "a")
        self._mark_done("b")
        out = self._silent("locate", "a")
        body = out.split("closure", 1)[-1]
        self.assertIn("b", body)
        self.assertIn("done", body, "settled dependents re-verify too — marked, kept")


if __name__ == "__main__":
    unittest.main(verbosity=2)
