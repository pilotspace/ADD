# TASK: new-milestone preserves the active SET (adds, never replaces)

slug: new-milestone-add-focus · created: 2026-06-26 · stage: mvp
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
- `add-method/tooling/add.py:cmd_new_milestone` (2537-2594) — the ONE line that sets focus on a NON-queued create: `if not queued: _set_active_milestone(state, slug)`. SWAP `_set_active_milestone` → `_activate_milestone`. That is the whole behavior change.
- `add-method/tooling/add.py:_set_active_milestone` — REPLACES the active set (`active_milestones = [slug]`, wiping others); leaves the scalar `active_task` untouched (can go stale). Stays as a helper (still used by deactivate-to-empty etc.) — only its CALL SITE in new-milestone changes.
- `add-method/tooling/add.py:_activate_milestone` — ADDs `slug` to `active_milestones` (idempotent), makes it primary, and re-points the scalar `active_task` to `active_tasks.get(slug)` (None for a fresh milestone — a correctness BONUS over the stale scalar today). This is the swap target.
- `--queued` path UNCHANGED: a queued create still leaves the active set alone (it never set focus). Only the non-queued branch changes.
- `engine_pin.py:ENGINE_MD5` = `d1c1b68702543c38c9e97bde71e39ba6` — re-pin after this engine edit.

Context (working folder):
- 3 byte-identical add.py copies (`add-method/tooling` · `.add/tooling` · `add-method/src/add_method/_bundled/tooling`) — edit in lockstep + re-pin.
- MEASURED blast radius (experimental swap + full suite): exactly ONE existing behavioral test breaks — `test_multi_active_commands.py:test_deactivate_nonmember_rejected`. Its setUp creates m1 then m2 and the test asserts `m1 NOT in active_milestones` ("only m2 from the replace-focus new-milestone"). Under preserve both are active, so its PREMISE is obsolete. Fix in the TESTS phase (not build — tamper tripwire): make a genuine non-member via `--queued` and keep the "deactivate non-member rejected" assertion. New tests land in `add-method/tooling/test_new_milestone_add_focus.py`.

Honors (patterns / conventions):
- multi-active model (team-collaboration major): N active milestones via the `active_milestones` SET; `_activate_milestone` is the canonical "add to the SET + focus" helper. This task makes new-milestone use it (was the odd one out, silently wiping the SET).
- single-active stays identical: with no other active milestone, add-vs-replace produce the SAME `[slug]` set — only a user who ALREADY has an active milestone sees the difference (the new one no longer evicts the old).
- engine-edit discipline: 3-tree byte-identity + same-commit ENGINE_MD5 re-pin; the existing suite is the regression oracle.

Anchors the contract cites: `cmd_new_milestone` (the non-queued focus line) · `_activate_milestone` (swap target) · `_set_active_milestone` (the replaced call) · `active_milestones` SET + scalar `active_milestone`/`active_task` · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: creating a milestone while one is active PRESERVES the active SET — `new-milestone` (non-queued) ADDS the new milestone to `active_milestones` and makes it primary, instead of REPLACING the set and evicting the others. One-line swap at the focus call: `_set_active_milestone` → `_activate_milestone`. This makes N≥2 active reachable in one command and stops the silent eviction of your other active milestones.
Framings weighed: swap the focus call to `_activate_milestone` (chosen — `_activate_milestone` is already the canonical "add to SET + focus" helper; new-milestone was the lone caller still wiping the set; smallest change, reuses tested behavior) · add an opt-in `--add` flag and keep replace as default (rejected by the freeze decision — the criterion wants preserve as the DEFAULT; replace-by-default is the multi-active footgun being removed) · leave it and rely on `activate` after create (rejected — two commands for what should be one; the eviction already happened).
Must:
<must>
  - `new-milestone X` (NON-queued) with a milestone P already active leaves BOTH active: `active_milestones` contains P and X, with X primary (`active_milestone == X`). P is NOT evicted.
  - the active_task scalar re-points to X's entry — `active_tasks.get(X)`, i.e. None for a brand-new (taskless) milestone — rather than dangling at P's task (the `_activate_milestone` behavior; a correctness bonus).
  - single-active is unchanged: with NO other active milestone, `new-milestone X` yields `active_milestones == [X]`, X primary — identical to today.
  - `--queued` is unchanged: a queued create never set focus and still leaves the active set exactly as it was (byte-identical).
  - idempotent: re-creating/`--force` an already-active milestone keeps it a single set member (no duplicate), still primary.
  - all 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned; parity/pin tests green; the full suite green (the one premise-obsolete test updated in the TESTS phase, assertion preserved).
