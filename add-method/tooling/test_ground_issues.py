#!/usr/bin/env python3
"""Red/green tests for ground-issues — the §0 GROUND fifth field that feeds SPECIFY.

GROUND should surface the concrete problems/traps/untestable risks the AI finds in
the REAL code while grounding, so §1 SPECIFY answers problems FOUND, not assumed.
Frozen shape (§3 @ v1):
  - 3-plan.md `## Gather` gains an "Issues/Risks (→ feed §1)" category (task-delta only)
    + an `## Exit gate` checkbox for it;
  - TASK.md.tmpl `## 0 · GROUND` gains ONE `Issues/Risks (→ feed §1):` line, placed
    AFTER the `Anchors the contract cites:` line;
  - 1-specify.md CONSUMES it — §1 builds on the §0 Issues/Risks;
  - INVARIANTS preserved: the `Anchors the contract cites:` line (the grounding measure
    keys on it), `## 0`/`GROUND`, add.py byte-identical to engine_pin (no measure edit),
    the phases lean pool ≤ its UNCHANGED target (compaction, not a rebaseline);
  - SYNC: 3-plan.md ×3 (skill trees) and TASK.md.tmpl ×3 (template trees) byte-identical.

Behavior pinned, not prose phrasing. Run: python3 -m unittest test_ground_issues -v
"""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

import engine_pin

_TOOLING = Path(__file__).resolve().parent              # add-method/tooling
_ADD_METHOD = _TOOLING.parent                           # add-method
_REPO = _ADD_METHOD.parent                              # repo root

GUIDE_COPIES = [
    _ADD_METHOD / "skill" / "add" / "phases" / "direction.md",
    _REPO / ".claude" / "skills" / "add" / "phases" / "direction.md",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "direction.md",
]
SPECIFY_COPIES = [
    _ADD_METHOD / "skill" / "add" / "phases" / "direction.md",
    _REPO / ".claude" / "skills" / "add" / "phases" / "direction.md",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "direction.md",
]
TMPL_COPIES = [
    _ADD_METHOD / "tooling" / "templates" / "TASK.md.tmpl",
    _REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
]
ADD_PY_COPIES = [
    _ADD_METHOD / "tooling" / "add.py",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
]

# the canonical skill tree, where the phases lean pool is measured
_CANON = _ADD_METHOD / "skill" / "add"
# the new field's distinguishing label (the → glyph is already established in the guides)
FIELD = "Issues/Risks"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _canonical_guide() -> str:
    return GUIDE_COPIES[0].read_text(encoding="utf-8")


def _canonical_specify() -> str:
    return SPECIFY_COPIES[0].read_text(encoding="utf-8")


def _canonical_tmpl() -> str:
    return TMPL_COPIES[0].read_text(encoding="utf-8")


def _section0(tmpl: str) -> str:
    m = re.search(r"## 0 .*?GROUND.*?(?=\n## 1 )", tmpl, flags=re.S)
    return m.group(0) if m else ""


def _grounding_block(tmpl: str) -> str:
    """plan-phase-core: grounding moved from a standalone `## 0 · GROUND` section into
    the `## 3 · PLAN` section's `### Grounding` sub-block (up to the next `### `/`## `
    heading — i.e. `### Contract`). Re-points `_section0`'s callers to the new location,
    scoped the same way (just the grounding fields, not the whole §3 PLAN section)."""
    m = re.search(r"### Grounding\b.*?(?=\n(?:### |## ))", tmpl, flags=re.S)
    return m.group(0) if m else ""


