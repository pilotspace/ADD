"""Red→green guard for the FROZEN foundation-compaction contract (compact-contract §3).

PROSE-CONTRACT tests: they parse `compaction-contract.md` (the build deliverable that realizes
the frozen §3) and assert its SHAPE and behavior — not bare token presence (CONVENTIONS:
"words-exist ≠ method-works"). The human SEMANTIC check at the verify gate carries aptness;
these carry structure. Red until `compaction-contract.md` exists.

unittest (repo convention — no pytest dependency). Run: python3 -m unittest discover -s tests
"""
import os
import re
import unittest

_DOC = os.path.join(os.path.dirname(__file__), "..", "compaction-contract.md")

# the 5 spec sections that each need a DISTINCT tailored rolled-line shape
_SPECS = [
    "project.md §spec",
    "project.md §key-decisions",
    "conventions.md",
    "glossary.md",
    "model_registry.md",
]
# the 3 frozen reject codes
_REJECTS = ["open-residue-version", "trail-loss", "wrong-order"]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


class CompactionContractTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(_DOC):
            self.fail(f"compaction-contract.md missing at {_DOC} — build has not run (expected RED pre-build)")
        with open(_DOC, encoding="utf-8") as fh:
            self.raw = fh.read()
        self.t = _norm(self.raw)

    def test_eligibility_rule(self):
        """Eligible IFF shipped AND zero open residues; the violation is open-residue-version."""
        self.assertIn("eligib", self.t, "no eligibility rule stated")
        self.assertIn("shipped", self.t, "eligibility must require the entry's milestone be SHIPPED")
        self.assertTrue(
            re.search(r"(open[_ ]residues?\s*==?\s*0|zero open|no open residue)", self.t),
            "eligibility must require ZERO open residues",
        )
        self.assertIn("open-residue-version", self.t, "violation must map to open-residue-version")

    def test_per_spec_shapes_named(self):
        """A DISTINCT rolled-line shape is named for each of the 5 spec sections."""
        for spec in _SPECS:
            self.assertIn(spec, self.t, f"no rolled-line shape named for {spec}")
        shapes = re.findall(r'->\s*"([^"]+)"', self.raw)
        self.assertGreaterEqual(len(shapes), 5, f"expected >=5 quoted rolled-line shapes, found {shapes}")
        self.assertEqual(len(set(shapes)), len(shapes), f"per-spec shapes must be DISTINCT, got dups: {shapes}")

    def test_newest_first_ordering(self):
        """Newest-first: prepend newest at top, settled line at bottom/tail; out-of-order → wrong-order."""
        self.assertIn("newest-first", self.t, "ordering rule must say newest-first")
        self.assertTrue(
            "prepend" in self.t or "at the top" in self.t or "at top" in self.t,
            "must prepend the newest record at the TOP",
        )
        self.assertTrue("tail" in self.t or "bottom" in self.t, "settled line must anchor at the BOTTOM/tail")
        self.assertIn("wrong-order", self.t, "out-of-order placement must map to wrong-order")

    def test_preservation_guarantees(self):
        """Never delete; a git/archive pointer survives; OPEN residues stay live; loss → trail-loss."""
        self.assertIn("never delete", self.t, "preservation must state NEVER delete")
        self.assertIn("git", self.t, "a surviving git/archive pointer is required")
        self.assertTrue(re.search(r"open residues? (stay|remain|live)", self.t), "OPEN residues must stay live")
        self.assertIn("trail-loss", self.t, "a collapse that loses the trail must map to trail-loss")

    def test_disambiguation_seam(self):
        """Convention-guided: distinct from engine `add.py compact`; no new engine command, no check enforcement."""
        self.assertIn("add.py compact", self.t, "must name the engine `add.py compact` it disambiguates from")
        self.assertIn("convention", self.t, "foundation compaction must be a convention-guided ritual")
        self.assertTrue(re.search(r"no (new )?engine command", self.t), "must disclaim a new engine command")
        self.assertTrue(re.search(r"no .*check.* enforcement", self.t), "must disclaim add.py check enforcement")

    def test_all_three_reject_codes_present(self):
        """All three frozen reject codes appear."""
        for code in _REJECTS:
            self.assertIn(code, self.t, f"frozen reject code missing: {code}")


if __name__ == "__main__":
    unittest.main()
