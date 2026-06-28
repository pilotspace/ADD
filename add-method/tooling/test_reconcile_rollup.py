#!/usr/bin/env python3
"""Tests for reconcile-rollup (installer-polish · reconcile-rollup).

FROZEN @ v1: a reconcile REPORTS a file-level "N restored · M refreshed" roll-up.
  - _clean_replace(src, dest, *, strip_tests) returns {restored, refreshed}: snapshot dest's
    set of relative FILE paths BEFORE the wipe; after the copy(+strip), restored = a final
    file absent-before, refreshed = a final file present-before. Orphans (before\\after) are
    swept and counted as neither. Copy semantics are UNCHANGED (wipe + copytree).
  - _reconcile sums the per-tree counts across the 3 MANAGED trees, logs one
    "→ N restored · M refreshed" line, and returns {"restored", "refreshed", "trees"}.
  - update() folds the rollup into its headline. A partially-gutted PRESENT tree shows
    restored>0 even though the tree-level status calls it "refreshed".

Hermetic: a bundled fixture (skill/tooling/docs with known file counts) + tmp targets; the
npm twin is exercised by a node subprocess. RED until _clean_replace returns counts and
_reconcile returns/logs the rollup — red for the right reason (missing implementation).

Run: python3 -m unittest test_reconcile_rollup -v
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from add_method import _installer            # noqa: E402

CLI_JS = _ADD_METHOD / "bin" / "cli.js"


def _make_bundled(root: Path) -> Path:
    """A managed-layer fixture with KNOWN file counts: skill=1, tooling=3, docs=2 (total 6)."""
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    (root / "tooling" / "add_engine").mkdir()
    (root / "tooling" / "add_engine" / "__init__.py").write_text("# pkg\n")
    (root / "tooling" / "add_engine" / "core.py").write_text("# core\n")
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro\n")
    (root / "docs" / "01-flow.md").write_text("flow\n")
    return root


TOTAL_MANAGED = 6   # skill(1) + tooling(3) + docs(2)


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rollup-")).resolve()
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.userhome = self.tmp / "user"; self.userhome.mkdir()
        self.proj = self.tmp / "proj"; self.proj.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self):
        return {"HOME": str(self.userhome)}

    def _reconcile(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            roll = _installer._reconcile(self.proj, self.bundled)
        return roll, buf.getvalue()


# --- _clean_replace unit -----------------------------------------------------

class CleanReplaceUnitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rollup-cr-")).resolve()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_returns_restored_and_refreshed(self):                  # Must 1
        src = self.tmp / "src"; src.mkdir()
        for n in ("a.py", "b.py", "c.py", "d.py", "e.py"):
            (src / n).write_text(n)
        dest = self.tmp / "dest"; dest.mkdir()
        for n in ("a.py", "b.py", "c.py"):                          # 3 present, 2 (d,e) missing
            (dest / n).write_text(n)
        r = _installer._clean_replace(src, dest)
        self.assertEqual(r["restored"], 2, "two src files were absent in dest")
        self.assertEqual(r["refreshed"], 3, "three src files were present in dest")
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["a.py", "b.py", "c.py", "d.py", "e.py"],
                         "dest healed to the full src set")

    def test_orphan_swept_not_counted(self):                        # Must 1 (copy semantics unchanged)
        src = self.tmp / "src2"; src.mkdir()
        (src / "a.py").write_text("a"); (src / "b.py").write_text("b")
        dest = self.tmp / "dest2"; dest.mkdir()
        (dest / "b.py").write_text("b")                             # shared
        (dest / "orphan.py").write_text("x")                        # NOT in src
        r = _installer._clean_replace(src, dest)
        self.assertFalse((dest / "orphan.py").exists(), "orphan swept")
        self.assertEqual(r["restored"], 1, "a.py was absent")
        self.assertEqual(r["refreshed"], 1, "b.py was present")
        self.assertEqual(r["restored"] + r["refreshed"], 2, "counts cover only final-tree files, not the orphan")

    def test_stripped_test_files_not_counted(self):                 # Must 1 (count the FINAL tree)
        src = self.tmp / "src3"; src.mkdir()
        (src / "add.py").write_text("real")
        (src / "test_foo.py").write_text("a dev test")              # stripped when strip_tests=True
        dest = self.tmp / "dest3"; dest.mkdir()
        r = _installer._clean_replace(src, dest, strip_tests=True)
        self.assertFalse((dest / "test_foo.py").exists(), "test_*.py stripped from the final tree")
        self.assertEqual(r["restored"], 1, "only the surviving add.py is counted, not the stripped test")
        self.assertEqual(r["refreshed"], 0)

    def test_nested_files_counted_as_leaves(self):                  # Must 1 (files, not dirs)
        src = self.tmp / "src4"; src.mkdir()
        (src / "pkg").mkdir(); (src / "pkg" / "m.py").write_text("m"); (src / "top.py").write_text("t")
        dest = self.tmp / "dest4"
        r = _installer._clean_replace(src, dest)                    # dest absent -> all restored
        self.assertEqual(r["restored"], 2, "a nested file counts as a leaf, the dir does not")
        self.assertEqual(r["refreshed"], 0)


# --- _reconcile roll-up ------------------------------------------------------

class ReconcileRollupTest(_Base):
    def test_fresh_reconcile_all_restored(self):                    # Must 5
        roll, out = self._reconcile()
        self.assertEqual(roll["restored"], TOTAL_MANAGED, "a fresh target restores every managed file")
        self.assertEqual(roll["refreshed"], 0)
        self.assertIn(f"{TOTAL_MANAGED} restored", out, "the rollup line reports the restored count")

    def test_intact_reconcile_all_refreshed(self):                  # Must 5
        self._reconcile()                                           # materialize once
        roll, out = self._reconcile()                               # re-run on the intact tree
        self.assertEqual(roll["restored"], 0, "nothing missing the second time")
        self.assertEqual(roll["refreshed"], TOTAL_MANAGED, "every managed file is refreshed")
        self.assertIn("0 restored", out)

    def test_partial_gut_healed_and_counted(self):                  # Must 1 + Must 4
        self._reconcile()                                           # materialize
        engine = self.proj / ".add" / "tooling" / "add_engine"      # present tree, gut a subdir
        self.assertTrue(engine.exists())
        shutil.rmtree(engine)                                       # delete 2 files (__init__, core)
        roll, out = self._reconcile()
        self.assertEqual(roll["restored"], 2, "the 2 gutted files are counted as restored")
        self.assertEqual(roll["refreshed"], TOTAL_MANAGED - 2, "the rest are refreshed")
        self.assertTrue((engine / "core.py").exists(), "the gutted files are healed on disk")
        self.assertIn("2 restored", out, "a present-but-gutted tree shows restored>0 in the rollup")

    def test_reconcile_returns_rollup_shape(self):                  # Must 2
        roll, _ = self._reconcile()
        self.assertEqual(set(roll), {"restored", "refreshed", "trees"})
        self.assertIn("tooling", roll["trees"], "the tree-level pre-status is still returned")


# --- update() headline -------------------------------------------------------

class UpdateHeadlineTest(_Base):
    def _install(self):
        return _installer.install(target=str(self.proj), bundled=str(self.bundled),
                                  non_interactive=True, env=self._env())

    def test_headline_carries_rollup(self):                         # Must 3
        self.assertEqual(self._install(), 0)
        shutil.rmtree(self.proj / ".add" / "tooling" / "add_engine")   # gut a present tree
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                     version="9.9.9", force=True, env=self._env())
        out = buf.getvalue()
        self.assertEqual(code, 0)
        headline = [ln for ln in out.splitlines() if ln.startswith("ADD updated")]
        self.assertTrue(headline, "an 'ADD updated …' headline is printed")
        self.assertRegexpMatches(headline[-1], r"\(\d+ restored · \d+ refreshed\)") if hasattr(self, "assertRegexpMatches") \
            else self.assertRegex(headline[-1], r"\(\d+ restored · \d+ refreshed\)")


# --- npm / pip parity --------------------------------------------------------

class ParityRollupTest(_Base):
    def test_parity_surface(self):                                  # Must 6 (structural — call-sites)
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        self.assertIn("restored", py); self.assertIn("refreshed", py)
        self.assertIn("restored ·", py, "_installer.py must emit the '· restored · refreshed' rollup wording")
        self.assertIn("restored ·", js, "cli.js must emit the same rollup wording")
        self.assertIn("refreshed)", js, "cli.js headline must carry (… restored · … refreshed)")

    def test_pip_restored_equals_files_deleted(self):               # Must 6 (computation invariant — pip)
        # The twin-independent claim of the v2 INV: restored == count of files absent-before.
        # Gut a known subdir, reconcile, assert restored == files deleted.
        _installer.install(target=str(self.proj), bundled=str(self.bundled),
                           non_interactive=True, env=self._env())
        engine = self.proj / ".add" / "tooling" / "add_engine"
        deleted = len([p for p in engine.rglob("*") if p.is_file()])
        shutil.rmtree(engine)
        roll, _ = self._reconcile()
        self.assertEqual(roll["restored"], deleted, "pip restored == files deleted from the gutted subdir")

    def test_npm_restored_equals_files_deleted(self):               # Must 6 (computation invariant — npm)
        # SAME invariant via the node twin (its own bundle): restored == files deleted. Proves both
        # twins compute restored = absent-before identically, the parity the v2 INV actually claims.
        if not shutil.which("node"):
            self.skipTest("node not available")
        env = dict(os.environ); env.update(self._env())
        r0 = subprocess.run(["node", str(CLI_JS), "init", str(self.proj), "--yes"],
                            capture_output=True, text=True, env=env, cwd=str(self.bundled.parent))
        self.assertEqual(r0.returncode, 0, f"npm init failed: {r0.stderr}")
        engine = self.proj / ".add" / "tooling" / "add_engine"
        if not engine.exists():
            self.skipTest("node bundle has no add_engine subdir to gut")
        deleted = len([p for p in engine.rglob("*") if p.is_file()])
        shutil.rmtree(engine)
        r = subprocess.run(["node", str(CLI_JS), "update", str(self.proj), "--force"],
                           capture_output=True, text=True, env=env, cwd=str(self.bundled.parent))
        self.assertEqual(r.returncode, 0, f"npm update failed: {r.stderr}")
        import re as _re
        m = _re.search(r"→ (\d+) restored · (\d+) refreshed", r.stdout)
        self.assertTrue(m, f"cli.js prints the rollup line; got:\n{r.stdout}")
        self.assertEqual(int(m.group(1)), deleted, "npm restored == files deleted (same computation as pip)")
        self.assertRegex(r.stdout, r"reconciled \(\d+ restored · \d+ refreshed\)",
                         "cli.js headline carries the same parenthetical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
