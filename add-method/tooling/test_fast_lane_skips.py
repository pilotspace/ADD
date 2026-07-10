#!/usr/bin/env python3
"""Red/green tests for fast-lane-skips (task: fast-lane-skips, milestone: three-phase-flow).

CONTRACT (frozen @ v1, §3 of .add/tasks/fast-lane-skips/TASK.md): a per-task, AI-declared
skip-set (subset of `{scenarios, observe}`) that lets `cmd_advance` jump those two phases as a
REAL engine-level crossing (never entered) — gated by lane eligibility (`fast:true` |
`oneshot:true` | project `benchmark_mode:true`), fail-closed on any out-of-set token, and never
honored without a stated per-phase reason (§0 "Skip rationale:") recorded BEFORE the jump. Every
actual skip is recorded in `state["tasks"][slug]["skips"]`. Composed with, never entangled in,
task2's (`ai-plan-verify-gate`) `gate_mode: ai-plan-verify` contract-auto-freeze mechanism via a
new `--oneshot` flag that declares both at once.

  add_engine/constants.py  _SKIPPABLE_PHASES = ("scenarios", "observe")        — joins __all__
  add.py                   _SKIPS_LINE_RE / _task_skip_set(hdr)                — mirrors _task_gate_mode
  add_engine/predicates.py _skip_lane_eligible(fast, oneshot, benchmark_mode)  — mirrors _ai_freeze_allowed
  add_engine/predicates.py _skip_set_allowed(skip_tokens, eligible)
  add.py                   _skip_rationale(raw0, phase)
  add.py                   _project_benchmark_mode(root)                      — mirrors _project_autonomy_token
  add.py cmd_advance       skip pre-pass (`if nxt in _SKIPPABLE_PHASES:`)
  add.py cmd_new_task      --oneshot (sibling of --fast)
  add.py cmd_status/guide  additive "skips   : ..." line
  add.py _gate_explain     additive "skip-set: ..." line
  add.py cmd_audit         skip_rationale_missing_post_hoc residual glint (MEASURE-NOT-BLOCK)
  templates/TASK.fast.md.tmpl  scaffold: commented `skips:` header hint + §0 placeholder line

The normal flow (no fast/oneshot/benchmark, no skips:) is BYTE-IDENTICAL to before this task.

Run: cd add-method/tooling && python3 -m unittest test_fast_lane_skips -v
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import add
from add_engine import constants as engine_constants
from add_engine import predicates as engine_predicates

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
REPO_ROOT = PKG_ROOT.parent

ADD_PY_TREES = (
    HERE / "add.py",
    REPO_ROOT / ".add" / "tooling" / "add.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)
CONSTANTS_TREES = (
    HERE / "add_engine" / "constants.py",
    REPO_ROOT / ".add" / "tooling" / "add_engine" / "constants.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add_engine" / "constants.py",
)
PREDICATES_TREES = (
    HERE / "add_engine" / "predicates.py",
    REPO_ROOT / ".add" / "tooling" / "add_engine" / "predicates.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add_engine" / "predicates.py",
)
FAST_TMPL_TREES = (
    HERE / "templates" / "TASK.fast.md.tmpl",
    REPO_ROOT / ".add" / "tooling" / "templates" / "TASK.fast.md.tmpl",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.fast.md.tmpl",
    REPO_ROOT / "add-method" / ".add" / "tooling" / "templates" / "TASK.fast.md.tmpl",
)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Harness (mirrors test_ai_plan_verify_gate.py's _Harness idiom)
# ---------------------------------------------------------------------------

class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fls-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return out.getvalue() + err.getvalue(), code

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _task_md(self, slug):
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _fill_boundary(self, slug):
        # boundary floor (fast-lane-boundary-line): the rendered fast template now
        # scaffolds a placeholder `Boundary:` line that refuses the freeze — fill it
        # with a real declaration, as any real task must before its freeze
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        t = re.sub(r"(?m)^Boundary: <[^\n]*$",
                   "Boundary: aware vs naive timestamp on the request payload", t, count=1)
        p.write_text(t, encoding="utf-8")

    def _set_header(self, slug, **kv):
        """Insert/replace autonomy:/fast:/oneshot:/skips: header lines."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        for key in ("autonomy", "fast", "oneshot", "skips"):
            if key not in kv:
                continue
            val = kv[key]
            pattern = rf"(?m)^{key}:.*$"
            if re.search(pattern, t):
                t = re.sub(pattern, f"{key}: {val}", t, count=1)
            else:
                t = re.sub(r"(?m)^(autonomy:[^\n]*)$", rf"\1\n{key}: {val}", t, count=1)
        p.write_text(t, encoding="utf-8")

    def _set_skip_rationale(self, slug, text):
        """Replace (or insert) the §0 'Skip rationale:' line — text is everything after the colon."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        pattern = r"(?m)^Skip rationale:.*$"
        if re.search(pattern, t):
            t = re.sub(pattern, f"Skip rationale: {text}", t, count=1)
        else:
            t = re.sub(r"(?=\n## 1 ·)", f"\nSkip rationale: {text}\n", t, count=1)
        p.write_text(t, encoding="utf-8")

    def _clear_skip_rationale(self, slug):
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        t = re.sub(r"(?m)^Skip rationale:.*$\n?", "", t)
        p.write_text(t, encoding="utf-8")

    def _new_fast_task(self, slug="t", fast=True, oneshot=False, benchmark=False):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        if benchmark:
            proj = self.tmp / ".add" / "PROJECT.md"
            proj.write_text(proj.read_text(encoding="utf-8") + "\nbenchmark_mode: true\n",
                             encoding="utf-8")
        argv = ["new-task", slug, "--title", "Feature"]
        if oneshot:
            argv.append("--oneshot")
        elif fast:
            argv.append("--fast")
        self._silent(*argv)


# ---------------------------------------------------------------------------
# M1 — _SKIPPABLE_PHASES closed 2-tuple, importable, listed in __all__
# ---------------------------------------------------------------------------

class SkippablePhasesConstantTest(unittest.TestCase):
    def test_value_and_all(self):
        self.assertEqual(engine_constants._SKIPPABLE_PHASES, ("scenarios", "observe"))
        self.assertIn("_SKIPPABLE_PHASES", engine_constants.__all__)

    def test_importable_via_star_import(self):
        self.assertTrue(hasattr(add, "_SKIPPABLE_PHASES"))
        self.assertEqual(add._SKIPPABLE_PHASES, engine_constants._SKIPPABLE_PHASES)


# ---------------------------------------------------------------------------
# M2 — _task_skip_set resolves absence, a valid CSV, and a malformed token
# ---------------------------------------------------------------------------

class TaskSkipSetResolverTest(unittest.TestCase):
    def test_absent_line_returns_empty_set_no_error(self):
        self.assertEqual(add._task_skip_set("slug: t · created: x\nautonomy: auto\n"),
                         (frozenset(), None))

    def test_valid_two_token_csv(self):
        self.assertEqual(add._task_skip_set("skips: scenarios,observe\n"),
                         (frozenset({"scenarios", "observe"}), None))

    def test_valid_single_token(self):
        self.assertEqual(add._task_skip_set("skips: scenarios\n"),
                         (frozenset({"scenarios"}), None))

    def test_one_bad_token_refuses_whole_declaration(self):
        # skip-error-ergonomics: the error string now carries its own repair —
        # assert the empty set + the stable `skip_not_allowed` prefix, not equality.
        toks, err = add._task_skip_set("skips: scenarios,build\n")
        self.assertEqual(toks, frozenset())
        self.assertTrue(err and err.startswith("skip_not_allowed"), err)
        self.assertIn("'build'", err, "the bad token is named")

    def test_wholly_unknown_token(self):
        toks, err = add._task_skip_set("skips: bogus\n")
        self.assertEqual(toks, frozenset())
        self.assertTrue(err and err.startswith("skip_not_allowed"), err)
        self.assertIn("'bogus'", err, "the bad token is named")


# ---------------------------------------------------------------------------
# M3 — _skip_lane_eligible: true iff any of the three inputs is true
# ---------------------------------------------------------------------------

class SkipLaneEligibleTest(unittest.TestCase):
    def test_any_single_true_input_yields_true(self):
        self.assertTrue(add._skip_lane_eligible(True, False, False))
        self.assertTrue(add._skip_lane_eligible(False, True, False))
        self.assertTrue(add._skip_lane_eligible(False, False, True))

    def test_all_false_yields_false(self):
        self.assertFalse(add._skip_lane_eligible(False, False, False))

    def test_predicate_lives_in_engine_predicates_module(self):
        self.assertIs(add._skip_lane_eligible, engine_predicates._skip_lane_eligible)


# ---------------------------------------------------------------------------
# M4 — _skip_set_allowed
# ---------------------------------------------------------------------------

class SkipSetAllowedTest(unittest.TestCase):
    def test_empty_set_permitted_regardless_of_eligibility(self):
        self.assertEqual(add._skip_set_allowed(frozenset(), False), (True, None))

    def test_non_empty_set_permitted_only_when_eligible(self):
        toks = frozenset({"scenarios"})
        self.assertEqual(add._skip_set_allowed(toks, True), (True, None))
        self.assertEqual(add._skip_set_allowed(toks, False), (False, "skip_lane_required"))

    def test_predicate_lives_in_engine_predicates_module(self):
        self.assertIs(add._skip_set_allowed, engine_predicates._skip_set_allowed)


# ---------------------------------------------------------------------------
# M5 — _skip_rationale extracts a matching clause and fails closed on absence
# ---------------------------------------------------------------------------

class SkipRationaleTest(unittest.TestCase):
    RAW0 = ("Touches: x\nSkip rationale: scenarios — the Accept line covers it; "
            "observe — no rollout to watch\nGround SHA: abc\n")

    def test_extracts_each_matching_clause(self):
        self.assertEqual(add._skip_rationale(self.RAW0, "scenarios"),
                         "the Accept line covers it")
        self.assertEqual(add._skip_rationale(self.RAW0, "observe"),
                         "no rollout to watch")

    def test_no_line_at_all_returns_none(self):
        self.assertIsNone(add._skip_rationale("Touches: x\nGround SHA: abc\n", "observe"))

    def test_line_present_but_no_clause_for_phase_returns_none(self):
        raw0 = "Skip rationale: scenarios — reason only\n"
        self.assertIsNone(add._skip_rationale(raw0, "observe"))

    def test_empty_reason_text_returns_none(self):
        raw0 = "Skip rationale: scenarios —    \n"
        self.assertIsNone(add._skip_rationale(raw0, "scenarios"))


# ---------------------------------------------------------------------------
# M6 — cmd_advance skip mechanic
# ---------------------------------------------------------------------------

class CmdAdvanceSkipMechanicTest(_Harness):
    def test_jumps_specify_to_contract_when_scenarios_declared_eligible_reasoned(self):
        self._new_fast_task("t", fast=True)
        self._silent("phase", "specify", "t")
        self._set_header("t", skips="scenarios")
        self._set_skip_rationale("t", "scenarios — collapsed into Accept")
        out = self._silent("advance", "t")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "contract")
        self.assertIn("phase specify -> contract", out)
        skips = self._state()["tasks"]["t"]["skips"]
        self.assertEqual(len(skips), 1)
        self.assertEqual(skips[0]["phase"], "scenarios")
        self.assertEqual(skips[0]["reason"], "collapsed into Accept")
        self.assertIn("by", skips[0])
        self.assertIn("at", skips[0])

    def test_jumps_verify_to_done_when_observe_declared_eligible_reasoned(self):
        self._new_fast_task("t", fast=True)
        self._silent("phase", "verify", "t")
        self._set_header("t", skips="observe")
        self._set_skip_rationale("t", "observe — no rollout to watch")
        out = self._silent("advance", "t")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")
        self.assertIn("phase verify -> done", out)
        skips = self._state()["tasks"]["t"]["skips"]
        self.assertEqual(len(skips), 1)
        self.assertEqual(skips[0]["phase"], "observe")

    def test_ordinary_path_when_phase_not_in_declared_skip_set(self):
        self._new_fast_task("t", fast=True)
        self._silent("phase", "specify", "t")
        self._set_header("t", skips="observe")
        self._set_skip_rationale("t", "observe — no rollout to watch")
        self._silent("advance", "t")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "scenarios")
        self.assertNotIn("skips", self._state()["tasks"]["t"])


# ---------------------------------------------------------------------------
# M6 / M13 — the 6 non-skippable crossings execute none of this task's new logic
# ---------------------------------------------------------------------------

class NonSkippableCrossingsUntouchedTest(_Harness):
    def _advance_spy_count(self, slug="t"):
        from unittest import mock
        with mock.patch.object(add, "_task_skip_set", wraps=add._task_skip_set) as spy:
            self._silent("advance", slug)
            return spy.call_count

    def _set_section3_and_freeze(self, slug):
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        body = ("\n```\nGET /x\n  200 -> {ok:true}\n```\n\n"
                "Least-sure flag surfaced at freeze:\n"
                "  ⚠ [contract] x — cost: y.\n"
                "Status: DRAFT\n")
        new = re.sub(r"(## 3 · CONTRACT[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        p.write_text(new, encoding="utf-8")
        self._fill_boundary(slug)
        self._silent("freeze", "--by", "Human")

    def test_six_non_skippable_crossings_never_invoke_task_skip_set(self):
        self._new_fast_task("t", fast=True)   # no skips: declared anywhere
        self.assertEqual(self._advance_spy_count(), 0, "ground->specify")
        self.assertGreater(self._advance_spy_count(), 0, "specify->scenarios (by design)")
        self.assertEqual(self._advance_spy_count(), 0, "scenarios->contract")
        self._set_section3_and_freeze("t")
        self.assertEqual(self._advance_spy_count(), 0, "contract->tests")
        self.assertEqual(self._advance_spy_count(), 0, "tests->build")
        self.assertEqual(self._advance_spy_count(), 0, "build->verify")
        self.assertGreater(self._advance_spy_count(), 0, "verify->observe (by design)")
        self.assertEqual(self._advance_spy_count(), 0, "observe->done")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")


# ---------------------------------------------------------------------------
# M7 — new-task --oneshot / --fast (no --oneshot)
# ---------------------------------------------------------------------------

class OneshotNewTaskTest(_Harness):
    def test_scaffolds_minimal_template_and_both_header_lines(self):
        self._silent("lock", "--force")
        self._silent("new-task", "quick", "--title", "Feature", "--oneshot")
        text = self._task_md("quick").read_text(encoding="utf-8")
        secs = set(add._phase_spans(text))
        self.assertEqual(secs, {0, 1, 3, 4, 5, 6})
        self.assertRegex(text, r"(?m)^fast:\s*true")
        self.assertRegex(text, r"(?m)^oneshot:\s*true")
        self.assertRegex(text, r"(?m)^gate_mode:\s*ai-plan-verify")
        st = self._state()["tasks"]["quick"]
        self.assertIs(st["fast"], True)
        self.assertIs(st["oneshot"], True)


class FastOnlyUnaffectedByOneshotTest(_Harness):
    def test_fast_without_oneshot_has_no_new_header_lines_or_state_key(self):
        self._silent("lock", "--force")
        self._silent("new-task", "quick", "--title", "Feature", "--fast")
        text = self._task_md("quick").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^fast:\s*true")
        self.assertNotRegex(text, r"(?m)^oneshot:")
        self.assertNotRegex(text, r"(?m)^gate_mode:")
        self.assertNotIn("oneshot", self._state()["tasks"]["quick"])


# ---------------------------------------------------------------------------
# M8 — _project_benchmark_mode
# ---------------------------------------------------------------------------

class ProjectBenchmarkModeTest(_Harness):
    def _write_project(self, extra):
        p = self.tmp / ".add" / "PROJECT.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n" + extra + "\n", encoding="utf-8")

    def test_declared_true(self):
        self._write_project("benchmark_mode: true")
        self.assertTrue(add._project_benchmark_mode(self.tmp / ".add"))

    def test_declared_false(self):
        self._write_project("benchmark_mode: false")
        self.assertFalse(add._project_benchmark_mode(self.tmp / ".add"))

    def test_absent_is_false(self):
        self.assertFalse(add._project_benchmark_mode(self.tmp / ".add"))

    def test_malformed_token_is_false(self):
        self._write_project("benchmark_mode: yes")
        self.assertFalse(add._project_benchmark_mode(self.tmp / ".add"))


# ---------------------------------------------------------------------------
# M9 — status/guide surface the declared and consumed skip-set
# ---------------------------------------------------------------------------

class StatusGuideSurfaceTest(_Harness):
    def test_status_and_guide_show_declared_csv_and_progress(self):
        self._new_fast_task("t", fast=True)
        self._silent("phase", "specify", "t")
        self._set_header("t", skips="scenarios,observe")
        self._set_skip_rationale("t", "scenarios — collapsed into Accept")
        self._silent("advance", "t")   # consumes the "scenarios" skip -> 1 recorded
        out_status = self._silent("status")
        out_guide = self._silent("guide")
        for out in (out_status, out_guide):
            self.assertIn("declared scenarios,observe", out)
            self.assertIn("skipped so far 1/2", out)

    def test_no_declaration_no_recorded_skip_prints_no_line(self):
        self._new_fast_task("t", fast=True)
        out = self._silent("status")
        self.assertNotIn("skips   :", out)


# ---------------------------------------------------------------------------
# M10 — gate-explain surfaces the skip-set predicate outcome
# ---------------------------------------------------------------------------

class GateExplainSkipSetTest(_Harness):
    def test_blocked_outcome_for_ineligible_declared_task(self):
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")   # NOT fast/oneshot
        self._set_header("t", skips="scenarios")
        out = self._silent("gate", "--explain", "t")
        self.assertIn("skip-set: blocked (skip_lane_required)", out)
        # the existing gate_mode line (task2, absent here) never crashes / interferes
        self.assertIn("advisor-gate-relax:", out)

    def test_no_declaration_prints_no_skip_set_line(self):
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")
        out = self._silent("gate", "--explain", "t")
        self.assertNotIn("skip-set:", out)


# ---------------------------------------------------------------------------
# M11 — audit flags a post-skip deleted rationale
# ---------------------------------------------------------------------------

class AuditSkipRationaleMissingPostHocTest(_Harness):
    def _skipped_task(self, slug="t"):
        self._new_fast_task(slug, fast=True)
        self._silent("phase", "verify", slug)
        self._set_header(slug, skips="observe")
        self._set_skip_rationale(slug, "observe — no rollout to watch")
        self._silent("advance", slug)   # verify -> done, records the skip
        self._silent("gate", "HARD-STOP", slug)   # recordable from any phase

    def test_intact_rationale_not_flagged(self):
        self._skipped_task("t")
        out, _ = self._run("audit")
        self.assertNotIn("skip_rationale_missing_post_hoc", out)

    def test_deleted_rationale_flagged_measure_not_block(self):
        self._skipped_task("t")
        self._clear_skip_rationale("t")
        out, code = self._run("audit")
        self.assertIn("skip_rationale_missing_post_hoc", out)
        self.assertIn("t", out)
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------------
# M12 — TASK.fast.md.tmpl carries the scaffold; TASK.md.tmpl is untouched
# ---------------------------------------------------------------------------

class TemplateScaffoldTest(unittest.TestCase):
    def test_fast_template_has_skips_hint_and_rationale_placeholder(self):
        text = (HERE / "templates" / "TASK.fast.md.tmpl").read_text(encoding="utf-8")
        self.assertIn("skips:", text)
        self.assertIn("Skip rationale:", text)

    def test_full_template_carries_no_skips_machinery(self):
        # the skip lane is fast-template-only: the full template must never gain a
        # `skips:` header hint. (Amended @ dialect-check-and-data-vocab TESTS re-cross:
        # the original empty-git-diff guard was task-local and could not survive any
        # later legitimate full-template task — re-pinned to the invariant it protected.)
        body = (REPO_ROOT / "add-method" / "tooling" / "templates" /
                "TASK.md.tmpl").read_text(encoding="utf-8")
        self.assertNotIn("skips:", body, "skip machinery must stay fast-lane-only")


# ---------------------------------------------------------------------------
# M14 — the three engine trees + the 4th dogfood template mirror stay byte-identical
# ---------------------------------------------------------------------------

class EngineTreeParityTest(unittest.TestCase):
    def test_add_py_trees_byte_identical(self):
        present = [p for p in ADD_PY_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2)
        self.assertEqual(len({_md5(p) for p in present}), 1)

    def test_constants_trees_byte_identical(self):
        present = [p for p in CONSTANTS_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2)
        self.assertEqual(len({_md5(p) for p in present}), 1)

    def test_predicates_trees_byte_identical(self):
        present = [p for p in PREDICATES_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2)
        self.assertEqual(len({_md5(p) for p in present}), 1)

    def test_fast_template_trees_byte_identical(self):
        present = [p for p in FAST_TMPL_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2)
        self.assertEqual(len({_md5(p) for p in present}), 1)


# ---------------------------------------------------------------------------
# Reject scenarios
# ---------------------------------------------------------------------------

class RejectPathsTest(_Harness):
    def test_malformed_token_refused_as_whole_not_partially_honored(self):
        self._new_fast_task("t", fast=True)
        self._silent("phase", "specify", "t")
        self._set_header("t", skips="scenarios,build")
        before = self._state()
        out, code = self._run("advance", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("skip_not_allowed", out)
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "specify")
        self.assertNotIn("skips", self._state()["tasks"]["t"])
        self.assertEqual(self._state(), before)

    def test_lane_ineligible_declaration_refused(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "t", "--title", "F")   # NOT fast/oneshot
        self._silent("phase", "specify", "t")
        self._set_header("t", skips="scenarios")
        out, code = self._run("advance", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("skip_lane_required", out)
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "specify")

    def test_missing_rationale_refused(self):
        self._new_fast_task("t", fast=True)
        self._silent("phase", "specify", "t")
        self._set_header("t", skips="scenarios")
        out, code = self._run("advance", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("skip_reason_missing", out)
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "specify")
        self.assertNotIn("skips", self._state()["tasks"]["t"])

    def test_unskippable_phase_name_refused_via_same_code(self):
        self._new_fast_task("t", fast=True)
        self._silent("phase", "specify", "t")
        self._set_header("t", skips="build")
        out, code = self._run("advance", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("skip_not_allowed", out)


# ---------------------------------------------------------------------------
# Floor composition — --oneshot + security sensitivity still needs a human freeze;
# the skip axis is unaffected (edge case)
# ---------------------------------------------------------------------------

class FloorCompositionTest(_Harness):
    def test_oneshot_security_task_skip_fires_but_freeze_stays_human(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "risky", "--title", "F", "--oneshot")
        self._set_header("risky", skips="scenarios,observe")
        p = self._task_md("risky")
        t = p.read_text(encoding="utf-8")
        t = re.sub(r"(?m)^(autonomy:[^\n]*)$", r"\1\nsensitivity: security", t, count=1)
        p.write_text(t, encoding="utf-8")
        self._set_skip_rationale("risky", "scenarios — a; observe — b")
        self._silent("phase", "specify", "risky")
        self._silent("advance", "risky")   # specify -> contract (scenarios skip fires, recorded)
        self.assertEqual(self._state()["tasks"]["risky"]["phase"], "contract")
        self.assertEqual(len(self._state()["tasks"]["risky"]["skips"]), 1)
        # AI freeze attempt is blocked (task2's unchanged floor)
        body = ("\n```\nGET /x\n  200 -> {ok:true}\n```\n\n"
                "Least-sure flag surfaced at freeze:\n  ⚠ [contract] x — cost: y.\nStatus: DRAFT\n"
                "\n### AI-verify record (required when gate_mode: ai-plan-verify)\n"
                "- [x] §0 GROUND anchors resolve in the current tree\n"
                "- [x] §1 every Must + every Reject present, each Reject paired with an error code\n"
                "- [x] §3 CONTRACT shape is concrete (no template placeholder text remains)\n"
                "- [x] Lowest-confidence flag surfaced and substantive\n"
                "Verified by: agent:x · at: 2026-07-09T00:00:00Z\n")
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(## 3 · CONTRACT[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        p.write_text(new, encoding="utf-8")
        self._fill_boundary("risky")
        out, code = self._run("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertNotEqual(code, 0)
        self.assertIn("ai_freeze_blocked_sensitivity", out)
        # the human path still works, and the earlier skip record is untouched
        self._silent("freeze", "--by", "A Human")
        st = self._state()["tasks"]["risky"]
        self.assertRegex(self._silent("status", "--section", "3"), r"Status:\s*FROZEN")
        self.assertEqual(len(st["skips"]), 1)
        self.assertEqual(st["skips"][0]["phase"], "scenarios")


# ---------------------------------------------------------------------------
# Normal flow — a task with no skips: line behaves exactly as today at every crossing
# ---------------------------------------------------------------------------

class NormalFlowUnchangedTest(_Harness):
    def test_plain_task_visits_scenarios_and_observe_every_crossing(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "t", "--title", "F")   # full-lane, no fast/oneshot
        self._silent("advance", "t")    # ground -> specify
        self._silent("advance", "t")    # specify -> scenarios
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "scenarios")
        self.assertNotIn("skips", self._state()["tasks"]["t"])
        # freeze the contract to cross scenarios -> contract -> tests
        self._silent("advance", "t")    # scenarios -> contract
        p = self._task_md("t")
        text = p.read_text(encoding="utf-8")
        body = ("\n```\nGET /x\n  200 -> {ok:true}\n```\n\n"
                "Least-sure flag surfaced at freeze:\n  ⚠ [contract] x — cost: y.\nStatus: DRAFT\n")
        new = re.sub(r"(## 3 · CONTRACT[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        p.write_text(new, encoding="utf-8")
        self._silent("freeze", "--by", "Human")
        self._silent("advance", "t")    # contract -> tests
        self._silent("advance", "t")    # tests -> build
        self._silent("advance", "t")    # build -> verify
        self._silent("advance", "t")    # verify -> observe
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "observe")
        self.assertNotIn("skips", self._state()["tasks"]["t"])
        self._silent("advance", "t")    # observe -> done
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")
        self.assertNotIn("skips", self._state()["tasks"]["t"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
