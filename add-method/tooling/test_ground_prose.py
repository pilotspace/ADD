#!/usr/bin/env python3
"""Red/green tests for the ground-phase prose alignment (task ground-prose-align).

The engine ships the `ground` phase (ground-phase-engine) and wires its measure
(ground-bundle-wiring). This task makes the PROSE name it — prose ≡ enforcement —
rendering `ground` as the §0 preamble to the seven steps, byte-synced across trees,
WITHOUT touching the engine (prose-only):

  * book   — docs/02-the-flow.md names ground as the phase-0 preamble (×4 synced);
             docs/appendix-c-glossary.md defines **Ground** + **Grounding map** (×4).
  * skill  — SKILL.md's phase table lists a `plan` row → phases/3-plan.md (×3).
  * GLOSSARY— the survivor .add/GLOSSARY.md + the GLOSSARY.md.tmpl name ground (×3).
  * engine — UNTOUCHED: md5(add.py) ×3 == engine_pin (prose-only guard).

    cd add-method/tooling && python3 -m unittest test_ground_prose -v
"""
import hashlib
import re
import unittest
from pathlib import Path

from engine_pin import ENGINE_MD5

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"


def _doc_trees(fname: str) -> list[Path]:
    """The 4 book copies: root · canonical (add-method/docs) · bundle · dogfood (.add/docs)."""
    return [REPO / fname, ADD_METHOD / "docs" / fname,
            BUNDLE / "docs" / fname, REPO / ".add" / "docs" / fname]


FLOW = ADD_METHOD / "docs" / "02-the-flow.md"            # canonical content source
BOOK_GLOSSARY = ADD_METHOD / "docs" / "appendix-c-glossary.md"
SKILL_TREES = [ADD_METHOD / "skill" / "add" / "SKILL.md",
               REPO / ".claude" / "skills" / "add" / "SKILL.md",
               BUNDLE / "skill" / "add" / "SKILL.md"]
TMPL_TREES = [ADD_METHOD / "tooling" / "templates" / "GLOSSARY.md.tmpl",
              REPO / ".add" / "tooling" / "templates" / "GLOSSARY.md.tmpl",
              BUNDLE / "tooling" / "templates" / "GLOSSARY.md.tmpl"]
SURVIVOR = REPO / ".add" / "GLOSSARY.md"


def _strip_mermaid(text: str) -> str:
    return re.sub(r"```mermaid\n.*?```", "", text, flags=re.DOTALL)


class FlowChapterTest(unittest.TestCase):
    def test_flow_chapter_names_grounding_in_plan(self):
        # plan-phase-core: grounding is no longer a §0 preamble — it is the first part of the
        # Plan phase. The prose must still NAME grounding + the plan phase (outside the mermaid).
        prose = _strip_mermaid(FLOW.read_text(encoding="utf-8")).lower()
        self.assertIn("grounding", prose, "ch02 prose must name grounding")
        self.assertIn("plan", prose, "ch02 prose must name the plan phase (grounding folds into it)")
        # the seven-step brand is preserved (specify..observe; grounding is Plan's first part, not a step)
        self.assertIn("seven steps", FLOW.read_text(encoding="utf-8").lower())

    def test_flow_chapter_synced_x4(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest()
                   for p in _doc_trees("02-the-flow.md") if p.exists()}
        self.assertEqual(len(digests), 1, "02-the-flow.md differs across trees")


class BookGlossaryTest(unittest.TestCase):
    def test_book_glossary_defines_ground(self):
        text = BOOK_GLOSSARY.read_text(encoding="utf-8")
        self.assertRegex(text, r"\*\*Ground\b", "appendix-c must define a **Ground** term")
        self.assertRegex(text, r"\*\*Grounding map\b",
                         "appendix-c must define a **Grounding map** term")

    def test_book_glossary_synced_x4(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest()
                   for p in _doc_trees("appendix-c-glossary.md") if p.exists()}
        self.assertEqual(len(digests), 1, "appendix-c-glossary.md differs across trees")


# ---- book-plan-align (expectations-first T4): the GLOSSARY names the Plan phase, --------
# ---- Ground is redefined as Plan's first part, and no stale phase-model prose survives. --

# LIVE stale phase-model framings the expectations-first flow retired (grounding is Plan's
# first PART, the contract is a sub-block of Plan — neither is a live phase). Emphasis is
# stripped before matching so `*before*` still reads as "before". A historical "(formerly
# the ground phase)" bridge is NOT forbidden — the guard targets only LIVE framing.
_STALE_PHASE_PROSE = (
    "phase-0 preamble",
    "the contract phase",
    "the ground phase",
    "as step 0",
    "phase before specify",
)


def _deemphasize(text: str) -> str:
    return text.replace("*", "").replace("_", "").lower()


def _stale_phase_hits(text: str) -> list[str]:
    """LIVE stale phase-model framings in `text`, per line. A line marked as a history
    bridge ('formerly …') is exempt — the guard targets the LIVE definition, not the past
    (R3). Emphasis is stripped so `*before*` still reads as 'before'."""
    hits = []
    for line in text.splitlines():
        low = _deemphasize(line)
        if "formerly" in low:                 # history bridge — not a live-phase claim
            continue
        for stale in _STALE_PHASE_PROSE:
            if stale in low:
                hits.append(f"{stale!r} in: {line.strip()[:70]}")
    return hits


