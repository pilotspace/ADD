# TASK: Lock-state schema + atomic add.py lock + downstream gating

slug: setup-lock-state · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- high-risk: method/trust-layer scope; `auto` refused here (unguarded_high_risk_auto). The run builds, then STOPS at verify for a human. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: setup lock-down — an atomic, engine-enforced gate that freezes the autonomously-drafted
onboarding (foundation + first-milestone scope + first task contract). Until it is set, a project
in "await-lock" mode refuses to add further scope or cross into BUILD. It is the setup-altitude
analog of the contract freeze, and the only new human action onboarding requires.

Framings weighed: build-boundary gate (chosen) · dumb flag · verifying lock
  - chosen: pre-lock you may draft EXACTLY the first task's front (milestone + one task + §1–§4);
    the engine refuses a 2nd task and refuses advancing into build/verify until `add.py lock`.
  - dumb flag (rejected): a bare boolean with no gating — nothing enforces "no build before review".
  - verifying lock (rejected): `lock` inspects foundation/scope/contract artifacts before allowing —
    injects judgment into the engine; ADD keeps `add.py` judgment-free, the human signature IS the gate.

Must:
  - `add.py lock` sets `setup.locked=true` in ONE atomic state write, stamping `locked_at` (`_now()`),
    `locked_by`, and `layers` (default `foundation,scope,contract`).
  - `add.py lock --json` prints exactly ONE compact JSON object and nothing else.
  - `add.py init --await-lock` seeds `setup={locked:false, locked_at:null, locked_by:null, layers:[]}`;
    plain `add.py init` writes NO `setup` key (unchanged).
  - Grandfather: a state with NO `setup` key is treated as locked — legacy projects are never gated.
  - Pre-lock gating fires ONLY when `setup` exists AND `locked==false`:
      · `new-task` refuses once ≥1 task already exists (exactly one first task may be drafted pre-lock).
      · `advance` refuses when the next phase would be `build`/`verify`/`observe`/`done`.
      · `gate` refuses always.
  - Every refusal prints a clear message naming the unblock command (`add.py lock`).

Reject:
  - `lock` when already locked and no `--force` -> "already_locked"
    (already-locked is the `_setup_locked` predicate — so a GRANDFATHERED project with no `setup`
    key counts as already locked: bare `lock` refuses; `lock --force` writes a fresh `setup` block.)
  - `lock --layers` that parses to empty -> "layers_invalid"
  - `new-task` (2nd) while await-lock -> "setup_unlocked"
  - `advance` into build/verify/observe/done while await-lock -> "setup_unlocked"
  - `gate` while await-lock -> "setup_unlocked"

After:
  - `state.setup.locked==true`, timestamped + signed; `new-task`/`advance`/`gate` then proceed normally;
    re-lock is refused without `--force` (the lock is not casually re-run).
  - Plain-init and legacy projects (no `setup` key) behave EXACTLY as before — zero behavior change.

Assumptions — least-sure first:
  ⚠ [contract] The gate sits at the BUILD BOUNDARY, not at task creation — pre-lock the engine ALLOWS
    the first milestone + first task + its full front, and only refuses a SECOND task and advancing
    into BUILD. This REFINES the milestone exit criterion's flat wording ("new-task/advance refuse
    pre-lock"). Least sure because the milestone said "new-task refuses" flatly; if wrong (you want
    task creation itself blocked), the autonomous flow couldn't draft its own first contract —
    cost: re-cut the gate + the `autonomous-setup-guide` task, and update MILESTONE.md exit criterion.
  ⚠ [spec] The gate is OPT-IN via `init --await-lock`, NOT mandatory on every `init`. Least sure
    because the headline goal reads "fully autonomous → single lock", which sounds mandatory; chose
    opt-in because mandatory-on-init would break ~30 existing tests and force `lock` on manual users.
    If wrong, we make it mandatory + migrate the suite — cost: broad test churn + a doc rewrite.
  - [ ] `locked_by` defaults to `getpass.getuser()` when `--by` omitted — confirm vs requiring `--by`.
  - [ ] `lock` is idempotent-guarded (re-lock needs `--force`) — confirm vs silent no-op re-lock.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: lock sets and signs the setup state
  Given an `init --await-lock` project
  When I run `lock --by Tin`
  Then state.setup.locked is true, locked_by is "Tin", locked_at is set, layers == [foundation,scope,contract]
  And previously-gated commands now proceed

