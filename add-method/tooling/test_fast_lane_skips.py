#!/usr/bin/env python3
"""Tests for the RETIRED fast-lane skip grammar (fast-lane-skips shipped it; the two
six-phase-loop merges retired it — first scenarios, then observe left PHASES, and with
them _SKIPPABLE_PHASES emptied). What survives, pinned here:

  _SKIPPABLE_PHASES = ()          — nothing is skippable; no crossing runs skip logic
  _task_skip_set                  — resolver kept for read-tolerance: retired tokens filter
                                    to the empty set; a truly bad token still errs
  cmd_gate (completion)           — the ONE seam that reads a vestigial `skips:` header:
                                    one loud advisory note, never a die
  status/guide + audit            — historic boards with RECORDED skips keep their surface
                                    (the line renders; a deleted rationale still audits)
  templates                       — NEITHER template scaffolds the skip grammar anymore
  --oneshot / benchmark_mode      — the lane flags live on (unrelated to skipping)

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
    # 3-tree parity (canon · repo-root dogfood · bundled) — mirrors test_plan_phase_flow.py's
    # ADD_PY_COPIES/TMPL_COPIES convention. The 4th, add-method's OWN nested `.add/` dogfood
    # copy, is gitignored local scratch state for add-method's self-hosted task tracking; it
    # is not part of the shipped-artifact parity claim (its currency depends on whether that
    # local dogfood task has itself been advanced), so it is deliberately excluded here.
    HERE / "templates" / "PLAN.fast.md.tmpl",
    REPO_ROOT / ".add" / "tooling" / "templates" / "PLAN.fast.md.tmpl",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.fast.md.tmpl",
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
        return self.tmp / ".add" / "tasks" / slug / "PLAN.md"

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
        self._silent(*argv)
        if oneshot:
            # atomic-node: gate_mode is declared in the artifact header, not a CLI flag
            md = self._task_md(slug)
            md.write_text(md.read_text(encoding="utf-8").replace(
                "phase: direction", "gate_mode: ai-plan-verify\nphase: direction", 1),
                encoding="utf-8")

    def _set_section3_and_freeze(self, slug):
        # phase-collapse-3: a fresh task is BORN at `direction` — draft + freeze §3
        # right there, straight into the ONE direction->build crossing.
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        body = ("\n```\nGET /x\n  200 -> {ok:true}\n```\n\n"
                "Least-sure flag surfaced at freeze:\n"
                "  ⚠ [contract] x — cost: y.\n"
                "Status: DRAFT\n")
        new = re.sub(r"(## 3 · PLAN[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        p.write_text(new, encoding="utf-8")
        self._fill_boundary(slug)
        self._silent("freeze", "--by", "Human")


# ---------------------------------------------------------------------------
# M1 — _SKIPPABLE_PHASES closed 2-tuple, importable, listed in __all__
# ---------------------------------------------------------------------------

class SkippablePhasesConstantTest(unittest.TestCase):
    def test_value_and_all(self):
        self.assertEqual(engine_constants._SKIPPABLE_PHASES, ())
        # phase-merge-verify: observe left the tuple too — nothing is skippable
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

    def test_retired_token_filtered_from_csv(self):
        # phase-merge-verify: BOTH pre-merge tokens are retired — the set is empty
        self.assertEqual(add._task_skip_set("skips: scenarios,observe\n"),
                         (frozenset(), None))

    def test_observe_token_retired_resolves_empty(self):
        self.assertEqual(add._task_skip_set("skips: observe\n"),
                         (frozenset(), None))

    def test_retired_only_declaration_resolves_empty(self):
        self.assertEqual(add._task_skip_set("skips: scenarios\n"),
                         (frozenset(), None))

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
class CmdAdvanceSkipMechanicTest(_Harness):
    def test_retired_declaration_never_touches_a_crossing(self):
        # phase-collapse-3: NO crossing runs skip logic; a vestigial declaration (either
        # retired token) is invisible to advance and records nothing, across all 3 remaining
        # crossings (direction->build, build->verify, verify->done).
        self._new_fast_task("t", fast=True)
        self._set_header("t", skips="scenarios,observe")
        self._set_section3_and_freeze("t")
        out = self._silent("advance", "t")                 # direction -> build, silent
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "build")
        self.assertNotIn("skips", self._state()["tasks"]["t"])
        self.assertNotIn("note:", out, "crossings stay silent — the note lives at gate")
        self._silent("phase", "verify", "t")
        out = self._silent("advance", "t")                 # verify -> done, silent
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")
        self.assertNotIn("skips", self._state()["tasks"]["t"])
        self.assertNotIn("note:", out, "crossings stay silent — the note lives at gate")

    def test_vestigial_declaration_noted_loud_at_gate(self):
        # the ONE seam that reads the header: gate/completion (where the ADR
        # harvest + fold nudge already live).
        self._new_fast_task("t", fast=True)
        self._set_header("t", skips="observe")
        self._silent("phase", "verify", "t")
        out = self._silent("gate", "PASS", "t")
        self.assertIn("retired", out)
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")
        self.assertNotIn("skips", self._state()["tasks"]["t"])


# ---------------------------------------------------------------------------
# M6 / M13 (generalized by phase-merge-verify) — EVERY crossing runs zero skip logic
# ---------------------------------------------------------------------------

class NonSkippableCrossingsUntouchedTest(_Harness):
    def _advance_spy_count(self, slug="t"):
        from unittest import mock
        with mock.patch.object(add, "_task_skip_set", wraps=add._task_skip_set) as spy:
            self._silent("advance", slug)
            return spy.call_count

    def test_every_crossing_never_invokes_task_skip_set(self):
        # phase-collapse-3: the front collapsed into ONE phase (`direction`), so the flow is
        # direction -> build -> verify -> done — 3 crossings total, ALL of them run ZERO skip
        # logic (the old M13 pin, now universal; the header is read once, at gate, not here).
        self._new_fast_task("t", fast=True)   # no skips: declared anywhere
        self._set_section3_and_freeze("t")
        self.assertEqual(self._advance_spy_count(), 0, "direction->build")
        self.assertEqual(self._advance_spy_count(), 0, "build->verify")
        self.assertEqual(self._advance_spy_count(), 0, "verify->done")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")


# ---------------------------------------------------------------------------
# M7 retired (atomic-node): the --oneshot/--fast scaffolds are gone — gate_mode
# is a header declaration and the template is ONE atomic render for every task.
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
    def test_historic_recorded_skip_keeps_its_status_surface(self):
        # No live path records a skip anymore; a HISTORIC board (pre-merge) may
        # still carry one — its status/guide line must keep rendering (read-tolerance).
        self._new_fast_task("t", fast=True)
        sp = self.tmp / ".add" / "state.json"
        raw = json.loads(sp.read_text(encoding="utf-8"))
        raw["tasks"]["t"]["oneshot"] = True   # legacy lane marker (historic board)
        raw["tasks"]["t"]["skips"] = [{"phase": "observe", "reason": "historic",
                                       "by": "Tester", "at": "2026-01-01T00:00:00Z"}]
        sp.write_text(json.dumps(raw), encoding="utf-8")
        out_status = self._silent("status")
        out_guide = self._silent("guide")
        for out in (out_status, out_guide):
            self.assertIn("skipped so far 1/", out)

    def test_no_declaration_no_recorded_skip_prints_no_line(self):
        self._new_fast_task("t", fast=True)
        out = self._silent("status")
        self.assertNotIn("skips   :", out)


# ---------------------------------------------------------------------------
# M10 — gate-explain surfaces the skip-set predicate outcome
# ---------------------------------------------------------------------------

class GateExplainSkipSetTest(_Harness):
    def test_vestigial_declaration_prints_no_skip_set_line(self):
        # a retired-token declaration resolves to the empty set — gate-explain
        # shows no skip-set line (there is no live skip mechanism to explain)
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")   # NOT fast/oneshot
        self._set_header("t", skips="observe")
        out = self._silent("gate", "--explain", "t")
        self.assertNotIn("skip-set:", out)
        # the surrounding explain surface never crashes / interferes
        self.assertIn("advisor-gate-relax:", out)

    def test_no_declaration_prints_no_skip_set_line(self):
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")
        out = self._silent("gate", "--explain", "t")
        self.assertNotIn("skip-set:", out)
class TemplateScaffoldTest(unittest.TestCase):
    def test_full_template_carries_no_skips_machinery(self):
        # (pre-dates the retirement: the full template NEVER carried the grammar)
        body = (REPO_ROOT / "add-method" / "tooling" / "templates" /
                "PLAN.md.tmpl").read_text(encoding="utf-8")
        self.assertNotIn("skips:", body)


# ---------------------------------------------------------------------------
# M14 — the three engine trees + the 4th dogfood template mirror stay byte-identical
# ---------------------------------------------------------------------------

class EngineTreeParityTest(unittest.TestCase):


    def test_fast_template_gone_from_every_tree(self):
        # template-unify: the fast lane derives from PLAN.md.tmpl — no tree may
        # resurrect the deleted PLAN.fast.md.tmpl
        for p in FAST_TMPL_TREES:
            self.assertFalse(p.exists(), f"PLAN.fast.md.tmpl must stay deleted: {p}")


# ---------------------------------------------------------------------------
# Reject scenarios
# ---------------------------------------------------------------------------

class RejectPathsTest(_Harness):
    # The advance-time refusals died with the grammar; what survives is (a) the
    # resolver still names a truly bad token (TaskSkipSetResolverTest above) and
    # (b) NO declaration — malformed, ineligible, or unskippable — can block or
    # alter a crossing anymore; the loud surface is the single gate note.
    def test_malformed_declaration_cannot_block_a_crossing(self):
        self._new_fast_task("t", fast=True)
        self._silent("phase", "verify", "t")
        self._set_header("t", skips="observe,build")
        out, code = self._run("advance", "t")
        self.assertEqual(code, 0, f"the retired grammar must never die at advance: {out}")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")
        self.assertNotIn("skips", self._state()["tasks"]["t"])

    def test_unskippable_token_noted_at_gate_not_died(self):
        self._new_fast_task("t", fast=True)
        self._set_header("t", skips="build")
        self._silent("phase", "verify", "t")
        out = self._silent("gate", "PASS", "t")
        self.assertIn("retired", out)
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")


# ---------------------------------------------------------------------------
# Floor composition — --oneshot + security sensitivity still needs a human freeze;
# the skip axis is unaffected (edge case)
# ---------------------------------------------------------------------------

class FloorCompositionTest(_Harness):
    def test_oneshot_security_task_freeze_stays_human(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "risky", "--title", "F")
        self._set_header("risky", skips="observe")   # vestigial — must change nothing
        p = self._task_md("risky")
        t = p.read_text(encoding="utf-8")
        t = t.replace("phase: direction", "gate_mode: ai-plan-verify\nphase: direction", 1)
        t = re.sub(r"(?m)^(autonomy:[^\n]*)$", r"\1\nsensitivity: security", t, count=1)
        p.write_text(t, encoding="utf-8")
        # phase-collapse-3: the task is BORN at `direction` — no bookkeeping crossing is
        # needed before drafting §3.
        # AI freeze attempt is blocked (task2's unchanged floor)
        body = ("\n```\nGET /x\n  200 -> {ok:true}\n```\n\n"
                "Least-sure flag surfaced at freeze:\n  ⚠ [contract] x — cost: y.\nStatus: DRAFT\n"
                "\n### AI-verify record (required when gate_mode: ai-plan-verify)\n"
                "- [x] §3 PLAN grounding anchors resolve in the current tree\n"
                "- [x] §1 every Must + every Reject present, each Reject paired with an error code\n"
                "- [x] §3 Contract shape is concrete (no template placeholder text remains)\n"
                "- [x] Lowest-confidence flag surfaced and substantive\n"
                "Verified by: agent:x · at: 2026-07-09T00:00:00Z\n")
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(## 3 · PLAN[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        p.write_text(new, encoding="utf-8")
        self._fill_boundary("risky")
        out, code = self._run("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertNotEqual(code, 0)
        self.assertIn("ai_freeze_blocked_sensitivity", out)
        # the human path still works; downstream verify -> done is the natural
        # last crossing now — no skip fires, none is recorded
        self._silent("freeze", "--by", "A Human")
        self.assertRegex(self._silent("status", "--section", "3"), r"Status:\s*FROZEN")
        self._silent("phase", "verify", "risky")
        self._silent("advance", "risky")
        st = self._state()["tasks"]["risky"]
        self.assertEqual(st["phase"], "done")
        self.assertNotIn("skips", st)


# ---------------------------------------------------------------------------
# Normal flow — a task with no skips: line behaves exactly as today at every crossing
# ---------------------------------------------------------------------------

class NormalFlowUnchangedTest(_Harness):
    def test_plain_task_visits_every_phase_every_crossing(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "t", "--title", "F")   # full-lane, no fast/oneshot; born at direction
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "direction")
        self.assertNotIn("skips", self._state()["tasks"]["t"])
        # freeze the contract to cross direction -> build (the ONE crossing)
        p = self._task_md("t")
        text = p.read_text(encoding="utf-8")
        body = ("\n```\nGET /x\n  200 -> {ok:true}\n```\n\n"
                "Least-sure flag surfaced at freeze:\n  ⚠ [contract] x — cost: y.\nStatus: DRAFT\n")
        new = re.sub(r"(## 3 · PLAN[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        # template-unify M6: the full scaffold now carries the §1 Boundary line — fill
        # it (the boundary_unfilled floor fires on both lanes at freeze)
        new = re.sub(r"(?m)^Boundary: <[^\n]*$", "Boundary: none — no external input", new)
        p.write_text(new, encoding="utf-8")
        self._silent("freeze", "--by", "Human")
        self._silent("advance", "t")    # direction -> build
        self._silent("advance", "t")    # build -> verify
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "verify")
        self.assertNotIn("skips", self._state()["tasks"]["t"])
        self._silent("advance", "t")    # verify -> done
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")
        self.assertNotIn("skips", self._state()["tasks"]["t"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
