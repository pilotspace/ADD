#!/usr/bin/env python3
"""Regression: declaration-token readers must anchor to a DECLARATION position.

Defect (found at the init-auto-default freeze): `_AUTONOMY_LINE_RE` and
`_RISK_HIGH_RE` used `\\b<token>:` and matched the FIRST occurrence anywhere in
the scanned header — including the freeform H1 title and quoted prose. A task
literally titled "Project seeds autonomy: auto …" therefore read as `auto` even
though its declaration line said `autonomy: conservative`; symmetrically a title
containing "autonomy: conservative" could make a real `auto` task read as
*lowered*, fooling the high-risk guard.

Fix: a declared token is only one written at a declaration position — line-start
(optionally indented) OR after the `·` slug-line separator — never a title/prose
substring. The FROZEN grammar (`manual|conservative|auto`, line + inline forms)
is UNCHANGED; the reader is made to honor it.

    cd add-method/tooling && python3 -m unittest test_autonomy_reader_anchor -v
"""
import unittest

import add


class AutonomyReaderAnchorTest(unittest.TestCase):

    def test_line_form_reads(self):
        hdr = "# PLAN: x\n\nslug: x · stage: mvp\nautonomy: conservative\nphase: specify\n"
        self.assertEqual(add._autonomy_level(hdr), "conservative")

    def test_inline_form_reads(self):
        # the `·`-separated inline form on the slug line is the deliberately-supported shape
        hdr = "# PLAN: x\n\nslug: x · stage: mvp · autonomy: manual\nphase: specify\n"
        self.assertEqual(add._autonomy_level(hdr), "manual")

    def test_title_substring_is_not_a_declaration(self):
        # the H1 title legitimately contains "autonomy: auto"; the real decl is conservative
        hdr = ("# PLAN: Project seeds autonomy: auto by default at init\n\n"
               "slug: x · stage: mvp\nautonomy: conservative\nphase: specify\n")
        self.assertEqual(add._autonomy_level(hdr), "conservative",
                         "a title substring must NOT be read as the declaration")

    def test_prose_substring_before_decl_is_not_a_declaration(self):
        # quoted prose mentioning the ladder precedes the real decl; the decl must win
        hdr = ("# PLAN: x\n\n> note: prefer autonomy: manual for risky work\n"
               "slug: x · stage: mvp\nautonomy: auto\nphase: specify\n")
        self.assertEqual(add._autonomy_level(hdr), "auto",
                         "prose mentioning a rung must NOT be read as the declaration")

    def test_guard_reliability_title_cannot_fake_lowered(self):
        # a real `auto` decl + a title containing "autonomy: conservative":
        # the reader must return auto and the guard must NOT see it as lowered.
        hdr = ("# PLAN: about autonomy: conservative tradeoffs\n\n"
               "slug: x · stage: mvp\nautonomy: auto\nphase: verify\n")
        self.assertEqual(add._autonomy_level(hdr), "auto")
        self.assertFalse(add._autonomy_lowered(hdr),
                         "a title string must not make an auto task read as lowered")

    def test_unset_when_no_declaration_line(self):
        # a title-only mention with no decl line reads UNSET (None), not the title value
        hdr = "# PLAN: notes on autonomy: manual\n\nslug: x · stage: mvp\nphase: specify\n"
        self.assertIsNone(add._autonomy_level(hdr))


class RiskReaderAnchorTest(unittest.TestCase):

    def test_line_form_reads(self):
        self.assertTrue(bool(add._RISK_HIGH_RE.search("slug: x\nrisk: high\nautonomy: manual\n")))

    def test_inline_form_reads(self):
        self.assertTrue(bool(add._RISK_HIGH_RE.search("slug: x · risk: high · autonomy: manual\n")))

    def test_title_substring_is_not_a_declaration(self):
        hdr = "# PLAN: how to handle risk: high tasks\n\nslug: x\nautonomy: auto\nphase: specify\n"
        self.assertFalse(bool(add._RISK_HIGH_RE.search(hdr)),
                         "a title about risk must NOT flip the risk guard on")


if __name__ == "__main__":
    unittest.main()
