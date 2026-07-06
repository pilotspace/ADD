#!/usr/bin/env python3
"""Worktree-isolation-default wording guard (worktree-isolated-spawn-default).

streams.md's 3 mention sites (wave-spawn, Isolation bullet, spawn-adapter intro) and
docs/10-setup-and-stages.md's hard-boundary sentence must each state worktree isolation
as the DEFAULT for any agent-spawned step (single sequential OR parallel wave), not
merely an example tied to an explicitly-parallel wave — closing the gap named in the
phase-search-wiring spec-delta.

Reads the CANONICAL tree (add-method/skill/, add-method/docs/); 3-tree parity is
guarded elsewhere (test_tree_parity.py / test_bundle_parity.py).
Run: python3 -m unittest test_worktree_default_wording -v
"""
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skill" / "add"
DOCS = Path(__file__).resolve().parent.parent / "docs"


class WorktreeDefaultWordingTest(unittest.TestCase):
    def test_streams_md_states_worktree_default(self):
        t = (SKILL / "streams.md").read_text(encoding="utf-8")
        wave_para = re.search(r"Wave = a fan-out batch.*?next wave is unblocked\.", t, re.S).group(0)
        self.assertIn("default for any spawn", wave_para,
                      "the wave-spawn mention must state worktree isolation is the default, "
                      "not merely an example tied to a wave")

        isolation_para = re.search(r"\*\*Isolation\*\*:.*?last-good phase\.", t, re.S).group(0)
        self.assertIn("default for any agent-spawned step", isolation_para)
        self.assertIn("stated reason", isolation_para,
                      "a shared-tree opt-out must require a stated reason, not be presented "
                      "as an equal alternative")

        adapter_para = re.search(r"ADD needs six capabilities.*?native sandbox\.", t, re.S).group(0)
        self.assertIn("default for any spawn", adapter_para)

    def test_setup_stages_states_worktree_default(self):
        t = (DOCS / "10-setup-and-stages.md").read_text(encoding="utf-8")
        boundary_para = re.search(r"\*\*The hard boundary\.\*\*.*?never auto-passes that step\.",
                                   t, re.S).group(0)
        self.assertIn("default for any agent-spawned step", boundary_para,
                      "10-setup-and-stages.md's hard-boundary sentence must state worktree "
                      "isolation as the default, consistent with streams.md's wording")

    def test_no_reference_to_user_global_config(self):
        # R1: the new wording must scope itself to ADD's own shipped guidance, never mention
        # or attempt to override a user-specific config file outside this repo.
        streams = (SKILL / "streams.md").read_text(encoding="utf-8")
        stages = (DOCS / "10-setup-and-stages.md").read_text(encoding="utf-8")
        for t in (streams, stages):
            self.assertNotIn("CLAUDE.md", t)
            self.assertNotIn("global", t.lower().replace("globally", ""))


if __name__ == "__main__":
    unittest.main()
