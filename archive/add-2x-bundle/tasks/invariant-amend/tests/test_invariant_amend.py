"""Red→green guard for the invariant amendment (invariant-amend §3, FROZEN @ v1).

Realizes compaction-contract.md: append-only -> newest-first prepend + the recorded compaction
door, applied BYTE-IDENTICALLY across the 3 canonical fold.md homes, echoed in the dogfood
foundation, with the engine left untouched (convention-guided seam).

unittest (repo convention). Run: python3 -m unittest discover -s tests
RED before build: the clause/door/reject-codes/echo are absent until the amendment lands.
"""
import hashlib
import os
import re
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

_FOLD_HOMES = [
    "add-method/skill/add/fold.md",
    "add-method/src/add_method/_bundled/skill/add/fold.md",
    ".claude/skills/add/fold.md",
]
_PROJECT = ".add/PROJECT.md"
_CONVENTIONS = ".add/CONVENTIONS.md"
_ENGINES = ["add-method/tooling/add.py", ".add/tooling/add.py"]
_REJECTS = ["open-residue-version", "trail-loss", "wrong-order"]
# a known-old §Key-Decisions row that must survive (proves the trail was not wiped)
_ANCHOR_ROW = "fold v6 learnings"


def _read(rel):
    p = os.path.join(_ROOT, rel)
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


class InvariantAmendTest(unittest.TestCase):
    def test_append_only_newest_first(self):
        """Each fold.md home's clause says append-only (newest-first)/prepend AND keeps 'never silently rewrites'."""
        for home in _FOLD_HOMES:
            t = _norm(_read(home))
            self.assertIn("append-only (newest-first)", t, f"{home}: clause not re-frozen to newest-first")
            self.assertIn("prepend", t, f"{home}: clause must direct prepend-at-top")
            self.assertIn("never silently rewrites", t, f"{home}: lost the no-silent-rewrite guarantee")

    def test_compaction_door_named_and_gated(self):
        """The clause names the recorded compaction door, cites compact-foundation.md, and is gated by eligibility."""
        t = _norm(_read(_FOLD_HOMES[0]))
        self.assertIn("compaction door", t, "the recorded compaction door must be named")
        self.assertIn("compact-foundation.md", t, "the door must cite compact-foundation.md")
        self.assertIn("shipped", t, "the door must carry the shipped precondition")
        self.assertIn("zero open residues", t, "the door must carry the zero-open-residues precondition")

    def test_three_reject_codes_at_invariant(self):
        """All 3 contract reject codes are named at the invariant."""
        t = _norm(_read(_FOLD_HOMES[0]))
        for code in _REJECTS:
            self.assertIn(code, t, f"reject code missing at the invariant: {code}")

    def test_step5_reconciled_to_prepend(self):
        """fold.md step 5 no longer says the contradictory 'append the accepted edits'."""
        t = _norm(_read(_FOLD_HOMES[0]))
        self.assertNotIn("append the accepted edits", t,
                         "step 5 still says 'append the accepted edits' — contradicts newest-first prepend")

    def test_no_contradictory_append_position(self):
        """No append-AT-POSITION sentence survives to contradict newest-first (coherence across the ritual)."""
        t = _norm(_read(_FOLD_HOMES[0]))
        for phrase in ("append the accepted edits", "appends one row to", "is appended to the routed target"):
            self.assertNotIn(phrase, t, f"contradicts newest-first prepend: '{phrase}' still present")

    def test_fold_mirror_parity(self):
        """The 3 canonical fold.md homes are byte-identical (md5)."""
        digests = {home: hashlib.md5(_read(home).encode("utf-8")).hexdigest() for home in _FOLD_HOMES}
        self.assertEqual(len(set(digests.values())), 1, f"fold.md homes diverged (mirror-drift): {digests}")

    def test_foundation_echo_no_loss(self):
        """PROJECT.md + CONVENTIONS.md echo the amended invariant; the audit trail is not wiped."""
        proj = _norm(_read(_PROJECT))
        conv = _norm(_read(_CONVENTIONS))
        self.assertIn("newest-first", proj, "PROJECT.md must echo the newest-first invariant")
        self.assertIn("compaction door", proj, "PROJECT.md must name the compaction door")
        self.assertIn("newest-first", conv, "CONVENTIONS.md must echo the newest-first invariant")
        self.assertIn(_ANCHOR_ROW, proj, "an old §Key-Decisions row vanished — trail-loss")

    def test_engine_unchanged(self):
        """Convention-guided seam: no compaction reject-code is wired into the engine."""
        for eng in _ENGINES:
            src = _read(eng)
            for code in _REJECTS:
                self.assertNotIn(code, src, f"{eng}: engine enforces '{code}' — violates the convention-guided seam")


if __name__ == "__main__":
    unittest.main()
