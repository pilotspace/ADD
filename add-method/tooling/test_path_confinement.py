#!/usr/bin/env python3
"""Red/green tests for confining §4-declared test paths to the project root
(task declared-path-confinement, milestone v13-1 — contract v2 of the
declared-fallback seam).

Every file the declaration leads to must resolve (symlinks followed) INSIDE the
project root before any read; outside -> contributes 0, fail-closed, silently.
In-root v1 behavior is byte-for-byte unchanged. Asserts rendered report/--json
output, never function internals. Run:
    python3 -m unittest test_path_confinement -v
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

HERE = Path(__file__).resolve().parent          # add-method/tooling
REPO = HERE.parent.parent
BUNDLE = HERE.parent / "src" / "add_method" / "_bundled"

# the confinement clause stated where §4 authors read (prose accord, task 1's files)
CLAUSE = "outside the project root counts 0"


def _tests_src(n):
    return "\n".join(f"def test_case_{i}():\n    assert True\n" for i in range(n))


def _task_md_text(sec4):
    return "\n".join([
        "# TASK: t", "",
        "## 1 · SPECIFY", "Feature: f", "",
        "## 2 · SCENARIOS", "(none)", "",
        "## 3 · CONTRACT", "shape", "",
        "## 4 · TESTS", sec4, "",
        "## 5 · BUILD", "code", "",
        "## 6 · VERIFY", "  - [x] all tests pass", "",
        "## 7 · OBSERVE", "watch", "",
    ])


class PathConfinementTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-confine-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        # a REAL out-of-tree test file: sibling of the project root in the temp area
        self.evil = Path(tempfile.mkdtemp(prefix="add-evil-")).resolve()
        self.addCleanup(shutil.rmtree, self.evil, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        (self.evil / "t.py").write_text(_tests_src(3), encoding="utf-8")
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

    def _mk_task(self, slug, declare_line):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["new-task", slug, "--title", slug])
        (self._root() / "tasks" / slug / "TASK.md").write_text(
            _task_md_text(declare_line), encoding="utf-8")

    def _json_tests(self, slug):
        out, _, code = self._run("v13", "--json")
        self.assertEqual(code, 0)
        row = next(r for r in json.loads(out)["tasks"] if r["slug"] == slug)
        return row["tests"], row.get("tests_declared")

    # ---- scenarios: the three escape routes (red) ---------------------------
    def test_dotdot_traversal_zero(self):
        rel = f"../{self.evil.name}/t.py"          # token with "/" -> root-relative
        self._mk_task("alpha", f"Tests live in: `{rel}`")
        n, declared = self._json_tests("alpha")
        self.assertEqual(n, 0, "dot-dot traversal must not be counted")
        self.assertFalse(declared, "no † for a confined-away declaration")
        out, _, _ = self._run("v13")
        self.assertNotIn("†", out)

    def test_absolute_token_zero(self):
        self._mk_task("alpha", f"Tests live in: `{self.evil / 't.py'}`")
        n, _ = self._json_tests("alpha")
        self.assertEqual(n, 0, "absolute token must not escape (pathlib absolute-join)")

    def test_symlink_escape_zero(self):
        (self.tmp / "x").mkdir()
        os.symlink(self.evil / "t.py", self.tmp / "x" / "linked.py")
        # "/" token -> root-relative: the name is in-tree, the TARGET is not
        self._mk_task("alpha", "Tests live in: `x/linked.py`")
        n, _ = self._json_tests("alpha")
        self.assertEqual(n, 0, "an in-tree symlink to an out-of-tree file must count 0")

    # ---- guards: v1 behavior + purity (green-by-design) ---------------------
    def test_inroot_forms_unchanged(self):
        (self.tmp / "pkg").mkdir()
        (self.tmp / "pkg" / "t_root.py").write_text(_tests_src(2), encoding="utf-8")
        tdir = self._root() / "tasks"
        self._mk_task("alpha", "Tests live in: `./local/` and `pkg/t_root.py` and `more.py`")
        (tdir / "alpha" / "local").mkdir(parents=True)
        (tdir / "alpha" / "local" / "t_a.py").write_text(_tests_src(1), encoding="utf-8")
        (self.tmp / "pkg" / "more.py").write_text(_tests_src(4), encoding="utf-8")
        n, declared = self._json_tests("alpha")
        self.assertEqual(n, 1 + 2 + 4)             # ./dir + root-relative + bare sibling
        self.assertTrue(declared)

    def test_dotdot_inside_counts(self):
        (self.tmp / "tests").mkdir()
        (self.tmp / "tests" / "t.py").write_text(_tests_src(2), encoding="utf-8")
        self._mk_task("alpha", "Tests live in: `pkg/../tests/t.py`")
        (self.tmp / "pkg").mkdir(exist_ok=True)
        n, _ = self._json_tests("alpha")
        self.assertEqual(n, 2, "dot-dot RESOLVING inside the root still counts")

    def test_confinement_pure(self):
        rel = f"../{self.evil.name}/t.py"
        self._mk_task("alpha", f"Tests live in: `{rel}`")
        before_state, before_files = self._hash_state(), self._file_set()
        for argv in (("v13",), ("v13", "--json")):
            _, _, code = self._run(*argv)
            self.assertEqual(code, 0, f"exit != 0 for {argv}")
        self.assertEqual(self._hash_state(), before_state)
        self.assertEqual(self._file_set(), before_files)

    # ---- prose accord (anchors, red until build) ----------------------------
    def test_prose_clause_present(self):
        tmpl = (HERE / "templates" / "TASK.md.tmpl").read_text(encoding="utf-8")
        guide = (HERE.parent / "skill" / "add" / "phases" / "4-tests.md").read_text(
            encoding="utf-8")
        self.assertIn(CLAUSE, tmpl)
        self.assertIn(CLAUSE, guide)
        for canon, twins in (
            (HERE / "templates" / "TASK.md.tmpl",
             (REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
              BUNDLE / "tooling" / "templates" / "TASK.md.tmpl")),
            (HERE.parent / "skill" / "add" / "phases" / "4-tests.md",
             (REPO / ".claude" / "skills" / "add" / "phases" / "4-tests.md",
              BUNDLE / "skill" / "add" / "phases" / "4-tests.md")),
        ):
            for twin in twins:
                self.assertEqual(canon.read_bytes(), twin.read_bytes(),
                                 f"tree divergence: {twin}")


if __name__ == "__main__":
    unittest.main()
