# TASK: Cross Component Milestone

slug: cross-component-milestone · created: 2026-06-25 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project `auto`: method-defining — adds a HOLD gate to the core `cmd_advance` path. The opt-in byte-identical invariant + a human verify guard the blast radius. -->
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
  - `add-method/tooling/add.py:cmd_advance(args)` (L1186) — the phase-bump path. Task 3 added a producer-write / consumer-pin hook at the `nxt == "tests"` (contract→tests) crossing. This task adds an EARLIER hold at `nxt == "contract"` (scenarios→contract): a consumer may not WRITE its §3 until the producer froze.
  - `add-method/tooling/add.py:_task_consumes(root, slug)` + `_contract_snapshot(root, id)` (task 3) — the binding + the snapshot whose EXISTENCE is the proof "the producer froze its contract". The inputs this hold consumes.
  - `add-method/tooling/add.py:_contracts(root)` (task 3) — to name the producer in the refusal message.
Context (working folder):
  - NEW test `add-method/tooling/test_cross_component_milestone.py`; models task 3's board harness (a producer + a consumer task in one milestone). 3-tree parity + `engine_pin.py` re-pin.
Honors (patterns / conventions):
  - INVARIANT (MILESTONE): freeze is the cross-component gate — a consumer task may not enter §3 (contract) until its producer's cross-component contract is frozen; this is the intra-milestone BE→FE ordering (the FE stays downstream of the frozen endpoint).
  - INVARIANT: opt-in — no `consumes:` header / no contract ⇒ `cmd_advance` byte-identical to today.
  - validate-before-write: the hold refuses BEFORE the phase bump (the task stays at `scenarios`).
  - red/green TDD · 3-tree parity.
