#!/usr/bin/env python3
"""Content test for flow-jit-tasks-doc (todo #17): book ch.02-the-flow must EXPLAIN the
milestone-scale composition rule — tasks are listed breadth-first up front (the DAG), each
specified + built just-in-time. Asserts the new subsection exists in the canonical chapter and
is byte-identical across all 4 book copies. Run:
  python3 -m unittest test_flow_jit_doc -v
"""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
COPIES = (
    REPO / "add-method" / "docs" / "02-the-flow.md",                       # canonical
    REPO / "02-the-flow.md",                                               # repo-root mirror
    REPO / ".add" / "docs" / "02-the-flow.md",                            # dogfood
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "docs" / "02-the-flow.md",  # bundled
)
HEADING = "Many features, one at a time"


class FlowJitDocTest(unittest.TestCase):
    def test_canonical_explains_breadth_first_just_in_time(self):
        text = COPIES[0].read_text(encoding="utf-8")
        self.assertIn(HEADING, text, "ch.02 missing the milestone-composition subsection")
        # the section must carry BOTH anchor phrases (lower-cased compare)
        low = text.lower()
        self.assertIn("breadth-first", low)
        self.assertIn("just-in-time", low)

    def test_subsection_sits_in_the_flow_chapter_between_sections(self):
        text = COPIES[0].read_text(encoding="utf-8")
        # placed after "## The flow", before "## Why the order is the order"
        i_flow = text.find("## The flow")
        i_new = text.find(HEADING)
        i_why = text.find("## Why the order is the order")
        self.assertTrue(0 <= i_flow < i_new < i_why,
                        "subsection not positioned between The flow and Why the order is the order")

    def test_all_four_copies_byte_identical(self):
        present = [p for p in COPIES if p.exists()]
        self.assertGreaterEqual(len(present), 1)
        blobs = {p.read_bytes() for p in present}
        self.assertEqual(len(blobs), 1, "02-the-flow.md diverged across the 4 book copies")


if __name__ == "__main__":
    unittest.main(verbosity=2)
