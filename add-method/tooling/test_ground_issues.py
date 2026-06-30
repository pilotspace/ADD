#!/usr/bin/env python3
"""Red/green tests for ground-issues — the §0 GROUND fifth field that feeds SPECIFY.

GROUND should surface the concrete problems/traps/untestable risks the AI finds in
the REAL code while grounding, so §1 SPECIFY answers problems FOUND, not assumed.
Frozen shape (§3 @ v1):
  - 0-ground.md `## Gather` gains an "Issues/Risks (→ feed §1)" category (task-delta only)
    + an `## Exit gate` checkbox for it;
  - TASK.md.tmpl `## 0 · GROUND` gains ONE `Issues/Risks (→ feed §1):` line, placed
    AFTER the `Anchors the contract cites:` line;
  - 1-specify.md CONSUMES it — §1 builds on the §0 Issues/Risks;
  - INVARIANTS preserved: the `Anchors the contract cites:` line (the grounding measure
    keys on it), `## 0`/`GROUND`, add.py byte-identical to engine_pin (no measure edit),
    the phases lean pool ≤ its UNCHANGED target (compaction, not a rebaseline);
  - SYNC: 0-ground.md ×3 (skill trees) and TASK.md.tmpl ×3 (template trees) byte-identical.

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
    _ADD_METHOD / "skill" / "add" / "phases" / "0-ground.md",
    _REPO / ".claude" / "skills" / "add" / "phases" / "0-ground.md",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "0-ground.md",
]
SPECIFY_COPIES = [
    _ADD_METHOD / "skill" / "add" / "phases" / "1-specify.md",
    _REPO / ".claude" / "skills" / "add" / "phases" / "1-specify.md",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "1-specify.md",
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
PHASES_POOL = [
    "phases/0-ground.md", "phases/0-setup.md", "phases/1-specify.md",
    "phases/2-scenarios.md", "phases/3-contract.md", "phases/4-tests.md",
    "phases/5-build.md", "phases/6-verify.md", "phases/7-observe.md",
]
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


class GuideNamesIssuesCategory(unittest.TestCase):
    """0-ground.md ## Gather names the Issues/Risks category; existing fields remain."""

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
        # the ## Exit gate must gain a checkbox for the new field
        text = _canonical_guide()
        gate = text.split("## Exit gate", 1)
        self.assertEqual(len(gate), 2, "the guide must keep its ## Exit gate")
        self.assertIn(FIELD, gate[1], "the exit gate must list the Issues/Risks field")


class TemplateGainsIssuesLine(unittest.TestCase):
    """TASK.md.tmpl §0 carries the Issues/Risks line, AFTER the Anchors line."""

    def test_section0_has_issues_line(self):
        sec0 = _section0(_canonical_tmpl())
        self.assertTrue(sec0, "the template must have a `## 0 · GROUND` section")
        self.assertIn(f"{FIELD} (→ feed §1):", sec0,
                      "§0 must gain the `Issues/Risks (→ feed §1):` line")

    def test_issues_line_after_anchors(self):
        sec0 = _section0(_canonical_tmpl())
        self.assertIn("Anchors the contract cites:", sec0)
        self.assertLess(sec0.index("Anchors the contract cites:"), sec0.index(f"{FIELD} (→ feed §1):"),
                        "the Issues/Risks line must come AFTER the Anchors measure line")

    def test_section0_preserves_anchors_line(self):
        sec0 = _section0(_canonical_tmpl())
        self.assertIn("Anchors the contract cites:", sec0,
                      "the §0 grounding-measure line must be preserved verbatim")

    def test_section0_keeps_heading_tokens(self):
        sec0 = _section0(_canonical_tmpl())
        self.assertIn("## 0 ", sec0)
        self.assertIn("GROUND", sec0)


class SpecifyConsumesIssues(unittest.TestCase):
    """1-specify.md builds §1 on the §0 GROUND Issues/Risks; existing structure remains."""

    def test_specify_references_issues(self):
        text = _canonical_specify()
        self.assertIn(FIELD, text,
                      "the specify guide must consume the §0 GROUND Issues/Risks")

    def test_specify_keeps_cospecify_and_gate(self):
        text = _canonical_specify()
        self.assertIn("Co-specify", text, "the three-moves co-specify must remain")
        self.assertIn("Exit gate", text, "the specify exit gate must remain")


class EngineMeasureUntouched(unittest.TestCase):
    """The grounding measure is out of scope — add.py must not change."""

    def test_engine_byte_identical_to_pin(self):
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match engine_pin.ENGINE_MD5 (no measure edit this task)")


class LeanPoolHeldByCompaction(unittest.TestCase):
    """The phases pool stays under its LIVE target. (ground-issues shipped under the unchanged
    40065 baseline by compaction; ground-related-intent later rebaselined to 40280 for two
    genuinely-new §0 fields — so this reads the live budget, not a frozen number. The real
    invariant: the pool is within its budget and the budget is internally consistent.)"""

    def test_phases_pool_under_live_target(self):
        from test_skill_lean import POOLS
        phases = next(p for p in POOLS if p["name"] == "phases")
        target = int(phases["baseline"] * phases["ratio"])
        nbytes = sum(len((_CANON / g).read_bytes()) for g in PHASES_POOL if (_CANON / g).exists())
        self.assertLessEqual(nbytes, target,
                             f"phases pool is {nbytes} B; must stay ≤ live target {target}")

    def test_phases_budget_consistent(self):
        from test_skill_lean import POOLS
        phases = next(p for p in POOLS if p["name"] == "phases")
        self.assertEqual(phases["ratio"], 0.80, "the phases ratio must stay 0.80")
        self.assertGreaterEqual(phases["baseline"], 40065,
                                "the phases baseline only ever grows (human-approved rebaselines)")


class CopiesStayByteIdentical(unittest.TestCase):
    """The ×3 guide/specify and ×3 template copies stay md5-identical (dogfood parity)."""

    def test_guide_copies_byte_identical(self):
        present = [p for p in GUIDE_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "all 3 skill 0-ground.md copies must exist")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 0-ground.md copies must be byte-identical")

    def test_specify_copies_byte_identical(self):
        present = [p for p in SPECIFY_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "all 3 skill 1-specify.md copies must exist")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 1-specify.md copies must be byte-identical")

    def test_template_copies_byte_identical(self):
        present = [p for p in TMPL_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "all 3 TASK.md.tmpl copies must exist")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 TASK.md.tmpl copies must be byte-identical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