Scenario: lock --json prints exactly one object
  Given an `init --await-lock` project
  When I run `lock --by Tin --json`
  Then stdout parses as ONE json dict with keys locked, locked_at, locked_by, layers
  And stdout carries nothing but that object

Scenario: plain init is unchanged (grandfathered)
  Given a plain `init` project (no --await-lock)
  When I create several tasks, advance one into build, and record a gate
  Then state has no "setup" key
  And every command succeeds exactly as before

Scenario: await-lock init starts unlocked
  Given I run `init --await-lock`
  Then state.setup exists with locked == false

Scenario: first task allowed, second refused pre-lock
  Given an `init --await-lock` project with no tasks
  When I run `new-task a`
  Then it succeeds
  When I run `new-task b`
  Then it fails with "setup_unlocked"
  And only task `a` exists

Scenario: front advances but build is blocked pre-lock
  Given an `init --await-lock` project with task `a` at phase tests
  When I run `advance` (tests -> build)
  Then it fails with "setup_unlocked"
  And task `a` is still at phase tests
  And advancing specify->scenarios->contract->tests was allowed

Scenario: gate is blocked pre-lock
  Given an `init --await-lock` project with a task
  When I run `gate PASS`
  Then it fails with "setup_unlocked"
  And no gate outcome is recorded

Scenario: after lock, build and gate proceed
  Given an `init --await-lock` project, locked, with task `a` at phase tests
  When I run `advance`
  Then `a` moves tests -> build
  When I run `gate PASS`
  Then the outcome is recorded

Scenario: re-lock is guarded
  Given a locked project
  When I run `lock` again without --force
  Then it fails with "already_locked"
  When I run `lock --force`
  Then it re-locks successfully

Scenario: lock on a grandfathered project is refused
  Given a plain `init` project (no "setup" key — grandfathered-locked)
  When I run `lock` without --force
  Then it fails with "already_locked"
  And state still has no "setup" key
  When I run `lock --force`
  Then it writes setup.locked == true

Scenario: empty layers rejected
  Given an `init --await-lock` project
  When I run `lock --layers ""`
  Then it fails with "layers_invalid"
  And state.setup.locked is still false
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# CLI
add.py lock [--by NAME] [--layers a,b,c] [--force] [--json]
  text  -> "locked setup (foundation,scope,contract) by <who> @ <iso>"            exit 0
  --json-> {"locked":true,"locked_at":"<iso>","locked_by":"<who>","layers":[...]}  exit 0  (one object, stdout only)
  _setup_locked(state) & no --force -> stderr "add: error: already_locked"         exit 1
       (guard is the predicate, so a grandfathered no-`setup`-key project is "already locked";
        `--force` then writes a fresh setup block — `lock` always sets locked:true.)
  --layers parses to empty    -> stderr "add: error: layers_invalid"               exit 1
  --by omitted -> who = getpass.getuser()

add.py init [--await-lock]
  --await-lock -> seeds state.setup = {locked:false, locked_at:null, locked_by:null, layers:[]}
  (plain init writes NO setup key)

# Gating (active ONLY when "setup" in state AND state.setup.locked is false)
new-task  + a task already exists      -> stderr "add: error: setup_unlocked — lock the foundation first: add.py lock"  exit 1
advance   + next phase in {build,verify,observe,done} -> stderr "add: error: setup_unlocked …"                          exit 1
gate                                   -> stderr "add: error: setup_unlocked …"                                         exit 1

# State schema delta (state.json)
"setup": {
  "locked":    bool,        # init --await-lock writes false; KEY ABSENT => grandfathered-locked
  "locked_at": str | null,  # _now() ISO8601 UTC, set on lock
  "locked_by": str | null,  # set on lock
  "layers":    [str]        # set on lock; default ["foundation","scope","contract"]
}

