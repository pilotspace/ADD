"""bundle-advance (method-ergonomics): fast-forward the bundle's bookkeeping crossings +
a recorded, legal post-freeze re-cross.

CONTRACT:
  advance --to <phase>: repeats the single-step advance (every existing crossing guard runs
    per step) until the task reaches <phase>. HARD LIMIT: <phase> is at most `tests` — the
    tests->build crossing carries the gate stack and is never fast-forwarded.
    Reject codes: advance_to_invalid · advance_to_stops_at_tests · advance_to_not_forward.
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
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

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
        for _ in range(5):                       # ground→specify→scenarios→contract→tests→build
            self._silent("advance", slug)
        self.assertEqual(self._phase(slug), "build")


class AdvanceToTest(_Harness):
    def test_to_tests_one_call(self):                            # scenario 1
        self._silent("new-task", "t", "--title", "F")
        out = self._silent("advance", "t", "--to", "tests")
        self.assertEqual(self._phase("t"), "tests")
        self.assertIn("-> tests", out)

    def test_to_past_tests_refused(self):                        # scenario 2
        self._silent("new-task", "t", "--title", "F")
        code, out = self._run("advance", "t", "--to", "build")
        self.assertNotEqual(code, 0)
        self.assertIn("advance_to_stops_at_tests", out)
        self.assertEqual(self._phase("t"), "ground", "phase unchanged on refusal")

    def test_to_not_forward_refused(self):                       # scenario 3
        self._silent("new-task", "t", "--title", "F")
        self._silent("advance", "t", "--to", "tests")
        code, out = self._run("advance", "t", "--to", "specify")
        self.assertNotEqual(code, 0)
        self.assertIn("advance_to_not_forward", out)
        self.assertEqual(self._phase("t"), "tests")

    def test_to_invalid_refused(self):                           # scenario 4
        self._silent("new-task", "t", "--title", "F")
        code, out = self._run("advance", "t", "--to", "bogus")
        self.assertNotEqual(code, 0)
        self.assertIn("advance_to_invalid", out)

    def test_plain_advance_unchanged(self):                      # scenario 5 (additive)
        self._silent("new-task", "t", "--title", "F")
        self._silent("advance", "t")
        self.assertEqual(self._phase("t"), "specify")


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
        self._silent("new-task", "t", "--title", "F")
        for _ in range(4):                                       # ground → tests
            self._silent("advance", "t")
        self._silent("advance", "t", "--skip-freeze")            # DRAFT §3 crossing, recorded
        self.assertEqual(self._phase("t"), "build")
        code, out = self._run("re-cross", "t", "--by", "Tin")
        self.assertNotEqual(code, 0)
        self.assertIn("contract_not_frozen", out)


if __name__ == "__main__":
    unittest.main()
