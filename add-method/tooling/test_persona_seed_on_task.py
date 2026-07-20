#!/usr/bin/env python3
"""persona-seed-on-task (skill enhancement): every new task establishes a
domain-fit persona BEFORE drafting — seeding one when none fits, reusing
otherwise. Pins the instruction across all three skill trees so the dogfood
+ bundled copies never drift from canon.

The design floor these assertions guard (against the naive "one persona per
task" reading): personas are seeded per DOMAIN and REUSED across tasks — a
new task spawns a seed ONLY when no existing persona fits.

Run: cd add-method/tooling && python3 -m unittest test_persona_seed_on_task -v
"""
import re
import unittest
from pathlib import Path


def _flat(text: str) -> str:
    """Wrap-tolerant: drop markdown blockquote markers + collapse whitespace, so a
    pinned phrase that line-wraps (this project's line-wrap-splits-phrase-pin trap)
    still matches. Lowercased for case-insensitive substring checks."""
    return re.sub(r"\s+", " ", text.replace("\n>", " ")).lower()

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent

SKILL_TREES = [
    _ADD_METHOD / "skill" / "add",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add",
    _ADD_METHOD.parent / ".claude" / "skills" / "add",
]


class PersonaSeedInstructionTest(unittest.TestCase):
    def test_skill_beat_one_names_persona_fit(self):
        for tree in SKILL_TREES:
            flat = _flat((tree / "SKILL.md").read_text(encoding="utf-8"))
            self.assertRegex(
                flat, r"fit persona|persona.*fit|domain-fit persona",
                f"{tree}/SKILL.md beat 1 must point new-task drafting at a fit persona")

    def test_direction_seeds_when_none_fits(self):
        for tree in SKILL_TREES:
            flat = _flat((tree / "phases" / "direction.md").read_text(encoding="utf-8"))
            self.assertIn("persona mode", flat,
                          f"{tree} direction.md must name the seed action (add agent, persona mode)")
            self.assertIn("none fits", flat,
                          f"{tree} direction.md must gate the seed on NO fit persona existing")

    def test_direction_forbids_one_persona_per_task(self):
        # the anti-sprawl floor: the guide must say reuse-across-tasks, not seed-per-task
        for tree in SKILL_TREES:
            flat = _flat((tree / "phases" / "direction.md").read_text(encoding="utf-8"))
            self.assertIn("reuse", flat,
                          f"{tree} direction.md must say personas are reused across tasks (anti-sprawl)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
