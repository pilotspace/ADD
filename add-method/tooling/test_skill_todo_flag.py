#!/usr/bin/env python3
"""Guard: SKILL.md documents the `--todo` fast-path (task: skill-todo-flag).

The `/add --todo` flag is an INSTRUCTION to the orchestrator (the AI), not engine code — so the
only thing the engine can test is that the instruction is WRITTEN and complete. This is a
presence/format fence, not a behavioural one: it proves the doc names the full mirror of the
engine's `cmd_todo` (capture · list · close) and that `argument-hint` advertises the flag. It
CANNOT prove the orchestrator obeys at runtime (the honest blind spot disclosed in §1 Assumptions,
same class as the security-escalation disclosure).

Anchored on the disclosure-unique marker `` `--todo` fast-path `` (not a bare common word, which a
keyword-only assert would vacuously satisfy — lesson from security-escalation-disclosure). Reads the
CANONICAL tree only; 3-tree parity is guarded by test_tree_parity + test_bundle_parity.

Run: python3 -m unittest test_skill_todo_flag -v
"""
import re
import unittest
from pathlib import Path

_CANON = Path(__file__).resolve().parent.parent / "skill" / "add"
_SKILL = _CANON / "SKILL.md"


class SkillTodoFlagTest(unittest.TestCase):
    def setUp(self):
        self.skill = _SKILL.read_text()

    def test_fastpath_block_present(self):
        """The fast-path is documented under a disclosure-unique marker."""
        self.assertIn(
            "`--todo` fast-path", self.skill,
            "SKILL.md must document the `--todo` fast-path block (orchestrator routes to the engine).",
        )

    def test_full_mirror_three_subforms(self):
        """All three sub-forms of cmd_todo are named: capture · list · close."""
        for token, what in [
            ("--todo <text>", "capture form"),
            ("lists open todos", "list form (bare --todo)"),
            ("--todo --done <id>", "close form"),
        ]:
            self.assertIn(token, self.skill, f"--todo fast-path is missing the {what} ('{token}').")

    def test_routes_to_engine(self):
        """The fast-path routes to the engine command, it does not reimplement it."""
        self.assertIn(
            "add.py todo", self.skill,
            "the --todo fast-path must route to `add.py todo …` (cmd_todo), not swallow it.",
        )

    def test_argument_hint_advertises_todo(self):
        """The frontmatter argument-hint names --todo so the flag is discoverable."""
        m = re.search(r"^argument-hint:.*$", self.skill, re.MULTILINE)
        self.assertIsNotNone(m, "argument-hint frontmatter line is missing.")
        self.assertIn("--todo", m.group(0), "argument-hint must name --todo (discoverable cue).")


if __name__ == "__main__":
    unittest.main(verbosity=2)