# Predicate (the single source of truth for "is this project gated")
_setup_locked(state) := ("setup" not in state) or (state["setup"].get("locked") is True)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- locked 2026-06-04 by Tin (one human lock-down); build may not edit this. -->
<!-- Least-sure flag for the freeze: the two ⚠ in §1 — (1) gate at build-boundary (refines the
     milestone exit criterion), (2) opt-in via --await-lock not mandatory. Both are CONTRACT-shaping. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all new branches — `lock` (success/json/already_locked/layers_invalid), `init --await-lock`,
the `_setup_locked` predicate, and the three gates (new-task / advance / gate) in both states.
Plan (one test per scenario) lives in `add-method/tooling/test_setup_lock.py` — `import add`, the shared
`_run(argv)` capture helper, temp project via `add.main(["init", ...])`. Asserts behavior via state.json
+ exit code + stderr code, never internals.

Tests live in: `add-method/tooling/test_setup_lock.py` · MUST run red (lock subcommand + gating absent) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): `lock` is ONE atomic `save_state` (no partial lock). Edits land in the
canonical `add-method/tooling/add.py`, then sync to `.add/tooling/add.py` + `src/add_method/_bundled/` so
`test_bundle_parity` / tree-parity stay green. Grandfather path must leave plain-init behavior byte-for-byte.
Code lives in: `add-method/tooling/add.py` (+ synced copies)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib: getpass); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `Ran 310 tests … OK`; the 11 new `test_setup_lock` scenarios all green;
      `test_plain_init_is_grandfathered` proves plain-init is byte-for-byte non-breaking.
- [x] coverage did not decrease — every new branch is exercised AND asserted: `cmd_lock` (success / --json /
      already_locked / layers_invalid / grandfathered+--force), `init --await-lock`, the `_setup_locked` predicate,
      and all three gates (new-task 2nd / advance into build / gate) in both locked & unlocked states. The FROZEN
      text format and the `getpass` default `locked_by` are now pinned by assertion (closed pre-gate, not just run).
- [~] no test or contract was altered during build — **DISCLOSED DEVIATION (not a silent pass).** §3 (frozen
      contract) and `test_setup_lock.py` (this task's tests) were NOT touched. I DID add one line to a *different*,
      pre-existing meta-test, `test_min_pillar.py`: `["lock","--force"]` into its LIFECYCLE list. That test is a
      self-maintaining coverage registry whose own docstring says *"A new subcommand fails this until it is
      classified here (exercised or excluded)"* — so the edit is the intended maintenance, and it *adds* scrutiny
      (subjects `lock` to the read-spy proving it reads no `docs/`). It weakens no assertion. Flagged for the human.
- [x] concurrency / timing safe — `lock` is ONE atomic `save_state` (`_atomic_write` = temp + `os.replace`); layers
      are parsed and validated BEFORE the write, so an invalid request never half-locks. No partial lock state.
- [x] no exposed secrets, injection openings, or unexpected dependencies — only new import is `getpass` (stdlib,
      allow-listed in §5); `--layers` is split on comma into a plain string list, never eval'd; no secrets.
- [x] layering & dependencies follow CONVENTIONS.md — stdlib-only; 3-tree parity verified by md5
      (`add-method/tooling/add.py` == `.add/tooling/add.py` == `_bundled/tooling/add.py`); `test_bundle_parity` green.
- [x] a person reviewed and approved the change — Tin, 2026-06-04 (gate PASS)   <!-- autonomy: conservative — REQUIRED, no auto-PASS -->

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-04
Note: disclosed deviation accepted — one line added to the self-maintaining `test_min_pillar.py` coverage
registry (classifies the new `lock` subcommand; adds read-spy scrutiny, weakens no assertion). §3 frozen
contract and `test_setup_lock.py` were untouched. 310/310 tests green; 3-tree md5 parity.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): rate of `setup_unlocked` refusals (are users hitting the gate as expected?)
Spec delta for the next loop: <what dogfooding the lock taught>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
