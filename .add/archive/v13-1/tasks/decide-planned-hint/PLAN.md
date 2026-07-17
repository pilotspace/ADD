# TASK: DECIDE NEXT shows n planned tasks not yet scaffolded

slug: decide-planned-hint · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: DECIDE NEXT names planned-but-unscaffolded tasks (v13 fold residue: the
  footer said "fold + archive" while 2 of 3 MILESTONE.md-planned tasks had no TASK.md)
Framings weighed: hint INSIDE the _decide_next string + additive rollup-JSON key
  (chosen: zero frozen-guard edits — the two --decide --json key-set pins stay
  byte-true) · new top-level key in the decide payload (rejected: breaks both
  frozen key-set guards; a ratified-but-noisy change for the same information) ·
  change the fold+archive precedence itself (rejected: the footer's frozen
  precedence is correct — the gap is MISSING information, not wrong ordering)
Must:
  - A pure helper parses MILESTONE.md's "## Tasks" list: lines `- [ ]`/`- [x]`
    whose first token is a VALID slug ([A-Za-z0-9_-]+ — template placeholders
    like <slug> never match); returns those with no .add/tasks/<slug>/TASK.md,
    in file order.
  - When that list is non-empty, the DECIDE NEXT line gains the suffix
    " — n planned not yet scaffolded: a · b" in EVERY surface that carries the
    footer (rollup · `report <ms> --decide` block · milestone --decide JSON's
    "decide" string).
  - report_data (rollup `--json`) gains ONE additive key `planned_unscaffolded`
    (list of slugs, [] when none) — outside every pinned key-set.
  - When the list is empty, every existing surface is byte-identical (exit
    criterion); the two frozen --decide --json key-set guards stay untouched.
Reject:
  - MILESTONE.md missing/unreadable -> no hint, no crash (fail-closed, OSError -> [])
  - template placeholder rows (`- [ ] <slug>`) -> never counted
After:
  - The fold+archive suggestion can no longer mask unscaffolded planned work;
    the orchestrator's manual MILESTONE.md cross-check (foundation v11) is
    mechanized in the engine.
Assumptions — least-sure first:
  ⚠ the slug is the FIRST whitespace-token after the checkbox in a Tasks row —
    least sure because MILESTONE.md is prose (authors could write "- [ ] the
    parser task"); evidence: all 14 milestone files in this repo use
    slug-first rows; if wrong: a phrase-first row is silently skipped by the
    valid-slug filter (fail-closed, cost: a hint missed, never a false hint)
  - [ ] the hint belongs at every footer surface, not only the rollup — the
    --decide block exists precisely for decision seams
  - [ ] suffix-in-string is acceptable to JSON consumers (the structured list
    lives in the rollup key; the decide payload carries it only as text)

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: unscaffolded planned tasks are named
  Given MILESTONE.md lists three task rows and only one has a TASK.md
  When report <ms> renders (and report <ms> --decide)
  Then the DECIDE NEXT line carries "2 planned not yet scaffolded" + both slugs

Scenario: the fold+archive blind spot is closed
  Given every SCAFFOLDED task is done but MILESTONE.md plans more
  When the rollup renders
  Then the footer still says fold + archive-milestone AND names the missing count

Scenario: rollup JSON carries the structured list
  Given the same fixture
  When report <ms> --json runs
  Then planned_unscaffolded equals the missing slugs
  And the --decide --json key set is EXACTLY the nine frozen keys

Scenario: byte-identical when nothing is missing
  Given every planned row has a TASK.md
  When every report surface renders
  Then no output contains "not yet scaffolded"

Scenario: template placeholders ignored
  Given MILESTONE.md still holds the scaffold row "- [ ] <slug>"
  When the rollup renders
  Then no hint appears

Scenario: missing MILESTONE.md fails closed
  Given the milestone directory has no MILESTONE.md
  When every report surface renders
  Then no hint, no crash, exit 0

Scenario: hint stays pure
  Given any fixture above
  When report and --json twins run
  Then the .add file set and state.json bytes are unchanged, every exit 0
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_planned_unscaffolded(root, mslug) -> list[str]    # NEW pure helper, fail-closed []
  # parse milestones/<mslug>/MILESTONE.md lines: ^- \[[ x~]\] ([A-Za-z0-9_-]+)\b
  # keep slugs with no tasks/<slug>/TASK.md file; file order; OSError -> []
report_data(...)  +1 additive key: "planned_unscaffolded": [...]   ([] when none)
_decide_next(state, d) -> str   # signature unchanged; when d carries a non-empty
  # planned_unscaffolded, append " — n planned not yet scaffolded: a · b"
render surfaces: rollup footer · render_decide_next · milestone --decide "decide"
  string — all inherit the suffix; EMPTY list -> byte-identical output everywhere
frozen seams untouched: decide --json key-set (9 keys) · decide facts {phase,
  gate, deps, tests} · footer precedence (HARD-STOP -> fold+archive -> ...)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front; suffix-in-string + additive rollup key accepted)   <!-- Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must + both Rejects; red tests assert rendered output /
