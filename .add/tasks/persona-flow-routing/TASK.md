# TASK: Route dynamic teacher-grade personas to their agent surfaces via flow:

slug: persona-flow-routing · created: 2026-07-06 · stage: mvp
milestone: dynamic-personas
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/agents/add-{persona,design,build,verify,advisor}.md ×2 trees (+ .claude/agents/ — agents are NOT a bundled tree) · add-method/skill/add/design.md + advisor.md ×3 skill trees · .add/personas/*.md (6 dogfood files, frontmatter only) · add-method/tooling/test_persona_flow_routing.py (new)
Context (working folder): templates/personas/_template.md.tmpl (the schema source of truth — flow: RECOMMENDED, distillation discipline #5 'NAME the flow') · docs/18-personas.md 'Apply — three surfaces' (design · advisor/streams · build)
Honors (patterns / conventions): lean-over-budget-bump (orchestration pool 41270/42045, 775B slack — additions absorbed) · two-tree agent parity (test_worker_contract_sync) · advisor.md byte-identical ×3 (test_advisor_persona_select) · persona NEVER lowers a gate
Seams consulted: none apply (no engine change — prose/agents/personas only)
Anchors the contract cites: add-persona.md '## What you own' schema bullet + '## Return' verdict shape · the 'Become the persona' stanza in each of the 4 other agents · design.md 'Persona evidence checklist' para · advisor.md `<persona>` block · `flow:` frontmatter key (template-defined)
Issues/Risks (→ feed §1): the 1.16.1 flow:/Abilities schema has zero consumers — add-persona drafts the STALE schema (no flow:/Abilities/source: in its drafting bullet), all selection surfaces match by archetype prose, dogfood personas 0/6 carry flow: — dynamically drafted personas can't be routed to the surface that needs them. Traps: test_streams pins </persona> before <strategy> ordering · orchestration pool slack only 775B · '## Abilities' pinned by test_persona_setup + test_release_1_16_1 (keep, don't move)
Related intent: Tin 2026-07-06 — 'correct ADD flow with personas and design.md flow' · 'personas for agents team' · 'we offer dynamic personas but high performance as personas_teacher' — dynamic per-domain personas whose quality floor is the vendored teacher library, routed by flow: to design/build/advisor surfaces
Ground SHA: 60a81a3

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: persona flow-routing — dynamic teacher-grade personas reach their agent surface
Framings weighed: route-by-flow:-frontmatter (chosen — schema already defines it; consumers just read it) · engine-enforced flow: validation (rejected — schema keeps flow: RECOMMENDED, presence-based) · per-agent persona allowlists (rejected — duplicates routing in 5 places, drifts)
Must:
<must>
  - M1: add-persona (both agent trees) drafts to the CURRENT schema — its drafting bullet names `flow:` + `source:` frontmatter and the `## Abilities` section, teacher-distilled — and its Return verdict carries `flow`
  - M2: each of the 4 other roster agents (both trees) selects flow:-first in 'Become the persona' — add-design→`flow: design` · add-build→`flow: build` · add-verify/add-advisor→`flow: advisor` — archetype stance as tie-break
  - M3: design.md (×3 skill trees) persona evidence checklist selects personas by `flow: design` (description match as legacy fallback)
  - M4: advisor.md (×3 skill trees) `<persona>` block prefers a flow-matched persona
  - M5: all 6 dogfood personas under .add/personas/ carry a `flow:` frontmatter line
</must>
Reject:
<reject>
  - R1: any wording that lets a persona lower/skip a gate -> "persona_gate_creep" (personas stay advisory; the no-match generic fallback never blocks — existing sentences preserved)
  - R2: growing the orchestration pool past its frozen ceiling -> "pool_budget_bust" (absorb via same-guide compression)
  - R3: agent trees or skill trees drifting apart -> "tree_drift" (two-tree agent parity + three-tree skill parity held)
</reject>
After:
<after>
  - a persona drafted dynamically by add-persona is born with flow: routing and teacher provenance, and every consuming surface picks it up by flow: — the 1.16.1 schema is live wiring, not dead
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ mapping verify→`flow: advisor` (not a 4th flow value) is right — lowest confidence because 18-personas.md's three surfaces fold the verify refute-read under advisor/streams delegation; if wrong: a schema change request adds a `verify` flow value later (cheap, additive)
  - [x] the 775B orchestration-pool slack absorbs the design.md+advisor.md edits — confirmed by measuring before commit
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: dynamic draft is born routable   # M1
  Given a domain no seeded persona covers
  When add-persona drafts a new persona from the teacher library
  Then the draft carries flow: + source: frontmatter and ## Abilities, and the Return verdict names its flow

Scenario: roster agents pick by flow   # M2
  Given seeded personas carrying flow: values
  When add-design/add-build/add-verify/add-advisor load 'Become the persona'
  Then each names its own flow: value as the first selection key (archetype = tie-break)

Scenario: design checklist routes by flow   # M3
  Given a UI feature at design-confirm
  When design.md builds the persona evidence checklist
  Then it selects flow: design personas (description match only as legacy fallback)

Scenario: advisor spawn prefers flow match   # M4
  Given the orchestrator delegates a piece via advisor.md
  When the <persona> block selects a project persona
  Then it prefers a flow-matched one, and </persona> still precedes <strategy>

Scenario: dogfood roster is routable   # M5
  Given the 6 seeded .add/personas files
  When their frontmatter is read
  Then each carries a flow: line restricted to design|build|advisor values

Scenario: no gate creep   # R1
  Given all edited surfaces
  When a persona matches or fails to match
  Then gates are unchanged and the generic fallback never blocks
  And every never-blocks/advisory sentence survives

Scenario: budgets and parity hold   # R2+R3
  Given the frozen orchestration pool ceiling and the twin trees
  When the edits land
  Then the pool measures ≤ ceiling
  And agents ×2 and skill guides ×3 stay byte-identical
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE CONTRACT (no engine change):
  add-persona.md (×2 trees): drafting schema bullet names flow:/source: frontmatter + ## Abilities,
    distilled from .add/personas-teacher/; Return verdict shape gains `flow`:
    { phase: persona, slug, drafted, flow, rationale, confidence, open_questions }
  add-{design,build,verify,advisor}.md (×2 trees): 'Become the persona' selects flow:-first —
    design→flow: design · build→flow: build · verify/advisor→flow: advisor; archetype = tie-break;
    generic no-match fallback sentence preserved verbatim-in-spirit (never blocks)
  design.md (×3 trees): checklist keys on `flow: design` personas; description match = legacy fallback
  advisor.md (×3 trees): <persona> block says flow-matched first; </persona> stays before <strategy>
  .add/personas/*.md ×6: + one `flow:` frontmatter line each (routing only, no body change)
  guard: test_persona_flow_routing.py — errors surface as failing assertions:
    "persona_gate_creep" | "pool_budget_bust" | "tree_drift"
Schema: none (no state.json / engine surface touched)
```

Glossary deltas: none (flow: and the three apply-surfaces are already defined in 18-personas.md + the persona template)
Status: FROZEN @ v1 — approved by Tin (standing 2026-07-06 directive: investigate then CORRECT the persona/design.md flow — collapsed ceremony)
Reported: yes — investigation findings + correction shape reported in-chat before this froze (dead-wiring census: 0 writers, 0 readers of flow:)
Least-sure flag surfaced at freeze: [spec] mapping verify to `flow: advisor` instead of a 4th flow value — 18-personas.md folds the verify refute-read under the advisor/streams surface, but if verify deserves its own routing value a later additive change request adds it cheaply

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: one assertion per Must + per Reject (prose task — guard suite)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_add_persona_drafts_current_schema: add-persona names flow:/source:/## Abilities in its drafting bullet · covers: M1
  - test_add_persona_returns_flow: Return verdict shape carries `flow` · covers: M1
  - test_roster_agents_select_flow_first: each of the 4 agents names its flow: value in 'Become the persona' · covers: M2
  - test_design_checklist_routes_by_flow: design.md keys the checklist on `flow: design` · covers: M3
  - test_advisor_persona_block_prefers_flow: advisor.md <persona> block names flow; </persona> still precedes <strategy> · covers: M4
  - test_dogfood_personas_carry_flow: all 6 .add/personas files have a flow: frontmatter line with only known values · covers: M5
  - test_generic_fallback_never_blocks: every selection surface keeps its never-blocks fallback · covers: R:persona_gate_creep
  - test_pool_budget_absorbed: orchestration pool ≤ frozen ceiling · covers: R:pool_budget_bust
  - test_trees_stay_in_parity: agents ×2 + design.md/advisor.md ×3 byte-identical · covers: R:tree_drift
</test_plan>

Tests live in: `add-method/tooling/` (test_persona_flow_routing.py) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/agents/` `add-method/skill/add/` `add-method/src/add_method/_bundled/` `add-method/tooling/` `add-method/../.claude/` `add-method/../.add/personas/`
Strategy (ordered batches): 1. red guard suite 2. add-persona.md (schema + Return, canonical tree) 3. the 4 agents' flow:-first lines 4. design.md checklist + advisor.md <persona> block (measure pool) 5. dogfood flow: lines 6. sync twins (agents ×2, skill ×3) 7. green + sibling suites. Domain stance: routing metadata, not new prose — smallest wording delta that names the flow: key.

Persona (required): method-product-owner — the surface being corrected is the method's own agent-routing ergonomics
Spawn isolation (default): n/a — direct build in the main tree (sequential, no spawn), per Tin's standing directive
Known-problem fixes: pool bust → compress same-guide prose in design.md/advisor.md · test_streams ordering → keep </persona> before <strategy> · worker-contract sync → edit both agent trees identically · pinned '## Abilities'/'.add/personas/' strings → never remove
Strategy actually used: as planned, plus two discoveries — (a) the guard test's ordering assertion had to key on line-start tags (advisor.md line 28 MENTIONS `<strategy>` in prose; test bug fixed, tests→build re-crossed); (b) agents ship in THREE trees now (canonical · .claude/ · _bundled/agents/ per test_roster_shipped) — all three synced
Safety rule (feature-specific): a persona never lowers a gate — every edited surface must retain its advisory/never-blocks sentence; security stays HARD-STOP everywhere
Code lives in: add-method/agents/ + skill trees + .add/personas/ (prose) · add-method/tooling/ (guard test)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease (new 10-test guard suite added; 196 persona/agent-suite tests green)
- [x] no test or contract was altered during build (one test-bug fix re-crossed tests→build per the tripwire convention, not a weakening — the assertion now checks the same ordering more precisely)
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe (prose-only; no engine/runtime change)
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md (twin-tree parity held ×3 agents, ×3 skills)
- [x] a person reviewed and approved the change — Tin's standing 2026-07-06 correction directive; diff summarized in-chat

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] grep `flow:` across .add/personas/ returns 6/6 files — confirmed by test_dogfood_personas_carry_flow + add.py check (6× schema-conformant)
- [x] every selection surface (5 agents ×3 trees · design.md · advisor.md ×3 trees) names its flow: key — confirmed by the guard suite's 10 assertions green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — n/a (no code symbol added; guard test discovered via unittest discover)
- [x] DEAD-CODE (code) — none (prose + one test module)
- [x] SEMANTIC (prose / non-code) — read in full: all 5 edited agent stanzas + design.md checklist para + advisor.md <persona> block · confirmed every advisory/never-blocks sentence survives and no gate wording changed

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves — confirmed by the green guard suite reading those exact stanzas
- [x] one anchor set WIDENED since ground: agents are a 3-tree surface (bundled agents dir), not 2 — named in Strategy-actually-used and synced

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: mutation-probed the ordering assertion (prose-mention false positive found and fixed — the failure was REAL before the fix); confirmed the 7 red-first failures each named the missing wiring, not a fixture artifact; test_generic_fallback_never_blocks would go red if any never-blocks sentence were dropped (verified by the pre-edit red run)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — no gate/trust wording touched; security HARD-STOP sentences intact on every edited surface
2. Concurrency: CLEAR — prose-only change
3. Architecture: CLEAR — routing reads the schema field the template already defines; no new mechanism
Verdict: PASS
Residue: none
Binding: yes — mechanical

### GATE RECORD
Reported: yes — evidence summary rendered in-chat before recording
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin (standing correction directive) · date: 2026-07-06

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): next add-persona spawn should return `flow` in its verdict; next design-confirm should key its checklist on flow: design

### Decisions (ADR)
- [AI] specify — chose route-by-flow:-frontmatter; rejected engine-enforced flow: validation (rejected — schema keeps flow: RECOMMENDED, presence-based) · per-agent persona allowlists (rejected — duplicates routing in 5 places, drifts)
- [human] freeze — froze §3 @ v1 (approved by Tin (standing 2026-07-06 directive: investigate then CORRECT the persona/design.md flow — collapsed ceremony))
- [AI] build — strategy used: as planned, plus two discoveries — (a) the guard test's ordering assertion had to key on line-start tags (advisor.md line 28 MENTIONS `<strategy>` in prose; test bug fixed, tests→build re-crossed); (b) agents ship in THREE trees now (canonical · .claude/ · _bundled/agents/ per test_roster_shipped) — all three synced
- [AI] verify — gate PASS (reviewed by Tin (standing correction directive))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
  - [SPEC · seeded] weigh a dedicated `verify` flow value vs folding verify under advisor — the §1 ⚠ flag, revisit after the roster runs with flow: routing (evidence: TASK §1 assumptions) [→ verify-flow-value]
  - [SPEC · seeded] the streams.md worker-contract `<persona>` block could also name flow: preference — deferred to keep the pin-locked `<strategy>` floor untouched (evidence: test_streams byte pins) [→ streams-persona-flow]

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

  - [ADD · folded] a schema field shipped without a consumer is dead wiring — land writer+reader in the SAME task, or the field rots unnoticed for a release (evidence: flow: shipped 1.16.1, first consumer 2026-07-06) [folded foundation-version 65]
  - [TDD · folded] a text-index ordering assertion must key on line-start tags when the guide also MENTIONS the tag in prose (evidence: test_persona_still_precedes_strategy false red) [folded foundation-version 65]
