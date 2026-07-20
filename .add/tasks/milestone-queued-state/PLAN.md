# TASK: Queued milestone status

slug: milestone-queued-state · created: 2026-06-26 · stage: mvp
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
- `add-method/tooling/add.py:cmd_new_milestone` (2421) — creates a milestone; hardcodes `record["status"]="active"` then `_set_active_milestone(state, slug)` (replaces the active set with N<=1). Add a `--queued` arg: status="queued", and SKIP `_set_active_milestone` (don't focus it).
- `add-method/tooling/add.py:cmd_activate` (2940) — adds a milestone to the active SET via `_activate_milestone`; currently rejects only `status=="done"`. Must PROMOTE a `queued` milestone: flip its `status` queued→active when activated.
- `add-method/tooling/add_engine/accessors.py:_activate_milestone` (41) / `_set_active_milestone` (22) — the active-set mutators; `_activate_milestone` appends (N>=2), `_set_active_milestone` replaces (N<=1). Neither touches `status` today.
- `add-method/tooling/add_engine/milestones.py:_all_milestones_done` (108) — `all(status=="done")`; a `queued` milestone is correctly NOT done (no change needed, but assert it).
- the argparse subparser for `new-milestone` in `add.py` (near other `add_argument` blocks) — add `--queued` flag (store_true), mirroring `--await-confirm`.
- the milestone status render in `status` (add.py ~3523, ~2385 parse) — surfaces `m["status"]`; queued must render as `queued`, not marked active `*`.

Context (working folder):
- engine tests: `add-method/tooling/test_*.py` — the new red suite is a new `test_milestone_queued_state.py`; existing milestone tests (new-milestone/activate/milestone-done) must stay green (byte-identical default when `--queued` absent).
- ENGINE_MD5 pin: `add-method/tooling/engine_pin.py` — an engine code change re-aims the pin (the 3-tree engine mirror + pin must update); this is an ENGINE task (unlike the prior convention-only one).
- milestone status enum is implicit (strings "active"/"done"); no central enum constant today.

Honors (patterns / conventions):
- **Opt-in / byte-identical default** — `--queued` absent ⇒ behavior unchanged (existing milestone tests stay green); mirrors `--await-confirm`'s grandfathering.
- **Migration-safe** — existing milestones (active/done) need no migration; `queued` is additive.
- **Engine 3-tree mirror + ENGINE_MD5** — add.py edits propagate to `_bundled` + dogfood `.add/tooling/`, re-pin ENGINE_MD5 (the convention-only invariant does NOT apply here — this task DOES touch the engine).
- **Never silently activate** — promotion queued→active is human-gated (`activate`), never automatic.

Anchors the contract cites:
- `cmd_new_milestone` + the `--queued` flag (status="queued", not focused)
- `cmd_activate` promotes queued→active (status flip + add to set)
- milestone status enum: **active · queued · done**
- opt-in/byte-identical-default + ENGINE_MD5 re-pin as the engine-change invariant

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a `queued` milestone status — a milestone can be CREATED non-active (`new-milestone --queued`) and later PROMOTED to active (`activate`). Foundation for roadmap intake (1 active + N−1 queued).
Framings weighed: new status value `queued` + `--queued` flag + `activate`-promotes (chosen — minimal, reuses the active-set machinery) · a separate `queue` list in state (rejected: duplicates status) · a `--inactive` boolean on the record (rejected: status is the clear enum)
Must:
<must>
  - The milestone status enum is **active · queued · done** (was active · done) — a `queued` milestone exists but is neither active nor done.
  - `add.py new-milestone --queued <slug>` creates the milestone with `status="queued"` and does NOT focus it: `active_milestone` / `active_milestones` are UNCHANGED. The MILESTONE.md is still rendered.
  - `add.py new-milestone <slug>` WITHOUT `--queued` is byte-identical to today (status="active" + `_set_active_milestone`).
  - `add.py activate <slug>` on a `queued` milestone PROMOTES it: flips `status` queued→active AND adds it to the active set (`_activate_milestone`).
  - A `queued` milestone is NOT counted done (does not satisfy `_all_milestones_done` / the graduation gate) and is NOT in the active set (not marked active in `status`).
  - Migration-safe: existing milestones (active/done) are unaffected; `queued` is additive, no state migration.
  - The add.py edit propagates byte-identical across the engine 3-tree mirror (canonical · `_bundled` · dogfood `.add/tooling/`) and ENGINE_MD5 is re-pinned.
</must>
Reject:
<reject>
  - `new-milestone --queued` on an existing slug without `--force` -> "milestone_exists"  (existing guard, unchanged)
  - `activate` a `done` milestone -> "milestone_done"  (existing guard, unchanged — done never re-opens via activate)
  - `activate` an unknown slug -> "unknown_milestone"  (existing guard)
</reject>
After:
<after>
  - A milestone can be created `queued` (state-recorded, MILESTONE.md on disk, not focused) and promoted to active via `activate`.
  - The default (no `--queued`) path is byte-identical to today; the engine mirror + ENGINE_MD5 are in sync.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Promotion reuses the EXISTING `activate` command (queued→active status flip) rather than a new `promote` verb — lowest confidence because `activate` today only manages the multi-active SET, and overloading it to also flip status may surprise; if wrong: users expect a distinct `promote`/`start` verb and `activate` stays set-only. (Surface at the freeze.)
  - [ ] a `queued` milestone correctly blocks "MVP covered → graduation" (it is not-done) — confirm this is desired, not a surprise hold.
  - [ ] `new-milestone --queued` still writes MILESTONE.md to disk (same as active) — confirm queued ≠ "deferred draft with no file".
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: create a queued milestone without focusing it
  Given a project with active milestone "alpha"
  When I run `new-milestone --queued beta`
  Then milestone "beta" exists with status "queued" and its MILESTONE.md is on disk
  And the active milestone is still "alpha"   # active set unchanged

Scenario: default new-milestone is unchanged (byte-identical)
  Given a project
  When I run `new-milestone gamma` (no --queued)
  Then "gamma" has status "active" and becomes the focused active milestone

Scenario: promote a queued milestone to active
  Given a queued milestone "beta"
  When I run `activate beta`
  Then "beta" status flips to "active" and it joins the active set

Scenario: a queued milestone is neither done nor active
  Given a project whose only non-done milestone is queued "beta"
  When I check all-milestones-done and the active set
  Then all-milestones-done is False   # queued blocks graduation
  And "beta" is not in active_milestones   # not marked active

Scenario: queued on an existing slug is rejected
  Given milestone "beta" already exists
  When I run `new-milestone --queued beta` without --force
  Then it errors "milestone_exists"
  And "beta" is unchanged   # no clobber

Scenario: activating a done milestone is still rejected
  Given a done milestone "alpha"
  When I run `activate alpha`
  Then it errors "milestone_done"
  And "alpha" stays done   # done never re-opens
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI CONTRACT (engine commands — the shape of the change)

new-milestone <slug> [--queued] [--title T] [--goal G] [--stage S] [--force] [--await-confirm]
  default (no --queued)  -> milestones[slug].status = "active"; _set_active_milestone(slug)   # UNCHANGED
  --queued               -> milestones[slug].status = "queued"; active set UNCHANGED; MILESTONE.md still written
  slug exists, no --force -> err "milestone_exists"

activate <slug>
  slug status == "queued" -> status -> "active"; _activate_milestone(slug)   # PROMOTE
  slug status == "active" -> _activate_milestone(slug) (refocus)             # UNCHANGED
  slug status == "done"   -> err "milestone_done"
  slug unknown            -> err "unknown_milestone"

State shape: milestones[slug].status ∈ { "active", "queued", "done" }   (was {active,done})
  - _all_milestones_done(): all(status=="done") — a "queued" milestone => False (UNCHANGED logic, new input)
  - active_milestones / active_milestone: a "queued" milestone is absent until promoted
  - migration: none — existing records carry active/done; "queued" is only ever written by --queued

Mirror: add.py edit -> _bundled/tooling/add.py + .add/tooling/add.py byte-identical; engine_pin.py ENGINE_MD5 re-pinned.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-26); promotion verb = reuse `activate` (queued→active flip)
Least-sure flag surfaced at freeze: [spec] promotion reuses the existing `activate` verb rather than a new `promote`/`start`. Why most likely wrong: `activate` today only manages the multi-active set; overloading it to also flip status may surprise. Cost if wrong: users expect a distinct verb. RESOLVED by the human at freeze → reuse `activate`.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_milestone_queued_state.py`
Strategy (ordered batches): 1. write red `test_milestone_queued_state.py` (6 scenarios) · 2. add.py: `--queued` arg on the new-milestone subparser + branch in cmd_new_milestone (status/queued, skip focus) · 3. add.py: cmd_activate promotes queued→active (status flip before/with _activate_milestone) · 4. propagate add.py byte-identical to _bundled + dogfood · 5. re-pin ENGINE_MD5 (engine_pin.py) · 6. run full suite + check
Safety rule (feature-specific): the default (no --queued) path must stay byte-identical — guard with the existing milestone tests; `queued` only ever written via the explicit flag; promotion is human-gated (activate), never automatic.
Code lives in: add.py (×3 trees) + engine_pin.py (no `./src/`).
Constraints: do NOT change the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2002/0 (+7 new); `add.py check` 435/0
- [x] coverage did not decrease — +1 test file (test_milestone_queued_state.py, 7 assertions); nothing removed
- [x] no test or contract was altered during build — contract untouched; the test file was final at the tests→build snapshot and NOT edited in build (tripwire clean)
- [x] the green was EARNED, not gamed — tests drive real CLI paths via add.main + state inspection (status flips, active-set membership, MILESTONE.md on disk, SystemExit on the 2 rejects). No vacuous asserts; the default-path test guards byte-identical behavior.
- [x] concurrency / timing — N/A (synchronous CLI state mutation; save_state is the existing atomic write)
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; zero new deps
- [x] layering & dependencies follow CONVENTIONS.md — reuses `_set_active_milestone`/`_activate_milestone`; engine 3-tree mirror byte-identical + ENGINE_MD5 re-pinned
- [ ] a person reviewed and approved the change — pending the gate (contract human-approved at freeze)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `new-milestone --queued <slug>` creates status=queued WITHOUT changing focus — confirmed: dogfood `--help` shows `--queued`; test asserts active_milestone unchanged + MILESTONE.md on disk
- [x] `activate <queued>` flips it to active + joins the set — confirmed by test_activate_promotes_queued
- [x] default `new-milestone` (no flag) is byte-identical — confirmed: 3-tree add.py all md5 8a6440cf…; existing milestone suite green; default-path test passes
- [x] a queued milestone blocks all-done/graduation — confirmed by test_queued_not_done_not_active (_all_milestones_done False)
- [x] engine mirror + pin in sync — confirmed: 3 add.py copies byte-identical; ENGINE_MD5 re-pinned to md5(add.py); cross-tree pin tests green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the `--queued` arg feeds `getattr(args,"queued")` in cmd_new_milestone; the queued branch in cmd_activate is reached by test_activate_promotes_queued. All new code paths exercised.
- [x] DEAD-CODE (code) — no orphaned symbol; the only additions are one arg, one branch in each of two existing functions.

### GATE RECORD
Outcome: PASS
Note: engine change; no residue. Default path byte-identical (md5-confirmed across 3 trees); ENGINE_MD5 re-pinned. No security/concurrency/architecture concern. Task 1 of 3 in multi-milestone-intake.
Reviewed by: Tin Dang (contract approved @ freeze; verify auto-gated on complete evidence under autonomy:auto) · date: 2026-06-26

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
