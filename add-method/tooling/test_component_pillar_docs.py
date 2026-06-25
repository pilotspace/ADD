#!/usr/bin/env python3
"""Content driver for the component-pillar teaching surface (component-aware-add, task 6).

The byte-identity of mirrors is guarded by test_book_parity / test_bundle_parity / test_tree_parity;
the untouched engine by the engine-pin guards. THIS test asserts the CONTENT exists and teaches the
five shipped capabilities (tasks 1–5): declared components, per-component verify, cross-component
contract, the intra-milestone hold, and multi-repo federation.

Run: cd add-method/tooling && python3 -m unittest test_component_pillar_docs -v
"""
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CHAPTER = _ADD_METHOD / "docs" / "17-components.md"
GLOSSARY = _ADD_METHOD / "docs" / "appendix-c-glossary.md"
SKILL_GUIDE = _ADD_METHOD / "skill" / "add" / "components.md"
SKILL_MD = _ADD_METHOD / "skill" / "add" / "SKILL.md"
MKDOCS = _REPO / "mkdocs.yml"
README = _REPO / "README.md"


class ChapterTest(unittest.TestCase):
    def test_chapter_exists_and_teaches_the_five_capabilities(self):
        self.assertTrue(CHAPTER.is_file(), "chapter 17-components.md must exist in the canonical docs")
        body = CHAPTER.read_text(encoding="utf-8")
        for needle in ("components.toml", "green-bar", "produces:", "consumes:",
                       "federate pull", "[contract.", "[federation."):
            self.assertIn(needle, body, f"chapter must teach '{needle}'")
        # the intra-milestone BE->FE ordering is the headline of task 4
        self.assertRegex(body.lower(), r"(hold|held|ordered|downstream)")

    def test_chapter_registered_in_nav_and_toc(self):
        self.assertIn("17-components.md", MKDOCS.read_text(encoding="utf-8"),
                      "mkdocs.yml nav must list the new chapter")
        self.assertIn("17-components.md", README.read_text(encoding="utf-8"),
                      "README ToC must link the new chapter")


class GlossaryTest(unittest.TestCase):
    def test_pillar_terms_defined(self):
        body = GLOSSARY.read_text(encoding="utf-8")
        for term in ("**Component**", "**Cross-component contract**", "**Federation"):
            self.assertIn(term, body, f"glossary must define {term}")


class SkillGuideTest(unittest.TestCase):
    def test_skill_guide_exists_and_is_pointed_to(self):
        self.assertTrue(SKILL_GUIDE.is_file(), "skill guide components.md must exist")
        guide = SKILL_GUIDE.read_text(encoding="utf-8")
        for needle in ("components.toml", "federate pull"):
            self.assertIn(needle, guide, f"skill guide must cover '{needle}'")
        self.assertIn("components.md", SKILL_MD.read_text(encoding="utf-8"),
                      "SKILL.md must point to components.md")


if __name__ == "__main__":
    unittest.main()
