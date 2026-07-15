#!/usr/bin/env python3
"""Red/green for status-brief-adoption (engine-minimalism, frozen §3 v1).

The SKILL orient step calls `add.py status --brief` (resume essentials) instead
of bare `status` (the 75-line dump re-read every session, 29.8% of engine_output),
with the "read PROJECT.md + SOUL.md" orient instruction carried by the skill PROSE.
Both SKILL trees (source + _bundled) must carry it. DOC-only — no engine edit.

Run: python3 -m unittest test_status_brief_orient -v
"""
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
SKILL_TREES = (
    REPO / "add-method" / "skill" / "add" / "SKILL.md",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "skill" / "add" / "SKILL.md",
)


def _orient_block(text: str) -> str:
    """The '## Always start here (orient …)' section up to the next H2."""
    marker = "## Always start here"
    i = text.index(marker)
    rest = text[i + len(marker):]
    j = rest.find("\n## ")
    return rest[:j] if j != -1 else rest


class StatusBriefOrientTest(unittest.TestCase):
    def test_orient_call_uses_brief_in_both_trees(self):
        for tree in SKILL_TREES:
            block = _orient_block(tree.read_text())
            self.assertIn("add.py status --brief", block,
                          f"orient block must call `status --brief` in {tree.name} ({tree.parent})")
            # the bare orient command must be gone from the orient block (a fenced `status\n`
            # with no flag) — allow only the --brief form.
            self.assertNotIn("add.py status\n", block,
                             f"the bare orient `status` must be replaced in {tree}")

    def test_orient_prose_still_names_both_files(self):
        # R1 orient_floor_lost guard: --brief does NOT name the files, so the PROSE must
        # point the agent at BOTH the foundation and the voice. The foundation is reached
        # either by its raw path (`PROJECT.md`) or via the scoped `status --foundation`
        # slice that serves it (foundation-slice) — both satisfy the floor.
        for tree in SKILL_TREES:
            block = _orient_block(tree.read_text())
            self.assertTrue("PROJECT.md" in block or "status --foundation" in block,
                            f"orient prose must point at the foundation in {tree}")
            self.assertIn("SOUL.md", block, f"orient prose must still name SOUL.md in {tree}")

    def test_both_skill_trees_byte_identical(self):
        texts = {t.read_text() for t in SKILL_TREES}
        self.assertEqual(len(texts), 1, "the two SKILL.md trees must stay byte-identical")


if __name__ == "__main__":
    unittest.main()
