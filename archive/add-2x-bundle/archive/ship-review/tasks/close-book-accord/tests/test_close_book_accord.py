"""Red→green guard for close-book-accord §3 (FROZEN @ v1).

The book (ch09) + GLOSSARY DESCRIBE the ship review + release steps and POINT at the
`add` skill's loop.md (the authoritative ritual) — describe, don't re-specify. Terms land
in all 3 glossary TYPES, each in its native format.

RED drivers (fail until the book + glossary are edited across their trees):
  test_B1_ch9_ship_review_passage · test_B2_glossary_all_three_types ·
  test_B4_book_glossary_parity
DISCLOSED green-at-red guard (green now, MUST stay green):
  test_B3_points_not_forks (ch09 copies none of release.md's reject codes).

unittest (repo convention). Run: python3 -m unittest discover -s tests
"""
import hashlib
import os
import re
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

_CH9 = [
    os.path.join(_ROOT, "add-method/docs/09-the-loop.md"),
    os.path.join(_ROOT, "09-the-loop.md"),
    os.path.join(_ROOT, ".add/docs/09-the-loop.md"),
    os.path.join(_ROOT, "add-method/src/add_method/_bundled/docs/09-the-loop.md"),
]
_APPENDIX = [
    os.path.join(_ROOT, "add-method/docs/appendix-c-glossary.md"),
    os.path.join(_ROOT, "appendix-c-glossary.md"),
    os.path.join(_ROOT, ".add/docs/appendix-c-glossary.md"),
    os.path.join(_ROOT, "add-method/src/add_method/_bundled/docs/appendix-c-glossary.md"),
]
_TEMPLATE_GLOSSARY = [
    os.path.join(_ROOT, "add-method/tooling/templates/GLOSSARY.md.tmpl"),
    os.path.join(_ROOT, ".add/tooling/templates/GLOSSARY.md.tmpl"),
    os.path.join(_ROOT, "add-method/src/add_method/_bundled/tooling/templates/GLOSSARY.md.tmpl"),
]
_DOGFOOD_GLOSSARY = os.path.join(_ROOT, ".add/GLOSSARY.md")

_CANON_CH9 = _CH9[0]
_CANON_APPENDIX = _APPENDIX[0]
_CANON_TEMPLATE = _TEMPLATE_GLOSSARY[0]

_RELEASE_REJECT_CODES = [
    "release_security_open", "release_tests_red",
    "release_no_closed_milestone", "release_undisclosed_waiver",
]


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _md5(path):
    return hashlib.md5(_read(path).encode("utf-8")).hexdigest()


class CloseBookAccord(unittest.TestCase):

    # B1: ch09 gains the ship-review passage pointing at loop.md ----------
    def test_B1_ch9_ship_review_passage(self):
        low = _read(_CANON_CH9).lower()
        self.assertIn("ship review", low, "ch09 must describe the ship review")
        self.assertIn("domain", low, "ch09 must name the ship-by-domain breakdown")
        self.assertIn("cross-task", low, "ch09 must name cross-task evidence")
        self.assertIn("goal", low, "ch09 must name the goal-met map")
        self.assertIn("release steps", low, "ch09 must name the release steps")
        self.assertIn("merge", low, "ch09 must name merge as one step")
        self.assertIn("loop.md", low, "ch09 must POINT at the add skill's loop.md")

    # B2: both terms in all 3 glossary types, native format --------------
    def test_B2_glossary_all_three_types(self):
        appendix = _read(_CANON_APPENDIX)
        self.assertRegex(appendix, r"\*\*Ship review\*\*", "appendix-c missing **Ship review**")
        self.assertRegex(appendix, r"\*\*Release steps\*\*", "appendix-c missing **Release steps**")
        for path, kind in ((_CANON_TEMPLATE, "template"), (_DOGFOOD_GLOSSARY, "dogfood")):
            txt = _read(path)
            self.assertRegex(txt, r"(?im)^ship review:", f"{kind} glossary missing 'ship review:'")
            self.assertRegex(txt, r"(?im)^release steps:", f"{kind} glossary missing 'release steps:'")

    # B3 (disclosed green-at-red guard): points, does not fork -----------
    def test_B3_points_not_forks(self):
        text = _read(_CANON_CH9)
        for code in _RELEASE_REJECT_CODES:
            self.assertNotIn(code, text,
                             f"ch09 copied release.md's reject code {code!r} (duplicates_guide)")

    # B4: byte parity across each artifact's trees -----------------------
    def test_B4_book_glossary_parity(self):
        for group, label in ((_CH9, "ch09"), (_APPENDIX, "appendix-c"),
                             (_TEMPLATE_GLOSSARY, "template glossary")):
            for p in group:
                self.assertTrue(os.path.exists(p), f"missing {label} copy: {p}")
                self.assertIn("ship review", _read(p).lower(), f"{p} missing the ship-review content")
            self.assertEqual(len({_md5(p) for p in group}), 1, f"{label} copies diverged (tree_drift)")


if __name__ == "__main__":
    unittest.main()
