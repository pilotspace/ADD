#!/usr/bin/env python3
"""Red/green tests for udd-persona-loop (persona-learning-loop 2/7).

The UDD render-capture-confirm beat (design.md) gains a persona-sourced evidence checklist:
before design-confirm, the matched UI personas' `## Success Metrics` render as a confirmable
checklist carrying BOTH dimensions — UI-Designer (visual/WCAG-AA accessibility) and UX-Researcher
(methodology-first, evidence-not-assumption). The checklist is evidence the human confirms, never
an auto-pass (a persona never lowers a gate). Guide-only: the engine is unchanged (NO render).
Doc-truth across the 3 skill trees. Run: python3 -m unittest test_udd_persona_checklist -v
"""
import hashlib
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

SKILL_TREES = (
    PKG_ROOT / "skill" / "add",
    REPO_ROOT / ".claude" / "skills" / "add",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",
)


def _design(tree: Path) -> str:
    return (tree / "design.md").read_text(encoding="utf-8")


def _design_lower(tree: Path) -> str:
    return _design(tree).lower()


class DesignConfirmChecklistTest(unittest.TestCase):
    # scenario: the design-confirm checklist sources both UI personas' success-metrics
    def test_design_confirm_sources_persona_metrics(self):
        for tree in SKILL_TREES:
            txt = _design(tree)
            low = txt.lower()
            self.assertIn("## Success Metrics", txt,
                          f"design.md in {tree} must source the persona '## Success Metrics'")
            self.assertIn("persona", low, "must reference personas")
            self.assertIn("checklist", low,
                          f"design.md in {tree} must render the metrics as a confirm checklist")

    # scenario: the guide names both dimensions explicitly (doc-truth)
    def test_checklist_names_both_dimensions(self):
        for tree in SKILL_TREES:
            low = _design_lower(tree)
            self.assertIn("ui-designer", low, f"{tree}: must name the UI-Designer dimension")
            self.assertIn("ux-researcher", low, f"{tree}: must name the UX-Researcher dimension")
            self.assertIn("accessibility", low, f"{tree}: UI-Designer dimension = visual/accessibility")
            self.assertTrue("not assumed" in low or "evidence-not-assumption" in low,
                            f"{tree}: UX-Researcher dimension = validated by evidence, not assumed")

    # scenario: a persona success-metric is evidence, never an auto-pass
    def test_metric_is_evidence_not_autopass(self):
        for tree in SKILL_TREES:
            low = _design_lower(tree)
            self.assertIn("never an auto-pass", low,
                          f"{tree}: a success-metric is evidence, never an auto-pass")
            self.assertIn("never lowers a gate", low,
                          f"{tree}: a persona never lowers a gate (ADD principle 2)")

    # scenario: a project with no UI personas still confirms (degrade-safe)
    def test_degrade_no_ui_personas(self):
        for tree in SKILL_TREES:
            low = _design_lower(tree)
            self.assertIn("no ui personas", low,
                          f"{tree}: must document the no-UI-personas degrade path")
            self.assertTrue("generic design-confirm" in low or "never blocked" in low,
                            f"{tree}: degrade must keep design-confirm flowing, never blocked")

    # scenario: the change is byte-identical across the three skill trees
    def test_persona_checklist_3tree_parity(self):
        bodies = {(_design(tree)) for tree in SKILL_TREES}
        self.assertEqual(len(bodies), 1, "design.md must be byte-identical across the 3 skill trees")

    # scenario: the engine is unchanged by this guide-only task (NO render)
    def test_engine_unchanged_no_render(self):
        import engine_pin
        live = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(live, engine_pin.ENGINE_MD5,
                         "udd-persona-loop is guide-only — add.py (engine) must be untouched")
        for tree in SKILL_TREES:
            self.assertIn("The engine never renders", _design(tree),
                          f"{tree}: the NO-render invariant must survive")


if __name__ == "__main__":
    unittest.main(verbosity=2)
