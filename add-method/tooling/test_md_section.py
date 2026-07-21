#!/usr/bin/env python3
"""fence-aware-section — one fence-aware markdown section slicer.

Guard files once sliced markdown sections by splitting at the next H2 line,
fence-blind: a ``` fence containing an H2-looking line silently truncated the
scan while the guard claimed the whole section (the wave-ledger hazard). This
suite drives md_section.section(): the terminator scan skips fenced lines.

Run: python3 -m unittest test_md_section -v
"""
import unittest

FENCE = "`" * 3


class SlicerBehaviorTest(unittest.TestCase):
    """section(text, heading): heading-inclusive, fence-aware terminator."""

    def test_basic_slice_heading_to_next_h2(self):
        from md_section import section
        text = "intro\n## A\nbody of a\n## B\nbody of b\n"
        got = section(text, "## A")
        self.assertTrue(got.startswith("## A"))
        self.assertIn("body of a", got)
        self.assertNotIn("## B", got)

    def test_fenced_h2_does_not_terminate(self):
        from md_section import section
        text = (
            "## A\nbefore fence\n"
            f"{FENCE}markdown\n## Fake heading inside fence\n{FENCE}\n"
            "after fence — the guard must still scan this\n"
            "## B\nbody of b\n"
        )
        got = section(text, "## A")
        self.assertIn("after fence", got,
                      "fenced_h2_truncates: a fenced H2 must not terminate")
        self.assertIn("## Fake heading inside fence", got)
        self.assertNotIn("body of b", got)

    def test_missing_heading_returns_empty(self):
        from md_section import section
        self.assertEqual(section("no such thing\n## Real\n", "## Nope"), "")

    def test_unclosed_fence_scans_to_end(self):
        from md_section import section
        text = f"## A\nbody\n{FENCE}\nnever closed\n## B\nswallowed\n"
        got = section(text, "## A")
        self.assertIn("swallowed", got,
                      "an unclosed fence runs to end-of-text, no raise")


if __name__ == "__main__":
    unittest.main(verbosity=2)
