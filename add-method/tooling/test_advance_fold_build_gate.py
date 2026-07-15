#!/usr/bin/env python3
"""Red/green for advance-fold (ceremony-turn-cut): the build-phase next verb steers to
`gate PASS` — which compound-ticks build->verify in ONE call — NOT a redundant separate
`advance` turn. The real wm1 run made `advance` (build->verify) THEN `gate PASS`; the
advance was pure bookkeeping the gate already does (cmd_gate compound tick). Killing that
steer saves one ceremony turn per task (~85k cache-read) with zero trust-floor change.

Run: python3 -m unittest test_advance_fold_build_gate -v
"""
import pathlib
import unittest

import add

# the build guide across all three skill trees (resolved from this file's location)
_TOOLING = pathlib.Path(__file__).resolve().parent          # add-method/tooling
_ADDROOT = _TOOLING.parent                                  # add-method
_REPO = _ADDROOT.parent                                     # repo root
BUILD_GUIDES = [
    _ADDROOT / "skill" / "add" / "phases" / "5-build.md",
    _ADDROOT / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "5-build.md",
    _REPO / ".claude" / "skills" / "add" / "phases" / "5-build.md",
]


class AdvanceFoldBuildGateTest(unittest.TestCase):
    def test_build_next_verb_is_gate_not_advance(self):
        cmd = add._next_command("build")
        self.assertIn("gate PASS", cmd, "build must steer to the compound gate verb")
        self.assertNotIn("advance", cmd,
                         "no redundant advance before gate — compound-ticks crosses build->verify")

    def test_verify_next_verb_unchanged(self):
        self.assertIn("gate PASS", add._next_command("verify"))

    def test_earlier_phase_verbs_unchanged(self):
        # the fold touches ONLY the build fallthrough — front phases keep their exact steer
        self.assertIn("advance --to plan", add._next_command("specify"))
        self.assertIn("freeze --by", add._next_command("plan"))
        self.assertIn("add.py advance", add._next_command("plan", contract_frozen=True))
        self.assertIn("advance --fill", add._next_command("tests"))

    def test_build_guides_steer_to_gate_across_three_trees(self):
        for g in BUILD_GUIDES:
            if not g.exists():
                continue
            txt = g.read_text(encoding="utf-8")
            # the Next section names the compound gate from build, not a bare advance->verify
            self.assertIn("gate PASS", txt, f"{g} must steer build to gate PASS")


if __name__ == "__main__":
    unittest.main()
