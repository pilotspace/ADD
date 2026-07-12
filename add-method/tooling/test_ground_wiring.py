#!/usr/bin/env python3
"""Red/green tests for grounding wiring (task ground-bundle-wiring, ground-phase milestone).

Grounding is the §0 GROUND map a task gathers before it specifies. This task WIRES it
into the two seams the human and the engine watch — MEASURE, never block:

  * _grounded_state / _section0_anchors — the PURE tri-state measure
        True  = §0 "Anchors the contract cites:" line filled
        False = §0 present but the Anchors line is the "<…>" placeholder / empty
        None  = no §0 section (a pre-ground / legacy task) — EXEMPT
  * status — a human-readable `grounded:` line for the active task, ONLY when §0 exists
             (a None/legacy task prints nothing → current output byte-unchanged).
  * check  — a `task_not_grounded` WARN (NEVER red) IFF §3 is FROZEN AND state is False
             ("you froze without grounding"); it rides the existing `warnings` array
             (no new --json key).
  * prose  — phases/3-contract.md freeze checklist gains a 7th **Grounded** item (⚠ first,
             ≤16 lines); run.md says "seven lines"; both byte-identical ×3.

    cd add-method/tooling && python3 -m unittest test_ground_wiring -v
"""
import hashlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import md_section
from engine_pin import ENGINE_MD5

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BUNDLE = HERE.parent / "src" / "add_method" / "_bundled"

CONTRACT_MD = HERE.parent / "skill" / "add" / "phases" / "3-contract.md"
RUN_MD = HERE.parent / "skill" / "add" / "run.md"
CHECKLIST_HEADING = "## The freeze review checklist"

PLACEHOLDER = "<the symbols §3 will name>"
REAL_ANCHORS = "add.py:cmd_status · add.py:cmd_check · add.py:_raw_phase_bodies"


# ---------------------------------------------------------------------------
# PURE measure — no board needed
# ---------------------------------------------------------------------------
class GroundedStateTest(unittest.TestCase):
    """_grounded_state over raw §body dicts (the shape _raw_phase_bodies returns)."""

    def _raw(self, *, section0: str | None, status3: str = "DRAFT") -> dict[int, str]:
        text = "# TASK: t\n\nphase: contract\n\n"
        if section0 is not None:
            text += f"## 0 · GROUND — the real codebase\n\n{section0}\n\n"
        text += f"## 3 · CONTRACT\n\nStatus: {status3}\n"
        return add._phase_spans(text)

    def test_filled_anchors_is_grounded(self):
        raw = self._raw(section0=f"Anchors the contract cites: {REAL_ANCHORS}")
        self.assertIs(add._grounded_state(raw), True)

    def test_placeholder_anchors_not_grounded(self):
        raw = self._raw(section0=f"Anchors the contract cites: {PLACEHOLDER}")
        self.assertIs(add._grounded_state(raw), False)

    def test_empty_anchors_not_grounded(self):
        raw = self._raw(section0="Anchors the contract cites:")
        self.assertIs(add._grounded_state(raw), False)

    def test_no_section0_is_none(self):
        raw = self._raw(section0=None)
        self.assertIsNone(add._grounded_state(raw), "a pre-ground/legacy task is exempt")

    def test_missing_anchors_line_is_none(self):
        # §0 present but no Anchors line at all → fail-open (None), never a false False
        raw = self._raw(section0="Touches: add.py:cmd_status")
        self.assertIsNone(add._grounded_state(raw))


# ---------------------------------------------------------------------------
# Live board — surfaces arranged through the real CLI / state
# ---------------------------------------------------------------------------
class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-grw-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _make_active_task(self, slug="feat", *, anchors=REAL_ANCHORS,
                          frozen=False, phase="contract", legacy=False) -> Path:
        """Write a marker-consistent TASK.md with a controlled §0 / §3 and set it active."""
        root = self._root()
        tdir = root / "tasks" / slug
        tdir.mkdir(parents=True, exist_ok=True)
        section0 = "" if legacy else (
            "## 0 · GROUND — the real codebase\n\n"
            "Touches (files · symbols · signatures): add.py:cmd_status\n"
            f"Anchors the contract cites: {anchors}\n\n"
        )
        status = "FROZEN @ v1 — approved by t · 2026-06-11" if frozen else "DRAFT"
        body = (
            f"# TASK: {slug}\n\n"
            f"slug: {slug} · created: 2026-06-10 · stage: mvp\n"
            "autonomy: conservative\n"
            f"phase: {phase}\n\n"
            f"{section0}"
            "## 3 · CONTRACT — freeze the shape\n\n"
            "```\nshape\n```\n\n"
            f"Status: {status}\n"
        )
        (tdir / "TASK.md").write_text(body, encoding="utf-8")
        st = add.load_state(root)
        st["tasks"][slug] = {"phase": phase, "gate": "none"}
        st["active_task"] = slug
        add.save_state(root, st)
        return root

    def _status(self) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            add.main(["status"])
        return buf.getvalue()

    def _check_json(self):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["check", "--json"])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return json.loads(buf.getvalue()), code

    def _warn_blob(self, d) -> str:
        return " ".join(f'{w["name"]} {w["reason"]}' for w in d["warnings"])

    def _failed_reasons(self, d) -> str:
        return " ".join(c["reason"] for c in d["checks"] if not c["ok"])


