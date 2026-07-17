#!/usr/bin/env python3
"""Red/green tests for the milestone-level `## Ground` seed (task milestone-ground-seed).

Expectations-first, lever 2: a milestone gains a thin `## Ground` section — shared
real-code context gathered ONCE — that each task's `specify` projects its §1
expectations from, so tasks stop re-grounding shared context per task. Prose/
template-only (a heavy milestone-ground validator is deferred per the milestone Out);
the engine digest must NOT change.

  * template — MILESTONE.md.tmpl (×3 trees) carries `## Ground` right after `## Scope`,
               before `## Shared decisions`, with four milestone-altitude field labels.
  * guide    — phases/direction.md (×3 skill trees) cues projecting §1 from the
               milestone Ground + the request.
  * drafting — scope.md (×3) names the Ground section among the MILESTONE.md sections.
  * engine   — UNTOUCHED: md5(add.py) == engine_pin.ENGINE_MD5 (prose-only guard).

    cd add-method/tooling && python3 -m unittest test_milestone_ground -v
"""
import hashlib
import unittest
from pathlib import Path

from engine_pin import ENGINE_MD5

HERE = Path(__file__).resolve().parent          # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

# The 3 MILESTONE.md.tmpl copies (the `.add/` one is a gitignored dogfood twin —
# present in this repo and byte-parity-pinned, but exists()-skipped to stay honest).
MILE_TMPL_COPIES = [
    HERE / "templates" / "MILESTONE.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "MILESTONE.md.tmpl",
    BUNDLE / "tooling" / "templates" / "MILESTONE.md.tmpl",
]
SPECIFY_GUIDE_COPIES = [
    ADD_METHOD / "skill" / "add" / "phases" / "direction.md",
    REPO / ".claude" / "skills" / "add" / "phases" / "direction.md",
    BUNDLE / "skill" / "add" / "phases" / "direction.md",
]
SCOPE_GUIDE_COPIES = [
    ADD_METHOD / "skill" / "add" / "scope.md",
    REPO / ".claude" / "skills" / "add" / "scope.md",
    BUNDLE / "skill" / "add" / "scope.md",
]
CANON_TMPL = MILE_TMPL_COPIES[0]
CANON_SPECIFY = SPECIFY_GUIDE_COPIES[0]
CANON_SCOPE = SCOPE_GUIDE_COPIES[0]

# The four milestone-altitude field labels the frozen §3 contract (v2) names.
# v2: `Honors (conventions):` replaced v1 `Conventions/Seams:` — the bare word tripped
# the ubiquitous-language slang guard on the template surface.
GROUND_FIELDS = (
    "Touches (shared files · symbols):",
    "Anchors:",
    "Honors (conventions):",
    "Issues/Risks (shared):",
)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _ground_block(text: str) -> str:
    """The `## Ground` section body — from its heading to the next `## ` heading."""
    if "## Ground" not in text:
        return ""
    after = text.split("## Ground", 1)[1]
    return after.split("\n## ", 1)[0]


class MilestoneGroundSectionTest(unittest.TestCase):
    def test_ground_section_present(self):                       # M1 / R1
        self.assertIn("## Ground", CANON_TMPL.read_text(encoding="utf-8"),
                      "MILESTONE.md.tmpl must carry a `## Ground` section (milestone_ground_absent)")

    def test_ground_placed_after_scope_before_shared_decisions(self):   # M1
        text = CANON_TMPL.read_text(encoding="utf-8")
        i_scope = text.find("## Scope")
        i_ground = text.find("## Ground")
        i_shared = text.find("## Shared decisions")
        self.assertNotEqual(i_scope, -1, "no ## Scope heading")
        self.assertNotEqual(i_ground, -1, "no ## Ground heading")
        self.assertNotEqual(i_shared, -1, "no ## Shared decisions heading")
        self.assertLess(i_scope, i_ground, "## Ground must come AFTER ## Scope")
        self.assertLess(i_ground, i_shared, "## Ground must come BEFORE ## Shared decisions")

    def test_ground_is_thin_with_altitude_vocabulary(self):     # M2
        block = _ground_block(CANON_TMPL.read_text(encoding="utf-8"))
        self.assertTrue(block, "no ## Ground block found")
        for field in GROUND_FIELDS:
            self.assertIn(field, block, f"the ## Ground section must carry the `{field}` line")

    def test_ground_is_not_a_per_task_table(self):              # M2
        block = _ground_block(CANON_TMPL.read_text(encoding="utf-8"))
        self.assertNotIn("- [ ]", block,
                         "## Ground is THIN shared context, never a per-task grounding table")

    def test_ground_names_gathered_once(self):                  # M2 semantic
        block = _ground_block(CANON_TMPL.read_text(encoding="utf-8")).lower()
        self.assertIn("once", block,
                      "the ## Ground heading/body must say it is gathered ONCE (shared, not per-task)")

    def test_milestone_tmpl_byte_identical(self):               # M6 / R2
        present = [p for p in MILE_TMPL_COPIES if p.exists()]
        self.assertTrue(CANON_TMPL.exists(), "canonical MILESTONE.md.tmpl missing")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the MILESTONE.md.tmpl copies must be byte-identical (milestone_tmpl_drift)")


class SpecifyGuideCueTest(unittest.TestCase):
    def test_specify_guide_cues_projecting_from_milestone_ground(self):     # M3
        low = CANON_SPECIFY.read_text(encoding="utf-8").lower()
        self.assertIn("ground", low, "the specify guide must name the milestone Ground")
        self.assertIn("project", low,
                      "the specify guide must cue PROJECTING the §1 expectations from the milestone Ground")

    def test_specify_guide_byte_identical(self):                # M6 / R2
        present = [p for p in SPECIFY_GUIDE_COPIES if p.exists()]
        self.assertTrue(CANON_SPECIFY.exists(), "canonical 1-specify.md missing")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 phases/direction.md copies must be byte-identical")


class ScopeGuideDraftsGroundTest(unittest.TestCase):
    def test_scope_guide_names_ground_section(self):            # M4
        # scope.md already GROUNDS the goal (the "Position the goal" step) but discards it;
        # this task makes that grounding PERSIST as the MILESTONE's `## Ground` section.
        # Require the literal section reference, not the incidental "ground" substring.
        text = CANON_SCOPE.read_text(encoding="utf-8")
        self.assertIn("## Ground", text,
                      "scope.md must name the `## Ground` section it drafts (not just 'ground the goal')")

    def test_scope_guide_byte_identical(self):                  # M6 / R2
        present = [p for p in SCOPE_GUIDE_COPIES if p.exists()]
        self.assertTrue(CANON_SCOPE.exists(), "canonical scope.md missing")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 scope.md copies must be byte-identical")


class EngineUntouchedTest(unittest.TestCase):
    def test_engine_untouched(self):                            # M5 / R3
        for p in (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
                  BUNDLE / "tooling" / "add.py"):
            if p.exists():
                self.assertEqual(hashlib.md5(p.read_bytes()).hexdigest(), ENGINE_MD5,
                                 f"prose/template-only task must not touch the engine: {p} (engine_touched)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
