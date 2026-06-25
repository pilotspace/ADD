# TASK: F4: cmd_phase build must refuse an unfrozen contract (heal-loop exempt)

slug: phase-build-guard · created: 2026-06-25 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py:cmd_phase` (1200–1211) — the `phase` CLI handler. Sets `state["tasks"][slug]["phase"] = args.phase` directly, with NO tests→build guards. THE FIX SITE.
  - `add-method/tooling/add.py:cmd_advance` (1214–1355) — the guarded crossing. At `nxt == "build"` it computes `_optin` (milestone `await_confirm`) and reads `task.fast`; `_freeze_gated = _optin or fast`; refuses `contract_not_frozen` when `_freeze_gated and not _contract_frozen(raw3)`. The behavior cmd_phase must mirror.
  - `add-method/tooling/add.py:_contract_frozen(raw3) -> bool` (5013–5016) — reads §3 `Status: FROZEN` (fail-closed to DRAFT). The freeze predicate.
  - `add-method/tooling/add.py:_raw_phase_bodies(root, slug) -> dict[int,str]` (4737) — returns §N bodies; `.get(3,"")` is `raw3`.
  - `add-method/tooling/add.py:_heal_or_escalate` (4482–4516) — sets `t["phase"] = "build"` DIRECTLY (never via cmd_phase) → the heal loop is EXEMPT by construction; no special-casing needed.
Context (working folder):
  - `add-method/tooling/test_freeze_before_build_gate.py` — the harness the new red test mirrors (opted-in vs plain vs no-milestone fixtures; `_die_stderr` / `_freeze`).
  - 24 existing `test_*.py` call `phase build` on plain/draft tasks (e.g. test_add.py:132, test_argv_portability.py:161) — the guard MUST NOT ripple onto them.
  - Engine is mirrored ×3 (`.add/tooling/` dogfood · canonical `add-method/tooling/` · `_bundled/tooling/`) under an ENGINE_MD5 pin + parity tests — the build edits canonical, re-mirrors, re-pins.
Honors (patterns / conventions):
  - Reuse the EXISTING `contract_not_frozen` reject code (ubiquitous language — no new code for the same condition).
  - Validate-then-write / fail-closed: refuse BEFORE any state mutation; a refused `phase build` leaves phase unchanged.
  - Mirror-3-trees + ENGINE_MD5 re-pin on any add.py edit (CONVENTIONS.md engine-pin convention).
  - Red/green TDD.
Anchors the contract cites: `cmd_phase` · `cmd_advance` · `_contract_frozen` · `_freeze_gated` (the `_optin or fast` condition) · reject code `contract_not_frozen`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py phase build` must run the SAME build-entry guards as `add.py advance` — the admin override may not be a backdoor around the freeze gate, the flag check, OR the tamper-tripwire / scope snapshots.
Framings weighed: shared-build-entry-helper (chosen) · freeze-check-only · forbid-`phase build`-entirely
  - chosen: extract cmd_advance's `nxt == "build"` guard+snapshot block into a shared helper `_build_entry(root, state, slug)`; BOTH cmd_advance and cmd_phase call it when entering build. `phase build` becomes EQUIVALENT to advancing into build — no divergence to reason about, and the altitude question dissolves (cmd_phase inherits advance's exact rules).
  - freeze-check-only: the earlier draft — closes the freeze hole but leaves the tripwire/flag/scope holes open (verify's tamper guard still returns silently). Rejected on the human's direction to fold the tripwire gap in.
  - forbid-`phase build`: makes cmd_phase refuse the build target outright (use advance). Rejected — removes the admin override and breaks the 24 usages hardest.
Must:
<must>
  - Setting a task to `build` via `cmd_phase` runs the identical build-entry block cmd_advance runs at `nxt == "build"`: the freeze gate, the build-expectations gate, the unflagged_freeze check + `flag_verified` stamp, the tamper-tripwire snapshot, AND the §5 scope snapshot.
  - A freeze-gated task (`_optin or fast`) with a DRAFT §3 is refused `contract_not_frozen` — validate-then-write: phase marker + state.json unchanged (no tripwire/scope written on a refusal).
  - Entering build via `phase build` writes the SAME `tripwire` baseline advance writes, so verify's `_tamper_guard` is effective on a cmd_phase-entered build (closes the silent-pass hole F4 named).
  - cmd_advance's externally-observable behavior is byte-unchanged (the extraction is a pure refactor; its existing suites stay green).
  - The guard runs ONLY for the `build` target; other `phase <x>` targets are unchanged.
  - The heal loop (`_heal_or_escalate`, sets phase=build directly) never routes through cmd_phase — exempt by construction.
</must>
Reject:
<reject>
  - freeze-gated task + DRAFT §3 + `phase build` -> "contract_not_frozen"
  - frozen-but-unflagged §3 + `phase build` -> "unflagged_freeze"
</reject>
After:
<after>
  - No engine path (`advance` OR `phase build`) reaches build without the freeze/flag gates (for gated tasks) and the tamper-tripwire baseline (all tasks) — `phase build` is exactly as safe as `advance`.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The shared `_build_entry` helper carries cmd_advance's tripwire+scope snapshots UNCONDITIONALLY (as advance does today), so the 24 plain-task `phase build` usages now also get a tripwire/scope snapshot — lowest confidence because some of those tests may assert exact state.json or a sidecar's absence and flip red. If wrong: each is a contained fix (freeze §3 first, or update the assertion) discovered green/red at build — I'll report the count, never weaken a test to hide it.
  - [x] The heal loop is exempt purely because it sets phase directly (`_heal_or_escalate` line 4511) — confirmed.
  - [x] Extracting advance's build block is behavior-preserving for advance (existing advance suites are the guard) — confirmed by the test plan.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: freeze-gated task with a DRAFT contract is refused
  Given an --await-confirm milestone with a task at phase=tests and §3 Status: DRAFT
  When I run `add.py phase build <slug>`
  Then it exits 1 with "contract_not_frozen"
  And the task's phase marker stays "tests" and state.json is unchanged

Scenario: freeze-gated task with a FROZEN (flagged) contract advances AND snapshots the tripwire
  Given an --await-confirm milestone with a task at phase=tests and §3 Status: FROZEN @ v1 (flagged)
  When I run `add.py phase build <slug>`
  Then the task's phase becomes "build"
  And state.tasks[slug].tripwire is now present (verify's tamper guard is armed)
  And state.tasks[slug].flag_verified is true

Scenario: frozen but unflagged contract is refused
  Given a freeze-gated task at phase=tests with §3 FROZEN but no least-sure flag
  When I run `add.py phase build <slug>`
  Then it exits 1 with "unflagged_freeze"
  And the task's phase marker stays "tests"

Scenario: plain-milestone task with a DRAFT contract enters build with a tripwire (as advance does)
  Given a milestone WITHOUT --await-confirm, a task at phase=tests and §3 Status: DRAFT
  When I run `add.py phase build <slug>`
  Then the task's phase becomes "build" (the freeze gate does not fire — not gated)
  And state.tasks[slug].tripwire is present (same baseline advance writes)

Scenario: fast task with a DRAFT contract is refused
  Given a --fast task at phase=tests and §3 Status: DRAFT (under any milestone)
  When I run `add.py phase build <slug>`
  Then it exits 1 with "contract_not_frozen"
  And the task's phase marker stays "tests"

Scenario: a non-build phase target is never gated
  Given a freeze-gated task with a DRAFT §3
  When I run `add.py phase scenarios <slug>`
  Then the phase becomes "scenarios" with no freeze check
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# NEW shared helper — the single build-entry guard+snapshot block, extracted verbatim
# from cmd_advance's `nxt == "build"` body (behavior-preserving for advance):
_build_entry(root, state, slug):
    raw3          = _raw_phase_bodies(root, slug).get(3, "")
    _freeze_gated = _optin(state, slug) or tasks[slug].get("fast") is True
    if _freeze_gated and not _contract_frozen(raw3): _die("contract_not_frozen")   # exit 1, no write
    if _optin and _section_unfilled(§6, "### Build expectations"): _die("build_expectations_unfilled")
    if _contract_frozen(raw3):
        if not _flag_well_formed(raw3): _die("unflagged_freeze")
        tasks[slug].flag_verified = True
    tasks[slug].tripwire = _tripwire_snapshot(root, slug, raw3)     # arm verify's tamper guard
    <§5 scope snapshot — declared ? write sidecar + anchor : clean stale>   # unchanged from advance

cmd_advance(...)   # at nxt == "build": calls _build_entry(root, state, slug) in place of the inline block
cmd_phase(args)    # at args.phase == "build": calls _build_entry(root, state, slug) BEFORE setting phase
  ok   -> phase set; marker synced; "task '<slug>' phase -> build" (+ tripwire/flag/scope written)
  4xx  -> _die "contract_not_frozen" | "unflagged_freeze" | "build_expectations_unfilled"
          (only on the build target; validate-then-write — a refusal writes NOTHING)
Exemption: _heal_or_escalate sets phase=build directly (never via cmd_phase) — structurally unaffected.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25.
Least-sure flag surfaced at freeze: [scope] `_build_entry` carries advance's tripwire+scope snapshots UNCONDITIONALLY, so the 24 plain-task `phase build` usages now also get a tripwire/scope snapshot — a few may assert exact state.json / a sidecar's absence and flip red. Cost: each is a contained, honest fix (freeze §3 first, or update the assertion) found at build via green/red — I report the count, never weaken a test to hide it. [test] the extraction must leave cmd_advance byte-equivalent — its existing suites are the guard.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject (5 scenarios).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_optedin_unfrozen_blocks_phase_build: opted-in + DRAFT §3 / `phase build t` / exit 1 + "contract_not_frozen" + phase stays "tests" + NO tripwire written
  - test_optedin_frozen_phase_build_arms_tripwire: opted-in + FROZEN+flagged §3 / `phase build t` / phase == "build" + state.tripwire present + flag_verified true
  - test_unflagged_freeze_blocks_phase_build: opted-in + FROZEN but unflagged §3 / `phase build t` / exit 1 + "unflagged_freeze" + phase stays "tests"
  - test_plain_milestone_unfrozen_arms_tripwire: plain milestone + DRAFT §3 / `phase build t` / phase == "build" (no freeze gate) + state.tripwire present (same baseline advance writes)
  - test_fast_unfrozen_blocks_phase_build: `--fast` task + DRAFT §3 / `phase build t` / exit 1 + "contract_not_frozen"
  - test_non_build_target_never_gated: opted-in + DRAFT §3 / `phase scenarios t` / phase == "scenarios", no check, no tripwire
  - test_advance_into_build_unchanged: parity guard — `advance` into build still writes tripwire/flag exactly as before (the extraction is behavior-preserving)
</test_plan>

Tests live in: `add-method/tooling/test_phase_build_guard.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_phase_build_guard.py`   <!-- canonical engine + bundled mirror + the single-source ENGINE_MD5 pin (engine_pin.py) + the new test; the dogfood .add tree is mirrored too but pruned from the scope walk (_SCOPE_EXCLUDE_DIRS), so it needs no token -->
Strategy (ordered batches): 1. add the `args.phase == "build"` freeze guard in `cmd_phase` (canonical add.py). 2. green the new test. 3. mirror canonical → `.add/tooling/` + `_bundled/tooling/` and re-pin ENGINE_MD5; confirm `test_book/bundle/engine` parity + full suite green.
Safety rule (feature-specific): validate-then-write — the `_die` precedes every state mutation, so a refused `phase build` leaves phase + state.json byte-unchanged.
Code lives in: `add-method/tooling/add.py` (+ its two mirrors)
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

- [x] all tests pass — full suite 1780/0 after mirror + re-pin
- [x] coverage did not decrease — +7 new behavioral tests (test_phase_build_guard), no test removed
- [x] no test or contract was altered during build — §3 frozen + §4 tests untouched since the tripwire snapshot
- [x] the green was EARNED, not gamed — refute-read (inline): the 7 asserts check real outputs (exit code, error string, `phase` marker, `tripwire`/`flag_verified` keys), not constants or mocks; the plain-task test asserts the tripwire IS armed (the actual gap closed), and test_advance_into_build_unchanged proves the extraction didn't silently drop advance's behavior — no overfit, no vacuous assert
- [x] concurrency / timing of the risky operation is safe — pure single-process state mutation; validate-then-write (`_die` precedes any write) so a refusal is atomic
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports; reuses existing helpers only
- [x] layering & dependencies follow CONVENTIONS.md — extraction preserves the engine's NO-EXEC contract (engine records, never runs a suite); 3-tree mirror + ENGINE_MD5 re-pinned
- [x] a person reviewed and approved the change — Tin Dang approved the frozen §3 contract (v1) and directed the folded scope

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py phase build` on a freeze-gated DRAFT task exits 1 with `contract_not_frozen` and leaves phase=tests — confirmed by test_optedin_unfrozen_blocks_phase_build (green) + test_fast_unfrozen_blocks_phase_build
- [x] `add.py phase build` arms `state.tasks[slug].tripwire` (so verify's `_tamper_guard` bites) for BOTH a frozen gated task AND a plain task — confirmed by test_optedin_frozen_phase_build_arms_tripwire + test_plain_milestone_unfrozen_arms_tripwire
- [x] `add.py advance` into build is byte-behaviour-unchanged — confirmed by test_advance_into_build_unchanged + the 53 engine-pin/parity suites green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the new `_build_entry` is referenced by exactly two call sites: `cmd_phase` (when `args.phase == "build"`) and `cmd_advance` (at `nxt == "build"`); confirmed by grep + the green suite exercising both paths
- [x] DEAD-CODE (code) — no orphan introduced: the extracted block REPLACED cmd_advance's inline body (no duplication); the old inline statements no longer exist
- [x] SEMANTIC (prose / non-code) — read the engine_pin.py re-aim note + this TASK.md in full: the pin history records the extraction faithfully; the §1 flag and §3 contract match the shipped behaviour

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

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
