# PLAN: strategy.md: the explicit risk-proportional depth ladder (micro skips, zero cost)

slug: risk-proportional-skip · created: 2026-07-24 · stage: mvp
milestone: strategy-intake
autonomy: auto
gate_mode: ai-plan-verify
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an explicit **risk-proportional depth ladder** in strategy.md — one legible section that states how the strategy loop's DEPTH scales with a milestone's risk/size: micro/`--tiny` skips entirely (drafted-blank, zero added per-turn cost) · multi-task but low-uncertainty runs the loop without the advisor · high-uncertainty runs the full loop + the advisor refute. Today those three tiers are scattered across the Skip line, the Trigger line, and the CONVERGE advisor-skip; this unifies them so a reader SEES depth-scales-by-risk as one rule, and states the zero-cost micro guarantee as first-class.
Framings weighed: an explicit unified ladder section in strategy.md (chosen — the three tiers already EXIST but are inferred from scattered lines; making the risk→depth mapping ONE legible rule is the genuine value, and it states the exit criterion's "zero added per-turn cost" micro-skip explicitly) · a new engine skip-flag / gate (rejected — the skip is a JUDGMENT the skill makes, not an engine gate; strategy stays SOFT and the engine never gates on `## Strategy`) · leave it as-is and close the criterion as already-met (rejected — the criterion IS literally satisfied by strategy.md's Skip line, but the depth LADDER is not stated anywhere as a unified rule; legibility is the deliverable, honestly scoped as "make explicit" not "add mechanism")
Must:
<must>
  - M1 strategy.md carries an explicit risk-proportional DEPTH section naming the tiers as ONE ladder: micro/--tiny (skip, drafted-blank) → low-uncertainty multi-task (loop, no advisor) → high-uncertainty (loop + advisor refute)
  - M2 the micro/--tiny skip is stated with its guarantee: **zero added per-turn cost** (drafted-blank is valid; the loop runs nothing)
  - M3 depth SCALES BY RISK/SIZE — the ladder is monotonic (more risk/size → more depth), and it is the SKILL's judgment, never an engine gate; the strategy stays SOFT and security stays HARD-STOP
  - M4 the ladder REUSES the existing signals (the Trigger/Skip micro-vs-multi-task line + the CONVERGE high-uncertainty advisor condition) — it does not invent a new risk threshold or number
  - M5 strategy.md is byte-identical across all three skill trees
</must>
Reject:
<reject>
  - a skip that requires an engine flag/gate to take effect (an engine gate on `## Strategy`) -> "engine_gated_skip"
  - a depth tier that adds per-turn cost to a micro / --tiny milestone -> "micro_cost_added"
</reject>
After:
<after>
  - a reader of strategy.md sees, in one place, how loop depth scales with milestone risk/size; a micro milestone skips at zero cost, a high-uncertainty one gets the full loop + refute
  - no engine change: the skip and the depth are the skill's risk-proportional judgment
