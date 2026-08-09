"""Red→green guard for close-guide §3 (FROZEN @ v1).

loop.md step 6 "Close" gains the cross-task ship-review ritual: FILL the milestone
`## Close — ship review` (ship-by-domain + cross-task evidence + goal-met map) as the
evidence read before checking the exit-criteria boxes (NOT a new gate), then DEFINE
`## Release steps` (merge = one step) that FEED `release.md` (a pointer, not a re-spec).

RED drivers (fail until loop.md is edited across the 3 skill trees):
  test_L1_loop_cues_ship_review_fill · test_L2_loop_feeds_release ·
  test_L4_loop_tree_parity_includes_ship_review
DISCLOSED green-at-red guard (green now, MUST stay green):
  test_L3_no_new_gate (no second 'approve merge/ship' approval introduced).

unittest (repo convention). Run: python3 -m unittest discover -s tests
"""
import hashlib
import os
import re
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

_LOOP_COPIES = [
    os.path.join(_ROOT, "add-method/skill/add/loop.md"),
    os.path.join(_ROOT, ".claude/skills/add/loop.md"),
    os.path.join(_ROOT, "add-method/src/add_method/_bundled/skill/add/loop.md"),
]
_CANON_LOOP = _LOOP_COPIES[0]

# release.md's distinctive reject codes — their presence in loop.md would mean a FORK, not a pointer
_RELEASE_REJECT_CODES = [
    "release_security_open", "release_tests_red",
    "release_no_closed_milestone", "release_undisclosed_waiver",
]
# a second human approval would read as one of these in the close ritual
_SECOND_GATE_PHRASES = ["approve merge", "approve the merge", "approve ship", "approve the ship"]


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class CloseGuide(unittest.TestCase):

    # L1: loop.md cues filling the ship-review ----------------------------
    def test_L1_loop_cues_ship_review_fill(self):
        t = _read(_CANON_LOOP)
        self.assertIn("Close — ship review", t, "loop.md must cue the Close — ship review fill")
        low = t.lower()
        self.assertIn("ship by domain", low, "loop.md must name the ship-by-domain block")
        self.assertIn("cross-task", low, "loop.md must name cross-task evidence")
        self.assertIn("goal", low, "loop.md must name the goal-met map")
        self.assertIn("exit criteria", low, "loop.md must frame it as evidence before the exit-criteria boxes")

    # L2: defines release steps that POINT at release.md (no fork) ---------
    def test_L2_loop_feeds_release(self):
        t = _read(_CANON_LOOP)
        self.assertIn("Release steps", t, "loop.md must instruct defining Release steps")
        self.assertIn("release.md", t, "loop.md must point at release.md as the feed")
        for code in _RELEASE_REJECT_CODES:
            self.assertNotIn(code, t,
                             f"loop.md copied release.md's reject code {code!r} (duplicates_release_scope)")

    # L3 (disclosed green-at-red guard): no second approval gate -----------
    def test_L3_no_new_gate(self):
        low = _read(_CANON_LOOP).lower()
        for phrase in _SECOND_GATE_PHRASES:
            self.assertNotIn(phrase, low,
                             f"loop.md introduces a second approval gate ({phrase!r}) — new_gate_introduced")

    # L4: byte parity across the 3 skill trees, including the new content --
    def test_L4_loop_tree_parity_includes_ship_review(self):
        digests = set()
        for p in _LOOP_COPIES:
            self.assertTrue(os.path.exists(p), f"missing loop.md copy: {p}")
            txt = _read(p)
            self.assertIn("Close — ship review", txt, f"{p} missing the ship-review ritual")
            digests.add(hashlib.md5(txt.encode("utf-8")).hexdigest())
        self.assertEqual(len(digests), 1, "the three loop.md copies diverged (tree_drift)")


if __name__ == "__main__":
    unittest.main()
