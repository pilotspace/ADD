#!/usr/bin/env python3
"""Red/green tests for `add.py report <task>` — the read-only per-task PHASE DETAIL.

The drill-down renders a single task's seven phase blocks (specify→observe), each with
its captured §N body from TASK.md + reached/current marker from state.json; the verify
block surfaces the recorded GATE from state (authoritative, never parsed from prose). It
is STRICTLY read-only and purely additive — the v9 milestone rollup is untouched. Run:
    python3 -m unittest test_phase_detail -v
"""
import hashlib
import io
import json as _json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


# A synthetic TASK.md with a known marker per phase so assertions are exact. §5 BUILD is
# only an angle-placeholder (the (empty) case); §6 VERIFY prose deliberately omits the
# word PASS (so a "PASS" in the render can only come from state, not the prose).
_TASK_MD = """# TASK: Alpha demo

## 1 · SPECIFY
SPEC_MARKER the rules live here.
<!-- a comment that must be stripped -->

## 2 · SCENARIOS
SCEN_MARKER given / when / then.

## 3 · CONTRACT
CONTRACT_MARKER the frozen shape.

## 4 · TESTS
TESTS_MARKER red safety net.

## 5 · BUILD
<e.g. only a placeholder body>

## 6 · VERIFY
VERIFY_MARKER reviewer notes look fine here.
<!-- EXIT: stripped marker -->

## 7 · OBSERVE
OBSERVE_MARKER what the loop taught.
"""


class PhaseDetailTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-detail-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "vX", "--title", "Demo", "--goal", "drill in"])
        add.main(["new-task", "alpha", "--title", "Alpha"])
        self._task_md("alpha").write_text(_TASK_MD, encoding="utf-8")

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _state_file(self) -> Path:
        return self._root() / "state.json"

    def _hash_state(self) -> str:
        return hashlib.sha256(self._state_file().read_bytes()).hexdigest()

    def _task_md(self, slug) -> Path:
        return self._root() / "tasks" / slug / "TASK.md"

    def _report(self, *args):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["report", *args])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _done_pass(self, slug):
        add.main(["phase", "verify", slug])
        add.main(["gate", "PASS", slug])

    # ---- scenarios --------------------------------------------------------
    def test_drill_renders_seven_phases(self):
        add.main(["phase", "contract", "alpha"])
        before = self._hash_state()
        out, _, code = self._report("vX", "alpha")
        self.assertEqual(code, 0)
        names = ["1 SPECIFY", "2 SCENARIOS", "3 CONTRACT", "4 TESTS",
                 "5 BUILD", "6 VERIFY", "7 OBSERVE"]
        # all seven present, in order
        positions = [out.find(n) for n in names]
        self.assertNotIn(-1, positions, "a phase block is missing")
        self.assertEqual(positions, sorted(positions), "phase blocks out of order")
        # §1–§3 captured content shown
        for marker in ("SPEC_MARKER", "SCEN_MARKER", "CONTRACT_MARKER"):
            self.assertIn(marker, out)
        # ascii tier under a non-tty StringIO: reached '#', current '>', pending '.'
        self.assertIn("> 3 CONTRACT", out)   # contract is current
        self.assertIn("# 1 SPECIFY", out)    # specify reached
        self.assertIn(". 4 TESTS", out)      # tests pending
        self.assertEqual(self._hash_state(), before)  # read-only

    def test_verify_block_shows_gate_from_state(self):
        # §6 prose has NO 'PASS' — a PASS in the render proves it came from state.json
        self._done_pass("alpha")
        out, _, code = self._report("vX", "alpha")
        self.assertEqual(code, 0)
        self.assertIn("GATE  PASS", out)          # verify block sources gate from state
        self.assertNotIn("PASS", _TASK_MD)        # guard: the fixture prose never says PASS
        self.assertIn("# 6 VERIFY", out)          # every block reached (done)
        self.assertIn("# 7 OBSERVE", out)

    def test_unfilled_phase_is_empty(self):
        out, _, code = self._report("vX", "alpha")
        self.assertEqual(code, 0)
        # §5 BUILD body is only a placeholder -> (empty), never a silent gap
        build_at = out.find("5 BUILD")
        verify_at = out.find("6 VERIFY")
        self.assertNotEqual(build_at, -1)
        self.assertIn("(empty)", out[build_at:verify_at])

    def test_unknown_task_rejected(self):
        before = self._hash_state()
        out, err, code = self._report("vX", "ghost")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown_task", err)
        self.assertEqual(out, "")
        self.assertEqual(self._hash_state(), before)

    def test_unknown_milestone_rejected(self):
        _, err, code = self._report("v99", "alpha")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown_milestone", err)

    def test_smart_single_arg_drills_by_task(self):
        add.main(["phase", "contract", "alpha"])
        # 'alpha' is a task, not a milestone -> drills; identical to explicit form
        out_smart, _, c1 = self._report("alpha")
        out_explicit, _, c2 = self._report("vX", "alpha")
        self.assertEqual(c1, 0)
        self.assertEqual(c2, 0)
        self.assertIn("1 SPECIFY", out_smart)         # it drilled, not rolled up
        self.assertEqual(out_smart, out_explicit)     # same render either way
        # a name that is neither milestone nor task -> unknown_milestone (milestone-first)
        _, err, code = self._report("ghost")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown_milestone", err)

    def test_rollup_unaffected(self):
        out, _, code = self._report("vX")   # name is a milestone -> v9 rollup
        self.assertEqual(code, 0)
        self.assertIn("VERDICT", out)               # the rollup header grid
        self.assertNotIn("1 SPECIFY", out)          # NOT the phase detail

    def test_detail_is_read_only(self):
        state = add.load_state(self._root())
        before = self._hash_state()
        a = add.render_task_detail(self._root(), state, "vX", "alpha")
        b = add.render_task_detail(self._root(), state, "vX", "alpha")
        self.assertEqual(a, b)                       # pure / deterministic
        self.assertEqual(self._hash_state(), before)  # zero writes

    def test_json_dumps_task_phases(self):
        before = self._hash_state()
        out, _, code = self._report("vX", "alpha", "--json")
        self.assertEqual(code, 0)
        data = _json.loads(out)
        self.assertEqual(len(data), 8)
        self.assertEqual([d["n"] for d in data], [0, 1, 2, 3, 4, 5, 6, 7])
        for d in data:
            self.assertIn("phase", d)
            self.assertIn("body", d)
        self.assertEqual(self._hash_state(), before)  # read-only

    def test_unreadable_file_failclosed(self):
        # design-for-failure: an existing-but-unreadable TASK.md must NOT crash —
        # every phase fails closed to "(empty)", never a bare traceback.
        from unittest import mock
        with mock.patch.object(Path, "read_text", side_effect=OSError("boom")):
            phases = add.task_phases(self._root(), "alpha")
        self.assertEqual(len(phases), 8)
        self.assertTrue(all(p["body"] == "(empty)" for p in phases))

    def test_task_phases_pure_extraction(self):
        phases = add.task_phases(self._root(), "alpha")
        self.assertEqual(len(phases), 8)
        self.assertEqual([p["phase"] for p in phases],
                         ["ground", "specify", "scenarios", "contract", "tests",
                          "build", "verify", "observe"])
        bodies = {p["n"]: p["body"] for p in phases}
        self.assertIn("SPEC_MARKER", bodies[1])
        self.assertNotIn("a comment that must be stripped", bodies[1])  # HTML comment gone
        self.assertNotIn("EXIT:", bodies[6])                            # EXIT marker gone
        self.assertEqual(bodies[5], "(empty)")                         # placeholder-only


if __name__ == "__main__":
    unittest.main()
