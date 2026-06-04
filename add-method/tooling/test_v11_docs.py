#!/usr/bin/env python3
"""v11 — trust-layer truth: the book + skill must say what the engine does.

These guards pin the contradictions v11 fixed so they cannot silently regress.
For each, we assert BOTH that the corrected claim is present AND that the stale,
contradicted claim is gone (words-exist alone catches deletion, not contradiction):

  - Verify is no longer "human only" — auto-PASS on evidence is the default.
  - The human-led front is ONE approval at the contract seam, not three.
  - The flow is SEVEN steps (Observe is step 7), reconciled across ch02 + Matrix 3.
  - Competency deltas / the fold ritual / parallel streams now have book coverage.

Run: python3 -m unittest test_v11_docs -v
"""
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
DOCS = _ADD_METHOD / "docs"
SKILL = _ADD_METHOD / "skill" / "add"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class VerifyBothBranchTest(unittest.TestCase):
    """Verify is auto-gated by default; the 'no AI role' contradiction is gone."""

    def test_verify_chapter_describes_auto_gate(self):
        raw = _read(DOCS / "08-step-6-verify.md")
        low = raw.lower()
        self.assertNotIn("there is no ai role", low,
                         "08-verify still claims Verify has no AI role (contradicts the auto-gate)")
        self.assertIn("auto", low, "08-verify must describe the evidence auto-gate")
        self.assertIn("autonomy", low, "08-verify must name the autonomy dial")
        self.assertIn("hard-stop", low, "08-verify must keep security as a HARD-STOP escalation")

    def test_verify_phase_guide_describes_auto_gate(self):
        low = _read(SKILL / "phases" / "6-verify.md").lower()
        self.assertNotIn("there is no ai role", low,
                         "phases/6-verify.md still says 'no AI role' (contradicts run.md)")
        self.assertIn("autonomy", low)
        self.assertIn("auto", low)


class OneApprovalFrontTest(unittest.TestCase):
    """The front is one approval at the contract seam; SKILL header is current."""

    def test_skill_router_states_one_approval(self):
        raw = _read(SKILL / "SKILL.md")
        self.assertIn("one approval", raw.lower(), "SKILL.md must name the one-approval front")
        self.assertIn("v6–v7", raw, "the dynamic-run header must be bumped past bare v6")

    def test_step_chapters_name_the_bundle(self):
        for ch in ("04-step-2-scenarios.md", "05-step-3-contract.md", "06-step-4-tests.md"):
            low = _read(DOCS / ch).lower()
            self.assertIn("bundle", low, f"{ch} must mention the one-approval bundle")
            self.assertTrue("one approval" in low or "one-approval" in low,
                            f"{ch} must mention the single (one-)approval front")


class SevenStepsTest(unittest.TestCase):
    """The flow is seven steps; the six-step framing is gone, Observe is in Matrix 3."""

    def test_flow_chapter_says_seven_steps(self):
        low = _read(DOCS / "02-the-flow.md").lower()
        self.assertIn("seven steps", low)
        self.assertNotIn("flow of six steps", low,
                         "02-the-flow still frames the flow as six steps")

    def test_matrix3_has_observe_row(self):
        low = _read(DOCS / "appendix-f-requirements-matrix.md").lower()
        self.assertIn("seven steps", low)
        self.assertIn("observe", low, "Matrix 3 must include the Observe step")
        self.assertNotIn("(the six steps)", low,
                         "Matrix 3 header still says six steps")


class ShippedFeatureChaptersTest(unittest.TestCase):
    """deltas/fold and parallel-streams now have human-readable book coverage."""

    def test_loop_chapter_covers_deltas_and_fold(self):
        low = _read(DOCS / "09-the-loop.md").lower()
        self.assertIn("competency delta", low)
        self.assertIn("udd", low, "the five-competency tagging must appear (UDD is distinctive)")
        self.assertIn("fold", low, "09 must describe the foundation fold")
        self.assertIn("add.py deltas", low, "09 must name the deltas tooling")

    def test_setup_chapter_covers_parallel_streams(self):
        low = _read(DOCS / "10-setup-and-stages.md").lower()
        self.assertIn("parallel streams", low)
        self.assertIn("ready-queue", low)
        self.assertIn("review-queue", low)


if __name__ == "__main__":
    unittest.main(verbosity=2)
