#!/usr/bin/env python3
"""Setup reminds the user to commit the .add/ folder to git (task: setup-commit-prompt).

`add.py init` is the setup bootstrap. It should close with a tip to commit the `.add/`
folder so a team shares the ADD state — its transient files are already .gitignored. The
reminder must appear for BOTH the greenfield and brownfield closing branches.

Run: python3 -m unittest test_setup_commit_prompt -v
"""
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add

_COMMIT_RE = re.compile(r"commit .*\.add", re.IGNORECASE)


class SetupCommitPrompt(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="commit-prompt-")
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _init_output(self) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["init", "--name", "demo", "--stage", "mvp"])
        return buf.getvalue()

    def test_greenfield_init_reminds_to_commit_add(self):
        out = self._init_output()
        self.assertRegex(out, _COMMIT_RE,
                         "greenfield init must remind the user to commit .add/ to git")

    def test_brownfield_init_reminds_to_commit_add(self):
        # a stray source file makes _is_brownfield trip -> the brownfield closing branch
        (Path(self.tmp) / "main.py").write_text("print('hi')\n", encoding="utf-8")
        out = self._init_output()
        self.assertRegex(out, _COMMIT_RE,
                         "brownfield init must also remind the user to commit .add/ to git")


if __name__ == "__main__":
    unittest.main(verbosity=2)
