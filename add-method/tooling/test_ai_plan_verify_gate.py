#!/usr/bin/env python3
"""Red/green tests for ai-plan-verify-gate (task: ai-plan-verify-gate, milestone: three-phase-flow).

CONTRACT (frozen @ v1, §3 of .add/tasks/ai-plan-verify-gate/TASK.md): a two-way DIRECTION-freeze
gate `gate_mode: human | ai-plan-verify`. When a task declares `gate_mode: ai-plan-verify`, its
EFFECTIVE autonomy is `auto`, and its sensitivity is NOT `security`/`data`/`architecture` (a
malformed "?" token also refused) — an AI agent may perform the §3 contract freeze via
`add.py freeze --ai-plan-verify --by AGENT_ID`, IF the §3 "AI-verify record" checklist (4 items
+ Verified by:) is complete. A BLOCK-list (not an allow-list of one): undeclared sensitivity,
"mechanical", and any other valid project-GLOSSARY class all qualify.

  add_engine/constants.py  _GATE_MODES = ("human", "ai-plan-verify")           — joins __all__
  add.py                   _task_gate_mode(hdr) -> str | None                   — mirrors _task_sensitivity
  add_engine/predicates.py _ai_freeze_allowed(gate_mode, sensitivity, autonomy) -> (bool, str|None)
  add.py cmd_freeze        --ai-plan-verify + --by AGENT_ID additive branch
  add.py                   _ai_verify_slice / _ai_verify_checklist_complete    — mirrors _advisor_slice
  add.py cmd_audit         ai_freeze_checklist_missing residual glint (MEASURE-NOT-BLOCK)
  add.py _gate_explain     one additive print line when gate_mode: ai-plan-verify

The flagless human path (`add.py freeze --by NAME`) is BYTE-IDENTICAL to before this task.

Run: cd add-method/tooling && python3 -m unittest test_ai_plan_verify_gate -v
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
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


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


# a real drafted §3 body (no template placeholders), well-formed flag included
_DRAFT_FLAGGED = (
    "\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\n"
    "Status: DRAFT\n"
    "Least-sure flag surfaced at freeze:\n"
    "  ⚠ [contract] the id encoding is the least-sure part — cost if wrong: a reparse.\n"
)
_DRAFT_NOFLAG = (
    "\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\nStatus: DRAFT\n"
)

_AI_RECORD_COMPLETE = (
    "\n### AI-verify record (required when gate_mode: ai-plan-verify)\n"
    "- [x] §0 GROUND anchors resolve in the current tree\n"
    "- [x] §1 every Must + every Reject present, each Reject paired with an error code\n"
    "- [x] §3 CONTRACT shape is concrete (no template placeholder text remains)\n"
    "- [x] Least-sure flag surfaced and substantive (mirrors unflagged_freeze's own bar)\n"
    "Verified by: agent:add-design · at: 2026-07-09T00:00:00Z\n"
)
_AI_RECORD_INCOMPLETE = (
    "\n### AI-verify record (required when gate_mode: ai-plan-verify)\n"
    "- [ ] §0 GROUND anchors resolve in the current tree\n"
    "- [x] §1 every Must + every Reject present, each Reject paired with an error code\n"
    "- [x] §3 CONTRACT shape is concrete (no template placeholder text remains)\n"
    "- [x] Least-sure flag surfaced and substantive (mirrors unflagged_freeze's own bar)\n"
    "Verified by: agent:add-design · at: 2026-07-09T00:00:00Z\n"
)


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-aipv-")).resolve()
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

    def _section3(self, slug):
        return add._phase_spans(self._task_md(slug).read_text(encoding="utf-8")).get(3, "")

    def _set_section3(self, slug, body):
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(## 3 · CONTRACT[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        p.write_text(new, encoding="utf-8")

    def _set_header(self, slug, **kv):
        """Insert/replace `gate_mode:`/`sensitivity:`/`autonomy:` header lines."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        for key in ("autonomy", "gate_mode", "sensitivity"):
            if key not in kv:
                continue
            val = kv[key]
            pattern = rf"(?m)^{key}:.*$"
            if re.search(pattern, t):
                t = re.sub(pattern, f"{key}: {val}", t, count=1)
            else:
                t = re.sub(r"(?m)^(autonomy:[^\n]*)$", rf"\1\n{key}: {val}", t, count=1)
        p.write_text(t, encoding="utf-8")

    def _new_task_at_contract(self, slug="t", drafted=_DRAFT_FLAGGED, ai_record=None, **hdr):
        """Lock, a milestone + task, jump to `contract`, replace §3 with `drafted` (+ optional
        AI-verify record block), and declare any header fields (gate_mode/sensitivity/autonomy)."""
        self._silent("lock", "--force")
        if "m" not in self._state().get("milestones", {}):
            self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", slug, "--title", "Feature")
        if hdr:
            self._set_header(slug, **hdr)
        self._silent("phase", "contract", slug)
        if drafted is not None:
            body = drafted + (ai_record or "")
            self._set_section3(slug, body)


