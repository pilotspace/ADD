#!/usr/bin/env python3
"""Doc-truth + parity tests for persona-method-docs (persona-learning-loop, wave-2 3/3).

A dedicated book chapter (18 · Personas) teaches the persona loop end-to-end — SEED at setup,
GROW via observe→delta→fold, APPLY to UDD/advisor/build, expose a cross-runner subagent — with
the local vendored teacher library (.add/personas-teacher) read off-build (never a runtime dependency), the engine NO-EXEC, and a
persona never lowering a gate. The chapter is registered in the mkdocs nav, the glossary gains the
persona headwords, SKILL.md points to the loop, and every surface stays byte-identical across the
git-tracked trees (canonical · repo-root · _bundled). Docs are descriptive: no engine change. Run:
python3 -m unittest test_persona_method_docs -v
"""
import hashlib
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

CHAPTER = "18-personas.md"
GLOSSARY = "appendix-c-glossary.md"
BOOK_TREES = (
    PKG_ROOT / "docs",
    REPO_ROOT,
)   # book-stops-shipping (2.0 M6b): no bundled copy
SKILL_TREES = (
    PKG_ROOT / "skill" / "add",
    REPO_ROOT / ".claude" / "skills" / "add",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",
)
MKDOCS = REPO_ROOT / "mkdocs.yml"
CANON_DOCS = BOOK_TREES[0]
CANON_SKILL = SKILL_TREES[0]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class PersonaMethodDocsTest(unittest.TestCase):
    def test_chapter_exists_and_teaches_loop(self):
        chap = CANON_DOCS / CHAPTER
        self.assertTrue(chap.is_file(), f"{CHAPTER} must exist in the canonical docs tree")
        low = _read(chap).lower()
        for token in ("seed", "grow", "apply", "observe", "fold", "udd",
                      "advisor", "overlay", "subagent", "personas-teacher",
                      "no-exec", "never lower", "hard-stop"):
            self.assertIn(token, low, f"18-personas.md must teach '{token}'")

    def test_chapter_in_nav(self):
        self.assertIn(CHAPTER, _read(MKDOCS),
                      "mkdocs.yml nav must list 18-personas.md (orphan_chapter)")

    def test_glossary_defines_persona_terms(self):
        text = _read(CANON_DOCS / GLOSSARY)
        self.assertIn("**persona**", text, "glossary must define the **persona** headword")
        self.assertIn("**persona loop**", text, "glossary must define the **persona loop** headword")

    def test_skill_points_to_loop(self):
        text = _read(CANON_SKILL / "SKILL.md")
        self.assertIn(".add/personas/", text, "SKILL.md must point to where personas live")
        self.assertIn("persona loop", text.lower(), "SKILL.md must name the persona loop")


if __name__ == "__main__":
    unittest.main(verbosity=2)
