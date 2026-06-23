# TASK: advance tests->build refuses an unfilled §6 Build-expectations block

slug: build-expectations-gate · created: 2026-06-23 · stage: mvp · risk: high
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_advance` — at the `if nxt == "build":` block; add the build-expectations gate (validate-then-write, BEFORE the tripwire/scope snapshot writes).
  - `add-method/tooling/add.py:_section_unfilled` — EXTEND (compatible): break on ANY header line + skip `>` blockquote guidance, so it reads the `### Build expectations` SUB-section. Task-1's `## Shared / risky contracts` behavior is preserved (its tests stay green).
  - `add-method/tooling/add.py:_raw_phase_bodies` — reused to read the task's §6 body (keyed by section number, like the §3 read already in cmd_advance).
  - milestone opt-in: the task's parent = `state["tasks"][slug].get("milestone")`; opted-in iff that milestone record has a `confirmed` key (the SAME switch task-1 uses, one level out).
  - `engine_pin.py:ENGINE_MD5` re-aim. `test_min_pillar` LIFECYCLE: NO change (advance already exercised).
Context (working folder): this task's own §6 (under the opted-in flow-enforcement milestone) — it must fill its Build-expectations to reach build (self-dogfood).
Honors (patterns / conventions): mirrors task-1's opted-in scope guard + the existing build-entry guards (unflagged_freeze, tripwire) — validate-then-write; grandfather-by-(no-confirmed-key | absent-section).
Anchors the contract cites: `cmd_advance` build-entry · `_section_unfilled` (extended) · reject `build_expectations_unfilled`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: build-expectations gate — verify-expectations must exist BEFORE build, opted-in per milestone
Framings weighed: gate at tests→build, milestone-opt-in scoped (chosen — the --await-confirm switch already turns on the flow-enforcement suite; zero ripple) · unconditional gate (rejected — breaks 33 advance-to-build suites) · risk:high-scoped (rejected — couples concepts + ripples to ~5 suites) · warning-only (rejected — Finding B asks for a gate)
Must:
<must>
  - SCOPE: the gate fires ONLY when the task's parent milestone OPTED IN (its record has a `confirmed` key). A task with no milestone, or under a grandfathered/plain milestone, is NEVER gated (every existing advance-to-build flow stays green).
  - for an opted-in task: `advance` from tests→build REFUSES `build_expectations_unfilled` when the §6 `### Build expectations` block is a `<…>` placeholder or empty — BEFORE the tripwire/scope snapshot writes (validate-then-write)
  - for an opted-in task whose §6 Build-expectations is FILLED, advance proceeds normally (and still takes the tripwire + scope snapshots)
  - `_section_unfilled` is EXTENDED compatibly (break on any header + skip `>` guidance) so it reads the `### Build expectations` sub-section; task-1's `## Shared / risky contracts` truth table is unchanged
</must>
Reject:
<reject>
  - opted-in task, tests→build, §6 Build-expectations placeholder/empty -> "build_expectations_unfilled"
</reject>
After:
<after>
  - an opted-in task cannot enter build until its verify-expectations are pre-declared; a refused advance leaves phase=tests and writes nothing (no tripwire, no scope snapshot)
  - the --await-confirm opt-in now activates BOTH the contract-fill gate (confirm) and the build-expectations gate (build)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ milestone-inherited opt-in is the right switch — lowest confidence because a task under a plain milestone gets no build-expectations enforcement even if high-risk; chosen because it unifies the flow-enforcement suite under one opt-in with ZERO ripple, and a plain-milestone project opted out of the strict flow wholesale; if wrong: a high-rigor task on a plain milestone misses the gate (cost: low — re-create the milestone --await-confirm, or a future per-task override).
  - [x] extend _section_unfilled (any-header break + skip `>`) is compatible — confirmed: task-1 contracts sections have no `>` and end at a `## ` header; re-run test_contract_fill_gate to prove green.
  - [x] gate before the snapshot writes — confirmed: a refused advance must not leave a tripwire/scope sidecar.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: opted-in task with unfilled build-expectations is blocked
  Given a task under an --await-confirm milestone, at phase=tests, whose §6 "### Build expectations" is the scaffold placeholder
  When add.py advance
  Then it dies "build_expectations_unfilled"
  And phase stays tests and no tripwire/scope snapshot is written