# ---------------------------------------------------------------------------
# M1 — _GATE_MODES closed 2-tuple, importable, listed in __all__
# ---------------------------------------------------------------------------

class GateModesConstantTest(unittest.TestCase):
    def test_value_and_all(self):
        self.assertEqual(engine_constants._GATE_MODES, ("human", "ai-plan-verify"))
        self.assertIn("_GATE_MODES", engine_constants.__all__)

    def test_importable_via_star_import(self):
        self.assertTrue(hasattr(add, "_GATE_MODES"),
                        "add.py must re-export _GATE_MODES via `from add_engine.constants import *`")
        self.assertEqual(add._GATE_MODES, engine_constants._GATE_MODES)


# ---------------------------------------------------------------------------
# M2 — _task_gate_mode resolves declared / absent / unknown
# ---------------------------------------------------------------------------

class TaskGateModeResolverTest(unittest.TestCase):
    def test_declared_token(self):
        self.assertEqual(add._task_gate_mode("gate_mode: ai-plan-verify\n"), "ai-plan-verify")

    def test_absent_returns_none(self):
        self.assertIsNone(add._task_gate_mode("slug: t · created: x\nautonomy: auto\n"))

    def test_unknown_token_returns_qmark(self):
        self.assertEqual(add._task_gate_mode("gate_mode: bogus\n"), "?")

    def test_inline_slug_line_form(self):
        self.assertEqual(add._task_gate_mode("slug: t · gate_mode: ai-plan-verify · risk: high\n"),
                         "ai-plan-verify")


# ---------------------------------------------------------------------------
# M3 — _ai_freeze_allowed: the BLOCK-list predicate
# ---------------------------------------------------------------------------

class AiFreezeAllowedPredicateTest(unittest.TestCase):
    def test_permits_undeclared_sensitivity(self):
        self.assertEqual(add._ai_freeze_allowed("ai-plan-verify", None, "auto"), (True, None))

    def test_permits_mechanical(self):
        self.assertEqual(add._ai_freeze_allowed("ai-plan-verify", "mechanical", "auto"), (True, None))

    def test_permits_other_valid_project_class(self):
        self.assertEqual(add._ai_freeze_allowed("ai-plan-verify", "compliance", "auto"), (True, None))

    def test_blocks_human_mode(self):
        self.assertEqual(add._ai_freeze_allowed(None, "mechanical", "auto"),
                         (False, "ai_freeze_not_opted_in"))
        self.assertEqual(add._ai_freeze_allowed("human", "mechanical", "auto"),
                         (False, "ai_freeze_not_opted_in"))

    def test_blocks_non_auto_autonomy_regardless_of_sensitivity(self):
        self.assertEqual(add._ai_freeze_allowed("ai-plan-verify", None, "conservative"),
                         (False, "ai_freeze_requires_auto"))
        self.assertEqual(add._ai_freeze_allowed("ai-plan-verify", "security", "conservative"),
                         (False, "ai_freeze_requires_auto"))

    def test_blocks_every_human_floor_sensitivity(self):
        for sens in ("security", "data", "architecture"):
            with self.subTest(sens=sens):
                self.assertEqual(add._ai_freeze_allowed("ai-plan-verify", sens, "auto"),
                                 (False, "ai_freeze_blocked_sensitivity"))

    def test_fails_closed_on_malformed_sensitivity(self):
        self.assertEqual(add._ai_freeze_allowed("ai-plan-verify", "?", "auto"),
                         (False, "ai_freeze_unknown_sensitivity"))

    def test_predicate_lives_in_engine_predicates_module(self):
        # engine-modularization discipline: add.py re-exports, predicates.py owns it
        self.assertIs(add._ai_freeze_allowed, engine_predicates._ai_freeze_allowed)


