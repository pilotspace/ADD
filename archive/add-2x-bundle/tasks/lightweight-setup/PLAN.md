# TASK: Lightweight setup: seed-and-defer foundation — sections fill on first touch by milestones/tasks

slug: lightweight-setup · created: 2026-07-07 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/skill/add/phases/0-setup.md §3 "Draft to the lock" (mandates filling ALL living docs + per-role personas upfront — the WM1 bootstrap token bomb) · add-method/tooling/add.py init-seeded PROJECT.md/GLOSSARY/CONVENTIONS templates (already skeletal; gain explicit living markers) · exit-gate wording in 0-setup.md
Context (working folder): human-proposed (2026-07-07): "setup lightweight, domain files update living with milestones/tasks" — round-3 add-arm WM1 burned 9.7M pre-code tokens largely on upfront foundation drafting
Honors (patterns / conventions): trust floor untouched (lock = the one baseline approval; first task §1–§4 + RED suite still mandatory) · lean pool byte fences (guide edit should SHRINK) · doc-truth ripples into guard tests pinning old wording (fix doc-pinning tests forward, never weaken behavior tests) · 3-tree skill parity
Seams consulted: none beyond the pool fences
Anchors the contract cites: 0-setup.md §3 step 1 · PROJECT.md template seed · exit_gate block
Issues/Risks (→ feed §1): guard tests may pin the current §3.1 wording (surface at red-run); the living marker must not trip the frozen tag census (bare HTML comments are safe — TASK.md.tmpl hazard memory does not apply to PROJECT.md)
Related intent: add-lean-loop MILESTONE.md task 3 (human-added) — attacks the bootstrap half of the cost
Ground SHA: a4d2eef

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: seed-and-defer foundation (lightweight setup)
Framings weighed: guide+template change (chosen — the tokens are spent by the AGENT following §3.1; no engine gating exists on doc fullness, so no engine risk) · engine-enforced doc stubs (rejected: adds a gate where none exists; trust floor is the lock, not doc volume) · skip setup entirely (rejected: kills the baseline approval — the floor)
Must:
<must>
  - 0-setup.md §3 step 1 becomes seed-and-defer: fill ONLY the goal line, the 4-lens seed answers (one line each into PROJECT.md Domain/Spec/UI-UX/Key Decisions), and what the FIRST milestone touches; every untouched living-doc section is left with its`<!-- living: fill on first touch -->` marker. One `generic` persona suffices at setup; per-role personas draft on first touch.
  - The init-seeded PROJECT.md template carries explicit`<!-- living: fill on first touch — grown by milestones/tasks, consolidated at fold -->` markers on its Domain/Spec/UI-UX sections.
  - The 0-setup.md exit gate says "seed lines filled + untouched sections carry the living marker" instead of "Living docs filled"; the lock / first-task §1–§4 RED-suite floor is UNCHANGED.
</must>
Reject:
<reject>
  - none engine-enforced — this is guide+template truth; the failure mode is a doc-pinning guard test going red, fixed forward at build
</reject>
After:
<after>
  - a fresh greenfield setup drafts ~1 screen of foundation instead of 5 full documents; foundation depth arrives exactly when a milestone/task first touches a section (the existing delta→fold loop keeps it living)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ no engine check requires filled living docs at lock — lowest confidence because adopt/check may census placeholders; if wrong: the red run of the tooling suite names the check, and the seed lines satisfy it or the task returns to specify
  - [ ] guide byte pools SHRINK from this edit (deferral is shorter than mandates) — confirmed at build by the fence tests
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: init seeds living markers   # M2
  Given a fresh `add.py init`
  Then .add/PROJECT.md contains "living: fill on first touch" markers on Domain/Spec/UI-UX

Scenario: setup guide teaches seed-and-defer   # M1
  Given the shipped 0-setup.md
  Then §3 instructs filling ONLY goal + 4-lens seed lines + first-milestone touches
  And it names the living marker for every untouched section
  And it no longer mandates authoring one persona per role at setup

Scenario: trust floor unchanged   # M3
  Given the shipped 0-setup.md exit gate
  Then it still requires: lock by the human · first task §1–§4 drafted · red suite RED before build
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
0-setup.md §3 step 1 (rewritten):
  "Seed, don't draft: goal line + the 4-lens seed answers (one line each) + ONLY the
   sections the first milestone touches. Every other living-doc section keeps its
   `<!-- living: fill on first touch -->` marker — the milestone/task loop grows it,
   `fold` consolidates it. One `generic` persona is enough at setup; author per-role
   personas when a task first embodies the role."
0-setup.md exit gate line 2 (rewritten):
  "Seed lines filled (goal · 4-lens · first-milestone touches); untouched sections
   carry the living marker (brownfield: evidence-grounded from code as today)."
