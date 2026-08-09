"""graph-view-signals — §4 red suite (task: graph-view-signals, milestone signal-graph).

CONTRACT (frozen @ v1): `cmd_graph` gains an opt-in `--signals` layer that renders the
signals `_signals(root)` produces as nodes wired to their task nodes by typed edges
(observed-by `-.->`, resolves-into `-->`, blocks `==>`), reusing node_id + the x_<slug>
missing fallback. Only LIVE signals (status not in {resolved, dropped}) render. The
default `graph` (no flag) output stays byte-identical (guarded here + by test_graph_views).

Run: python3 -m unittest test_graph_view_signals -v
"""
import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "add-method" / "tooling"))

import add  # noqa: E402
from test_graph_repair import _GraphHarness  # noqa: E402


class GraphSignalsTest(_GraphHarness):

    def _set_seven(self, slug, deltas):
        """Inject delta lines directly under the task's §7 OBSERVE heading."""
        p = self.tmp / ".add" / "tasks" / slug / "PLAN.md"
        t = p.read_text(encoding="utf-8")
        marker = "## 7"
        i = t.index(marker)
        j = t.index("\n", i)
        p.write_text(t[:j + 1] + "\n" + deltas + "\n" + t[j + 1:], encoding="utf-8")

    def _seed(self):
        self._mk_board()                                 # lock + milestone "m"
        self._silent("new-task", "alpha", "--title", "A", "--milestone", "m")
        self._silent("new-task", "beta", "--title", "B", "--milestone", "m")
        self._set_seven("alpha",
                        "- [SPEC · open] a proven gap (evidence: e)\n"
                        "- [SPEC · seeded] moved on [→ beta]\n"
                        "- [SPEC · seeded] lost [→ ghosttask]\n"
                        "- [SPEC · dropped] not doing it")
        self._silent("todo", "a live open todo")         # -> captured
        self._silent("todo", "will finish soon")         # id 2
        self._silent("todo", "--done", "2")              # -> resolved (omitted)

    def _sig_nodes(self, out):
        return [ln.strip() for ln in out.splitlines() if ln.strip().startswith("sig_")]

    def test_graph_default_byte_identical(self):                    # M1
        self._seed()
        out = self._silent("graph")
        self.assertIn("flowchart TD", out)
        self.assertNotIn("sig_", out, "no-flag graph must not leak signal nodes")
        self.assertNotIn("classDef signal", out)

    def test_graph_signals_nodes_and_observed_by(self):             # M2,M3
        self._seed()
        out = self._silent("graph", "--signals")
        self.assertIn("classDef signal", out)
        self.assertTrue(self._sig_nodes(out), "signal nodes must render under --signals")
        self.assertIn("-.->|observed-by| t_alpha", out.replace("  ", " "))

    def test_graph_signals_resolves_into(self):                     # M3
        self._seed()
        out = self._silent("graph", "--signals").replace("  ", " ")
        self.assertIn("-->|resolves-into| t_beta", out)

    def test_graph_signals_missing_target_fallback(self):           # M3, R:missing_target_fallback
        self._seed()
        out = self._silent("graph", "--signals")
        self.assertIn("x_ghosttask", out)
        self.assertIn("missing", out)
        self.assertNotIn("|resolves-into| ghosttask", out, "bare dangling id is forbidden")

    def test_graph_signals_omits_resolved_dropped(self):            # M2, R:resolved_omitted
        self._seed()
        out = self._silent("graph", "--signals")
        for ln in self._sig_nodes(out):
            self.assertNotIn("resolved", ln)
            self.assertNotIn("dropped", ln)
        # live set = 1 captured todo + 1 evidenced + 2 resolving = 4 sig nodes
        node_defs = [ln for ln in self._sig_nodes(out) if '["' in ln]
        self.assertEqual(len(node_defs), 4, f"expected 4 live signal nodes, got {node_defs}")

    def test_graph_signals_three_trees_identical(self):             # M5
        import hashlib
        trees = [_REPO / "add-method" / "tooling" / "add.py",
                 _REPO / "add-method" / ".add" / "tooling" / "add.py",
                 _REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py"]
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in trees}
        self.assertEqual(len(digests), 1, "the three tooling trees must be byte-identical")


if __name__ == "__main__":
    unittest.main()
