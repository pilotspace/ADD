"""Red→green guard for suggest-book-align §3 (FROZEN @ v1).

The book + glossary catch up to the shipped guided-decision convention (report-template.md):
`02-the-flow.md` gains one guided-choice sentence beside the decision-arc paragraph, and the
GLOSSARY gains two own-entry headwords — **Guided decision** + **Recommended pick** — that
POINT at report-template.md (describe, never re-specify). Byte-identical across the parity
trees (canonical · root · _bundled) + the dogfood `.add/docs/` synced.

RED drivers (fail until the book is edited): test_flow_describes_guided_choice ·
  test_glossary_headwords (headword_absent) · test_book_points_at_report_template.
DISCLOSED green-at-red regression guards: test_book_trees_parity (book_drift — green once the
  edits mirror) · test_convention_untouched (report-template.md already carries the tokens).

unittest (repo convention). Run: python3 -m unittest discover -s tests
"""
import hashlib
import os
import re
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

# each changed file is synced ×4 (root · canonical · bundle · dogfood); the dogfood is NOT parity-guarded
_FLOW = ["02-the-flow.md",
         "add-method/docs/02-the-flow.md",
         "add-method/src/add_method/_bundled/docs/02-the-flow.md",
         ".add/docs/02-the-flow.md"]
_GLOSSARY = ["appendix-c-glossary.md",
             "add-method/docs/appendix-c-glossary.md",
             "add-method/src/add_method/_bundled/docs/appendix-c-glossary.md",
             ".add/docs/appendix-c-glossary.md"]
_REPORT_TEMPLATE = "add-method/skill/add/report-template.md"
_HEADWORDS = ["Guided decision", "Recommended pick"]


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _entry(text, headword):
    """The single-line glossary paragraph for a bold headword (this glossary's native shape)."""
    for line in text.splitlines():
        if re.match(r"\s*\*\*" + re.escape(headword) + r"\*\*\s*[—-]", line):
            return line
    return ""


class SuggestBookAlignTest(unittest.TestCase):
    # ---- RED drivers --------------------------------------------------------
    def test_flow_describes_guided_choice(self):
        """B1: 02-the-flow names the guided choice beside the decision-arc paragraph."""
        text = _read(_FLOW[1])  # canonical
        self.assertIn("guided choice", text, "02-the-flow.md does not describe the guided choice")
        arc = re.search(r"the decision arc\.\*\*(.*?)\n\n", text, re.S)
        self.assertTrue(arc and "guided choice" in arc.group(1),
                        "the guided-choice sentence is not beside the decision-arc paragraph")

    def test_glossary_headwords(self):
        """B2+B3 / headword_absent: both own-entry bold headwords are defined."""
        text = _read(_GLOSSARY[1])  # canonical
        for hw in _HEADWORDS:
            self.assertTrue(_entry(text, hw), f"glossary missing own-entry headword '{hw}'")

    def test_book_points_at_report_template(self):
        """B4 / book_respecifies guard: the Guided decision entry POINTS at report-template.md."""
        gd = _entry(_read(_GLOSSARY[1]), "Guided decision")
        self.assertIn("report-template", gd,
                      "Guided decision entry must point at report-template.md (describe, not re-specify)")

    # ---- DISCLOSED green-at-red regression guards ---------------------------
    def test_book_trees_parity(self):
        """book_drift / I2: canonical == root == _bundled for both changed files; dogfood synced."""
        for group in (_FLOW, _GLOSSARY):
            d = {h: hashlib.md5(_read(h).encode("utf-8")).hexdigest() for h in group[:3]}
            self.assertEqual(len(set(d.values())), 1, f"parity drift across {group[1]} trees: {d}")
            self.assertEqual(_read(group[3]), _read(group[1]),
                             f"dogfood {group[3]} out of sync with canonical")

    def test_convention_untouched(self):
        """I1: report-template.md (the frozen convention) still carries its tokens — unchanged here."""
        rt = _read(_REPORT_TEMPLATE)
        self.assertIn("guided choice", rt)
        self.assertIn("▶", rt)  # ▶ recommended-pick marker


if __name__ == "__main__":
    unittest.main()
