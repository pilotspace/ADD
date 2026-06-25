#!/usr/bin/env python3
"""Doc-consistency guard (audit F9) — the scope-level enumeration is ONE canonical
ordered list across the book.

The five scope levels, in canonical order, are:
    1. setup / foundation   2. intake   3. milestone loop (task = inner unit)
    4. stage graduation     5. release

ch10 (the anchor) and two appendix-c entries already use this base; ch16 and the
appendix-c "Scope level" entry used to enumerate a conflicting base (task · milestone
· setup … , no intake). This guard pins all three to the canonical order so the
enumeration cannot silently re-drift -> scope_level_enum_drift.

Reads the CANONICAL tree (add-method/docs/); 3-tree parity is guarded elsewhere.
Run: python3 -m unittest test_scope_level_enum -v
"""
import re
import unittest
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def _entry(text: str, term: str) -> str:
    """The glossary paragraph beginning '**<term>**' up to the next blank line."""
    m = re.search(rf"\*\*{re.escape(term)}\*\*.*?(?:\n\s*\n|\Z)", text, re.S)
    return m.group(0) if m else ""


class ScopeLevelEnumTest(unittest.TestCase):
    def test_ch16_canonical_order(self):
        t = (DOCS / "16-releasing.md").read_text(encoding="utf-8")
        self.assertIn(
            "after setup, intake, the milestone loop, and stage graduation", t,
            "scope_level_enum_drift: ch16 must enumerate the canonical base "
            "(setup · intake · milestone loop · stage graduation), release fifth",
        )
        self.assertNotIn(
            "after the task, the milestone", t,
            "scope_level_enum_drift: ch16 still uses the old conflicting base",
        )

    def test_appendix_c_scope_level_ordered(self):
        entry = _entry((DOCS / "appendix-c-glossary.md").read_text(encoding="utf-8"),
                       "Scope level")
        self.assertTrue(entry, "could not find the 'Scope level' glossary entry")
        order = ["setup", "intake", "milestone", "stage", "release"]
        idx = [entry.find(tok) for tok in order]
        self.assertTrue(all(i >= 0 for i in idx),
                        f"scope_level_enum_drift: 'Scope level' entry misses a level: "
                        f"{dict(zip(order, idx))}")
        self.assertEqual(idx, sorted(idx),
                         "scope_level_enum_drift: 'Scope level' entry lists the levels "
                         f"out of canonical order: {dict(zip(order, idx))}")
        self.assertNotIn("· task level", entry,
                         "scope_level_enum_drift: 'task' must be the milestone loop's "
                         "inner unit, not a separately-counted scope level")

    def test_ch10_anchor_intact(self):
        t = (DOCS / "10-setup-and-stages.md").read_text(encoding="utf-8")
        self.assertIn(
            "the fourth after setup, intake, and the milestone loop", t,
            "the canonical anchor in ch10 must stay intact",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
