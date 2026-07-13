#!/usr/bin/env python3
"""Red/green tests for the freeze review checklist (task review-checklist, v14).

The seam guide (phases/3-plan.md) presents a SEVEN-item checklist that aims
the human's one approval — ⚠-first, with an explicit high-risk declaration
prompt and a grounding check — without re-adding ceremony: ≤16 lines, never a
second gate, engine byte-identical. Run:
    python3 -m unittest test_review_checklist -v
"""
import hashlib
import md_section
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BUNDLE = HERE.parent / "src" / "add_method" / "_bundled"

CONTRACT_MD = HERE.parent / "skill" / "add" / "phases" / "3-plan.md"
RUN_MD = HERE.parent / "skill" / "add" / "run.md"

HEADING = "## The freeze review checklist"
# the engine must not change in this prose-only task (scope-creep guard)
from engine_pin import ENGINE_MD5


def _section() -> str | None:
    """The checklist section body (heading to next heading), or None."""
    text = CONTRACT_MD.read_text(encoding="utf-8")
    return md_section.section(text, HEADING) or None


class ChecklistTest(unittest.TestCase):
    def test_seam_guide_presents_checklist(self):
        sec = _section()
        self.assertIsNotNone(sec, f"{HEADING} missing from 3-plan.md")
        items = [ln for ln in sec.splitlines() if ln.lstrip().startswith("- **")]
        # v(ground-bundle-wiring): the checklist grew six -> seven — the **Grounded** item
        # was added after **Shape** (the ⚠-first + exact-count shape is unchanged).
        self.assertEqual(len(items), 7, f"exactly seven items, got {len(items)}")
        self.assertIn("⚠", items[0], "the least-sure flags must be item ONE")

    def test_risk_prompt_names_the_tokens(self):
        sec = _section()
        self.assertIsNotNone(sec)
        self.assertIn("high-risk", sec)
        self.assertIn("`risk: high · autonomy: conservative`", sec,
                      "the exact header tokens must be named at the prompt")

    def test_no_ceremony(self):
        sec = _section()
        self.assertIsNotNone(sec)
        nonblank = [ln for ln in sec.splitlines() if ln.strip()]
        self.assertLessEqual(len(nonblank), 16,
                             f"checklist bloated to {len(nonblank)} lines — "
                             "it must stay the human's one minute")
        self.assertIn("the freeze stays the only gate", sec,
                      "the anti-ceremony clause must be stated")
        # needle updated by ratified CR-2 (rewrite-guides, 2026-06-07): the clause was
        # positivized "never a second gate" -> "the freeze stays the only gate" (v17 rubric);
        # the guard's intent — the anti-ceremony clause must be stated — is unchanged.

    def test_run_md_accord(self):
        self.assertIn("freeze review checklist",
                      RUN_MD.read_text(encoding="utf-8"),
                      "run.md's one-approval front must point at the checklist")

    def test_three_trees_agree(self):
        for rel in (("skill", "add", "phases", "3-plan.md"),
                    ("skill", "add", "run.md")):
            canon = HERE.parent.joinpath(*rel)
            for twin in (REPO / ".claude" / "skills" / "add" / Path(*rel[2:]),
                         BUNDLE.joinpath(*rel)):
                self.assertEqual(canon.read_bytes(), twin.read_bytes(),
                                 f"divergence: {twin}")

    def test_engine_untouched(self):
        for p in (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
                  BUNDLE / "tooling" / "add.py"):
            self.assertEqual(hashlib.md5(p.read_bytes()).hexdigest(), ENGINE_MD5,
                             f"prose-only task must not touch the engine: {p}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
