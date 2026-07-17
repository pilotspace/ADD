#!/usr/bin/env python3
"""Red/green tests for `add.py guide` — the focused "what do I do next?" printer.

guide is NON-interactive and STRICTLY read-only: it prints the active (or named)
task's phase, the one next action, the chapter to read, and the `then:` command —
and never mutates state. Run: python3 -m unittest test_guide -v
"""
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


class GuideTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-guide-cmd-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _state(self) -> Path:
        return self.tmp / ".add" / "state.json"

    def _guide(self, *args) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["guide", *args])
        return buf.getvalue()

    def _freeze(self, slug: str) -> None:
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = self.tmp / ".add" / "tasks" / slug / "PLAN.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def test_guide_direction_phase(self):
        add.main(["new-task", "feat-a", "--title", "Feat A"])   # active, phase=direction (phase-collapse-3)
        out = self._guide()
        self.assertIn("phase: direction", out)
        self.assertIn("03-step-1-specify.md", out)
        self.assertIn("add.py freeze", out)

    def test_guide_verify_points_at_gate(self):
        add.main(["new-task", "feat-a"])
        add.main(["phase", "verify", "feat-a"])
        out = self._guide()
        self.assertIn("08-step-6-verify.md", out)
        self.assertIn("add.py gate", out)
        self.assertNotIn("advance", out, "verify must point at the gate, not advance")

    def test_guide_contract_points_at_freeze(self):
        # status-guide-fold: guide reuses the ONE next-step composer, so at
        # plan (ground+contract+build-strategy collapsed) it names the freeze gate —
        # never the divergent `add.py advance`.
        add.main(["new-task", "feat-a"])
        add.main(["phase", "plan", "feat-a"])
        out = self._guide()
        self.assertIn("add.py freeze", out, f"plan guide points at freeze: {out!r}")
        self.assertNotIn("then   : add.py advance", out,
                         "plan must NOT tell the agent to advance")

    # test_guide_front_phase_teaches_collapse DELETED (rule W, authorized 2026-07-16,
    # same justification as test_next_footer_engine's deleted collapse-hint tests): it
    # pinned the exact wording of a transitional "teach the --to plan shortcut" hint from
    # the prior thin-engine-loop W1 milestone. Under phase-collapse-3 the front is already
    # ONE phase (direction) and `guide`'s own `then:` line names `add.py freeze` directly
    # (see test_guide_direction_phase) — there is no more shortcut to teach.

    def test_guide_done_points_at_new_task(self):
        add.main(["new-task", "feat-a"])
        add.main(["phase", "done", "feat-a"])
        out = self._guide()
        self.assertIn("new-task", out)

    def test_guide_no_active_task(self):
        before = self._state().read_bytes()
        out = self._guide()                          # must NOT raise (guidance, not error)
        self.assertIn("new-task", out)
        self.assertEqual(self._state().read_bytes(), before, "guide must not mutate state")

    def test_guide_explicit_slug(self):
        add.main(["new-task", "feat-a"])
        self._freeze("feat-a")                   # freeze-gate-universal sweep
        add.main(["phase", "build", "feat-a"])
        add.main(["new-task", "feat-b"])             # active becomes feat-b (specify)
        out = self._guide("feat-a")                  # explicit slug overrides active
        self.assertIn("phase: build", out)
        self.assertIn("07-step-5-build.md", out)

    def test_guide_unknown_slug_errors(self):
        add.main(["new-task", "feat-a"])
        before = self._state().read_bytes()
        err = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stderr(err):
            add.main(["guide", "does-not-exist"])
        self.assertIn("unknown task", err.getvalue(),
                      "must fail for the right reason (unknown task), not a parse error")
        self.assertEqual(self._state().read_bytes(), before)

    def test_guide_is_read_only(self):
        add.main(["new-task", "feat-a"])
        before = self._state().read_bytes()
        self._guide()
        self.assertEqual(self._state().read_bytes(), before,
                         "guide is read-only: state.json must be byte-identical")

    def test_guide_unknown_phase_dies_clean(self):
        # a hand-corrupted phase value must produce a clean _die, not a raw KeyError
        add.main(["new-task", "feat-a"])
        sp = self._state()
        st = json.loads(sp.read_text(encoding="utf-8"))
        st["tasks"]["feat-a"]["phase"] = "planning"        # not a real PHASES value
        sp.write_text(json.dumps(st), encoding="utf-8")
        err = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stderr(err):
            add.main(["guide", "feat-a"])
        self.assertIn("planning", err.getvalue(),
                      "guide must _die naming the bad phase, not raise a raw KeyError")


if __name__ == "__main__":
    unittest.main(verbosity=2)
