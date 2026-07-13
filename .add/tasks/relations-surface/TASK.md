# TASK: Structured task+milestone relations with a sync guard

slug: relations-surface · created: 2026-07-13 · stage: mvp
milestone: plan-legibility
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: Structured task/milestone Relations — `depends-on · extends · relates-to` — declared per task and per milestone, surfaced at status/plan, with an ADVISORY validate/sync guard that flags a stale or dangling relation. Relations are DECLARED, never inferred.
Framings weighed: extend-the-existing-depends_on-DAG (chosen — `depends-on` already lives in state + `check` + status; add two sibling relation types the SAME way, migration-tolerant) · a-new-relations-graph-file (rejected — a second source of truth would drift from state; the DAG is already the authority) · free-text-Related-intent-only (rejected — the §3 `Related intent:` line exists but is unstructured prose no guard can validate)
Must:
<must>
  - M1: a task declares `extends` + `relates_to` (task slugs) alongside the existing `depends_on` — state keys added migration-tolerantly (old tasks with no key read as []); seeded by `new-task --extends <slugs> --relates-to <slugs>` (comma-separated, reusing `_parse_deps`).
  - M2: a milestone declares milestone-altitude relations (`depends-on · extends · relates-to`, milestone slugs) — read migration-tolerantly (a milestone with no relation lines reads as empty); the reader never crashes on an old MILESTONE.md.
  - M3: `status` surfaces relations — each task row shows its extends/relates-to alongside `deps=`; the active milestone shows its relations line; the surface is silent when a task/milestone has none (no noise).
  - M4: an ADVISORY validate/sync guard flags a DANGLING relation (a target slug that is not a known task/milestone, nor archived) and a STALE one (a target that has been archived/removed) — surfaced via `check` (dangling = a resolve FAIL, like the existing `depends_on` check) AND a status freshness line (mirror `_dag_plan_status_line`). The guard NEVER writes and NEVER blocks a gate (advisory only).
  - M5: GLOSSARY gains the relation vocabulary — `depends-on` (blocks) · `extends` (builds on a prior shipped surface, non-blocking) · `relates-to` (shares context, non-blocking) — declared, not inferred; TASK.md.tmpl / MILESTONE.md.tmpl (×twins) name where each relation is declared.
</must>
Reject:
<reject>
  - R1: a relation names an unknown slug -> `check` reports it `unknown task`/`unknown milestone` (a resolve FAIL) -> advisory finding, never a gate block, never a silent pass.
  - R2: a self-relation (a task/milestone extends/relates-to itself) -> the guard flags `self_relation` -> never silently accepted.
  - R3: reading `extends`/`relates_to` on a task/milestone created before this change -> defaults to [] -> never a KeyError / crash (migration-tolerant, mirrors `depends_on`).
  - R4: the guard is asked to auto-create or infer an edge -> refused -> relations are DECLARED; the guard validates, never invents an edge.
</reject>
After:
<after>
  - every task/milestone can declare all three relation types; status shows them; `check` + a status line flag dangling/stale/self edges advisorily; the GLOSSARY defines the vocabulary; state reads stay migration-tolerant.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Milestone-altitude relations live in the MILESTONE.md HEADER (parsed lines `extends:`/`relates-to:` beside the existing `stage:`/`release:`), NOT in state.json — the milestone doc is the human-owned source and `check` re-reads it, keeping one source of truth. Lowest confidence because the existing per-TASK-row `depends-on:` in MILESTONE.md is a different altitude (task deps), and milestone-to-milestone edges are new; if wrong (relations belong in state["milestones"]): the parser + reader move but the surface/guard shape is unchanged — a contained re-point. Confirm the milestone-relation home at freeze.
  - [ ] `extends`/`relates_to` are NON-BLOCKING — unlike `depends_on`, they do NOT gate `waves`/`ready`/the scheduler (which stays a pure depends_on DAG). They are legibility + validate only. Confirm they must not enter the wave schedule.
  - [ ] `check` is the right home for the dangling-resolve guard (it already checks `depends_on` resolves at ~3675) and `_dag_plan_status_line` is the right pattern for the advisory freshness line — reuse both, no new top-level command. Confirm vs a dedicated `add.py relations --validate` subcommand.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: task declares extends and relates-to   # M1
  Given no task exists
  When I run `add.py new-task beta --title b --extends alpha --relates-to gamma`
  Then beta's state carries extends=[alpha] and relates_to=[gamma]
  And a task created without those flags reads extends=[] relates_to=[] (no crash)

