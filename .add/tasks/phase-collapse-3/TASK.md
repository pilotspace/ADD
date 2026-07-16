# TASK: Engine: collapse 6 phases to 3 (direction·build·verify), freeze/gate compound-cross, back-compat read map

slug: phase-collapse-3 · created: 2026-07-16 · stage: mvp · risk: high
milestone: thin-engine-loop
autonomy: conservative   <!-- method-defining engine surgery: risk: high declared on the slug line; the verify gate is human-led (unguarded_high_risk_auto guard honored) -->
sensitivity: architecture
phase: build   <!-- specify→plan→tests→build→verify→done; plan unites grounding + frozen contract + build strategy -->

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

<!-- EXIT: the specify guide's exit_gate binds (rules + ranked ⚠ assumptions). -->

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

<!-- EXIT: the scenarios guide's exit_gate binds. -->

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
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — banner/ARC/SHAPE freeze card rendered in-session before the stamp; approved via guided choice
Least-sure flag surfaced at freeze:
  ⚠ [contract] the read-map accessor must cover every phase-read site (~18 scattered) — if one is missed an old record renders wrong; cost: confusing surface, caught by suite + audit.

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/constants.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_phase_collapse.py` `add-method/tooling/test_advance_fold_build_gate.py` `add-method/tooling/test_first_call_ergonomics.py` `add-method/tooling/test_hint_batch_ops.py` `add-method/tooling/test_guide.py` `add-method/tooling/test_kickoff_truth.py` `add-method/tooling/test_next_footer_engine.py` `add-method/tooling/test_status_orientation_diet.py` `add-method/tooling/test_thin_engine_call_floor.py` `add-method/src/add_method/_bundled/tooling/` `.add/SEAMS.md` `tmp/`
Strategy (ordered batches): 1. one phase-read accessor + legacy map (M5) — land it first so every later batch reads through it · 2. new-task → direction on every lane + 3-call recipe (M1, M4) · 3. freeze --cross universal — collapse the is_thin conditional into the only path (M2) · 4. phase/advance legacy mapping + notes (M6; advance inside direction becomes a friendly no-op pointing at freeze --cross) · 5. migrate the 8 recipe value-pin tests forward (declared, never weakened) · 6. re-aim ENGINE_MD5 · sync bundled + dogfood twins · SEAMS sanity
Approach (domain strategy): generalize the PROVEN W1 corridor instead of writing a new state machine — freeze reuses _build_entry's floor verbatim; compat is read-side only (from §1 framing "generalize + read map")
Data strategy: phase writes narrow to the 4-value enum; reads normalize through the one accessor — agrees with the Contract READ MAP/Schema
Pattern: validate-then-write + warn-never-block (Honors), the same pattern cmd_freeze already follows
Optimization stance: call-count first — the 3-call walk is the budget; ⚠ least-trusted facet: read-map coverage across the scattered phase-read sites (mitigation: accessor + full-suite sweep); risk: high → add-advisor consulted at verify via the 3-lens sweep
Persona (required): methodology-engine-dev
Spawn isolation (default): inline — sequential engine surgery in one file; a worktree spawn would fork state.json mid-milestone (stated reason)
Known-problem fixes: recipe value-pins → migrate forward, or DELETE where the pin is pure wording (human-authorized wordy-test removal, milestone shared decision 2026-07-16; floor tests never deleted) + `re-cross --by` if the tamper snapshot trips (recorded lesson) · §5 Scope stays ONE physical line (engine bug #25) · phase-name pins → grep the census before renaming any printed phrase · never ground against the dogfood twin (diverged once already — sync from canonical)

<!-- The freeze IS the one approval — it freezes the whole PLAN; lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). The Contract shape is HARD (tamper-guarded); Grounding + Build-strategy are SOFT (the builder may improve on the strategy, recording actual at §5/verify). Approved -> Status: FROZEN @ vN — approved by <name>; changing the frozen Contract = change request back to SPECIFY. Scope tokens, backticked, on the Scope line: `./…` = this task dir · a token with "/" = project root · a bare name = sibling of the previous token's dir · a DIRECTORY token covers its whole subtree · outside-root resolutions drop fail-closed · absent line = UNDECLARED (grandfathered — an undeclared task is never retro-red). The plan guide's exit_gate binds: frozen · every rejection contracted · names match GLOSSARY · anchors grounded · flag surfaced. -->

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

<!-- EXIT: the tests guide's exit_gate binds (red for the RIGHT reason). -->

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): the freeze --cross compound is validate-then-write — every refusal fires before ANY phase/state/snapshot write; a crash mid-cross may never leave a frozen §3 with an unarmed tamper floor
Code lives in: `add-method/tooling/add.py`
Constraints: do NOT change any test or the frozen §3 contract (the 8 recipe-pin migrations are declared in §3/§5, recorded at verify); stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

<!-- Scope-lock source: the §3 `Scope (may touch)` line; an out-of-scope build fails the gate (scope_violation); the build guide's exit_gate binds. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [ ] a fresh temp project walks new-task → freeze --by --cross → gate to done in 3 calls — confirmed by the walkthrough transcript recorded at the gate
- [ ] `status` on a pre-collapse record (stored phase "plan") renders it at direction with zero task-file diffs — confirmed by the status output + a clean git diff over .add/tasks
- [ ] the full engine suite (311 files, recipe pins migrated or removed per the authorization) is green — confirmed by the suite run pasted at the gate
- [ ] ENGINE_MD5/ENGINE_PKG_MD5 re-aimed once; bundled + dogfood twins byte-identical to canonical — confirmed by the md5 triple pasted at the gate

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] DIALECT — tests speak the same value formats the spec's examples use (spec-dialect floor): <what confirmed>
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced (the subsumed is_thin branch removed, not orphaned)
- [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [ ] every symbol the §3 Contract cites still resolves in the current tree — confirmed by <how / where>
- [ ] any anchor that moved/renamed since Ground SHA is named here, not left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: <agent-id | self>
1. Security: <CLEAR | HARD-STOP: finding>
2. Concurrency: <CLEAR | RESIDUE: finding>
3. Architecture: <CLEAR | RESIDUE: finding>
Verdict: <PASS | HARD-STOP>
Residue: <none | summary>
Binding: <yes — mechanical | advisory — <sensitivity>>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- Security is ALWAYS HARD-STOP; record exactly one outcome — no silent pass. The Advisor 3-lens and Refute-read verdicts are audit-measured (`advisor_verdict_unrecorded` · `refute_unrecorded`), never engine-blocked; a human spot-audit backstops anything unrecorded. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-task engine-call count on the next bench WM (the milestone's census verifier) · legacy-record render errors in status/audit after ship

### Decisions (ADR)
<harvested at done from §1/§3/§5/§6 — do not hand-edit; one actor-tagged line per decision, refilled only while this placeholder stands>

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