# ---------------------------------------------------------------------------
# M4 — cmd_freeze --ai-plan-verify writes the AI freeze record on a qualifying task
# ---------------------------------------------------------------------------

class CmdFreezeAiPathHappyTest(_Harness):
    def test_writes_status_and_freeze_mode_line_and_state(self):
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="mechanical",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        self._silent("freeze", "--ai-plan-verify", "--by", "agent:add-design")
        raw3 = self._section3("t")
        self.assertRegex(raw3, r"Status:\s*FROZEN @ v1 — approved by agent:add-design")
        self.assertRegex(raw3, r"Freeze mode:\s*ai-plan-verify — verified by agent:add-design at \S+")
        # the additive line sits directly beneath Status
        lines = [ln for ln in raw3.splitlines() if ln.strip()]
        status_idx = next(i for i, ln in enumerate(lines) if ln.strip().startswith("Status:"))
        self.assertTrue(lines[status_idx + 1].strip().startswith("Freeze mode:"))
        rec = self._state()["tasks"]["t"]["freeze"]
        self.assertEqual(rec["mode"], "ai-plan-verify")
        self.assertEqual(rec["verified"], {"anchors": True, "rules": True, "shape": True, "flag": True})
        self.assertEqual(rec["approved_by"], "agent:add-design")
        self.assertTrue(add._contract_frozen(raw3))

    def test_undeclared_sensitivity_qualifies(self):
        # the common oneshot/benchmark case: no sensitivity: line at all
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", autonomy="auto",
                                   ai_record=_AI_RECORD_COMPLETE)
        self._silent("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1")


# ---------------------------------------------------------------------------
# M5 — the human freeze path is untouched (byte-identical, no mode key)
# ---------------------------------------------------------------------------

class HumanFreezePathUnchangedTest(_Harness):
    def test_human_path_unaffected_by_gate_mode_declaration(self):
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="mechanical",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        self._silent("freeze", "--by", "A Human")
        raw3 = self._section3("t")
        self.assertRegex(raw3, r"Status:\s*FROZEN @ v1 — approved by A Human")
        self.assertNotIn("Freeze mode:", raw3)
        rec = self._state()["tasks"]["t"]["freeze"]
        self.assertNotIn("mode", rec)
        self.assertNotIn("verified", rec)

    def test_plain_freeze_no_flag_matches_pre_existing_behavior(self):
        # regression: the exact assertions test_freeze_command.py's happy path makes
        self._new_task_at_contract("t")
        self._silent("freeze", "--by", "Ada")
        raw3 = self._section3("t")
        self.assertRegex(raw3, r"Status:\s*FROZEN @ v1 — approved by Ada")
        self.assertNotIn("Freeze mode:", raw3)
        rec = self._state()["tasks"]["t"]["freeze"]
        self.assertEqual(rec["version"], "v1")
        self.assertEqual(rec["approved_by"], "Ada")
        self.assertNotIn("mode", rec)


# ---------------------------------------------------------------------------
# M6 — the AI-verify record block is read/validated like the advisor 3-lens slice
# ---------------------------------------------------------------------------

