#!/usr/bin/env python3
"""Red/green tests for add.py. Run: python3 -m unittest test_add -v"""
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add


class AddToolTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-test-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    def _run(self, *argv):
        return add.main(list(argv))

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _freeze(self, slug="t"):
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = Path(self.tmp) / ".add" / "tasks" / slug / "PLAN.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    # --- init ---
    def test_init_creates_state_and_setup_files(self):
        self._run("init", "--name", "demo", "--stage", "mvp")
        root = Path(self.tmp) / ".add"
        self.assertTrue((root / "state.json").exists())
        for f in add.SETUP_FILES:
            self.assertTrue((root / f).exists(), f"missing {f}")
        st = self._state()
        self.assertEqual(st["project"], "demo")
        self.assertEqual(st["stage"], "mvp")
        self.assertIsNone(st["active_task"])

    def test_reinit_is_noop_without_force(self):
        # init-idempotent-nudge (call-residuals): a re-init WITHOUT --force is now a
        # LOUD NO-OP (exit 0, writes nothing), not a SystemExit refusal — superseding
        # the earlier clobber-refusal contract. Full contract in
        # test_init_idempotent_nudge.py.
        self._run("init")
        before = {p: p.read_bytes()
                  for p in (Path(self.tmp) / ".add").rglob("*") if p.is_file()}
        self._run("init")   # must NOT raise SystemExit
        after = {p: p.read_bytes()
                 for p in (Path(self.tmp) / ".add").rglob("*") if p.is_file()}
        self.assertEqual(before, after, "a no-op re-init must write nothing")

    # --- gitignore scaffold (keep transient engine artifacts out of git) ---
    def test_init_scaffolds_gitignore(self):
        # RED pre-build: cmd_init does not yet write .add/.gitignore.
        self._run("init", "--name", "demo", "--stage", "mvp")
        gi = Path(self.tmp) / ".add" / ".gitignore"
        self.assertTrue(gi.exists(), "init did not scaffold .add/.gitignore")
        body = gi.read_text()
        self.assertIn("scope-snapshot.json", body)
        self.assertIn("pre-archive-state.bak.json", body)
        self.assertIn(".update-cache.json", body)

    def test_gitignore_ignores_transient_artifacts(self):
        # RED pre-build: with no scaffolded rules, git ignores neither artifact.
        # Enforcement, not string-presence: a real `git check-ignore` must match.
        import shutil
        import subprocess
        if shutil.which("git") is None:
            self.skipTest("git unavailable")
        subprocess.run(["git", "init", "-q", self.tmp], check=True)
        self._run("init", "--name", "demo", "--stage", "mvp")
        root = Path(self.tmp) / ".add"
        snap = root / "tasks" / "demo" / "scope-snapshot.json"
        bak = root / "milestones" / "demo" / "pre-archive-state.bak.json"
        cache = root / ".update-cache.json"
        snap.parent.mkdir(parents=True, exist_ok=True)
        bak.parent.mkdir(parents=True, exist_ok=True)
        snap.write_text("{}")
        bak.write_text("{}")
        cache.write_text("{}")

        def ignored(rel):
            return subprocess.run(
                ["git", "-C", self.tmp, "check-ignore", rel],
                capture_output=True, text=True).returncode == 0

        self.assertTrue(ignored(".add/tasks/demo/scope-snapshot.json"))
        self.assertTrue(ignored(".add/milestones/demo/pre-archive-state.bak.json"))
        self.assertTrue(ignored(".add/.update-cache.json"))
        # artifact-specific, never a blanket .add/ ignore
        self.assertFalse(ignored(".add/state.json"))

    def test_init_never_clobbers_existing_gitignore(self):
        # Regression guard (green pre-build): a pre-existing .add/.gitignore is
        # preserved. Only fails if the scaffold is ever made to clobber.
        root = Path(self.tmp) / ".add"
        root.mkdir(parents=True, exist_ok=True)
        sentinel = "# human-customised\nfoo.tmp\n"
        (root / ".gitignore").write_text(sentinel)
        self._run("init", "--name", "demo", "--stage", "mvp")
        self.assertEqual((root / ".gitignore").read_text(), sentinel)
        self.assertTrue((root / "state.json").exists())

    # --- new-task ---
    def test_new_task_scaffolds_and_activates(self):
        self._run("init")
        self._run("new-task", "transfer", "--title", "Transfer money")
        tdir = Path(self.tmp) / ".add" / "tasks" / "transfer"
        self.assertTrue((tdir / "PLAN.md").exists())
        self.assertTrue((tdir / "tests").is_dir())
        self.assertTrue((tdir / "src").is_dir())
        st = self._state()
        self.assertEqual(st["active_task"], "transfer")
        self.assertEqual(st["tasks"]["transfer"]["phase"], "direction")  # phase-collapse-3 seed
        self.assertIn("Transfer money", (tdir / "PLAN.md").read_text())

    def test_new_task_rejects_bad_slug(self):
        self._run("init")
        with self.assertRaises(SystemExit):
            self._run("new-task", "bad slug!")

    def test_new_task_requires_init(self):
        with self.assertRaises(SystemExit):
            self._run("new-task", "x")

    # --- advance / phase / marker sync ---
    def test_advance_moves_phase_and_syncs_marker(self):
        self._run("init")
        self._run("new-task", "t")            # phase=direction (phase-collapse-3 seed)
        self._freeze()                        # the ONE crossing runs the freeze gate
        self._run("advance")  # direction -> build (the full _build_entry stack)
        st = self._state()
        self.assertEqual(st["tasks"]["t"]["phase"], "build")
        marker = [l for l in (Path(self.tmp) / ".add" / "tasks" / "t" / "PLAN.md"
                              ).read_text().splitlines() if l.startswith("phase:")][0]
        self.assertIn("build", marker)

    def test_phase_explicit_set(self):
        self._run("init")
        self._run("new-task", "t")
        self._freeze()  # freeze-gate-universal: §3 must be FROZEN before entering build
        self._run("phase", "build", "t")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "build")

    # --- gate ---
    def test_gate_pass_marks_done(self):
        self._run("init")
        self._run("new-task", "t")
        self._freeze()  # freeze-gate-universal: §3 must be FROZEN before tests->build crossing
        for _ in range(6):  # ground -> ... -> verify: PASS requires verify (no silent skip)
            self._run("advance")
        self._run("gate", "PASS")
        st = self._state()
        self.assertEqual(st["tasks"]["t"]["gate"], "PASS")
        self.assertEqual(st["tasks"]["t"]["phase"], "done")

    def test_gate_hardstop_keeps_phase(self):
        self._run("init")
        self._run("new-task", "t")
        self._run("phase", "verify", "t")
        self._run("gate", "HARD-STOP")
        st = self._state()
        self.assertEqual(st["tasks"]["t"]["gate"], "HARD-STOP")
        self.assertEqual(st["tasks"]["t"]["phase"], "verify")

    # --- stage ---
    def test_stage_change(self):
        # v22 graduate-guide: the →production flip is now GUARDED (it needs ≥1 production
        # milestone — a roadmap), so this bare-flip mechanic is asserted on a NON-production
        # stage; the guarded production path lives in test_graduate_guard.py. This is a
        # precondition-change (the old premise — an unguarded production flip — no longer
        # holds), NOT a weakening: the flip mechanic is still proven, just on a stage the
        # transition guard does not gate.
        self._run("init")
        self._run("stage", "poc")
        self.assertEqual(self._state()["stage"], "poc")

    # --- find_root walks up ---
    def test_find_root_from_subdir(self):
        self._run("init")
        sub = Path(self.tmp) / "a" / "b"
        sub.mkdir(parents=True)
        os.chdir(sub)
        self.assertIsNotNone(add.find_root())

    # --- check (project integrity validator) ---
    def test_check_passes_on_clean_project(self):
        self._run("init")
        self._run("new-task", "t")
        self.assertEqual(self._run("check"), 0)

    def test_check_detects_missing_task_md(self):
        self._run("init")
        self._run("new-task", "t")
        task_md = Path(self.tmp) / ".add" / "tasks" / "t" / "PLAN.md"
        task_md.unlink()
        with self.assertRaises(SystemExit) as cm:
            self._run("check")
        self.assertEqual(cm.exception.code, 1)  # contract: failure -> exit 1
        self.assertFalse(task_md.exists())       # read-only: not recreated

    def test_check_detects_phase_mismatch(self):
        self._run("init")
        self._run("new-task", "t")
        st = self._state()
        st["tasks"]["t"]["phase"] = "build"  # diverge from PLAN.md marker (specify)
        (Path(self.tmp) / ".add" / "state.json").write_text(json.dumps(st))
        with self.assertRaises(SystemExit) as cm:
            self._run("check")
        self.assertEqual(cm.exception.code, 1)

    def test_check_no_project(self):
        with self.assertRaises(SystemExit) as cm:
            self._run("check")
        self.assertEqual(cm.exception.code, 1)  # "no_project"

    def test_check_state_invalid(self):
        self._run("init")
        (Path(self.tmp) / ".add" / "state.json").write_text("{ not json")
        with self.assertRaises(SystemExit) as cm:
            self._run("check")
        self.assertEqual(cm.exception.code, 1)  # "state_invalid"


if __name__ == "__main__":
    unittest.main(verbosity=2)