JSON, never helper internals; the frozen key-set + byte-identical-when-empty
cases are green-by-design guards re-asserting what must not change.
Plan (one test per scenario):
  - test_hint_named_when_unscaffolded: 3 planned, 1 scaffolded → rollup + --decide
    both carry "2 planned not yet scaffolded" + both slugs
  - test_fold_archive_still_suffixed: scaffolded all done → footer has
    archive-milestone AND the hint (the original v13 blind spot)
  - test_rollup_json_additive_key: planned_unscaffolded == missing slugs; decide
    --json key-set still exactly the nine frozen keys (guard inside)
  - test_byte_identical_when_none: all planned scaffolded → "not yet scaffolded"
    absent from rollup, --decide, drill (guard)
  - test_placeholder_ignored: "- [ ] <slug>" row → no hint (guard)
  - test_missing_milestone_md_failclosed: MILESTONE.md deleted → no hint, exit 0 (guard)
  - test_hint_pure: file set + state hash unchanged across all surfaces (guard)

Tests live in: `add-method/tooling/test_planned_hint.py` (suite root, like every
prior tooling task) · MUST run red (hint absent) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): empty-list renders byte-identical everywhere; the
two frozen --decide --json key-set guards and the decide-facts key-set stay green untouched.
Code lives in: `add-method/tooling/add.py` (canonical) → synced ×3 (md5 parity).
Constraints: do NOT change any test or the contract; stdlib only; no new exit codes.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 381/381 (374 prior + 7 new), `add.py check` 194/0 (4 pre-existing warns)
- [x] coverage did not decrease — 7 tests added, none removed/weakened; red 3-for-the-right-reason
      (hint + JSON key absent pre-build) + 4 green-by-design guards (byte-identical-when-none ·
      placeholder ignored · missing-file fail-closed · purity); both frozen --decide --json
      key-set guards in test_decide_digest stayed green UNTOUCHED (the design goal)
- [x] no test or contract was altered during build — §3 untouched post-freeze; two mid-build
      defects fixed in the BUILD output, never a matcher: (1) the parser scanned the whole file
      and caught the exit-criteria "User can…" row -> scoped to ## Tasks sections; (2) _wrap
      split the hint phrase mid-token -> the hint renders as its OWN wrapped segment
- [x] concurrency / timing safe — pure read-side computation, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — the only read is
      MILESTONE.md, a file the report path already reads (_milestone_doc); no new file class,
      no write, stdlib only; nothing on this line to escalate
- [x] layering & dependencies follow CONVENTIONS.md — additive evolution honored (one new JSON
      key, hint absent -> byte-identical surfaces); 3-tree md5 parity
      dbe550df09ed6e699f1cbc2a9fd0ca19 ×3
- [x] a person reviewed and approved the change — Tin approved the frozen contract
      (one-approval front, 2026-06-05); gate auto-resolved on complete evidence per
      `autonomy: auto` (no deviation residue, security line genuinely empty)

### GATE RECORD
Outcome: PASS (auto-resolved on complete evidence — all green · loops dry · no residue ·
build touched exactly add.py ×3 + the new test file; live dogfood: v13-1's own rollup shows
no hint with all 3 tasks scaffolded, planned_unscaffolded = [])
Reviewed by: auto-gate under `autonomy: auto` · contract approved by Tin · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a phrase-first Tasks row (`- [ ] the parser task`)
silently skipped by the valid-slug filter (the accepted ⚠ — a missed hint, never a false
one); any new MILESTONE.md section whose heading starts with "Tasks" unexpectedly feeding
the parser.
Spec delta for the next loop: DECIDE NEXT is no longer state-only-blind — the plan-vs-state
diff is in the engine (v13's ADD residue closed); the foundation-v11 convention's "until the
engine grows a hint" clause is now satisfied, so the manual cross-check can retire at the
next fold.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [TDD · folded] a fixture that REUSES the scaffolded template inherits its example rows — the
    first red run counted the template's "User can…" exit criterion as a planned task; scope a
    prose parser to its section and make a guard of the template's own placeholders
    (evidence: phantom "User" slug in the first red run, fixed by ## Tasks scoping)
  - [ADD · folded] a convention can be written to RETIRE: foundation-v11's decide-next cross-check
    named its own sunset condition ("until the engine grows a hint"), making the fold-out
    decision mechanical once this task shipped (evidence: this task + the v11 convention text)
