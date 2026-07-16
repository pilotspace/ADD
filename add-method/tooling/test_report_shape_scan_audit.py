#!/usr/bin/env python3
"""Red/green tests for report-shape-scan-audit (frozen @ v1, milestone loop-readability).

PROSE-ONLY task — no engine logic change. §3 CONTRACT: the two phase guides that fire
an actual contract-freeze (phases/3-plan.md, phases/0-setup.md) gain a minimal
citation of report-template.md's SHAPE block — the one gate SHAPE's own "freeze-only"
definition names as its use case. report-template.md itself is UNCHANGED (0 B delta):
its "Summary-first" bullet is byte-verbatim guarded by
test_question_summary_layer.py::test_existing_constraints_verbatim, and the other
candidate fix is redundant with SKILL.md's own compact pipeline map.

Mirrors §2 SCENARIOS M3/M4/M6/R1/R2/R4 (the mechanically-checkable ones; M1/M2/M5 are
audit-process scenarios verified by hand at the freeze, not re-derivable from file state).

Run: python3 -m unittest test_report_shape_scan_audit -v
"""
import hashlib
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
_BUNDLE = _ADD_METHOD / "src" / "add_method" / "_bundled"

CANON_SKILL = _ADD_METHOD / "skill" / "add"
DOG_SKILL = _REPO / ".claude" / "skills" / "add"
BUNDLE_SKILL = _BUNDLE / "skill" / "add"

CONTRACT_TRIO = (CANON_SKILL / "phases" / "3-plan.md",
                 DOG_SKILL / "phases" / "3-plan.md",
                 BUNDLE_SKILL / "phases" / "3-plan.md")
SETUP_TRIO = (CANON_SKILL / "phases" / "0-setup.md",
              DOG_SKILL / "phases" / "0-setup.md",
              BUNDLE_SKILL / "phases" / "0-setup.md")
REPORT_TMPL = CANON_SKILL / "report-template.md"

# the exact BEFORE fragments (verified byte-for-byte against the live files at ground time)
_CONTRACT_BEFORE = ("rendering the freeze APPROVE as a guided choice")
_CONTRACT_AFTER = ("rendering SHAPE then the freeze APPROVE as a guided choice")
_SETUP_BEFORE = ("render APPROVE as a guided choice, then present")
_SETUP_AFTER = ("render SHAPE then APPROVE as a guided choice, then present")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class ContractFreezeGateCitesShape(unittest.TestCase):
    """M3: phases/3-plan.md cites SHAPE at the contract-freeze gate."""

    def test_contract_gate_cites_shape(self):
        text = CONTRACT_TRIO[0].read_text(encoding="utf-8")
        self.assertIn(_CONTRACT_AFTER, text,
                      "3-plan.md must cite SHAPE at the freeze gate")
        self.assertNotIn(_CONTRACT_BEFORE, text,
                         "the pre-fix wording (no SHAPE) must not survive")

    def test_contract_mirrors_byte_identical(self):
        digests = {_md5(p) for p in CONTRACT_TRIO}
        self.assertEqual(len(digests), 1, "3-plan.md's 3 mirrors must be byte-identical")


class SetupGateCitesShape(unittest.TestCase):
    """M4: phases/0-setup.md cites SHAPE at the baseline-lock gate."""

    def test_setup_gate_cites_shape(self):
        text = SETUP_TRIO[0].read_text(encoding="utf-8")
        self.assertIn(_SETUP_AFTER, text,
                      "0-setup.md must cite SHAPE at the baseline-lock gate")
        self.assertNotIn(_SETUP_BEFORE, text,
                         "the pre-fix wording (no SHAPE) must not survive")

    def test_setup_mirrors_byte_identical(self):
        digests = {_md5(p) for p in SETUP_TRIO}
        self.assertEqual(len(digests), 1, "0-setup.md's 3 mirrors must be byte-identical")


class ReportTemplateUnchanged(unittest.TestCase):
    """R1/R2: report-shape-scan-audit itself left report-template.md at 0 B delta (9298 B) — the
    guarded bullet and the considered-but-redundant fix both stayed untouched BY THAT TASK. A later,
    separate direct chat-directed edit (report-template-recorded-loop) deliberately appended one new
    <constraints> bullet (+290 B) closing the loop with the report-rendered-trace `Reported:` field —
    the byte count migrates forward here (same convention as a release test's version bump) so this
    class keeps proving no OTHER, unrecorded drift occurs."""

    def test_report_template_byte_count_unchanged(self):
        self.assertEqual(len(REPORT_TMPL.read_bytes()), 9514,
                         "report-template.md drifted beyond its recorded, deliberate additions "
                         "(9298 @ report-shape-scan-audit + 290 B @ report-template-recorded-loop "
                         "+ 39 B @ intake-freeze-batch: the Batch-don't-serialize hard rule "
                         "+ the BUILD-PLAN-is-the-HOW bullet @ plan-in-report, net −1 B of "
                         "same-guide compression, then −3 B @ status-lean-default: the m-goal "
                         "line points at `status --all`, then −109 B @ persona-owns-gates: the "
                         "fixed report-blocks MANDATE retired to persona-owned PRINCIPLES + a "
                         "four-floors block, net −109 B after same-guide compression of the "
                         "now-optional prescriptive prose — keeping the reference pool under budget)")

    def test_guarded_bullet_untouched(self):
        text = REPORT_TMPL.read_text(encoding="utf-8")
        self.assertIn("**Summary-first.** Never bury the decision under a task list or a diff.",
                      text, "the byte-verbatim-guarded bullet must survive unedited")


class PoolBudgetsHold(unittest.TestCase):
    """M6: both affected lean-fence pools measure within budget after the edit."""

    def test_phases_and_reference_pools_under_budget(self):
        import test_skill_lean as tsl
        for pool in tsl.POOLS:
            if pool["name"] not in ("phases", "reference"):
                continue
            target = int(pool["baseline"] * pool["ratio"])
            nbytes = sum(len((tsl._CANON / g).read_bytes())
                        for g in pool["guides"] if (tsl._CANON / g).exists())
            self.assertLessEqual(nbytes, target,
                                 f"{pool['name']} pool {nbytes} B must stay <= {target} B")


if __name__ == "__main__":
    unittest.main(verbosity=2)