class AiVerifySliceAndChecklistTest(unittest.TestCase):
    def test_complete_checklist_true(self):
        raw3 = _DRAFT_FLAGGED + _AI_RECORD_COMPLETE
        self.assertTrue(add._ai_verify_checklist_complete(raw3))
        slc = add._ai_verify_slice(raw3)
        self.assertTrue(slc.startswith("### AI-verify record"))
        self.assertIn("Verified by:", slc)
        self.assertNotIn("Status: DRAFT", slc)   # heading-bounded — text BEFORE the block excluded

    def test_incomplete_checklist_false(self):
        raw3 = _DRAFT_FLAGGED + _AI_RECORD_INCOMPLETE
        self.assertFalse(add._ai_verify_checklist_complete(raw3))

    def test_absent_block_is_fail_safe_empty_and_false(self):
        self.assertEqual(add._ai_verify_slice(_DRAFT_FLAGGED), "")
        self.assertFalse(add._ai_verify_checklist_complete(_DRAFT_FLAGGED))

    def test_empty_verified_by_is_incomplete(self):
        raw3 = _DRAFT_FLAGGED + _AI_RECORD_COMPLETE.replace(
            "Verified by: agent:add-design · at: 2026-07-09T00:00:00Z\n", "Verified by:\n")
        self.assertFalse(add._ai_verify_checklist_complete(raw3))


# ---------------------------------------------------------------------------
# M7 — audit flags a post-freeze deleted/mangled AI-verify record
# ---------------------------------------------------------------------------

