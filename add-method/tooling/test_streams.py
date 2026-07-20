#!/usr/bin/env python3
"""v11 — parallel-streams safety: the ENGINE behavior the concurrency rubric leans on.

streams.md is the opt-in concurrency rubric; it changes NO add.py code. The one safety
guarantee that IS engine-enforced — and thus tested here — is slug routing: advance/gate/
phase act on the EXPLICIT <slug>, and omitting it falls back to the single active_task.
streams.md tells the orchestrator to name the task every time precisely because that
fallback races once more than one stream is live. If the precedence ever flipped, every
parallel orchestration would corrupt the wrong task while the rubric still read as safe.

(The rubric's prose clauses — design-for-failure rules, the human floor — are no longer
word-pinned here: doc wording is free to evolve; only the engine contract is guarded.)

Run: python3 -m unittest test_streams -v
"""
import contextlib
import hashlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
SKILL = _ADD_METHOD / "skill" / "add"

_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class SlugRoutingPrecedenceTest(unittest.TestCase):
    """advance/gate/phase act on the EXPLICIT slug; omitting it uses active_task.

    This is the engine contract streams.md §'Who writes what' depends on. Two tasks
    exist; 'b' is active (created last). Naming 'a' must mutate ONLY 'a' and must
    leave active_task untouched — proving the orchestrator can drive any stream
    without first switching focus."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-streams-route-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", "a"])   # auto-linked to mvp
        add.main(["new-task", "b"])   # active_task is now 'b'
        self.state_path = Path(self.tmp) / ".add" / "state.json"

    def tearDown(self):
        os.chdir(self._cwd)

    def _state(self):
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _freeze(self, slug):
        """Stamp §3 FROZEN + a well-formed flag so `advance` (no admin override) can
        actually cross the slug's direction->build gate. freeze-gate-universal sweep."""
        p = Path(self.tmp) / ".add" / "tasks" / slug / "PLAN.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def test_active_task_is_b_after_setup(self):
        # premise check: the LAST-created task is active, so naming 'a' is the non-trivial path
        self.assertEqual(self._state()["active_task"], "b")

    def test_phase_routes_to_explicit_slug_not_active(self):
        code, _, _ = _run(["phase", "verify", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "verify", "the NAMED task must change")
        self.assertEqual(st["tasks"]["b"]["phase"], "direction", "the active task must NOT change")
        self.assertEqual(st["active_task"], "b", "phase <slug> must not steal focus from active_task")

    def test_advance_routes_to_explicit_slug_not_active(self):
        self._freeze("a")                        # a bare advance now needs a frozen §3 to cross
        code, _, _ = _run(["advance", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "build", "advance must step the NAMED task")
        self.assertEqual(st["tasks"]["b"]["phase"], "direction", "the active task must NOT step")
        self.assertEqual(st["active_task"], "b")

    def test_gate_routes_to_explicit_slug_not_active(self):
        _run(["phase", "verify", "a"])          # bring 'a' to verify so PASS is legal
        code, _, _ = _run(["gate", "PASS", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "done")
        self.assertEqual(st["tasks"]["a"]["gate"], "PASS", "gate must record on the NAMED task")
        self.assertEqual(st["tasks"]["b"]["phase"], "direction", "the active task must be untouched")
        self.assertEqual(st["tasks"]["b"].get("gate", "none"), "none", "no gate may land on 'b'")
        self.assertEqual(st["active_task"], "b")

    def test_omitted_slug_falls_back_to_active_task(self):
        # the documented fallback (and the race premise): no slug => act on active_task ('b')
        self._freeze("b")                        # a bare advance now needs a frozen §3 to cross
        code, _, _ = _run(["advance"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["b"]["phase"], "build", "omitted slug must step the active task")
        self.assertEqual(st["tasks"]["a"]["phase"], "direction", "the non-active task must be untouched")


# ── wave-protocol-runtime: merge-time fork-base shift + worker commits its report ──
# v19 wave deltas #7 (merge-time fork-base) + #8 (worker commits SUMMARY.md). streams.md must
# MIRROR the folded CONVENTIONS runtime-exception: on a spawn-time-worktree runner the pre-spawn
# rev-parse cell is unsatisfiable, so the `unverified_fork_base` check SHIFTS to worker step-0
# (sync + re-echo) verified at MERGE-time; and the worker `<return>` contract must COMMIT its
# SUMMARY.md/deltas.md. Token-presence guards (phrasing free, behaviour locked) + ×3 parity.
_REPO = _ADD_METHOD.parent
_STREAMS_TREES = (
    SKILL / "streams.md",                                                              # canonical
    _REPO / ".claude" / "skills" / "add" / "streams.md",                               # dogfood
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "streams.md",  # bundle
)
if __name__ == "__main__":
    unittest.main(verbosity=2)
