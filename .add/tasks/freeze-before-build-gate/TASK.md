# TASK: opt-in freeze-before-build gate

slug: freeze-before-build-gate · created: 2026-06-23 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add.py:cmd_advance` (1044 — the `nxt == "build"` block at 1062; add a freeze check BESIDE the build-expectations gate at 1069-1073). ×3 add.py trees + engine_pin re-pin. `test_freeze_before_build_gate.py` in `add-method/tooling/`.
Context (working folder): EMPIRICAL FINDING (verified) — the engine does NOT block an unfrozen task from build/gate today; a DRAFT §3 task reaches gate=PASS. An ALL-tasks guard breaks ~40 fixtures (81 fails at build-entry, 176 at gate) → the human chose the opt-in path.
Honors (patterns / conventions): opt-in-grandfather (mirror the build-expectations gate EXACTLY: fire only when `state.milestones[ms].await_confirm is True`; a plain/no-milestone task is never gated → zero ripple) · validate-then-write (refuse BEFORE the tripwire/scope snapshots) · 3-tree parity · engine-pin-3-parts.
Anchors the contract cites: `cmd_advance` build-expectations gate (1069-1073 — `_ms = ...; if _ms and (...).get(_ms,{}).get("await_confirm") is True:` — the SIBLING opt-in condition this mirrors, placed adjacent) · `_contract_frozen` (4361 — the §3-FROZEN predicate) · `_raw_phase_bodies` (4042 — reads the raw §3 body) · the freeze should be checked BEFORE build-expectations (you freeze §3 before pre-declaring §6 outcomes).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an OPT-IN freeze-before-build gate — under an `await_confirm` milestone, a task may not cross tests→build until §3 is FROZEN, so the freeze becomes ENGINE-enforced (not just convention) where the human opted in.
Framings weighed: mirror the build-expectations gate's opt-in keyed on `await_confirm is True`, placed adjacent in cmd_advance (chosen — proven, zero-ripple) · all-tasks hard guard (rejected — ~40-file fixture migration, the confirm-parent trap: 81 fails at build-entry / 176 at gate) · fast-only (rejected — the human chose opt-in over fast-only)
Must:
<must>
  - in `cmd_advance` at `nxt == "build"`, when the parent milestone has `await_confirm is True` AND §3 is NOT `_contract_frozen`, die `contract_not_frozen` (validate-then-write — refuse BEFORE the tripwire/scope snapshots, writing nothing)
  - check the freeze BEFORE the build-expectations gate (you freeze §3 before pre-declaring §6 outcomes)
  - a task under a plain / no-`await_confirm` milestone (or no milestone) is NEVER gated → every existing advance-to-build flow stays byte-green (zero ripple)
  - a FROZEN §3 passes the new check; the EXISTING `unflagged_freeze` flag check still applies after it (a frozen contract still needs its well-formed flag)
  - 3 add.py trees byte-identical; engine_pin re-pinned
</must>
Reject:
<reject>
  - advancing tests→build with an unfrozen §3 under an opted-in (`await_confirm`) milestone -> "contract_not_frozen" (names the fix: approve the contract → Status: FROZEN @ vN)
</reject>
After:
<after>
  - under an opted-in milestone, `advance` tests→build refuses an unfrozen task and leaves it at `tests` (no phase write); a non-opted-in milestone is unchanged
  - the milestone's "collapse-never-skip" floor is now REAL for opted-in milestones (incl. fast-lane once it opts in)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ keying on `await_confirm is True` is truly ~zero-ripple — RESOLVED by measurement: an opt-in-keyed prototype broke ONLY `test_build_expectations_gate` (2 tests, the sibling gate whose fixtures opt-in + advance an unfrozen §3 to build). Every other failure (53) was pure parity/pin noise from the canonical-only prototype, NOT guard-logic ripple. So the fix is contained: add `Status: FROZEN` to those 2 sibling fixtures (declared in §5 scope). NOT the 40-file all-tasks migration.
  - [ ] placing the freeze check before build-expectations (vs after) is right — freezing §3 logically precedes pre-declaring §6; deny only if the reverse order reads better.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: opted-in milestone refuses an unfrozen task at tests→build
  Given a task under an await_confirm milestone, at the tests phase, §3 Status DRAFT
  When I run advance
  Then it dies "contract_not_frozen"
  And the task stays at the tests phase (no phase write)

Scenario: opted-in milestone lets a FROZEN task cross
  Given a task under an await_confirm milestone, at tests, §3 FROZEN with a well-formed flag
  When I run advance
  Then the task advances to build
  And the existing unflagged_freeze check still applies (a frozen §3 missing its flag is still refused)

Scenario: a non-opted-in milestone is unaffected (zero ripple)
  Given a task under a PLAIN milestone (no await_confirm), at tests, §3 Status DRAFT
  When I run advance
  Then the task advances to build (the gate does not fire)

Scenario: a task with no milestone is unaffected
  Given a milestone-less task at tests, §3 Status DRAFT
  When I run advance
  Then the task advances to build

Scenario: the freeze check precedes build-expectations
  Given an opted-in task at tests with BOTH §3 DRAFT and §6 Build expectations empty
  When I run advance
  Then it dies "contract_not_frozen" (the freeze gate fires first, not build_expectations_unfilled)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE  cmd_advance — a NEW gate at the `nxt == "build"` crossing, placed BEFORE the
        existing build-expectations gate.

GUARD (the frozen seam):
  _optin := the task has a milestone M AND state["milestones"][M]["await_confirm"] is True
  if _optin and NOT _contract_frozen(_raw_phase_bodies(root, slug).get(3, "")):
      _die("contract_not_frozen: freeze §3 before crossing into build — approve the
            contract (Status: FROZEN @ vN)")
  validate-then-write: the refusal runs BEFORE the tripwire + scope snapshots, writes
    NOTHING; the task stays at `tests`.
  ORDER: this check PRECEDES the build-expectations check (freeze §3 before §6 pre-declare).
  PASS-THROUGH: a FROZEN §3 continues; the existing _flag_well_formed / unflagged_freeze
    check still applies after it.

FIRING SCOPE:
  fires ONLY when await_confirm is True — a plain milestone, a no-await_confirm milestone,
  or a milestone-less task is NEVER gated (zero ripple; mirrors the build-expectations opt-in).

REJECT: contract_not_frozen — an unfrozen §3 crossing tests→build under an opted-in milestone.
STATE: no new key, no new flag — reads existing state.milestones[M].await_confirm + the §3 body.
SIBLING-FIXTURE FIX (in-scope): test_build_expectations_gate's 2 opted-in fixtures advance an
  unfrozen task to build; they get a `Status: FROZEN` added (the only real ripple, measured).
```

