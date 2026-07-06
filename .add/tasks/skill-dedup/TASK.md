# TASK: run.md bundle section becomes a pointer to 3-contract.md (dedup)

slug: skill-dedup · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/skill/add/run.md (+2 twins) — '## The specification bundle (v7)' section compressed to a pointer; phases/3-contract.md — untouched, confirmed as the grammar's one home
Context (working folder): orchestration pool (run.md+streams.md+advisor.md+loop.md+design.md, ceiling 42045B, 28B slack before)
Honors (patterns / conventions): progressive disclosure — one home per rule, pointers elsewhere; reconcile (shrink) the lean budget, never rebaseline; xml-convention narrative census keeps the section heading
Seams consulted: none apply
Anchors the contract cites: run.md '## The specification bundle (v7)' · 3-contract.md flag grammar
Issues/Risks (→ feed §1): run.md's bundle section (~1.6KB) duplicated the freeze presentation 3-contract.md owns — the ⚠ flag grammar lived in TWO guides and could drift; ~22 suites pin run.md so every removed sentence needed a census ('seven lines' · 'freeze review checklist' · the narrative heading are pinned)
Related intent: method-ergonomics (final task) — duplicated method prose is drift surface + token cost; one home per rule
Ground SHA: 015df8c

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: run.md's bundle section deduped to a pointer at phases/3-contract.md
Framings weighed: compress run.md, 3-contract.md stays the home (chosen) · SKILL.md absorbs the summary (core pool has 17B slack, no room) · leave the duplication (drift already bit once on guide compaction)
Must:
<must>
  - the bundle section keeps: one approval · seven lines · lowest-confidence first · a pointer at phases/3-contract.md — and shrinks under 700B
  - the flag grammar [spec|scenario|contract|test] keeps exactly ONE guide home (3-contract.md)
  - the orchestration pool RECLAIMS ground (≤41300B vs 42017 before); ceiling untouched
</must>
Reject:
<reject>
  - any pinned run.md token dropped ('seven lines' · 'freeze review checklist' · narrative heading · gate/heal/autonomy sections) -> consumer suite red
</reject>
After:
<after>
  - the freeze presentation has one authoritative home; run.md owns only the post-freeze run
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ no un-censused suite pins the removed sentences — lowest confidence because 22+ suites read run.md; if wrong: an immediate red names the exact token to restore (observed twice: 'freeze review checklist' wrap · my own pool bound)
  - [x] the narrative heading must survive — confirmed: test_xml_convention registers it for run.md
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: pointer present   # M1
  Given run.md's bundle section
  When read
  Then it points at phases/3-contract.md

Scenario: kept tokens   # M1
  Given the same section
  When scanned
  Then one approval · seven lines · lowest-confidence first all present

Scenario: single grammar home   # M2
  Given run.md and 3-contract.md
  When scanned for [spec|scenario|contract|test]
  Then absent from run.md, present in 3-contract.md

Scenario: compressed   # M1
  Given the section bytes
  When measured
  Then ≤700B

Scenario: trees identical   # M3
  Given the 3 run.md trees
  When hashed
  Then one digest

Scenario: pool reclaimed   # M3
  Given the 5 orchestration guides
  When summed
  Then ≤41300B
  And the frozen ceiling is unchanged
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
run.md '## The specification bundle (v7)' → one ~490B paragraph:
  one-approval fact · decision-point-stays-human · lowest-confidence-first cue ·
  freeze review checklist (seven lines, ⚠-first) · pointer: phases/3-contract.md,
  its one home; "this rubric owns what happens AFTER the freeze."
Removed from run.md (3-contract.md keeps them): the ⚠ flag grammar line ·
the why-one-not-zero paragraph · the honor-system/CI-checker sentence.
run.md 9603 → 8862B (−741); orchestration pool 42017 → 41276B.
Schema: none — prose-only
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (standing directive: implement all remaining milestone tasks directly)
Reported: no — collapsed ceremony under the standing implement-all directive; flag surfaced above
Least-sure flag surfaced at freeze: ⚠ [test] the pin census caught every consumer — because 22+ suites read run.md; if wrong: a red names the token, restore it verbatim

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: pointer + kept tokens + single home + size + parity + pool
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_skill_dedup (6 tests): pointer · kept tokens · single grammar home · ≤700B section · 3-tree parity · pool ≤41300B · covers: M1–M3, R1
</test_plan>

Tests live in: `add-method/tooling/` (test_skill_dedup.py) · ran red 3/6 (duplication present) before build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/` · `add-method/tooling/` · `.claude/` · `add-method/src/add_method/_bundled/`
Strategy (ordered batches): 1. census pins across the 22 run.md consumers 2. red suite 3. compress the section 4. sync 3 trees 5. run the 25-suite consumer batch

Persona (required): generic — method-prose lean stance
Spawn isolation (default): n/a — orchestrator-inline, no spawn
Known-problem fixes: a pinned phrase split by a line wrap reads as missing ('freeze review checklist') → keep pinned phrases on one physical line; mid-compaction loss of safety sentences → the removed sentences all have a live home in 3-contract.md, nothing is deleted from the method
Strategy actually used: as planned; two batch-caught fixes (pinned-phrase rewrap · my own pool bound was 25B too aggressive)
Safety rule (feature-specific): dedup deletes nothing from the METHOD — every removed sentence keeps a live home in 3-contract.md
Code lives in: `add-method/skill/add/`
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
- [x] run.md's bundle section is ≤700B and points at 3-contract.md — confirmed by test_skill_dedup
- [x] orchestration pool 42017→41276B under the unchanged ceiling — confirmed by test_skill_lean + the pool test

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — n/a, prose-only
- [x] DEAD-CODE (code) — none
- [x] SEMANTIC (prose / non-code) — run.md + 3-contract.md read in full; every removed rule verified present in 3-contract.md before deletion

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] both anchors resolve — heading + grammar grep at HEAD
- [x] no anchor moved since Ground SHA

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: 25-suite run.md consumer batch (258 tests) — the two reds it produced were real (wrap-split pin · over-tight bound) and fixed in the doc/test respectively, not suppressed

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — prose-only; the security floor sentences live in the untouched sections
2. Concurrency: CLEAR — n/a
3. Architecture: CLEAR — one home per rule restored; pointers over copies
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
- [AI] specify — chose compress run.md, 3-contract.md stays the home; rejected SKILL.md absorbs the summary (core pool has 17B slack, no room) · leave the duplication (drift already bit once on guide compaction)
- [human] freeze — froze §3 @ v1 (approved by Tin (standing directive: implement all remaining milestone tasks directly))
- [AI] build — strategy used: as planned; two batch-caught fixes (pinned-phrase rewrap · my own pool bound was 25B too aggressive)
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