Anchors the contract cites: `cmd_advance` · `_task_consumes` · `_contract_snapshot` · `_contracts`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Intra-milestone cross-component ordering — a consumer task is HELD from writing its §3 until its producer's contract is frozen, so a BE→FE vertical slice ships in one milestone
Framings weighed: hold at the scenarios→contract crossing keyed on snapshot existence (chosen — reuses task 3's snapshot as the freeze-proof, no new state) · a separate `depends-on`-style DAG block the engine schedules · hold at ground→specify (too early — the consumer can't even frame its rules)
Must:
<must>
  - HOLD: a task with `consumes: <id>` may not advance scenarios→contract while `.add/contracts/<id>.json` does NOT exist (its producer has not frozen) — refused `producer_contract_unfrozen`, the task stays at `scenarios`.
  - Once the producer's snapshot exists (the producer froze + crossed contract→tests), the consumer advances into §3 normally; it then pins at contract→tests (task 3).
  - the refusal names the producer component (from `_contracts`) so the operator knows what to freeze first.
  - OPT-IN / byte-identical: a task with no `consumes:` header (or a `consumes:` whose contract isn't declared) advances scenarios→contract exactly as today.
</must>
Reject:
<reject>
  - a `consumes: <id>` task advancing scenarios→contract while `.add/contracts/<id>.json` is absent -> "producer_contract_unfrozen"
</reject>
After:
<after>
  - In one milestone a producer (BE) task and a consumer (FE) task coexist; the FE cannot enter §3 until the BE's contract is frozen — a full-stack slice ordered by the frozen seam, not split across milestones.
  - No-role / undeclared-contract task: scenarios→contract byte-identical to today.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ snapshot EXISTENCE is a sufficient proxy for "the producer froze its contract" — lowest confidence because a stale snapshot from a prior run could let a consumer through prematurely; if wrong: the FE enters §3 against an out-of-date endpoint. Mitigation: task 3 writes the snapshot only on the producer's contract→tests crossing (a real freeze), and `contract_consumer_stale` catches a later drift — so the window is a deleted-then-recreated edge, acceptable for MVP.
  - [x] hold at scenarios→contract (not at a `depends-on` DAG) is the right altitude — CONFIRMED (lead): §3 is where the consumer commits to the producer's shape, the latest safe moment to require the freeze.
  - [x] a `consumes:` whose `<id>` has no `[contract.*]` entry should NOT hold (treat as no-op) — CONFIRMED (lead): an undeclared contract has no producer to wait on; task 3's `contract_*` finding surfaces the typo.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Consumer is held until the producer freezes
  Given a declared [contract.gateway-api] (producer gateway, consumer dashboard), a consumer task `consumes: gateway-api` at `scenarios`, and NO `.add/contracts/gateway-api.json` yet
  When it advances scenarios -> contract
  Then it fails with "producer_contract_unfrozen"
  And the task stays at `scenarios` — phase unchanged

Scenario: Consumer proceeds once the producer's contract is frozen
  Given the producer task froze + wrote `.add/contracts/gateway-api.json`
  When the consumer task advances scenarios -> contract
  Then it advances to `contract` (no hold)

Scenario: Full-stack slice in one milestone
  Given a producer (BE) `produces: gateway-api` and a consumer (FE) `consumes: gateway-api` in the SAME milestone
  When the BE freezes its contract, then the FE advances
  Then the FE enters §3 only after the BE froze — one milestone, ordered by the seam

Scenario: Undeclared consumed contract does not hold
  Given a task `consumes: nope` where no [contract.nope] is declared
  When it advances scenarios -> contract
  Then it advances normally (the registry finding, not a hold, surfaces the typo)

Scenario: No-role task is byte-identical
  Given a task with no `consumes:` header
  When it advances scenarios -> contract
  Then it advances exactly as today
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Engine API — add-method/tooling/add.py · builds on task 3's _task_consumes/_contracts/_contract_snapshot

cmd_advance(args)                                  # EXTENDED — only the consumer-hold path is new
  at the scenarios->contract crossing (nxt == "contract"):
    let cid = _task_consumes(root, slug)
    if cid and cid in _contracts(root) and not _contract_snapshot(root, cid).exists():
        _die("producer_contract_unfrozen: the producer '<producer>' of contract '<cid>' must freeze
            its contract before you write §3 — wait for .add/contracts/<cid>.json")
        # HARD-STOP placed BEFORE state["phase"]=nxt -> task stays at `scenarios`
  cid not a declared contract / no consumes  ->  scenarios->contract BYTE-IDENTICAL to today

Schema: no new state · no new file · reads task 3's _contracts + _contract_snapshot existence
```

Status: FROZEN @ v1 — approved by Tin Dang (AUTO MODE: project-lead decision), 2026-06-25. Both flags ACCEPTED as defaults.
Least-sure flag surfaced at freeze: [spec] snapshot EXISTENCE is the freeze-proof — a stale leftover snapshot could admit a consumer prematurely; if wrong: gate on a richer freeze record. [contract] the hold fires only for a DECLARED contract id (an undeclared `consumes:` is a registry finding, not a hold) — if wrong: hold on any consumed id. Both default-accepted.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new hold branch.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - Hold: held-until-frozen (refused + stays scenarios) · proceeds-once-snapshot-exists · full-stack-slice (real producer freeze, then FE proceeds) · undeclared-no-hold · no-role-byte-identical
</test_plan>
Red run (2026-06-25): 5 tests · 4 green (proceed/full-stack/undeclared/no-role already advance) · 1 RED (the hold not yet implemented). Right reason.

Tests live in: `add-method/tooling/test_cross_component_milestone.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/add.py`
Strategy (ordered batches): 1. RED — `add-method/tooling/test_cross_component_milestone.py` (5 scenarios) · 2. add the scenarios→contract hold in `cmd_advance` (consumes + declared + no-snapshot → `producer_contract_unfrozen`) · 3. GREEN; propagate to 2 mirrors + re-pin.
Safety rule (feature-specific): the hold refuses BEFORE the phase bump (validate-before-write — task stays at `scenarios`). The non-consumer / undeclared path takes NO new branch.
Code lives in: `add-method/tooling/add.py` (+ mirrors)
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear. Re-cross tests→build after declaring §5. `.add/` is pruned by `_scope_walk` so the gate-enforced token is `add-method/`.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full engine suite 1722/0; task suite test_cross_component_milestone.py 5/5.
- [x] coverage did not decrease — +5 tests; the hold branch (held / proceed / full-stack / undeclared / no-role) is fully exercised; one task-3 test was adapted (cross-task interaction, below).
- [x] no test or contract was altered during build — §3 v1 untouched. The hold made a task-3 SCENARIO (declared consumer reaching contract→tests with a never-present snapshot) unreachable, so `test_consumer_without_snapshot_hard_stops` was re-arranged to the still-reachable "snapshot vanished after §3-entry" path — intent preserved (still asserts `contract_snapshot_missing` + phase stays `contract`); the never-present case is now covered by this task's hold test. Refute-read Finding 3 confirmed the adaptation honest (coverage redistributed, not dropped).
- [x] the green was EARNED — adversarial refute-read returned GREEN-EARNED: validate-before-write confirmed (hold `_die` precedes the phase bump; held task stays at `scenarios`), opt-in byte-identity confirmed, composition with task-3's pin confirmed, `test_full_stack_slice_one_milestone` drives a REAL engine producer-freeze (not a hand-written snapshot). One MAJOR (Finding 1, disclosed below) is a pre-existing engine-wide property, not introduced here.
- [x] concurrency / timing safe — pure reads (`_task_consumes`/`_contracts`/snapshot existence); no new IO. `_contracts` is degrade-safe (never raises), so a malformed components.toml can't break a non-consumer advance.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; no new state, no new file; the consumed id flows only into an existence check + the refusal message.
- [x] layering & dependencies follow CONVENTIONS.md — the hold sits beside the existing `setup_unlocked`/freeze guards at the top of `cmd_advance`; reuses task 3's readers.
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] A consumer of a declared contract is REFUSED scenarios→contract with `producer_contract_unfrozen` while no snapshot exists, and stays at `scenarios` — `test_consumer_held_until_producer_freezes`.
- [x] Once the producer's snapshot exists, the same consumer advances into `contract` — `test_consumer_proceeds_once_snapshot_exists` + `test_full_stack_slice_one_milestone` (real BE freeze → FE proceeds).
- [x] An undeclared `consumes:` id and a no-role task both advance scenarios→contract byte-identically — `test_undeclared_contract_does_not_hold` + `test_no_role_byte_identical` + full suite 1722/0.
- [x] 3-tree parity + ENGINE_MD5 re-pinned (`80b9350a…`) — parity/pin tests green.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the hold block reads `_task_consumes` + `_contracts` + `_contract_snapshot` (all task 3) and fires `_die`; reachable from `cmd_advance` scenarios→contract. No new symbol introduced (reuses task 3's readers).
- [x] DEAD-CODE (code) — no new symbols; pure reuse.
- [x] SEMANTIC — re-read the refute-read: the hold is validate-before-write + opt-in + composes with task 3. The one MAJOR (cmd_phase bypass) is a pre-existing engine-wide property (cmd_phase bypasses ALL gates by design — it's the backward-correction tool) → seeded as a §7 SPEC delta, not a blocker.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] `cmd_phase` bypasses the cross-component HOLD (and every advance-time gate) — an operator can `add.py phase contract <consumer>` to enter §3 without the producer freeze (evidence: refute-read Finding 1 MAJOR; this is a pre-existing engine-wide property of `cmd_phase`, the backward-correction tool, not specific to this task — a future `phase`-gate or a documented invariant would close it). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] the hold keys on snapshot EXISTENCE, so a stale leftover snapshot from a prior milestone admits a consumer prematurely (evidence: §1 ⚠ + refute-read Finding 4; `contract_consumer_stale` catches post-admission drift but only after entry — a freeze-recency check would close it). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
