#!/usr/bin/env python3
"""Content-pin guard for the fable Floor reasoning pass (task `fable-floor-reasoning`).

Four reasoning disciplines distilled from the fable-thinking protocol were added to
the ADD method PROSE — claim grammar (advisor Return), the pre-freeze Floor
(Goal + Leftovers), GROUND observation-over-memory, and the output-shape
constraint-loop — all in the direction phase guide + the advisor agent.

This suite pins the CONTENT is present in every live tree; byte-parity across trees
(M5) and the engine pin (M6) stay owned by test_tree_parity.py — not re-tested here.

Skip policy mirrors test_tree_parity: canonical + bundled are git-tracked and ALWAYS
checked (their absence is a hard failure); the gitignored .claude dogfood twins are
checked only when present. Run: python3 -m unittest test_fable_floor -v
"""
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
_BUNDLE = _ADD_METHOD / "src" / "add_method" / "_bundled"

# (canonical, bundled) are git-tracked → always present; the third is the dogfood twin.
ADVISORS = [
    _ADD_METHOD / "agents" / "add-advisor.md",
    _BUNDLE / "agents" / "add-advisor.md",
    _REPO / ".claude" / "agents" / "add-advisor.md",
]
DIRECTIONS = [
    _ADD_METHOD / "skill" / "add" / "phases" / "direction.md",
    _BUNDLE / "skill" / "add" / "phases" / "direction.md",
    _REPO / ".claude" / "skills" / "add" / "phases" / "direction.md",
]


def _live(paths):
    """Git-tracked first two always live; a missing tracked file is a hard failure."""
    for tracked in paths[:2]:
        assert tracked.is_file(), f"git-tracked method file missing: {tracked}"
    return [p for p in paths if p.is_file()]


def _bullet_containing(body, needle):
    """Return the single markdown bullet (`- ...` up to the next bullet/blank-block)
    that contains `needle` — so a content pin can require tokens CO-LOCATED in one
    bullet, not merely present somewhere in the file (Goal/invariant pre-exist elsewhere
    in direction.md; a whole-file check would pass vacuously)."""
    bullets = [b for b in re.split(r"\n(?=- )", body) if b.startswith("- ")]
    hits = [b for b in bullets if needle in b]
    return hits[0] if hits else ""


class FableFloorContentTest(unittest.TestCase):
    def test_claim_grammar_in_advisor_return(self):
        """M1 — advisor §6 Return defines the OBSERVED/DERIVED/PRIOR/ASSUMED legend."""
        for p in _live(ADVISORS):
            body = p.read_text(encoding="utf-8")
            for tag in ("OBSERVED", "DERIVED", "PRIOR", "ASSUMED"):
                self.assertIn(tag, body, f"{p}: claim-grammar tag {tag!r} missing")

    def test_floor_goal_and_leftovers_prefreeze(self):
        """M2 — a pre-freeze Floor bullet names Goal AND Leftovers AND invariants,
        CO-LOCATED (Goal/invariant pre-exist elsewhere, so require one bullet)."""
        for p in _live(DIRECTIONS):
            bullet = _bullet_containing(p.read_text(encoding="utf-8"), "eftover")
            self.assertTrue(bullet, f"{p}: no Floor/Leftovers bullet")
            for tok in ("Floor", "Goal", "invariant"):
                self.assertIn(tok, bullet,
                              f"{p}: Floor bullet lacks {tok!r} — got:\n{bullet[:400]}")

    def test_ground_observation_over_memory(self):
        """M3 — a recalled fact is PRIOR until re-confirmed live this session."""
        for p in _live(DIRECTIONS):
            body = p.read_text(encoding="utf-8")
            self.assertRegex(
                body, r"PRIOR until",
                f"{p}: GROUND lacks the observation-over-memory rule")

    def test_constraint_loop_before_freeze(self):
        """M4 — one output-shape self-verify bullet naming census/covers/REDS AND the
        mechanical step, CO-LOCATED in a single bullet."""
        for p in _live(DIRECTIONS):
            bullet = _bullet_containing(p.read_text(encoding="utf-8"), "census")
            self.assertTrue(bullet, f"{p}: no tag-census bullet")
            for tok in ("census", "REDS", "covers"):
                self.assertIn(tok, bullet, f"{p}: constraint-loop bullet lacks {tok!r}")
            self.assertRegex(
                bullet, r"(?i)(self-verify|mechanically)",
                f"{p}: constraint-loop bullet lacks the mechanical self-verify step")


if __name__ == "__main__":
    unittest.main(verbosity=2)
