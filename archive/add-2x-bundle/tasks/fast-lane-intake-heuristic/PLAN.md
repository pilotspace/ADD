# TASK: Intake proposes --fast for small/mechanical tasks (human still confirms)

slug: fast-lane-intake-heuristic · created: 2026-07-07 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/skill/add/intake.md "The four buckets" table + the task-bucket row (the command an intake proposal emits) — 3 skill trees; new guard test test_fast_lane_heuristic.py
Context (working folder): add-lean-loop task 4 — full-bundle ceremony on CRUD-sized tasks drove the 41–55% pre-code share; the fast lane already exists (freeze-gated, floor held) but nothing routes small tasks toward it — the human must remember the flag
Honors (patterns / conventions): fast is HUMAN-OWNED, never auto-picked — a PROPOSAL in the intake menu keeps that floor (the human confirms the command) · intake.md is in the core lean pool (compress-to-absorb) · 3-tree skill parity
Seams consulted: none
Anchors the contract cites: intake.md four-buckets table · the { bucket, rationale, command } proposal shape
Issues/Risks (→ feed §1): SKILL.md flag-mode line says "never auto-picked" — the heuristic wording must visibly preserve that; pool bytes bind (+N needs -N)
Related intent: add-lean-loop MILESTONE.md task 4
Ground SHA: 980a483

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: fast-lane intake heuristic — propose, never pick
Framings weighed: intake-guide heuristic (chosen — the sizing moment is where the flag decision belongs) · engine auto-flag (rejected: violates the human-owned-flag floor) · status hint (rejected: too late, task already created)
Must:
<must>
  - intake.md's task bucket gains a fast-fit test: single behavior · no new contract surface consumed by others · sensitivity mechanical → the proposal's command becomes `add.py new-task <slug> --fast` with the rationale naming why it fast-fits.
  - The heuristic text states the flag stays human-owned: the proposal CARRIES --fast; only the human's confirm picks it.
  - Core lean pool absorbs the addition (compress-to-absorb inside intake.md/SKILL.md; no rebaseline).
</must>
Reject:
<reject>
  - none engine-enforced — guide truth; a doc-pinning guard going red is fixed forward
</reject>
After:
<after>
  - small/mechanical requests arrive at the human's confirm ALREADY routed to the fast lane; declining costs one word
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the 3-condition fast-fit test is sharp enough to avoid routing risky work fast — lowest confidence because "single behavior" is judgment; if wrong: the freeze gate + sensitivity floor still hold (fast collapses ceremony, never the floor); cost = one human decline
  - [ ] pool headroom from task 3 (-290B) covers this addition — measured at build
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: intake teaches the fast-fit test   # M1
  Given the shipped intake.md
  Then it names the 3 fast-fit conditions (single behavior · no consumed contract surface · mechanical)
  And the task-bucket proposal command shows `new-task <slug> --fast` for a fast-fit

Scenario: flag stays human-owned   # M2
  Given the same text
  Then it states the proposal carries --fast and the human's confirm is what picks it

Scenario: pool fence holds   # M3
  When test_skill_lean runs
  Then the core pool + whole-tree budgets stay green
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
intake.md (after the four-buckets table):
  "**Fast-fit test (task bucket only).** single behavior · no new contract surface another
   task consumes · sensitivity mechanical → propose `add.py new-task <slug> --fast` and say
   why it fast-fits. The flag stays human-owned: the proposal carries it; the human's
   confirm picks it. Any doubt on any condition → propose the full lane."
3 skill trees byte-identical; core pool + whole-tree lean fences green (compress-to-absorb).
Schema: guide text only; no engine change.
```

Glossary deltas: none
`Least-sure flag surfaced at freeze:` [spec] "no new contract surface another task consumes" as the sharpest of the 3 conditions — if too subtle for agents, fast routes too much; cost: human declines, or a later delta sharpens the wording.
Status: FROZEN @ v1 — approved by Tin Dang (milestone plan confirmed; "keep going" standing)
Reported: yes — shape rendered in the milestone plan + this bundle

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/intake.md` · `.claude/skills/add/intake.md` · `add-method/src/add_method/_bundled/skill/add/intake.md` · `add-method/tooling/test_fast_lane_heuristic.py`
Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced; preferred architecture/pattern strategies; advise solution/method to resolve issues/implement features; let the named Persona's domain stance (below) shape the approach, not just architecture patterns>
Approach (domain strategy): <the core technique chosen and WHY it fits this task's domain — an algorithm, a data model, a migration path, a prose structure, a UX flow — in the named Persona's domain vocabulary; derive from §1 Framings weighed, not invented here>
Data strategy: <the shapes and access patterns the work realizes — data structures, schema use, information architecture for prose/docs — must agree with the §3 Schema line>
Pattern: <the domain pattern this build follows and the §0 Honors / CONVENTIONS.md anchor it extends>
Optimization stance: <WHAT is optimized and its budget — latency, memory, token cost, readability — or "correctness-first, no budget"; never blank; ⚠-mark the facet you trust least; risk: high -> consult add-advisor; facets draft at tests->build; advisory, never a gate>

Persona (required): methodology-engine-dev
Spawn isolation (default): <prefer isolation: "worktree" for any subagent build/verify spawn; shared-tree needs a stated reason — see worktree-isolated-spawn-default>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: as planned; two compression passes needed (216B then 117B) to absorb 331B
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (test_fast_lane_heuristic 5/5 · fences 12/12 · full tooling suite exit 0)
- [x] coverage did not decrease (5 new tests)
- [x] no test or contract altered during build
- [x] green EARNED — human-owned/confirm asserted INSIDE the heuristic's own 600-char span, not anywhere-in-file; doubt→full-lane direction pinned
- [x] concurrency safe — prose
- [x] no secrets/injection/deps
- [x] layering — guide text; engine untouched
- [x] shape confirmed via milestone plan + standing directive

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] Fast-fit test present with all 4 pinned elements — tests green
- [x] fences green — +331B absorbed by -333B compression (2 passes), no rebaseline
- [x] 3 trees byte-identical

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — n/a (prose)
- [x] DEAD-CODE — none
- [x] SEMANTIC — compressed paragraphs (interview · batched intake · one-task gap) re-read in full; every rule survives compression (search-first, ask_human floor, ONE-proposal batching, micro-milestone routing)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] §3 anchors resolve: four-buckets table · proposal shape · Fast-fit block
- [x] none moved

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: probed that compression didn't drop the ask_human floor or the frozen-scope tie-break; that the heuristic scopes to the task bucket only

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR
2. Concurrency: CLEAR
3. Architecture: CLEAR — proposal-not-pick preserves the human-owned-flag floor
Verdict: PASS
Residue: none
Binding: advisory — guide truth

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose intake-guide heuristic; rejected engine auto-flag (rejected: violates the human-owned-flag floor) · status hint (rejected: too late, task already created)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (milestone plan confirmed; "keep going" standing))
- [AI] build — strategy used: as planned; two compression passes needed (216B then 117B) to absorb 331B
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

