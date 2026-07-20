# TASK: Guard open SPEC deltas — compact blocks, status/report nudge

slug: spec-delta-guards · created: 2026-06-16 · stage: mvp
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

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_compact` (~2352-2382) — the HARD guard seam. Today it refuses `open_deltas_unfolded` when a member task still has an open COMPETENCY delta (`_collect_open_deltas` ∩ member_set, line 2378). The SYMMETRIC guard: refuse `open_spec_deltas_unresolved` when a member has an open SPEC delta — placed right after, BEFORE the "every precondition passed" move (validate-all-then-move preserved).
  - `add-method/tooling/add.py:cmd_status` (~1156-1160) — the soft nudge surface. Today prints `deltas  : N open — consolidate at milestone close` (read-only, silent when none). Add a symmetric `spec    : N open SPEC delta(s) — resolve via new-task --from-delta / drop-delta` line.
  - `add-method/tooling/add.py:cmd_milestone_done` (~2281-2286) — close-point nudge. Today prints `note: N open deltas to consolidate`. Add the symmetric open-SPEC nudge (resolve, don't fold).
  - `add-method/tooling/add.py:report_data` (3160-3194) + its renderer (the `LEARNINGS (N carried)` line ~3428) — the report already surfaces the first open SPEC delta per task via the `observe` field (task 1), but never COUNTS open SPEC deltas milestone-wide. Add an `open_spec` count to the summary + a render nudge.
  - `add-method/tooling/add.py:_collect_open_spec_deltas` (3996) — the task-1 READER reused by ALL surfaces (filtered to member tasks for compact; project-wide for status). NO new collector needed.
Context (working folder):
  - tests (unittest): `add-method/tooling/test_*.py`; NEW `test_spec_delta_guards.py`. Existing compact/status/report tests must stay green (additive guard + nudge). Baseline green: 1177 OK.
  - the SUBCOMMAND census (`test_min_pillar` LIFECYCLE) is NOT tripped — this task adds NO subcommand (it extends compact/status/report/milestone-done behavior). Confirmed verb-vs-flag lesson from task 2.
  - parity: 3 md5-identical `add.py` copies + `prepare_bundle.py` + `engine_pin.py` re-sync after the canonical edit.
Honors (patterns / conventions):
  - SYMMETRY with the competency machine: every place competency deltas are guarded/nudged (`open_deltas_unfolded` · `deltas : N open` · the milestone-close note), SPEC deltas get the parallel — but RESOLVE (seed/drop), never FOLD (SPEC is a separate track, never consolidated into the foundation).
  - validate-all-then-write: the compact guard refuses BEFORE the first rename, so a reject leaves tree + state byte-for-byte unchanged (the existing cmd_compact contract).
  - read-only nudges: status/report/milestone-done print only; they never mutate (the existing fold-pressure nudge discipline, v11).
Anchors the contract cites: `cmd_compact` · `open_spec_deltas_unresolved` · `cmd_status` spec-nudge · `cmd_milestone_done` spec-nudge · `report_data.open_spec` · `_collect_open_spec_deltas`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: SPEC-delta GUARDS — a compact HARD-block + status/milestone-done/report NUDGES that make an open SPEC delta impossible to lose silently (symmetric with the competency machine — but RESOLVE via seed/drop, never FOLD).
Framings weighed: mirror the competency guard/nudge surfaces 1:1 (chosen — the open_deltas_unfolded guard + the `deltas : N open` nudges already define the shape) · a single global check in `add.py check` only (rejected — compaction is where an open SPEC delta actually vanishes from `deltas`, so the hard block must live in cmd_compact) · auto-drop open SPEC deltas at compact (rejected — that SILENTLY discards a forward hand-off; preventing silent loss is the whole point)
Must:
<must>
  - `compact <milestone>` REFUSES `open_spec_deltas_unresolved` when ANY task in the project has an open SPEC delta (PROJECT-WIDE — human-chosen at the freeze) — placed directly after the `open_deltas_unfolded` competency guard, BEFORE the first rename (validate-all-then-move: a reject leaves tree + state byte-for-byte unchanged). DELIBERATELY broader than the member-scoped competency guard: a SPEC delta is a project-global forward hand-off, so a clean slate (every open SPEC delta resolved) is required before ANY compaction. The message names the offending task(s) + points to the resolution verbs (`new-task --from-delta` / `drop-delta`).
  - `status` prints a read-only `spec    : N open SPEC delta(s) — resolve: new-task --from-delta / drop-delta` line when ≥1 open SPEC delta exists PROJECT-WIDE; SILENT when none (symmetric to the `deltas  : N open` line; never mutates).
  - `milestone-done` prints a symmetric `note: N open SPEC delta(s) to resolve (seed/drop) — review: add.py deltas` when ≥1 open SPEC delta exists PROJECT-WIDE (matches the competency note at line 2282, which also sums project-wide); silent when none.
  - `report` (report_data + renderer) carries a PROJECT-WIDE `open_spec` count in its summary (uniform with compact/status/milestone-done — human-chosen at the freeze; all four surfaces use the same project-wide total); the renderer shows a nudge line when >0 (the dashboard already lists the first open SPEC delta per task via the `observe` field — task 1).
  - Every nudge is READ-ONLY (no state/file mutation); the compact guard is the ONLY surface that blocks. SPEC is a SEPARATE track — the language is RESOLVE (seed/drop), never FOLD/consolidate.
</must>
Reject:
<reject>
  - `compact <ms>` with ≥1 open SPEC delta anywhere in the project -> "open_spec_deltas_unresolved"
  - (existing compact rejects UNCHANGED: milestone_not_archived · unknown_milestone · already_compacted · archive_destination_exists · source_files_missing · open_deltas_unfolded)
</reject>
After:
<after>
  - NO milestone can be compacted while any open SPEC delta exists anywhere in the project (project-wide) — every open SPEC delta must be seeded or dropped first; `status` / `milestone-done` / `report` each surface the same project-wide open count; a compact reject leaves the tree byte-for-byte unchanged; full unittest suite + 3-copy md5 parity stay green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ PROJECT-WIDE compact guard (human-chosen at the freeze, change-request from member-scoped) means a milestone CANNOT compact while ANY task anywhere holds an open SPEC delta — lowest confidence because the dogfood repo itself accumulates open SPEC deltas across active milestones, so a future compaction may require resolving unrelated deltas first; if wrong (too strict): compaction friction. Cost: MEDIUM — mitigated because the status/milestone-done nudges keep every open SPEC delta visible, so resolution (seed/drop) is a known step. Deliberate divergence from the competency member-scoped guard, by design.
  - [x] compact, status, milestone-done AND report are now ALL project-wide — fully uniform (human-chosen: report's open_spec is the project-wide total too, even though report renders one milestone's tasks). One count, one source: `len(_collect_open_spec_deltas(root))`.
  - [ ] cosmetic: the `spec    :` status label + its position (right after `deltas  :`) and the exact nudge wording.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: compact refuses while ANY task (project-wide) holds an open SPEC delta
  Given an archived milestone to compact, and ANOTHER task elsewhere with "- [SPEC · open] x (evidence: e)"
  When I run `compact <ms>`
  Then it exits non-zero with "open_spec_deltas_unresolved" naming the offending task
  And the .add tree and state.json are byte-for-byte unchanged (no archive/ move)

Scenario: compact proceeds once every open SPEC delta (project-wide) is resolved
  Given the same setup but the offending SPEC delta is now "[SPEC · dropped] x (evidence: e)"
  When I run `compact <ms>`
  Then it succeeds and moves the bundle to .add/archive/<ms>/
  And no open_spec_deltas_unresolved is raised

Scenario: status nudges open SPEC deltas, silent when none
  Given a project with one "- [SPEC · open]" delta somewhere
  When I run `status`
  Then the output contains a "spec" line reporting 1 open SPEC delta
  And after the delta is dropped, `status` prints no "spec" open line
  And status writes nothing (state.json byte-unchanged across both runs)

Scenario: milestone-done nudges a member's open SPEC delta
  Given an active milestone whose only task is done but holds "- [SPEC · open] y (evidence: e)"
  When I run `milestone-done <ms>` (exit criteria met)
  Then the output contains a "note" naming open SPEC delta(s) to resolve
  And the close still succeeds (the nudge never blocks)

Scenario: report carries an open_spec count
  Given a milestone with one member open SPEC delta
  When I run `report <ms> --json`
  Then the summary carries open_spec == 1
  And report writes nothing (read-only)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py compact <milestone>
  ok  -> moves the bundle to .add/archive/<ms>/   (UNCHANGED behavior)
  err -> "open_spec_deltas_unresolved"   ANY project task has an open SPEC delta (PROJECT-WIDE) —
                                         names them + points to new-task --from-delta / drop-delta;
                                         tree+state BYTE-UNCHANGED. AFTER open_deltas_unfolded, BEFORE move.
         (+ existing UNCHANGED: milestone_not_archived · unknown_milestone · already_compacted ·
            archive_destination_exists · source_files_missing · open_deltas_unfolded)

add.py status
  +line -> "spec    : N open SPEC delta(s) — resolve: new-task --from-delta / drop-delta"
           N = PROJECT-WIDE open SPEC count; printed only when N>0; SILENT at 0; READ-ONLY

add.py milestone-done <ms>
  +line -> "note: N open SPEC delta(s) to resolve (seed/drop) — review: add.py deltas"
           N = PROJECT-WIDE open SPEC count; printed only when N>0; SILENT at 0; NEVER blocks the close

add.py report <ms> [--json]
  summary.open_spec = N   (PROJECT-WIDE open SPEC count — uniform with the other surfaces); renderer adds a nudge line when N>0; READ-ONLY

Internal: ONE count, ONE source — every surface uses `len(_collect_open_spec_deltas(root))` (project-wide).
          NO member filter (the change-request unified report with the rest).
Files/State: compact guard writes NOTHING on a reject; all three nudges are pure reads (no save_state, no _atomic_write).
```

