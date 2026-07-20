#!/usr/bin/env python3
"""Red/green tests for phase-merge-verify (six-phase-loop 2/6, frozen v1): the
observe PHASE folds into verify — verify owns evidence + gate AND the watch/
spec-delta duty; §7 OBSERVE stays as a section (the stable API) rendered under
verify exactly as §2 renders under specify. The skip grammar retires whole:
nothing is skippable, vestigial declarations are noted loud at gate, never a die.
The two residual ordinal->section mappings (advance --fill · status --section)
repair to the _PHASE_SECTIONS table.

Run: python3 -m unittest test_phase_merge_verify -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-pmv-")).resolve()
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
        p = self.tmp / ".add" / "tasks" / slug / "PLAN.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-07-14.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _phase(self, slug="t"):
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        return state["tasks"][slug]["phase"]

    def _to_verify(self):
        """Drive t direction -> verify (2 hops post phase-collapse-3: direction -> build
        -> verify; freeze first for the direction->build gate)."""
        self._freeze()
        for _ in range(2):
            self._ok("advance", "t")
        self.assertEqual(self._phase(), "verify")


class PhaseListTest(_Harness):
    def test_phases_has_no_observe(self):                          # M1
        self.assertNotIn("observe", PHASES)
        self.assertEqual(PHASES, ("direction", "build", "verify", "done"))

    def test_maps_carry_no_observe_key(self):                      # M1
        for name, mapping in (("PHASE_GUIDE", PHASE_GUIDE), ("PHASE_OWNER", PHASE_OWNER),
                              ("PHASE_AGENT", PHASE_AGENT)):
            self.assertNotIn("observe", mapping, f"{name} still maps the retired phase")
        self.assertEqual(PHASE_GROUPS["VERIFY"], ("verify",))
        self.assertEqual(_SKIPPABLE_PHASES, ())

    def test_verify_guide_action_names_the_observe_duty(self):     # M1
        action = PHASE_GUIDE["verify"][0]
        self.assertIn("spec delta", action,
                      "the merged verify action must carry observe's watch/spec-delta duty")


class AdvanceAndGateTest(_Harness):
    def test_advance_verify_lands_done(self):                      # M1 + Accept
        self._board()
        self._to_verify()
        self._ok("advance", "t")
        self.assertEqual(self._phase(), "done",
                         "a bare advance from verify must land at done (no observe stop)")

    def test_gate_pass_at_verify_marks_done_with_fold_nudge(self):  # M6 + Accept
        self._board()
        self._to_verify()
        out = self._ok("gate", "PASS", "t")
        self.assertEqual(self._phase(), "done")
        self.assertIn("delta-append", out,
                      "gate completion must carry the living-spec delta nudge")

    def test_phase_cmd_observe_maps_to_verify(self):                # R1 (retargeted:
        # phase-collapse-3's LEGACY_PHASES recognizes "observe" as a legacy alias —
        # mapped to verify, never refused as an unknown token)
        self._board()
        out, code = self._run("phase", "observe", "t")
        self.assertEqual(code, 0, "observe is a recognized legacy alias, not refused")
        self.assertEqual(self._phase(), "verify")
        self.assertIn("verify", out, "the mapping must be noted in the output")

    def test_advance_to_observe_stops_at_direction(self):          # R1
        self._board()
        out2, code2 = self._run("advance", "--to", "observe")
        self.assertNotEqual(code2, 0,
                            "observe maps to verify, past the direction span --to may reach")
        self.assertIn("advance_to_stops_at_direction", out2)


class LegacyStateTest(_Harness):
    def test_legacy_observe_state_normalizes(self):                # M2 + Boundary
        # Normalize-on-read (the frozen §1 wording): a READ shows verify and never
        # observe; the next WRITE persists the normalized token — proven by an
        # advance that lands done (verify -> done), impossible from a dead token.
        self._board()
        self._freeze()
        sp = self.tmp / ".add" / "state.json"
        raw = json.loads(sp.read_text(encoding="utf-8"))
        raw["tasks"]["t"]["phase"] = "observe"                     # a pre-merge record
        sp.write_text(json.dumps(raw), encoding="utf-8")
        out = self._ok("status")                                   # any state read
        self.assertNotIn("phase=observe", out.replace(" ", ""))
        self._ok("advance", "t")                                   # verify -> done, persisted
        self.assertEqual(self._phase(), "done")

    def test_legacy_observe_with_recorded_gate_stays_recorded(self):  # M2 + Boundary
        self._board()
        self._to_verify()
        self._ok("gate", "PASS", "t")
        sp = self.tmp / ".add" / "state.json"
        raw = json.loads(sp.read_text(encoding="utf-8"))
        raw["tasks"]["t"]["phase"] = "observe"                     # pre-merge post-gate parking
        sp.write_text(json.dumps(raw), encoding="utf-8")
        self._ok("status")
        raw2 = json.loads(sp.read_text(encoding="utf-8"))
        self.assertEqual(raw2["tasks"]["t"].get("gate"), "PASS",
                         "normalizing observe->verify must not drop the recorded gate")


class VestigialSkipsTest(_Harness):
    def _declare_skip(self, token):
        p = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^phase:.*$", text)
        self.assertIsNotNone(m, "no phase marker line to anchor the skip header")
        p.write_text(text[:m.end()] + f"\nskips: {token}" + text[m.end():],
                     encoding="utf-8")

    def test_vestigial_skips_header_noted_at_gate_never_dies(self):  # M3 + R2 + Boundary
        # The grammar itself is retired: EVERY crossing runs zero skip logic, the
        # declaration is read once, at gate/completion, and ignored loud.
        self._board()
        self._declare_skip("observe")
        self._freeze()
        for _ in range(2):                                          # direction -> build -> verify, silent
            out, code = self._run("advance", "t")
            self.assertEqual(code, 0,
                             f"a vestigial skips: header must never die at a crossing: {out}")
        out = self._ok("gate", "PASS", "t")
        self.assertIn("retired", out,
                      "the ignored declaration must be noted loud at gate")
        self.assertEqual(self._phase(), "done")

    def test_any_token_tolerated_not_just_retired_phases(self):    # R2 (grammar retired whole)
        self._board()
        self._declare_skip("build")                                # was a die pre-merge
        self._freeze()
        for _ in range(2):                                         # direction -> build -> verify
            self._ok("advance", "t")
        out = self._ok("gate", "PASS", "t")
        self.assertIn("retired", out)


class SectionsTableTest(_Harness):
    def test_phase_sections_verify_owns_6_and_7(self):             # M4
        self.assertEqual(add._PHASE_SECTIONS["verify"], (6, 7))
        self.assertEqual(add._PHASE_SECTIONS["direction"], (1, 2, 3, 4),
                         "direction owns the whole front span's sections (§1-§4)")

    def test_section_flag_uses_the_sections_table(self):           # M5
        self._board()
        out1 = self._ok("status", "--section", "direction")
        self.assertIn("Feature:", out1,
                      "--section direction must print §1 SPECIFY (its primary section)")
        out6 = self._ok("status", "--section", "verify")
        self.assertIn("GATE RECORD", out6,
                      "--section verify must print §6 VERIFY (its primary section, not "
                      "ordinal index+1=§3)")

    def test_fill_targets_the_primary_section(self):               # M5
        # At build the table says §5; ordinal math would say §2 (index 1 + 1) — the
        # discriminating hop under the collapsed 4-phase ladder.
        self._board()
        self._freeze()
        self._ok("advance", "t")                                   # direction -> build
        draft = self.tmp / "d.txt"
        draft.write_text("PMV-FILL-MARKER red-suite note", encoding="utf-8")
        self._ok("advance", "t", "--fill", str(draft))             # fills §5 then advances
        body = (self.tmp / ".add" / "tasks" / "t" / "PLAN.md").read_text(encoding="utf-8")
        sec5 = body.split("## 5 ·", 1)[1].split("## 6 ·", 1)[0]
        self.assertIn("PMV-FILL-MARKER", sec5,
                      "--fill at build must write §5 (the table), not §2 (ordinal math)")


if __name__ == "__main__":
    unittest.main()
