#!/usr/bin/env python3
"""Red/green tests for template-hint-dedup (call-residuals, frozen §3 v1):
the recent fast TASK.md files restated frozen upstream text — §5 Approach echoed the
Strategy stance, §6 Build-expectations paraphrased §1 Accept, and the milestone
Exit-criteria restated the task's plan line. This tightens those 4 placeholder HINTS
to demand each field's OWN distinct/concrete content. NON-weakening: the LABELS + the
`<…>` wrapper stay, so the build-expectations gate still fires on an unfilled template;
no engine/gate code changes. Asserts the hint VALUES across both tracked template trees.

Run: python3 -m unittest test_template_hint_dedup -v
"""
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent                       # add-method/tooling
_TREES = [
    _HERE / "templates",                                      # canonical
    _HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates",  # bundle
]


def _line(text: str, needle: str) -> str:
    for ln in text.splitlines():
        if needle in ln:
            return ln
    return ""


class HintDedupTest(unittest.TestCase):
    def _fast(self):
        for tree in _TREES:
            p = tree / "TASK.fast.md.tmpl"
            self.assertTrue(p.exists(), f"missing: {p}")
            yield p, p.read_text(encoding="utf-8")

    def _milestone(self):
        for tree in _TREES:
            p = tree / "MILESTONE.md.tmpl"
            self.assertTrue(p.exists(), f"missing: {p}")
            yield p, p.read_text(encoding="utf-8")

    def test_approach_hint_forbids_restatement(self):
        for p, text in self._fast():
            ln = _line(text, "Approach (domain strategy):")
            self.assertIn("NOT a restatement", ln,
                          f"{p}: §5 Approach hint must forbid restating the Strategy")

    def test_strategy_used_hint_asks_divergences_only(self):
        for p, text in self._fast():
            ln = _line(text, "Strategy actually used:")
            self.assertRegex(ln, r"diverg", f"{p}: §5 Strategy-actually-used hint must ask for divergences only")
            self.assertIn("re-narrate", ln, f"{p}: hint must say don't re-narrate §3 Strategy")

    def test_build_expectations_hint_demands_seen_observable(self):
        for p, text in self._fast():
            ln = _line(text, "Build expectations (from")
            self.assertIn("NOT a paraphrase", ln,
                          f"{p}: §6 Build-expectations hint must forbid paraphrasing §1 Accept")
            self.assertIn("SEE", ln, f"{p}: hint must demand a concrete SEEN observable")

    def test_build_expectations_placeholder_still_gated(self):
        # NON-weakening: the shipped hint must remain a `<…>` placeholder so the
        # build-expectations gate still reads it as unfilled. Label + `(from …)` kept.
        for p, text in self._fast():
            ln = _line(text, "Build expectations (from")
            self.assertIn("Build expectations (from §1 Accept + §3 CONTRACT):", ln,
                          f"{p}: label + derivation note must be byte-unchanged")
            self.assertRegex(ln, r"<[^>]*>", f"{p}: hint must stay a `<…>` placeholder (gate detects it)")

    def test_milestone_exit_criteria_hint_forbids_plan_line(self):
        for p, text in self._milestone():
            ln = _line(text, "User can <observable")
            self.assertIn("NOT the task's plan line", ln,
                          f"{p}: Exit-criteria hint must ask for the seen outcome, not the plan line")
            self.assertIn("(← <slug>)", ln, f"{p}: the `(← <slug>)` mapping must stay")

    def test_canonical_and_bundle_byte_identical(self):
        for name in ("TASK.fast.md.tmpl", "MILESTONE.md.tmpl"):
            canon = (_TREES[0] / name).read_text(encoding="utf-8")
            bundle = (_TREES[1] / name).read_text(encoding="utf-8")
            self.assertEqual(canon, bundle, f"{name}: canonical and bundle must be byte-identical")


if __name__ == "__main__":
    unittest.main()
