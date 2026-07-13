#!/usr/bin/env python3
"""Red/green tests for the plan-aware DECIDE NEXT hint (task decide-planned-hint,
milestone v13-1).

When MILESTONE.md lists task rows with no TASK.md, every footer surface gains
" — n planned not yet scaffolded: a · b" and the rollup --json gains one additive
planned_unscaffolded list. Empty list -> byte-identical surfaces; the frozen
--decide --json nine-key set is untouched. Run:
    python3 -m unittest test_planned_hint -v
"""
import hashlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _meet_exit_criteria(ms: str) -> None:
    """v20 goal-gate: check the milestone's '## Exit criteria' box so milestone-done
    releases. Targets only the Exit-criteria section — never the Tasks rows."""
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")

HINT = "not yet scaffolded"
FROZEN_DECIDE_KEYS = {"seam", "milestone", "task", "phase", "gate",
                      "judgment", "facts", "unlocks", "decide", "plan"}


class PlannedHintTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-planned-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["init", "--name", "demo"])
            add.main(["new-milestone", "v13", "--title", "Decide", "--goal", "decide fast"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _hash_state(self) -> str:
        return hashlib.sha256((self._root() / "state.json").read_bytes()).hexdigest()

    def _file_set(self):
        return sorted(str(p) for p in self.tmp.rglob("*") if p.is_file())

    def _run(self, *args):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["report", *args])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _mk_task(self, slug):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["new-task", slug, "--title", slug])

    def _plan(self, *rows):
        """Write a Tasks section listing the given rows into MILESTONE.md."""
        md = self._root() / "milestones" / "v13" / "MILESTONE.md"
        body = md.read_text(encoding="utf-8")
        lines = "\n".join(rows)
        md.write_text(body + f"\n## Tasks (test fixture)\n{lines}\n", encoding="utf-8")

    # ---- scenarios: the hint (red) ------------------------------------------
    def test_hint_named_when_unscaffolded(self):
        self._mk_task("alpha")
        self._plan("- [ ] alpha   depends-on: none — exists",
                   "- [ ] beta    depends-on: none — planned only",
                   "- [x] gamma   depends-on: none — planned only")
        for argv in (("v13",), ("v13", "--decide")):
            out, _, code = self._run(*argv)
            self.assertEqual(code, 0)
            self.assertIn("2 planned " + HINT, out, f"hint missing in {argv}")
            self.assertIn("beta", out)
            self.assertIn("gamma", out)

    def test_fold_archive_still_suffixed(self):
        self._mk_task("alpha")
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["phase", "verify"])
            add.main(["gate", "PASS", "alpha"])
        self._plan("- [ ] alpha — done", "- [ ] beta — planned only")
        _meet_exit_criteria("v13")   # v20 goal-gate: criteria met so footer shows archive path
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertIn("archive-milestone", out)      # precedence unchanged
        self.assertIn("1 planned " + HINT, out)      # the v13 blind spot, closed

    def test_rollup_json_additive_key(self):
        self._mk_task("alpha")
        self._plan("- [ ] alpha — exists", "- [ ] beta — planned only")
        out, _, code = self._run("v13", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["planned_unscaffolded"], ["beta"])
        # guard: the decide payload's frozen nine keys are untouched
        out, _, code = self._run("v13", "--decide", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(set(json.loads(out).keys()), FROZEN_DECIDE_KEYS)

    # ---- guards (green-by-design) -------------------------------------------
    def test_byte_identical_when_none(self):
        self._mk_task("alpha")
        self._plan("- [ ] alpha — every planned row is scaffolded")
        for argv in (("v13",), ("v13", "--decide"), ("v13", "alpha")):
            out, _, code = self._run(*argv)
            self.assertEqual(code, 0)
            self.assertNotIn(HINT, out, f"phantom hint in {argv}")
        out, _, _ = self._run("v13", "--json")
        self.assertEqual(json.loads(out)["planned_unscaffolded"], [])

    def test_placeholder_ignored(self):
        self._mk_task("alpha")
        self._plan("- [ ] <slug>   depends-on: none     — <one line>")
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertNotIn(HINT, out)

    def test_missing_milestone_md_failclosed(self):
        self._mk_task("alpha")
        (self._root() / "milestones" / "v13" / "MILESTONE.md").unlink()
        for argv in (("v13",), ("v13", "--decide"), ("v13", "--json")):
            out, _, code = self._run(*argv)
            self.assertEqual(code, 0, f"exit != 0 for {argv}")
            self.assertNotIn(HINT, out)

    def test_hint_pure(self):
        self._mk_task("alpha")
        self._plan("- [ ] beta — planned only")
        before_state, before_files = self._hash_state(), self._file_set()
        for argv in (("v13",), ("v13", "--decide"), ("v13", "--json"),
                     ("v13", "--decide", "--json")):
            _, _, code = self._run(*argv)
            self.assertEqual(code, 0, f"exit != 0 for {argv}")
        self.assertEqual(self._hash_state(), before_state)
        self.assertEqual(self._file_set(), before_files)


if __name__ == "__main__":
    unittest.main()
