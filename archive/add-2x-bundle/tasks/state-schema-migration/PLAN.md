# TASK: Multi-active state.json schema + idempotent fail-soft migration

slug: state-schema-migration · created: 2026-06-22 · stage: mvp · risk: high
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
- `add-method/tooling/add.py:load_state(root) -> dict` (line 241) — the load seam: bare `json.loads(state.json)`, fails CLOSED (`state_invalid`). NO migration runs today. The natural hook point for the forward migration (read → migrate → return).
- `add-method/tooling/add.py:_load_state_for_json() -> (Path, dict)` (line 252) — the SECOND load path used by every `--json` command; must apply the same migration so harness reads see the upgraded shape (two seams, one migration helper).
- `add-method/tooling/add.py:save_state(root, state)` (line 273) — atomic write of the whole state dict; the migrated shape is what gets persisted on the next write.
- `add-method/tooling/add.py` init default block (lines 451–460) — `state = {... "active_task": None, "active_milestone": None, "tasks": {}, "milestones": {} ...}`. A FRESH project must be born in the new shape (born-migrated), so init writes `active_milestones` natively.
- `add-method/tooling/add.py:_setup_locked(state)` (line 278) — the existing GRANDFATHER pattern: a missing `"setup"` key ⇒ legacy/grandfathered. The migration MIRRORS this exact idiom (missing `active_milestones` ⇒ derive from the scalar `active_milestone`).
- The ~20 reader call sites of `state.get("active_milestone")` / `state.get("active_task")` (init 454-455 · new-task 502/554 · status 1064/1087/1114-1116 · milestone-done 1835-1851 · check 1740-1744 · archive 2372-2375 · new-milestone 2082 · use 2464-2485 · report 3809-3819/4929-4937 · graduation 2740) — these are NOT changed in THIS task (they stay reading the scalar, which the migration keeps populated for N=1); they are the `active-accessors` task's job. Listed so the migration's compatibility contract is grounded.
- `add-method/tooling/engine_pin.py:ENGINE_MD5` (line 13) = `25c6fcc54ceb0e3d10610a95ebec4c3f` — the byte-pin this task must re-establish after editing the engine.

