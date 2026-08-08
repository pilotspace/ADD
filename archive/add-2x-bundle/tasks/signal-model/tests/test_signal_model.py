"""signal-model — §4 red suite (task: signal-model, milestone signal-graph).

CONTRACT (frozen @ v1): `_signals(root) -> list[dict]` is a PURE projection over the
three split observation primitives — todos (state["todos"]), SPEC deltas and
competency deltas (each task's §7) — into ONE unified signal node:
  {id, kind, text, status, edges}
  kind   in {todo, spec-delta, competency-delta}
  status in {advisory, captured, evidenced, resolving, resolved, dropped}
  edges  = list of (rel, target_slug), rel in {observed-by, resolves-into, blocks}
It writes NOTHING, adds no store, and backward-reads every existing line (fail-soft).

Run: python3 -m unittest test_signal_model -v
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "add-method" / "tooling"))

import add  # noqa: E402


def _mk(tmp: Path, todos=None, task_sevens=None) -> Path:
    """Build a fixture `.add` root: state.json (todos + task registry) + each task's
    PLAN.md carrying the given §7 body. Returns the `.add` root _signals reads."""
    root = tmp / ".add"
    (root / "tasks").mkdir(parents=True)
    tasks = {slug: {"phase": "done"} for slug in (task_sevens or {})}
    state = {"tasks": tasks}
    if todos is not None:
        state["todos"] = todos
    (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
    for slug, seven in (task_sevens or {}).items():
        d = root / "tasks" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "PLAN.md").write_text(
            f"# PLAN: {slug}\n\nphase: done\n\n## 7 · OBSERVE\n\n{seven}\n",
            encoding="utf-8")
    return root


def _by_id(signals):
    return {s["id"]: s for s in signals}


class SignalModelTest(unittest.TestCase):

    def test_signal_todo_open_and_done(self):                       # M1,M2,M4
        root = _mk(Path(tempfile.mkdtemp()),
                   todos=[{"id": 1, "text": "a", "status": "open"},
                          {"id": 2, "text": "b", "status": "done"}])
        sig = _by_id(add._signals(root))
        self.assertEqual(sig["t1"]["kind"], "todo")
        self.assertEqual(sig["t1"]["status"], "captured")
        self.assertEqual(sig["t2"]["status"], "resolved")

    def test_signal_spec_open_evidenced(self):                      # M1,M2,M3
        root = _mk(Path(tempfile.mkdtemp()),
                   task_sevens={"alpha": "- [SPEC · open] a gap (evidence: proof)"})
        s = _by_id(add._signals(root))["s:alpha:1"]
        self.assertEqual(s["kind"], "spec-delta")
        self.assertEqual(s["status"], "evidenced")
        self.assertIn(("observed-by", "alpha"), s["edges"])

    def test_signal_spec_open_no_evidence_is_captured(self):        # M2 (boundary)
        root = _mk(Path(tempfile.mkdtemp()),
                   task_sevens={"alpha": "- [SPEC · open] a bare gap, no evidence tail"})
        self.assertEqual(_by_id(add._signals(root))["s:alpha:1"]["status"], "captured")

    def test_signal_spec_seeded_resolving(self):                    # M2,M3
        root = _mk(Path(tempfile.mkdtemp()),
                   task_sevens={"alpha": "- [SPEC · seeded] moved on [→ beta]"})
        s = _by_id(add._signals(root))["s:alpha:1"]
        self.assertEqual(s["status"], "resolving")
        self.assertIn(("observed-by", "alpha"), s["edges"])
        self.assertIn(("resolves-into", "beta"), s["edges"])

    def test_signal_spec_dropped(self):                             # M2
        root = _mk(Path(tempfile.mkdtemp()),
                   task_sevens={"alpha": "- [SPEC · dropped] not doing it"})
        self.assertEqual(_by_id(add._signals(root))["s:alpha:1"]["status"], "dropped")

    def test_signal_competency_open(self):                          # M1,M2,M4
        root = _mk(Path(tempfile.mkdtemp()),
                   task_sevens={"alpha": "- [ADD · open] a lesson (evidence: y)"})
        s = _by_id(add._signals(root))["c:alpha:1"]
        self.assertEqual(s["kind"], "competency-delta")
        self.assertEqual(s["status"], "evidenced")
        self.assertIn(("observed-by", "alpha"), s["edges"])

    def test_signal_backward_read_and_failsoft(self):               # M5, R:silent_skip
        seven = ("- [SPEC · open] real one (evidence: e)\n"
                 "- [SPEC bad malformed line that must not match\n"
                 "prose line, not a delta\n"
                 "- [ZZZ · open] unknown competency token, skipped")
        root = _mk(Path(tempfile.mkdtemp()),
                   todos=[{"id": 1, "text": "ok", "status": "open"},
                          "corrupt-not-a-dict",
                          {"no_id": True}],
                   task_sevens={"alpha": seven})
        sig = add._signals(root)          # must not raise
        ids = {s["id"] for s in sig}
        self.assertEqual(ids, {"t1", "s:alpha:1"})   # junk skipped, valid kept

    def test_signal_pure_no_store(self):                            # M5
        root = _mk(Path(tempfile.mkdtemp()),
                   todos=[{"id": 1, "text": "a", "status": "open"}],
                   task_sevens={"alpha": "- [SPEC · open] g (evidence: e)"})
        before = (root / "state.json").read_bytes()
        add._signals(root)
        after = (root / "state.json").read_bytes()
        self.assertEqual(before, after, "state.json must be byte-identical (pure read)")
        self.assertNotIn("signals", json.loads(after), "no signals store may be added")

    def test_signal_three_trees_identical(self):                    # M6
        trees = [_REPO / "add-method" / "tooling" / "add.py",
                 _REPO / "add-method" / ".add" / "tooling" / "add.py",
                 _REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py"]
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in trees}
        self.assertEqual(len(digests), 1, "the three tooling trees must be byte-identical")


if __name__ == "__main__":
    unittest.main()
