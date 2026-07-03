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

project-scope-atomic-reconcile (TASK.md v1) extends this file with a crash-safe stage-then-
swap redesign of _clean_replace/cleanReplaceTree: StageCommitUnitTest (§2 scenarios 1-9, 11 —
missing/present dest, strip-on-staged, mid-copy + commit-land failure rollback, stale
tmp/backup self-heal), CrossTwinStagedCommitTest (§2 scenario 10 — python+node parity),
ConcurrencyDisclosureTest (§2 scenario 12 — the disclosed no-cross-writer-guarantee). A
scratch sibling of dest is named "<dest.name>.add-tmp-<token>" (staging) or
"<dest.name>.add-bak-<token>" (backup), in dest's own parent.

Run: python3 -m unittest test_reconcile_rollup -v
"""
import concurrent.futures
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


# --- project-scope-atomic-reconcile: crash-safe stage-then-swap (TASK.md v1) ------------

def _partial_copytree_then_raise(n_files):
    """A shutil.copytree replacement that really copies the first n_files (sorted,
    deterministic) leaf files from src into dst — dst is expected to already exist as an
    empty dir, matching how the real staging call is made — then raises, simulating a real
    crash/disk-full/permission-denied partway through a directory copy (TASK.md §1 Issue #1)."""
    def _fn(src, dst, *a, **kw):
        srcp, dstp = Path(src), Path(dst)
        dstp.mkdir(parents=True, exist_ok=True)
        files = sorted((p for p in srcp.rglob("*") if p.is_file()), key=str)
        for f in files[:n_files]:
            target = dstp / f.relative_to(srcp)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(f.read_bytes())
        raise OSError("injected mid-copy failure (test seam)")
    return _fn


class StageCommitUnitTest(unittest.TestCase):
    """_clean_replace: TASK.md §2 scenarios 1-9, 11. Each dest lives in its OWN dedicated
    `area` dir (never a sibling of src) so `_siblings_of` only ever reveals a GENUINE scratch
    sibling (staging/backup), never an unrelated fixture. scn1/2/9/11 restate the pre-existing
    happy-path contract (M8: unchanged) and are expected GREEN even pre-build — the
    crash-safety scenarios (3-8, 8b) are the ones that are RED pre-build (mirrors this
    project's own "a mix of red + already-green preservation tests is honest red" convention,
    CONVENTIONS.md fv49/pages-deploy)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rollup-stage-")).resolve()
        self.area = self.tmp / "area"
        self.area.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def _siblings_of(dest: Path) -> set:
        if not dest.parent.exists():
            return set()
        return {p.name for p in dest.parent.iterdir() if p.name != dest.name}

    # --- scenario 1: a missing dest is fully materialized -------------------

    def test_scn1_missing_dest_materialized_no_scratch_survives(self):   # M1, M3, M4, M8
        src = self.tmp / "src1"; src.mkdir()
        (src / "a.py").write_text("A"); (src / "b.py").write_text("B")
        (src / "pkg").mkdir(); (src / "pkg" / "m.py").write_text("M")
        dest = self.area / "dest"                    # absent; area exists, dest does not
        r = _installer._clean_replace(src, dest)
        self.assertEqual((dest / "a.py").read_text(), "A")
        self.assertEqual((dest / "b.py").read_text(), "B")
        self.assertEqual((dest / "pkg" / "m.py").read_text(), "M")
        self.assertEqual(r, {"restored": 3, "refreshed": 0})
        self.assertEqual(self._siblings_of(dest), set(), "no staging/backup scratch sibling survives")

    # --- scenario 2: a present dest is refreshed, never half-mixed ----------

    def test_scn2_present_dest_refreshed_never_half_mixed(self):         # M1, M3, M4, M8
        src = self.tmp / "src2"; src.mkdir()
        (src / "kept.py").write_text("KEPT-NEW")      # same name, new content
        (src / "added.py").write_text("ADDED")        # new file
        dest = self.area / "dest"; dest.mkdir()
        (dest / "kept.py").write_text("KEPT-OLD")
        (dest / "removed.py").write_text("REMOVED-UPSTREAM")   # orphan: not in src
        r = _installer._clean_replace(src, dest)
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["added.py", "kept.py"])
        self.assertEqual((dest / "kept.py").read_text(), "KEPT-NEW", "the new generation landed whole")
        self.assertFalse((dest / "removed.py").exists(), "an upstream-removed file is swept, not left")
        self.assertEqual(r, {"restored": 1, "refreshed": 1})
        self.assertEqual(self._siblings_of(dest), set())

    # --- scenario 3: strip_tests applied to the STAGED copy -----------------

    def test_scn3_strip_tests_applied_before_commit_not_after(self):     # M2
        src = self.tmp / "src3"; src.mkdir()
        (src / "add.py").write_text("real")
        (src / "test_foo.py").write_text("dev test")
        (src / "__pycache__").mkdir()
        (src / "__pycache__" / "x.pyc").write_text("bytecode")
        dest = self.area / "dest"                    # absent
        captured = {}
        real_copytree = _installer.shutil.copytree

        def _spy(s, d, *a, **kw):
            result = real_copytree(s, d, *a, **kw)
            # shutil.copytree's own _copytree helper recurses into subdirectories (here:
            # __pycache__) via this SAME public, patched symbol -- so only the OUTERMOST
            # call (source == the real src argument) is the one event under test; a nested
            # recursive call's `d` is a subdirectory of the staged dir, not the staged dir
            # itself, and must not be asserted against.
            if Path(s) == src:
                # immediately after the raw copy (before strip runs), the STAGED dir must
                # still hold the unstripped files -- proving strip happens AFTER copy, on
                # the staged dir
                self.assertTrue((Path(d) / "test_foo.py").exists(), "copy landed test_foo.py pre-strip")
                self.assertTrue((Path(d) / "__pycache__").exists(), "copy landed __pycache__ pre-strip")
                captured["staged"] = Path(d)
            return result

        with mock.patch.object(_installer.shutil, "copytree", side_effect=_spy):
            r = _installer._clean_replace(src, dest, strip_tests=True)
        self.assertNotEqual(captured["staged"], dest, "copy wrote into a staging sibling, not dest directly")
        self.assertFalse(captured["staged"].exists(),
                         "the staging path itself is gone (consumed by becoming dest via rename)")
        self.assertFalse((dest / "test_foo.py").exists(), "dest never shows the stripped test file")
        self.assertFalse((dest / "__pycache__").exists(), "dest never shows the stripped pycache")
        self.assertEqual(r, {"restored": 1, "refreshed": 0},
                         "only add.py is counted -- stripped files never appear in after")

    # --- scenario 4/5: a mid-copy failure leaves dest untouched -------------

    def test_scn4_mid_copy_failure_present_dest_byte_for_byte_untouched(self):
        # M5, Reject: stage_failure_dest_present_untouched
        src = self.tmp / "src4"; src.mkdir()
        for n in ("a.py", "b.py", "c.py"):
            (src / n).write_text("NEW-" + n)
        dest = self.area / "dest"; dest.mkdir()
        (dest / "old.py").write_text("OLD-CONTENT")
        before = {p.name: p.read_bytes() for p in dest.iterdir()}
        with mock.patch.object(_installer.shutil, "copytree",
                               side_effect=_partial_copytree_then_raise(1)):
            with self.assertRaises(OSError):
                _installer._clean_replace(src, dest)
        after = {p.name: p.read_bytes() for p in dest.iterdir()}
        self.assertEqual(after, before, "a present dest is byte-for-byte untouched by a mid-copy failure")
        self.assertEqual(self._siblings_of(dest), set(), "the partial staging dir is removed, not left")

    def test_scn5_mid_copy_failure_absent_dest_stays_absent(self):
        # M5, Reject: stage_failure_dest_absent_untouched
        src = self.tmp / "src5"; src.mkdir()
        for n in ("a.py", "b.py"):
            (src / n).write_text(n)
        dest = self.area / "dest"                    # never created
        with mock.patch.object(_installer.shutil, "copytree",
                               side_effect=_partial_copytree_then_raise(1)):
            with self.assertRaises(OSError):
                _installer._clean_replace(src, dest)
        self.assertFalse(dest.exists(), "dest stays absent -- no partial tree ever materialized at its path")
        self.assertEqual(self._siblings_of(dest), set(), "no partial staging directory survives")

    # --- scenario 6: a commit-land failure after the aside-rename rolls back -

    def test_scn6_commit_land_failure_after_aside_rolls_back(self):
        # M6, Reject: commit_land_failure_rolls_back
        src = self.tmp / "src6"; src.mkdir()
        (src / "new.py").write_text("NEW")
        dest = self.area / "dest"; dest.mkdir()
        (dest / "old.py").write_text("ORIGINAL")
        before = {p.name: p.read_bytes() for p in dest.iterdir()}
        real_rename = os.rename
        failed_once = {"done": False}

        def _fail_landing_rename(src_p, dst_p, *a, **kw):
            # the FIRST rename targeting dest is the SECOND commit rename (staged -> dest);
            # let the aside (dest -> bak) succeed for real, fail only that one landing
            # attempt, then let the code's OWN rollback rename (bak -> dest, which also
            # targets dest) succeed for real too -- a blanket intercept on every future
            # rename to dest would make rollback impossible by construction, which is not
            # the scenario under test (one transient landing failure, not a permanently
            # blocked target).
            if str(dst_p) == str(dest) and not failed_once["done"]:
                failed_once["done"] = True
                raise OSError("injected commit-land failure")
            return real_rename(src_p, dst_p, *a, **kw)

        with mock.patch.object(_installer.os, "rename", side_effect=_fail_landing_rename):
            with self.assertRaises(OSError):
                _installer._clean_replace(src, dest)
        after = {p.name: p.read_bytes() for p in dest.iterdir()}
        self.assertEqual(after, before, "dest is restored to its exact original content (the backup renamed back)")
        self.assertEqual(self._siblings_of(dest), set(), "no staging or backup scratch sibling survives")

    # --- scenario 7: a stale STAGING leftover is swept before new work ------

    def test_scn7_stale_staging_leftover_swept_before_new_stage(self):
        # M7, Reject: stale_stage_swept_next_call
        src = self.tmp / "src7"; src.mkdir()
        (src / "fresh.py").write_text("FRESH")
        dest = self.area / "dest"; dest.mkdir()
        (dest / "current.py").write_text("CURRENT")
        stale = self.area / f"{dest.name}.add-tmp-deadbeef"
        stale.mkdir()
        (stale / "partial.py").write_text("leftover from a crashed prior call")
        r = _installer._clean_replace(src, dest)
        self.assertFalse(stale.exists(), "the stale staging leftover is gone, never merged in")
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["fresh.py"],
                         "dest ends up holding exactly src's fresh content, same as a normal call")
        # fresh.py's relative path was ABSENT from dest before this call (current.py, not
        # fresh.py, was there) -- same counting convention as the pre-existing, unchanged
        # test_orphan_swept_not_counted: a swapped-in new filename is `restored`, not
        # `refreshed`; only a REPEATED filename counts as refreshed.
        self.assertEqual(r, {"restored": 1, "refreshed": 0})
        self.assertEqual(self._siblings_of(dest), set())

    # --- scenario 8: a stale BACKUP leftover self-heals an absent dest ------

    def test_scn8_stale_backup_self_heals_absent_dest(self):
        # M7, Reject: stale_backup_self_heals_next_call
        src = self.tmp / "src8"; src.mkdir()
        (src / "fresh.py").write_text("FRESH")
        dest = self.area / "dest"                     # ABSENT
        stale_bak = self.area / f"{dest.name}.add-bak-deadbeef"
        stale_bak.mkdir()
        (stale_bak / "known_good.py").write_text("last known good (pre-crash)")
        r = _installer._clean_replace(src, dest)
        self.assertFalse(stale_bak.exists(), "no backup scratch sibling survives")
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["fresh.py"],
                         "dest ends up on src's fresh content, same as the normal-success scenario")
        self.assertFalse((dest / "known_good.py").exists(),
                         "the backup's stale content does not linger as the final state")
        self.assertEqual(r, {"restored": 1, "refreshed": 0})

    def test_scn8b_stale_backup_restore_confirmed_not_mere_sweep(self):
        # bonus: reinforces M7/A2's RESTORE semantics (not a mere sweep), a stricter proof
        # than scn8 alone. If self-heal only SWEPT the stale backup, a subsequent STAGE
        # failure would leave dest absent. Because self-heal RESTORES first (A2), the SAME
        # stage failure instead leaves dest holding the restored backup content -- proving
        # the mechanism is restore-then-update, not sweep-then-fresh-stage.
        src = self.tmp / "src8b"; src.mkdir()
        (src / "fresh.py").write_text("FRESH")
        dest = self.area / "dest"                     # ABSENT
        stale_bak = self.area / f"{dest.name}.add-bak-deadbeef"
        stale_bak.mkdir()
        (stale_bak / "known_good.py").write_text("last known good (pre-crash)")
        with mock.patch.object(_installer.shutil, "copytree",
                               side_effect=_partial_copytree_then_raise(0)):
            with self.assertRaises(OSError):
                _installer._clean_replace(src, dest)
        self.assertTrue((dest / "known_good.py").exists(),
                        "self-heal already restored dest from the stale backup before staging began")
        self.assertEqual((dest / "known_good.py").read_text(), "last known good (pre-crash)")

    # --- scenario 9: return contract + orphan-sweep counts unchanged --------

    def test_scn9_return_contract_and_orphan_sweep_unchanged(self):      # M8
        src = self.tmp / "src9"; src.mkdir()
        for n in ("m1.py", "m2.py", "m3.py", "m4.py", "m5.py"):
            (src / n).write_text(n)
        dest = self.area / "dest"; dest.mkdir()
        for n in ("m1.py", "m2.py", "m3.py"):         # 3 already present -> refreshed
            (dest / n).write_text("OLD-" + n)
        (dest / "orphan.py").write_text("not in src at all")
        r = _installer._clean_replace(src, dest)
        self.assertEqual(r["restored"], 2, "m4.py + m5.py were absent before")
        self.assertEqual(r["refreshed"], 3, "m1..m3 were present before")
        self.assertEqual(set(r), {"restored", "refreshed"}, "return shape unchanged")
        self.assertFalse((dest / "orphan.py").exists(), "the orphan is gone")

    # --- scenario 11: dest's parent directory does not exist yet -----------

    def test_scn11_dest_parent_not_yet_created(self):                    # boundary, feeds M1
        src = self.tmp / "src11"; src.mkdir()
        (src / "a.py").write_text("A")
        dest = self.area / "brand" / "new" / "dest"   # no part of this chain exists
        self.assertFalse(dest.parent.exists())
        r = _installer._clean_replace(src, dest)
        self.assertEqual((dest / "a.py").read_text(), "A")
        self.assertEqual(r, {"restored": 1, "refreshed": 0})
        self.assertEqual(self._siblings_of(dest), set(),
                         "no error, no scratch sibling, merely from a missing parent")


class ConcurrencyDisclosureTest(unittest.TestCase):
    """Scenario 12: two concurrent, lock-less runs racing on the SAME dest -- ruled out on
    purpose (Reject: no cross-writer guarantee; owned by project-scope-install-lock). This
    task guarantees only that EACH writer's own copy is never observed half-composed; it does
    NOT guarantee which writer wins the race. Best-effort: real OS thread-scheduling
    nondeterminism means this test cannot force a specific interleaving, but the ASSERTION
    (never a blend of both generations) holds for ANY interleaving under a correct
    atomic-rename implementation, so it remains a meaningful regression guard."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rollup-race-")).resolve()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scn12_concurrent_racing_writers_never_leave_a_blend(self):   # Reject: concurrent runs
        src_a = self.tmp / "src_a"; src_a.mkdir()
        for n in ("x.py", "y.py"):
            (src_a / n).write_text("A-" + n)
        src_b = self.tmp / "src_b"; src_b.mkdir()
        for n in ("y.py", "z.py"):
            (src_b / n).write_text("B-" + n)
        dest = self.tmp / "dest"; dest.mkdir()
        (dest / "y.py").write_text("ORIGINAL-y")

        def _run(src):
            try:
                _installer._clean_replace(src, dest)
            except OSError:
                pass    # a lock-less race MAY raise for the losing writer -- disclosed, tolerated

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futures = [ex.submit(_run, src_a), ex.submit(_run, src_b)]
            concurrent.futures.wait(futures)

        final = sorted(p.name for p in dest.iterdir()) if dest.exists() else []
        set_a, set_b = sorted(p.name for p in src_a.iterdir()), sorted(p.name for p in src_b.iterdir())
        self.assertIn(final, (set_a, set_b),
                     "dest is fully ONE writer's generation or fully the OTHER's -- never an "
                     "impossible blend (e.g. never missing y.py while holding both x.py and z.py)")