</must>
Reject:
<reject>
  - (no new error code — this changes the success-path focus semantics only; bad-slug / milestone-exists rejections are unchanged.)
</reject>
After:
<after>
  - after `new-milestone X` while P was active, `status` shows P AND X active (X primary); the eviction is gone; plain/`--queued`/single-active paths behave as before; suite + 3 copies + pin green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ preserving the set is desired as the DEFAULT (not behind a flag) — settled by the freeze decision ("Preserve by default"); lowest residual risk is that a user who created milestones serially now accumulates active ones (a finished-but-unarchived P lingers active). Mitigation: `status` shows the N active set and `deactivate`/`archive-milestone` remove P; cost if unwanted: revert to the `--add` opt-in framing (one-line).
  - [ ] re-pointing active_task to None for the fresh milestone is acceptable (vs leaving P's task dangling) — chosen as more correct; confirm no workflow relied on the stale scalar (measured: 0 behavioral tests do).
  - [ ] the single obsolete test (`test_deactivate_nonmember_rejected`) is fixed by creating a genuine non-member via `--queued`, keeping its assertion — confirm this is a faithful premise-fix, not a weakening.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: creating a milestone while one is active preserves both
  Given milestone P is active (active_milestones == [P])
  When `new-milestone X` runs (non-queued)
  Then active_milestones contains both P and X
  And active_milestone (primary) == X

Scenario: the fresh milestone re-points the scalar active_task
  Given P is active with a task whose slug is the scalar active_task
  When `new-milestone X` runs
  Then active_task is X's entry (None — X has no tasks yet), not P's dangling task

Scenario: single-active is unchanged
  Given no milestone is active (active_milestones == [])
  When `new-milestone X` runs
  Then active_milestones == [X] and active_milestone == X

Scenario: --queued leaves the active set untouched
  Given P is active
  When `new-milestone X --queued` runs
  Then X is queued (not active) and active_milestones is still [P]

Scenario: re-activating an already-active milestone stays single-membership
  Given X is already active
  When `new-milestone X --force` runs
  Then active_milestones contains X exactly once and active_milestone == X

Scenario: The engine edit stays pinned
  Given all three add.py copies are edited
  When the parity + ENGINE_MD5 tests run
  Then the three copies are byte-identical AND match the re-pinned ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# new-milestone preserves the active SET (internal CLI; state mutation on the success path)

cmd_new_milestone(args):                          # ONLY the focus line changes
  ...                                             # slug-validate, render MILESTONE.md, build record (UNCHANGED)
  state["milestones"][slug] = record
  if not queued:
-     _set_active_milestone(state, slug)          # REPLACE: active_milestones = [slug]  (evicts others)
+     _activate_milestone(state, slug)            # PRESERVE: append slug + focus + repoint active_task
  save_state(root, state)
  ...                                             # prints UNCHANGED

_activate_milestone(state, slug):                 # existing helper, now the new-milestone focus path
  active_milestones.append(slug) if slug not in it # idempotent ADD
  active_milestone = slug                          # primary
  active_task = (active_tasks or {}).get(slug)      # None for a fresh milestone

Observable: after `new-milestone X` with P active → active_milestones ⊇ {P, X}, active_milestone == X.
Unchanged: --queued path · single-active ([] → [X]) · bad_slug/milestone_exists rejects · all prints.
Errors: none new. Engine: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned same commit.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [spec] preserve-by-default changes a DEFAULT and re-points the scalar `active_task` to None for the fresh milestone — already settled ("Preserve by default" decision); residual risk is a finished-but-unarchived milestone now lingering in the active set (mitigated by `status` showing the N set + `deactivate`/`archive-milestone`). Second flag: [test] the ONE existing test invalidated (`test_deactivate_nonmember_rejected`) is repaired by creating a genuine non-member via `--queued` — assertion kept, premise fixed (a faithful update, not a weakening); measured as the only behavioral break (2053/2054 pass under the swap).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the swapped focus line in `cmd_new_milestone` across the 5 behaviors (preserve, scalar re-point, single-active, --queued untouched, idempotent) + the pin; plus updating the ONE premise-obsolete existing test.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_create_while_active_preserves_set: P active → new-milestone X → {P, X} active, primary X
  - test_fresh_milestone_repoints_active_task: P active w/ scalar task → new-milestone X → active_task is None (X's empty entry), not P's
  - test_single_active_unchanged: no active → new-milestone X → active_milestones == [X], primary X
  - test_queued_leaves_set_untouched: P active → new-milestone X --queued → X queued, active_milestones == [P]
  - test_force_recreate_single_membership: X active → new-milestone X --force → X once, primary X
  - test_three_trees_pinned: 3 add.py copies byte-identical AND == engine_pin.ENGINE_MD5
  - (existing-test UPDATE, in this phase) test_multi_active_commands.test_deactivate_nonmember_rejected: its premise ("m1 not active, only m2 from replace-focus") is obsolete under preserve — rewrite the arrange to create a GENUINE non-member via `new-milestone m3 --queued`, keep the "deactivate non-member rejected" assertion. This is the only existing test the spec change invalidates (measured).
</test_plan>

Tests live in: `add-method/tooling/test_new_milestone_add_focus.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_new_milestone_add_focus.py` `add-method/tooling/test_multi_active_commands.py`
Strategy (ordered batches): 1. (TESTS phase) write `test_new_milestone_add_focus.py` red + update `test_multi_active_commands.py:test_deactivate_nonmember_rejected` to a genuine non-member — BOTH before crossing to build (test edits in build trip the tamper tripwire). · 2. (BUILD) swap the single line `_set_active_milestone(state, slug)` → `_activate_milestone(state, slug)` in the non-queued branch of `cmd_new_milestone`. · 3. mirror byte-identically to the other 2 copies; re-pin ENGINE_MD5. · 4. full suite green incl. parity/pin.
Safety rule (feature-specific): the swap is the ONLY production edit — do not touch the `--queued`, validation, render, record-build, or print lines. `_set_active_milestone` stays defined (other callers). Diff the 3 copies before re-pinning.
Code lives in: `add-method/tooling/add.py` (+ its two mirror copies)
Constraints: do NOT change the contract; the ONLY test edits are this task's new file + the one premise-obsolete test (both in the tests phase, declared above); stdlib only.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2060 OK (2054→2060, +6 test_new_milestone_add_focus); check 447/0; audit clean (93 tasks)
- [x] coverage did not decrease — 6 new tests cover preserve, scalar re-point, single-active, queued-untouched, force-idempotent, pin; the updated test_multi_active_commands stays at 13 green
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; ALL test edits (the new file + the obsolete-test premise-fix) happened in the TESTS phase before the tests→build snapshot, so the tamper tripwire passed clean; build touched only the single production line (git: add.py swap only)
- [x] the green was EARNED, not gamed — the 2 preserve-specific tests were RED for the right reason (set==[X] / active_task=='t1' under replace) before the swap, GREEN after; the obsolete test's ASSERTION was preserved (deactivate non-member rejected) with only the arrange fixed to a genuine `--queued` non-member; blast radius independently measured (2053/2054 pass under the swap)
- [x] concurrency / timing of the risky operation is safe — single-process state write; `_activate_milestone` is an in-memory mutation before one `save_state`; no new I/O
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; reuses an existing helper; one-line call swap
- [x] layering & dependencies follow CONVENTIONS.md — uses the canonical `_activate_milestone` (the established "add to SET + focus" helper); `_set_active_milestone` retained for its other callers; no new surface
- [x] a person reviewed and approved the change — Tin Dang: the design fork ("Preserve by default") chosen via the active-set question + the §3 freeze ("Freeze as-is")

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `new-milestone X` with P active → `active_milestones` ⊇ {P, X}, `active_milestone` == X (P not evicted) — confirmed: test_create_while_active_preserves_set green
- [x] the scalar `active_task` re-points to X's (empty → None) entry, not P's dangling task — confirmed: test_fresh_milestone_repoints_active_task green
- [x] single-active unchanged ([] → [X], primary X) — confirmed: test_single_active_unchanged green
- [x] `--queued` leaves the active set exactly [P] (byte-identical path) — confirmed: test_queued_leaves_set_untouched green
- [x] idempotent under `--force` (X once, primary) — confirmed: test_force_recreate_single_membership green
- [x] the ONE obsolete existing test was updated faithfully (assertion kept, genuine non-member via --queued) + full suite green — confirmed: test_multi_active_commands 13/13 green
- [x] 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned — confirmed: all three == `0d03e178a0f00e7684dfc8b1ffd64342` == engine_pin.ENGINE_MD5

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the swapped call `_activate_milestone(state, slug)` runs in the non-queued branch of `cmd_new_milestone`; `_activate_milestone` is a pre-existing, separately-tested helper (HelperTest in test_multi_active_commands); no new symbol introduced
- [x] DEAD-CODE (code) — REFUTE-READ CORRECTION: the swap removed the LAST internal *caller* of `_set_active_milestone` (grep: zero non-def call sites across all 3 copies). But it is NOT dead code — it is a directly-TESTED state accessor in the `_active_*` family: `test_active_accessors.py` exercises it (set "m1" / set None) and `test_engine_extract_accessors.py` pins it in the MOVED accessor set. So it is correctly retained as covered API (and removing it would RED those two tests). My §0/§3 "still used by deactivate-to-empty" rationale was factually wrong (`_deactivate_milestone` uses inline logic) — the retention conclusion holds, the reason was corrected here. No actual dead code introduced.
- [ ] SEMANTIC (prose / non-code) — N/A (code change; the new comment passed the ubiquitous-language lint in the full suite)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-26

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does the active set grow unboundedly now that new-milestone never evicts? if users routinely carry many active milestones, a `status` nudge to deactivate/archive stale ones (done-but-active) is the natural follow-up.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] now that new-milestone preserves the set, a done-but-unarchived milestone lingers active — consider a `status`/doctor nudge to deactivate or archive a milestone whose tasks are all done (evidence: the freeze flag's residual risk, this task)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] before claiming "helper retained — other callers remain" in a contract, GREP the call sites — here the swap removed the LAST caller and the §0/§3 "used by deactivate-to-empty" rationale was wrong; the retention still held but for a DIFFERENT reason (it's a directly-tested accessor), caught only by the verify refute-read (evidence: zero non-def call sites + test_active_accessors references) [folded foundation-version 55]
- [ADD · folded] doing ALL test edits (new file + premise-fix of an invalidated existing test) in the TESTS phase before crossing to build avoids the tamper tripwire — contrast mine-all-lens, where a build-phase fixture fix tripped it and forced a re-baseline (evidence: this task's verify gated clean on the first try) [folded foundation-version 55]
