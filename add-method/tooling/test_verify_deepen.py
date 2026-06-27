#!/usr/bin/env python3
"""Red/green tests for verify-deepen (v20) - deepen the Verify rubric.

A gate must prove the work is real, not merely plausible:
  - for a task that produced code: recorded evidence that every new symbol is
    referenced (wiring) and that no new dead/unused code was introduced;
  - for a task that produced prose/non-code: a recorded semantic no-skim read.

The requirement is stated IDENTICALLY in the skill guide (phases/6-verify.md),
the book (docs/08-step-6-verify.md), and run.md's automated-quality-gate list,
and carried as an additive "Deep checks" block in the section-6 TASK.md template.
This is rubric + template only: add.py is byte-unchanged (engine stays
judgment-free; the resolver, not the engine, judges code-vs-prose).

ASCII-safe asserts (house rule): anchors are contiguous ASCII substrings of the
frozen canonical wording, so drift between surfaces shows up as a missing anchor.

Run: python3 -m unittest test_verify_deepen -v
"""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

import engine_pin

_TOOLING = Path(__file__).resolve().parent              # add-method/tooling
_ADD_METHOD = _TOOLING.parent                           # add-method
_REPO = _ADD_METHOD.parent                              # repo root

# The three prose surfaces the rubric must state identically (canonical copies).
GUIDE = _ADD_METHOD / "skill" / "add" / "phases" / "6-verify.md"
RUN_MD = _ADD_METHOD / "skill" / "add" / "run.md"
BOOK = _ADD_METHOD / "docs" / "08-step-6-verify.md"
# Template + glossary (canonical), and the engine the lean scope must NOT touch.
TASK_TMPL = _ADD_METHOD / "tooling" / "templates" / "TASK.md.tmpl"
GLOSSARY_TMPL = _ADD_METHOD / "tooling" / "templates" / "GLOSSARY.md.tmpl"
ADD_PY = _ADD_METHOD / "tooling" / "add.py"
# Mirror copies (for the focused template-parity guard).
DOGFOOD_TMPL = _REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl"
BUNDLE_TMPL = _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl"
LIVING_GLOSSARY = _REPO / ".add" / "GLOSSARY.md"

# Contiguous ASCII substrings of the frozen canonical wording. Each must appear
# VERBATIM in all three surfaces; a missing anchor in any one is rubric_drift.
DEEP_ANCHORS = [
    "do not skim",
    "If the task produced code, record that every new symbol is referenced (wiring) "
    "and that no new dead/unused code was introduced.",
    "If it produced prose or non-code, record a semantic read",
    "the engine never classifies",
]

