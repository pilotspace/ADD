# TASK: batched intake + batched freeze presentation (one report, one confirm)

slug: intake-freeze-batch · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/skill/add/intake.md (+2 twins) — 'Batched intake' paragraph; add-method/skill/add/report-template.md (+2 twins) — 'Batch, don't serialize' hard rule; test_report_shape_scan_audit.py — recorded-additions ledger migrated forward
Context (working folder): core pool (SKILL.md+intake.md, ceiling 18186B) · reference pool (14 guides, ceiling 51885B) — 53B/39B slack before the task
Honors (patterns / conventions): lean-over-budget-bump (absorb via same-guide compression); byte-ledger migrates forward like a release-test version bump (the test's own docstring); ubiquitous language — no 'least-sure' slang on the guide surface
Seams consulted: none apply
Anchors the contract cites: intake.md '## The four buckets' · report-template.md '## Hard rules' <constraints>
Issues/Risks (→ feed §1): a directive creating N tasks forces N sequential intake+freeze ceremonies today (this very session's pain); report-template.md carries an EXACT byte pin (9588) with a recorded-additions ledger; 'least-sure' is banned slang on the extended surface
Related intent: method-ergonomics — one human decision should cover one batch of same-gate items; collapse ceremony, never the floor
Ground SHA: 69dd68e

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: batched intake + batched same-gate presentation — one report, one confirm, per-item holdback
Framings weighed: presentation-only prose in intake.md + report-template.md (chosen) · an engine batch-freeze verb (policy change, needs its own contract) · a new reference guide (over-weight)
Must:
<must>
  - intake.md: N same-bucket items arriving together classify as ONE proposal — one report, one human confirm covering the batch, never N sequential asks
  - report-template.md hard rule: N same-gate decisions ready together render as ONE report; each item keeps its own lowest-confidence flag; any item can be held back by name
  - presentation only: no gate added or removed; the floor (frozen §3 · red test · recorded gate) is untouched
</must>
Reject:
<reject>
  - mixed-bucket batch -> stays "split_required" (never batch-merged)
</reject>
After:
<after>
  - a drafted milestone's task list can be intaken and its ready contracts frozen with one decision each, itemized
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ a batched confirm stays as informed as N sequential ones — lowest confidence because one ask covers more surface; if wrong: the per-item flags + hold-back-by-name line is the mitigation, and any item can still be pulled out
  - [x] both pools can absorb the additions — confirmed: core 18169/18186, reference 51878→pin-ledger path for the exact-byte guard
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: batched intake documented   # M1
  Given intake.md
  When read
  Then "Batched intake" states ONE proposal + never N sequential asks

Scenario: mixed buckets excluded   # R1
  Given the Batched intake paragraph
  When read
  Then split_required is named as the mixed-bucket route
  And the four-bucket table is unchanged

Scenario: batch rule in the template   # M2
  Given report-template.md's hard rules
  When read
  Then "Batch, don't serialize" appears with hold-back-by-name and per-item flags

Scenario: trees identical   # M3
  Given the 3 trees of each guide
  When hashed
  Then one digest each

Scenario: pools absorbed   # M3
  Given the core and reference pools
  When summed
  Then both stay ≤ their frozen ceilings
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
intake.md (+89B gross, −142B reclaim = −53B net after round 2):
  "**Batched intake.** N same-bucket items arriving together … classify as
   ONE proposal: one report listing every item, one human confirm covering
   the batch — never N sequential asks. Mixed buckets stay `split_required`."
report-template.md (+39B net, ledger-recorded):
  "- **Batch, don't serialize.** N same-gate decisions ready together …
   render as ONE report: PLAN lists each item with its own lowest-confidence
   flag; APPROVE covers the batch in one ask, and any item can be held back
   by name."
test_report_shape_scan_audit byte ledger: 9588 → 9627 (+39 @ this task).
Schema: none — prose-only
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (standing directive: implement all remaining milestone tasks directly)
Reported: no — collapsed ceremony under the standing implement-all directive; flag surfaced above
Least-sure flag surfaced at freeze: ⚠ [spec] a batched confirm stays as informed as N sequential ones — because one ask covers more surface; if wrong: per-item flags + hold-back-by-name mitigate, presentation-only so no gate weakens

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: both guide anchors + bucket exclusion + tree parity + both pool ceilings
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_intake_freeze_batch (6 tests): batched-intake anchors · split_required exclusion · batch rule + hold-back + per-item flag · tree parity ×2 · pools absorbed · covers: M1–M3, R1
</test_plan>

Tests live in: `add-method/tooling/` (test_intake_freeze_batch.py) · ran red (anchors absent) before build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/` · `add-method/tooling/` · `.claude/` · `add-method/src/add_method/_bundled/`
Strategy (ordered batches): 1. pin census (14 consumer suites) 2. red suite 3. add + compress both guides 4. sync trees 5. run the consumer batch

Persona (required): generic — method-prose lean stance
Spawn isolation (default): n/a — orchestrator-inline, no spawn
Known-problem fixes: exact byte pin on report-template.md → migrate the ledger forward with an annotation (the test's documented convention), never weaken it; banned-slang census → 'lowest-confidence' not 'least-sure'
Strategy actually used: as planned + two round-2 fixes the batch caught: the byte-ledger migration (9588→9627, annotated) and the least-sure→lowest-confidence slang swap
Safety rule (feature-specific): batching is presentation only — it must never merge or lower a gate, and any item is holdable by name
Code lives in: `add-method/skill/add/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build (the byte-ledger literal migrated forward per its own documented convention — a recorded addition, not a weakening)
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] both guides carry the batch anchors in all 3 trees — confirmed by test_intake_freeze_batch parity + anchors
- [x] core 18169/18186B · reference ledger-recorded at 9627 — confirmed by test_skill_lean + test_report_shape_scan_audit green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — n/a, prose-only
- [x] DEAD-CODE (code) — none
- [x] SEMANTIC (prose / non-code) — both guides re-read end-to-end post-compression; every pinned rule still stated

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every anchor §3 cites still resolves — heading grep at HEAD
- [x] no anchor moved since Ground SHA

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: 14-suite consumer batch (113 tests) incl. the exact-byte guard, slang census, intake rubric table parser — green only after honest ledger migration + slang fix

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — prose-only; the security floor and HARD-STOP semantics untouched
2. Concurrency: CLEAR — n/a
3. Architecture: CLEAR — presentation layer only; the engine's gate policy unreferenced
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
- [AI] specify — chose presentation-only prose in intake.md + report-template.md; rejected an engine batch-freeze verb (policy change, needs its own contract) · a new reference guide (over-weight)
- [human] freeze — froze §3 @ v1 (approved by Tin (standing directive: implement all remaining milestone tasks directly))
- [AI] build — strategy used: as planned + two round-2 fixes the batch caught: the byte-ledger migration (9588→9627, annotated) and the least-sure→lowest-confidence slang swap
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

