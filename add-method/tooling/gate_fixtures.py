"""Shared frozen-record fixture shapes for the gate/freeze test suites.

kernel-trim (ADD 2.0 M5): these constants lived in test_gate_audit.py — the ONE
place for the frozen record shapes. The `audit` verb died with its suite; the
shapes survive here for the suites that pin KEPT surface (high-risk signal,
unflagged-freeze refusal). Fixture-only: no tests, no add.py import.
"""

GOOD3 = "Status: FROZEN @ v1 — approved by Tin, 2026-06-05"
SEC_CLEAN = "  - [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only"
SEC_NOTE = ("  - [x] no exposed secrets, injection openings, or unexpected dependencies — NOTE\n"
            "        (security line): residual metadata touch outside the root")
REC_AUTO = ("### GATE RECORD\nOutcome: PASS (auto-resolved on complete evidence)\n"
            "Reviewed by: auto-gate under autonomy: auto · date: 2026-06-05")
REC_HUMAN = ("### GATE RECORD\nOutcome: PASS — human-confirmed\n"
             "Reviewed by: Tin (human gate) · date: 2026-06-05")


def _sec6(item=SEC_CLEAN, record=REC_AUTO):
    return f"{item}\n\n{record}"