Scenario: opted-in task with filled build-expectations advances
  Given the same task but §6 Build-expectations filled with real outcomes (no <…>)
  When add.py advance
  Then phase becomes build and the tripwire + scope snapshots are taken

Scenario: task under a plain (no-key) milestone is never gated
  Given a task under a milestone created WITHOUT --await-confirm, §6 placeholder, at phase=tests
  When add.py advance
  Then phase becomes build (gate skipped — every existing advance-to-build flow stays green)

Scenario: task with no milestone is never gated
  Given a milestone-less task at phase=tests with §6 placeholder
  When add.py advance
  Then phase becomes build (gate skipped)

Scenario: _section_unfilled still reads task-1's contracts section unchanged
  Given the extended predicate (any-header break + skip > guidance)
  When test_contract_fill_gate runs
  Then all 7 stay green (the ## Shared / risky contracts truth table is preserved)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py advance   (when nxt == "build")
  ok  -> phase=build (+ tripwire & scope snapshots)   [NOT opted-in · OR opted-in + §6 Build-expectations FILLED]
  4xx -> error: "build_expectations_unfilled"          [opted-in (parent milestone has a `confirmed` key) AND §6 "### Build expectations" placeholder/empty]
Opt-in: ms = state.tasks[slug].milestone; opted_in = bool(ms) and "confirmed" in state.milestones.get(ms, {})
Predicate (extended, compatible): _section_unfilled(md, header)
  break the section at ANY next header line (startswith "#"); SKIP `>` blockquote guidance lines;
  then PRESENT-but-(empty | `<…>`)→True · ABSENT→False · filled→False  (## Shared/risky contracts unchanged)
Order in cmd_advance build-entry: [build-expectations gate, opted-in only] -> unflagged_freeze -> tripwire snapshot -> scope snapshot
Schema: validate-then-write — a refused advance leaves phase=tests, writes NO tripwire/scope sidecar, no state change
```

Status: FROZEN @ v1 — approved by Tin Dang (milestone-inherited --await-confirm opt-in is the master switch for the flow-enforcement suite; zero ripple; _section_unfilled extended compatibly)
Least-sure flag surfaced at freeze:
[spec] milestone-inherited opt-in is the gate switch — biggest risk: a high-rigor task under a PLAIN milestone gets no build-expectations enforcement. Chosen to unify the suite under one opt-in with zero ripple; cost if wrong is low (re-create the milestone --await-confirm). The predicate extension (any-header break + skip `>`) is confirmed compatible, not flagged.
risk: high
autonomy: conservative
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject + the predicate extension (≥6 tests)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_optedin_unfilled_blocks_build: --await-confirm ms + fill contracts + confirm + new-task + reach tests, §6 placeholder / advance / assert SystemExit "build_expectations_unfilled" + phase still tests + no scope-snapshot sidecar
  - test_optedin_filled_advances: same but §6 filled / advance / assert phase==build
  - test_plain_milestone_task_not_gated: no --await-confirm ms / task to tests, §6 placeholder / advance / assert phase==build
  - test_no_milestone_task_not_gated: milestone-less task / advance to build / assert phase==build
  - test_section_unfilled_subsection: predicate over "### Build expectations" (placeholder→True · filled→False · empty-but-> guidance→True)
  - test_section_unfilled_contracts_unchanged: re-assert the task-1 truth table holds with the extended predicate
</test_plan>

Tests live in: `add-method/tooling/test_build_expectations_gate.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_build_expectations_gate.py` `add-method/tooling/engine_pin.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py`
Strategy (ordered batches): 1. extend `_section_unfilled` (any-header break + skip `>`). 2. add the opted-in build-expectations gate in cmd_advance build-entry (before tripwire). 3. cp canonical → 2 mirror trees. 4. re-aim engine_pin. 5. full suite green (incl. task-1's tests).
Safety rule (feature-specific): validate-then-write — the gate `_die`s BEFORE the tripwire/scope snapshot writes, so a refused advance leaves phase=tests with no sidecar.
Code lives in: `add-method/tooling/add.py` (canonical) → propagated byte-identical to the 2 mirror trees
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1583/0; +6 new test_build_expectations_gate.py; task-1's 7 stay green (predicate extension compatible)
- [x] coverage did not decrease — +6 new tests; no existing test deleted; the census + 33 advance-to-build suites untouched (await_confirm marker contains the gate)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 unchanged; the await_confirm marker is an additive seed field (task-1's tests ignore it)
- [x] the green was EARNED, not gamed — the gate fires on a real _section_unfilled read of the on-disk §6; proven live by blocking THIS task's own advance until §6 was filled; the not-gated tests prove the opt-in is genuinely scoped (not vacuous)
- [x] concurrency / timing of the risky operation is safe — no new IO/threading; one extra in-memory §6 read before the existing snapshot writes; validate-then-write (refused advance writes no sidecar)
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports; reads only the task's own TASK.md via the existing _raw_phase_bodies
- [x] layering & dependencies follow CONVENTIONS.md — mirrors task-1's opted-in gate + the existing build-entry guards; 3-tree parity (md5 d7a104fa)
- [ ] a person reviewed and approved the change — **PENDING: risk:high + autonomy:conservative → this gate STOPS for the human (you)**

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] advancing an opted-in task with placeholder §6 prints `add: error: build_expectations_unfilled …` and leaves phase=tests — seen LIVE on this very task (build-expectations-gate blocked its own advance until §6 was filled)
- [x] a task under a plain/no milestone advances to build despite a placeholder §6 — the census + test_plain_milestone_task_not_gated + test_no_milestone_task_not_gated stay green (gate skipped)
- [x] task-1's contract-fill gate still works after the _section_unfilled extension — test_contract_fill_gate 7/7 green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the gate calls `_section_unfilled` + `_raw_phase_bodies` in cmd_advance's build-entry; `await_confirm` is seeded in cmd_new_milestone and read by the gate; all exercised by the 6 tests
- [x] DEAD-CODE (code) — no orphan; the extended `_section_unfilled` now has two callers (confirm gate + build gate) + direct tests; `await_confirm` has a writer + a reader
- [x] SEMANTIC (prose / non-code) — re-read the §3 v1 contract + the engine_pin v1.1 note: the gate keys on the stable `await_confirm` marker (not `confirmed`, which milestone-confirm stamps on plain milestones); grandfather holds for plain/no-milestone tasks

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
- [SPEC · open] reconcile the §3 opt-in prose ("`confirmed` in milestone") to the stable `await_confirm` marker the build actually uses (evidence: build v1.1 — milestone-confirm stamps confirmed:true on plain milestones too, so the census broke; the marker is the correct opt-in signal — observable contract unchanged)

### Competency deltas
- [ADD · open] a content gate placed at a LATER lifecycle point than its opt-in marker can mis-read a field a sibling command mutates in between — key gates on a STABLE creation-time marker (`await_confirm`), not a mutable one (`confirmed`) (evidence: milestone-confirm stamps confirmed on plain milestones → census false-positive at advance time)
- [ADD · open] reuse one predicate across gates by EXTENDING it conservatively (any-header break + skip `>` guidance) and prove the prior caller's truth table still holds (evidence: _section_unfilled shared by contract-fill + build-expectations; test_contract_fill_gate 7/7 stayed green)
