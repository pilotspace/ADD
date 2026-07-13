#!/usr/bin/env python3
"""Structural proof of the scope-drafting rubric (task: scope-loop, v4-1).

scope-loop ships a JUDGMENT artifact (scope.md — the facilitation method that turns a
CLASSIFIED request into a versioned MILESTONE.md), not code. So the red/green guard asserts
the ARTIFACT's structure, never the AI's live drafting: scope.md exists in both synced skill
trees (md5 parity), documents the per-outcome behavior for all 4 intake outcomes + the 3 reject
codes, states the confirm-before-create invariant and the exit-criteria->task-slug rule, carries
a worked example naming a REAL milestone slug in this repo, and both SKILL.md copies link it.
The human reviews the drafting JUDGMENT at the verify gate.

Run: python3 -m unittest test_scope_loop -v
"""
import hashlib
import re
import unittest
from pathlib import Path

# Resolve repo paths from THIS file, not cwd: tooling/ -> add-method/ -> repo root.
_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANONICAL_SCOPE = _ADD_METHOD / "skill" / "add" / "scope.md"
DOGFOOD_SCOPE = _REPO / ".claude" / "skills" / "add" / "scope.md"
BUNDLE_SCOPE = _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "scope.md"
CANONICAL_SKILL = _ADD_METHOD / "skill" / "add" / "SKILL.md"
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add" / "SKILL.md"
MILESTONES_DIR = _REPO / ".add" / "milestones"

# The 4 intake outcomes (the 4 buckets) plus the split path the outcomes table must cover.
OUTCOME_TOKENS = {"new-major", "sub-milestone", "task", "change-request", "split_required"}
# scope-complete-position (v1): duplicate_goal joins the closed set — a DRAFTING reject the
# Position-the-goal step raises when a goal is already delivered by an existing milestone.
REJECT_CODES = {"not_classified", "dangling_criterion", "no_milestone", "duplicate_goal"}

# The 10 MILESTONE.md.tmpl sections scope.md's drafting section must name (E1). The header
# fields goal + rationale count as named items; stage/status/created is a single header line.
# `ground` was added by milestone-ground-seed (expectations-first): the shared real-code
# context gathered ONCE that each task's specify projects from.
TEMPLATE_SECTIONS = (
    "goal", "rationale", "scope", "ground", "shared decisions", "shared", "contracts",
    "tasks", "exit criteria", "close", "release steps",
)
# Frozen tokens (TASK.md §3, scope-complete-position v1) — must appear verbatim in scope.md.
FROZEN_TOKENS = ("Position the goal", "duplicate_goal", "drafted-blank", "well-formedness")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _parse_outcomes_table(text: str):
    """Parse the | intake outcome | scope-loop action | creates | table -> outcome-column cells.

    Identified by an 'outcome' + 'action' header with no 'bucket'/'request' column.
    """
    cells_out = []
    in_table = False
    outcome_col = None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if (any("outcome" in c for c in lowered) and any("action" in c for c in lowered)
                and not any("bucket" in c or "request" in c for c in lowered)):
            in_table = True
            outcome_col = next(i for i, c in enumerate(lowered) if "outcome" in c)
            continue
        if not in_table:
            continue
        if set("".join(cells)) <= set("-: "):   # the |---|---| separator row
            continue
        if len(cells) > outcome_col:
            cells_out.append(cells[outcome_col])
    return cells_out


def _worked_example_section(text: str) -> str:
    """Return the text from the 'worked example' heading onward (empty if absent)."""
    m = re.search(r"^#+\s*worked example.*$", text, flags=re.IGNORECASE | re.MULTILINE)
    return text[m.start():] if m else ""


def _real_milestone_slugs():
    if not MILESTONES_DIR.is_dir():
        return set()
    return {p.name for p in MILESTONES_DIR.iterdir() if p.is_dir()}


