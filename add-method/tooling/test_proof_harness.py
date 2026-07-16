#!/usr/bin/env python3
"""Proof-harness: the executable acceptance layer for the gate guardrails the BOOK
promises (task: proof-harness, milestone v2).

These tests are the delta over the existing suite — they do NOT re-prove the golden
flow (test_quickstart) or injection-by-reference (test_guidelines). They pin the one
divergence the harness surfaces — `gate PASS` could skip `verify` — and the
invariants that must hold around the fix. Each test maps to a requirements-matrix
row (see add-method/docs/appendix-f-requirements-matrix.md, "Matrix 4").
Run: python3 -m unittest test_proof_harness -v
"""
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

GLOSSARY = Path(__file__).resolve().parent.parent / "docs" / "appendix-c-glossary.md"


class ProofHarnessTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-proof-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-task", "t", "--title", "Feature"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _freeze(self, slug="t"):
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    # --- Matrix 3 / principle 7: no silent skips -----------------------------
    def test_gate_pass_refused_before_verify(self):
        # the divergence: the engine must REFUSE PASS before the task reaches verify
        with self.assertRaises(SystemExit) as cm:
            add.main(["gate", "PASS"])               # phase is "direction" (phase-collapse-3 seed)
        self.assertEqual(cm.exception.code, 1)       # _die default; cf. check's exit 1
        st = self._state()["tasks"]["t"]
        self.assertEqual(st["phase"], "direction", "refused gate must NOT advance phase")
        self.assertEqual(st["gate"], "none", "refused gate must NOT record an outcome")

    # --- Matrix 3: done only when Verify reads PASS ---------------------------
    def test_gate_pass_at_verify_reaches_done(self):
        self._freeze()  # freeze-gate-universal: §3 must be FROZEN before the direction->build crossing
        for _ in range(2):                            # direction -> build -> verify
            add.main(["advance"])
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "verify")
        add.main(["gate", "PASS"])
        st = self._state()["tasks"]["t"]
        self.assertEqual(st["phase"], "done")
        self.assertEqual(st["gate"], "PASS")

    # --- SPECIFY escape-hatch rule: deliberate override is allowed ------------
    def test_phase_override_escape_hatch(self):
        add.main(["phase", "verify", "t"])            # explicit, logged jump
        add.main(["gate", "PASS"])                    # now permitted
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "done")

    # --- book invariant: a security finding is ALWAYS HARD-STOP, any phase ----
    def test_hardstop_recordable_mid_build(self):
        self._freeze()  # freeze-gate-universal: §3 must be FROZEN before entering build
        add.main(["phase", "build", "t"])
        add.main(["gate", "HARD-STOP"])
        st = self._state()["tasks"]["t"]
        self.assertEqual(st["gate"], "HARD-STOP")
        self.assertEqual(st["phase"], "build", "HARD-STOP must not force phase to done")

    # --- Story <-> State consistency: the book's outcomes match the engine ----
    def test_book_gate_outcomes_match_engine(self):
        documented = {"PASS", "RISK-ACCEPTED", "HARD-STOP"}
        self.assertTrue(documented.issubset(set(add.GATES)),
                        f"book outcomes {documented} must all be engine GATES {add.GATES}")
        glossary = GLOSSARY.read_text(encoding="utf-8")
        for term in documented:
            self.assertIn(term, glossary, f"glossary must define gate outcome {term!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