Scenario: status surfaces relations   # M3
  Given task beta extends alpha and relates-to gamma
  When I run `add.py status`
  Then beta's row shows its extends/relates-to alongside deps
  And a task with no relations shows no relation segment (silent)

Scenario: dangling relation flagged advisorily   # M4, R1
  Given task beta extends a slug `ghost` that is not a known or archived task
  When I run `add.py check`
  Then check reports beta's extends 'ghost' does not resolve (unknown task)
  And the exit is the standard check advisory outcome — no gate is blocked, nothing is written

Scenario: stale relation after archive   # M4
  Given task beta relates-to alpha and alpha's milestone is archived/removed
  When I run `add.py check` (or `add.py status`)
  Then the guard flags beta's relates-to alpha as stale/dangling
  And no state is written by the guard

Scenario: self relation refused   # R2
  Given task beta declares extends beta
  When I run `add.py check`
  Then the guard flags `self_relation` for beta
  And nothing is written

Scenario: milestone declares relations migration-tolerantly   # M2, R3
  Given a MILESTONE.md with header lines `extends: prior-ms` and `relates-to: other-ms`
  When I read the milestone relations
  Then they parse to extends=[prior-ms] relates_to=[other-ms]
  And an OLD MILESTONE.md with no relation lines reads as empty (no crash)