Boundary: a milestone is one of THREE risk/size tiers the ladder must name — micro/--tiny · multi-task low-uncertainty · high-uncertainty; the ladder must map each to a depth and never add cost to the first.
<assumptions>
  ⚠ the three tiers already implicit in strategy.md ARE the right granularity — if the human wants a finer risk gradient (e.g. poc vs mvp vs production depth), this ladder is too coarse; mitigated by tying depth to the EXISTING loop-run vs advisor-spawn signals (which already encode the meaningful jumps) rather than inventing new tiers, and noting the ladder is SOFT so a run may go deeper/shallower and record what it did

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
EDIT strategy.md (skill/add/, +2 twins) — add a "How deep? (risk-proportional)"
section that unifies the three EXISTING tiers into one legible ladder:

  ## How deep? (risk-proportional)
  Loop depth scales with the milestone's risk/size — more risk/size, more depth:
  - **micro / --tiny** → skip the loop. Drafted-blank `## Strategy` is valid;
    the loop runs nothing — **zero added per-turn cost**.
  - **multi-task, low-uncertainty** → run DISCUSS→OPTIMIZE→CONVERGE; no advisor.
  - **high-uncertainty** (contested sequencing / self-score won't clear its bar)
    → the full loop PLUS the add-advisor refute at CONVERGE.
  This is the skill's judgment, reusing the Trigger/Skip + CONVERGE signals above
  — never an engine gate on `## Strategy`. The ladder is SOFT: a run may go
  deeper/shallower and records what it did. Security stays HARD-STOP.

Twins (byte-identical): skill/add/strategy.md ×3 trees
NOT changed: no engine, no template, no pin, no new tier/threshold (reuse the
existing micro-vs-multi-task + high-uncertainty signals).
```

Grounding anchors (verified in-context): strategy.md:8 `**Skip:** a micro / --tiny milestone — drafted-blank, run nothing (risk-proportional)` (tier 1, the exit-criterion's micro skip already present) · strategy.md:7 `**Trigger:** several tasks or real uncertainty` (tier boundary) · strategy.md:22-26 CONVERGE `high-uncertainty → spawn add-advisor` / `low-uncertainty/micro → skip the spawn` (tier 2 vs 3, from advisor-strategy-trigger) · strategy.md:35-40 "It stays SOFT" (the SOFT/HARD-STOP frame the ladder inherits).
Target (measurable): strategy.md gains a risk-proportional depth section naming all three tiers as one monotonic ladder · the micro/--tiny tier states "zero added per-turn cost" · the ladder is stated as SKILL judgment not an engine gate + SOFT + security-HARD-STOP · no new threshold/number · 3 skill trees byte-identical · new content-guard red before / green after · full `tooling/` suite green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/skill/add/` `add-method/src/add_method/_bundled/skill/add/` `.claude/skills/add/` `add-method/tooling/test_risk_proportional_skip.py` `./tests/`
Regression floor: the full `tooling/` suite via CI's `unittest discover` — test_tree_parity, the shipped-surface wording-lint (test_autonomy_command.WordingFenceTest), test_strategy_guide, and test_advisor_strategy_trigger must stay green.
Persona (optional): `.add/personas/method-product-owner.md` — the PM lens sizing depth to risk.

Least-sure flag surfaced at freeze: [spec] whether this task adds enough beyond what strategy.md already implies (the exit criterion's micro-skip is LITERALLY present at line 8). Chosen to ship: the three tiers exist but are SCATTERED (Skip line · Trigger line · CONVERGE) and never stated as a unified risk→depth ladder; legibility of the mapping IS the deliverable, honestly scoped as "make explicit," not "add mechanism." Risk if wrong: the section reads as restatement — mitigated by keeping it a tight ladder that POINTS at the existing signals, adding the one net-new frame (monotonic depth-scales-by-risk) rather than re-explaining each tier.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — strategy.md:8 Skip line, :7 Trigger, :22-26 CONVERGE advisor condition, :35-40 SOFT frame all verified in-context
- [x] §1 every Must + every Reject present, each Reject paired with an error code — M1–M5; R:engine_gated_skip, R:micro_cost_added
- [x] §3 Contract shape is concrete (no template placeholder text remains) — the new depth section is written out verbatim
- [x] Lowest-confidence flag surfaced and substantive — [spec] on whether the task adds enough beyond the already-present micro-skip line; reasoned to "legibility of the unified ladder IS the deliverable"
Verified by: self (worker, sensitivity=mechanical/docs — not an AI-frozen security|data|architecture floor) · at: 2026-07-24

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_depth_ladder_names_three_tiers: strategy.md has a risk-proportional depth section naming micro/--tiny + multi-task-low-uncertainty + high-uncertainty as one ladder · covers: M1
  - test_micro_skip_is_zero_cost: the micro/--tiny tier states zero added per-turn cost / drafted-blank / runs nothing · covers: M2, R:micro_cost_added
  - test_depth_is_soft_skill_judgment_not_engine_gate: the section states it is the skill's judgment (not an engine gate on ## Strategy) + SOFT + security HARD-STOP · covers: M3, R:engine_gated_skip
  - test_ladder_reuses_existing_signals: the section ties depth to the existing high-uncertainty / advisor signals, invents no new number · covers: M4
  - test_strategy_twinned: strategy.md byte-identical across all three skill trees · covers: M5
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Kind: method/docs — assertions over SHIPPED GUIDE text. M1–M4 run RED (the unified depth section doesn't exist; the tiers are scattered). To be red-first the checks target a DEDICATED depth section (a heading naming risk/depth), not the scattered lines. M5 (twin parity) is a regression guard; its red-first duty is mutation.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — added a "## How deep? (risk-proportional)" section to strategy.md after "It stays SOFT", unifying the three pre-existing tiers into one monotonic ladder (micro/--tiny skip @ zero cost → multi-task low-uncertainty loop → high-uncertainty loop+advisor), stated as the skill's judgment (never an engine gate), SOFT, security HARD-STOP. Mirrored ×3 skill trees (md5-verified). No engine/template/pin; no new tier or threshold.
Code lives in: the skill trees (method/docs task; the guide IS the artifact; no `src/`)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — guard test_risk_proportional_skip 5/5; regression floor (strategy-guide + advisor guard + tree-parity + wording-lint) 18/18; full `tooling/` discover green (see gate)
- [x] coverage did not decrease — added a guard file, removed none
- [x] no test or contract was altered during build — only the frozen §3-scoped strategy.md twins + the new guard
- [x] the green was EARNED, not gamed — the guard targets a DEDICATED depth section (heading match), so M1–M4 were RED against the scattered pre-existing lines and only GREEN once the unified section shipped — it cannot pass on the old scattered prose; M5 twin-parity is a mutation-red regression guard
- [x] concurrency / timing of the risky operation is safe — N/A (docs-only)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure markdown
- [x] layering & dependencies follow CONVENTIONS.md — no engine change; the ladder is skill judgment, honoring "the engine never gates on ## Strategy"
- [x] a person reviewed and approved the change — gate_mode ai-plan-verify (human authorized the 8/8 build; mechanical/docs); AI-verify record filled + the [spec] redundancy flag surfaced honestly

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) is this pure restatement? — the exit-criterion micro-skip WAS already at strategy.md:8, disclosed in §1/§3; the net-new is the UNIFIED monotonic ladder (no single place stated depth-scales-by-risk), and the guard proves it by requiring a dedicated section the scattered lines don't satisfy. (2) did I sneak in an engine gate? — test_depth_is_soft_skill_judgment_not_engine_gate asserts "skill's judgment"/"never an engine gate" + SOFT + HARD-STOP; R:engine_gated_skip guarded. (3) new threshold invented? — test_ladder_reuses_existing_signals + the no-numeric-% assert; the ladder reuses the existing signals. No cheat.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose an explicit unified ladder section in strategy.md; rejected a new engine skip-flag / gate (rejected — the skip is a JUDGMENT the skill makes, not an engine gate; strategy stays SOFT and the engine never gates on `## Strategy`) · leave it as-is and close the criterion as already-met (rejected — the criterion IS literally satisfied by strategy.md's Skip line, but the depth LADDER is not stated anywhere as a unified rule; legibility is the deliverable, honestly scoped as "make explicit" not "add mechanism")
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — added a "## How deep? (risk-proportional)" section to strategy.md after "It stays SOFT", unifying the three pre-existing tiers into one monotonic ladder (micro/--tiny skip @ zero cost → multi-task low-uncertainty loop → high-uncertainty loop+advisor), stated as the skill's judgment (never an engine gate), SOFT, security HARD-STOP. Mirrored ×3 skill trees (md5-verified). No engine/template/pin; no new tier or threshold.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] strategy.md's risk→depth ladder is coarse (3 tiers); a future task could map it onto the stage gradient (poc/mvp/production) if a finer depth is wanted (evidence: §1 assumptions ⚠).

### Competency deltas
- [ADD · open] when an exit criterion is LITERALLY already met by shipped prose (the micro-skip was at strategy.md:8), the honest task is LEGIBILITY not mechanism — scope it as "make the scattered rule explicit," disclose the redundancy in §1/§3, and prove the delta with a guard that only a UNIFIED artifact satisfies (evidence: guard targets a dedicated depth section the scattered lines fail).
- [SDD · open] a red-first guard for "unify scattered prose" must anchor to a NEW container (a dedicated heading), not the keywords — else it passes on the scattered instances and never goes red (evidence: _depth_section() matches a heading, not the Skip/Trigger lines).
