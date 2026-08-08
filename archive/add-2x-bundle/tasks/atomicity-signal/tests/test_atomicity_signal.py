"""atomicity-signal — §4 red suite (task: atomicity-signal, milestone signal-graph).

CONTRACT (frozen @ v1): `_scope_parts(root, slug)` PURE-reads §1/§3 and returns the
ordered independent-Part labels (numbered-bold ∪ `(N parts)` marker ∪ catch-all keyword);
`_atomicity_signal_seed(root, slug)` SEEDS one `captured` todo (idempotent per slug) when
≥2 Parts, read by `_signals` and rendered under `graph --signals`; the `cmd_freeze` hook
fires it fail-open. A single-Part / malformed scope seeds nothing and never raises.

The applied case that CLOSES the signal-graph milestone: note = todo = delta = nudge, one signal.

Run: python3 -m unittest test_atomicity_signal -v
"""
import hashlib
import io
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "add-method" / "tooling"))

import add  # noqa: E402
from test_graph_repair import _GraphHarness  # noqa: E402


# a full, freezable PLAN.md whose §3 body we control (mirrors test_unflagged_freeze._body,
# minimal: concrete contract + a well-formed flag + a filled Boundary so `freeze` stamps).
def _plan(slug, sec3_extra):
    return "\n".join([
        f"# PLAN: {slug}", "",
        "## 1 · SPECIFY", "Feature: f", "Boundary: none — no external input", "",
        "## 2 · SCENARIOS", "(none)", "",
        "## 3 · PLAN", "### Contract", "```", "_thing(x) -> y", "```",
        sec3_extra,
        "Target (measurable): t",
        "Status: DRAFT",
        "Least-sure flag surfaced at freeze: ⚠ [contract] the heuristic biases precision over recall",
        "Scope (may touch): `./src/`", "",
        "## 4 · TESTS", "plan", "",
        "## 5 · BUILD", "code", "",
        "## 6 · VERIFY", "- [ ] a person reviewed", "",
        "## 7 · OBSERVE", "watch", "",
    ])


_THREE_PARTS = "1. **Part A** does alpha\n2. **Part B** does beta\n3. **Part C** does gamma"


class AtomicitySignalTest(_GraphHarness):

    def _root(self):
        return self.tmp / ".add"

    def _new_task(self, slug, sec3_extra, title="T"):
        self._silent("new-task", slug, "--title", title, "--milestone", "m")
        (self._root() / "tasks" / slug / "PLAN.md").write_text(_plan(slug, sec3_extra),
                                                               encoding="utf-8")

    def _freeze(self, slug):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["freeze", slug, "--by", "Tin"])
        return buf.getvalue()

    # ---- _scope_parts (M1) -------------------------------------------------
    def test_scope_parts_numbered_bold(self):
        self._mk_board()
        self._new_task("multi", _THREE_PARTS)
        self.assertEqual(len(add._scope_parts(self._root(), "multi")), 3)

    def test_scope_parts_marker(self):
        self._mk_board()
        self._new_task("marked", "This drains (4 parts) of the backlog.")
        self.assertGreaterEqual(len(add._scope_parts(self._root(), "marked")), 2)

    def test_scope_parts_catchall_keyword(self):
        self._mk_board()
        self._new_task("admin-longtail", "One prose Must, no numbered list.")
        self.assertGreaterEqual(len(add._scope_parts(self._root(), "admin-longtail")), 2)

    def test_scope_parts_single_none(self):
        self._mk_board()
        self._new_task("atomic", "One contract shape, one behavior.")
        self.assertEqual(add._scope_parts(self._root(), "atomic"), [])

    # ---- _atomicity_signal_seed (M2, M3) -----------------------------------
    def test_seed_appends_captured_signal(self):
        self._mk_board()
        self._new_task("multi", _THREE_PARTS)
        sid = add._atomicity_signal_seed(self._root(), "multi")
        self.assertIsNotNone(sid)
        sigs = [s for s in add._signals(self._root())
                if s["kind"] == "todo" and s["text"].startswith("atomicity: multi")]
        self.assertEqual(len(sigs), 1)
        self.assertEqual(sigs[0]["status"], "captured")

    def test_seed_idempotent(self):
        self._mk_board()
        self._new_task("multi", _THREE_PARTS)
        add._atomicity_signal_seed(self._root(), "multi")
        second = add._atomicity_signal_seed(self._root(), "multi")
        self.assertIsNone(second)
        sigs = [s for s in add._signals(self._root())
                if s["text"].startswith("atomicity: multi")]
        self.assertEqual(len(sigs), 1)

    def test_seed_in_graph_signals(self):
        self._mk_board()
        self._new_task("multi", _THREE_PARTS)
        add._atomicity_signal_seed(self._root(), "multi")
        out = self._silent("graph", "--signals")
        self.assertIn("atomicity: multi", out)

    # ---- freeze integration (M2, M4, M5) -----------------------------------
    def test_freeze_multipart_leaves_signal(self):
        self._mk_board()
        self._new_task("multi", _THREE_PARTS)
        self._freeze("multi")
        sigs = [s for s in add._signals(self._root())
                if s["text"].startswith("atomicity: multi")]
        self.assertEqual(len(sigs), 1, "a real freeze of a multi-Part task must leave a signal")

    def test_freeze_single_part_no_seed(self):
        self._mk_board()
        self._new_task("atomic", "One contract shape, one behavior.")
        self._freeze("atomic")
        sigs = [s for s in add._signals(self._root())
                if s["text"].startswith("atomicity:")]
        self.assertEqual(sigs, [], "a single-Part freeze seeds nothing")

    # ---- fail-open (M4, R:silent_absent) -----------------------------------
    def test_seed_fail_open_absent(self):
        self._mk_board()
        self.assertIsNone(add._atomicity_signal_seed(self._root(), "ghost-never-created"))

    # ---- engine parity (M6) ------------------------------------------------
    def test_three_trees_identical(self):
        trees = [_REPO / "add-method" / "tooling" / "add.py",
                 _REPO / "add-method" / ".add" / "tooling" / "add.py",
                 _REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py"]
        self.assertEqual(len({hashlib.md5(p.read_bytes()).hexdigest() for p in trees}), 1)


if __name__ == "__main__":
    unittest.main()
