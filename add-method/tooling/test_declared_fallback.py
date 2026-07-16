#!/usr/bin/env python3
"""Red/green tests for the TESTS-column declared-path fallback (task
tests-declared-fallback, milestone v13).

When `tasks/<slug>/tests/` yields 0 tests AND §4 carries a `Tests live in:` line,
the count falls back to the backticked declared path(s) — rendered `n†` with ONE
footnote line under the task table; `report --json` gains `tests_declared: bool`;
decide facts reuse the truthful count with their FROZEN key-set unchanged. Primary
count always wins when > 0. Every path stays PURE (v9). Asserts rendered bytes /
JSON values / exit codes — never internals. Run:
    python3 -m unittest test_declared_fallback -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

FOOTNOTE = "† counted at the §4-declared path"


def _task_md_text(sec4="plan"):
    """A minimal TASK.md with the seven numbered headings and a controlled §4."""
    return "\n".join([
        "# TASK: t", "",
        "## 1 · SPECIFY", "Feature: f", "",
        "## 2 · SCENARIOS", "(none)", "",
        "## 3 · PLAN", "shape", "",   # plan-phase-core: §3 is now PLAN (ground+contract collapsed into it)
        "## 4 · TESTS", sec4, "",
        "## 5 · BUILD", "code", "",
        "## 6 · VERIFY", "  - [x] all tests pass", "",
        "## 7 · OBSERVE", "watch", "",
    ])


def _tests_src(n):
    return "\n".join(f"def test_case_{i}():\n    assert True\n" for i in range(n))


class DeclaredFallbackTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-declared-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
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
        """Run `report` capturing stdout/stderr; return (out, err, code)."""
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["report", *args])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _mk_task(self, slug, sec4="plan", phase=None):
        add.main(["new-task", slug, "--title", slug])
        (self._root() / "tasks" / slug / "TASK.md").write_text(
            _task_md_text(sec4), encoding="utf-8")
        if phase:
            add.main(["phase", phase, slug])

    def _declare(self, relpath, n):
        """Drop a real test file with n tests at tmp/<relpath> (project root)."""
        p = self.tmp / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(_tests_src(n), encoding="utf-8")

    # ---- scenarios ---------------------------------------------------------
    def test_declared_fallback_footnote(self):
        self._declare("tooling/test_real.py", 3)
        self._mk_task("alpha", sec4="Tests live in: `tooling/test_real.py` · red first.")
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"alpha\s+direction\s+—\s+3†\s")
        self.assertEqual(out.count(FOOTNOTE), 1)
        jout, _, jcode = self._run("v13", "--json")
        self.assertEqual(jcode, 0)
        row = json.loads(jout)["tasks"][0]
        self.assertEqual(row["tests"], 3)
        self.assertIs(row["tests_declared"], True)

    def test_primary_wins(self):
        self._declare("tooling/test_other.py", 5)
        self._mk_task("alpha", sec4="Tests live in: `tooling/test_other.py`.")
        d = self._root() / "tasks" / "alpha" / "tests"
        (d / "test_local.py").write_text(_tests_src(2), encoding="utf-8")
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"alpha\s+direction\s+—\s+2\s")
        self.assertNotIn("†", out)
        jout, _, _ = self._run("v13", "--json")
        row = json.loads(jout)["tasks"][0]
        self.assertEqual(row["tests"], 2)
        self.assertIs(row["tests_declared"], False)

    def test_bare_zero_no_footnote(self):
        self._mk_task("alpha", sec4="plan only — no declaration line here.")
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"alpha\s+direction\s+—\s+0\s")
        self.assertNotIn("†", out)

    def test_missing_declared_failclosed(self):
        self._mk_task("alpha", sec4="Tests live in: `tooling/does_not_exist.py`.")
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"alpha\s+direction\s+—\s+0\s")
        self.assertNotIn("†", out)

    def test_sibling_shorthand_sums(self):
        self._declare("tooling/test_a.py", 2)
        self._declare("tooling/test_b.py", 3)
        # bare `test_b.py` resolves beside the previous token; dup `test_a.py` deduped
        self._mk_task("alpha", sec4="Tests live in: `tooling/test_a.py` + `test_b.py` "
                                    "+ `tooling/test_a.py`.")
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"alpha\s+direction\s+—\s+5†\s")

    def test_directory_token(self):
        # "./" form resolves against the TASK dir; a dir token counts its *.py files
        self._mk_task("alpha", sec4="Tests live in: `./extra/` · red first.")
        d = self._root() / "tasks" / "alpha" / "extra"
        d.mkdir(parents=True)
        (d / "test_one.py").write_text(_tests_src(2), encoding="utf-8")
        (d / "test_two.py").write_text(_tests_src(2), encoding="utf-8")
        (d / "helper.txt").write_text("def test_not_python(): ...", encoding="utf-8")
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"alpha\s+direction\s+—\s+4†\s")

    def test_decide_facts_truthful_frozen(self):
        self._declare("tooling/test_real.py", 3)
        self._mk_task("alpha", sec4="Tests live in: `tooling/test_real.py`.",
                      phase="verify")
        jout, _, code = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(code, 0)
        d = json.loads(jout)
        self.assertEqual(d["facts"]["tests"], 3)
        self.assertEqual(set(d["facts"].keys()), {"phase", "gate", "deps", "tests"})

    def test_purity_all_paths(self):
        self._declare("tooling/test_real.py", 3)
        self._mk_task("alpha", sec4="Tests live in: `tooling/test_real.py`.",
                      phase="verify")
        before_state, before_files = self._hash_state(), self._file_set()
        for argv in (("v13",), ("v13", "--json"),
                     ("v13", "alpha", "--decide"),
                     ("v13", "alpha", "--decide", "--json")):
            _, _, code = self._run(*argv)
            self.assertEqual(code, 0, f"exit != 0 for {argv}")
        self.assertEqual(self._hash_state(), before_state)
        self.assertEqual(self._file_set(), before_files)


if __name__ == "__main__":
    unittest.main()
