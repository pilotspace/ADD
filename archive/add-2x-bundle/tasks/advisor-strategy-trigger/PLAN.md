# PLAN: add-advisor refutes a high-uncertainty milestone strategy before commit

slug: advisor-strategy-trigger · created: 2026-07-24 · stage: mvp
milestone: strategy-intake
autonomy: auto
gate_mode: ai-plan-verify

phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a spawn-to-refute step in strategy.md's CONVERGE — a high-uncertainty milestone spawns `add-advisor` (refute mode) to try to BREAK its strategy before the plan is recorded/committed; the add-advisor agent's `direction` beat is extended to name the milestone strategy as a refutable artifact alongside the task bundle. Advisory: the advisor breaks, the human still confirms at the gate.
Framings weighed: extend strategy.md's CONVERGE + the add-advisor `direction` beat prose (chosen — the advisor already refutes a task DIRECTION bundle; a milestone strategy is the milestone-level analog of that same artifact, so it reuses the existing refute mode + persona-select, not a new mechanism; strategy.md is where the loop already converges) · a new engine verb / gate on the strategy (rejected — strategy stays SOFT, the engine never spawns; a refute that BLOCKS would convert the soft slot into a covert gate — the Reject) · a standalone advisor-strategy.md guide (rejected — one line in the loop + one in the agent beat is the whole change; a new guide would restate the advisor's existing refute contract)
Must:
<must>
  - M1 strategy.md's CONVERGE spawns `add-advisor` in REFUTE mode for a HIGH-UNCERTAINTY milestone, before the plan is recorded — to break the sequencing / freeze-first choice / wave partition; what survives is folded, then converge
  - M2 the trigger is RISK-PROPORTIONAL — a low-uncertainty / micro / --tiny milestone does NOT spawn the advisor (no forced ceremony); it is offered, never required
  - M3 the refute is ADVISORY — the advisor cannot reach the human and cannot block; it hands back the concrete break (or concedes it holds), the human still confirms the strategy at the persona-owned gate; security stays HARD-STOP
  - M4 the add-advisor agent's `direction` beat names the milestone STRATEGY as a refutable artifact (alongside the task bundle) — reusing the existing refute mode, not a new mode
  - M5 strategy.md (3 skill trees) and add-advisor.md (3 agent trees) are each byte-identical across their trees
