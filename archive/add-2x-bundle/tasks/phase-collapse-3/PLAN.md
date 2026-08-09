# TASK: Engine: collapse 6 phases to 3 (direction·build·verify), freeze/gate compound-cross, back-compat read map

slug: phase-collapse-3 · created: 2026-07-16 · stage: mvp · risk: high
milestone: thin-engine-loop
autonomy: conservative
sensitivity: architecture
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Projected from milestone Ground (thin-engine-loop) + the confirmed scope: universalize W1's thin-lane 3-call corridor into THE phase model.
Feature: universal 3-phase task walk — `direction · build · verify`
Framings weighed: generalize W1's Direction-span freeze to every lane + a read-side legacy map (chosen) · keep 6 phases and only alias the recipe (rejected — leaves two state machines alive) · bulk-rewrite the 473 legacy task records (rejected — churn, audit noise, archive is read-only by convention)
Must:
<must>
  - M1 `new-task` lands `phase: direction` in state.json AND the TASK.md marker, on EVERY lane (default · --fast · --oneshot · --full; `--thin` becomes an accepted no-op with a deprecation note)
  - M2 `freeze --by <name> --cross` from `direction` crosses the whole front (spec+plan+tests) into `build` in ONE call for every lane, through the SAME floor machinery (_build_entry: tamper tripwire + §5 scope snapshot; the W1 thin branch becomes the only branch)
  - M3 `gate <outcome>` from `build` keeps the compound cross (build→verify + recorded outcome) — regression-pinned, byte-level behavior unchanged
  - M4 every lane's `new-task` output prescribes ≤3 total engine calls (the spent new-task + freeze --cross + gate)
  - M5 legacy phase values (`specify · scenarios · ground · plan · contract · tests`) normalize to `direction` at READ time through ONE accessor; status/freeze/guide/report behave on old records; ZERO task-file or archive rewrites
  - M6 `phase <name> [slug]` accepts `direction | build | verify | done`; a legacy name is accepted, MAPPED to its 3-phase home, and noted in the output
</must>
Reject:
<reject>
  - `phase <token outside the 4 ∪ legacy set> [slug]` -> refused by the parser (argparse invalid choice, exit ≠ 0); stored phase unchanged
  - `freeze --cross` while §3 still carries the template contract -> "contract_not_drafted" (floor unchanged)
  - `freeze --cross` without the well-formed ⚠ flag -> "unflagged_freeze" (floor unchanged)
  - `gate` at `direction` (nothing frozen) -> refused by the existing pre-build floor; task state unchanged
