# TASK: activate/deactivate/use over the active set

slug: multi-active-commands · created: 2026-06-22 · stage: mvp · risk: high
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
- `add-method/tooling/add.py:cmd_use` (2549) — `_set_active_task(state, slug)`; enhance to be milestone-aware (focus the task's own milestone + record active_tasks[ms]=task) — consumes the active-accessors §7 nit-2 delta.
- `add-method/tooling/add.py:cmd_archive_milestone` (2403) — currently clears the primary scalar; route to `_deactivate_milestone` so archiving removes the milestone from the active SET (and repoints the primary).
- `add-method/tooling/add.py` subparser block (~5122-5134) — register NEW `activate` / `deactivate` subparsers next to `use`/`set-milestone`; dispatch via `set_defaults(func=…)`.
- `add-method/tooling/add.py` accessor seam (277-308) — task-2 `_set_active_milestone`/`_set_active_task` stay frozen + in use (new-milestone still uses `_set_active_milestone`); ADD `_activate_milestone(state, slug)` (append to set + focus) and `_deactivate_milestone(state, slug)` (remove + repoint primary + pop map).
- reject vocab already present: `unknown_milestone` (×several) · `_die` idiom · milestone `status=="done"` check pattern (cmd_milestone_done 2351).
- `engine_pin.py:ENGINE_MD5` = `5eb79fa818b9c70b9f4eb4289ce70944` — re-pin after this engine edit.

Context (working folder):
- 3 byte-identical add.py copies — edit in lockstep + re-pin.
- full suite 1398 is the regression oracle for the UNCHANGED paths; the NEW commands get their own red suite.
- the migration seeds active_milestones from the scalar (one member); activate is how a user grows it to N.

Honors (patterns / conventions):
- additive verbs — no existing test enumerates the subcommand set, so new subparsers don't break the parser census (precedent: seed-and-drop/autonomy tasks).
- design-for-failure — activate/deactivate validate BEFORE mutate; reject leaves state byte-unchanged; helpers never raise on dict input.
- single-active stays a special case of the SET (N=1) — existing single-active commands keep their decisions.
- engine-edit discipline — 3-tree byte-identity + same-commit re-pin.

Anchors the contract cites: NEW `cmd_activate`/`cmd_deactivate` + `_activate_milestone`/`_deactivate_milestone` · enhanced `cmd_use` · `cmd_archive_milestone` routed to deactivate · the `activate`/`deactivate` subparsers · reject codes `unknown_milestone`/`milestone_done`/`milestone_not_active` · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Commands that operate the active SET — `activate`/`deactivate` a milestone into/out of the working set, and a milestone-aware `use` that switches the active task within a milestone. This is where N-parallel activation turns on.
Framings weighed: explicit working-set verbs (chosen — activate/deactivate manage `active_milestones` membership; the scalar is the primary focus; new-milestone keeps its replace-to-focus form so task-2's frozen helpers are untouched) · derive the set from status==active (rejected — conflates "not done" with "I'm actively working it"; users couldn't choose a focused subset) · make `use` the only verb and auto-manage the set (rejected — no explicit way to parallelize, and `use` overloads two intents).
Must:
<must>
  - NEW `activate <milestone>`: adds the milestone to `active_milestones` (idempotent — re-activating just refocuses) and makes it the primary focus (scalar active_milestone + active_task synced to that milestone's entry). Does NOT remove other active milestones (this is how a user reaches N≥2).
  - NEW `deactivate <milestone>`: removes the milestone from `active_milestones`, pops its `active_tasks` entry; if it was the primary, repoints the primary to the most-recent remaining member (or None when the set empties), syncing the scalar active_task.
  - `activate` REJECTS an unknown milestone (`unknown_milestone`) and a done milestone (`milestone_done`); `deactivate` REJECTS a milestone not in the active set (`milestone_not_active`). All validate BEFORE mutating (a reject leaves state byte-unchanged).
  - `use <task>` becomes milestone-aware: it focuses the task's OWN milestone (activating it into the set if not already) and records `active_tasks[task's milestone] = task` (consumes the active-accessors nit-2 §7 delta), so a user can switch the active task within each active milestone. The scalar active_task is still set (back-compat).
  - `archive-milestone` routes its active-state cleanup through `_deactivate_milestone` so archiving removes the milestone from the SET (not just clearing a scalar).
  - Single-active (N≤1) behavior of every PRE-EXISTING command is unchanged — the full suite stays green with no test weakened.
  - All 3 add.py copies byte-identical + ENGINE_MD5 re-pinned in the same change; parity/pin tests green.
</must>
Reject:
<reject>
  - activate an unknown milestone -> "unknown_milestone"
  - activate a milestone whose status == "done" -> "milestone_done"
  - deactivate a milestone not in active_milestones -> "milestone_not_active"
</reject>
After:
<after>
  - A user can `activate` ≥2 milestones (active_milestones has ≥2 members), `use` a task in each (active_tasks maps each milestone to its task), and `deactivate` to shrink the set; activating unknown/done and deactivating a non-member are refused with state byte-unchanged; the 3 copies + pin are green; the full prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ new-milestone keeps REPLACE-to-focus (not add) — creating a milestone via intake resets the working set to the new one (the user `activate`s others to re-parallelize). Lowest confidence because a user mid-parallel-work who creates new scope loses their set; chosen to keep task-2's FROZEN `_set_active_milestone` untouched + zero behavior change for new-milestone. If wrong: a one-line switch of new-milestone to `_activate_milestone` in a follow-up (additive, no data risk). 
  - [ ] `use` on a task whose milestone is None (milestone-less task) — focuses nothing extra, just sets the scalar active_task (orphan path); active_milestones unchanged. Confirm at freeze.
  - [ ] deactivate repoint picks the LAST remaining member (most-recently-active heuristic) vs the first — chosen last; cosmetic, only affects which milestone is "primary" after a removal. Confirm at freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Activate a second milestone (reach N=2)
  Given a project with active_milestones=["m1"] and milestones m1,m2 both status active
  When `activate m2`
  Then active_milestones contains m1 AND m2
  And the primary active_milestone is m2

Scenario: Activate is idempotent (refocus)
  Given active_milestones=["m1","m2"]
  When `activate m1`
  Then active_milestones is still {m1,m2} (no duplicate)
  And the primary is m1

Scenario: Activate refuses an unknown milestone
  Given a project without milestone mX
  When `activate mX`
  Then it dies "unknown_milestone"
  And active_milestones is unchanged

Scenario: Activate refuses a done milestone
  Given milestone mDone with status "done"
  When `activate mDone`
  Then it dies "milestone_done"
  And active_milestones is unchanged

Scenario: Use switches the active task within a milestone
  Given active_milestones=["m1","m2"] and task t2 belongs to m2
  When `use t2`
  Then active_tasks["m2"]=="t2" AND the primary focus is m2 AND scalar active_task=="t2"

Scenario: Deactivate removes a milestone and repoints
  Given active_milestones=["m1","m2"] with m2 primary
  When `deactivate m2`
  Then active_milestones=["m1"] AND m2 not in active_tasks AND primary is m1

Scenario: Deactivate refuses a non-member
  Given active_milestones=["m1"]
  When `deactivate m2`
  Then it dies "milestone_not_active"
  And active_milestones is unchanged

Scenario: Archive deactivates the milestone from the set
  Given active_milestones=["m1","m2"], m2 done and archivable
  When `archive-milestone m2`
  Then m2 is not in active_milestones AND not in active_tasks

Scenario: Single-active behavior is unchanged
  Given the existing suite (the oracle)
  When the new commands + routing are added
  Then the full prior suite stays green with no test changed

Scenario: The engine edit stays pinned
  Given all three add.py copies are edited
  Then they are byte-identical AND match the re-pinned ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# Multi-active commands (CLI verbs over the active SET) + helpers in add.py

_activate_milestone(state, slug) -> None
  ms_list = state.setdefault("active_milestones", [])
  if slug not in ms_list: ms_list.append(slug)
  state["active_milestone"] = slug                              # focus the newly activated
  state["active_task"] = (state.get("active_tasks") or {}).get(slug)   # sync scalar to its task

_deactivate_milestone(state, slug) -> None
  ms_list = state.setdefault("active_milestones", [])
  if slug in ms_list: ms_list.remove(slug)
  (state.setdefault("active_tasks", {})).pop(slug, None)
  if state.get("active_milestone") == slug:                     # repoint primary
      new = ms_list[-1] if ms_list else None
      state["active_milestone"] = new
      state["active_task"] = (state.get("active_tasks") or {}).get(new) if new else None

activate <milestone>   (cmd_activate)
  reject unknown_milestone   if slug not in state["milestones"]
  reject milestone_done      if state["milestones"][slug]["status"] == "done"
  -> _activate_milestone(state, slug); save; print focus + the active set

deactivate <milestone> (cmd_deactivate)
  reject milestone_not_active if slug not in active_milestones
  -> _deactivate_milestone(state, slug); save; print the active set

use <task>  (cmd_use, enhanced)
  reject unknown_task (unchanged)
  ms = state["tasks"][task].get("milestone")
  if ms is not None and ms in state["milestones"]: _activate_milestone(state, ms); _set_active_task(state, task, ms)
  else: _set_active_task(state, task)                           # milestone-less task: scalar only (back-compat)

archive-milestone <slug>  (cmd_archive_milestone)
  replace the task-2 clear pair with: _deactivate_milestone(state, slug)   # remove from the SET

Reject codes: unknown_milestone · milestone_done · milestone_not_active   (validate BEFORE any write)
Invariant: every PRE-EXISTING command's N≤1 decision is unchanged (full suite is the oracle).
Engine: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned same commit.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-22; auto-mode standing authorization; multi-active foundation 3/5; explicit working-set verbs · new-milestone keeps replace-to-focus)
Least-sure flag surfaced at freeze: [contract] new-milestone keeps REPLACE-to-focus rather than ADD — a user mid-parallel-work who creates new scope via intake resets their working set to the new milestone (must re-`activate` the others). Chosen to leave task-2's FROZEN `_set_active_milestone` untouched and keep new-milestone byte-identical; if the parallel-preserve behavior is wanted, it is a one-line switch to `_activate_milestone` later (additive, no data risk). Second flag: [contract] deactivate repoints the primary to the LAST remaining member (most-recently-active) — cosmetic ordering only.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 3 verbs + 2 helpers at every branch + 3 reject codes; full suite as the N≤1 oracle.
Plan (one test per scenario, asserting behavior not internals; via add.main subprocess/in-proc):
<test_plan>
  - test_activate_reaches_n2: init m1,m2; activate m2 → active_milestones {m1,m2}, primary m2
  - test_activate_idempotent: activate an already-active milestone → no dup, refocus
  - test_activate_unknown_rejected: activate mX → SystemExit "unknown_milestone", set unchanged
  - test_activate_done_rejected: milestone done → activate → "milestone_done", set unchanged
  - test_use_switches_task_in_milestone: t2∈m2 active; use t2 → active_tasks["m2"]=="t2", primary m2, scalar t2
  - test_deactivate_removes_and_repoints: active {m1,m2} primary m2; deactivate m2 → {m1}, m2∉active_tasks, primary m1
  - test_deactivate_nonmember_rejected: deactivate m2 not active → "milestone_not_active", unchanged
  - test_archive_deactivates_from_set: archive m2 → m2 ∉ active_milestones and ∉ active_tasks
  - test_use_milestoneless_task_scalar_only: task with milestone None; use → scalar set, active_milestones unchanged
  - (regression) FULL prior suite green, no test changed (N≤1 oracle)
  - test_engine_three_trees_pinned: 3 copies byte-identical == ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_multi_active_commands.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_multi_active_commands.py` `add-method/tooling/test_min_pillar.py` `add-method/tooling/test_next_footer_engine.py` `add-method/tooling/test_gate_owner_marker.py`
Strategy (ordered batches): 1. write `test_multi_active_commands.py` red. · 2. add `_activate_milestone`/`_deactivate_milestone` near the accessor seam; add `cmd_activate`/`cmd_deactivate`; enhance `cmd_use`; route `cmd_archive_milestone` to `_deactivate_milestone`; register the 2 subparsers. · 3. green new suite + FULL suite (N≤1 oracle, no test change). · 4. mirror to 2 copies; re-pin ENGINE_MD5; green incl. parity.
Safety rule (feature-specific): validate-before-mutate in activate/deactivate (reject leaves state byte-unchanged); do not alter any existing command's N≤1 decision; diff the 3 copies before re-pinning.
Code lives in: `add-method/tooling/add.py` (+ its two mirror copies)
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1398→1411 green; new test_multi_active_commands.py [13] green
- [x] coverage did not decrease — +13 new tests; the verify fix added a red→green regression guard
- [x] no FROZEN CONTRACT altered — §3 untouched. Tests were ADDED (the red suite + the verify-gate regression guard) and 3 SIBLING tests co-updated (only to track the new milestone-aware `use` vehicle — intent preserved + strengthened, none weakened); these are declared in §5 Scope
- [x] the green was EARNED, not gamed — independent python-expert adversarial refute-read (0.97) ran; it found a real BLOCKING N≤1 regression (non-primary archive stale scalar) which was FIXED red→green, plus a NOTE seeded as a §7 delta; re-reviewed clean
- [x] concurrency / timing — N/A (single-process CLI; validate-before-mutate keeps a reject byte-unchanged; no IO interleave)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — SET writers sit beside the task-2 accessor seam; commands route through helpers
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization) after the independent review + the BLOCK fix

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `activate m1` on a board where only m2 is active grows `active_milestones` to {m1,m2} (N=2) and makes m1 the primary — confirmed by test_activate_reaches_n2 + the CLI line `activated 'm1' — active: m2, m1`
- [x] `use t2` (t2 ∈ m2) records `active_tasks["m2"]=="t2"` AND flips the primary to m2 — confirmed by test_use_switches_task_in_milestone (cross-milestone focus switch, closes the active-accessors nit-2 §7 delta)
- [x] `deactivate`/`archive-milestone` drop the milestone from `active_milestones` AND pop its `active_tasks` entry, repointing the primary — confirmed by test_deactivate_removes_and_repoints + test_archive_deactivates_from_set + (verify fix) test_archive_nonprimary_clears_stale_scalar_task
- [x] a reject (`unknown_milestone`/`milestone_done`/`milestone_not_active`) leaves `active_milestones` byte-unchanged — confirmed by the unchanged-set assertions in the 3 reject tests (validate-before-mutate)
- [x] every PRE-EXISTING command's N≤1 decision is unchanged — confirmed by the full suite staying green (1398→1411) with no test weakened; the ONE N≤1 regression the independent review caught (non-primary archive stale scalar) is now FIXED + guarded red→green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_activate_milestone`/`_deactivate_milestone` referenced by cmd_activate/cmd_deactivate/cmd_use/cmd_archive_milestone; `cmd_activate`/`cmd_deactivate` dispatched via the `activate`/`deactivate` subparsers (`set_defaults(func=…)`); confirmed by test_min_pillar's parser census (every subcommand exercised) + the 12 command tests
- [x] DEAD-CODE (code) — no orphaned symbol; the replaced cmd_archive_milestone clear-pair is gone (single `_deactivate_milestone` call); grep confirms no remaining `_set_active_task(state, None, slug)` site
- [ ] SEMANTIC (prose / non-code) — n/a (engine-logic + test edits only; no prose/guide changed)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22
Evidence: full suite 1411 green · new red→green suite test_multi_active_commands.py [13] · dogfood check 403/0 · audit clean (73) · 3-tree byte-identity + ENGINE_MD5 929ced7e re-pinned. Independent python-expert adversarial review (0.97) verdict BLOCK on one real N≤1 regression (non-primary archive stale scalar active_task) — FIXED red→green in-verify (restored the back-compat scalar clear after the SET deactivate) + a guard test; one NOTE (cmd_use re-activates a done milestone) seeded as a §7 SPEC delta. No frozen contract altered; no test weakened.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] decide whether `use <task-in-done-milestone>` should re-activate a DONE milestone — `cmd_use` calls `_activate_milestone` with no done-check while `cmd_activate` rejects `milestone_done`; latent policy inconsistency (evidence: independent verify-gate review NOTE, contract-faithful but a UX gap) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] consider switching `new-milestone` from REPLACE-to-focus to ADD-and-focus so creating scope mid-parallel-work preserves the active SET (evidence: §3 freeze flag — today a user must re-`activate` siblings after `new-milestone`) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a frozen contract can hold an INTERNAL tension — here "replace the clear-pair with `_deactivate_milestone`" collided with the frozen "every N≤1 decision unchanged" invariant; the literal instruction REGRESSED the invariant. Resolution: honor the structural instruction (route through the SET writer) AND restore the invariant additively (a back-compat guard), rather than treat either clause as the whole truth (evidence: independent verify-gate review found the BLOCK that the green suite missed because no test exercised a non-primary archive with a live scalar) [folded foundation-version 41]
- [TDD · folded] a behavior-preserving refactor's regression hides where NO test arranges the precondition — the stale-scalar path needed a task created BEFORE the replace-to-focus `new-milestone`; add a coverage case for each pre-existing guard a routing change subsumes (evidence: test_archive_deactivates_from_set created zero tasks, so the dropped guard read green) [folded foundation-version 41]