class PlanPhaseGlossaryTest(unittest.TestCase):
    """T4: the book glossary names the unified Plan phase; Ground is its first part."""

    def test_book_glossary_defines_plan(self):                      # M1
        text = BOOK_GLOSSARY.read_text(encoding="utf-8")
        self.assertRegex(text, r"\*\*Plan\b",
                         "appendix-c must define a **Plan** phase term (the unified step 3)")
        # the definition must convey the three things Plan does + the one approval
        plan_para = next((ln for ln in text.splitlines() if ln.startswith("**Plan")), "")
        low = plan_para.lower()
        self.assertIn("ground", low, "the **Plan** term must name grounding as its first part")
        self.assertTrue("freeze" in low or "frozen" in low,
                        "the **Plan** term must name freezing the contract")
        self.assertTrue("one" in low or "single" in low,
                        "the **Plan** term must name the ONE human approval (the plan freeze)")

    def test_ground_term_is_plan_first_part_not_phase_zero(self):   # M2
        ground = next((ln for ln in BOOK_GLOSSARY.read_text(encoding="utf-8").splitlines()
                       if ln.startswith("**Ground")), "")
        self.assertTrue(ground, "appendix-c must still define a **Ground** term")
        low = _deemphasize(ground)
        self.assertIn("plan", low, "the **Ground** term must place grounding inside the Plan phase")
        for stale in ("phase-0 preamble", "as step 0", "phase before specify"):
            self.assertNotIn(stale, low,
                             f"the **Ground** term still carries the retired framing {stale!r}")

    def test_no_stale_phase_prose_in_book(self):                    # M3
        offenders = []
        for md in sorted((ADD_METHOD / "docs").glob("*.md")):
            for hit in _stale_phase_hits(md.read_text(encoding="utf-8")):
                offenders.append(f"{md.name}: {hit}")
        self.assertEqual([], offenders,
                         f"stale phase-model prose survives in the book: {offenders}")

    def test_grep_guard_allows_legitimate_prose(self):             # R3
        # the guard passes live-flow prose + a 'formerly …' history bridge…
        for ok in ("Grounding is the first part of Plan.",
                   "This was formerly the ground phase; now grounding folds into Plan.",
                   "The contract is frozen within the Plan phase."):
            self.assertEqual([], _stale_phase_hits(ok),
                             f"guard false-flags legitimate prose: {ok!r}")
        # …but still catches a LIVE stale claim (the guard is not vacuous)
        self.assertTrue(_stale_phase_hits("Ground precedes the seven steps as step 0."),
                        "the guard must still catch a live stale-phase claim")


class EngineUntouchedByBookAlignTest(unittest.TestCase):
    def test_engine_md5_unchanged(self):                           # R2
        got = hashlib.md5((ADD_METHOD / "tooling" / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, ENGINE_MD5,
                         "book-plan-align is docs-only — add.py must be byte-identical to the pin")



class SkillTableTest(unittest.TestCase):
    def test_skill_phase_table_lists_plan(self):
        # expectations-first (guides-and-skill): the phase table names `plan`, not `ground`/`contract`.
        text = SKILL_TREES[0].read_text(encoding="utf-8")
        self.assertRegex(text, r"\|\s*plan\s*\|", "SKILL.md phase table needs a 'plan' row")
        self.assertIn("phases/3-plan.md", text, "the plan row points at its guide")
        self.assertNotRegex(text, r"\|\s*ground\s*\|", "no stale 'ground' phase row")
        self.assertNotRegex(text, r"\|\s*contract\s*\|", "no stale 'contract' phase row")

    def test_skill_synced_x3(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in SKILL_TREES}
        self.assertEqual(len(digests), 1, "SKILL.md differs across the 3 skill trees")


class GlossaryTest(unittest.TestCase):
    def test_survivor_names_ground_first(self):
        text = SURVIVOR.read_text(encoding="utf-8")
        self.assertRegex(text, r"Phase:.*\bground,\s*specify",
                         "the survivor Phase line must list 'ground' first")
        self.assertRegex(text, r"(?im)^ground:", "the survivor must define a 'ground' term")
        self.assertRegex(text, r"(?im)^grounding map",
                         "the survivor must define a 'grounding map' term")

    def test_template_names_ground(self):
        text = TMPL_TREES[0].read_text(encoding="utf-8")
        self.assertIn("ground", text.lower(), "the GLOSSARY template must name ground")
        self.assertIn("grounding map", text.lower())

    def test_template_synced_x3(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in TMPL_TREES}
        self.assertEqual(len(digests), 1, "GLOSSARY.md.tmpl differs across the 3 trees")


class EngineUntouchedTest(unittest.TestCase):
    def test_engine_untouched(self):
        for p in (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
                  BUNDLE / "tooling" / "add.py"):
            self.assertEqual(hashlib.md5(p.read_bytes()).hexdigest(), ENGINE_MD5,
                             f"prose-only task must not touch the engine: {p}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