Least-sure flag surfaced at freeze: [spec] PROJECT-WIDE everywhere (human-chosen change-request from member-scoped) — compact refuses, and status/milestone-done/report all count, while ANY task anywhere holds an open SPEC delta. DELIBERATELY broader than the member-scoped competency open_deltas_unfolded (line 2378). Risk: the dogfood repo accumulates open SPEC deltas across active milestones, so a future compaction may require resolving unrelated deltas first (compaction friction), and `report <ms>` shows a count that may exceed that milestone's own tasks; mitigated because status/milestone-done keep them visible so seed/drop is a known step. ONE count, ONE source (`len(_collect_open_spec_deltas(root))`) — maximal uniformity. (Runner-up [contract]: the `spec :` label + nudge wording — cosmetic, resolved here.)

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-16
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject has a test (5 scenarios → ≥5 tests); full suite stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_compact_blocks_open_spec_delta_projectwide: archive milestone A (clean), put [SPEC · open] on a task in ANOTHER milestone B / compact A / assert exit≠0 + "open_spec_deltas_unresolved" naming B's task + .add tree & state.json byte-unchanged (hash before==after) — proves PROJECT-WIDE, not member-scoped
  - test_compact_proceeds_when_spec_resolved: same but flip the offending delta to [SPEC · dropped] / compact A / assert exit 0 + .add/archive/A/ exists
  - test_status_nudges_open_spec_silent_when_none: inject one [SPEC · open] / status / assert a "spec" line with count 1; drop it / status / assert no "spec" open line; assert state.json byte-unchanged across both
  - test_milestone_done_nudges_open_spec: done task w/ [SPEC · open], criteria met / milestone-done / assert exit 0 + a "note" naming open SPEC delta(s)
  - test_report_counts_open_spec: exactly one [SPEC · open] anywhere in the project / report <ms> --json / assert summary["open_spec"]==1 (PROJECT-WIDE — even if the delta is on a non-member task) + state.json byte-unchanged
  - (regression) test_fold_nudge · test_report · test_archive_compaction stay green (additive: nudges silent on their no-open-SPEC fixtures; the new summary key is additive)
