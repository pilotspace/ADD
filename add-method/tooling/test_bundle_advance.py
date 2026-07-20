"""bundle-advance (method-ergonomics): fast-forward the bundle's bookkeeping crossings +
a recorded, legal post-freeze re-cross.

CONTRACT (phase-collapse-3: direction·build·verify·done):
  advance --to <phase>: --to has no bundle bookkeeping left to fast-forward now the front
    is ONE phase (direction). A target at/behind direction is a friendly no-op; any target
    past direction dies — the direction->build crossing carries the gate stack and is never
    fast-forwarded. Reject codes: advance_to_invalid · advance_to_stops_at_direction.
  re-cross <slug> --by <name>: for a task at build/verify whose §3 is FROZEN, re-runs the
    IDENTICAL _build_entry gate stack (freeze gate · flag check · tamper tripwire · §5 scope
    snapshot), sets phase=build, and records {by, at, from_phase} in state["tasks"][slug]
    ["recross"] — the auditable trail for a HUMAN-APPROVED post-freeze test addition.
    Reject codes: recross_wrong_phase · recross_unsigned; the freeze gate still refuses a
    DRAFT §3 (contract_not_frozen) — re-cross is never a freeze bypass.
One test per scenario. Run: python3 -m unittest test_bundle_advance -v
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-badv-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code, out.getvalue()

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))

    def _phase(self, slug):
        return self._state()["tasks"][slug]["phase"]

    def _task_md(self, slug):
        return self.tmp / ".add" / "tasks" / slug / "PLAN.md"

    def _freeze(self, slug):
        p = self._task_md(slug)
        t = (p.read_text(encoding="utf-8")
             .replace("Status: DRAFT", "Status: FROZEN @ v1 — approved by T"))
        t = t.replace(
            "Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>",
            "Reported: yes\nLeast-sure flag surfaced at freeze: ⚠ [contract] shape guessed "
            "from thin input — because no prior art; if wrong: rework the endpoint")
        p.write_text(t, encoding="utf-8")

    def _to_build(self, slug):
        self._silent("new-task", slug, "--title", "F")
        tests_dir = self.tmp / ".add" / "tasks" / slug / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "test_red.py").write_text("def test_x():\n    assert False\n",
                                               encoding="utf-8")
        self._freeze(slug)
        self._silent("advance", slug)            # direction -> build (the ONE crossing)
        self.assertEqual(self._phase(slug), "build")


class AdvanceToTest(_Harness):
    def test_to_direction_is_noop(self):                          # scenario 1 (phase-collapse-3)
        # --to has no bundle bookkeeping left to fast-forward now the front is ONE phase
        # (direction); a still-inside-the-span target (direction itself, or a legacy
        # front alias) is a friendly no-op — the build crossing is never fast-forwarded.
        self._silent("new-task", "t", "--title", "F")
        out = self._silent("advance", "t", "--to", "direction")
        self.assertEqual(self._phase("t"), "direction")
        self.assertIn("already at direction", out)

    def test_to_past_direction_refused(self):                     # scenario 2
        self._silent("new-task", "t", "--title", "F")
        code, out = self._run("advance", "t", "--to", "build")
        self.assertNotEqual(code, 0)
        self.assertIn("advance_to_stops_at_direction", out)
        self.assertEqual(self._phase("t"), "direction", "phase unchanged on refusal")

    def test_to_backward_from_build_is_noop(self):                # scenario 3 (re-shaped)
        # scenario 3 used to refuse a backward --to with advance_to_not_forward; that
        # reject code is gone post-collapse — going "backward" to direction from a later
        # phase now folds into the SAME already-there no-op branch as going nowhere.
        self._to_build("t")
        out = self._silent("advance", "t", "--to", "direction")
        self.assertIn("already at build", out)
        self.assertEqual(self._phase("t"), "build", "a backward --to must not move the phase")

    def test_to_invalid_refused(self):                           # scenario 4
        self._silent("new-task", "t", "--title", "F")
        code, out = self._run("advance", "t", "--to", "bogus")
        self.assertNotEqual(code, 0)
        self.assertIn("advance_to_invalid", out)

    def test_plain_advance_unchanged(self):                      # scenario 5 (additive; re-shaped)
        # a bare advance on a fresh, unfrozen direction task now refuses outright — the
        # universal freeze gate fires on EVERY crossing into build, not just --to.
        self._silent("new-task", "t", "--title", "F")
        code, out = self._run("advance", "t")
        self.assertNotEqual(code, 0, "an unfrozen direction task must refuse to cross")
        self.assertIn("contract_not_frozen", out)
        self.assertEqual(self._phase("t"), "direction")


class RecrossTest(_Harness):
    def test_recross_rearms_tripwire(self):                      # scenario 6
        self._to_build("t")
        before = self._state()["tasks"]["t"]["tripwire"]
        tests_dir = self.tmp / ".add" / "tasks" / "t" / "tests"
        (tests_dir / "test_added.py").write_text(
            "def test_new():\n    assert False\n", encoding="utf-8")
        out = self._silent("re-cross", "t", "--by", "Tin")
        self.assertEqual(self._phase("t"), "build")
        after = self._state()["tasks"]["t"]
        self.assertNotEqual(before, after["tripwire"], "tripwire re-snapshotted")
        self.assertEqual(after["recross"]["by"], "Tin")
        self.assertEqual(after["recross"]["from_phase"], "build")
        self.assertIn("re-crossed", out)

    def test_recross_from_verify(self):                          # scenario 7
        self._to_build("t")
        self._silent("advance", "t")                             # build -> verify
        self._silent("re-cross", "t", "--by", "Tin")
        self.assertEqual(self._phase("t"), "build")
        self.assertEqual(self._state()["tasks"]["t"]["recross"]["from_phase"], "verify")

    def test_recross_wrong_phase_refused(self):                  # scenario 8
        self._silent("new-task", "t", "--title", "F")
        code, out = self._run("re-cross", "t", "--by", "Tin")
        self.assertNotEqual(code, 0)
        self.assertIn("recross_wrong_phase", out)

    def test_recross_unsigned_refused(self):                     # scenario 9
        self._to_build("t")
        code, out = self._run("re-cross", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("recross_unsigned", out)
        self.assertEqual(self._phase("t"), "build", "nothing moves on refusal")

    def test_recross_never_bypasses_freeze(self):                # scenario 10
        # plan-phase-core: reach build honestly (frozen §3, no skip ever recorded — the
        # ONLY path that reaches build via `advance` with a DRAFT §3 is --skip-freeze at
        # the plan->tests gate, and that marker then carries through every later
        # _build_entry call including re-cross — see report for that suspected gap).
        # This scenario instead proves the freeze gate re-cross itself still enforces: a
        # §3 that reverts to DRAFT post-freeze (e.g. a tampered edit), with no recorded
        # freeze_skipped marker, must still refuse re-cross.
        self._to_build("t")
        st = self._state()
        st["tasks"]["t"].pop("freeze_skipped", None)
        (self.tmp / ".add" / "state.json").write_text(json.dumps(st), encoding="utf-8")
        p = self._task_md("t")
        p.write_text(p.read_text(encoding="utf-8").replace(
            "Status: FROZEN @ v1 — approved by T", "Status: DRAFT"), encoding="utf-8")
        code, out = self._run("re-cross", "t", "--by", "Tin")
        self.assertNotEqual(code, 0)
        self.assertIn("contract_not_frozen", out)


if __name__ == "__main__":
    unittest.main()
