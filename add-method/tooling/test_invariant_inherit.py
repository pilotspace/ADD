#!/usr/bin/env python3
"""invariant-inherit: `new-task --depends-on` shows the invariants the new node
inherits — a VIEW over the graph, never a second store.

WHY A VIEW. The moment inherited invariants are COPIED into the new task's
PLAN.md they can drift from the ancestor that owns them, and the copy is what a
builder reads. `graph --signals` already established the shape for this project:
the graph is a view, not a store. An inherited invariant is the ancestor's
invariant, read fresh, attributed to its owner.

Fail-soft is deliberate. An ancestor whose PLAN.md is missing or unreadable
contributes NOTHING and never crashes `new-task` — a broken neighbour must not
block a new node, and the guard for an unproven invariant lives at the
ancestor's own freeze, not here.

Run:
    python3 -m unittest test_invariant_inherit -v
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"

INV = "the payout timeout is bounded"
INV2 = "settlement is idempotent per idempotency-key"


def _run(cwd, *args, timeout=120):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=str(cwd),
                          capture_output=True, text=True, timeout=timeout)


class _Project(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        r = _run(self.root, "init", "--name", "inh", "--stage", "mvp")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        _run(self.root, "lock")

    def tearDown(self):
        self._tmp.cleanup()

    def _plan(self, slug):
        return self.root / ".add" / "tasks" / slug / "PLAN.md"

    def _publish(self, slug, *invariants):
        """Give `slug` a §3 that publishes `invariants`."""
        p = self._plan(slug)
        block = "Invariants (published):\n" + "".join(
            f"  - {t} (proof: `tests/test_x.py::test_y`)\n" for t in invariants) + "\n"
        p.write_text(p.read_text().replace("Status: DRAFT", block + "Status: DRAFT"),
                     encoding="utf-8")


class TheViewShowsWhatIsInherited(_Project):
    def test_new_task_prints_an_ancestors_published_invariant(self):  # M1
        _run(self.root, "new-task", "a", "--title", "A")
        self._publish("a", INV)
        r = _run(self.root, "new-task", "b", "--title", "B", "--depends-on", "a")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(INV, r.stdout, "the new node was never told what it inherits")

    def test_the_view_attributes_each_invariant_to_its_owner(self):  # M1
        _run(self.root, "new-task", "a", "--title", "A")
        self._publish("a", INV)
        r = _run(self.root, "new-task", "b", "--title", "B", "--depends-on", "a")
        line = next((l for l in r.stdout.splitlines() if INV in l), "")
        self.assertIn("a", line,
                      "an inherited invariant must name the node that owns it — "
                      f"unattributed, it is unmaintainable: {line!r}")

    def test_inheritance_is_transitive(self):  # M2
        # b depends on a; c depends on b. c inherits a's invariant through b.
        _run(self.root, "new-task", "a", "--title", "A")
        self._publish("a", INV)
        _run(self.root, "new-task", "b", "--title", "B", "--depends-on", "a")
        r = _run(self.root, "new-task", "c", "--title", "C", "--depends-on", "b")
        self.assertIn(INV, r.stdout,
                      "a grandparent's invariant binds too — inheritance stops at the "
                      "first hop only if the graph is a list")

    def test_several_invariants_all_surface(self):  # M1 [edge]
        _run(self.root, "new-task", "a", "--title", "A")
        self._publish("a", INV, INV2)
        r = _run(self.root, "new-task", "b", "--title", "B", "--depends-on", "a")
        for t in (INV, INV2):
            self.assertIn(t, r.stdout)


class ItIsAViewNotAStore(_Project):
    def test_nothing_is_copied_into_the_new_plan(self):  # M3
        _run(self.root, "new-task", "a", "--title", "A")
        self._publish("a", INV)
        _run(self.root, "new-task", "b", "--title", "B", "--depends-on", "a")
        self.assertNotIn(INV, self._plan("b").read_text(),
                         "the invariant was COPIED — a copy drifts from the node that "
                         "owns it, and the copy is what the builder reads")

    def test_no_new_state_key(self):  # M3
        _run(self.root, "new-task", "a", "--title", "A")
        self._publish("a", INV)
        _run(self.root, "new-task", "b", "--title", "B", "--depends-on", "a")
        state = json.loads((self.root / ".add" / "state.json").read_text())
        self.assertNotIn(INV, json.dumps(state),
                         "an inherited invariant landed in state.json — that is a second "
                         "store, and it can disagree with the PLAN.md that owns it")


class ItDegradesQuietly(_Project):
    def test_missing_ancestor_doc_is_fail_soft(self):  # M4
        _run(self.root, "new-task", "a", "--title", "A")
        self._publish("a", INV)
        self._plan("a").unlink()
        r = _run(self.root, "new-task", "b", "--title", "B", "--depends-on", "a")
        self.assertEqual(r.returncode, 0,
                         "a broken neighbour blocked a new node:\n" + r.stderr + r.stdout)

    def test_ancestor_with_no_invariants_prints_nothing(self):  # M4 [edge]
        _run(self.root, "new-task", "a", "--title", "A")
        r = _run(self.root, "new-task", "b", "--title", "B", "--depends-on", "a")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("inherits", r.stdout.lower(),
                         "an empty inheritance must print NOTHING — a header with no rows "
                         "is noise on every task that has no invariants")

    def test_no_depends_on_prints_nothing(self):  # M4 [edge]
        r = _run(self.root, "new-task", "solo", "--title", "Solo")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("inherits", r.stdout.lower())


if __name__ == "__main__":
    unittest.main()
