#!/usr/bin/env python3
"""Red/green tests for phase-parallel execution (maximize throughput via the phase-agent roster).

streams.md gains a "phase-parallel execution" section: under parallel+auto the machine-led phases
PREFER spawning the registered phase-specialist (`add:add-<phase>`) over doing the work in-context,
and they fan out — ground/tests/verify/observe run concurrently across the wave's ready tasks, and a
single task's BUILD fans out two ways: SPLIT (disjoint §5 sub-units, merged serially) or MULTIPLE
attempts (a tournament keeping the cleanest earned-green). The irreducible floor is untouched:
human gates, SECURITY HARD-STOP, serial integration Verify, propose-not-record, worktree isolation.

Run: python3 -m unittest test_phase_parallel -v
"""
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

SKILL_TREES = (
    PKG_ROOT / "skill" / "add",
    REPO_ROOT / ".claude" / "skills" / "add",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",
)
CANON = SKILL_TREES[0]
# the machine-led phases the enhancement parallelizes (the human-gated spec phases are excluded)
PARALLEL_PHASES = ("ground", "tests", "build", "verify", "observe")


def _streams(tree: Path) -> str:
    return (tree / "streams.md").read_text(encoding="utf-8")


class PhaseParallelSectionTest(unittest.TestCase):
    def setUp(self):
        self.text = _streams(CANON)
        self.low = self.text.lower()

    # scenario: a dedicated section documents phase-parallel execution
    def test_section_present(self):
        self.assertIn("phase-parallel", self.low,
                      "streams.md must carry a phase-parallel execution section")

    # scenario: the section PREFERS spawning the registered roster for machine-led phases
    def test_prefers_spawning_the_roster(self):
        self.assertIn("prefer", self.low, "the section must make spawning the PREFERRED default")
        self.assertIn("add:add-", self.text,
                      "the section must spawn the registered roster (add:add-<phase>)")

    # scenario: the five machine-led phases are named as parallelizable
    def test_names_machine_led_phases(self):
        for phase in PARALLEL_PHASES:
            self.assertIn(phase, self.low, f"the section must name the {phase} phase")

    # scenario: BUILD fans out two ways — split, and multiple attempts (tournament)
    def test_build_fanout_modes(self):
        self.assertIn("split", self.low, "build fan-out must document the SPLIT mode")
        self.assertTrue("tournament" in self.low or "attempt" in self.low,
                        "build fan-out must document MULTIPLE attempts (a tournament)")

    # scenario: the irreducible floor is restated — parallelism never lowers a gate
    def test_floor_preserved(self):
        self.assertIn("hard-stop", self.low, "security HARD-STOP must remain stated")
        # serial integration Verify is the existing guard the section must not contradict
        self.assertIn("integration", self.low, "serial integration Verify must remain")

    # scenario: byte-identical across the skill trees
    def test_streams_parity(self):
        bodies = {_streams(t) for t in SKILL_TREES}
        self.assertEqual(len(bodies), 1, "streams.md must be byte-identical across skill trees")


if __name__ == "__main__":
    unittest.main(verbosity=2)
