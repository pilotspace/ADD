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
# phases 37920 → 38298 @ setup-tests-before-build (F6, same method): 0-setup.md now drafts the full
# §1–§4 bundle (the §4 red suite via phases/4-tests.md) + the Exit gate requires it RED before build —
# closing the audit hole where setup reached build with NO red test; +302 B routing surface, human-approved;
# ratio 0.80 kept (+⌈302/0.80⌉=378). The won ground is untouched.
# phases 38298 → 39008 @ ground-phase-harden (same method): 0-ground.md's <exit_gate> now names all four
# grounding fields (the missing Context check) + a "grounding is complete when…" STRONG-vs-placeholder
# rubric; +568 B human-approved surface, ratio 0.80 kept (+⌈568/0.80⌉=710). The won ground is untouched.
# reference 65756 → 66345 @ ground-phase-harden (same method): scope.md's "Position the goal — ground in
# assets" step gained the SAME four-field rubric at milestone altitude (a milestone grounds as rigorously as
# a task §0); +400 B human-approved surface, ratio 0.68 kept (+⌈400/0.68⌉=589). The won ground is untouched.
POOLS = [
    # core 18465 → 19675 @ roadmap-intake-guide (same "rebaseline for human-approved new surface" method):
    # intake.md gains a NEW "## Roadmap" section (decompose an N-milestone request → 1 active + N−1
    # `new-milestone --queued`, promote with `activate`) — +1064 B human-approved surface (milestone
    # multi-milestone-intake 2/3, contract FROZEN @ v1). RATIO 0.88 kept EXACTLY; baseline grows by
    # surface ÷ ratio (+⌈1064/0.88⌉=1210). The won compaction on SKILL.md + intake.md is untouched.
    # core 19675 → 20004 @ skill-todo-flag (same method): SKILL.md gains a front-of-skill `--todo`
    # fast-path block (route `/add --todo` to `add.py todo`: capture/list/close, then STOP) + the
    # argument-hint names --todo — +289 B human-approved surface (loose fast-lane task, contract FROZEN
    # @ v1). RATIO 0.88 kept EXACTLY; baseline grows by surface ÷ ratio (+⌈289/0.88⌉=329). Won ground untouched.
    # core 20004 → 20490 @ sensitivity-glossary (same method): SKILL.md's "Beyond the bundle" gains a
    # `sensitivity.md` pointer (the project-extensible risk-class vocabulary) — +427 B human-approved
    # surface (milestone advisor-gated-autonomy, contract FROZEN @ v1). RATIO 0.88 kept EXACTLY; baseline
    # grows by surface ÷ ratio (+⌈427/0.88⌉=486). The won compaction is untouched.
    {"name": "core",          "ratio": 0.88, "baseline": 20490,
     "guides": ["SKILL.md", "intake.md"]},
    # orchestration 50098 → 51732 @ design-intake-beat (same "rebaseline for human-approved new surface"
    # method): design.md's UDD loop gains a NEW front beat `### 0 · design-intake` (the four design axes
    # FIDELITY·CONCEPT·LAYOUT·VISUAL DESIGN) + a hard rule — +1225 B human-approved surface (milestone
    # udd-design-intake, contract FROZEN @ v1). RATIO 0.75 kept EXACTLY; baseline grows by surface ÷ ratio
    # (+⌈1225/0.75⌉=1634). The won compaction on every orchestration guide is untouched.
    # orchestration 51732 → 51994 @ security-escalation-disclosure (same "rebaseline for human-approved
    # new surface" method): run.md's auto bullet gains the honest "security escalates only a finding the
    # AI SURFACES; one it misses is invisible to the engine → human spot-audit is the only backstop"
    # disclosure — +196 B human-approved surface (milestone flow-honesty, contract FROZEN @ v1). RATIO
    # 0.75 kept EXACTLY; baseline grows by surface ÷ ratio (+⌈196/0.75⌉=262). The won compaction is untouched.
    # orchestration 51994 → 52464 @ build-strategy-solutions (same method): advisor.md's fenced plan-following
    # template gains a <strategy> block (mirrors the task's §5 Strategy + Known-problem fixes) + a prose clause —
    # +352 B human-approved surface (loose task, contract FROZEN @ v1). RATIO 0.75 kept EXACTLY; baseline grows
    # by surface ÷ ratio (+⌈352/0.75⌉=470). The won compaction is untouched.
    # orchestration 52464 → 52731 @ streams-strategy-pull (same method): streams.md's worker-contract
    # ```xml fence gains the SAME fenced <strategy> block (mirrors the task's §5), so the parallel-spawn
    # home matches the single advisor — +200 B human-approved surface (loose task, contract FROZEN @ v1).
    # RATIO 0.75 kept EXACTLY; baseline grows by surface ÷ ratio (+⌈200/0.75⌉=267). The won compaction is untouched.
    # orchestration 52731 → 53125 @ strategy-soft-not-hard (change-request, §3 FROZEN @ v1): the <strategy>
    # block is SOFTENED (preferred-not-hard + self-improve + report-the-strategy-used-for-audit) in BOTH
    # advisor.md and streams.md, and advisor's intro clause softened to match — +295 B human-approved surface
    # (block 198→327 ×2 files = +258, advisor intro 151→188 = +37). RATIO 0.75 kept EXACTLY; baseline grows
    # by surface ÷ ratio (+⌈295/0.75⌉=394). The won compaction is untouched.
    # orchestration 53125 → 54363 @ docs-align (advisor-gated-autonomy, same "rebaseline for human-approved
    # new surface" method): advisor.md gains the "3-lens sequential checklist at verify" section (+248 B) and
    # run.md gains the Advisor-3-lens-verdict auto-gate bullet + the `advisor-gate-relax` pathway bullet (+680 B)
    # — the milestone's autonomy feature documented at its homes. RATIO 0.75 kept EXACTLY; baseline grows by
    # surface ÷ ratio (+⌈928/0.75⌉=1238). The won compaction is untouched.
    # orchestration 54363 → 55159 @ phase-agent-roster (same "rebaseline for human-approved new surface"
    # method): advisor.md gains the "## The phase-specialist roster" section — the 9 registered phase-specialist
    # subagents (`add-<phase>`) + the spawn convention (plugin `add:add-<phase>` / project bare) — documenting
    # the agency-agents roster at its spawn-authority home. +597 B human-approved surface (direct batch on
    # feat/persona-distillation-depth, Tin-approved rebaseline). RATIO 0.75 kept EXACTLY; baseline grows by
    # surface ÷ ratio (+⌈597/0.75⌉=796). The won compaction on the orchestration guides is untouched.
    # orchestration: phase-parallel-execution adds streams.md's "## Phase-parallel execution — prefer the
    # roster" section but is ABSORBED by compaction (NOT a rebaseline) — streams.md's worker-contract prose,
    # the design-for-failure bullets, and the spawn-adapter prose were tightened to fit the new section under
    # the unchanged 55159 baseline. Leaner-net is the project goal: do not bump the budget for in-guide surface.
    {"name": "orchestration", "ratio": 0.75, "baseline": 55159,
     "guides": ["run.md", "streams.md", "advisor.md", "loop.md", "design.md"]},
    # phases 39008 → 39446 @ security-escalation-disclosure (same method): phases/6-verify.md's Security
    # residue bullet gains the disclosure that `unescalated_security_note` sees only a MARKED note — a
    # finding never marked is invisible to the engine, so a human spot-audit is the only backstop under
    # `auto` — +350 B human-approved surface (milestone flow-honesty, contract FROZEN @ v1). RATIO 0.80
    # kept EXACTLY; baseline grows by surface ÷ ratio (+⌈350/0.80⌉=438). The won ground is untouched.
    # phases 39446 → 39523 @ build-strategy-enhance (commit c05a034, "enhance strategy section with
    # solution methods for task implementation"): phases/5-build.md's §5 Strategy prompt gains solution-method
    # guidance — +61 B human-authored surface (Tin-approved rebaseline). RATIO 0.80 kept EXACTLY; baseline
    # grows by surface ÷ ratio (+⌈61/0.80⌉=77). The won ground is untouched.
    # phases 39523 → 40065 @ docs-align (advisor-gated-autonomy, same method): phases/6-verify.md's Part-two
    # 3-lens checklist gains the §6 `### Advisor 3-lens verdict` recording instruction (Verdict · Residue ·
    # Binding + the `advisor_verdict_unrecorded` lint) — +433 B human-approved surface. RATIO 0.80 kept
    # EXACTLY; baseline grows by surface ÷ ratio (+⌈433/0.80⌉=542). The won ground is untouched.
    {"name": "phases",        "ratio": 0.80, "baseline": 40065,
     "guides": ["phases/0-ground.md", "phases/0-setup.md", "phases/1-specify.md",
                "phases/2-scenarios.md", "phases/3-contract.md", "phases/4-tests.md",
                "phases/5-build.md", "phases/6-verify.md", "phases/7-observe.md"]},
    # reference 66345 → 70282 @ sensitivity-glossary (same "rebaseline for genuinely-new surface" method):
    # a NEW load-on-demand guide (`sensitivity.md`, 2677 B — how the AI maintains the project's extensible
    # risk-class vocabulary) joins the reference pool. RATIO 0.68 kept EXACTLY; baseline grows by new-surface
    # ÷ ratio (+⌈2677/0.68⌉=3937). The won ground is untouched.
    # reference 70282 → 70359 @ docs-align (advisor-gated-autonomy, same method): sensitivity.md's mechanical
    # class names the three §6 advisor-verdict fields (Verdict · Residue · Binding) the engine reads for
    # `advisor-gate-relax` — +52 B human-approved surface. RATIO 0.68 kept EXACTLY; baseline grows by surface
    # ÷ ratio (+⌈52/0.68⌉=77). The won ground is untouched.
    {"name": "reference",     "ratio": 0.68, "baseline": 70359,
     "guides": ["scope.md", "deltas.md", "fold.md", "release.md", "report-template.md",
                "graduate.md", "soul.md", "setup-review.md", "adopt.md", "confidence.md",
                "compact-foundation.md", "phases/fast-lane.md", "components.md", "sensitivity.md"]},
]

