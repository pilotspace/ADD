#!/usr/bin/env python3
"""Red/green tests for phase-merge-specify (six-phase-loop 1/6, frozen v1): the
scenarios PHASE folds into specify — one drafting phase produces §1 AND §2; the
TASK.md §-section shape is untouched (sections are the stable API). Legacy state
tokens normalize on read (expectations-first precedent); a pre-merge header skip
declaration naming scenarios is tolerated loud, never a die.

Run: python3 -m unittest test_phase_merge_specify -v
"""
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
from add_engine.constants import (PHASES, _SKIPPABLE_PHASES, PHASE_GUIDE,
                                  PHASE_OWNER, PHASE_GROUPS, PHASE_AGENT)


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-pms-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _ok(self, *argv):
        text, code = self._run(*argv)
        self.assertEqual(code, 0, f"{argv} exited {code}: {text}")
        return text

    def _board(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T", "--oneshot")

    def _phase(self, slug="t"):
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        return state["tasks"][slug]["phase"]


class PhaseListTest(_Harness):
    def test_phases_has_no_scenarios(self):                        # M1
        self.assertNotIn("scenarios", PHASES)
        self.assertEqual(PHASES, ("specify", "plan", "tests", "build", "verify",
                                  "observe", "done"))

    def test_maps_carry_no_scenarios_key(self):                    # M1
        for name, mapping in (("PHASE_GUIDE", PHASE_GUIDE), ("PHASE_OWNER", PHASE_OWNER),
                              ("PHASE_AGENT", PHASE_AGENT)):
            self.assertNotIn("scenarios", mapping, f"{name} still maps the retired phase")
        self.assertEqual(PHASE_GROUPS["DIRECTION"], ("specify", "plan", "tests"))
        self.assertEqual(_SKIPPABLE_PHASES, ("observe",))

    def test_specify_guide_action_names_gwt(self):                 # M1
        self.assertIn("Given/When/Then", PHASE_GUIDE["specify"][0],
                      "the merged specify action must carry scenarios' Given/When/Then duty")


class AdvanceTest(_Harness):
    def test_advance_specify_lands_plan(self):                     # M1 + Accept
        self._board()
        self._ok("advance")
        self.assertEqual(self._phase(), "plan",
                         "a bare advance from specify must land at plan (no scenarios stop)")

    def test_new_phase_cmd_scenarios_refused(self):                # R1
        self._board()
        out, code = self._run("phase", "scenarios", "t")
        self.assertNotEqual(code, 0, "scenarios is no longer a phase token")
        out2, code2 = self._run("advance", "--to", "scenarios")
        self.assertNotEqual(code2, 0)


class LegacyStateTest(_Harness):
    def test_legacy_state_token_normalizes(self):                  # M2 + Boundary
        self._board()
        sp = self.tmp / ".add" / "state.json"
        raw = json.loads(sp.read_text(encoding="utf-8"))
        raw["tasks"]["t"]["phase"] = "scenarios"                   # a pre-merge record
        sp.write_text(json.dumps(raw), encoding="utf-8")
        out = self._ok("status")                                   # any state read
        self.assertNotIn("phase=scenarios", out.replace(" ", ""))
        self._ok("advance")                                        # specify -> plan works
        self.assertEqual(self._phase(), "plan")


class LegacySkipDeclarationTest(_Harness):
    def _declare_skip(self, token):
        p = self.tmp / ".add" / "tasks" / "t" / "TASK.md"
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^phase:.*$", text)
        self.assertIsNotNone(m, "no phase marker line to anchor the skip header")
        text = text[:m.end()] + f"\nskips: {token}" + text[m.end():]
        p.write_text(text, encoding="utf-8")

    def test_old_skip_declaration_tolerated_loud(self):            # M3 + R2 + Boundary
        # The note fires at the crossing where the skip machinery reads the header —
        # the observe crossing (M13 of fast-lane-skips: non-skippable crossings run
        # ZERO skip logic; that frozen placement is preserved, so earlier advances
        # sail through silently and nothing ever dies).
        self._board()
        self._declare_skip("scenarios")
        out, code = self._run("advance")                           # specify -> plan, silent
        self.assertEqual(code, 0,
                         f"a retired scenarios skip declaration must never die: {out}")
        self.assertEqual(self._phase(), "plan")
        self._ok("phase", "verify", "t")
        out, code = self._run("advance")                           # verify -> observe crossing
        self.assertEqual(code, 0, f"the observe crossing must tolerate it too: {out}")
        self.assertIn("merged into specify", out,
                      "the ignored declaration must be noted loud at the skip crossing")
        self.assertEqual(self._phase(), "observe")

    def test_truly_bad_skip_token_still_dies(self):                # R2 (floor held)
        self._board()
        self._declare_skip("build")                                # never skippable
        self._ok("phase", "verify", "t")
        out, code = self._run("advance")                           # the observe crossing
        self.assertNotEqual(code, 0,
                            "a non-skippable token must keep the existing die at the "
                            "crossing where a skip could take effect")


if __name__ == "__main__":
    unittest.main()
