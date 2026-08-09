# TASK: consolidated parity audit + multi-active invariant hardening

slug: engine-repin-parity · created: 2026-06-22 · stage: mvp · risk: high
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
- NEW `add-method/tooling/test_engine_repin_parity.py` — the consolidated audit + invariant guard. NO engine edit: tasks 1–4 already re-pinned (current ENGINE_MD5 `fa8e981875354468ad426b8012e11689`), so this task AUDITS that the pin is current across all 3 copies and HARDENS the suite to lock the multi-active behavior into the parity backstop.
- `add-method/tooling/engine_pin.py:ENGINE_MD5` — the single-source literal pin (read, not changed).
- 3 engine copies: `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py`.
- existing parity guards reused as the model: `test_shared_engine_pin.py` (single-source pin → 3 copies) · the per-task `test_three_trees_byte_identical_and_pinned` duplicates.
- engine seams the invariants exercise (already built + pinned): born-migrated `cmd_init` (active_milestones list + active_tasks dict) · `_migrate_state` on the load + json-load seams (idempotent, derives the SET from the scalar) · `activate`/`deactivate` verbs · the `streams :` render in `cmd_status`.

Context (working folder):
- VERIFIED before drafting: init is born-migrated; a legacy state (stripped of the new keys) re-derives active_milestones from the scalar on a read-only `status --json` AND on any save command; the parser exposes activate + deactivate.
- test-only task → no 3-tree edit, no re-pin; the pin STAYS `fa8e9818` and this audit asserts it is current.