</must>
Reject:
<reject>
  - a refute that BLOCKS the milestone (hard-gates commit on the advisor's verdict) -> "refute_blocks_strategy"
  - forcing the advisor spawn on a low-uncertainty / micro milestone -> "forced_advisor_ceremony"
</reject>
After:
<after>
  - a high-uncertainty milestone's strategy is adversarially pressure-tested before the tasks are built; the surviving plan is stronger and the human confirms it
  - a low-risk milestone converges with no advisor spawn and zero added cost
Boundary: a milestone reaches CONVERGE in TWO shapes — high-uncertainty (spawn the refute) and low-uncertainty/micro (skip it); the trigger must never fire on the second.
<assumptions>
  ⚠ "high-uncertainty" is judged by the same signal that already decides whether the strategy loop runs at all (multi-task / real uncertainty vs micro/--tiny) — if a NEW uncertainty threshold is expected, this conflates them; mitigated by expressing the trigger as "when the loop runs AND the self-score won't clear its bar / the sequencing is contested", reusing the existing loop-vs-skip signal rather than a new number
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
EDIT strategy.md (skill/add/, +2 twins) — CONVERGE gains a refute step:

  3. CONVERGE — before recording: if the milestone is HIGH-UNCERTAINTY (the
     sequencing is contested / the self-score won't clear its bar), spawn
     `add-advisor` in REFUTE mode to try to BREAK the strategy — the approach,
     the freeze-first choice, the wave partition. Fold what survives; concede
     what holds. THEN self-score to convergence and record in `## Strategy`.
     Low-uncertainty / micro / --tiny → skip the spawn (no forced ceremony).
  Advisory: the advisor hands back the concrete break; it cannot block. The
  human still confirms the strategy at the persona-owned gate. Security HARD-STOP.

EDIT add-advisor.md (agents/, +2 twins) — the `direction` beat line:
  direction (propose the bundle plan · refute the draft — a task bundle OR a
  high-uncertainty milestone STRATEGY — so the human freezes the stronger shape)

Twins (byte-identical):
  skill/add/strategy.md ×3 trees · agents/add-advisor.md ×3 trees
NOT changed: no engine, no template, no pin, no new advisor MODE (reuse refute).
```

Grounding anchors (verified in-context): strategy.md CONVERGE step (the record point this refute precedes) · add-advisor.md §1 `refute` mode + the "Every mode serves EVERY beat" line naming `direction` as "refute the draft so the human freezes the stronger shape" (the exact line extended) · add-advisor.md §3 "You CANNOT reach the human" (the advisory/no-block floor this task honors) · AGENT_TREES = agents/ ↔ _bundled/agents ↔ .claude/agents (test_tree_parity.py:44).
Target (measurable): strategy.md CONVERGE names the add-advisor refute spawn + the high-uncertainty condition + the skip + the no-block/advisory caveat · add-advisor.md `direction` beat names the milestone strategy as refutable · both files byte-identical across their 3 trees · new content-guard red before / green after · full `tooling/` suite green (incl. tree-parity + wording-lint).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/skill/add/` `add-method/src/add_method/_bundled/skill/add/` `.claude/skills/add/` `add-method/agents/` `add-method/src/add_method/_bundled/agents/` `.claude/agents/` `add-method/tooling/test_advisor_strategy_trigger.py` `./tests/`
Regression floor: the full `tooling/` suite via CI's `unittest discover` — test_tree_parity (skill + agent trees), the shipped-surface wording-lint (test_autonomy_command.WordingFenceTest), and test_strategy_guide must stay green.
Persona (optional): `.add/personas/method-product-owner.md` — the PM lens; the refute pressure-tests the PM plan.

Least-sure flag surfaced at freeze: [spec] whether the refute trigger belongs IN strategy.md's CONVERGE step vs. as a separate advisor-spawn note. Chosen IN CONVERGE: the advisor breaks the plan at the moment it would otherwise be recorded — that IS the CONVERGE boundary; a separate note would divorce the trigger from the point it guards. The whole change is two prose lines (loop + agent beat), so a tighter container isn't available.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — strategy.md CONVERGE step, add-advisor.md §1 refute mode + the "Every mode serves EVERY beat" direction line, §3 "cannot reach the human", AGENT_TREES (test_tree_parity.py:44) all verified in-context
- [x] §1 every Must + every Reject present, each Reject paired with an error code — M1–M5; R:refute_blocks_strategy, R:forced_advisor_ceremony
- [x] §3 Contract shape is concrete (no template placeholder text remains) — the two prose edits are written out verbatim, no `<...>` placeholders
- [x] Lowest-confidence flag surfaced and substantive — [spec] on the refute-trigger's container (in-CONVERGE vs separate note), reasoned to a choice
Verified by: self (worker, sensitivity=mechanical/docs — not an AI-frozen security|data|architecture floor) · at: 2026-07-24

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_converge_spawns_advisor_refute: strategy.md CONVERGE names spawning add-advisor in refute mode for a high-uncertainty milestone before recording · covers: M1
  - test_trigger_is_risk_proportional: strategy.md states the low-uncertainty / micro / --tiny milestone SKIPS the spawn (offered, not required) · covers: M2, R:forced_advisor_ceremony
  - test_refute_is_advisory_never_blocks: strategy.md states the refute cannot block / the human still confirms + security HARD-STOP · covers: M3, R:refute_blocks_strategy
  - test_advisor_direction_beat_names_strategy: add-advisor.md's direction beat names the milestone strategy as a refutable artifact (reusing refute mode, no new mode) · covers: M4
  - test_strategy_and_advisor_twinned: strategy.md (3 skill trees) + add-advisor.md (3 agent trees) each byte-identical · covers: M5
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Kind: method/docs — assertions over SHIPPED GUIDE + AGENT text. M1–M4 run RED (the refute step / beat extension don't exist yet). M5 (twin parity) is a regression guard; its red-first duty is mutation (drop a twin → red).

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — two prose edits. (1) strategy.md CONVERGE gained a refute step: high-uncertainty → spawn add-advisor in refute mode to break the plan before recording, fold survivors; low-uncertainty/micro/--tiny skips; the refute is advisory ("cannot block"), the human still confirms, security HARD-STOP. (2) add-advisor.md `direction` beat now names "a task bundle OR a high-uncertainty milestone strategy" as the refutable artifact — reusing the existing refute mode, no new mode. Mirrored strategy.md ×3 skill trees + add-advisor.md ×3 agent trees (md5-verified). No engine/template/pin.
Code lives in: the skill + agent trees (method/docs task — the guides ARE the artifact; no `src/`)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — guard test_advisor_strategy_trigger 5/5; regression floor test_strategy_guide + test_tree_parity + wording-lint green (13/13); full `tooling/` discover green (see gate)
- [x] coverage did not decrease — added a guard file, removed none
- [x] no test or contract was altered during build — only the frozen §3-scoped skill/agent files + the new guard were written
- [x] the green was EARNED, not gamed — M1/M3/M4 proven RED before the edits (M3 tightened to scope the no-block statement to the refute context so it couldn't pass on the pre-existing SOFT prose); GREEN after; M5 twin-parity is a mutation-red regression guard
- [x] concurrency / timing of the risky operation is safe — N/A (docs-only)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure markdown
- [x] layering & dependencies follow CONVENTIONS.md — reuses the advisor's existing refute mode + persona-select; no new mode, no engine spawn (the engine never spawns)
- [x] a person reviewed and approved the change — gate_mode: ai-plan-verify (human authorized building the milestone to 8/8; mechanical/docs sensitivity, not a security|data|architecture floor); AI-verify record filled

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) does the refute re-introduce a gate? — test_refute_is_advisory_never_blocks asserts "cannot block" IN the refute context + human-confirms + HARD-STOP; the Reject refute_blocks_strategy is guarded. (2) is M2/M3 vacuous? — M2 legitimately reuses strategy-guide's shipped skip rule (a regression guard for it under the new spawn); M3 was tightened mid-build to scope to the refute context (caught it passing on pre-existing prose). (3) new advisor mode smuggled in? — the beat reuses `refute`; test_advisor_direction_beat_names_strategy asserts "refute" in the beat. No cheat.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose extend strategy.md's CONVERGE + the add-advisor `direction` beat prose; rejected a new engine verb / gate on the strategy (rejected — strategy stays SOFT, the engine never spawns; a refute that BLOCKS would convert the soft slot into a covert gate — the Reject) · a standalone advisor-strategy.md guide (rejected — one line in the loop + one in the agent beat is the whole change; a new guide would restate the advisor's existing refute contract)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — two prose edits. (1) strategy.md CONVERGE gained a refute step: high-uncertainty → spawn add-advisor in refute mode to break the plan before recording, fold survivors; low-uncertainty/micro/--tiny skips; the refute is advisory ("cannot block"), the human still confirms, security HARD-STOP. (2) add-advisor.md `direction` beat now names "a task bundle OR a high-uncertainty milestone strategy" as the refutable artifact — reusing the existing refute mode, no new mode. Mirrored strategy.md ×3 skill trees + add-advisor.md ×3 agent trees (md5-verified). No engine/template/pin.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] the milestone strategy is now a first-class refutable artifact for add-advisor's `direction` beat — a future task could let the advisor's refute of a strategy feed the persona-owned gate report's FLAGS automatically (evidence: add-advisor.md direction beat + strategy.md CONVERGE).

### Competency deltas
- [ADD · open] a content-guard assert that passes against PRE-EXISTING prose isn't red-first — M3 ("refute cannot block") first matched strategy.md's own SOFT "never blocked on a confidence bar"; scoping the assert to the refute context (from the `add-advisor`/`refute` marker onward) made it genuinely red before / green after (evidence: guard went 2-red → 3-red after the tighten).
- [TDD · open] when a NEW feature restates a caveat the surface already carries (advisory/SOFT/HARD-STOP), the guard must anchor the caveat to the NEW construct's context, not the whole file — else the regression guard and the feature guard collide into a vacuous green (evidence: same M3 tighten).
