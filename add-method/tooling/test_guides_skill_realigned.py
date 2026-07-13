#!/usr/bin/env python3
"""Red/green tests for the guides-and-skill realignment (task guides-and-skill).

expectations-first, lever 3: the phase guides + SKILL.md (+ the engine's plan→book-chapter
ref + the book PATH cascade) move to the 8-phase flow. `phases/0-ground.md` and
`phases/3-contract.md` retire into a unified `phases/3-plan.md`; the book chapter
`05-step-3-contract.md` is renamed to `05-step-3-plan.md` and every path reference follows.
Deep book NARRATIVE (the word "contract" as a concept · the GLOSSARY term · the diagram) stays T4.

    cd add-method/tooling && python3 -m unittest test_guides_skill_realigned -v
"""
import hashlib
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent          # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

SKILL_TREES = [ADD_METHOD / "skill" / "add",
               REPO / ".claude" / "skills" / "add",
               BUNDLE / "skill" / "add"]
BOOK_TREES = [ADD_METHOD / "docs", REPO, REPO / ".add" / "docs", BUNDLE / "docs"]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class PlanGuideExistsTest(unittest.TestCase):
    def test_3_plan_guide_exists_and_covers_the_three_parts(self):   # M1
        canon = SKILL_TREES[0] / "phases" / "3-plan.md"
        self.assertTrue(canon.exists(), "phases/3-plan.md must exist (the unified plan guide)")
        low = canon.read_text(encoding="utf-8").lower()
        for part in ("ground", "contract", "build"):
            self.assertIn(part, low, f"3-plan.md must cover the {part} part of the plan phase")

    def test_3_plan_guide_byte_identical_x3(self):                   # M1
        digests = {_md5(t / "phases" / "3-plan.md") for t in SKILL_TREES
                   if (t / "phases" / "3-plan.md").exists()}
        present = [t for t in SKILL_TREES if (t / "phases" / "3-plan.md").exists()]
        self.assertEqual(len(present), 3, "3-plan.md must exist in all 3 skill trees")
        self.assertEqual(len(digests), 1, "the 3 phases/3-plan.md copies must be byte-identical")


class OldGuidesRetiredTest(unittest.TestCase):
    def test_ground_and_contract_guides_deleted(self):              # M2 / R2
        for t in SKILL_TREES:
            for old in ("phases/0-ground.md", "phases/3-contract.md"):
                self.assertFalse((t / old).exists(),
                                 f"retired guide still present: {t / old}")


class SkillTableTest(unittest.TestCase):
    def test_skill_names_plan_not_ground_or_contract(self):         # M3 / R2
        for t in SKILL_TREES:
            text = (t / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(text, r"\|\s*plan\s*\|", f"{t}/SKILL.md needs a 'plan' phase row")
            self.assertIn("phases/3-plan.md", text, "the plan row points at its guide")
            self.assertNotRegex(text, r"\|\s*ground\s*\|", f"{t}/SKILL.md has a stale 'ground' row")
            self.assertNotRegex(text, r"\|\s*contract\s*\|", f"{t}/SKILL.md has a stale 'contract' row")


class EngineBookRefTest(unittest.TestCase):
    def test_engine_plan_chapter_renamed(self):                    # M4 / R3
        import importlib
        constants = importlib.import_module("add_engine.constants")
        _, chapter = constants.PHASE_GUIDE["plan"]
        self.assertEqual(chapter, "05-step-3-plan.md",
                         "PHASE_GUIDE['plan'] must point at the renamed chapter")

    def test_renamed_chapter_exists_x4(self):                      # M4
        present = [t / "05-step-3-plan.md" for t in BOOK_TREES if (t / "05-step-3-plan.md").exists()]
        self.assertTrue((BOOK_TREES[0] / "05-step-3-plan.md").exists(),
                        "canonical docs/05-step-3-plan.md must exist")
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "the book copies of 05-step-3-plan.md must be byte-identical")

    def test_old_chapter_gone_x4(self):                            # M4 / R3
        for t in BOOK_TREES:
            self.assertFalse((t / "05-step-3-contract.md").exists(),
                             f"old chapter still present: {t / '05-step-3-contract.md'}")


class NoStalePathTest(unittest.TestCase):
    def test_no_05_step_3_contract_path_survives(self):            # M4 / M6
        # the PATH cascade must be complete: mkdocs nav + every cross-linking chapter moved.
        hits = []
        roots = [ADD_METHOD / "docs", BUNDLE / "docs", REPO / ".add" / "docs",
                 ADD_METHOD, REPO / "mkdocs.yml"]
        scan = []
        scan += [REPO / "mkdocs.yml"]
        for d in (ADD_METHOD / "docs", BUNDLE / "docs", REPO / ".add" / "docs"):
            if d.exists():
                scan += sorted(d.glob("*.md"))
        # repo-root book copies
        scan += sorted(REPO.glob("*.md"))
        scan += [ADD_METHOD / "GETTING-STARTED.md",
                 ADD_METHOD / "agents" / "add-design.md",
                 BUNDLE / "agents" / "add-design.md"]
        for p in scan:
            if p.exists() and "05-step-3-contract" in p.read_text(encoding="utf-8"):
                hits.append(str(p.relative_to(REPO)))
        self.assertEqual(hits, [], f"stale '05-step-3-contract' path in: {hits}")


class NoStalePhaseProseTest(unittest.TestCase):
    def test_guides_and_skill_have_no_ground_first_or_contract_phase(self):   # M6
        # scoped to the phase guides + SKILL.md (book narrative stays T4). Catch a phase table
        # row or a flow arrow that still names ground/contract as a PHASE.
        bad = []
        for t in SKILL_TREES:
            for f in [t / "SKILL.md"] + sorted((t / "phases").glob("*.md")):
                txt = f.read_text(encoding="utf-8")
                # a flow arrow naming ground/contract as a step
                if re.search(r"ground\s*(?:->|→)\s*specify", txt) or \
                   re.search(r"contract\s*(?:->|→)\s*tests", txt):
                    bad.append(f"{f.relative_to(REPO)}: stale flow arrow")
                # a phase-table row — the phase name is the FIRST cell (line-start `|`), NOT the
                # inline `[spec|scenario|contract|test]` freeze-flag vocabulary mid-sentence.
                if re.search(r"^\s*\|\s*ground\s*\|", txt, re.M) or \
                   re.search(r"^\s*\|\s*contract\s*\|", txt, re.M):
                    bad.append(f"{f.relative_to(REPO)}: stale phase-table row")
                # a dangling link to a DELETED guide file (e.g. a `Next` pointer)
                for gone in ("phases/0-ground.md", "phases/3-contract.md"):
                    if gone in txt:
                        bad.append(f"{f.relative_to(REPO)}: dangling ref to deleted {gone}")
        self.assertEqual(bad, [], f"stale ground-first/contract-phase reference: {bad}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