add.py PROJECT.md init template: Domain/Spec/UI-UX section headers gain
  `<!-- living: fill on first touch — grown by milestones/tasks, consolidated at fold -->`
Floor unchanged: lock · first task §1–§4 · RED suite · SETUP-REVIEW.md lowest-confidence-first.

Schema: no state.json change; guide + template text only; 3 skill trees + 3 engine trees parity.
```

Glossary deltas: none
`Least-sure flag surfaced at freeze:` [test] an existing guard test may pin the exact "Living docs filled" exit-gate wording or §3.1 text — surfaces red at build; fixed forward (doc-truth ripple), never by weakening a behavior test.
Status: FROZEN @ v1 — approved by Tin Dang (the feature is his 2026-07-07 proposal; slot confirmed "Add, after task 2")
Reported: yes — design rendered in-session at intake (skeleton/first-touch/fold triad) before this freeze

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

Scope (may touch): `add-method/tooling/templates/PROJECT.md.tmpl` · `.add/tooling/templates/PROJECT.md.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/PROJECT.md.tmpl` · `add-method/tooling/add.py` · `add-method/tooling/test_lightweight_setup.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/skill/add/phases/0-setup.md` · `.claude/skills/add/phases/0-setup.md` · `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md` · `.add/SEAMS.md`
Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced; preferred architecture/pattern strategies; advise solution/method to resolve issues/implement features; let the named Persona's domain stance (below) shape the approach, not just architecture patterns>
Approach (domain strategy): <the core technique chosen and WHY it fits this task's domain — an algorithm, a data model, a migration path, a prose structure, a UX flow — in the named Persona's domain vocabulary; derive from §1 Framings weighed, not invented here>
Data strategy: <the shapes and access patterns the work realizes — data structures, schema use, information architecture for prose/docs — must agree with the §3 Schema line>
Pattern: <the domain pattern this build follows and the §0 Honors / CONVENTIONS.md anchor it extends>
Optimization stance: <WHAT is optimized and its budget — latency, memory, token cost, readability — or "correctness-first, no budget"; never blank; ⚠-mark the facet you trust least; risk: high -> consult add-advisor; facets draft at tests->build; advisory, never a gate>

Persona (required): methodology-engine-dev
Spawn isolation (default): <prefer isolation: "worktree" for any subagent build/verify spawn; shared-tree needs a stated reason — see worktree-isolated-spawn-default>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: as planned; one recurring nuisance absorbed (importlib-loading tests regenerate _bundled __pycache__ — purged pre-fence)
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (test_lightweight_setup 6/6 · fences 63/63 targeted · full tooling suite exit 0)
- [x] coverage did not decrease (6 new tests)
- [x] no test or contract altered during build
- [x] green EARNED — living markers asserted on a REAL fresh init; floor asserted inside the actual <exit_gate> block, not anywhere-in-file
- [x] concurrency safe — text-only change
- [x] no secrets/injection/deps
- [x] layering — guide + template text; no engine logic change; ENGINE_MD5 unchanged this task... verified: add.py untouched
- [x] the feature is the human's own proposal; slot + shape confirmed in-session

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] fresh init shows 3 living markers — M2 green (real init)
- [x] guide teaches seed-and-defer — M1 tests green; -290 bytes (pools gained headroom)
- [x] exit gate keeps lock · §1–§4 · RED — M3 green; skill_lean fences green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — n/a (no code symbol); markers verified consumed by init output
- [x] DEAD-CODE — none
- [x] SEMANTIC — rewritten §3.1 + exit gate read in full across 3 trees; brownfield path (adopt.md, evidence-grounded) preserved; personas-teacher pointer preserved

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] §3 anchors resolve: 0-setup.md §3 step 1 · exit_gate · PROJECT.md.tmpl headers
- [x] none moved

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: probed that the floor assertions read the exit_gate REGION (regex-scoped), that markers land under the right headers (positional check), and that Key Decisions (append-only) is NOT marked living

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — prose
2. Concurrency: CLEAR
3. Architecture: CLEAR — defer-to-first-touch composes with the existing delta→fold loop; no new mechanism
Verdict: PASS
Residue: none
Binding: advisory — guide/template truth

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose guide+template change; rejected engine-enforced doc stubs (rejected: adds a gate where none exists; trust floor is the lock, not doc volume) · skip setup entirely (rejected: kills the baseline approval — the floor)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (the feature is his 2026-07-07 proposal; slot confirmed "Add, after task 2"))
- [AI] build — strategy used: as planned; one recurring nuisance absorbed (importlib-loading tests regenerate _bundled __pycache__ — purged pre-fence)
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