class StatusSurfaceTest(_Board):
    def test_status_surfaces_grounded_when_filled(self):
        self._make_active_task(anchors=REAL_ANCHORS)
        self.assertIn("grounded ✓", self._status(),
                      "a filled §0 map must surface 'grounded ✓'")

    def test_status_surfaces_not_yet_when_unfilled(self):
        self._make_active_task(anchors=PLACEHOLDER)
        out = self._status()
        self.assertIn("grounded:", out)
        self.assertIn("not yet", out, "a placeholder §0 must surface 'not yet'")

    def test_status_silent_for_pre_ground_task(self):
        # the additive proof: a legacy task (no §0) prints NO grounded line
        self._make_active_task(legacy=True)
        self.assertNotIn("grounded:", self._status(),
                         "a pre-ground/legacy task must not add a grounded line")


class CheckWarnTest(_Board):
    def test_frozen_ungrounded_warns_not_red(self):
        self._make_active_task(anchors=PLACEHOLDER, frozen=True)
        d, code = self._check_json()
        self.assertIn("task_not_grounded", self._warn_blob(d))
        self.assertEqual(code, 0, "grounding is a WARN, never a red check")
        self.assertNotIn("task_not_grounded", self._failed_reasons(d))

    def test_draft_ungrounded_silent(self):
        # PINS the freeze-gated boundary (⚠ flag): no nag while the contract is still DRAFT
        self._make_active_task(anchors=PLACEHOLDER, frozen=False)
        d, _ = self._check_json()
        self.assertNotIn("task_not_grounded", self._warn_blob(d))

    def test_frozen_grounded_silent(self):
        self._make_active_task(anchors=REAL_ANCHORS, frozen=True)
        d, _ = self._check_json()
        self.assertNotIn("task_not_grounded", self._warn_blob(d))

    def test_pre_ground_task_never_warned(self):
        # a frozen legacy task (no §0) is EXEMPT — None never warns
        self._make_active_task(legacy=True, frozen=True)
        d, _ = self._check_json()
        self.assertNotIn("task_not_grounded", self._warn_blob(d))

    def test_no_new_json_key_on_check(self):
        # the task_not_grounded warning rides the EXISTING `warnings` array (adds no key).
        # The key set is a SURFACE LOCK — it grows ONLY by a deliberate, frozen contract:
        # standalone-fast-task added the additive `informed`/`infos` soft-info tier (a fast
        # standalone is an INFO, never a WARN). The lock stays strict at this exact set.
        self._make_active_task(anchors=PLACEHOLDER, frozen=True)
        d, _ = self._check_json()
        self.assertEqual(set(d.keys()),
                         {"passed", "failed", "warned", "warnings", "informed", "infos", "checks"})


# ---------------------------------------------------------------------------
# Prose — the freeze review checklist gains the 7th item; trees stay in lockstep
# ---------------------------------------------------------------------------
class FreezeChecklistTest(unittest.TestCase):
    def _section(self) -> str:
        return md_section.section(CONTRACT_MD.read_text(encoding="utf-8"), CHECKLIST_HEADING)

    def test_checklist_has_seven_items_grounded_named(self):
        sec = self._section()
        items = [ln for ln in sec.splitlines() if ln.lstrip().startswith("- **")]
        self.assertEqual(len(items), 7, f"the checklist must walk seven items, got {len(items)}")
        self.assertIn("⚠", items[0], "the least-sure flags stay item ONE")
        self.assertTrue(any("Grounded" in it for it in items), "a **Grounded** item must exist")
        self.assertRegex(sec, r"(?i)anchor", "the Grounded item names the §0 anchors")

    def test_checklist_within_line_budget(self):
        nonblank = [ln for ln in self._section().splitlines() if ln.strip()]
        self.assertLessEqual(len(nonblank), 16,
                             f"checklist bloated to {len(nonblank)} non-blank lines")

    def test_count_word_is_seven(self):
        self.assertIn("seven", self._section(), "the count word must read 'seven'")

    def test_run_md_says_seven_lines(self):
        self.assertIn("seven lines", RUN_MD.read_text(encoding="utf-8"),
                      "run.md's freeze-checklist reference must say 'seven lines'")

    def test_prose_three_trees_agree(self):
        for rel in (("skill", "add", "phases", "3-contract.md"),
                    ("skill", "add", "run.md")):
            canon = HERE.parent.joinpath(*rel)
            for twin in (REPO / ".claude" / "skills" / "add" / Path(*rel[2:]),
                         BUNDLE.joinpath(*rel)):
                self.assertEqual(canon.read_bytes(), twin.read_bytes(),
                                 f"divergence (synced ×3): {twin}")