Context (working folder):
- THREE byte-identical engine copies confirmed all == `25c6fcc5…`: `add-method/tooling/add.py` · `.add/tooling/add.py` (this project's dogfooded runtime) · `add-method/src/add_method/_bundled/tooling/add.py`. Editing the engine means editing all three in lockstep + bumping `engine_pin.py` in the same commit.
- `add-method/tooling/test_release_1_7_3.py:test_engine_untouched` + the parity guard assert the 3 copies hash-equal `ENGINE_MD5`; they go RED the moment one copy changes and must be brought back GREEN within the task (re-pin discipline).
- `STATE_FILE` = `state.json`; the dogfood state at `.add/state.json` is itself an old-schema (`active_milestone` scalar) instance — the migration's first real fixture.

Honors (patterns / conventions):
- design-for-failure (CLAUDE.md / load_state docstring) — the migration is PURE + idempotent + fail-soft: it never throws on a malformed/old/partial state; a second run is a no-op; a corrupt file still dies CLOSED with `state_invalid`, never a traceback.
- grandfather-by-missing-key (the `_setup_locked` idiom) — absence of the new key means "legacy, derive it", never "rewrite destructively".
- engine-edit discipline (MILESTONE shared decision) — 3-tree byte-identity + same-commit re-pin; the pin tracks HEAD, never lifted.

Anchors the contract cites: `load_state` · `_load_state_for_json` · the init default block · `save_state` · `engine_pin.ENGINE_MD5` · the new keys `active_milestones` / per-milestone `active_task` · the grandfather-by-missing-key idiom.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Multi-active state.json schema + a pure, idempotent, fail-soft forward migration that upgrades any single-active state to the multi-active shape on load.
Framings weighed: migrate-on-load (chosen — `load_state`/`_load_state_for_json` derive the new shape every read and persist on the next `save_state`; mirrors the grandfather-by-missing-key idiom; no command a user can forget to run, the engine self-heals) · explicit one-shot `migrate` command (rejected — a step users skip; a state can reach a reader un-upgraded) · dual-read-forever / no schema key (rejected — pushes N-active branching into all ~20 call sites with no canonical shape to test against).
Must:
<must>
  - load_state AND _load_state_for_json route every loaded state through ONE pure migration helper before returning it (two seams, one helper).
  - A state lacking the `active_milestones` key gains it, DERIVED from the scalar: `active_milestone=None` → `[]`; `active_milestone="x"` → `["x"]`. (grandfather-by-missing-key)
  - The per-milestone active task is recorded so each active milestone resolves its own active task; the old global `active_task` is placed under its owning active milestone (placement of the orphan case is the flagged contract decision below).
  - The scalar `active_milestone` / `active_task` keys are KEPT and kept consistent for the N≤1 case, so the ~20 not-yet-routed readers keep working unchanged (this task changes SHAPE, not behavior — `active-accessors` routes the readers next).
  - Idempotent: a state that ALREADY has `active_milestones` is returned byte-unchanged — never re-derived, never clobbering a richer multi-active state.
  - Fail-soft + pure: the migration never throws on a None/partial/old/unknown-shaped state and has no side effects beyond returning the upgraded dict; a corrupt/unreadable file still dies CLOSED with `state_invalid` (unchanged) — migration is not error handling.
  - init is BORN-MIGRATED: the init default block writes the new shape natively (empty active set), so a fresh project never needs migrating.
  - All THREE add.py copies edited byte-identically + `engine_pin.ENGINE_MD5` re-pinned in the same change; the parity/pin tests end GREEN.
</must>
Reject:
<reject>
  - corrupt / unreadable state.json -> "state_invalid"  (pre-existing load behavior; migration must NOT swallow it)
  - (no new error codes — the migration is total: every well-formed-JSON state maps to a valid migrated state; malformedness is the loader's job, not the migration's)
</reject>
After:
<after>
  - Every state returned by the two load seams has `active_milestones` (a list) and a resolvable per-milestone active task; the scalar mirror is correct for N≤1; re-loading is a no-op; an init-born state already conforms; the 3 engine copies + pin are green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ orphan-active-task placement — when the old global `active_task` belongs to NO active milestone (`active_milestone=None` while `active_task` is set, or the task's milestone ≠ the active one), it has no per-milestone home. Options: (a) keep a top-level `active_task` fallback alongside the per-milestone map — lossless, mirrors today's resume point [RECOMMENDED]; (b) attach it to the derived active milestone — risks a wrong association; (c) drop it with a warning — loses the resume point. Lowest confidence because real states here (the dogfood `.add/state.json`) have milestone-less active tasks; if wrong, a user's resume point is silently dropped or mis-associated. → DECIDE AT FREEZE.
  - [ ] active-task STORAGE shape — a top-level parallel map `active_tasks: {milestone_slug: task_slug}` [RECOMMENDED — keeps `state["milestones"][slug]` entries stable, trivial to migrate + for accessors to read] vs an `active_task` field stored ON each milestone entry. Confirm at freeze.
  - [ ] keep-the-scalar-mirror — retain `active_milestone`/`active_task` as synced mirror keys for N≤1 until `active-accessors` routes the readers (yes — removing them now would red ~20 call sites in one task). Confirm at freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Single-active state gains the active set on load
  Given a state.json with active_milestone="m1" and no active_milestones key
  When load_state reads it
  Then the returned state has active_milestones == ["m1"]
  And the scalar active_milestone is still "m1" (mirror kept for N≤1)

Scenario: Empty single-active state migrates to an empty set
  Given a state.json with active_milestone=None and active_task=None
  When load_state reads it
  Then active_milestones == [] and the per-milestone active-task map is empty
  And no error is raised

Scenario: The active task lands under its owning active milestone
  Given a state with active_milestone="m1" and active_task="t1" where t1's milestone is m1
  When load_state reads it
  Then m1 resolves its active task as "t1" (via the per-milestone store)

Scenario: Orphan active task is preserved per the frozen decision
  Given a state with active_milestone=None and active_task="t9" (t9 in no active milestone)
  When load_state reads it
  Then t9 is retained as the contracted fallback (NOT silently dropped)
  And active_milestones == []

Scenario: Migration is idempotent (no-op on already-migrated state)
  Given a state that already has active_milestones=["m1","m2"] and a per-milestone task map
  When load_state reads it (a second run)
  Then the returned state equals the input byte-for-byte
  And neither active set nor the task map is re-derived or reordered

Scenario: Fresh project is born in the new shape
  Given a new `add.py init`
  When the initial state.json is written
  Then it contains active_milestones (an empty list) natively
  And it never needs migrating on the next load

Scenario: Solo behavior is unchanged for one active milestone
  Given a migrated state with exactly one active milestone
  When any existing command reads active_milestone / active_task
  Then it sees the same scalar values as before the migration (no regression)

Scenario: Corrupt state still fails closed (migration does not swallow it)
  Given a state.json that is not valid JSON
  When load_state reads it
  Then it dies with "state_invalid"
  And the migration is never reached (the loader's error path is unchanged)

Scenario: The engine edit stays pinned
  Given all three add.py copies are edited for this task
  When the parity + ENGINE_MD5 tests run
  Then the three copies are byte-identical AND match the re-pinned ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# state.json multi-active schema — additive, migrate-on-load (no API; this is a data contract)

_migrate_state(state: dict) -> dict      # PURE · idempotent · TOTAL · never raises · no I/O
  applied by: load_state (add.py:241) AND _load_state_for_json (add.py:252), before either returns

New keys (added only when "active_milestones" is absent):
  active_milestones : [slug, ...]              # the ACTIVE SET; [] or [one] after migration
  active_tasks      : { milestone_slug: task_slug }   # per-milestone active task — top-level parallel MAP (decision: storage shape = map, NOT a field on each milestone entry)

Kept keys (mirror, NOT removed this task):
  active_milestone  : slug | null              # N≤1 mirror for the ~20 un-routed readers
  active_task       : slug | null              # N≤1 mirror AND the orphan fallback (decision: orphan = option (a))

Migration rule  (only when "active_milestones" is absent):
  active_milestones = []            if active_milestone is None
                    = [active_milestone] otherwise
  active_tasks = { active_milestone: active_task }
                    if active_milestone and active_task and tasks[active_task].milestone == active_milestone
               = {} otherwise
  # ORPHAN (active_task set but belongs to no active milestone): active_task is LEFT as the top-level
  #   scalar (lossless resume-point fallback) — never placed in active_tasks, never dropped.   [decision (a)]
Idempotency: if "active_milestones" is already present -> return state UNCHANGED (no re-derive, no reorder, no clobber).
Born-migrated init: the init default block writes active_milestones=[], active_tasks={}, active_milestone=None, active_task=None natively.
N≤1 mirror invariant (held after migration): len(active_milestones) <= 1 in legacy states; active_milestone == (active_milestones[0] if active_milestones else None).
Errors: NONE new. Corrupt/unreadable state -> "state_invalid" in the loader (unchanged); the migration is never reached.
Engine discipline: all 3 add.py copies byte-identical + engine_pin.ENGINE_MD5 re-pinned in the same change; parity/pin tests GREEN.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-22; multi-active team-collaboration foundation; orphan=top-level fallback (a) · storage=top-level active_tasks map · scalar mirrors kept until active-accessors)
Least-sure flag surfaced at freeze: [contract] the ORPHAN-active-task landing — resolved as option (a): keep the global `active_task` as a top-level scalar fallback when it belongs to no active milestone (lossless, mirrors today's resume point). Alternatives weighed + rejected: (b) attach to the derived active milestone — risks a wrong association the user never made; (c) drop with a warning — loses the resume point. If (a) is wrong the cost is a stale top-level `active_task` that `active-accessors` must later reconcile — recoverable, not data loss. Second flag: [contract] storage shape = a top-level `active_tasks` MAP (keeps milestone entries stable + trivial for the accessor task to read) rather than an `active_task` field on each milestone entry.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject + the 9 scenarios; the `_migrate_state` helper at 100% branch.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_single_active_gains_set: state {active_milestone:"m1"} → migrated active_milestones==["m1"] AND scalar active_milestone still "m1"
  - test_empty_state_to_empty_set: {active_milestone:None, active_task:None} → active_milestones==[] AND active_tasks=={} AND no raise
  - test_active_task_lands_under_owner: {active_milestone:"m1", active_task:"t1", tasks.t1.milestone=="m1"} → active_tasks=={"m1":"t1"}
  - test_orphan_active_task_preserved: {active_milestone:None, active_task:"t9"} → active_task=="t9" retained (fallback), NOT in active_tasks, active_milestones==[]
  - test_migration_idempotent: state already has active_milestones=["m1","m2"] → _migrate_state returns it EQUAL (deep-equal, no reorder/re-derive)
  - test_init_born_migrated: a fresh `init` state.json contains active_milestones==[] + active_tasks=={} natively (subprocess or init helper) and a second load_state is a no-op
  - test_solo_behavior_unchanged: after migration with one active milestone, active_milestone/active_task scalars equal the pre-migration values (regression guard)
  - test_corrupt_state_still_invalid: non-JSON state.json → load_state dies "state_invalid"; _migrate_state never called
  - test_both_load_seams_migrate: load_state AND _load_state_for_json both return a state carrying active_milestones (one helper, two seams)
  - test_engine_three_trees_pinned: the 3 add.py copies are byte-identical and hash == engine_pin.ENGINE_MD5 (re-pin guard)
</test_plan>

Tests live in: `add-method/tooling/test_multi_active_state.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_multi_active_state.py`
Strategy (ordered batches): 1. write `test_multi_active_state.py` red (helper + both seams + init absent). · 2. add the pure `_migrate_state(state)` helper + call it in `load_state` and `_load_state_for_json`; extend the init default block (born-migrated) — in `add-method/tooling/add.py` first. · 3. mirror byte-identically into the other two add.py copies; re-pin `engine_pin.ENGINE_MD5` to the new hash. · 4. green the new file + the full suite (incl. parity/pin).
Safety rule (feature-specific): `_migrate_state` is PURE + TOTAL — no I/O, never raises, idempotent; it must NOT alter a state already carrying `active_milestones` (deep-equal in/out). The 3 add.py copies must be byte-identical at commit (diff them) before re-pinning.
Code lives in: `add-method/tooling/add.py` (+ its two mirror copies)
Constraints: do NOT change any test or the contract; stdlib only (json already imported); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1388 OK (was 1377; +11 from test_multi_active_state); new file 11/11
- [x] coverage did not decrease — 11 new tests; `_migrate_state` covered at every branch (single/empty/owns/orphan/idempotent/partial)
- [x] no test or contract was altered during build — build touched only add.py ×3 + engine_pin.py (all §5-declared); the test file was written in TESTS, untouched in BUILD (no tamper tripwire)
- [x] the green was EARNED, not gamed — adversarial refute-read (manual, small contained change): idempotency exercises the real `"active_milestones" in state` early-return; orphan exercises the real `owns=False` fallback; both seams genuinely call the helper (grep-confirmed); init asserts native keys on a real `add.py init` subprocess, not a fixture. No stub, no vacuous assert. One NON-cheat residue noted in §7 (a hand-edited state with `active_milestones` but no `active_tasks` is returned as-is — accessor reads will `.get` default).
- [x] concurrency / timing safe — `_migrate_state` is pure + synchronous; the load→migrate→(next)save path keeps the existing atomic-write; single-process CLI, no shared-state race introduced
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure dict reshape, no I/O, stdlib only (json already imported); no new import
- [x] layering & dependencies follow CONVENTIONS.md — migration sits at the load seam (the existing grandfather-by-missing-key layer, mirroring `_setup_locked`); no reader call site touched (deferred to active-accessors)
- [x] a person reviewed and approved the change — Tin Dang approved the gate (2026-06-22) after an independent python-expert review (MERGE-WITH-NITS, 0 blocking; nit 1 fixed in-build, nits 2–3 → §7 deltas)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] The live dogfood `.add/state.json` (old single-active schema) loads and migrates with no error — confirmed: `add.py status` renders the project + the m-goal; `check` 401 passed / 0 failed; `audit` clean (71 tasks)
- [x] A fresh `add.py init` writes `active_milestones`/`active_tasks` natively — confirmed by test_init_writes_active_set_natively (asserts the keys in the written state.json) + a second load is a no-op
- [x] Solo behavior unchanged — confirmed: the full pre-existing suite (1377) stays green with the scalar mirror kept; the ~20 readers were not touched
- [x] All 3 add.py copies byte-identical + ENGINE_MD5 current — confirmed: md5 of all three == `aef59d9ce7482ffa5d1a78f00f6e09bc` == engine_pin.ENGINE_MD5; EnginePinTest green (hash advanced 8a914147 → aef59d9c by the verify-review purity fix)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_migrate_state` is referenced from BOTH `load_state` and `_load_state_for_json`; init default block writes the new keys. CORRECTION (independent review found my earlier "no other load path" claim FALSE): `cmd_check`'s non-JSON branch reads `state.json` DIRECTLY (add.py:~1764), bypassing the helper — harmless today (it reads only legacy keys project/stage/active_task/tasks, never the new multi-active keys), but it IS a third read site. Routing it belongs to `active-accessors` (the "route all ~20 readers" task, outside this task's frozen 2-seam scope) — seeded as a §7 SPEC delta below.
- [x] DEAD-CODE (code) — no orphaned symbol; the helper is the only new symbol and has two live callers
- [x] INDEPENDENT REVIEW — python-expert adversarial review (6 probes: idempotency/data-loss/totality/seam-coverage/mirror-invariant/init-convergence): VERDICT **MERGE-WITH-NITS, 0 blocking, confidence 0.95**. Nit 1 (PURE-vs-mutation) FIXED in-build (top-level copy; pin → aef59d9c). Nit 2 (cmd_check third seam) → corrected record above + §7 delta. Nit 3 (partial-state) → §7 delta. No data-loss or idempotency violation found.
- [ ] SEMANTIC (prose / non-code) — N/A (code change)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): malformed-state rate at load (state_invalid) · any reader that reads active_milestones before active-accessors lands (should be none yet).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] route cmd_check's direct `state.json` read (add.py:~1764) through the migration when active-accessors adds multi-active reads — today it bypasses `_migrate_state` but reads only legacy keys, so it is safe ONLY until a multi-active read is added there (evidence: independent verify-review found the third read site; owned by active-accessors) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] in active-accessors, make every active-task READ tolerate a state with `active_milestones` but no `active_tasks` (hand-edited / partially-migrated) via a `.get("active_tasks", {})` default — the migration's idempotency early-return does not backfill a missing `active_tasks` (evidence: §3 After-clause gap confirmed by the independent review, nit 3) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] an engine-editing milestone should run a verify-gate independent review by default — it caught a false self-audit WIRING claim (a third undocumented load seam) that a manual refute-read had passed over (evidence: python-expert review nit 2, this task) [folded foundation-version 41]