class CrossTwinStagedCommitTest(unittest.TestCase):
    """Scenario 10 (M9): both twins guarantee the SAME observable staged-commit behavior."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rollup-xtwin-")).resolve()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scn10_python_twin_staging_failure_dest_untouched(self):
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root bypasses directory write permissions")
        src = self.tmp / "src"; src.mkdir()
        (src / "new.py").write_text("NEW")
        area = self.tmp / "area"; area.mkdir()
        dest = area / "dest"; dest.mkdir()
        (dest / "old.py").write_text("OLD")
        before = (dest / "old.py").read_bytes()
        os.chmod(area, 0o555)          # blocks a NEW entry in area/ -- the staging mkdtemp call
        try:
            with self.assertRaises(OSError):
                _installer._clean_replace(src, dest)
        finally:
            os.chmod(area, 0o755)
        self.assertTrue((dest / "old.py").exists(), "python twin: dest byte-for-byte untouched (old.py survives)")
        self.assertEqual((dest / "old.py").read_bytes(), before, "python twin: dest byte-for-byte untouched")
        self.assertEqual([p.name for p in area.iterdir()], ["dest"], "python twin: no scratch sibling survives")

    def test_scn10_node_twin_staging_failure_dest_untouched(self):
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root bypasses directory write permissions")
        if not shutil.which("node"):
            self.skipTest("node not available")
        target = self.tmp / "proj"; target.mkdir()
        env = dict(os.environ); env.pop("CI", None)
        r0 = subprocess.run(["node", str(CLI_JS), "init", str(target), "--yes"],
                            capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(r0.returncode, 0, f"setup: real npm init failed: {r0.stderr}")
        tooling = target / ".add" / "tooling"
        self.assertTrue(tooling.exists(), "setup: a real init materializes .add/tooling")
        before = {p.relative_to(tooling): p.read_bytes() for p in tooling.rglob("*") if p.is_file()}
        add_dir = target / ".add"
        os.chmod(add_dir, 0o555)       # blocks a NEW entry in .add/ -- the staging mkdtemp call
        try:
            r = subprocess.run(["node", str(CLI_JS), "update", str(target), "--force"],
                               capture_output=True, text=True, env=env, timeout=120)
        finally:
            os.chmod(add_dir, 0o755)
        self.assertNotEqual(r.returncode, 0, "node twin: a staging failure must fail the update")
        after = {p.relative_to(tooling): p.read_bytes() for p in tooling.rglob("*") if p.is_file()}
        self.assertEqual(after, before, "node twin: .add/tooling byte-for-byte untouched")
        leftover = [p.name for p in add_dir.iterdir()
                   if p.name.startswith("tooling.add-tmp-") or p.name.startswith("tooling.add-bak-")]
        self.assertEqual(leftover, [], "node twin: no partial staging/backup sibling survives inside .add/")

    def test_scn10_structural_parity_of_staged_commit_shape(self):
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        js = CLI_JS.read_text(encoding="utf-8")
        py_body = py[py.index("def _clean_replace("):]
        py_body = py_body[:py_body.index("\ndef ", 1)]
        js_body = js[js.index("function cleanReplaceTree("):]
        js_body = js_body[:js_body.index("\nfunction ", 1)]
        markers = ("-- self-heal --", "-- stage --", "-- commit --", "-- sweep --")
        for marker in markers:
            self.assertIn(marker, py_body, f"_clean_replace must mark its {marker} phase")
            self.assertIn(marker, js_body, f"cleanReplaceTree must mark its {marker} phase")
        for body, name in ((py_body, "_clean_replace"), (js_body, "cleanReplaceTree")):
            idxs = [body.index(m) for m in markers]
            self.assertEqual(idxs, sorted(idxs),
                             f"{name} must run self-heal -> stage -> commit -> sweep in source order")
        for token in ("add-tmp-", "add-bak-"):
            self.assertIn(token, py_body, f"_clean_replace must use the reserved '{token}' prefix")
            self.assertIn(token, js_body, f"cleanReplaceTree must use the reserved '{token}' prefix")
        # M9: internal failures in the NEW region throw/raise real errors; the ONE pre-existing
        # top-level precondition (source missing) is the only permitted fail() call-site.
        self.assertEqual(js_body.count("fail("), 1,
                         "cleanReplaceTree's new stage/commit region must never call fail() "
                         "internally (fail() calls process.exit(1) directly, skipping "
                         "finally-based cleanup) -- only the pre-existing source-missing "
                         "precondition may")
        self.assertIn("throw", js_body, "cleanReplaceTree's new logic must throw real Errors internally")


if __name__ == "__main__":
    unittest.main(verbosity=2)