</reject>
After:
<after>
  - A default-lane task walks `new-task → freeze --by --cross → gate PASS` to done: exactly 3 engine calls, every floor (frozen §3 · red-suite snapshot · tamper tripwire · scope lock · recorded gate) intact
  - All 206 live + 267 archived legacy records read cleanly everywhere the engine reads a phase
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ read-side normalization through one accessor covers EVERY phase consumer (status · freeze · guide · report · audit · mine · waves) — lowest confidence because phase reads are scattered across ~18 call sites; if wrong: an old task renders at a wrong phase or a gate misroutes — caught by the engine suite + audit, but a missed site ships a confusing surface
  - [ ] the 8 recipe-pinning test files (named in §5) migrate forward cleanly — the pins assert VALUE text, not floor semantics
  - [ ] `--thin` as a no-op keeps test_thin_engine_call_floor green (it asserts the prescribed-call count, not the flag's effect)
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: default lane starts at direction   # M1
  Given a fresh project
  When `new-task tweak` runs with no lane flag
  Then state.json records phase "direction"
  And the TASK.md phase marker reads "direction"

Scenario: every lane prescribes three calls   # M4
  Given a fresh project
  When `new-task` runs on the default, --fast, and --oneshot lanes
  Then each output prescribes only `freeze --by <name> --cross` and `gate` as remaining calls (≤3 total with new-task)

Scenario: one freeze call crosses the whole front   # M2
  Given a direction-phase task whose §3 is drafted and ⚠-flagged and whose §4 suite is red
  When `freeze --by "Tin Dang" --cross` runs
  Then §3 stamps FROZEN @ v1 and the phase lands "build" in that same call
  And the tests→build tamper snapshot and §5 scope snapshot were captured (heal/re-cross machinery armed)

Scenario: gate keeps the compound cross   # M3
  Given a build-phase task with its floor satisfied
  When `gate PASS` runs
  Then the task crosses build→verify and records PASS in one call

Scenario: legacy record reads as direction   # M5
  Given a state.json task whose stored phase is "plan" (and siblings at "specify" · "tests")
  When `status` and `freeze --by --cross` run
  Then each treats the task as direction-phase — status renders it, freeze crosses it
  And no task file or archive entry is rewritten

Scenario: phase command maps a legacy name   # M6
  Given any task
  When `phase plan <slug>` runs
  Then the stored phase becomes "direction" and the output notes the mapping

Scenario: unknown phase token refused   # R1
  Given any task
  When `phase shipping <slug>` runs
  Then the parser refuses it (exit ≠ 0)
  And the task's stored phase is unchanged

Scenario: template contract cannot freeze   # R2
  Given a direction-phase task whose §3 is still the scaffold template
  When `freeze --by --cross` runs
  Then it fails with "contract_not_drafted"
  And the phase stays "direction" and no snapshot is written

Scenario: unflagged bundle cannot freeze   # R3
  Given a drafted §3 with no well-formed ⚠ flag
  When `freeze --by --cross` runs
  Then it fails with "unflagged_freeze"
  And the phase stays "direction"

Scenario: no gate before the freeze   # R4
  Given a direction-phase task
  When `gate PASS` runs
  Then it is refused by the pre-build floor
  And the task's phase and gate record are unchanged
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): add_engine/constants.py:PHASES (the 6-value enum → 4 + legacy choices; ENGINE_PKG_MD5 re-aims) · add.py:cmd_new_task — lane flags + the recipe block (thin branch at `thin = bool(getattr(args,"thin",...))`, recipe prints) · add.py:cmd_freeze — `_min_freeze_phase` ("specify" if is_thin else "plan") + the `--cross` compound block (thin branch sets transit marker "tests" → `_build_entry` → "build") · add.py:cmd_gate — the build→verify compound tick (kept, regression-pinned) · add.py:_legacy (read-map home: already maps ground/contract/scenarios) · add.py:_PHASE_SECTIONS · add.py:_FRONT_PHASES ("specify","plan","tests") · add.py:_phase_index · add.py:_build_entry (the floor: tamper + scope snapshots) · add.py:_sync_task_marker · engine_pin.py:ENGINE_MD5 (re-aim on ship)
Context (working folder): .add/SEAMS.md (one add.py entry — verify, repin if line-anchored) · tmp/ (commit-msg files) · .add/tooling/add.py (gitignored dogfood twin — sync after ship)
Honors (patterns / conventions): validate-then-write (cmd_freeze discipline) · warn-never-block for nudges, `_die` for floors · the engine records/never classifies · stdlib-only, no new deps · engine edits re-aim ENGINE_MD5 with the one-prior trim policy · bundled twin `add-method/src/add_method/_bundled/tooling/add.py` stays byte-identical to canonical
Seams consulted: none line-anchored (SEAMS.md checked — symbol-pinned entries only)
Anchors the contract cites: constants.PHASES · cmd_new_task · cmd_freeze · cmd_gate · _legacy · _PHASE_SECTIONS · _FRONT_PHASES · _build_entry · _sync_task_marker · engine_pin.ENGINE_MD5 · engine_pin.ENGINE_PKG_MD5
Issues/Risks: phase reads are scattered (~18 sites) — normalization MUST be one accessor applied at read, or a missed site renders wrong · 8 test files value-pin the 5-call recipe/`advance --to plan` text (named in §5 scope) — migrate forward, never weaken · W1's `--thin` branch is subsumed — the flag stays as a no-op so W1's census test and any script keep working · the §5 Scope line must stay ONE physical line (engine bug #25: wrapped scope silently truncates)
Related intent: milestone thin-engine-loop goal (≤3 calls · 6→3 · loop-in-SKILL) · glossary "direction phase" · GLOSSARY "route" (persona-routes-depth builds on this enum)
Ground SHA: 21a6ef7 — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
add.py new-task <slug> [--fast|--oneshot|--full] [--thin: accepted no-op + note]
  -> state.tasks[slug].phase = "direction" (every lane) · TASK.md marker "direction"
  -> prints the 3-call recipe: freeze --by <name> --cross · gate <outcome>
add.py freeze --by <name> --cross            (task at direction; §3 drafted + ⚠-flagged)
  -> §3 FROZEN @ vN · direction crossed into build in this call via _build_entry
     (tamper tripwire + §5 scope snapshot captured — the W1 floor, now universal)
  4xx -> error: "contract_not_drafted" | "unflagged_freeze"     (floors unchanged)
add.py gate PASS|RISK-ACCEPTED|HARD-STOP     (from build)
  -> compound-cross build→verify + exactly one recorded outcome (unchanged behavior)
add.py phase <direction|build|verify|done|legacy-name> [slug]   (legacy -> mapped + printed note)
  4xx -> parser-refused (argparse invalid choice, exit != 0; state unchanged)
READ MAP (one accessor, applied wherever a phase is read):
  specify|scenarios|ground|plan|contract|tests -> direction · build/verify/done unchanged
Schema: state.json tasks[slug].phase — writes narrow to {direction,build,verify,done};
  legacy values remain on disk for old records and normalize on read (no bulk rewrite)
```

Glossary deltas: none new — realizes the milestone's "direction phase" entry
Status: FROZEN @ v2 — approved by Tin Dang 2026-07-16 (v2 = scope widened at verify: the recipe-pin migration swept the whole suite + the ch02 docs ripple; ratified via the recorded wordy-test authorization and the gate decision — contract shape unchanged)
Reported: yes — banner/ARC/SHAPE freeze card rendered in-session before the stamp; approved via guided choice
Least-sure flag surfaced at freeze:
  ⚠ [contract] the read-map accessor must cover every phase-read site (~18 scattered) — if one is missed an old record renders wrong; cost: confusing surface, caught by suite + audit.

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/` `add-method/.add/tooling/` `add-method/docs/02-the-flow.md` `add-method/docs/appendix-c-glossary.md` `add-method/diagrams/CHECKLIST.md` `add-method/../02-the-flow.md` `.add/SEAMS.md` `.add/docs/` `tmp/`
Strategy (ordered batches): 1. one phase-read accessor + legacy map (M5) — land it first so every later batch reads through it · 2. new-task → direction on every lane + 3-call recipe (M1, M4) · 3. freeze --cross universal — collapse the is_thin conditional into the only path (M2) · 4. phase/advance legacy mapping + notes (M6; advance inside direction becomes a friendly no-op pointing at freeze --cross) · 5. migrate the 8 recipe value-pin tests forward (declared, never weakened) · 6. re-aim ENGINE_MD5 · sync bundled + dogfood twins · SEAMS sanity
Approach (domain strategy): generalize the PROVEN W1 corridor instead of writing a new state machine — freeze reuses _build_entry's floor verbatim; compat is read-side only (from §1 framing "generalize + read map")
Data strategy: phase writes narrow to the 4-value enum; reads normalize through the one accessor — agrees with the Contract READ MAP/Schema
Pattern: validate-then-write + warn-never-block (Honors), the same pattern cmd_freeze already follows
Optimization stance: call-count first — the 3-call walk is the budget; ⚠ least-trusted facet: read-map coverage across the scattered phase-read sites (mitigation: accessor + full-suite sweep); risk: high → add-advisor consulted at verify via the 3-lens sweep
Persona (required): methodology-engine-dev
Spawn isolation (default): inline — sequential engine surgery in one file; a worktree spawn would fork state.json mid-milestone (stated reason)
Known-problem fixes: recipe value-pins → migrate forward, or DELETE where the pin is pure wording (human-authorized wordy-test removal, milestone shared decision 2026-07-16; floor tests never deleted) + `re-cross --by` if the tamper snapshot trips (recorded lesson) · §5 Scope stays ONE physical line (engine bug #25) · phase-name pins → grep the census before renaming any printed phrase · never ground against the dogfood twin (diverged once already — sync from canonical)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must and Reject has one executable test; the compound-gate regression pin included
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_default_lane_starts_at_direction: arrange fresh project / act new-task / assert state phase == "direction" + marker synced · covers: M1
  - test_every_lane_prescribes_three_calls: act new-task on default·fast·oneshot / assert prescribed calls ≤3, no `advance` verb in the recipe · covers: M4
  - test_freeze_cross_universal_from_direction: arrange drafted+flagged §3, red §4 / act freeze --by --cross / assert FROZEN @ v1 AND phase == "build" in one call · covers: M2
  - test_freeze_cross_arms_tamper_floor: same arrange / assert the tests→build snapshot exists after the cross (floor armed, not skipped) · covers: M2
  - test_gate_compound_cross_regression: arrange green build-phase task / act gate PASS / assert verify crossed + outcome recorded in one call · covers: M3
  - test_legacy_phase_values_read_as_direction: arrange state.json tasks stored at "plan"/"specify"/"tests" / act status + freeze --cross on one / assert rendered+crossed, files unrewritten · covers: M5
  - test_phase_cmd_maps_legacy_name: act `phase plan <slug>` / assert stored "direction" + mapping note · covers: M6
  - test_phase_cmd_rejects_unknown: act `phase shipping <slug>` / assert parser refusal (exit ≠ 0), stored phase unchanged · covers: R1
  - test_freeze_floors_unchanged: act freeze --cross on template §3 then on unflagged §3 / assert "contract_not_drafted" then "unflagged_freeze", phase stays direction · covers: R2, R3
  - test_no_gate_before_freeze: act gate PASS at direction / assert refused, phase + gate record unchanged · covers: R4
</test_plan>

Tests live in: `add-method/tooling/test_phase_collapse.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: as planned (batches 1–4 and 6 in order), with one self-improvement at batch 5 — the recipe-pin migration swept far wider than the 8 declared files (the whole suite reads the retired walk: 372 reds across ~49 files), so the migration ran as 3 parallel rule-sheet subagents (floor-gates · constants-ladder · output-pins) over disjoint file sets plus an orchestrator pass, under the recorded wordy-test authorization; 34 old-walk value pins deleted, every floor test migrated. Two engine gaps the tests exposed were folded in: check's marker-parity now normalizes legacy names (the zero-rewrite promise), and guide stops re-teaching a passed freeze. Docs ripple (ch02 mermaid ×4 trees + CHECKLIST bands + SEAMS re-pin) closed before the gate.
Safety rule (feature-specific): the freeze --cross compound is validate-then-write — every refusal fires before ANY phase/state/snapshot write; a crash mid-cross may never leave a frozen §3 with an unarmed tamper floor
Code lives in: `add-method/tooling/add.py`
Constraints: do NOT change any test or the frozen §3 contract (the 8 recipe-pin migrations are declared in §3/§5, recorded at verify); stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 3114 tests OK (exit 0) on 9afa0ef, incl. the fresh-checkout guard
- [x] coverage did not decrease — 34 deleted tests were old-walk value pins; every floor migrated and test_phase_collapse.py adds 11 pins on the new walk (net: same floors, new walk covered)
- [x] no test or contract was altered during build — beyond this task's DECLARED migration work, sanctioned by §3 v2 + the recorded re-cross; the frozen Contract SHAPE is unchanged
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe — validate-then-write preserved: every _build_entry refusal fires before any state/snapshot write (proved by the stall-phase asserts across the migrated floor suites)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib-only diff; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — LEGACY_PHASES lives in constants.py beside PHASES; normalization at the read accessors only
- [x] a person reviewed and approved the change — Tin Dang, gate decision 2026-07-16 (ratify v2 + gate PASS)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a fresh temp project walks new-task → freeze --by --cross → gate to done in 3 calls — confirmed by the walkthrough transcript recorded at the gate
- [x] `status` on a pre-collapse record (stored phase "plan") renders it at direction with zero task-file diffs — confirmed by the status output + a clean git diff over .add/tasks
- [x] the full engine suite (311 files, recipe pins migrated or removed per the authorization) is green — confirmed by the suite run pasted at the gate
- [x] ENGINE_MD5/ENGINE_PKG_MD5 re-aimed once; bundled + dogfood twins byte-identical to canonical — confirmed by the md5 triple pasted at the gate

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — tests drive the real CLI and assert the engine's own phase tokens (direction/build/verify) and error codes; no invented formats
- [x] WIRING (code) — LEGACY_PHASES read in _phase_index · _normalize_phase_tokens · cmd_advance/--to · cmd_phase · cmd_reopen · parser choices · check marker-parity; _POST_FREEZE_DIRECTION_ACTION read by both cmd_guide surfaces
- [x] DEAD-CODE (code) — is_thin branch removed with the crossing blocks it guarded; --thin flag retained as a DOCUMENTED no-op (compat), not an orphan
- [x] SEMANTIC (prose / non-code) — ch02 flow chapter + diagrams/CHECKLIST.md read in full; the 3-phase subgraph overlay keeps every prose claim (loopback rule, solid/dashed semantics) true

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol the §3 Contract cites still resolves in the current tree — cmd_new_task/cmd_freeze/cmd_advance/cmd_phase/_build_entry/PHASES/LEGACY_PHASES all exercised live by test_phase_collapse.py + the 3-call walkthrough
- [x] anchors that moved: _declared_scope def 5934→5915 (SEAMS.md re-pinned in this task); no silent moves

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self (orchestrator over 3 migration subagents) · adversarially checked: every subagent file-set re-run independently; deleted-test census pulled from git diff (not agent reports — agents returned empty reports); caught + reverted one over-narrow regex migration (template phase_marker seam) and one premature docs-red left to stand would have been masked

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — no secret/exec/net surface touched; error paths fail closed (_die before writes)
2. Concurrency: CLEAR — atomic-write discipline untouched; state_write_failed floor re-proven post-collapse (test_state_hardening migrated, green)
3. Architecture: CLEAR — one read-side map + one shared crossing stack REDUCES the state machine; legacy grammar isolated in constants
Verdict: PASS
Residue: none
Binding: advisory — architecture

### GATE RECORD
Reported: yes — the evidence bundle (suite verdict · 3-call transcript · legacy render · md5 4-way parity · deletion census · scope census) rendered to the human before this outcome
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-16

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-task engine-call count on the next bench WM (the milestone's census verifier) · legacy-record render errors in status/audit after ship

### Decisions (ADR)
- [AI] specify — chose generalize W1's Direction-span freeze to every lane + a read-side legacy map; rejected keep 6 phases and only alias the recipe (rejected — leaves two state machines alive) · bulk-rewrite the 473 legacy task records (rejected — churn, audit noise, archive is read-only by convention)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang 2026-07-16 (v2 = scope widened at verify: the recipe-pin migration swept the whole suite + the ch02 docs ripple; ratified via the recorded wordy-test authorization and the gate decision — contract shape unchanged))
- [AI] build — approach: generalize the PROVEN W1 corridor instead of writing a new state machine — freeze reuses _build_entry's floor verbatim; compat is read-side only (from §1 framing "generalize + read map")
- [AI] build — data strategy: phase writes narrow to the 4-value enum; reads normalize through the one accessor — agrees with the Contract READ MAP/Schema
- [AI] build — pattern: validate-then-write + warn-never-block (Honors), the same pattern cmd_freeze already follows
- [AI] build — optimization stance: call-count first — the 3-call walk is the budget; ⚠ least-trusted facet: read-map coverage across the scattered phase-read sites (mitigation: accessor + full-suite sweep); risk: high → add-advisor consulted at verify via the 3-lens sweep
- [AI] build — strategy used: as planned (batches 1–4 and 6 in order), with one self-improvement at batch 5 — the recipe-pin migration swept far wider than the 8 declared files (the whole suite reads the retired walk: 372 reds across ~49 files), so the migration ran as 3 parallel rule-sheet subagents (floor-gates · constants-ladder · output-pins) over disjoint file sets plus an orchestrator pass, under the recorded wordy-test authorization; 34 old-walk value pins deleted, every floor test migrated. Two engine gaps the tests exposed were folded in: check's marker-parity now normalizes legacy names (the zero-rewrite promise), and guide stops re-teaching a passed freeze. Docs ripple (ch02 mermaid ×4 trees + CHECKLIST bands + SEAMS re-pin) closed before the gate.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

