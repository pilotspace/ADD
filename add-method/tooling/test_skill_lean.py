#!/usr/bin/env python3
"""Lean-skill guard (lean-pass M1) — one fence for all four compaction pools + the tree-wide goal.

Consolidates the four per-task fences (skill-core-compact · orchestration-fold · phase-guides-trim
· reference-trim) into one parametrized module: each POOL must stay under its frozen byte budget
without any guide vanishing, and the WHOLE canonical tree must hold the milestone's headline
guardrail (≥25% under the pre-compaction baseline). These are REGRESSION fences — they pin the
won ground so the guides never regrow.

Token proxy = `wc -c` BYTES / 4 (the exact proxy every task froze — bytes, not unicode chars,
because the guides carry multibyte UTF-8: — → ⚠). Per-guide PROSE invariants (routing rows, XML
vocab, wording-lint, ARC/rubric anchors) are guarded by the full suite; 3-tree parity by
test_tree_parity + test_bundle_parity. This module reads the CANONICAL tree only.

Run: python3 -m unittest test_skill_lean -v
"""
import unittest
from pathlib import Path

_CANON = Path(__file__).resolve().parent.parent / "skill" / "add"

# Each pool: the guides it owns, its pre-compaction BYTE baseline (measured at the freeze),
# and the frozen ratio. target = int(baseline * ratio). Per-task targets are unchanged from the
# four original fences; the ratios differ because heavily test-pinned pools have an effectiveness
# floor (core 0.88, phases 0.80) while the load-on-demand reference pool carries the tree-wide cut.
# Baselines REBASELINED @ fast-lane-guide (human-approved "rebaseline for new surface"): the fast lane
# adds a genuinely NEW load-on-demand guide (`phases/fast-lane.md`, 1733 B) + a SKILL.md pointer — surface
# that did not exist at the M1 freeze. The RATIOS (the won compaction on every existing guide) are kept
# EXACTLY; each affected baseline grows by the new surface ÷ ratio, so the fence still pins the won ground:
#   reference 59421 → 61970 (+ ⌈1733/0.68⌉, the new guide), core 16894 → 17233 (+ ⌈pointer/0.88⌉).
# core 17233 → 17560: a SHORT SKILL.md quick-ref (orient commands + the opt-in feature flags --fast /
# --await-confirm) — new always-loaded surface, human-requested; ratio 0.88 kept.
# REBASELINED @ component-method-docs (same "rebaseline for genuinely-new surface" method): the component
# pillar adds a NEW load-on-demand guide (`components.md`, 2574 B) to the reference pool + a SKILL.md
# pointer (430 B). RATIOS kept EXACTLY; each baseline grows by new-surface ÷ ratio:
#   reference 61970 → 65756 (+⌈2574/0.68⌉), core 17560 → 18049 (+⌈430/0.88⌉). The won ground is untouched.
# core 18049 → 18465 @ flag-mode-quickref (same method): the "Opt-in flags" line becomes a labelled
# "Flag mode" quick-ref naming BOTH dials — fast (task lane) + auto (autonomy mode) — plus the blessed
# standalone lane + `todo` capture; +366 B new always-loaded surface, human-approved; ratio 0.88 kept
# (+⌈366/0.88⌉=416). The won ground is untouched.
POOLS = [
    {"name": "core",          "ratio": 0.88, "baseline": 18465,
     "guides": ["SKILL.md", "intake.md"]},
    {"name": "orchestration", "ratio": 0.75, "baseline": 50098,
     "guides": ["run.md", "streams.md", "advisor.md", "loop.md", "design.md"]},
    {"name": "phases",        "ratio": 0.80, "baseline": 37920,
     "guides": ["phases/0-ground.md", "phases/0-setup.md", "phases/1-specify.md",
                "phases/2-scenarios.md", "phases/3-contract.md", "phases/4-tests.md",
                "phases/5-build.md", "phases/6-verify.md", "phases/7-observe.md"]},
    {"name": "reference",     "ratio": 0.68, "baseline": 65756,
     "guides": ["scope.md", "deltas.md", "fold.md", "release.md", "report-template.md",
                "graduate.md", "soul.md", "setup-review.md", "adopt.md", "confidence.md",
                "compact-foundation.md", "phases/fast-lane.md", "components.md"]},
]

# The whole-tree headline guardrail: every .md in the canonical skill tree, ≥25% under baseline.
TREE_BASELINE_BYTES = 18049 + 50098 + 37920 + 65756   # = 171823, the sum of the four pool baselines
TREE_TARGET_BYTES = int(TREE_BASELINE_BYTES * 0.75)    # ≤125661 — still ≥25% lighter tree-wide

# Routing rows the SKILL.md phase table MUST keep (one guide per phase).
PHASE_GUIDES = [
    "phases/0-setup.md", "phases/0-ground.md", "phases/1-specify.md",
    "phases/2-scenarios.md", "phases/3-contract.md", "phases/4-tests.md",
    "phases/5-build.md", "phases/6-verify.md", "phases/7-observe.md",
]

# Load-on-demand pointers SKILL.md must keep naming.
ON_DEMAND_POINTERS = [
    "advisor.md", "compact-foundation.md", "confidence.md", "deltas.md",
    "design.md", "fold.md", "graduate.md", "intake.md", "loop.md",
    "release.md", "report-template.md", "run.md", "scope.md", "soul.md",
    "streams.md", "components.md",
]


def _pool_bytes(pool):
    return sum(len((_CANON / g).read_bytes()) for g in pool["guides"] if (_CANON / g).exists())


class SkillLeanTest(unittest.TestCase):
    def test_no_guide_dropped(self):
        for pool in POOLS:
            missing = [g for g in pool["guides"] if not (_CANON / g).exists()]
            self.assertEqual(missing, [], f"{pool['name']} pool dropped guide(s) — never drop a guide: {missing}")

    def test_pools_under_byte_budget(self):
        for pool in POOLS:
            target = int(pool["baseline"] * pool["ratio"])
            nbytes = _pool_bytes(pool)
            self.assertLessEqual(
                nbytes, target,
                f"{pool['name']} pool is {nbytes} bytes; frozen target is ≤{target} "
                f"({int((1 - pool['ratio']) * 100)}% under the {pool['baseline']}-byte baseline). "
                f"Compact: {', '.join(pool['guides'])}.",
            )

    def test_tree_under_byte_budget(self):
        """The milestone headline: the whole canonical skill tree ≥25% lighter."""
        nbytes = sum(len(p.read_bytes()) for p in _CANON.rglob("*.md"))
        self.assertLessEqual(
            nbytes, TREE_TARGET_BYTES,
            f"whole skill tree is {nbytes} bytes; the milestone guardrail is ≤{TREE_TARGET_BYTES} "
            f"(≥25% under the {TREE_BASELINE_BYTES}-byte pre-compaction baseline).",
        )

    def test_core_routing_rows_present(self):
        skill = (_CANON / "SKILL.md").read_text()
        missing = [g for g in PHASE_GUIDES if g not in skill]
        self.assertEqual(missing, [], f"routing_lost: SKILL.md dropped phase guide rows: {missing}")

    def test_core_pointers_present(self):
        skill = (_CANON / "SKILL.md").read_text()
        missing = [p for p in ON_DEMAND_POINTERS if f"`{p}`" not in skill]
        self.assertEqual(missing, [], f"dropped load-on-demand pointer(s) from SKILL.md: {missing}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