class ScopeLoopTest(unittest.TestCase):
    def test_scope_md5_parity_across_three_trees(self):
        # E1/E2 land in all 3 parity trees — canonical, dogfood, AND the pip bundle.
        for p in (CANONICAL_SCOPE, DOGFOOD_SCOPE, BUNDLE_SCOPE):
            self.assertTrue(p.exists(), f"missing {p}")
        self.assertEqual(_md5(CANONICAL_SCOPE), _md5(DOGFOOD_SCOPE),
                         "scope.md differs between the canonical and dogfood skill trees")
        self.assertEqual(_md5(CANONICAL_SCOPE), _md5(BUNDLE_SCOPE),
                         "scope.md differs between the canonical tree and the pip _bundled copy")

    def test_documents_all_four_intake_outcomes(self):
        # The outcomes table must cover all 4 buckets + the split path (in its outcome column),
        # not merely mention the words in prose. Deleting the table or a row goes red.
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        cells = _parse_outcomes_table(text)
        self.assertTrue(cells, "no outcomes table found in scope.md")
        joined = " ".join(cells).lower()
        for tok in OUTCOME_TOKENS:
            self.assertIn(tok, joined, f"outcomes table does not document the '{tok}' outcome")

    def test_documents_all_reject_codes(self):
        # duplicate_goal joins the closed set (scope-complete-position v1).
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        for code in REJECT_CODES:
            self.assertIn(code, text, f"scope.md does not document the '{code}' reject code")

    def test_states_confirm_before_create_invariant(self):
        text = CANONICAL_SCOPE.read_text(encoding="utf-8").lower()
        m = re.search(r"confirm[\s-]*before[\s-]*create", text)
        self.assertIsNotNone(
            m, "scope.md must state the confirm-before-create invariant")

    def test_states_exit_criteria_map_to_task_slug(self):
        text = CANONICAL_SCOPE.read_text(encoding="utf-8").lower()
        m = re.search(r"exit criteri.{0,60}task slug", text, flags=re.DOTALL)
        self.assertIsNotNone(
            m, "scope.md must state that every exit criterion maps to a declared task slug")

    def test_worked_example_references_real_milestone(self):
        section = _worked_example_section(CANONICAL_SCOPE.read_text(encoding="utf-8"))
        self.assertTrue(section, "scope.md has no 'worked example' section")
        real = _real_milestone_slugs()
        self.assertTrue(real, f"no milestones found under {MILESTONES_DIR}")
        hit = [s for s in real if s in section]
        self.assertTrue(
            hit, f"worked example names no real milestone slug (have {sorted(real)})")

    def test_frozen_tokens_present(self):
        # The §3 frozen tokens must appear verbatim in scope.md.
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        for tok in FROZEN_TOKENS:
            self.assertIn(tok, text, f"scope.md is missing the frozen token '{tok}'")

    def test_position_the_goal_is_the_first_drafting_step(self):
        # E2a — a "Position the goal" step that grounds in assets AND cross-references the
        # existing+archived milestone map, recorded in rationale.
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        m = re.search(r"^#+\s*.*position the goal.*$", text, flags=re.IGNORECASE | re.MULTILINE)
        self.assertIsNotNone(m, "scope.md has no 'Position the goal' step heading")
        body = text[m.start():]
        low = body.lower()
        self.assertTrue(
            re.search(r"asset|project\.md", low),
            "the Position-the-goal step must ground the goal in current assets")
        self.assertTrue(
            re.search(r"archive|existing milestone|milestone.{0,20}goal|relationship", low),
            "the Position-the-goal step must cross-reference the existing/archived milestone map")

    def test_covers_all_ten_template_sections(self):
        # E1a — the drafting section names all 10 MILESTONE.md.tmpl sections (incl. the three the
        # guide was silent on: rationale, Close ship-review, Release steps — and `ground`, added
        # by milestone-ground-seed).
        text = CANONICAL_SCOPE.read_text(encoding="utf-8").lower()
        self.assertEqual(len(TEMPLATE_SECTIONS), 11,
                         "TEMPLATE_SECTIONS must list the 10 milestone sections (goal+rationale "
                         "+ 8 headings, 'shared'/'contracts' both matching one heading)")
        for sec in TEMPLATE_SECTIONS:
            self.assertIn(sec, text, f"scope.md never names the '{sec}' template section")

    def test_marks_close_and_release_drafted_blank(self):
        # E1b — Close ship-review + Release steps are explicitly drafted-blank, owned by the
        # close/release flows (fold.md / release.md) — not filled at scope time.
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        self.assertIn("drafted-blank", text,
                      "scope.md must mark Close/Release sections drafted-blank")
        low = text.lower()
        self.assertTrue(
            "fold.md" in low or "release.md" in low or "close" in low,
            "scope.md must name the flow that owns the drafted-blank sections")

    def test_well_formedness_gate_present(self):
        # E1c — a draft well-formedness gate (a checklist a draft passes before it is proposed).
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        self.assertIn("well-formedness", text,
                      "scope.md must carry a draft well-formedness gate")

    def test_both_skill_md_link_scope_and_are_identical(self):
        for skill in (CANONICAL_SKILL, DOGFOOD_SKILL):
            self.assertIn("scope.md", skill.read_text(encoding="utf-8"),
                          f"{skill} does not point to scope.md")
        self.assertEqual(_md5(CANONICAL_SKILL), _md5(DOGFOOD_SKILL),
                         "the two SKILL.md copies are not byte-identical")


class ComponentsConsiderationPromptTest(unittest.TestCase):
    """scope-components-check: step 1 ("Ground in current assets") must prompt considering the
    components pillar once a milestone's Touches spans >1 app root — closing a real gap found in
    a downstream project where 30+ tasks spanned two app roots with the pillar never declared."""

    def test_components_prompt_present_and_mirrored(self):
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        self.assertIn(".add/components.toml", text,
                      "scope.md step 1 must name .add/components.toml")
        self.assertIn("components.md", text,
                      "scope.md must point at components.md for the full pillar")
        for tree in (DOGFOOD_SCOPE, BUNDLE_SCOPE):
            self.assertEqual(_md5(CANONICAL_SCOPE), _md5(tree),
                             f"{tree} is not byte-identical to the canonical scope.md")

    def test_components_prompt_lives_in_ground_step(self):
        # the prompt must sit inside step 1 ("Ground in current assets"), not floated elsewhere
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        step1 = text.split("**Ground in current assets.**", 1)[1].split("\n2.", 1)[0]
        self.assertIn(".add/components.toml", step1,
                      "the components-pillar prompt must live inside step 1, not elsewhere")


if __name__ == "__main__":
    unittest.main(verbosity=2)
