# TASK: Stage-goal-criteria block + status graduation cue

slug: stage-goal-criteria · created: 2026-06-08 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: stage-goal-criteria — a human-checked PROJECT.md block + an additive `add.py status` graduation cue
Framings weighed: two-tally cue, new PROJECT.md block (chosen) · reuse a final milestone's exit-criteria · fire on milestones-done alone (no human block)
Must:
<must>
  - Parse a `## Stage goal criteria` section in PROJECT.md into a (met, total) tally — a PROJECT.md analog of `_exit_criteria`, counting `- [x]` vs `- [ ]` (call it `_stage_criteria(root)`).
  - Emit a graduation cue from `add.py status` when, and ONLY when, BOTH tallies complete: every milestone in state is `status=done` (the project-global tally) AND the block has total>0 and met==total (the human's affirmation tally).
  - Word the cue as the ACTION, not a file — e.g. `MVP covered → propose graduation` — so it stands alone before `graduate.md` exists (that guide lands two tasks later).
  - Add a `status --json` field reporting the signal additively — `graduation_ready: bool` plus the `stage_criteria: {met,total}` tally — so a harness can branch without scraping text.
  - Keep the cue READ-ONLY: it changes no state, flips no stage, alters no exit code. It only invites the flow.
</must>
Reject:   <!-- read-only additive seam: each "reject" is a fail-closed state in which the cue is WITHHELD; none prints an error or changes an exit code -->
<reject>
  - any milestone not `done` (incl. an active milestone like v22 itself) -> cue withheld :: "milestones_incomplete"
  - no `## Stage goal criteria` block, or the block is empty (total==0) -> cue withheld, status byte-unchanged (the grandfather case) :: "no_stage_criteria"
  - block present but not all boxes checked (met < total) -> cue withheld :: "criteria_unmet"
  - PROJECT.md unreadable / OSError / malformed section -> cue withheld, status still renders (never crash) :: "project_unreadable" (fail-closed)
</reject>
After:
<after>
  - With every milestone `done` AND every `## Stage goal criteria` box `[x]`, `add.py status` shows the graduation cue and `--json` reports `graduation_ready: true`.
  - In every other state, `status` text + `--json` fields + exit codes are byte-identical to today (the additive-only guarantee — the seam this task freezes).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The cue renders at a project-global point in `cmd_status`, NOT in `_decide_next_base` (which is per-active-milestone) — lowest confidence because the existing "archive / goal not met" prompts are all per-milestone and there may be no clean global render seam that fires precisely when NO milestone is active (all done); if wrong: the cue needs a new render seam or collides with the per-milestone DECIDE-NEXT, risking the byte-unchanged guarantee. (The contract must pin WHERE the cue renders.)
  ⚠ "All milestones done" reads state["milestones"] only — archived milestones (removed from state by the archive lifecycle) don't count, and a project with zero milestones never false-fires — lowest confidence #2 because the done-tally's interaction with archive/empty states is unverified; if wrong: the cue fires too early, never, or on an empty project.
  - [ ] The section header is exactly `## Stage goal criteria` placed after the `goal:` line in PROJECT.md — confirm at contract (nameable, low stakes).
  - [ ] `--json` field names are `graduation_ready` + `stage_criteria:{met,total}` — confirm at contract (low stakes).
  - [ ] No `add.py check` lint for the block in THIS task (deferred to a later extra) — confirm out-of-scope.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
# --- Must rules ---
Scenario: Cue fires when both tallies complete          # M2 (+ M1, M3)
  Given every milestone in state.json is status=done
  And PROJECT.md has a "## Stage goal criteria" block with every box "- [x]"
  When I run `add.py status`
  Then the output contains the cue line "MVP covered → propose graduation"
  And the cue text names the action only — no file path

Scenario: --json reports the signal additively          # M4 (+ M1 tally observable)
  Given the same all-done, all-checked state
  When I run `add.py status --json`
  Then the JSON has graduation_ready=true and stage_criteria={met:N,total:N} with met==total
  And every pre-existing status --json field and value is unchanged

Scenario: Cue is self-contained before graduate.md exists  # M3
  Given the all-done, all-checked state
  And graduate.md does not exist in the skill
  When I run `add.py status`
  Then the cue still renders (it names the action, not the missing guide)

Scenario: Cue is read-only                               # M5
  Given the all-done, all-checked state
  When I run `add.py status`
  Then state.json and PROJECT.md are byte-identical before and after
  And the project stage is still "mvp" (no flip)

# --- Reject / fail-closed suppression states (each asserts status stays unchanged) ---
Scenario: Withheld while any milestone is active         # milestones_incomplete
  Given at least one milestone is status=active (e.g. v22)
  And the stage-goal-criteria are all "- [x]"
  When I run `add.py status`
  Then no graduation cue appears
  And status text + exit code are byte-identical to the pre-feature baseline

Scenario: Grandfather — no criteria block                # no_stage_criteria
  Given PROJECT.md has no "## Stage goal criteria" section
  And every milestone is status=done
  When I run `add.py status`
  Then no graduation cue appears (total==0)
  And status text + exit code are byte-identical to today

Scenario: Criteria present but unmet                     # criteria_unmet
  Given every milestone is status=done
  And the stage-goal-criteria block has at least one "- [ ]" (met < total)
  When I run `add.py status --json`
  Then graduation_ready is false and stage_criteria shows met < total
  And no cue line appears in the text output (unchanged from today)

Scenario: Fail-closed on unreadable PROJECT.md           # project_unreadable
  Given PROJECT.md cannot be read (OSError) or its section is malformed
  When I run `add.py status`
  Then status still renders its normal rollup without crashing
  And the cue is withheld and the exit code is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE CONTRACT — read-only, ADDITIVE to `add.py status`. No new command, no new exit code, no state mutation.

fn _stage_criteria(root) -> (met:int, total:int)        # PROJECT.md analog of _exit_criteria
  regex the "## Stage goal criteria" section of PROJECT.md:
    total = count("- [x]") + count("- [ ]")   within that section
    met   = count("- [x]")
  fail-closed: section absent / file unreadable (OSError) / no match -> (0, 0)

fn _all_milestones_done(state) -> bool
  ms = state.get("milestones") or {}
  return bool(ms) and all(m.get("status") == "done" for m in ms.values())
  # archived milestones are absent from state["milestones"] (excluded by the archive lifecycle);
  # zero milestones -> False (nothing shipped is not "covered")

graduation_ready := _all_milestones_done(state) AND total > 0 AND met == total

`add.py status` (text):
  graduation_ready == true  -> append ONE line after the milestones rollup, containing exactly:
        "MVP covered → propose graduation"          # the action; NO file path, NO graduate.md dependency
  graduation_ready == false -> output BYTE-IDENTICAL to today (no line, no whitespace delta)

`add.py status --json` -> add EXACTLY two keys; every existing key + value byte-unchanged:
  "graduation_ready": bool
  "stage_criteria":   { "met": int, "total": int }

PROJECT.md block (authored by a HUMAN; the engine only reads it), placed after the `goal:` line:
  ## Stage goal criteria
  - [ ] <observable stage-covered criterion>
  - [ ] ...
  # same "- [x]"/"- [ ]" grammar as a milestone's "## Exit criteria"

Reject codes -> contracted response (ALL fail-closed; none prints, none changes the exit code):
  milestones_incomplete -> graduation_ready=false · no cue · status unchanged
  no_stage_criteria     -> total==0 -> graduation_ready=false · no cue · status unchanged
  criteria_unmet        -> met<total -> graduation_ready=false · no cue · status unchanged
  project_unreadable    -> _stage_criteria=(0,0) · status still renders · no cue (never crash)

Names per GLOSSARY: stage · milestone · goal · status. New terms (stage-graduation · graduation
analytics · stage-goal-criteria) are defined in v22 MILESTONE §Shared decisions. Contract is pinned
by the §4 red suite (the byte-unchanged baseline + the cue + the two --json keys) — no service mock.
```

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-08
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new code (the `cmd_status` cue branch + the two `--json` keys + `_stage_criteria` + `_all_milestones_done`); the full engine suite stays green (no regression).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  RED drivers (fail today — graduation_ready/cue absent):
  - test_cue_fires_when_ready: all milestones done + block all "- [x]" -> status text contains the cue   (M2)
  - test_json_graduation_ready_true: same -> --json graduation_ready=true, stage_criteria={2,2}            (M4)
  - test_json_keys_present_when_not_ready: active milestone -> keys exist, graduation_ready=false (additive) (M4)
  - test_cue_self_contained_no_file_ref: cue line has no ".md"/"graduate.md" — names the action            (M3)
  - test_criteria_unmet_json_false: all done + one "- [ ]" -> graduation_ready=false, stage_criteria={1,2}  (criteria_unmet)
  SAFETY NETS (green now + after — guard the invariants):
  - test_cue_is_read_only: status mutates neither state.json nor PROJECT.md; no stage flip                  (M5)
  - test_withheld_while_milestone_active: active milestone + checked block -> no cue                        (milestones_incomplete)
  - test_grandfather_no_block: all done, no block (total==0) -> no cue                                      (no_stage_criteria)
  - test_block_presence_no_effect_while_incomplete: block must not perturb status text while incomplete     (byte-unchanged)
  - test_fail_closed_on_unparseable_section: header but no boxes -> no cue, status still renders            (project_unreadable / fail-closed)
</test_plan>

Tests live in: `add-method/tooling/test_graduation_cue.py` · ran RED 2026-06-08 (5 drivers fail: KeyError graduation_ready / cue absent; 5 safety nets green) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full engine suite 655 OK (incl. 10 new graduation-cue tests); three-tree byte-identical
- [x] coverage did not decrease — +10 tests; every new symbol (`_stage_criteria`·`_all_milestones_done`·`_graduation_ready`·cue branch·2 json keys) exercised
- [⚠] no test or contract altered during build — **NOT clean (residue → human gate):** `test_json_surface_frozen` was RE-AIMED and the v4-1 `machine-state-json` contract REINTERPRETED (status --json: closed-set → additive-safe). A **human-ratified change-request** (option A, 2026-06-08), disclosed in the test + here — not a silent weakening; the re-aim still pins the 5 base keys and admits ONLY the 2 ratified v22 keys.
  - **prose-drift swept (close-gap-before-gate):** grepped the loaded trust/survivor layer (PROJECT.md · CONVENTIONS.md · GLOSSARY · docs/*) — **no doc pins the status --json closed key set** (CONVENTIONS:124 is a TDD lesson naming `milestone --json` as a past under-coverage example; GLOSSARY:37 pins the `seam` enum; PROJECT:102 is the v11 cross-check). The closed shape is stated ONLY in the **archived** `machine-state-json` TASK.md §3 (L21-23) — a historical record of what was frozen *then*, not a loaded doc. v22 supersedes it additively; the supersession is logged as an SDD §7 delta. → no loaded-layer contradiction → **change-request is closed; PASS is not blocked on prose.**
- [x] concurrency / timing — N/A: feature is READ-ONLY (status reads state + PROJECT.md, mutates nothing — `test_cue_is_read_only` proves state.json/PROJECT.md md5 unchanged). No shared-state write → no race.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`); no secrets; read-only render has no injection surface; no new/invented package
- [x] layering & dependencies follow CONVENTIONS.md — `_stage_criteria` mirrors `_exit_criteria`; `_graduation_ready` is the SINGLE shared source for text+json (no duplicated predicate); three-tree byte-identity restored + `ENGINE_MD5` re-aimed → 41f21621
- [x] a person reviewed and approved the change — **Tin Dang · 2026-06-08 · PASS** (residue ratified: re-aim option A + prose-drift swept clean)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_stage_criteria`←`_graduation_ready`; `_all_milestones_done`←`_graduation_ready`; `_graduation_ready`←`cmd_status` (text branch + --json branch); `GRADUATION_CUE`←the cue line. Every new symbol referenced.
- [x] DEAD-CODE (code) — no new unused/orphaned symbol; each new `def`/const has a call site (grep-confirmed)
- [ ] SEMANTIC (prose / non-code) — n/a (code change)

### GATE RECORD
Outcome: PASS — human-led gate (frozen test re-aimed + v4-1 contract reinterpreted, both ratified option A; prose-drift swept clean: no loaded-layer contradiction). Auto-gate correctly declined; outcome stamped only AFTER the human answered.
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-08

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `graduation_ready` flips false→true exactly once per stage (the "Cue fires" scenario as a live monitor); the withheld-states (milestones_incomplete · no_stage_criteria · criteria_unmet · project_unreadable) must keep `status` text byte-identical — drift there is a false-positive graduation invitation.
Spec delta for the next loop: the cue names an ACTION with no destination yet — `graduate-guide` (task 3) must land `graduate.md` and make the cue point to it; `graduation-analytics` (task 2) must supply the evidence the cue currently invites by assertion only.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [SDD · folded] **Contract-freeze must check whether the seam it extends was already frozen-closed by a prior contract.** Freezing §3 here (status --json +2 keys) silently collided with v4-1 `machine-state-json`'s closed 5-key set; the collision surfaced only at the full-suite run in verify (`test_json_surface_frozen` red), not at freeze. Fix the contract guide: before freezing an additive extension to an existing `--json`/state surface, grep for the prior contract that froze it and state additive-vs-closed explicitly. (evidence: a HARD-STOP + human change-request mid-verify that a freeze-time cross-check would have pre-empted)
- [ADD · folded] **Reinterpreting a frozen contract must sweep the loaded trust layer for stale prose, not just the test guard.** Re-aiming `test_json_surface_frozen` made the suite green, but a green suite cannot catch prose drift (tests don't exercise docs). The advisor-prompted sweep found the closed-shape statement lived only in the *archived* v4-1 TASK.md (not PROJECT/CONVENTIONS/GLOSSARY/docs) → safe — but the check was nearly skipped. Fix: add "sweep loaded-layer prose for the old shape" to the change-request checklist (close-gap-before-gate). (evidence: blind-spot caught at the gate, not by any test)
- [DDD · folded] **The done-tally over `state["milestones"]` has an archive blind spot: every milestone archived → empty map → `bool(ms)` False → cue never fires.** Dogfood exercised the archived-*present* case; the all-archived case is unverified and is a real graduation path (a long-lived project archives finished milestones). `graduate-guide` (task 3) must decide the all-archived semantics — count archived milestones toward the done-tally, or document why not. (evidence: §1 assumption #2 flagged it lowest-confidence; no test covers it)
