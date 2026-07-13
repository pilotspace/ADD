#!/usr/bin/env python3
"""Red/green tests for ground-context-sources — broaden the §0 GROUND gather.

The ground phase gathers more than code: the `3-plan.md` guide's `## Gather`
section and the `## 0 · GROUND` TASK.md template name the working-folder context
categories — docs/textbase · TODOs · config/manifests · data/fixtures — beyond the
existing code Touches. Frozen shape (§3 @ v1):
  - 3-plan.md `## Gather` gains a "Context (working folder)" bullet enumerating
    docs/textbase · TODOs · config/manifests · data/fixtures (task-delta only);
  - TASK.md.tmpl `## 0 · GROUND` gains ONE light `Context (working folder):` line
    between Touches and Honors;
  - INVARIANTS preserved: the `Anchors the contract cites:` line (the grounding
    measure keys on it), `## 0`/`GROUND`, the guide saying gather/codebase, and the
    add.py engine byte-identical to engine_pin (no measure edit);
  - SYNC: 3-plan.md ×3 (skill trees) and TASK.md.tmpl ×3 (template trees) stay
    byte-identical.

Behavior pinned, not prose phrasing. ASCII-safe asserts where possible.
Run: python3 -m unittest test_ground_context -v
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

# The ground phase guide — 3 skill trees, must stay byte-identical.
GUIDE_COPIES = [
    _ADD_METHOD / "skill" / "add" / "phases" / "3-plan.md",
    _REPO / ".claude" / "skills" / "add" / "phases" / "3-plan.md",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "3-plan.md",
]

# The TASK.md template — 3 template trees, must stay byte-identical.
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

# The four working-folder context categories the gather must name (keyword per category).
CATEGORY_KEYWORDS = ["textbase", "todo", "config", "fixture"]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _canonical_guide() -> str:
    return GUIDE_COPIES[0].read_text(encoding="utf-8")


def _canonical_tmpl() -> str:
    return TMPL_COPIES[0].read_text(encoding="utf-8")


def _section0(tmpl: str) -> str:
    """The `## 0 · GROUND` ... up to the next `## 1 ` heading."""
    m = re.search(r"## 0 .*?GROUND.*?(?=\n## 1 )", tmpl, flags=re.S)
    return m.group(0) if m else ""


def _grounding_block(tmpl: str) -> str:
    """plan-phase-core: grounding moved from `## 0 · GROUND` into `## 3 · PLAN`'s
    `### Grounding` sub-block (up to the next `### `/`## ` heading, i.e. `### Contract`)."""
    m = re.search(r"### Grounding\b.*?(?=\n(?:### |## ))", tmpl, flags=re.S)
    return m.group(0) if m else ""


class GuideBroadensGather(unittest.TestCase):
    """3-plan.md `## Gather` names the working-folder context categories."""

    def test_guide_names_context_working_folder(self):
        low = _canonical_guide().lower()
        self.assertIn("context (working folder)", low,
                      "the guide must name the 'Context (working folder)' gather category")

    def test_guide_lists_all_four_categories(self):
        low = _canonical_guide().lower()
        for kw in CATEGORY_KEYWORDS:
            self.assertIn(kw, low,
                          f"the guide's gather must name the {kw!r} working-folder category")

    def test_guide_keeps_existing_structure(self):
        text = _canonical_guide()
        for anchor in ("Touches", "Honors", "Anchors"):
            self.assertIn(anchor, text, f"the guide must keep the {anchor} field")

    def test_guide_still_cues_gathering_the_codebase(self):
        # test_ground_phase invariant: the guide still cues gather/codebase.
        low = _canonical_guide().lower()
        self.assertIn("ground", low)
        self.assertTrue("gather" in low or "codebase" in low,
                        "the guide must still cue gathering the codebase")


class TemplateGainsContextLine(unittest.TestCase):
    """TASK.md.tmpl carries the light Context line; invariants preserved.

    plan-phase-core: re-pointed from the removed `## 0 · GROUND` section to the
    `## 3 · PLAN` section's `### Grounding` sub-block (_grounding_block)."""

    def test_section0_has_context_line(self):
        grounding = _grounding_block(_canonical_tmpl())
        self.assertTrue(grounding, "the template must have a `### Grounding` sub-block (§3 PLAN)")
        self.assertIn("Context (working folder):", grounding,
                      "§3 PLAN Grounding must carry the light `Context (working folder):` line")

    def test_section0_preserves_anchors_line(self):
        # The grounding measure (_grounded_state) keys on this exact line.
        grounding = _grounding_block(_canonical_tmpl())
        self.assertIn("Anchors the contract cites:", grounding,
                      "the §3 PLAN grounding measure line must be preserved verbatim")

    def test_section0_keeps_heading_tokens(self):
        tmpl = _canonical_tmpl()
        self.assertIn("## 3 · PLAN", tmpl, "the §3 PLAN heading must be preserved")
        self.assertIn("### Grounding", _grounding_block(tmpl),
                      "the Grounding sub-block heading must be preserved")


class CopiesStayByteIdentical(unittest.TestCase):
    """The ×3 guide and ×3 template copies stay md5-identical (dogfood parity)."""

    def test_guide_copies_byte_identical(self):
        present = [p for p in GUIDE_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "all 3 skill 3-plan.md copies must exist")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 3-plan.md copies must be byte-identical")

    def test_template_copies_byte_identical(self):
        present = [p for p in TMPL_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "all 3 TASK.md.tmpl copies must exist")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 TASK.md.tmpl copies must be byte-identical")


class EngineMeasureUntouched(unittest.TestCase):
    """The grounding measure is out of scope — add.py must not change."""

    def test_engine_byte_identical_to_pin(self):
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match engine_pin.ENGINE_MD5 (no measure edit this task)")


class GatherMethodHint(unittest.TestCase):
    """3-plan.md carries the gather-METHOD hint (subagent/skim sweep + deepen)."""

    def test_guide_recommends_subagent_sweep(self):
        low = _canonical_guide().lower()
        self.assertIn("subagent", low,
                      "the guide must recommend a subagent for the broad sweep")
        self.assertTrue("index" in low or "skim" in low,
                        "the guide must offer a fast index / skim sweep")

    def test_guide_says_deepen_task_specifically(self):
        low = _canonical_guide().lower()
        self.assertIn("deepen", low,
                      "the guide must say to deepen on what THIS task needs")

    def test_intro_names_working_folder(self):
        # task-1 §7 coherence: the intro names the broadened gather, not only "codebase".
        intro = _canonical_guide().split("## Gather", 1)[0].lower()
        self.assertIn("working folder", intro,
                      "the guide intro must name the broadened 'working folder' gather")


if __name__ == "__main__":
    unittest.main(verbosity=2)
