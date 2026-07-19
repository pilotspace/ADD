#!/usr/bin/env python3
"""fence-aware-section — one fence-aware section slicer, its importer suites.

Four guard files sliced markdown sections by splitting at the next H2 line,
fence-blind: a ``` fence containing an H2-looking line silently truncated the
scan while the guard claimed the whole section (the wave-ledger hazard; its
template was forced to ### headings as a workaround). This suite drives
md_section.section(): the terminator scan skips fenced lines, the four guard
files route through it, and a sweep proves the fence-blind idiom is gone.

Run: python3 -m unittest test_md_section -v
"""
import io
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent

# kernel-trim (ADD 2.0 M5): test_audit_ci + test_wave_ledger died with their pillars
IMPORTERS = (
    # atomic-node: test_ground_wiring retired with the §3 Grounding block
    "test_intake_interview.py",
    "test_review_checklist.py",
)
# the fence-blind idiom: slicing at the next-H2 escape sequence
_IDIOM = '\\n## '

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

    def test_importers_no_leftover_idiom(self):
        for name in IMPORTERS:
            src = (TOOLING / name).read_text(encoding="utf-8")
            self.assertIn("md_section", src,
                          f"{name} must route slicing through md_section")
            self.assertNotIn(_IDIOM, src,
                             f"slicer_not_single_source: {name} still carries "
                             f"the fence-blind slice idiom")

    def test_importer_guards_still_green(self):
        loader = unittest.defaultTestLoader
        suite = unittest.TestSuite(
            loader.loadTestsFromName(name[:-3]) for name in IMPORTERS)
        result = unittest.TextTestRunner(
            stream=io.StringIO(), verbosity=0).run(suite)
        self.assertTrue(result.wasSuccessful(),
                        "regression: the slicing suites must stay green — "
                        f"{result.failures} {result.errors}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