Honors (patterns / conventions):
- the pin is a literal, never recomputed (a recomputed pin is vacuous — test_shared_engine_pin's rule); the audit reads `engine_pin.ENGINE_MD5` and compares to each live copy.
- a parity guard must lock BEHAVIOUR, not just bytes — byte-identity + pin currency prove the 3 copies match, but NOT that they still contain the multi-active feature; the hardening adds behavioral round-trips so a future refactor that keeps the copies identical+pinned yet drops the feature goes red.
- backstop/characterization tests: green against the correct engine, each PROVEN to bite under the specific regression it guards (demonstrated by a transient mutation at build).

Anchors the contract cites: the 3 engine copies · `engine_pin.ENGINE_MD5` · born-migrated `cmd_init` · `_migrate_state` (load + json seams, idempotent) · the `activate`/`deactivate` parser choices · the `streams :` render.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A single consolidated parity-AUDIT + invariant guard suite that (a) proves the engine edits of tasks 1–4 are PINNED not bypassed (3 copies byte-identical AND equal to the single-source ENGINE_MD5), and (b) HARDENS the parity backstop to assert the multi-active invariants survive in the pinned engine — so the milestone's integrity exit-criterion ("the engine edit is pinned, not bypassed; the parity test asserts the new multi-active invariants") is mechanically enforced.
Framings weighed: a new dedicated guard suite (chosen — one authoritative home for the consolidated audit + the behavioral invariants; additive, no engine edit, no churn to the per-task pin duplicates) · delete + merge every per-task `test_three_trees_…` duplicate into one (rejected — needless churn across 4 task suites; each red suite legitimately owns its own pin check; consolidation = one authoritative ADD, not a delete sweep) · add the invariants into test_shared_engine_pin (rejected — that suite's charter is the single-source pin mechanism; behavioral multi-active round-trips belong in their own milestone-scoped guard).
Must:
<must>
  - AUDIT: all 3 add.py copies are byte-identical AND each equals `engine_pin.ENGINE_MD5` (the pin is CURRENT — the edit is pinned, not bypassed). Fails loud naming any drifted copy.
  - HARDEN — born-migrated: a fresh `init` writes `active_milestones` (list) + `active_tasks` (dict) into state.json.
  - HARDEN — migration: a legacy single-active state (no new keys) re-derives `active_milestones` from the scalar on load (asserted via the read-only `status --json` seam); re-running the migration is a no-op (idempotent).
  - HARDEN — verbs + render round-trip: from 2 milestones, `activate` reaches N≥2 and `status` shows the `streams :` block; `deactivate` shrinks back to N=1 and the block disappears (ties tasks 3 + 4).
  - HARDEN — parser surface: `build_parser()` exposes the `activate` AND `deactivate` choices.
  - Test-only: NO engine edit, NO re-pin; the suite is green against the correct engine and each guard is PROVEN to go red under the regression it guards (transient-mutation demonstration recorded at verify).
</must>
Reject:
<reject>
  - (none — this is a guard/audit suite, not a command; it has no runtime input to reject. The "negative" cases are the drift/regression scenarios each guard turns red on, demonstrated at build.)
</reject>
After:
<after>
  - The milestone ships with a single authoritative guard that fails the instant (a) any engine copy drifts from the pin, or (b) the multi-active behavior (born-migrated init · idempotent migration · activate/deactivate · streams render · the parser verbs) regresses — so the integrity exit-criterion is mechanically enforced, not asserted by hand.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Consolidation = ADD one authoritative guard, NOT delete the per-task `test_three_trees_…` duplicates. Lowest confidence because "consolidated" could be read as "merge + remove"; chosen ADD-only to avoid churning 4 task suites + re-anchoring their snapshots for zero behavioral gain (each per-task pin check is a legitimate member of that task's red suite). If wrong: a follow-up delete-sweep is mechanical and low-risk.
  - [ ] The migration assertion uses the read-only `status --json` seam (verified to migrate) rather than a save command, to prove the load seam itself migrates. Confirm at freeze.
  - [ ] Idempotency is asserted by migrating twice and comparing the derived shape is stable (not by inspecting `_migrate_state` internals). Confirm at freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: The pin is current across all three copies
  Given the three add.py copies and the single-source ENGINE_MD5
  When the audit runs
  Then every copy's md5 equals ENGINE_MD5 (the edit is pinned, not bypassed)

Scenario: A drifted copy fails the audit (the guard bites)
  Given one engine copy mutated by a byte
  When the audit runs
  Then it fails naming the drifted copy

Scenario: init is born-migrated
  Given a fresh `init`
  When state.json is read
  Then it has active_milestones (a list) AND active_tasks (a dict)

Scenario: A legacy state migrates on the read-only json seam, idempotently
  Given a state with the new keys stripped (scalar active_milestone only)
  When `status --json` runs twice
  Then both runs report active_milestones derived from the scalar AND the two derived shapes are identical

Scenario: activate/deactivate round-trips through the streams render
  Given a project with milestones m1 and m2
  When `activate m1` then `status`
  Then status shows "streams :" with both active
  And after `deactivate m1` then `status` the "streams :" block is gone

Scenario: the parser exposes the multi-active verbs
  Given build_parser()
  Then its subcommand choices include activate AND deactivate

Scenario: a removed multi-active feature fails the hardening (the guard bites)
  Given the engine with active_milestones stripped from init (a simulated regression)
  When the born-migrated guard runs
  Then it fails
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# Consolidated parity audit + multi-active invariant guard (test-only — NO engine edit)

NEW add-method/tooling/test_engine_repin_parity.py

class ParityAudit:
  test_three_engines_byte_identical_and_current:
    for p in (tooling/add.py, .add/tooling/add.py, src/.../_bundled/tooling/add.py):
       md5(p) == engine_pin.ENGINE_MD5            # byte-identical AND the pin is CURRENT
  test_audit_bites_on_drift:
    copy bytes, flip one, assert the equality check would fail (in-memory, no file mutation persisted)

class MultiActiveInvariants:   (drive the real CLI in a tmp project)
  test_init_born_migrated:        init -> state.json has active_milestones:list AND active_tasks:dict
  test_legacy_migrates_idempotent: strip the new keys -> `status --json` derives active_milestones
                                   from the scalar; a 2nd `status --json` derives the SAME shape
  test_activate_deactivate_streams_roundtrip:
                                   2 milestones -> activate -> status has "streams :" (both active)
                                   -> deactivate -> status has NO "streams :"
  test_parser_exposes_verbs:      build_parser() subcommand choices ⊇ {activate, deactivate}
  test_hardening_bites_on_feature_removal:
                                   demonstrate (transient) that stripping active_milestones from
                                   init turns test_init_born_migrated red

Invariant: test-only; the pin stays fa8e9818; the suite is GREEN against the correct engine and
  each guard is proven to bite under its specific regression.
No engine edit · no re-pin · no reject codes (guard suite).
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-22; auto-mode standing authorization; multi-active foundation 5/5; consolidate = ADD one authoritative guard · migration asserted via the read-only json seam · idempotency by stable-derived-shape)
Least-sure flag surfaced at freeze: [contract] consolidation is ADD-one-authoritative-guard, NOT delete the four per-task `test_three_trees_…` duplicates — chosen to avoid churning + re-anchoring 4 task suites for zero behavioral gain (each per-task pin check legitimately belongs to its own red suite). If a single home is later wanted, the delete-sweep is mechanical/low-risk. Second flag: [test] the guard suite is green-on-correct-engine (an audit/backstop, not feature TDD) — TDD honesty is preserved by proving each guard bites under a transient mutation, recorded at verify.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the consolidated audit (3-tree byte-identity + pin currency) + the 5 multi-active invariants; each guard proven to bite under its regression (transient mutation).
Plan (one test per scenario; guard suite — green on the correct engine, red under the guarded regression):
<test_plan>
  - test_three_engines_byte_identical_and_current: md5 of each of the 3 copies == engine_pin.ENGINE_MD5
  - test_audit_bites_on_drift: a flipped byte makes the equality fail (in-memory)
  - test_init_born_migrated: init → active_milestones is list, active_tasks is dict
  - test_legacy_migrates_idempotent: strip keys → status --json derives the SET; 2nd run identical
  - test_activate_deactivate_streams_roundtrip: activate→"streams :" present; deactivate→absent
  - test_parser_exposes_verbs: build_parser choices ⊇ {activate, deactivate}
  - test_hardening_bites_on_feature_removal: a simulated init without active_milestones fails the born-migrated guard (transient demonstration, restored)
</test_plan>

Tests live in: `add-method/tooling/test_engine_repin_parity.py` · MUST run green on the correct engine AND each guard proven red under its regression before Build closes.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/test_engine_repin_parity.py`
Strategy (ordered batches): 1. write the audit class (3-tree byte-identity + pin currency). · 2. write the 5 multi-active invariant guards driving the real CLI in a tmp project. · 3. run green; then transiently mutate (a flipped engine byte · a stripped init key) to PROVE two representative guards bite; restore. · 4. full suite green.
Safety rule (feature-specific): test-only — touch NO engine copy, NO engine_pin.py; any mutation used to prove a guard bites is in-memory / restored, never committed.
Code lives in: `add-method/tooling/test_engine_repin_parity.py`
Constraints: do NOT change any engine file or the pin; stdlib only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1420→1427 green; new test_engine_repin_parity.py [7] green
- [x] coverage did not decrease — +7 guard tests; +1 active_tasks-derivation assertion (review Finding 4)
- [x] no FROZEN CONTRACT altered — §3 untouched; test-only task (NO engine edit, NO re-pin); the 2 docstring-honesty + 1 assertion edits are post-review NIT closures within the new file, declared in §5 Scope
- [x] the green was EARNED, not gamed — independent python-expert adversarial refute-read (0.93) verdict MERGE, 0 blocking; it confirmed no test stays green while its named invariant regresses; its 2 over-claim NITs + 1 derivation NOTE were closed; the FILE-level audit guard was proven to bite on real drift out-of-band (restored byte-for-byte)
- [x] concurrency / timing — N/A (guard suite; in-proc CLI in isolated tmp dirs)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — reuses the single-source ENGINE_MD5 literal + the established 3-copy paths + tmp-CLI idiom
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization) after the independent review + NIT closure

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] the audit asserts each of the 3 copies equals the single-source ENGINE_MD5 (pin current = fa8e9818) — confirmed by test_three_engines_byte_identical_and_current
- [x] the multi-active behavior is locked: born-migrated init · idempotent load-seam migration (incl. active_tasks derivation) · activate/deactivate→streams round-trip · the two parser verbs — confirmed by the 4 invariant guards
- [x] each guard BITES under its regression — confirmed by the transient real-file flipped-byte run (audit went FAILED "engine copies diverged", then restored byte-for-byte to fa8e9818) + the in-memory predicate demonstrations
- [x] the milestone integrity exit-criterion is now MECHANISED — one suite proves "3 copies byte-identical AND pin current AND the multi-active invariants present"

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every guard references a real engine seam: the 3 add.py paths · engine_pin.ENGINE_MD5 · cmd_init/state.json · the status --json load seam · build_parser choices · the activate/deactivate/status verbs; no dead helper
- [x] DEAD-CODE (code) — no orphaned symbol; the transient real-file demonstration was out-of-band and restored (md5 re-verified fa8e9818); nothing left behind in the committed suite
- [x] SEMANTIC (prose / non-code) — re-read the MILESTONE exit-criterion ("All THREE add.py copies stay byte-identical and ENGINE_MD5 is current and green; the parity test asserts the new multi-active invariants"); the ParityAudit + MultiActiveInvariants classes map 1:1 to it

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22
Evidence: full suite 1427 green · new guard suite test_engine_repin_parity.py [7] · dogfood check 405/0 · audit clean · pin current fa8e9818 across all 3 copies (test-only task: no engine edit, no re-pin) · the file-level audit guard proven to bite on real drift then restored. Independent python-expert adversarial review (0.93) MERGE, 0 blocking — confirmed non-vacuous; its 2 docstring over-claims + 1 derivation NOTE closed. No frozen contract altered; no test weakened.

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
- [TDD · folded] a byte-identity + pin guard proves the copies MATCH, not that they still DO anything — a parity backstop for a feature must also assert the feature's BEHAVIOR survives (born-migrated init · migration · the verbs · the render), else a refactor can keep 3 files identical+pinned while silently dropping the feature (evidence: this task's hardening guards exist precisely to close that blind spot) [folded foundation-version 41]
- [ADD · folded] a backstop/audit task is honest TDD when each guard is PROVEN to bite under the regression it names — green-on-correct-engine is fine IF the bite is demonstrated (transient real-file drift for the file guard; in-memory predicate for the rest), not assumed (evidence: independent review flagged the 2 in-memory "bites" tests as demonstrations-not-guards until the docstrings named the scope + the out-of-band real-drift proof was recorded) [folded foundation-version 41]
