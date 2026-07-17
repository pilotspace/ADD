#!/usr/bin/env python3
"""Red/green tests for the auto-ready goal (task goal-auto-ready-gate).

A milestone goal is AUTO-READY iff its `## Exit criteria` has >= 1 criterion AND
every criterion line cites a verifier `(verify: <test|command|metric>)` — so the
engine can self-verify the result against the goal without human judgement.

  * _goal_auto_ready / _exit_criteria_cited — the PURE classifier (cited/total).
  * check  — a WARN (NEVER red) for the ACTIVE milestone when not auto-ready;
             live-only (a non-active milestone is never flagged).
  * status — surfaces the active milestone's auto-ready status.
  * docs   — GLOSSARY + book + skill name "auto-ready goal" (prose ≡ enforcement).

    cd add-method/tooling && python3 -m unittest test_goal_auto_ready_gate -v
"""
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BUNDLE = HERE.parent / "src" / "add_method" / "_bundled"


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-gar-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["init", "--name", "demo"])
            add.main(["new-milestone", "v1", "--title", "T", "--goal", "g"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _set_criteria(self, lines, mslug="v1"):
        body = ("# MILESTONE: T\n\n"
                "goal: g\nstage: mvp · status: active · created: 2026-06-10\n\n"
                "## Exit criteria\n" + "".join(f"{ln}\n" for ln in lines))
        (self._root() / "milestones" / mslug / "MILESTONE.md").write_text(body, encoding="utf-8")

    def _check_json(self):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["check", "--json"])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return json.loads(buf.getvalue()), code

    def _status(self) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            add.main(["status"])
        return buf.getvalue()

    def _warn_blob(self, d) -> str:
        return " ".join(f'{w["name"]} {w["reason"]}' for w in d["warnings"])

    def _failed_reasons(self, d) -> str:
        return " ".join(c["reason"] for c in d["checks"] if not c["ok"])


class ClassifierTest(_Board):

    def test_all_cited_is_auto_ready(self):
        self._set_criteria(["- [ ] one (verify: test_one)",
                            "- [x] two (verify: `add.py check`)"])
        self.assertTrue(add._goal_auto_ready(self._root(), "v1"))
        d, _ = self._check_json()
        self.assertNotIn("goal_not_auto_ready", self._warn_blob(d))

    def test_no_criteria_not_auto_ready(self):
        self._set_criteria([])
        self.assertFalse(add._goal_auto_ready(self._root(), "v1"))

    def test_empty_verify_paren_does_not_count(self):
        # an empty `(verify:)` must NOT count as a citation (the mid-text substring trap)
        self._set_criteria(["- [ ] do it (verify:)"])
        self.assertFalse(add._goal_auto_ready(self._root(), "v1"))

    def test_goal_auto_ready_helper(self):
        root = self._root()
        self._set_criteria(["- [ ] a (verify: t)", "- [x] b (verify: `c`)"])
        self.assertTrue(add._goal_auto_ready(root, "v1"))
        self._set_criteria(["- [ ] a (verify: t)", "- [ ] b"])
        self.assertFalse(add._goal_auto_ready(root, "v1"))
        self._set_criteria([])
        self.assertFalse(add._goal_auto_ready(root, "v1"))


class CheckWarnTest(_Board):

    def test_one_bare_criterion_warns_not_red(self):
        self._set_criteria(["- [ ] one (verify: test_one)", "- [ ] two"])  # 'two' is bare
        d, code = self._check_json()
        self.assertIn("goal_not_auto_ready", self._warn_blob(d))
        self.assertEqual(code, 0, "auto-readiness is a WARN, never a red check")
        self.assertNotIn("goal_not_auto_ready", self._failed_reasons(d))

    def test_zero_criteria_does_not_warn(self):
        # a zero-criteria active milestone is CLASSIFIED not-ready, but the WARN stays
        # SILENT — writing criteria is milestone-shaping's nudge, separable from citing
        # them (the deliberate firing condition: total >= 1 AND cited < total).
        self._set_criteria([])
        self.assertFalse(add._goal_auto_ready(self._root(), "v1"))
        d, _ = self._check_json()
        self.assertNotIn("goal_not_auto_ready", self._warn_blob(d))

    def test_check_warns_active_only(self):
        # v1 (the soon-to-be non-active) bare; v2 becomes active and is also bare.
        self._set_criteria(["- [ ] do the thing"], "v1")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["new-milestone", "v2", "--title", "T2", "--goal", "g2"])
        self._set_criteria(["- [ ] do another"], "v2")
        d, _ = self._check_json()
        blob = self._warn_blob(d)
        self.assertIn("goal_not_auto_ready", blob)
        self.assertIn("v2", blob, "the ACTIVE milestone is flagged")
        self.assertNotIn("v1", blob, "a non-active milestone is NEVER flagged (live-only)")

    def test_done_active_milestone_not_flagged(self):
        # `milestone done` flips status->done, but only `archive` clears the
        # active_milestone pointer (+ removes it from the dict). In that interim window a
        # CLOSED (done) milestone is still the active pointer — Must #4 (live-only) says a
        # closed milestone is NEVER flagged, even with bare criteria (no retro-redding).
        self._set_criteria(["- [ ] one (verify: test_one)", "- [ ] two"])  # 'two' is bare
        root = self._root()
        st = add.load_state(root)
        st["milestones"]["v1"]["status"] = "done"
        add.save_state(root, st)
        d, _ = self._check_json()
        blob = self._warn_blob(d)
        self.assertNotIn("goal_not_auto_ready", blob,
                         "a done (closed) milestone is never flagged while still the active pointer")
        self.assertNotIn("goal_not_auto_ready", self._failed_reasons(d))