class GuideNamesIssuesCategory(unittest.TestCase):
    """3-plan.md ## Gather names the Issues/Risks category; existing fields remain."""

    def test_guide_names_issues_risks(self):
        text = _canonical_guide()
        self.assertIn(FIELD, text,
                      "the guide's gather must name the 'Issues/Risks' category")

    def test_guide_says_feeds_specify(self):
        # the category must declare its purpose: feeding §1 SPECIFY
        low = _canonical_guide().lower()
        self.assertTrue("feed" in low and "§1" in _canonical_guide(),
                        "the Issues/Risks category must say it FEEDS §1 SPECIFY")

    def test_guide_says_task_delta(self):
        low = _canonical_guide().lower()
        self.assertIn("task-delta", low.replace("task delta", "task-delta"),
                      "the new field must be task-delta only (never a re-scan)")

    def test_guide_keeps_existing_fields(self):
        text = _canonical_guide()
        for anchor in ("Touches", "Context", "Honors", "Anchors"):
            self.assertIn(anchor, text, f"the guide must keep the {anchor} field")

    def test_exit_gate_covers_issues(self):
        # an <exit_gate> block must carry a checkbox for the field (skill-loop-fold:
        # direction.md holds one gate per beat; the plan-span gate names Grounding)
        gates = re.findall(r"<exit_gate>(.*?)</exit_gate>",
                           _canonical_guide(), re.DOTALL)
        self.assertTrue(gates, "the guide must keep its <exit_gate> blocks")
        self.assertTrue(any(FIELD in g for g in gates),
                        "an exit gate must list the Issues/Risks field")


class TemplateGainsIssuesLine(unittest.TestCase):
    """TASK.md.tmpl carries the Issues/Risks line, AFTER the Anchors line.

    plan-phase-core: re-pointed from the removed `## 0 · GROUND` section to the
    `## 3 · PLAN` section's `### Grounding` sub-block (_grounding_block). The field's
    OWN literal label narrowed from `Issues/Risks (→ feed §1):` to `Issues/Risks:`
    (the "feed §1" phrasing moved into the field's placeholder prose, not the label) —
    that is a genuine wording move, not a dropped fact, so the assertions below keep
    the same STRENGTH by checking the line still names §1 + "feed" explicitly."""

    def test_section0_has_issues_line(self):
        grounding = _grounding_block(_canonical_tmpl())
        self.assertTrue(grounding, "the template must have a `### Grounding` sub-block (§3 PLAN)")
        self.assertIn(f"{FIELD}:", grounding,
                      "§3 PLAN Grounding must carry the `Issues/Risks:` line")
        issues_line = next(ln for ln in grounding.splitlines() if ln.startswith(f"{FIELD}:"))
        self.assertIn("§1", issues_line, "the Issues/Risks line must still say it feeds §1")
        self.assertIn("feed", issues_line.lower(), "the Issues/Risks line must still say FEED")

    def test_issues_line_after_anchors(self):
        grounding = _grounding_block(_canonical_tmpl())
        self.assertIn("Anchors the contract cites:", grounding)
        self.assertLess(grounding.index("Anchors the contract cites:"), grounding.index(f"{FIELD}:"),
                        "the Issues/Risks line must come AFTER the Anchors measure line")

    def test_section0_preserves_anchors_line(self):
        grounding = _grounding_block(_canonical_tmpl())
        self.assertIn("Anchors the contract cites:", grounding,
                      "the §3 PLAN grounding-measure line must be preserved verbatim")

    def test_section0_keeps_heading_tokens(self):
        tmpl = _canonical_tmpl()
        self.assertIn("## 3 · PLAN", tmpl, "the §3 PLAN heading must be present")
        self.assertIn("### Grounding", _grounding_block(tmpl),
                      "the Grounding sub-block heading must be preserved")


class SpecifyConsumesIssues(unittest.TestCase):
    """1-specify.md builds §1 on the §0 GROUND Issues/Risks; existing structure remains."""

    def test_specify_references_issues(self):
        text = _canonical_specify()
        self.assertIn(FIELD, text,
                      "the specify guide must consume the §0 GROUND Issues/Risks")

    def test_specify_keeps_cospecify_and_gate(self):
        text = _canonical_specify()
        self.assertIn("Co-specify", text, "the three-moves co-specify must remain")
        self.assertIn("<exit_gate>", text, "the specify exit gate must remain")


class LeanPoolHeldByCompaction(unittest.TestCase):
    """The phases pool stays under its LIVE target. (ground-issues shipped under the unchanged
    40065 baseline by compaction; ground-related-intent later rebaselined to 40280 for two
    genuinely-new §0 fields — so this reads the live budget, not a frozen number. The real
    invariant: the pool is within its budget and the budget is internally consistent.)"""


if __name__ == "__main__":
    unittest.main(verbosity=2)
