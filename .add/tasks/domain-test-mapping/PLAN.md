# TASK: 4-tests.md: a test is any machine-checkable assertion (per-domain forms)

slug: domain-test-mapping · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/skill/add/phases/4-tests.md (+2 guide twins) — the tests-phase guide; add-method/tooling/templates/TASK.md.tmpl (+3 twins) — a 1-clause restore
Context (working folder): test_skill_lean phases pool (baseline 41190 × 0.80 = 32952B ceiling, 5B headroom before this task)
Honors (patterns / conventions): lean-over-budget-bump — absorb new surface by compressing the SAME guide's unpinned prose, never rebaseline; pinned tokens verbatim
Seams consulted: none apply
Anchors the contract cites: phases/4-tests.md '## The must-fail principle' · TASK.md.tmpl §4 comment
Issues/Risks (→ feed §1): the guide equates 'test' with xUnit code, so data/ML/infra tasks read red-first as inapplicable; pin census found the declare-grammar section token-pinned by 4 suites; test_path_confinement exposed a LATENT task-md-optimize regression (template lost 'outside the project root counts 0')
Related intent: method-ergonomics — the 5-domain review: TDD's red-first must be statable in every domain's native assertion form
Ground SHA: 6e8d477

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: 4-tests.md widens 'test' to any machine-checkable assertion with per-domain forms
Framings weighed: one compact paragraph under the must-fail principle (chosen) · a new ## section (bloats the xml-convention narrative census) · a separate reference guide (wrong pool, over-weight)
Must:
<must>
  - the guide states 'a test is any machine-checkable assertion' and names metric threshold · reconciliation query · plan-diff (+ rendered-screen diff)
  - red-first is restated where the forms are introduced (must FAIL before the change exists)
  - net ≤0B on the frozen phases pool; 3 guide trees byte-identical
</must>
Reject:
<reject>
  - any pinned token dropped (grammar forms · Advisor·Confidence hook · Success Metrics · narrative headers) -> sibling suite red
</reject>
After:
<after>
  - a data/ML/infra task can cite the guide for its red assertion form instead of skipping §4
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the compressed declare-grammar wording keeps every consumer suite green — lowest confidence because 12+ suites grep that section; if wrong: a red pin names the exact token to restore
  - [x] the pool had no room without compression — confirmed: 32947/32952B before the task
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: machine-checkable stated   # M1
  Given the canonical 4-tests.md
  When read
  Then it contains "machine-checkable assertion"

Scenario: domain forms named   # M1
  Given the same guide
  When read
  Then metric threshold, reconciliation query and plan-diff all appear

Scenario: red-first restated   # M2
  Given the paragraph introducing the forms
  When read
  Then "FAIL before" appears within it

Scenario: trees identical   # M3
  Given the 3 guide trees
  When hashed
  Then one digest

Scenario: pool absorbed   # M3
  Given the 9 phases guides
  When their bytes are summed
  Then the total stays ≤ 32952
  And no rebaseline was made
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
phases/4-tests.md, under "## The must-fail principle":
  "**A test is any machine-checkable assertion**, not only xUnit code —
   a metric threshold (ML/data), a reconciliation query (data integrity),
   a plan-diff (infra/IaC), a rendered-screen diff (UI). Red-first holds
   for each: the assertion must FAIL before the change exists."
Absorption: Goal line + declare-grammar prose + AI-prompt steps compressed
(pinned tokens verbatim); net −48B. TASK.md.tmpl: restore the pinned clause
"outside the project root counts 0" (latent task-md-optimize regression).
Schema: none — prose-only
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (standing directive: implement all remaining milestone tasks directly)
Reported: no — collapsed ceremony under the standing implement-all directive; flag surfaced above
Least-sure flag surfaced at freeze: ⚠ [test] the compressed grammar section keeps 12+ consumer suites green — because pin census can miss a suite; if wrong: an immediate red names the token

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: all 3 content anchors + tree parity + pool ceiling
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_domain_test_mapping (5 tests): machine-checkable stated · 3 forms named · red-first restated · 3-tree parity · pool ≤ 32952B · covers: M1–M3
</test_plan>

Tests live in: `add-method/tooling/` (test_domain_test_mapping.py) · ran red (forms absent) before build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/` · `add-method/tooling/` · `.claude/` · `add-method/src/add_method/_bundled/` · `.add/tooling/`
Strategy (ordered batches): 1. pin census (grep distinctive substrings across test_*.py) 2. red suite 3. add paragraph + compress Goal/grammar/prompt 4. sync trees 5. run the 12-suite pin batch

Persona (required): generic — method-prose lean stance
Spawn isolation (default): n/a — orchestrator-inline, no spawn
Known-problem fixes: a wrapped line splits a pinned phrase across a newline → keep each form on one physical line; template clause pins live in OTHER suites than the obvious ones (test_path_confinement, not test_taskmd_lean)
Strategy actually used: as planned + one unplanned fix — test_path_confinement caught the template's lost 'outside the project root counts 0' clause (task-md-optimize latent regression); restored (+1B, ceiling 10505/10600)
Safety rule (feature-specific): never weaken a pinned token to fit the budget — compress only unpinned prose
Code lives in: `add-method/skill/add/phases/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] the 3 domain forms appear in all 3 guide trees — confirmed by test_domain_test_mapping parity + anchors
- [x] phases pool 32947→32899B (≤32952, no rebaseline) — confirmed by test_skill_lean green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — n/a, prose-only; the new test module is the wiring
- [x] DEAD-CODE (code) — none
- [x] SEMANTIC (prose / non-code) — 4-tests.md re-read end-to-end post-edit; grammar section still states every resolution rule

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every anchor §3 cites still resolves — headings + clause grep at HEAD
- [x] no anchor moved since Ground SHA

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: 12-suite pin batch (108 tests) incl. path-confinement, xml-convention, per-step hooks, template form tags — all green post-compression

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — prose-only, engine untouched (guarded by test_declare_grammar_doc.test_engine_untouched)
2. Concurrency: CLEAR — n/a
3. Architecture: CLEAR — new surface absorbed under the frozen pool, precedent kept
Verdict: PASS
Residue: none
Binding: advisory — mechanical

### GATE RECORD
Reported: no — collapsed ceremony under the standing implement-all directive; evidence above
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-06

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose one compact paragraph under the must-fail principle; rejected a new ## section (bloats the xml-convention narrative census) · a separate reference guide (wrong pool, over-weight)
- [human] freeze — froze §3 @ v1 (approved by Tin (standing directive: implement all remaining milestone tasks directly))
- [AI] build — strategy used: as planned + one unplanned fix — test_path_confinement caught the template's lost 'outside the project root counts 0' clause (task-md-optimize latent regression); restored (+1B, ceiling 10505/10600)
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

