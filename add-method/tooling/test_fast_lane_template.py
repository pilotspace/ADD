#!/usr/bin/env python3
"""Red/green tests for the minimal "fast lane" TASK.md template (task fast-lane-template,
milestone fast-lane).

A template-artifact task: ship `templates/TASK.fast.md.tmpl` (a strict SUBSET of the full
TASK.md.tmpl) + an embedded `add._FALLBACK_TASK_FAST` circuit-breaker analog, and extend
`_render_template`'s fallback branch to cover "TASK.fast.md". The frozen seam (§3 of the
task's TASK.md) is the kept-section set {1,3,4,5,6} (DROP §2 SCENARIOS, §7 OBSERVE) plus
the trust-floor marker lines that the engine's gate guards read. (plan-phase-core: §0 GROUND
folded into §3 PLAN's ### Grounding sub-block — §0 is no longer a heading of its own.)

The `--fast` flag + cmd_new_task wiring + check/audit tolerance are OUT OF SCOPE here (owned
by fast-new-task-flag); this suite pins only the artifact + fallback + parity across 3 trees.

    python3 -m unittest test_fast_lane_template -v
"""
import re
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent              # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

CANON_FAST = HERE / "templates" / "TASK.fast.md.tmpl"
DOG_FAST = REPO / ".add" / "tooling" / "templates" / "TASK.fast.md.tmpl"
BUNDLE_FAST = BUNDLE / "tooling" / "templates" / "TASK.fast.md.tmpl"
FAST_TREES = (CANON_FAST, DOG_FAST, BUNDLE_FAST)

CANON_FULL = HERE / "templates" / "TASK.md.tmpl"

KEPT = {1, 3, 4, 5, 6}                # the frozen kept-section set (§0 folded into §3 PLAN)
DROPPED = {2, 7}                     # §2 SCENARIOS, §7 OBSERVE (TASK.md SECTION numbers)
DROPPED_IDX = set()                  # no whole-phase drop left: §2 folds into specify's
                                     # body (phase-merge-specify) so its absence is not empty
                                     # (plan=1, observe=5; n is the ordinal, not the §-number)


def _sections(text: str) -> set[int]:
    """Section numbers present, via the engine's own canonical heading scan."""
    return set(add._phase_spans(text))


def _floor_missing(text: str) -> set[int]:
    """The retrieve+persist floor: §3 CONTRACT + §6 GATE RECORD must both be present."""
    secs = _sections(text)
    missing = set()
    if 3 not in secs or "Status:" not in text:
        missing.add(3)
    if 6 not in secs or "### GATE RECORD" not in text:
        missing.add(6)
    return missing


class FastTemplateExists(unittest.TestCase):
    def test_canonical_template_exists(self):
        self.assertTrue(CANON_FAST.exists(), f"missing {CANON_FAST}")

    def test_present_in_all_three_trees(self):
        for p in FAST_TREES:
            self.assertTrue(p.exists(), f"missing fast template tree: {p}")

    def test_three_trees_byte_identical(self):
        texts = {p.read_text(encoding="utf-8") for p in FAST_TREES}
        self.assertEqual(len(texts), 1, "fast template diverges across the 3 parity trees")


class SubsetSectionSet(unittest.TestCase):
    def setUp(self):
        self.text = CANON_FAST.read_text(encoding="utf-8")

    def test_kept_section_set_is_exactly_1_3_4_5_6(self):
        self.assertEqual(_sections(self.text), KEPT)

    def test_scenarios_and_observe_are_absent(self):
        secs = _sections(self.text)
        for n in DROPPED:
            self.assertNotIn(n, secs)

    def test_sections_ascend(self):
        nums = [int(m.group(1))
                for m in re.finditer(r"(?m)^##\s*(\d+)\s*·", self.text)]
        self.assertEqual(nums, sorted(nums), "section headings must ascend")


class TrustFloorRetained(unittest.TestCase):
    def setUp(self):
        self.text = CANON_FAST.read_text(encoding="utf-8")

    def test_freeze_flag_line_present(self):          # feeds _flag_well_formed at freeze
        self.assertIn("Least-sure flag surfaced at freeze:", self.text)

    def test_gate_record_present(self):               # feeds _stamp_gate_record
        self.assertIn("### GATE RECORD", self.text)
        self.assertRegex(self.text, r"(?m)^Outcome:")
        self.assertIn("Reviewed by:", self.text)

    def test_ground_anchors_line_present(self):       # feeds _grounded_state
        self.assertIn("Anchors the contract cites:", self.text)

    def test_red_before_build_note_present(self):
        self.assertRegex(self.text, r"red.*before\s+Build|before\s+Build.*red")

    def test_scope_line_present(self):                # scope-gate declaration
        self.assertIn("Scope (may touch):", self.text)

    def test_floor_not_missing(self):
        self.assertEqual(_floor_missing(self.text), set())

    def test_component_affordance_present(self):      # component-registry-fill: monorepo hint
        # the fast lane carries the same `component:` binding affordance as the full template,
        # so a fast task in a monorepo can bind a component (its root joins §5, its bar gates).
        self.assertIn("component:", self.text)
        # it is an in-template HINT (a comment), not a live header line that would parse as a binding
        self.assertRegex(self.text, r"<!--[^>]*component:\s*<name>")