# ---------------------------------------------------------------------------
# ground-phase-harden — enrich BOTH grounding seams (per-task §0 + milestone-level)
# to one consistent four-field rubric. Guide + template only; no engine gate.
# ---------------------------------------------------------------------------
_SKILL = HERE.parent / "skill" / "add"
GROUND_MD = _SKILL / "phases" / "0-ground.md"
SCOPE_MD = _SKILL / "scope.md"
TASK_TMPL = HERE / "templates" / "TASK.md.tmpl"
FAST_TMPL = HERE / "templates" / "TASK.fast.md.tmpl"
GROUND_FIELDS = ("Touches", "Context", "Honors", "Anchors")


class GroundHardenTest(unittest.TestCase):
    """The four-field grounding rubric is demanded at both altitudes (per-task §0 guide
    + milestone-level scope.md), and the §0 template conveys required-not-optional."""

    def _exit_gate(self, text: str) -> str:
        m = re.search(r"<exit_gate>(.*?)</exit_gate>", text, re.DOTALL)
        return m.group(1) if m else ""

    def test_ground_exit_gate_names_all_four_fields(self):
        gate = self._exit_gate(GROUND_MD.read_text(encoding="utf-8"))
        self.assertTrue(gate, "0-ground.md must keep its <exit_gate> block")
        missing = [f for f in GROUND_FIELDS if f not in gate]
        self.assertEqual(missing, [],
                         f"the per-task ground exit gate must name all four fields; missing {missing}")

    def test_ground_guide_has_completeness_rubric(self):
        text = GROUND_MD.read_text(encoding="utf-8").lower()
        self.assertIn("grounding is complete when", text,
                      "0-ground.md must carry a 'grounding is complete when…' rubric")

    def test_scope_position_goal_names_four_field_rubric(self):
        sec = md_section.section(SCOPE_MD.read_text(encoding="utf-8"),
                                 "## Position the goal — ground in assets, relate to the milestone map")
        missing = [f for f in GROUND_FIELDS if f not in sec]
        self.assertEqual(missing, [],
                         f"the milestone-level grounding step must name the same four fields; missing {missing}")

    def test_task_template_section0_names_four_fields(self):
        # change request @ v2 (human-approved): the §0 <!-- EXIT --> comment clause was DROPPED —
        # it collided with the lean-pass comment fence (test_template_form_tags, count < 12). The
        # template keeps all four field labels; the completeness guidance lives in 0-ground.md.
        #
        # plan-phase-core: grounding moved from the standalone `## 0 · GROUND` section into
        # `## 3 · PLAN`'s `### Grounding` sub-block. Re-pointed via the engine's own
        # `_ground_section` extractor (add.py) so the assertion stays scoped to just the
        # grounding fields (not the whole §3 PLAN section, which would make this vacuous).
        sec = add._ground_section(TASK_TMPL.read_text(encoding="utf-8"))
        self.assertTrue(sec, "TASK.md.tmpl must carry a `### Grounding` sub-block")
        for f in GROUND_FIELDS:
            self.assertIn(f, sec, f"TASK.md.tmpl §3 PLAN Grounding must keep the {f} field")

    def test_fast_template_section0_names_four_fields(self):
        # §1 ⚠ flag RESOLVED at freeze: human chose uniform grounding — the fast §0 also
        # NAMES the four fields (compactly; it need not carry the full prose rubric).
        #
        # plan-phase-core: same re-point as above, fast-template Grounding sub-block.
        sec = add._ground_section(FAST_TMPL.read_text(encoding="utf-8"))
        self.assertTrue(sec, "TASK.fast.md.tmpl must carry a `### Grounding` sub-block")
        missing = [f for f in GROUND_FIELDS if f not in sec]
        self.assertEqual(missing, [],
                         f"the fast §3 PLAN Grounding must name all four grounding fields (uniform); missing {missing}")

    def test_ground_harden_three_tree_parity(self):
        for rel in ("phases/0-ground.md", "scope.md"):
            canon = (_SKILL / rel).read_bytes()
            bundled = (BUNDLE / "skill" / "add" / rel).read_bytes()
            self.assertEqual(canon, bundled, f"{rel} drifted: canonical vs _bundled")


class EngineParityTest(unittest.TestCase):
    def test_engine_byte_identical(self):
        for p in (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
                  BUNDLE / "tooling" / "add.py"):
            self.assertEqual(hashlib.md5(p.read_bytes()).hexdigest(), ENGINE_MD5,
                             f"engine tree drifted from the pin: {p}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