# Pre-existing section-6 checklist lines that must survive the additive change.
SIX_EXISTING = [
    "all tests pass",
    "coverage did not decrease",
    "no test or contract was altered during build",
    "concurrency / timing of the risky operation is safe",
    "no exposed secrets, injection openings, or unexpected dependencies",
    "layering & dependencies follow CONVENTIONS.md",
    "a person reviewed and approved the change",
    "### GATE RECORD",
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _norm(text: str) -> str:
    """Collapse all whitespace (incl. markdown hard-wraps) to single spaces.

    "Stated identically" means the same WORDING, not the same line breaks — each
    surface hard-wraps the canonical sentence at its own column. Normalizing lets
    the drift sentinel test word-sequence identity, which is the real invariant.
    """
    return " ".join(text.split())


class VerifyDeepenTest(unittest.TestCase):

    # --- per-surface content (one per Must) ---------------------------------
    def test_guide_has_deepcheck_rubric(self):
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("do not skim", text)
        self.assertIn("referenced (wiring)", text)
        self.assertIn("semantic read", text)

    def test_book_has_deepcheck_rubric(self):
        text = BOOK.read_text(encoding="utf-8")
        self.assertIn("do not skim", text)
        self.assertIn("referenced (wiring)", text)
        self.assertIn("semantic read", text)

    def test_runmd_autogate_has_deepcheck(self):
        text = RUN_MD.read_text(encoding="utf-8")
        self.assertIn("referenced (wiring)", text)
        self.assertIn("semantic read", text)

    # --- stated identically across surfaces (rubric_drift) ------------------
    def test_rubric_stated_identically(self):
        surfaces = {
            "guide": _norm(GUIDE.read_text(encoding="utf-8")),
            "book": _norm(BOOK.read_text(encoding="utf-8")),
            "run.md": _norm(RUN_MD.read_text(encoding="utf-8")),
        }
        for anchor in DEEP_ANCHORS:
            anchor = _norm(anchor)
            for name, text in surfaces.items():
                self.assertIn(
                    anchor, text,
                    f"rubric_drift: deep-check anchor missing from {name}: {anchor!r}",
                )

    # --- the section-6 template block (additive) ---------------------------
    def test_template_has_deepchecks_block(self):
        text = TASK_TMPL.read_text(encoding="utf-8")
        six = text.split("## 6 ")[1].split("## 7 ")[0]
        self.assertIn("Deep checks", six)
        self.assertIn("WIRING", six)
        self.assertIn("DEAD-CODE", six)
        self.assertIn("SEMANTIC", six)
        # the block sits inside section 6, before the gate record
        self.assertLess(six.index("Deep checks"), six.index("GATE RECORD"),
                        "Deep checks block must precede the GATE RECORD")

    def test_template_deepchecks_additive(self):
        text = TASK_TMPL.read_text(encoding="utf-8")
        for line in SIX_EXISTING:
            self.assertIn(line, text, f"seam_broken: existing section-6 line vanished: {line!r}")

    def test_template_triplet_identical(self):
        copies = [p for p in (DOGFOOD_TMPL, TASK_TMPL, BUNDLE_TMPL) if p.exists()]
        if len(copies) < 2:
            self.skipTest("fewer than two template trees present (bare package)")
        self.assertEqual(len({_md5(p) for p in copies}), 1,
                         "TASK.md.tmpl copies diverged across trees")

    # --- glossary term ------------------------------------------------------
    def test_glossary_defines_deep_verify(self):
        checked = 0
        for path in (GLOSSARY_TMPL, LIVING_GLOSSARY):
            if not path.exists():
                continue
            checked += 1
            terms = [l for l in path.read_text(encoding="utf-8").splitlines()
                     if l.lower().startswith("deep verify:")]
            self.assertTrue(terms, f"{path.name} must define a 'deep verify' term")
            self.assertIn("wiring", terms[0].lower())
            self.assertIn("semantic", terms[0].lower())
        self.assertGreater(checked, 0, "no glossary present to check")

    # --- the lean-scope guard: the engine is byte-unchanged -----------------
    def test_engine_unchanged(self):
        self.assertEqual(
            _md5(ADD_PY), engine_pin.ENGINE_MD5,
            "verify-deepen is rubric+template only - add.py must stay byte-identical "
            "to the pinned engine (no engine logic in this task)",
        )
        src = ADD_PY.read_text(encoding="utf-8")
        # NOTE: guarantee-audit-lints (flow-honesty M3) added a PRESENCE-ONLY `shallow_deep_check`
        # audit notice that NAMES the "### Deep checks" block to surface an unfilled one. The engine
        # may now reference the block HEADING for that lint — but the original invariant holds where
        # it matters: the engine embeds NONE of the deep-check CONTENT tokens (WIRING/DEAD-CODE/
        # SEMANTIC) and renders no verdict — presence via _section_unfilled, never judgment.
        self.assertNotIn("WIRING", src, "no deep-verify CONTENT token belongs in the engine")
        self.assertNotIn("DEAD-CODE", src, "no deep-verify CONTENT token belongs in the engine")

    # --- the rubric names the shallow-verify reject (verify_shallow) --------
    def test_verify_shallow_named(self):
        guide = GUIDE.read_text(encoding="utf-8").lower()
        self.assertIn("shallow verify", guide,
                      "the guide must name an unfilled deep-check block as a shallow verify, not a pass")


if __name__ == "__main__":
    unittest.main(verbosity=2)
