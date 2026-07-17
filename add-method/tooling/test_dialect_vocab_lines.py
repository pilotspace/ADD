#!/usr/bin/env python3
"""Red/green tests for quality-floors levers 3+4 (task dialect-check-and-data-vocab,
frozen contract v1): the §6 input-dialect check line in both task templates, and the
datetime/money/timezone ⇒ `data` sensitivity guidance in the glossary + skill guide.

The dialect line rides INSIDE the full template's `### Deep checks` block, so the
existing `shallow` audit counts its unfilled state with zero new engine code. The
guidance is PROSE, never a `- token:` bullet — it routes to the BASE `data` class
and must not mint a new sensitivity token (R1 vocab_leak).

Run: python3 -m unittest test_dialect_vocab_lines -v
"""
import re
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"
REPO = HERE.parents[1]
SKILL_GUIDE = HERE.parent / "skill" / "add" / "phases" / "verify.md"  # skill-fold-8: sensitivity.md folded here


class TemplateDialectLineTest(unittest.TestCase):
    def test_full_template_deep_checks_carries_dialect_line(self):
        body = (TEMPLATES / "TASK.md.tmpl").read_text(encoding="utf-8")
        idx = body.find("### Deep checks")
        self.assertNotEqual(idx, -1)
        nxt = body.find("###", idx + 3)
        block = body[idx:nxt]
        self.assertIn("DIALECT", block,
                      "the dialect check must live INSIDE Deep checks (shallow-audit-counted)")
        self.assertIn("spec-dialect floor", block)
        self.assertIn("same value formats", block)

    # template-unify: the fast lane derives from the one template and drops the §6
    # Deep-checks block; the input-dialect floor is held by the freeze-checked §1
    # Boundary line on BOTH lanes (test_fast_boundary_line, test_template_unify).


class GlossaryGuidanceTest(unittest.TestCase):
    def _sens_section(self, text: str) -> str:
        m = re.search(r"(?m)^##[ \t]+Sensitivity classes[ \t]*$", text)
        self.assertIsNotNone(m, "Sensitivity classes section missing")
        body = text[m.end():]
        nxt = re.search(r"(?m)^##[ \t]", body)
        return body[:nxt.start()] if nxt else body

    def test_glossary_template_carries_data_guidance_as_prose(self):
        section = self._sens_section(
            (TEMPLATES / "GLOSSARY.md.tmpl").read_text(encoding="utf-8"))
        self.assertIn("Datetime, money, or timezone arithmetic", section)
        self.assertIn("`data`", section)
        for line in section.splitlines():
            if "Datetime, money, or timezone arithmetic" in line:
                self.assertIsNone(
                    re.match(r"^[ \t]*-[ \t]", line),
                    "R1 vocab_leak: guidance must be prose, never a `- token:` bullet")

    def test_project_glossary_carries_the_rule(self):
        section = self._sens_section(
            (REPO / ".add" / "GLOSSARY.md").read_text(encoding="utf-8"))
        self.assertIn("Datetime, money, or timezone arithmetic", section)

    def test_no_new_sensitivity_token_from_guidance(self):
        text = (TEMPLATES / "GLOSSARY.md.tmpl").read_text(encoding="utf-8")
        section = self._sens_section(re.sub(r"<!--.*?-->", "", text, flags=re.S))
        tokens = re.findall(r"(?m)^[ \t]*-[ \t]+([A-Za-z][\w-]*)[ \t]*(?::|—)", section)
        self.assertEqual(tokens, [],
                         "the template section must declare no live domain token")


class SensitivityGuideTest(unittest.TestCase):
    def test_sensitivity_guide_names_wm2_evidence(self):
        body = SKILL_GUIDE.read_text(encoding="utf-8")
        self.assertIn("Datetime, money, or timezone arithmetic", body)
        self.assertIn("`data`", body)
        self.assertIn("wm2", body, "the guide must cite the benchmark evidence")


if __name__ == "__main__":
    unittest.main()
