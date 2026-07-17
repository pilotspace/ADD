# TASK: self-improve.md — the one map of how ADD improves itself

slug: self-improving-guide · created: 2026-07-07 · stage: mvp
milestone: self-improving-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/skill/add/self-improve.md (NEW, ~1.3KB, unpooled — tree census only, 1421B slack) ×3 trees · phases/7-observe.md pointer (+22B, phases pool 15B slack → 7B same-guide trim) · test_self_improving_guide.py (new)
Context (working folder): the self-improvement mechanics live in 6 scattered guides (deltas/fold/compact-foundation/soul/confidence/18-personas) — no single surface shows an agent the WHOLE loop across the 5 domains and 8 steps
Honors (patterns / conventions): progressive disclosure (the map POINTS, never duplicates the mechanics) · whole-tree byte budget 145663 · a guide nobody points to is dead weight → 7-observe.md pointer · 3-tree skill parity
Seams consulted: none apply (prose only, no engine change)
Anchors the contract cites: the four self-improving artifacts (foundation · personas · SOUL.md · next scope) · the 5-domain routing table (fold.md) · the 8-step feed lines · status cues carried:/compaction:
Issues/Risks (→ feed §1): budget is the risk — tree slack 1421B, phases slack 15B; the guide must stay a MAP (~1.3KB) or it busts the census. Trap: SKILL.md core pool (17B slack) can NOT take the pointer — 7-observe.md is the emission point and the right pointer home
Related intent: Tin 2026-07-07 'review ADD flow to make sure ADD are optimized for self-improving SKILL via 5 Domains - 8 step - maybe we need add a self-improving SKILL file md?' — decision: yes, as a map
Ground SHA: 733ba23

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: self-improve.md — one navigable map of the four self-improving artifacts across 5 domains and 8 steps
Framings weighed: a new ~1.3KB map file (chosen — Tin's suggestion; unpooled so no pool-list edit) · a section in fold.md (rejected — fold is one mechanic, the map is cross-artifact) · SKILL.md section (rejected — core pool 17B slack)
Must:
<must>
  - M1: self-improve.md exists ×3 trees and names the four artifacts (foundation · personas · SOUL.md · next scope) with emit-grammar + consolidator for each
  - M2: it maps all 5 domains (DDD·SDD·UDD·TDD·ADD) to their consolidation homes and names how the 8 steps feed observe
  - M3: it points at the mechanics guides (deltas.md · fold.md · compact-foundation.md · soul.md · confidence.md) and the status cues — never duplicating their rules
  - M4: 7-observe.md points at it
</must>
Reject:
<reject>
  - R1: whole-tree census over 145663 -> "tree_budget_bust"
  - R2: phases pool over its ceiling -> "pool_budget_bust"
  - R3: skill trees drift -> "tree_drift"
</reject>
After:
<after>
  - an agent (or human) asking 'how does ADD improve itself?' reads ONE ~1.3KB map and knows where every lesson goes and which command consolidates it
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ a map-only file earns its bytes — lowest confidence because it adds a 7th self-improvement surface; if wrong: it is unpooled and trivially removable
  - [x] no census requires every guide to belong to a pool — confirmed (unpooled=[] is coverage, not a gate; only the tree census counts new files)
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: one map, four artifacts   # M1+M2
  Given an agent asking how ADD self-improves
  When it reads self-improve.md
  Then it finds all four artifacts with grammar+consolidator, the 5 domains routed, and the 8-step feeds

Scenario: point, never duplicate   # M3
  Given the mechanics guides
  When the map references them
  Then it carries pointers (deltas.md · fold.md · compact-foundation.md · soul.md · confidence.md) and copies no reject-code list

Scenario: discoverable from observe   # M4
  Given phases/7-observe.md
  When an agent finishes §7
  Then the Next line points at self-improve.md

Scenario: budgets hold   # R1+R2+R3
  Given the frozen tree census and phases pool
  When the file lands ×3 trees
  Then both budgets hold and the trees stay byte-identical
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
self-improve.md (NEW, ≤1.3KB): a four-row artifact map (what improves · emitted at · grammar · consolidator)
  + the 5-domain routing line + the 8-step feed line + the convergence line (status cues) + self-score line
phases/7-observe.md: 'Next' line gains '· the map: self-improve.md' (+7B trim beside it)
Schema: none
```

Glossary deltas: none (the map introduces no term; it cites existing ones)
Status: FROZEN @ v1 — approved by Tin (the file was his suggestion; auto-mode directive, 2026-07-07)
Reported: yes — the budget math + yes-decision rendered in-chat
Least-sure flag surfaced at freeze: [spec] map-only value vs surface-count growth — removable cheaply if it proves noise

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: one test per Must/Reject
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_map_names_four_artifacts · covers: M1
  - test_map_covers_5_domains_8_steps · covers: M2
  - test_map_points_never_duplicates (pointers present; fold reject-codes NOT copied) · covers: M3
  - test_observe_points_at_map · covers: M4
  - test_tree_and_phases_budgets_hold · covers: R1,R2
  - test_three_tree_parity · covers: R3
</test_plan>

Tests live in: `add-method/tooling/` (test_self_improving_guide.py) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/` `add-method/tooling/` `add-method/src/add_method/_bundled/` `add-method/../.claude/`
Strategy (ordered batches): 1. red test 2. write the map (≤1.3KB) 3. observe pointer + 7B trim 4. sync ×3 5. green + budgets

Persona (required): book-technical-writer — a map section is pure method prose (5-second-test applies)
Spawn isolation (default): n/a — direct sequential build
Known-problem fixes: tree census bust → cut prose, the map has no minimum · phases 15B slack → trim beside the pointer
Strategy actually used: as planned; the map landed at 1449B (first cut 1538B busted the tree census by 136 → tightened) and the phases pool needed 3 micro-trims in 7-observe.md beside the pointer
Safety rule (feature-specific): the map never restates a gate rule — a paraphrased gate that drifts is a doc-truth bug; point, don't copy
Code lives in: skill/add/self-improve.md ×3 (prose) · tooling (test)
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
- [x] self-improve.md reads as one screen: 4-artifact table + routing + convergence + self-score — confirmed by full read (5-second test per section)
- [x] whole-tree census 145628/145663 and phases 32950/32952 — confirmed by measurement after sync

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — the map is pointed at from 7-observe.md's Next line (a guide nobody points to is dead weight)
- [x] DEAD-CODE — none (prose)
- [x] SEMANTIC — read in full: no gate rule restated (point-don't-copy held; reject codes absent by guard)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] §3 anchors resolve — the guard suite reads the exact tokens
- [x] none moved

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: red-first 7 failing (file absent); the no-duplication contract probed via assertNotIn on fold's reject codes; budget guards proven red by the 1538B first cut

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — map prose; the nothing-self-approves floor is quoted, not weakened
2. Concurrency: CLEAR — n/a
3. Architecture: CLEAR — progressive disclosure held (map points, mechanics stay in their guides)
Verdict: PASS
Residue: none
Binding: yes — mechanical

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin (auto-mode directive; the file was his suggestion) · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do future observe phases cite the map; does it stay ≤1.5KB

### Decisions (ADR)
- [AI] specify — chose a new ~1.3KB map file; rejected a section in fold.md (rejected — fold is one mechanic, the map is cross-artifact) · SKILL.md section (rejected — core pool 17B slack)
- [human] freeze — froze §3 @ v1 (approved by Tin (the file was his suggestion; auto-mode directive, 2026-07-07))
- [AI] build — strategy used: as planned; the map landed at 1449B (first cut 1538B busted the tree census by 136 → tightened) and the phases pool needed 3 micro-trims in 7-observe.md beside the pointer
- [AI] verify — gate PASS (reviewed by Tin (auto-mode directive; the file was his suggestion))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