Least-sure flag surfaced at freeze: [contract/test] keying on `await_confirm` (opt-in) — the bet that this is ~zero-ripple was MEASURED (only test_build_expectations_gate's 2 fixtures break, fixed by adding a freeze; the other 53 failures were parity/pin noise from a canonical-only prototype). Residual: a not-yet-seen fixture that opts in and advances unfrozen would also need a freeze — the full suite is the backstop.

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the new guard branch + its precedence over build-expectations (6 behavioral tests).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_optedin_unfrozen_blocks_build: opted-in + DRAFT §3 / advance / dies "contract_not_frozen" + phase stays "tests" + no scope-snapshot (validate-then-write)
  - test_optedin_frozen_advances: opted-in + FROZEN §3 (with well-formed flag) + filled §6 / advance / phase=="build"
  - test_plain_milestone_unfrozen_advances: plain milestone + DRAFT §3 / advance / phase=="build" (gate does not fire)
  - test_no_milestone_unfrozen_advances: milestone-less + DRAFT §3 / advance / phase=="build"
  - test_freeze_precedes_build_expectations: opted-in + DRAFT §3 + placeholder §6 / advance / dies "contract_not_frozen" NOT "build_expectations_unfilled" (freeze fires first)
  - test_frozen_then_build_expectations_gate_takes_over: opted-in + FROZEN §3 + placeholder §6 / advance / dies "build_expectations_unfilled" (precedence proof in reverse — next gate takes over)
</test_plan>

Tests live in: `add-method/tooling/test_freeze_before_build_gate.py` · MUST run red (missing implementation) before Build.
RED confirmed (2026-06-23): `python3 -m unittest test_freeze_before_build_gate` → 2 failures for the RIGHT reason — the two unfrozen-blocks scenarios expect `contract_not_frozen` but currently hit `build_expectations_unfilled` (the guard does not exist yet); the other 4 pass on the existing non-gated / build-expectations paths.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_build_expectations_gate.py`
Strategy (ordered batches): 1. add the `contract_not_frozen` guard in cmd_advance (canonical), placed BEFORE the build-expectations gate. 2. add `Status: FROZEN` to test_build_expectations_gate's 2 opted-in fixtures (the measured sibling ripple). 3. copy canonical add.py → the 2 mirror trees (byte parity). 4. re-pin engine_pin.py (ENGINE_MD5 + annotation).
Safety rule (feature-specific): validate-then-write — the refusal must run BEFORE the tripwire + scope snapshots, writing nothing; the task stays at `tests`.
Code lives in: `add-method/tooling/add.py` (+ 2 mirror trees)
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

- [ ] all tests pass
- [ ] coverage did not decrease
- [x] no test or contract was altered during build — the §3 frozen contract is byte-unchanged; the only test edit was the in-scope sibling-fixture fix (test_build_expectations_gate `_optedin_task_at_tests` freezes §3), declared in §5 and named in the frozen §3 SIBLING-FIXTURE FIX clause
- [x] the green was EARNED, not gamed — adversarial mutation refute-read: neutralizing the guard (`_optin` → `False`) breaks EXACTLY the 2 unfrozen-blocks tests, restoring returns to green; the tests assert observable behavior (error code, phase stays `tests`, no scope-snapshot on refusal, error-string precedence) not internals — not overfit
- [x] concurrency / timing of the risky operation is safe — pure synchronous in-process guard; no IO, no threads. validate-then-write: the refusal runs BEFORE the tripwire/scope snapshots, writing nothing
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports; reads existing `state` + the §3 body via existing `_raw_phase_bodies`/`_contract_frozen`
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the sibling build-expectations gate EXACTLY (same opt-in switch, same validate-then-write placement); 3-tree byte parity held (md5 80985fc3)
- [x] a person reviewed and approved the change — §3 FROZEN @ v1 approved by Tin Dang (the human decision point); verify auto-gated on complete evidence (no security / concurrency / architecture residue → no escalation trigger)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] under an opted-in (`await_confirm`) milestone, `advance` tests→build on an unfrozen §3 prints `contract_not_frozen` and leaves phase=`tests` — confirmed by test_optedin_unfrozen_blocks_build + the live mutation refute-read
- [x] a plain / no-`await_confirm` / milestone-less task still advances tests→build with a DRAFT §3 (zero ripple) — confirmed by test_plain_milestone_unfrozen_advances + test_no_milestone_unfrozen_advances + the full suite (1620 green, no existing advance-to-build test touched)
- [x] the freeze check fires BEFORE build-expectations (DRAFT §3 + placeholder §6 → `contract_not_frozen`, not `build_expectations_unfilled`) — confirmed by test_freeze_precedes_build_expectations; the reverse (frozen §3 + placeholder §6 → build-expectations takes over) by test_frozen_then_build_expectations_gate_takes_over

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the new guard is the only new code; `_optin`/`raw3` are computed once and consumed by the freeze check, the build-expectations check, and the unflagged_freeze check (all in the `nxt == "build"` block); `contract_not_frozen` present in all 3 trees (grep = 1 each)
- [x] DEAD-CODE (code) — no new symbol introduced (reuses `_contract_frozen`, `_raw_phase_bodies`, `_section_unfilled`, `_flag_well_formed`); the refactor REMOVED a duplicate `raw3` read, net-simpler
- [x] SEMANTIC (prose / non-code) — engine_pin.py annotation prepended (append-only history preserved); `add.py check` 391 passed / 0 failed; engine-pin parity (test_engine_repin_parity + test_shared_engine_pin) 13 green

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
