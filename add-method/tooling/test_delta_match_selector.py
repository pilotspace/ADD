#!/usr/bin/env python3
"""Red/green tests for delta-match-selector (delta-resolution-polish 2/3): a `--match <substr>`
selector on `new-task --from-delta` and `drop-delta` targets ONE open SPEC delta among several.
CONTRACT frozen @ v1. --match absent → byte-identical first-open behavior. Run:
  python3 -m unittest test_delta_match_selector -v
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    try:
        with redirect_stdout(out), redirect_stderr(err):
            add.main(list(argv))
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    return code, out.getvalue(), err.getvalue()


class _Project(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-dms-")).resolve()
        os.chdir(self.tmp)
        _run(["init", "--name", "demo"])
        self.root = self.tmp / ".add"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _task_md(self, slug):
        return (self.root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")

    def _mk(self, slug):
        _run(["new-task", slug, "--title", "Feature"])

    def _set_spec(self, slug, *open_texts):
        """Plant one open SPEC delta per text in slug's §7 OBSERVE."""
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        idx = s.index("## 7 · OBSERVE")
        head_end = s.index("\n", idx) + 1
        lines = "".join(f"- [SPEC · open] {t} (evidence: ev)\n" for t in open_texts)
        body = f"\n### Spec delta\n{lines}\n### Competency deltas\n"
        p.write_text(s[:head_end] + body, encoding="utf-8")
class SeedMatchTest(_Project):
    def test_seed_match_targets_and_prefills(self):
        self._mk("prior"); self._set_spec("prior", "rate limit", "retry budget")
        code, out, err = _run(["new-task", "follow", "--from-delta", "prior", "--match", "retry budget"])
        self.assertEqual(code, 0, err)
        prior = self._task_md("prior")
        self.assertIn("[SPEC · seeded] retry budget (evidence: ev) [→ follow]", prior)
        self.assertIn("[SPEC · open] rate limit", prior)
        self.assertIn("retry budget", self._task_md("follow"))   # §1 Feature pre-filled from the matched delta

    def test_match_requires_from_delta(self):
        code, out, err = _run(["new-task", "foo", "--match", "bar"])   # no --from-delta
        self.assertNotEqual(code, 0)
        self.assertIn("match_requires_from_delta", out + err)
        self.assertFalse((self.root / "tasks" / "foo").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
