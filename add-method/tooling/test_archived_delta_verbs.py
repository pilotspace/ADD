"""archived-delta-verbs (method-ergonomics): drop/carry/reopen-delta reach a light-archived task.

CONTRACT:
  A light-archived task (slug ∉ state.tasks, .add/tasks/<slug>/TASK.md still on disk) is a
  valid EXPLICIT target for the three delta write verbs — the delta lifecycle lives in the
  FILE, and `deltas` already lists these; previously resolving one needed a hand edit.
  The active-task fallback (no slug) NEVER resolves to an archived task; a slug that is
  neither in state nor on disk still dies `unknown task` (compacted bundles stay out of
  reach). Output for an archived target carries an explicit `(archived` marker.
Run: python3 -m unittest test_archived_delta_verbs -v
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

OPEN = "  - [SPEC · open] widen the retry window (evidence: task-x §6)\n"
CARRIED = "  - [SPEC · carried] widen the retry window (evidence: task-x §6) [carried: parked for v2]\n"


class ArchivedDeltaVerbsTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-adv-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._run("init", "--name", "demo", "--stage", "mvp")
        self._run("lock", "--force")
        self._run("new-task", "gone", "--title", "Archived task")
        self._run("new-task", "live", "--title", "Live task")
        self.gone_md = self.tmp / ".add" / "tasks" / "gone" / "TASK.md"
        # mirror light archive's observable effect: state entry dropped, file kept
        sj = self.tmp / ".add" / "state.json"
        state = json.loads(sj.read_text(encoding="utf-8"))
        del state["tasks"]["gone"]
        state["active_task"] = "live"
        sj.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    def _run(self, *argv, expect_die=False):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code or 0
        if expect_die:
            self.assertNotEqual(code, 0, f"{argv} unexpectedly succeeded: {buf.getvalue()}")
        else:
            self.assertEqual(code, 0, f"{argv} exited {code}: {err.getvalue()}")
        return buf.getvalue() + err.getvalue()

    def _seed_delta(self, line):
        t = self.gone_md.read_text(encoding="utf-8")
        marker = "### Spec delta\n"
        i = t.index(marker) + len(marker)
        # skip the grammar line under the heading
        j = t.index("\n", i) + 1
        self.gone_md.write_text(t[:j] + line + t[j:], encoding="utf-8")

    def test_drop_reaches_archived(self):                      # scenario 1
        self._seed_delta(OPEN)
        out = self._run("drop-delta", "gone")
        self.assertIn("(archived", out)
        self.assertIn("[SPEC · dropped]", self.gone_md.read_text(encoding="utf-8"))

    def test_carry_reaches_archived(self):                     # scenario 2
        self._seed_delta(OPEN)
        out = self._run("carry-delta", "gone", "--reason", "parked for v2")
        self.assertIn("(archived", out)
        body = self.gone_md.read_text(encoding="utf-8")
        self.assertIn("[SPEC · carried]", body)
        self.assertIn("[carried: parked for v2]", body)

    def test_reopen_reaches_archived(self):                    # scenario 3
        self._seed_delta(CARRIED)
        out = self._run("reopen-delta", "gone")
        self.assertIn("(archived", out)
        body = self.gone_md.read_text(encoding="utf-8")
        self.assertIn("[SPEC · open]", body)
        self.assertNotIn("[carried:", body)

    def test_unknown_slug_still_dies(self):                    # scenario 4
        out = self._run("drop-delta", "nowhere", expect_die=True)
        self.assertIn("unknown task", out)

    def test_slug_stays_explicit(self):                        # scenario 5
        # the delta verbs take a REQUIRED positional slug — an archived target can only ever
        # be named explicitly; there is no fallback that could wander to 'gone'
        self._seed_delta(OPEN)
        out = self._run("drop-delta", expect_die=True)
        self.assertIn("required: slug", out)
        self.assertIn("[SPEC · open]", self.gone_md.read_text(encoding="utf-8"))

    def test_state_untouched_by_archived_write(self):          # scenario 6
        self._seed_delta(OPEN)
        sj = self.tmp / ".add" / "state.json"
        before = sj.read_bytes()
        self._run("drop-delta", "gone")
        self.assertEqual(before, sj.read_bytes(), "an archived-target delta write must not touch state")


if __name__ == "__main__":
    unittest.main()
