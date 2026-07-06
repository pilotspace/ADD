"""worktree-prep (method-ergonomics): mechanize streams.md's manual worktree recipe.

CONTRACT:
  `add.py worktree-prep <slug> [--dir <path>]` cuts a git worktree at HEAD for a spawned
  worker, materializes the gitignored engine content a tracked-only checkout lacks
  (.add/tooling · .add/docs), and echoes the fork base for the WAVE.md ledger.
  Refusals fire before any filesystem write: worktree_prep_no_git · worktree_prep_exists ·
  unknown task. A dirty tree WARNS (streams.md: cut AFTER the bundle commit) but proceeds.
  state.json is never written (prep is workspace-only, not a state transition).
Run: python3 -m unittest test_worktree_prep -v
"""
import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import add


def _git(cwd, *argv):
    return subprocess.run(["git", "-C", str(cwd), *argv],
                          capture_output=True, text=True, timeout=60)


class WorktreePrepTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-wtp-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        os.chdir(self.proj)
        self._run("init", "--name", "demo", "--stage", "mvp")
        self._run("lock", "--force")
        self._run("new-task", "alpha", "--title", "A")
        # gitignored engine content the worktree must re-materialize
        (self.proj / ".add" / "tooling").mkdir(exist_ok=True)
        (self.proj / ".add" / "tooling" / "add.py").write_text("# engine\n", encoding="utf-8")
        (self.proj / ".add" / "docs").mkdir(exist_ok=True)
        (self.proj / ".add" / "docs" / "book.md").write_text("# book\n", encoding="utf-8")
        (self.proj / ".add" / ".gitignore").write_text("tooling/\ndocs/\n", encoding="utf-8")
        _git(self.proj, "init", "-q")
        _git(self.proj, "config", "user.email", "t@t")
        _git(self.proj, "config", "user.name", "T")
        _git(self.proj, "add", "-A")
        _git(self.proj, "commit", "-qm", "bundle")

    def _run(self, *argv, expect_die=False):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code or 0
        if expect_die:
            self.assertNotEqual(code, 0, f"{argv} unexpectedly succeeded: {buf.getvalue()}")
        else:
            self.assertEqual(code, 0, f"{argv} exited {code}: {err.getvalue()}")
        return buf.getvalue() + err.getvalue()

    def test_happy_path_materializes_and_echoes_base(self):    # scenarios 1–3
        out = self._run("worktree-prep", "alpha")
        dest = self.tmp / "proj-wt-alpha"
        self.assertTrue(dest.is_dir(), "worktree dir must exist")
        head = _git(self.proj, "rev-parse", "--short", "HEAD").stdout.strip()
        self.assertIn(f"fork base: {head}", out)
        self.assertTrue((dest / ".add" / "tooling" / "add.py").exists(),
                        "gitignored .add/tooling must be materialized")
        self.assertTrue((dest / ".add" / "docs" / "book.md").exists(),
                        "gitignored .add/docs must be materialized")
        wt_head = _git(dest, "rev-parse", "--short", "HEAD").stdout.strip()
        self.assertEqual(wt_head, head, "worktree must be cut from HEAD")

    def test_dir_override(self):                               # scenario 4
        dest = self.tmp / "elsewhere"
        self._run("worktree-prep", "alpha", "--dir", str(dest))
        self.assertTrue(dest.is_dir())

    def test_refuses_existing_dest(self):                      # R1
        (self.tmp / "proj-wt-alpha").mkdir()
        out = self._run("worktree-prep", "alpha", expect_die=True)
        self.assertIn("worktree_prep_exists", out)

    def test_refuses_without_git(self):                        # R2
        shutil.rmtree(self.proj / ".git")
        out = self._run("worktree-prep", "alpha", expect_die=True)
        self.assertIn("worktree_prep_no_git", out)

    def test_unknown_task_refused(self):                       # R3
        out = self._run("worktree-prep", "nowhere", expect_die=True)
        self.assertIn("unknown task", out)

    def test_dirty_tree_warns_but_proceeds(self):              # scenario 5
        (self.proj / "loose.txt").write_text("x", encoding="utf-8")
        out = self._run("worktree-prep", "alpha")
        self.assertIn("worktree_prep_dirty_tree", out)
        self.assertTrue((self.tmp / "proj-wt-alpha").is_dir())

    def test_state_never_written(self):                        # scenario 6
        sj = self.proj / ".add" / "state.json"
        before = sj.read_bytes()
        self._run("worktree-prep", "alpha")
        self.assertEqual(before, sj.read_bytes(), "prep must not touch state.json")


if __name__ == "__main__":
    unittest.main()
