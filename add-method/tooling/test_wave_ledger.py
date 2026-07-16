#!/usr/bin/env python3
"""wave-ledger — WAVE.md, the wave's resume point: a transient, evidence-bearing ledger.

streams.md:75 mandates "record which worker holds which task" but names no home; the
semantic wave state (task ↔ lease ↔ fork-base ↔ autonomy ↔ merge-order ↔ mid-wave
decisions) lived only in the orchestrator's chat context. v10's stale-base incident and
its v12-1 RECURRENCE ("the orchestrator never ran the check — it must EXECUTE pre-spawn")
proved orchestrator discipline without an artifact fails. This suite pins the WAVE.md
convention the same way test_streams.py pins the rubric's safety clauses: distinctive
lowercased substrings, so wording can evolve but a deleted guarantee fails loudly.

Run: python3 -m unittest test_wave_ledger -v
"""
import unittest
from pathlib import Path

import md_section

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
SKILL = _ADD_METHOD / "skill" / "add"


def _section(low: str, heading: str) -> str:
    """Return the lowercased text of one '## ' section (heading → next '## ')."""
    return md_section.section(low, heading)


class WaveLedgerClauseTest(unittest.TestCase):
    """The Wave ledger section and its template must exist and stay complete."""

    @classmethod
    def setUpClass(cls):
        cls.low = (SKILL / "streams.md").read_text(encoding="utf-8").lower()
        cls.sec = _section(cls.low, "## wave ledger")

    # -- wave_ledger_clause_missing -------------------------------------------------
    def test_wave_ledger_section_present(self):
        self.assertIn("## wave ledger", self.low,
                      "wave_ledger_clause_missing: streams.md must define the Wave ledger section")
        self.assertIn("wave.md", self.sec,
                      "wave_ledger_clause_missing: the section must name the WAVE.md artifact")
        self.assertIn(".add/milestones/", self.sec,
                      "wave_ledger_clause_missing: WAVE.md must live under the milestone dir")
        self.assertIn("resume point", self.sec,
                      "wave_ledger_clause_missing: WAVE.md is the wave's resume point — the analog of state.json for a wave")
        self.assertIn("one live wave", self.sec,
                      "wave_ledger_clause_missing: one live wave per milestone at a time")

    def test_template_homes_semantic_mapping(self):
        for token in ("lease", "fork-base", "autonomy", "spawned", "timeout",
                      "mid-wave decisions", "merge order"):
            self.assertIn(token, self.sec,
                          f"wave_ledger_clause_missing: the ledger must home '{token}' — "
                          "the semantic mapping streams.md mandates but never housed")

    # -- wave_evidence_cell_optional ------------------------------------------------
    def test_evidence_cell_requires_pasted_output(self):
        self.assertIn("rev-parse", self.sec,
                      "wave_evidence_cell_optional: the fork-base cell must hold the pasted "
                      "`git -C <wt> rev-parse HEAD` output, equal to the recorded wave base")
        self.assertIn("paste", self.sec,
                      "wave_evidence_cell_optional: pasted command output, never a bare tick — "
                      "a row must be fillable only by EXECUTING the pre-spawn check (v12-1)")

    # -- wave_merge_exclusion_missing -----------------------------------------------
    def test_merge_back_exclusion_names_wave(self):
        merge = _section(self.low, "## merge is serial")
        self.assertTrue(merge, "the 'Merge is serial' clause must remain (test_streams.py pins it too)")
        self.assertIn("wave.md", merge,
                      "wave_merge_exclusion_missing: WAVE.md must join state.json and MILESTONE.md "
                      "as never merged back from a worktree")

    # -- lifecycle + refusal rules --------------------------------------------------
    def test_lifecycle_and_refusals_documented(self):
        for code in ("wave_already_live", "unverified_fork_base", "digest_not_absorbed"):
            self.assertIn(code, self.sec,
                          f"the convention refusal '{code}' must be named in the section")
        self.assertIn("wave log", self.sec,
                      "digest_not_absorbed: the digest home must be named — the append-only "
                      "'## Wave log' block in MILESTONE.md, doubling as the integration-Verify record")
        i_digest = self.sec.find("digest")
        i_delete = self.sec.find("delete")
        self.assertNotEqual(i_digest, -1, "lifecycle must state the digest step")
        self.assertNotEqual(i_delete, -1, "lifecycle must state the delete step")
        self.assertLess(i_digest, i_delete,
                        "digest_not_absorbed: the evidence digest is absorbed into MILESTONE.md "
                        "BEFORE deletion — delete-first loses the proof the base-check executed")

    def test_worker_visibility_and_resume_rules(self):
        self.assertIn("workers never read", self.sec,
                      "workers never read WAVE.md — decisions are PROMPT-folded at spawn/respawn")
        self.assertIn("prompt", self.sec,
                      "the PROMPT-folding rule must be stated next to the visibility rule")
        self.assertIn("never from", self.sec,
                      "the resume rule must say: re-orient from the live ledger, never from memory")

    # -- additive guarantee: RETIRED. Its target (StreamsSafetyClausesTest, the streams.md
    # prose-clause guard) was deliberately gutted by the human-approved md ceremony-cut
    # (d264c38) — this meta-test dangled on a deleted class ever since. The surviving
    # streams behavior guards (slug routing, wave protocol runtime, worker strategy pull)
    # run in test_streams.py directly. Removed under the wordy-test authorization
    # (thin-engine-loop MILESTONE.md, 2026-07-16).


if __name__ == "__main__":
    unittest.main(verbosity=2)