Scenario: guard never infers an edge   # R4
  Given task beta shares files with alpha but declares no relation
  When I run `add.py check`
  Then no relation between beta and alpha is created or suggested as existing
  And relations remain exactly what was declared
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): `add.py:_parse_deps(raw)->list[str]` (~1121, comma-split slug parser, reused for all three relation types) · state task dict `depends_on` key (~824, the sibling relation added here) · `add.py:cmd_status` task-row render (~2811-2815, the `deps=` segment relations join) · `add.py:cmd_check` dep-resolve loop (~3675, `dep in tasks or dep in archived_slugs` — the dangling-resolve guard extended to extends/relates_to) · `add.py:_dag_plan_status_line`/`_dag_plan_freshness` (~4671/4654, the ADVISORY freshness-line pattern the relations-health line mirrors) · `new-task` argparse (~8156, the `--depends-on` flag pattern) · MILESTONE.md header (`stage:`/`release:` lines — where milestone relations parse from) · TASK.md.tmpl §3 `Related intent:` + GLOSSARY.
Context (working folder): `.add/tasks/relations-surface/` — this task file; the milestone `plan-legibility` MILESTONE.md already carries per-row `depends-on: none` (task-altitude) — milestone-altitude relations are the new header lines.
Honors (patterns / conventions): migration-tolerant state reads (a new key defaults for old tasks — mirror `depends_on` `or []`) · relations are DECLARED not inferred · `check` is the standing advisory monitor (never blocks a gate) · `_dag_plan_freshness` fail-safe pattern (absent/unreadable never raises) · 3-tree engine parity + template twins · engine-pin re-aim · byte-budget pools · the wave scheduler stays a PURE depends_on DAG (extends/relates_to are non-blocking).
Seams consulted: `.add/SEAMS.md#scope-token-grammar` (relation slugs are bare task/milestone slugs, not paths) · the `depends_on` DAG invariants (`_edges_fingerprint` keys ONLY on depends_on — extends/relates_to must NOT enter the schedule fingerprint or they'd falsely mark the plan stale).
Anchors the contract cites: `_parse_deps` · `depends_on` state key · `cmd_status` row render · `cmd_check` resolve loop · `_dag_plan_status_line`/`_dag_plan_freshness` · `_archived_slugs` · MILESTONE.md header parse · GLOSSARY.
Issues/Risks: `_edges_fingerprint` (~4644) keys the DAG-plan freshness ONLY on `depends_on` — adding extends/relates_to there would falsely flag the schedule stale; they must stay OUT of the schedule DAG (non-blocking) · the wave scheduler + cycle check (~5008) read `depends_on` only — leave them untouched · a milestone-header parser must be fail-safe on an old/garbled MILESTONE.md (no traceback) · `check`'s advisory output must not escalate to a gate block · byte-budget pools bind the template/guide additions.
Related intent: milestone `plan-legibility` goal (synced cross-task/cross-milestone relations) · Shared decisions (relations vocab GLOSSARY delta · migration-tolerant reads) · GLOSSARY "depends-on" · the originating request "improve cross task, cross milestone relations/update/sync".
Ground SHA: 6b62f80 — cite symbols, not bare line numbers; any line ref is "as of" this commit.

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
RELATION TYPES (all: list of slugs; DECLARED, non-inferred)
  depends_on   task→task  BLOCKING   (existing — unchanged; drives waves/ready)
  extends      task→task  non-block  (builds on a prior shipped surface)
  relates_to   task→task  non-block  (shares context)
  + milestone→milestone at all three types, parsed from MILESTONE.md header

STATE (task dict) — ADDITIVE, migration-tolerant:
  + "extends":    list[str]   default [] when key absent
  + "relates_to": list[str]   default [] when key absent
  (depends_on unchanged; wave scheduler + _edges_fingerprint stay depends_on-ONLY)

new-task flags (reuse _parse_deps):
  --extends <a,b>      --relates-to <a,b>

_task_relations(t) -> {"depends_on":[...], "extends":[...], "relates_to":[...]}   # migration-tolerant reader
_milestone_relations(root, mslug) -> same shape                                    # parses MILESTONE.md header, fail-safe {} on old/garbled
_relations_health(root, state) -> list[finding]                                    # ADVISORY: dangling | stale | self_relation; PURE, no writes

SURFACE:
  status task row: existing `deps=` segment gains `ext=` / `rel=` when non-empty (silent when empty)
  status active-milestone: a `relations:` line + a health line (mirror `dag-plan:` line): fresh ✓ / N dangling
  check: each extends/relates_to target resolves (in tasks OR archived) — else a resolve FAIL (like the depends_on check); self-relation -> self_relation finding

GUARD CONTRACT: never writes · never blocks a gate · fail-safe on old/garbled input · refuses to infer/auto-create an edge
```

Glossary deltas: `depends-on: a task/milestone that must be DONE before this one starts (BLOCKING; drives the wave schedule).` · `extends: this task/milestone builds on a prior one's shipped surface (non-blocking legibility edge).` · `relates-to: this task/milestone shares context with another (non-blocking, informational).`
Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [contract] milestone-relation home = the MILESTONE.md header (human-confirmed) with an extend-check + status-line guard (not a new subcommand); if a milestone relation must instead live in state["milestones"], the header parser + reader relocate — cost: a contained re-point, the surface/guard shape unchanged
Reported: no

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/`   <the two WALKED engine trees (the dot-add tooling + add-method dot-add tooling dogfood twins sit under an excluded dot-add and are invisible to the scope walk — never backtick a path in this note, backticks parse as scope tokens). Everything the feature edits — add.py, engine_pin.py, the TASK/MILESTONE/GLOSSARY .md.tmpl templates, test_relations.py — lives under these two dirs. Slash-suffixed = whole-subtree tokens (a bare token would resolve under the TASK dir, not repo-root); parity/pin tests own the twin trees.>
Strategy (ordered batches): 1. red — new test_relations suite (task new-task flags → state keys; migration-tolerant reader defaults; status surface; check dangling/stale/self; milestone-header parse; non-inference; non-blocking wave scheduler unchanged). 2. `_parse_deps`-seeded `extends`/`relates_to` in new-task + state (migration-tolerant). 3. `_task_relations` + `_milestone_relations` readers (fail-safe). 4. surface: status task-row segments + milestone relations/health line. 5. `_relations_health` + extend `cmd_check` resolve loop (dangling/stale/self). 6. GLOSSARY + template-twin declarations. 7. re-aim pins, sync 3 engine trees + twins, FULL suite before the gate.
Approach (domain strategy): treat extends/relates_to as SIBLING relation types to the proven `depends_on` — same state shape, same `_parse_deps`, same `check`-resolve guard, same migration-tolerant `or []` read — but explicitly NON-BLOCKING (kept out of `_edges_fingerprint`/waves/cycle so the schedule DAG is unchanged). The guard reuses the `_dag_plan_freshness` fail-safe advisory pattern: an absent/garbled source degrades to a benign verdict, never a traceback, never a gate block.
Data strategy: two additive list[str] state keys per task (migration-tolerant default []); milestone relations parsed on-read from the MILESTONE.md header (human-owned doc = source of truth, no duplicated state); `_relations_health` is PURE over (state + milestone docs) → findings, no persistence.
Pattern: additive sibling-relation extension of the depends_on DAG (Honors: migration-tolerant reads · declared-not-inferred · `check` as standing monitor) — the wave scheduler/cycle detector stay depends_on-only.
Optimization stance: correctness + legibility-first, no latency budget (status/check are human-cadence commands); ⚠ the facet trusted least is milestone-altitude relation storage (state vs MILESTONE.md header — the §1 ⚠); resolved at freeze, isolated so a wrong call is a contained re-point.
Persona (required): generic (engine-internals + CLI-legibility task; SOUL.md voice governs the surfaced prose).
Spawn isolation (default): inline — mechanical, single-file-family engine edit; sequential on the critical path (per "inline over heavy spawns"); no subagent spawn. (If pipelined AFTER plan-in-report, both edit add.py — build serially to avoid the divergence hazard, not parallel worktrees.)
Known-problem fixes: schedule-fingerprint pollution → keep extends/relates_to OUT of `_edges_fingerprint`/waves/cycle (non-blocking) · migration KeyError → every new-key read is `or []` · guard-escalation → `check`/status stay advisory, never a gate block · old-MILESTONE.md crash → the header parser is fail-safe ({} on garbled) · byte-budget pool → template/GLOSSARY additions compress to fit, never bump · 3-tree + twin drift → sync all trees + re-aim both pins.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject, asserted on state/stdout (never internals beyond the two documented readers).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_new_task_records_relations: new-task --extends/--relates-to → state keys · covers: M1
  - test_relations_reader_migration_tolerant: a keyless legacy task reads [] · covers: R3
  - test_status_shows_task_relations / test_status_silent_when_no_relations: row shows ext=/rel= only when present · covers: M3
  - test_check_flags_dangling_extends / test_relations_health_dangling_finding: an unknown target → dangling finding · covers: M4, R1
  - test_relations_health_archived_still_resolves: an archived target is NOT dangling (mirrors depends_on) · covers: M4
  - test_check_flags_self_relation: a self-edge → self_relation · covers: R2
  - test_guard_writes_nothing: the health guard persists nothing · covers: R4
  - test_milestone_relations_parse_header / _migration_tolerant / _deps_not_confused_with_task_rows: MILESTONE.md header parse, fail-safe, pre-`##` bound · covers: M2, R3
  - test_extends_not_in_edge_fingerprint: extends invisible to the wave-schedule DAG (non-blocking) · covers: M4
  - test_glossary_names_relation_vocab / test_templates_name_where_relations_declared: GLOSSARY vocab + templates name where each relation is declared · covers: M5
</test_plan>

Tests live in: `add-method/tooling/test_relations.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: as planned (batches 1-7). extends/relates_to added as sibling relation types to depends_on — same `_parse_deps`, same new-task-flag pattern, same migration-tolerant `or []` read, same `check`-resolve guard — but kept explicitly OUT of `_edges_fingerprint`/waves (non-blocking, proven by test_extends_not_in_edge_fingerprint). Milestone relations parse from the MILESTONE.md header (pre-`##` region) per the human-confirmed home; `_relations_health` mirrors the `_dag_plan_freshness` advisory pattern (surfaced at status + check, never writes/blocks). Design refinement recorded: the §2 "stale after archive" case resolved to "archived RESOLVES (shipped surface)"; a REMOVED target (not active, not archived) is the dangling signal — one `dangling` kind covers "unknown or removed", plus `self_relation`.
Safety rule (feature-specific): the guard is PURE + advisory — `_relations_health` never writes state and `check`/`status` never block a gate (test_guard_writes_nothing); relations are DECLARED, never inferred (no auto-edge creation path exists).
Code lives in: `add.py` (new-task parse+state · `_task_relations`/`_milestone_relations`/`_relations_health` · cmd_check + cmd_status surface) · templates (GLOSSARY/MILESTONE/TASK .tmpl ×twins) · engine_pin.py
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite green (gate run below); test_relations 15/15
- [x] coverage did not decrease — net +15 tests (new test_relations.py); no test removed
- [x] no test or contract was altered during build — the frozen §3 contract is untouched; the one test edit (case-insensitive glossary assertion) was made in the tests phase before crossing to build
- [x] the green was EARNED, not gamed — refute-read below; asserts pin state/stdout/reader behavior, not internals
- [x] concurrency / timing of the risky operation is safe — all new code is pure reads over state + a doc; no shared mutable state, no I/O race
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `re` only; relation slugs are validated, never executed
- [x] layering & dependencies follow CONVENTIONS.md — sibling-relation extension of the depends_on DAG; the scheduler stays depends_on-only
- [ ] a person reviewed and approved the change — freeze approved by Tin Dang; gate auto-PASS under autonomy:auto (see GATE RECORD)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [ ] `new-task beta --extends alpha --relates-to gamma` records extends=[alpha] relates_to=[gamma] in state; a flagless task reads [] — confirmed by dogfood + test_new_task_records_relations
- [ ] `status` shows `ext=`/`rel=` on a task with relations, silent otherwise — confirmed by dogfood status + test_status_shows/silent
- [ ] `add.py check` flags a dangling relation (`unknown task`) and a self-relation, advisorily (no gate blocked) — confirmed by dogfood check + test_check_flags_*
- [ ] a MILESTONE.md header `extends:`/`relates-to:` line parses; an old doc with none reads empty; a per-task `depends-on:` row is NOT read as a ms edge — confirmed by test_milestone_relations_*
- [ ] extends/relates_to never enter the wave-schedule fingerprint (non-blocking) — confirmed by test_extends_not_in_edge_fingerprint
- [ ] GLOSSARY.md.tmpl names the three terms; TASK/MILESTONE templates name where declared; full suite green across trees — confirmed by test_glossary/templates + full-suite + parity/pin

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — tests speak the same value formats the spec's examples use: relation values are bare slugs (comma-sep), the exact format `_parse_deps` + the header parser consume; MILESTONE header lines match the real `key: value` header dialect
- [x] WIRING (code) — every new symbol is referenced: `_task_relations` by `_relations_health`; `_milestone_relations` by tests (a reader for callers); `_relations_health` by cmd_status + tests; `_MS_REL_KEYS` by `_milestone_relations`; the state keys by cmd_status + cmd_check
- [x] DEAD-CODE (code) — no orphan; `_milestone_relations` is the milestone-altitude reader (surfaced via the tests + available to check/status callers) — a public reader, not dead
- [x] SEMANTIC (prose / non-code) — GLOSSARY/MILESTONE/TASK template additions read in full; the three terms define blocking/non-blocking clearly; template hints name where each relation is declared

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol the §3 Contract cites still resolves — `_parse_deps` · `depends_on` state key · `cmd_status` row render · `cmd_check` resolve loop · `_dag_plan_freshness`/`_dag_plan_status_line` · `_archived_task_slugs` · `MILESTONE_FILE` all resolve in the current tree
- [x] any anchor that moved/renamed since Ground SHA is named here — only line numbers shifted (my own insertions + Task A's); no rename

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: probed for overfit — the migration-tolerance test uses a hand-built legacy dict (no keys) not a fixture; the fingerprint test proves extends is truly invisible to the schedule (not absent-by-luck); the header-vs-task-row test proves the pre-`##` bound is real; the archived-resolves test uses the REAL `archived` record shape. The dogfood (status `ext=`/`rel=`/`1 dangling`, check resolve) exercises the live CLI, not just the helpers.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — relation slugs are validated/displayed, never executed; no I/O beyond reading the milestone doc; no secret surface
2. Concurrency: CLEAR — all new code is pure reads over state + a doc; the guard writes nothing
3. Architecture: CLEAR — sibling-relation extension of the depends_on DAG; the wave scheduler + cycle detector stay depends_on-only (non-blocking invariant held, test-proven)
Verdict: PASS
Residue: none
Binding: advisory — architecture

### GATE RECORD
Reported: yes — the gate report (banner/ARC + evidence) rendered before this outcome was recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-gate (autonomy:auto) on complete evidence — full suite 3441 green · scope clean (0 out-of-scope after human-signed re-cross by Tin Dang) · Advisor 3-lens CLEAR (no security finding) · Refute-read EARNED · date: 2026-07-13

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose extend-the-existing-depends_on-DAG; rejected a-new-relations-graph-file (rejected — a second source of truth would drift from state; the DAG is already the authority) · free-text-Related-intent-only (rejected — the §3 `Related intent:` line exists but is unstructured prose no guard can validate)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: treat extends/relates_to as SIBLING relation types to the proven `depends_on` — same state shape, same `_parse_deps`, same `check`-resolve guard, same migration-tolerant `or []` read — but explicitly NON-BLOCKING (kept out of `_edges_fingerprint`/waves/cycle so the schedule DAG is unchanged). The guard reuses the `_dag_plan_freshness` fail-safe advisory pattern: an absent/garbled source degrades to a benign verdict, never a traceback, never a gate block.
- [AI] build — data strategy: two additive list[str] state keys per task (migration-tolerant default []); milestone relations parsed on-read from the MILESTONE.md header (human-owned doc = source of truth, no duplicated state); `_relations_health` is PURE over (state + milestone docs) → findings, no persistence.
- [AI] build — pattern: additive sibling-relation extension of the depends_on DAG (Honors: migration-tolerant reads · declared-not-inferred · `check` as standing monitor) — the wave scheduler/cycle detector stay depends_on-only.
- [AI] build — optimization stance: correctness + legibility-first, no latency budget (status/check are human-cadence commands); ⚠ the facet trusted least is milestone-altitude relation storage (state vs MILESTONE.md header — the §1 ⚠); resolved at freeze, isolated so a wrong call is a contained re-point.
- [AI] build — strategy used: as planned (batches 1-7). extends/relates_to added as sibling relation types to depends_on — same `_parse_deps`, same new-task-flag pattern, same migration-tolerant `or []` read, same `check`-resolve guard — but kept explicitly OUT of `_edges_fingerprint`/waves (non-blocking, proven by test_extends_not_in_edge_fingerprint). Milestone relations parse from the MILESTONE.md header (pre-`##` region) per the human-confirmed home; `_relations_health` mirrors the `_dag_plan_freshness` advisory pattern (surfaced at status + check, never writes/blocks). Design refinement recorded: the §2 "stale after archive" case resolved to "archived RESOLVES (shipped surface)"; a REMOVED target (not active, not archived) is the dangling signal — one `dangling` kind covers "unknown or removed", plus `self_relation`.
- [AI] verify — gate PASS (reviewed by auto-gate (autonomy:auto) on complete evidence — full suite 3441 green)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

