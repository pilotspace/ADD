#!/usr/bin/env python3
"""Structural proof of `onboarding-align` — the onboarding surfaces tell the shipped
v7 one-approval flow, and the empty-project entry point is actionable.

Frozen contract (.add/tasks/onboarding-align/PLAN.md §3):
  - the two shipping onboarding surfaces (add-method/GETTING-STARTED.md, add-method/README.md)
    describe ONE flow (intake -> one-approval front -> self-driving run); NO v6/v7 "shipped
    default" version narration; security HARD-STOP intact
  - GETTING-STARTED leads AI-first; the by-hand 7-phase walk is under an
    "under the hood / escape hatch" heading (kept, demoted)
  - empty-project `status` prints a first-run panel naming BOTH `/add` and `new-task`;
    populated `status` does NOT show the panel (regression guard)
  - both add.py trees stay md5-identical

HONEST SCOPE (same caveat as v6/v7/v8): these tests prove the surfaces' WORDS and the
status branch's OUTPUT — not that a human's onboarding experience actually improves.
Words-exist != method-works.

Run: python3 -m unittest test_onboarding_align -v
"""
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANON_ADDPY = _TOOLING / "add.py"
DOGFOOD_ADDPY = _REPO / ".add" / "tooling" / "add.py"

GETTING_STARTED = _ADD_METHOD / "GETTING-STARTED.md"
PKG_README = _ADD_METHOD / "README.md"

# the version-history caveats that must NOT survive in onboarding (the drift)
CAVEAT_SUBSTRINGS = ("as designed in v7", "Today's **shipped**", "three-gate front")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _status_after(cmds: list[list[str]]) -> str:
    """Init a throwaway project, run any setup cmds, return `status` stdout."""
    with tempfile.TemporaryDirectory() as d:
        base = ["python3", str(CANON_ADDPY)]
        subprocess.run(base + ["init", "--name", "demo", "--stage", "prototype"],
                       cwd=d, check=True, capture_output=True, text=True)
        for c in cmds:
            subprocess.run(base + c, cwd=d, check=True, capture_output=True, text=True)
        out = subprocess.run(base + ["status"], cwd=d, check=True,
                             capture_output=True, text=True)
        return out.stdout


class OnboardingAlignTest(unittest.TestCase):
    # --- one flow, no version history -------------------------------------
    def test_no_version_caveat_in_onboarding(self):
        for surface in (GETTING_STARTED, PKG_README):
            text = surface.read_text()
            for caveat in CAVEAT_SUBSTRINGS:
                self.assertNotIn(
                    caveat, text,
                    f"{surface.name} still carries the version caveat {caveat!r} "
                    f"(version_caveat_in_onboarding)")
            self.assertIn(
                "specification bundle", text.lower(),
                f"{surface.name} must name the specification bundle as THE flow")

    # --- GETTING-STARTED leads AI-first; manual walk demoted --------------
    def test_getting_started_leads_ai_first(self):
        text = GETTING_STARTED.read_text()
        low = text.lower()
        # the AI-first conversation path must appear before the by-hand 7-phase walk
        ai_first = low.find("talk to the agent")
        by_hand = low.find("seven phases")
        self.assertNotEqual(ai_first, -1, "no AI-first 'talk to the agent' section found")
        self.assertNotEqual(by_hand, -1, "no by-hand 'seven phases' walk found")
        self.assertLess(ai_first, by_hand,
                        "AI-first path must lead; the by-hand walk comes after (manual_walk_leads)")
        # the by-hand walk must sit under an actual escape-hatch / under-the-hood HEADING
        # (a markdown heading line, not an incidental phrase in prose)
        heading_lines = [ln.lower() for ln in text.splitlines() if ln.lstrip().startswith("#")]
        self.assertTrue(
            any(("under the hood" in h) or ("escape hatch" in h) for h in heading_lines),
            "the by-hand walk must be under an 'under the hood'/'escape hatch' HEADING "
            "(manual_walk_leads)")

    # --- empty-project status is actionable -------------------------------
    def test_status_first_run_panel(self):
        out = _status_after([])
        self.assertIn("/add", out,
                      "empty-project status must name the AI-first move `/add` (silent_empty_state)")
        self.assertIn("new-task", out,
                      "empty-project status must keep the `new-task` escape hatch")

    def test_status_populated_does_not_show_panel(self):
        out = _status_after([["new-task", "demo-task", "--title", "Demo"]])
        self.assertIn("demo-task", out, "populated status must still list the task")
        self.assertNotIn("/add", out,
                         "the first-run panel must fire ONLY on the empty state, not when tasks exist")

    # --- parity: edits land in both add.py trees --------------------------
    def test_addpy_dual_tree_md5(self):
        self.assertEqual(_md5(CANON_ADDPY), _md5(DOGFOOD_ADDPY),
                         "add.py differs between canonical and dogfood trees — edit broke parity")


if __name__ == "__main__":
    unittest.main(verbosity=2)