class AuditChecklistMissingTest(_Harness):
    def _ai_frozen_task(self, slug="t"):
        self._new_task_at_contract(slug, gate_mode="ai-plan-verify", sensitivity="mechanical",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        self._silent("freeze", "--ai-plan-verify", "--by", "agent:x")
        # HARD-STOP is recordable from any phase — no need to drive through verify's full gate
        self._silent("gate", "HARD-STOP", slug)

    def test_intact_record_not_flagged(self):
        self._ai_frozen_task("t")
        out, _ = self._run("audit")
        self.assertNotIn("ai_freeze_checklist_missing", out)

    def test_mangled_record_flagged_measure_not_block(self):
        self._ai_frozen_task("t")
        # simulate a post-freeze hand-edit that unchecks an item
        p = self._task_md("t")
        t = p.read_text(encoding="utf-8").replace(
            "- [x] §0 GROUND anchors resolve in the current tree",
            "- [ ] §0 GROUND anchors resolve in the current tree", 1)
        p.write_text(t, encoding="utf-8")
        out, code = self._run("audit")
        self.assertIn("ai_freeze_checklist_missing", out)
        self.assertIn("t", out)
        # MEASURE-NOT-BLOCK means the ENGINE GATE is never refused for this finding — it does
        # NOT mean `add.py audit`'s own exit code is untouched: findings (like the sibling
        # unflagged_freeze) flip audit's exit code to 1, the CI-consumed signal (audit-ci).
        self.assertEqual(code, 1, "audit's own exit code flips on a real finding, same as "
                         "the sibling unflagged_freeze residual check")

    def test_deleted_block_flagged(self):
        self._ai_frozen_task("t")
        p = self._task_md("t")
        t = re.sub(r"### AI-verify record.*?(?=\n---)", "", p.read_text(encoding="utf-8"), flags=re.S)
        p.write_text(t, encoding="utf-8")
        out, _ = self._run("audit")
        self.assertIn("ai_freeze_checklist_missing", out)

    def test_human_freeze_never_flagged(self):
        self._new_task_at_contract("t")
        self._silent("freeze", "--by", "A Human")
        self._silent("gate", "HARD-STOP", "t")
        out, _ = self._run("audit")
        self.assertNotIn("ai_freeze_checklist_missing", out)

    def test_json_findings_carry_the_code(self):
        self._ai_frozen_task("t")
        p = self._task_md("t")
        t = p.read_text(encoding="utf-8").replace(
            "- [x] §1 every Must + every Reject present, each Reject paired with an error code",
            "- [ ] §1 every Must + every Reject present, each Reject paired with an error code", 1)
        p.write_text(t, encoding="utf-8")
        out, _ = self._run("audit", "--json")
        data = json.loads(out)
        codes = [f["code"] for f in data["findings"]]
        self.assertIn("ai_freeze_checklist_missing", codes)


# ---------------------------------------------------------------------------
# M8 — gate-explain surfaces the AI-plan-verify-gate predicate outcome
# ---------------------------------------------------------------------------

class GateExplainAiPlanVerifyTest(_Harness):
    def test_allowed_outcome_printed(self):
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")
        self._set_header("t", gate_mode="ai-plan-verify", sensitivity="mechanical", autonomy="auto")
        out = self._silent("gate", "--explain", "t")
        self.assertIn("ai-plan-verify-gate: allowed", out)
        # the existing advisor-gate-relax line is unchanged and still printed
        self.assertIn("advisor-gate-relax:", out)

    def test_blocked_outcome_printed_with_code(self):
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")
        self._set_header("t", gate_mode="ai-plan-verify", sensitivity="security", autonomy="auto")
        out = self._silent("gate", "--explain", "t")
        self.assertIn("ai-plan-verify-gate: blocked (ai_freeze_blocked_sensitivity)", out)

    def test_human_mode_task_prints_no_ai_plan_verify_line(self):
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")
        out = self._silent("gate", "--explain", "t")
        self.assertNotIn("ai-plan-verify-gate:", out)

    def test_read_only(self):
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")
        self._set_header("t", gate_mode="ai-plan-verify", sensitivity="mechanical", autonomy="auto")
        state_file = self.tmp / ".add" / "state.json"
        before = state_file.read_bytes()
        self._silent("gate", "--explain", "t")
        self.assertEqual(before, state_file.read_bytes(), "--explain writes NOTHING")


# ---------------------------------------------------------------------------
# Reject scenarios
# ---------------------------------------------------------------------------

class RejectPathsTest(_Harness):
    def test_missing_by_refuses_before_any_write(self):
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="mechanical",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        before = self._state()
        out, code = self._run("freeze", "--ai-plan-verify")
        self.assertNotEqual(code, 0)
        self.assertIn("ai_freeze_missing_actor", out)
        self.assertNotRegex(self._section3("t"), r"Status:\s*FROZEN")
        self.assertEqual(self._state(), before)

    def test_incomplete_checklist_refuses(self):
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="mechanical",
                                   autonomy="auto", ai_record=_AI_RECORD_INCOMPLETE)
        out, code = self._run("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertNotEqual(code, 0)
        self.assertIn("ai_freeze_checklist_incomplete", out)
        self.assertNotRegex(self._section3("t"), r"Status:\s*FROZEN")

    def test_preexisting_checks_still_fire_unchanged_on_ai_path(self):
        # no well-formed flag -> unflagged_freeze, the SAME code the human path uses;
        # no AI-specific check (opted-in/autonomy/sensitivity/checklist) is even reached
        self._new_task_at_contract("t", drafted=_DRAFT_NOFLAG, gate_mode="ai-plan-verify",
                                   sensitivity="mechanical", autonomy="auto")
        out, code = self._run("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertNotEqual(code, 0)
        self.assertIn("unflagged_freeze", out)

    def test_gate_mode_declared_never_forces_ai_path_or_blocks_human_path(self):
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="architecture")
        self._silent("freeze", "--by", "A Human")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1 — approved by A Human")

    def test_security_sensitivity_doubly_blocked_at_freeze(self):
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="security",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        out, code = self._run("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertNotEqual(code, 0)
        self.assertIn("ai_freeze_blocked_sensitivity", out)
        # the human path still works for this task
        self._silent("freeze", "--by", "A Human")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1 — approved by A Human")

    def test_refreeze_after_change_request_revalidates_from_scratch(self):
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="mechanical",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        self._silent("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertEqual(self._state()["tasks"]["t"]["freeze"]["version"], "v1")
        # change-request: revert §3 to a flagged DRAFT + a fresh complete AI-verify record
        self._set_section3("t", _DRAFT_FLAGGED + _AI_RECORD_COMPLETE)
        self._silent("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v2")
        self.assertEqual(self._state()["tasks"]["t"]["freeze"]["version"], "v2")
        self.assertEqual(self._state()["tasks"]["t"]["freeze"]["mode"], "ai-plan-verify")

    def test_refreeze_reevaluates_and_can_now_refuse(self):
        # v1 froze fine; a change request lowers autonomy before the v2 attempt -> refused,
        # proving nothing is grandfathered from the v1 approval.
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="mechanical",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        self._silent("freeze", "--ai-plan-verify", "--by", "agent:x")
        self._set_section3("t", _DRAFT_FLAGGED + _AI_RECORD_COMPLETE)
        self._set_header("t", autonomy="conservative")
        out, code = self._run("freeze", "--ai-plan-verify", "--by", "agent:x")
        self.assertNotEqual(code, 0)
        self.assertIn("ai_freeze_requires_auto", out)


# ---------------------------------------------------------------------------
# M9 — v2 amendment (2026-07-09, change request): on the --ai-plan-verify path the generic
# "?" guard is SKIPPED so a malformed sensitivity token routes to _ai_freeze_allowed's OWN
# "ai_freeze_unknown_sensitivity" code instead of the human path's "sensitivity_invalid" —
# an END-TO-END real-subprocess CLI test (not the in-process add.main() harness) per the
# change request's explicit ask, so the assertion exercises the literal shipped `add.py`
# entry point, argv parsing, and process exit code — not just the in-process call surface.
# ---------------------------------------------------------------------------

class MalformedSensitivityAiPathE2eTest(_Harness):
    def _freeze_subprocess(self, *extra_args):
        return subprocess.run(
            [sys.executable, str(HERE / "add.py"), "freeze", *extra_args],
            cwd=self.tmp, capture_output=True, text=True)

    def test_ai_path_malformed_sensitivity_yields_distinct_code_via_real_cli(self):
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="boguz",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        before_state = self._state()
        proc = self._freeze_subprocess("--ai-plan-verify", "--by", "agent:x")
        combined = proc.stdout + proc.stderr
        self.assertNotEqual(proc.returncode, 0,
                             f"expected a nonzero exit; got 0. output: {combined!r}")
        self.assertIn("ai_freeze_unknown_sensitivity", combined)
        self.assertNotIn("sensitivity_invalid", combined,
                          "the AI path must route through its OWN error code, not borrow "
                          "the human path's sensitivity_invalid")
        # validate-then-write: the malformed-token refusal must precede any write
        self.assertNotRegex(self._section3("t"), r"Status:\s*FROZEN")
        self.assertEqual(self._state(), before_state)

    def test_human_path_same_malformed_token_still_yields_sensitivity_invalid(self):
        # the SAME malformed token on the HUMAN (flagless) path must still hit the
        # pre-existing, unchanged sensitivity_invalid guard — proves the v2 amendment only
        # ever reorders/reguards the AI branch, never the human one.
        self._new_task_at_contract("t", sensitivity="boguz")
        proc = self._freeze_subprocess("--by", "A Human")
        combined = proc.stdout + proc.stderr
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("sensitivity_invalid", combined)
        self.assertNotIn("ai_freeze_unknown_sensitivity", combined)
        self.assertNotRegex(self._section3("t"), r"Status:\s*FROZEN")

    def test_ai_path_valid_nonfloor_token_still_freezes_via_real_cli(self):
        # confirms a VALID non-floor token (mechanical) still AI-freezes end-to-end, unaffected
        # by the reordering — the in-process CmdFreezeAiPathHappyTest covers this too; this is
        # the real-subprocess twin for the same v2-amended code path.
        self._new_task_at_contract("t", gate_mode="ai-plan-verify", sensitivity="mechanical",
                                   autonomy="auto", ai_record=_AI_RECORD_COMPLETE)
        proc = self._freeze_subprocess("--ai-plan-verify", "--by", "agent:x")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1 — approved by agent:x")


# ---------------------------------------------------------------------------
# M10 — the three engine trees stay byte-identical
# ---------------------------------------------------------------------------

class EngineTreeParityTest(unittest.TestCase):
    def test_add_py_trees_byte_identical(self):
        present = [p for p in ADD_PY_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2)
        self.assertEqual(len({_md5(p) for p in present}), 1, "add.py diverged across engine trees")

    def test_constants_trees_byte_identical(self):
        present = [p for p in CONSTANTS_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2)
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "add_engine/constants.py diverged across engine trees")

    def test_predicates_trees_byte_identical(self):
        present = [p for p in PREDICATES_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2)
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "add_engine/predicates.py diverged across engine trees")


if __name__ == "__main__":
    unittest.main(verbosity=2)