</test_plan>

Tests live in: `add-method/tooling/test_spec_delta_guards.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_spec_delta_guards.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py`
<!-- pre-declared: 3 byte-identical add.py copies + engine_pin re-pin + the new red suite. NO template change (no §7/template touch). NO subcommand added → test_min_pillar census NOT tripped (task-2 verb-vs-flag lesson). Downstream exact-match risk CHECKED & CLEARED before the freeze: test_fold_nudge fixtures use new-task (empty SPEC block → my additive nudges stay silent; its regex targets `deltas :`, not my `spec :`) · test_report never calls the compact COMMAND (its "compact" is a UI table) + asserts summary by KEY (additive open_spec is safe) · test_archive_compaction injects no [SPEC · open] (guard stays silent). If a downstream edit still surfaces it is a disclosed re-cross. -->
Strategy (ordered batches): 1. write the red suite test_spec_delta_guards.py · 2. cmd_compact: the symmetric `open_spec_deltas_unresolved` guard after open_deltas_unfolded (member-filtered, before the move) · 3. cmd_status: the `spec :` project-wide nudge after the `deltas :` nudge · 4. cmd_milestone_done: the member open-SPEC note after the competency note · 5. report_data: summary["open_spec"] (member count) + the renderer nudge line · 6. sync .add/tooling + prepare_bundle, re-pin engine_pin, assert 3-copy parity
Safety rule (feature-specific): the compact guard is validate-before-move — it refuses BEFORE the first rename, so a reject leaves tree + state byte-for-byte unchanged (the existing cmd_compact invariant); the nudges are pure reads (never save_state / _atomic_write).
Code lives in: `add-method/tooling/` (engine) — NOT this task's `./src/`.
Constraints: do NOT change any test's intent or the frozen contract; allow-list packages only (stdlib only); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1182 OK (0 fail); baseline 1177 → +5 new
- [x] coverage did not decrease — +5 tests; no test removed; existing compact/status/report/milestone-done suites stay green
- [x] no test or contract was altered during build — CONTRACT untouched; NO existing test edited (the pre-freeze downstream analysis held: test_fold_nudge/test_report/test_archive_compaction stay green; test_min_pillar NOT tripped — no subcommand added). NO §5 scope expansion, NO re-cross needed.
- [x] the green was EARNED — LIVE proof on the real dogfood project: `status` fires `spec : 3 open SPEC deltas` and `deltas` lists them (not fixtures); the suite proves PROJECT-WIDE via an offending delta on a NON-member task (test_compact_blocks_open_spec_delta_projectwide); the boundary test (proceeds-when-resolved) confirms no over-block.
- [x] concurrency / timing — N/A: read-only collectors + one validate-before-move guard; no shared state, no IO races. The compact guard refuses BEFORE the first rename (tree+state byte-unchanged on reject, asserted via snapshot hash).
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; no new dependency; no eval/shell/network. All four surfaces are pure reads except the existing compact move.
- [x] layering & dependencies follow CONVENTIONS.md — ONE source for all surfaces (`len(_collect_open_spec_deltas(root))`, the task-1 reader); no new collector, no new symbol, no parallel logic; 3-copy md5 parity restored (392b4e55a4ac01a022a9c4a46567b95f); engine_pin re-aimed newest-first.
- [x] a person reviewed and approved the change — Tin Dang, 2026-06-16 (gate PASS; project-wide change-request applied; no build deviations)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the task-1 reader `_collect_open_spec_deltas` now has 4 NEW live call sites: cmd_status (1163) · cmd_milestone_done (2295) · cmd_compact guard (2399) · report_data summary (3218); plus the renderer reads summary["open_spec"]. No NEW symbol defined.
- [x] DEAD-CODE (code) — zero new functions/constants; every change is an inline call to an existing collector. Nothing orphaned.
- [x] SEMANTIC (prose) — the §1/§3 project-wide change-request (compact + status + milestone-done + report all uniform) read in full; the render nudge format matches the contract; the milestone-close-cleanup observation recorded as a §7 spec delta

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-16   (project-wide change-request applied at the freeze; no test/contract/security finding; no §5 expansion)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `open_spec_deltas_unresolved` compact-reject rate · the `spec : N open` status count trend toward zero before a release

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task.
  - [SPEC · seeded] the project-wide compact guard has NO override — add a `compact --force` (or `--allow-open-spec`) escape hatch for when an UNRELATED open SPEC delta must not block an urgent compaction (evidence: the freeze flagged project-wide as a MEDIUM-cost risk — a cross-milestone open delta can wedge compaction; the competency guard has no force either, so this is a shared gap worth a unified flag) [→ compact-force-override]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [ADD · folded] pre-freeze downstream analysis (grep exact-match assertions + the subcommand census + compact-fixture SPEC injection) eliminated ALL mid-build surprises here — task 2 hit a census surprise + scope expansion; task 3 pre-checked the same classes and hit ZERO. Codify "scan downstream test assertions before freezing an additive engine change" as a §0/§5 step (evidence: task 3 needed no §5 expansion, no re-cross) [folded foundation-version 36]
  - [ADD · folded] seed a downstream task from a prior's SPEC delta via `new-task --from-delta`, not plain `new-task` — else the source delta stays `open` and (now) BLOCKS compaction even though the work is done; the live `status` showed 3 open SPEC deltas that tasks 2/3 had already implemented (evidence: the guard this task shipped surfaced its own milestone's un-seeded lineage — resolve at delta-resolution close) [folded foundation-version 36]
