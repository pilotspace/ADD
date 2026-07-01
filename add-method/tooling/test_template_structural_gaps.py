#!/usr/bin/env python3
"""Red/green tests for template-structural-gaps (milestone traceability-ids) — 3 additive
TASK.md.tmpl gaps surfaced by a cross-project TASK.md quality review: a `Glossary deltas:` line
in §3 CONTRACT, a scenario-ID back-reference slot in §2 SCENARIOS, and a `### Live-verify
evidence` block in §6 VERIFY. Frozen shape (§3 @ v1) — see
.add/tasks/template-structural-gaps/TASK.md.

Run: cd add-method/tooling && python3 -m unittest test_template_structural_gaps -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

TASK_TMPL_COPIES = [
    HERE / "templates" / "TASK.md.tmpl",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
]

FORM_TAGS = {"must", "reject", "after", "assumptions", "scenarios", "test_plan"}


def _sections(p: Path) -> dict[int, str]:
    return add._phase_spans(p.read_text(encoding="utf-8"))


class GlossaryDeltaLineTest(unittest.TestCase):
    def test_present_between_fence_and_status_all_trees(self):
        for p in TASK_TMPL_COPIES:
            sec3 = _sections(p)[3]
            self.assertIn("Glossary deltas:", sec3, f"missing in {p}")
            i_glossary = sec3.index("Glossary deltas:")
            i_status = sec3.index("Status: DRAFT")
            self.assertLess(i_glossary, i_status,
                             f"Glossary deltas: must precede Status: DRAFT in {p}")

    def test_section3_has_exactly_one_html_comment(self):
        for p in TASK_TMPL_COPIES:
            sec3 = _sections(p)[3]
            self.assertEqual(sec3.count("<!--"), 1, f"§3 comment count drifted in {p}")


class ScenarioIdSlotTest(unittest.TestCase):
    def test_scenario_line_carries_a_back_reference_slot(self):
        for p in TASK_TMPL_COPIES:
            sec2 = _sections(p)[2]
            m = re.search(r"^Scenario: <short name>(.*)$", sec2, re.M)
            self.assertIsNotNone(m, f"scenario placeholder line missing in {p}")
            self.assertIn("#", m.group(1), f"no back-reference slot in {p}")

    def test_given_when_then_and_lines_unchanged(self):
        for p in TASK_TMPL_COPIES:
            sec2 = _sections(p)[2]
            self.assertIn("Given <starting situation>", sec2)
            self.assertIn("When <action>", sec2)
            self.assertIn("Then <expected result>", sec2)
            self.assertIn("And <what must remain unchanged>", sec2)


class LiveVerifyEvidenceBlockTest(unittest.TestCase):
    def test_present_and_correctly_positioned(self):
        for p in TASK_TMPL_COPIES:
            sec6 = _sections(p)[6]
            self.assertIn("### Live-verify evidence", sec6, f"missing in {p}")
            i_deep = sec6.index("### Deep checks")
            i_live = sec6.index("### Live-verify evidence")
            i_refute = sec6.index("### Refute-read verdict")
            self.assertLess(i_deep, i_live, f"must come after Deep checks in {p}")
            self.assertLess(i_live, i_refute, f"must come before Refute-read verdict in {p}")

    def test_uses_blockquote_not_html_comment(self):
        for p in TASK_TMPL_COPIES:
            sec6 = _sections(p)[6]
            i_live = sec6.index("### Live-verify evidence")
            i_refute = sec6.index("### Refute-read verdict")
            block = sec6[i_live:i_refute]
            self.assertNotIn("<!--", block,
                              f"Live-verify evidence must not use an HTML comment in {p}")
            self.assertIn(">", block,
                           f"Live-verify evidence should use the blockquote cue style in {p}")


class CommentCeilingTest(unittest.TestCase):
    def test_total_comment_count_below_twelve(self):
        for p in TASK_TMPL_COPIES:
            text = p.read_text(encoding="utf-8")
            self.assertLess(text.count("<!--"), 12, f"comment ceiling breached in {p}")


_OPEN = re.compile(r"<([a-z][a-z0-9_-]*)>")
_CLOSE = re.compile(r"</([a-z][a-z0-9_-]*)>")


def _paired_tags(text: str) -> set[str]:
    """Paired <x>...</x> names only — an unpaired <x> is a prose placeholder
    (e.g. <name>, <path>) and never counts, matching test_template_form_tags.py's
    own v16 disambiguation rule."""
    return set(_OPEN.findall(text)) & set(_CLOSE.findall(text))


class TagClassUnchangedTest(unittest.TestCase):
    def test_no_new_bracketed_tag_introduced(self):
        for p in TASK_TMPL_COPIES:
            text = p.read_text(encoding="utf-8")
            self.assertEqual(_paired_tags(text), FORM_TAGS, f"tag set drifted in {p}")


class ThreeTreeParityTest(unittest.TestCase):
    def test_byte_identical_across_three_trees(self):
        texts = {p.read_text(encoding="utf-8") for p in TASK_TMPL_COPIES}
        self.assertEqual(len(texts), 1, "TASK.md.tmpl diverges across the 3 parity trees")


if __name__ == "__main__":
    unittest.main()