class StatusSurfaceTest(_Board):

    def test_status_surfaces_auto_ready(self):
        self._set_criteria(["- [ ] one (verify: test_one)"])
        self.assertRegex(self._status(), r"(?i)auto-ready",
                         "status must surface the active milestone's auto-ready status")


# ============================================================================
# Docs accord — every named surface defines "auto-ready goal" (prose ≡ enforcement);
# the ×3 book/template twins stay byte-synced. (v23 lesson: pin EVERY surface.)
# ============================================================================
class DocsAccordTest(unittest.TestCase):
    TERM = "auto-ready goal"
    DOC_TREES = (REPO / "add-method" / "docs",)   # book-stops-shipping (2.0 M6b): canonical only
    BOOK_DOCS = ("appendix-c-glossary.md", "11-governance.md")
    TMPL_TREES = (REPO / "add-method" / "tooling" / "templates",
                  REPO / ".add" / "tooling" / "templates",
                  BUNDLE / "tooling" / "templates")

    def _assert_has(self, path, label):
        self.assertIn(self.TERM, path.read_text(encoding="utf-8"),
                      f"{label} must name '{self.TERM}' (prose ≡ enforcement)")

    def _assert_synced(self, trees, fname):
        # trees[0] is the canonical (tracked) source. The .add/ twin is the gitignored
        # dogfood install — ABSENT on a clean checkout / CI (regenerated by `add.py init`) —
        # so assert parity only against twins that are present; the tracked canonical + bundle
        # still guarantee the sync (mirrors test_foundation_update_loop / test_flow_diagram).
        canon = (trees[0] / fname).read_bytes()
        present = [t for t in trees[1:] if (t / fname).exists()]
        self.assertTrue(present, f"{fname}: need at least one tracked twin beside canonical")
        for t in present:
            with self.subTest(file=fname, twin=str(t)):
                self.assertEqual(canon, (t / fname).read_bytes(),
                                 f"divergence (synced): {t / fname}")

    def test_glossary_survivor_names_term(self):
        self._assert_has(REPO / ".add" / "GLOSSARY.md", ".add/GLOSSARY.md")

    def test_glossary_template_names_term_synced(self):
        self._assert_has(self.TMPL_TREES[0] / "GLOSSARY.md.tmpl", "GLOSSARY.md.tmpl")
        self._assert_synced(self.TMPL_TREES, "GLOSSARY.md.tmpl")


    def test_skill_run_names_term(self):
        self._assert_has(REPO / ".claude" / "skills" / "add" / "run.md", "skill run.md")


if __name__ == "__main__":
    unittest.main()
