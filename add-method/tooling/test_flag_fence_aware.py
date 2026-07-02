#!/usr/bin/env python3
"""Red/green tests for `_flag_well_formed`'s fence-aware comment strip (task
fix-flag-fence-aware, milestone seams).

`_flag_well_formed` used a fence-unaware `re.sub(r"<!--.*?-->", "", raw3, flags=re.S)` to drop
HTML comments before searching for the `Least-sure flag surfaced at freeze:` label. A frozen §3
that legitimately quotes a bare backtick-quoted `` `<!--` `` inside its own fenced code block
(e.g. documenting an HTML-comment-count invariant, as seams-template-wiring's real contract
does) pairs with the NEXT unrelated `-->` found anywhere later in the raw §3 text — typically the
closing `-->` of the guide's own trailing instruction comment — silently swallowing everything in
between, including a correctly-placed flag line. The fix mirrors `_strip_live_scaffold`'s
already-correct fence-split-first pattern: split on ``` fences, strip comments only from the
non-fence (even-indexed) segments, rejoin.

    python3 -m unittest test_flag_fence_aware -v
"""
import unittest

import add


class FenceAwareFlagTest(unittest.TestCase):

    def test_bare_fenced_marker_no_longer_swallows_a_later_flag(self):
        # Reproduces seams-template-wiring's real §3 shape: a fenced block that quotes a bare
        # `<!--` (documenting a comment-count invariant), followed by a correctly-placed flag
        # line, followed by the guide's own trailing instruction comment.
        raw3 = (
            "```\n"
            "  - NoNewHtmlCommentTest — `<!--` count unchanged (11)\n"
            "```\n\n"
            "Status: FROZEN @ v1 — approved by Tin Dang\n"
            "Least-sure flag surfaced at freeze: [contract] some genuine risk here\n"
            "<!-- The freeze IS the one approval — trailing guide instruction. -->\n"
        )
        self.assertTrue(add._flag_well_formed(raw3))

    def test_fenced_marker_alone_with_no_flag_still_fails_closed(self):
        raw3 = (
            "```\n"
            "  - NoNewHtmlCommentTest — `<!--` count unchanged (11)\n"
            "```\n\n"
            "Status: FROZEN @ v1 — approved by Tin Dang\n"
            "<!-- The freeze IS the one approval — trailing guide instruction. -->\n"
        )
        self.assertFalse(add._flag_well_formed(raw3))

    def test_unfenced_instruction_comment_never_leaks_into_flag_content(self):
        # A flag-shaped label INSIDE the trailing unfenced guide comment must not count —
        # only real content outside any HTML comment satisfies the label search.
        raw3 = (
            "```\n"
            "some contract shape\n"
            "```\n\n"
            "Status: FROZEN @ v1 — approved by Tin Dang\n"
            "<!-- Least-sure flag surfaced at freeze: [spec] this is just template guidance -->\n"
        )
        self.assertFalse(add._flag_well_formed(raw3))

    def test_preexisting_well_formed_flag_without_fenced_marker_unaffected(self):
        raw3 = (
            "```\n"
            "plain contract, no HTML-comment mentions\n"
            "```\n\n"
            "Status: FROZEN @ v1 — approved by Tin Dang\n"
            "Least-sure flag surfaced at freeze: [spec] a real, ordinary flag\n"
        )
        self.assertTrue(add._flag_well_formed(raw3))

    def test_preexisting_none_material_escape_unaffected(self):
        raw3 = (
            "```\n"
            "plain contract\n"
            "```\n\n"
            "Status: FROZEN @ v1 — approved by Tin Dang\n"
            "Least-sure flag surfaced at freeze: none material — biggest risk: X\n"
        )
        self.assertTrue(add._flag_well_formed(raw3))

    def test_missing_label_entirely_still_fails_closed(self):
        raw3 = "```\nplain contract\n```\n\nStatus: FROZEN @ v1 — approved by Tin Dang\n"
        self.assertFalse(add._flag_well_formed(raw3))


if __name__ == "__main__":
    unittest.main()