# The whole-tree headline guardrail: every .md in the canonical skill tree, ≥25% under baseline.
# DERIVED from the pool baselines (lean-tree-baseline-derive / F10) — NOT a hand-summed literal: a pool
# rebaseline (surface÷ratio, see POOLS) now flows into the tree budget automatically, so the two can never
# drift again (the old literal lagged 802 B behind the live pools and needed a forgotten second edit). The
# tree budget floats up with each human-approved pool rebaseline; the 0.75 ratio is the unchanged guardrail.
TREE_BASELINE_BYTES = sum(p["baseline"] for p in POOLS)   # = the live sum of the four pool baselines
TREE_TARGET_BYTES = int(TREE_BASELINE_BYTES * 0.75)       # whole tree must stay ≥25% under that sum

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
    "streams.md", "components.md", "sensitivity.md",
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

    def test_tree_baseline_derived_from_pools(self):
        """lean-tree-baseline-derive (F10): the whole-tree baseline must be DERIVED from the pool
        baselines, never a hand-summed literal — so a pool rebaseline can't leave the tree budget
        lagging behind (the drift class: a stale tree sum + a second edit forgotten)."""
        self.assertEqual(
            TREE_BASELINE_BYTES, sum(p["baseline"] for p in POOLS),
            "TREE_BASELINE_BYTES must equal the sum of the pool baselines (derive it, don't hand-sum).",
        )

    def test_pool_rebaseline_propagates_to_tree(self):
        """A pool rebaseline propagates to the tree budget with no second edit — proven by bumping
        one pool's baseline by N and checking the derived tree baseline rises by exactly N."""
        N = 500
        bumped = sum(p["baseline"] for p in POOLS) + N
        self.assertEqual(
            bumped, TREE_BASELINE_BYTES + N,
            "a pool rebaseline must flow into TREE_BASELINE_BYTES automatically (it is the live sum).",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
