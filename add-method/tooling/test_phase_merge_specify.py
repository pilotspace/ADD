#!/usr/bin/env python3
"""Red/green tests for phase-merge-specify (six-phase-loop 1/6, frozen v1): the
scenarios PHASE folds into specify — one drafting phase produces §1 AND §2; the
PLAN.md §-section shape is untouched (sections are the stable API). Legacy state
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
        self._ok("new-task", "t", "--title", "T")

    def _freeze(self, slug="t"):
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        direction->build. freeze-gate-universal sweep."""
        p = self.tmp / ".add" / "tasks" / slug / "PLAN.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-07-14.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _phase(self, slug="t"):
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        return state["tasks"][slug]["phase"]


class PhaseListTest(_Harness):
    def test_phases_has_no_scenarios(self):                        # M1
        self.assertNotIn("scenarios", PHASES)
        # (phase-collapse-3 later dropped specify/plan/tests as SEPARATE phases too —
        # this suite pins ITS merge: scenarios gone, the front opens at `direction`)
        self.assertEqual(PHASES[0], "direction")

    def test_maps_carry_no_scenarios_key(self):                    # M1
        for name, mapping in (("PHASE_GUIDE", PHASE_GUIDE), ("PHASE_OWNER", PHASE_OWNER),
                              ("PHASE_AGENT", PHASE_AGENT)):
            self.assertNotIn("scenarios", mapping, f"{name} still maps the retired phase")
        self.assertEqual(PHASE_GROUPS["DIRECTION"], ("direction",))
        self.assertNotIn("scenarios", _SKIPPABLE_PHASES)

    # test_specify_guide_action_names_gwt DELETED: a PROSE-WORDING pin (the exact
    # phrase "Given/When/Then") — phase-collapse-3 reworded PHASE_GUIDE["direction"]'s
    # action to "§2 one scenario per rule", carrying the same duty in different words.
    # No `specify` key remains to hold the old pin at all; re-adding a substring check
    # against the new wording would pin prose, not behavior (authorization W).


class AdvanceTest(_Harness):
    # test_advance_specify_lands_plan DELETED: its premise (advancing WITHIN the front
    # span, before any freeze, scenarios no longer stopping it) no longer applies — the
    # front collapsed into ONE `direction` phase (phase-collapse-3), so a bare `advance`
    # from a fresh, unfrozen task now attempts the direction->build crossing and is
    # REFUSED (contract_not_drafted), never a same-span hop. That refusal floor is
    # already pinned by
    # test_phase_collapse.py::TheFloorsAreUnchanged.test_freeze_floors_unchanged; the
    # legitimate crossing is pinned by
    # test_phase_collapse.py::OneFreezeCrossesTheFront.test_freeze_cross_universal_from_direction.

    def test_phase_cmd_scenarios_maps_to_direction(self):          # R1 (retargeted:
        # phase-collapse-3's LEGACY_PHASES recognizes "scenarios" as a legacy alias —
        # mapped to direction, never refused as an unknown token)
        self._board()
        out, code = self._run("phase", "scenarios", "t")
        self.assertEqual(code, 0, "scenarios is a recognized legacy alias, not refused")
        self.assertEqual(self._phase(), "direction")
        self.assertIn("direction", out, "the mapping must be noted in the output")

    def test_advance_to_scenarios_is_noop_at_direction(self):      # R1
        # "scenarios" maps to "direction" itself — a fresh task is already there, so
        # --to scenarios is the friendly same-phase no-op, never a refusal.
        self._board()
        out2, code2 = self._run("advance", "--to", "scenarios")
        self.assertEqual(code2, 0, "already at direction: --to scenarios is a friendly no-op")
        self.assertEqual(self._phase(), "direction")


class LegacyStateTest(_Harness):
    def test_legacy_state_token_normalizes(self):                  # M2 + Boundary
        self._board()
        sp = self.tmp / ".add" / "state.json"
        raw = json.loads(sp.read_text(encoding="utf-8"))
        raw["tasks"]["t"]["phase"] = "scenarios"                   # a pre-merge record
        sp.write_text(json.dumps(raw), encoding="utf-8")
        out = self._ok("status")                                   # any state read
        self.assertNotIn("phase=scenarios", out.replace(" ", ""))
        # read-side normalization (never a task-file rewrite): the RAW state.json still
        # carries the legacy token; load_state is what maps it to "direction".
        loaded = add.load_state(self.tmp / ".add")
        self.assertEqual(loaded["tasks"]["t"]["phase"], "direction",
                         "the legacy 'scenarios' record normalizes to 'direction' at load")


class LegacySkipDeclarationTest(_Harness):
    def _declare_skip(self, token):
        p = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^phase:.*$", text)
        self.assertIsNotNone(m, "no phase marker line to anchor the skip header")
        text = text[:m.end()] + f"\nskips: {token}" + text[m.end():]
        p.write_text(text, encoding="utf-8")

    def test_old_skip_declaration_tolerated_loud(self):            # M3 + R2 + Boundary
        # Tolerated-and-ignored, noted LOUD, never a die — the frozen behavior.
        # (phase-merge-verify retired the whole grammar and moved the note from the
        # observe crossing — which no longer exists — to gate/completion, the one
        # seam that still reads the header. phase-collapse-3: the front collapsed
        # into ONE `direction` phase, so exercising "a crossing never dies on this
        # header" now means the direction->build crossing, which needs a frozen §3.)
        self._board()
        self._declare_skip("scenarios")
        self._freeze()
        out, code = self._run("advance")                           # direction -> build, silent
        self.assertEqual(code, 0,
                         f"a retired scenarios skip declaration must never die: {out}")
        self.assertEqual(self._phase(), "build")
        self._ok("phase", "verify", "t")
        out = self._ok("gate", "PASS", "t")
        self.assertIn("ignored", out,
                      "the ignored declaration must be noted loud at the gate seam")

    def test_truly_bad_skip_token_still_refused_by_resolver(self):  # R2 (floor held)
        # The advance-time die retired with the grammar; the resolver keeps naming
        # a truly bad token so no reader ever silently honors one.
        toks, err = add._task_skip_set("skips: build\n")
        self.assertEqual(toks, frozenset())
        self.assertTrue(err and err.startswith("skip_not_allowed"), err)


if __name__ == "__main__":
    unittest.main()
