#!/usr/bin/env python3
"""Behavioral proof of the Minimal pillar (task: minimalism-audit, milestone v2).

FINDING-A: the book claims "the Story is never auto-loaded" (01-principles.md; the
ETH-Zurich auto-context note in add.py). That claim was WRITTEN but UNPROVED —
`test_two_surface` only pins the prose string, so a regression that made a command
read a docs/ chapter would not turn any test red (it fails the circularity bar).

These tests pin the BEHAVIOR, not the words:
  - docs-absent : a project with no docs/ at all runs the whole lifecycle -> Story is
                  not REQUIRED at runtime.
  - read-spy    : no command's read_text resolves under a docs/ dir -> Story is not
                  READ at runtime. This is the non-vacuity guard: inject a docs/ read
                  into any command and this test goes red (verified during build, then
                  reverted).
  - coverage    : LIFECYCLE (+ init) covers EVERY subcommand the parser exposes, so
                  the read-spy's "no command" claim is universal, not a subset. A new
                  subcommand fails this until it is classified (exercised or excluded).

Assumption (worth knowing if a regression slips past): the spy patches only
Path.read_text. Every read site in add.py uses read_text today; a future read via
open(p).read() would evade the guard.
Run: python3 -m unittest test_min_pillar -v
"""
import argparse
import os
import pathlib
import tempfile
import unittest
from pathlib import Path

import add

# The FULL public surface: every subcommand `add.py` exposes, driven in one valid
# order, so the read-spy below observes EVERY command — not a convenient subset.
# (`guide` is included on purpose: it only PRINTS chapter pointers, it must not read
# them. `sync-guidelines` reads AGENTS.md/CLAUDE.md — State at the project root, never
# a docs/ chapter.) `init` is the one command not here: it runs in setUp, and the
# docs-absent assertion fires immediately after it. test_every_subcommand_is_covered
# proves this list (plus init) equals the parser's whole command set — so a NEW
# subcommand fails that test until it is classified here.
LIFECYCLE = [
    ["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"],
    ["new-task", "t", "--title", "Feature"],   # auto-linked to mvp
    ["status"],
    ["guide"],
    ["stage", "mvp"],
    ["set-milestone", "t", "none"], ["set-milestone", "t", "mvp"],
    ["use", "t"],                              # set active_task to an existing slug (read/writes state, not docs/)
    ["phase", "specify", "t"],
    ["advance", "t"], ["advance", "t"], ["advance", "t"],
    ["advance", "t"], ["advance", "t"],        # specify -> ... -> verify
    ["gate", "PASS", "t"],
    ["status"],
    ["check"],
    ["ready"],
    ["guide", "t"],
    ["report"], ["report", "mvp"],             # read-only dashboard (reads MILESTONE/TASK, not docs/)
    ["deltas"],                                # read-only: open competency deltas report
    ["project"],                               # read-only: prints PROJECT.md, reads no docs/ chapter
    ["sync-guidelines"],
    ["milestone-done", "mvp"],
    ["archive-milestone", "mvp"],              # mvp is done by now -> archivable
]

# init runs in setUp (it refuses to re-run on an existing project), so it is exercised
# under the docs-absent assertion rather than inside LIFECYCLE.
_EXERCISED_IN_SETUP = {"init"}


class MinimalPillarTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-min-pillar-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _docs_dirs(self):
        return list(Path(self.tmp).rglob("docs"))

    def test_full_lifecycle_runs_with_no_story(self):
        # init scaffolds no book; the Story is referenced by path, never installed.
        self.assertEqual(self._docs_dirs(), [], "init must not scaffold a docs/ Story")
        for argv in LIFECYCLE:
            try:
                add.main(argv)
            except SystemExit as e:
                if e.code:
                    self.fail(f"command {argv} failed (exit {e.code}) with no Story present")
        # the flow completing never created a Story either
        self.assertEqual(self._docs_dirs(), [], "no command may create a docs/ Story")

    def test_no_command_reads_a_docs_chapter(self):
        # Spy on every read_text during the whole lifecycle; assert none resolves
        # under a 'docs' directory. Goes red the moment a command auto-loads Story.
        orig = pathlib.Path.read_text
        reads: list[str] = []

        def spy(self, *a, **k):
            reads.append(str(self))
            return orig(self, *a, **k)

        pathlib.Path.read_text = spy
        try:
            for argv in LIFECYCLE:
                try:
                    add.main(argv)
                except SystemExit as e:
                    if e.code:
                        self.fail(f"command {argv} failed during read-spy (exit {e.code})")
        finally:
            pathlib.Path.read_text = orig

        story_reads = [p for p in reads if "docs" in Path(p).parts]
        self.assertEqual(story_reads, [],
                         f"a command auto-loaded the Story (read under docs/): {story_reads}")
        self.assertTrue(reads, "the spy must have observed reads (else it caught nothing)")

    def test_every_subcommand_is_covered(self):
        # Self-maintaining guard: the read-spy claim is "NO command reads a docs/
        # chapter", so the spy must run EVERY command. Derive the full command set
        # from the parser and assert LIFECYCLE (+ init in setUp) covers it exactly.
        # A new subcommand fails here until it is added to LIFECYCLE — closing the
        # gap where the claim is universal but the proof is a subset.
        parser = add.build_parser()
        sub = [a for a in parser._actions
               if isinstance(a, argparse._SubParsersAction)][0]
        all_cmds = set(sub.choices)
        covered = _EXERCISED_IN_SETUP | {argv[0] for argv in LIFECYCLE}
        self.assertEqual(
            all_cmds - covered, set(),
            f"subcommand(s) never run under the read-spy: {sorted(all_cmds - covered)}")
        self.assertEqual(
            covered - all_cmds, set(),
            f"LIFECYCLE names a command the parser does not expose: {sorted(covered - all_cmds)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