class HeaderAndRender(unittest.TestCase):
    def setUp(self):
        self.rendered = add._render_template(
            "TASK.fast.md", title="T", slug="s", date="2026-06-23",
            stage="mvp", autonomy="auto", milestone="(none)")

    def test_fast_marker_line_present(self):
        self.assertRegex(self.rendered, r"(?m)^fast:\s*true")

    def test_no_substitution_token_remains(self):
        self.assertNotIn("{{", self.rendered)
        self.assertNotIn("}}", self.rendered)

    def test_task_phases_renders_without_error(self):
        # absent sections must fail-closed to "(empty)", not raise
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / ".add"
            (root / "tasks" / "s").mkdir(parents=True)
            (root / "tasks" / "s" / "TASK.md").write_text(self.rendered, encoding="utf-8")
            phases = add.task_phases(root, "s")
        self.assertEqual(len(phases), 3)              # direction·build·verify (phase-collapse-3)
        bynum = {p["n"]: p["body"] for p in phases}   # keyed by PHASE INDEX (n), not §-number
        for n in DROPPED_IDX:
            self.assertEqual(bynum[n], "(empty)")     # dropped phases render empty, no crash
        self.assertNotEqual(bynum[0], "(empty)",
                            "specify renders §1 even with §2 absent (fast template)")


class BuildExpectationsWording(unittest.TestCase):
    def setUp(self):
        self.text = CANON_FAST.read_text(encoding="utf-8")

    def test_build_expectations_cites_kept_sections(self):
        self.assertIn("Build expectations", self.text)
        self.assertIn("Accept", self.text)            # the folded scenario lives in §1 Accept

    def test_does_not_reference_dropped_scenarios_section(self):
        self.assertNotIn("§2 SCENARIOS", self.text)


class FallbackParity(unittest.TestCase):
    def test_fallback_constant_exists(self):
        self.assertTrue(hasattr(add, "_FALLBACK_TASK_FAST"))

    def test_fallback_section_set_matches_file(self):
        file_secs = _sections(CANON_FAST.read_text(encoding="utf-8"))
        fb_secs = _sections(add._FALLBACK_TASK_FAST)
        self.assertEqual(fb_secs, file_secs, "fallback_drift: fallback != file section set")

    def test_fallback_used_when_file_absent(self):
        # _render_template must fall back for TASK.fast.md (not only TASK.md)
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            empty = Path(d)
            with mock.patch.object(add, "_templates_dir", return_value=empty):
                out = add._render_template(
                    "TASK.fast.md", title="T", slug="s", date="2026-06-23",
                    stage="mvp", autonomy="auto", milestone="(none)")
        self.assertIn("### GATE RECORD", out)         # the fallback carried the floor
        self.assertNotIn("{{", out)


class MateriallySmaller(unittest.TestCase):
    def setUp(self):
        self.fast = CANON_FAST.read_text(encoding="utf-8")
        self.full = CANON_FULL.read_text(encoding="utf-8")

    def test_strictly_fewer_sections(self):
        self.assertEqual(len(_sections(self.fast)), 5)
        self.assertEqual(len(_sections(self.full)), 7)   # §1..§7 (§0 folded into §3 PLAN)
        self.assertLess(len(_sections(self.fast)), len(_sections(self.full)))

    def test_substantially_fewer_lines(self):
        fast_lines = len(self.fast.splitlines())
        full_lines = len(self.full.splitlines())
        self.assertLess(fast_lines, full_lines * 0.6,
                        f"fast {fast_lines} not < 60% of full {full_lines}")


class RejectGuards(unittest.TestCase):
    """The reject codes are pinned as test-level invariants (engine tolerance is the next task)."""

    def setUp(self):
        self.text = CANON_FAST.read_text(encoding="utf-8")

    def test_missing_floor_detected(self):
        # synthetic: strip §3 -> floor check reports it; shipped template never does
        stripped = re.sub(r"(?ms)^## 3 ·.*?(?=^## 4 ·)", "", self.text)
        self.assertIn(3, _floor_missing(stripped))
        self.assertEqual(_floor_missing(self.text), set())

    def test_malformed_sections_detected(self):
        # an unnumbered heading is invisible to _phase_spans -> kept-set check fails
        malformed = self.text.replace("## 1 ·", "## SPECIFY ·")
        self.assertNotEqual(_sections(malformed), KEPT)
        self.assertEqual(_sections(self.text), KEPT)

    def test_fallback_drift_detected(self):
        drifted = add._FALLBACK_TASK_FAST + "\n## 7 · OBSERVE\n"
        self.assertNotEqual(_sections(drifted), _sections(self.text))


if __name__ == "__main__":
    unittest.main()
