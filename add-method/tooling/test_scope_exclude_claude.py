#!/usr/bin/env python3
"""Red/green test for pruning `.claude` from the scope walk (task scope-exclude-claude).

CONTRACT (frozen @ v1):
  _SCOPE_EXCLUDE_DIRS includes ".claude" → _scope_walk(root) prunes it at any depth
  (like .git/.add/.serena), so the returned {relpath: md5} map never contains a key
  under ".claude/". Consequently a Claude Code worktree file (.claude/worktrees/<wt>/<f>)
  is never counted as a scope touch, so _scope_findings never reports it out-of-scope.

Render-blind: asserts on the returned path map, not on the constant's internals.
Run: python3 -m unittest test_scope_exclude_claude -v
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add


class ScopeWalkPrunesClaudeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-scope-claude-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_scope_walk_prunes_claude(self):
        # a Claude Code worktree checkout living under .claude/ (gitignored, never task source)
        wt = self.tmp / ".claude" / "worktrees" / "wt"
        wt.mkdir(parents=True)
        (wt / "x.txt").write_text("a worktree file that is not this task's scope", encoding="utf-8")
        # a real project file at the root — proves the walk actually runs over this tree
        (self.tmp / "src.py").write_text("x = 1\n", encoding="utf-8")

        walked = add._scope_walk(self.tmp)

        self.assertIn("src.py", walked, "the walk must cover ordinary project files")
        offenders = [k for k in walked if k == ".claude" or k.startswith(".claude" + os.sep)
                     or k.startswith(".claude/")]
        self.assertEqual(offenders, [], f".claude must be pruned from the scope walk; walked: {offenders}")


if __name__ == "__main__":
    unittest.main()
