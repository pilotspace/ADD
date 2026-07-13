#!/usr/bin/env python3
"""Red/green tests for the explicit 3-mode autonomy dial (task explicit-autonomy-dial).

The autonomy level is an EXPLICIT, human-set per-task header token, an ordered
ladder `manual < conservative < auto`:

  * gate    — the high-risk completion guard accepts ANY lowered rung (manual OR
    conservative), not just the literal `conservative`; `risk: high` + `auto`
    (or no lowered level) still REFUSES `unguarded_high_risk_auto`. So a high-risk
    task set to the STRICTER `manual` is no longer wrongly refused.
  * check   — a REAL token outside {manual,conservative,auto} is `unknown_autonomy_level`
    (red); a LIVE task with no `autonomy:` line is `implicit_autonomy` (WARN — additive,
    never red; done/archived predecessors are SKIPPED, so the board never floods).
  * new-task — seeds a VISIBLE, overridable `autonomy: auto` default (the established
    v7 default made explicit, the human aware), so fresh tasks never warn.
  * status  — surfaces the active task's autonomy level every session.

Asserts CLI output + exit codes + the seeded file, never parser internals. Run:
    python3 -m unittest test_explicit_autonomy_dial -v
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

GOOD3 = "Status: FROZEN @ v1 — approved by Tin, 2026-06-10"


def _sec6():
    return ("  - [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only\n\n"
            "### GATE RECORD\nOutcome: PASS — human-confirmed\nReviewed by: Tin (human) · date: 2026-06-10")


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (engine input contracts)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-aut-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["init", "--name", "demo"])
            add.main(["new-milestone", "v1", "--title", "T", "--goal", "g"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _task_md(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "TASK.md"

    def _body(self, slug: str, risk=None, autonomy=None, frozen: bool = True) -> str:
        meta = f"slug: {slug} · created: 2026-06-10 · stage: mvp"
        if risk:
            meta += f" · risk: {risk}"
        head = [f"# TASK: {slug}", "", meta]
        if autonomy is not None:
            head.append(f"autonomy: {autonomy}")
        head.append("phase: specify")  # plan-phase-core seed; must match new-task's state phase
        sec3 = GOOD3 if frozen else "Status: DRAFT"
        return "\n".join(head + ["",
            "## 1 · SPECIFY", "Feature: f", "",
            "## 2 · SCENARIOS", "(none)", "",
            "## 3 · CONTRACT", "```\nshape\n```", "", sec3, "",
            "## 4 · TESTS", "plan", "",
            "## 5 · BUILD", "code", "",
            "## 6 · VERIFY", _sec6(), "",
            "## 7 · OBSERVE", "watch", "",
        ])

    def _mk(self, slug: str, risk=None, autonomy=None):
        """new-task, then overwrite with a header we control byte-exactly."""
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["new-task", slug, "--title", slug])      # becomes the active task
        self._task_md(slug).write_text(self._body(slug, risk, autonomy), encoding="utf-8")

    def _to_verify(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["phase", "verify"])                       # operates on the active task

    def _gate(self, slug, outcome="PASS"):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["gate", outcome, slug])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

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

    def _failed_reasons(self, d) -> str:
        return " ".join(c["reason"] for c in d["checks"] if not c["ok"])

    def _warn_blob(self, d) -> str:
        return " ".join(f'{w["name"]} {w["reason"]}' for w in d["warnings"])


# ============================================================================
# High-risk guard — the widening (conservative -> any lowered rung)
# ============================================================================
class HighRiskGuardTest(_Board):

    def test_manual_satisfies_high_risk_guard(self):
        # the core widening: manual is STRICTER than conservative; it must not be refused
        self._mk("alpha", risk="high", autonomy="manual")
        self._to_verify()
        out, err, code = self._gate("alpha")
        self.assertEqual(code, 0, out + err)

    def test_conservative_satisfies(self):       # regression — unchanged
        self._mk("alpha", risk="high", autonomy="conservative")
        self._to_verify()
        _, _, code = self._gate("alpha")
        self.assertEqual(code, 0)

    def test_auto_refused(self):                 # regression — unchanged
        self._mk("alpha", risk="high", autonomy="auto")
        self._to_verify()
        out, err, code = self._gate("alpha")
        self.assertNotEqual(code, 0)
        self.assertIn("unguarded_high_risk_auto", out + err)

    def test_high_risk_missing_level_refused(self):   # the soft path can't smuggle auto
        self._mk("alpha", risk="high", autonomy=None)
        self._to_verify()
        out, err, code = self._gate("alpha")
        self.assertNotEqual(code, 0)
        self.assertIn("unguarded_high_risk_auto", out + err)


# ============================================================================
# check lint — unknown (red) vs implicit (warn), live-only scope
# ============================================================================
class CheckLintTest(_Board):

    def test_unknown_level_rejected(self):
        self._mk("alpha", autonomy="yolo")       # a REAL out-of-set token
        d, _ = self._check_json()
        self.assertIn("unknown_autonomy_level", self._failed_reasons(d))
        self.assertGreaterEqual(d["failed"], 1)

    def test_missing_level_warns_not_red(self):
        self._mk("alpha", autonomy=None)          # LIVE (specify), no token
        d, _ = self._check_json()
        self.assertIn("implicit_autonomy", self._warn_blob(d))
        self.assertEqual(d["failed"], 0)          # a warning never reds

    def test_done_predecessor_not_warned(self):
        self._mk("alpha", autonomy=None)
        self._to_verify()
        self._gate("alpha")                       # -> done
        d, _ = self._check_json()
        self.assertNotIn("implicit_autonomy", self._warn_blob(d))


# ============================================================================
# new-task seed + status surface
# ============================================================================
class SeedAndSurfaceTest(_Board):

    def test_new_task_seeds_auto_default(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["new-task", "fresh", "--title", "fresh"])
        header = self._task_md("fresh").read_text(encoding="utf-8").split("\n## ", 1)[0]
        self.assertIn("autonomy: auto", header)
        # a freshly-seeded task carries a valid level, so it must NOT warn implicit_autonomy
        d, _ = self._check_json()
        self.assertFalse(
            any("implicit_autonomy" in w["reason"] and "fresh" in w["name"] for w in d["warnings"]),
            "a seeded `autonomy: auto` task must not be flagged implicit")

    def test_status_surfaces_level(self):
        self._mk("alpha", autonomy="conservative")     # alpha is the active task
        out = self._status()
        self.assertIn("autonomy", out)
        self.assertIn("conservative", out)


# ============================================================================
# Docs accord — the frozen §1 Must / §4 plan: GLOSSARY + the autonomy docs
# (appendix-c · 10-setup-and-stages · 11-governance) name all three rungs,
# prose ≡ enforcement, byte-synced across the three trees (add-method · .add · _bundled).
# ============================================================================
class DocsAccordTest(unittest.TestCase):
    RUNGS = ("manual", "conservative", "auto")

    # canonical add-method/ tree first; the synced twins must stay byte-identical
    DOC_TREES = (REPO / "add-method" / "docs", REPO / ".add" / "docs", BUNDLE / "docs")
    AUTONOMY_DOCS = ("appendix-c-glossary.md", "10-setup-and-stages.md", "11-governance.md")
    TMPL_TREES = (REPO / "add-method" / "tooling" / "templates",
                  REPO / ".add" / "tooling" / "templates",
                  BUNDLE / "tooling" / "templates")

    def _assert_names_rungs(self, path, label):
        text = path.read_text(encoding="utf-8")
        for rung in self.RUNGS:
            with self.subTest(surface=label, rung=rung):
                self.assertIn(rung, text, f"{label} must name the `{rung}` rung (prose ≡ enforcement)")

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

    def test_autonomy_book_docs_name_three_rungs_synced(self):
        # the §1 Must names appendix-c · 10-setup · 11-governance explicitly
        for fname in self.AUTONOMY_DOCS:
            self._assert_names_rungs(self.DOC_TREES[0] / fname, f"docs/{fname}")
            self._assert_synced(self.DOC_TREES, fname)

    def test_glossary_survivor_names_three_rungs(self):
        # the living-doc GLOSSARY the human reads on the board
        self._assert_names_rungs(REPO / ".add" / "GLOSSARY.md", ".add/GLOSSARY.md")

    def test_glossary_template_names_three_rungs_synced(self):
        # the GLOSSARY new projects are seeded with
        self._assert_names_rungs(self.TMPL_TREES[0] / "GLOSSARY.md.tmpl", "GLOSSARY.md.tmpl")
        self._assert_synced(self.TMPL_TREES, "GLOSSARY.md.tmpl")


if __name__ == "__main__":
    unittest.main(verbosity=2)
