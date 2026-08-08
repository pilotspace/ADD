# MILESTONE: Delta Resolution

goal: every delta — spec and competency — has a recorded, engine-driven resolution event, so a captured lesson is never a silent dangling line
rationale: new-major (human-confirmed intake 2026-06-16) — the delta system CAPTURES well but RESOLVES unevenly: a competency delta's fold is an error-prone hand-edit (no command), and the spec-delta is free text with NO closure concept at all (parse-and-report only). Both gaps let a captured delta drop silently.
stage: mvp · status: active · created: 2026-06-16

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a SPEC-delta resolution lifecycle (`[SPEC · open|seeded|dropped]`) as a SEPARATE track from competency deltas — its `### Spec delta` block, tag-aware parse + lint, and its own open-collector; the two resolution verbs (`new-task --from-delta <prior>` to seed, a drop path to dismiss) with `[→ <slug>]` stamp + `from_delta` state lineage; symmetry guards (compact blocks an open SPEC delta; status/report nudge unconsumed ones); and `add.py fold` to mechanize the competency-delta bookkeeping (flip open→folded + `[folded foundation-version N]` stamp + version bump)
Out: changing the five competencies or their fold ROUTING (deltas.md/fold.md routing table stays); auto-authoring the foundation CONTENT edit (fold mechanizes bookkeeping only — the human still owns the consolidation prose); migrating already-archived tasks' legacy free-text spec-delta field; any new release cut (release stays HELD)

## Shared decisions & glossary deltas   (living — every task must honor these)
- **SPEC is a separate track, not a 6th competency.** A spec-delta shares the `[TAG · status]` LINE shape but resolves into a TASK (seeded), never into the foundation (folded). Never fold a SPEC delta; never seed a competency delta. Keep the collectors/guards/nudges parallel-but-separate.
- **resolution = a recorded consumption event.** `seeded` (→ a task) and `dropped` (explicit dismissal) close a SPEC delta; `folded` (→ the foundation) closes a competency delta. `open` = unresolved. The engine RECORDS the transition at consumption; it never guesses a resolution.
- **status sets are tag-scoped.** competency tags accept `open|folded|rejected`; SPEC accepts `open|seeded|dropped`. The grammar must reject a cross-set state (e.g. `[SPEC · folded]`, `[SDD · seeded]`).
- **fold mechanizes bookkeeping, not judgment.** `add.py fold` flips status + stamps + bumps the version AFTER the human has confirmed the consolidation; it does not decide WHAT consolidates and does not auto-write the foundation §Domain/§Spec content (engine stays judgment-free — `unconfirmed_fold` still applies).
- glossary deltas: add `spec-delta (resolution lifecycle)`, `seeded`, `dropped`, `from-delta lineage`; refine `fold` to note the engine now mechanizes the bookkeeping step.

## Shared / risky contracts (freeze these first)
- the `[SPEC · open|seeded|dropped]` line grammar + the `### Spec delta` block shape + whether `(evidence: …)` is required (render-blind testable) -> owning task spec-delta-grammar (riskiest — every other task builds on it; also settles legacy free-text back-compat)
- the seed/drop CLI surface + the `[→ <slug>]` stamp + the `from_delta` state shape -> owning task seed-and-drop
- the `add.py fold` CLI surface + the version-bump write contract (one bump per call vs per session) + what it stamps vs leaves to prose -> owning task fold-command

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] spec-delta-grammar   depends-on: none                              — introduce SPEC as a separate delta track: `### Spec delta` block + `[SPEC · open|seeded|dropped]` grammar, tag-aware parse/lint, an open-SPEC collector, `add.py deltas` surfaces them apart from competency learnings
- [x] seed-and-drop        depends-on: spec-delta-grammar                — the resolution verbs: `new-task --from-delta <prior>` (prefill §1 Feature, flip open→seeded + `[→ <new>]` stamp, record `from_delta` state) and a drop path (open→dropped)
- [x] spec-delta-guards    depends-on: spec-delta-grammar,seed-and-drop  — the can't-drop-silently net: `compact` blocks a member task with an open SPEC delta; `status`/`report` nudge unconsumed open SPEC deltas
- [x] fold-command         depends-on: none                              — `add.py fold <task> --comp <TAG>` flips a competency delta open→folded, stamps `[folded foundation-version N]`, bumps the PROJECT.md header version atomically (validate-all-then-write); updates fold.md

## Exit criteria (observable; map each to the task that delivers it)
- [x] A §7 `### Spec delta` block accepts `[SPEC · open|seeded|dropped]`, the lint rejects a cross-set state, and `add.py deltas` lists open SPEC deltas separately from competency learnings   (← spec-delta-grammar)
- [x] `add.py new-task --from-delta <prior>` prefills the new §1 Feature, flips the source SPEC delta to `seeded` with `[→ <new>]`, records `from_delta`; a drop path flips an open SPEC delta to `dropped`   (← seed-and-drop)
- [x] `add.py compact` refuses a task carrying an open SPEC delta, and `status`/`report` surface a nudge for each unconsumed open SPEC delta   (← spec-delta-guards)
- [x] `add.py fold <task> --comp <TAG>` flips the delta open→folded, writes the `[folded foundation-version N]` stamp, and bumps the PROJECT.md `foundation-version:` header atomically (a reject leaves tree + version byte-for-byte unchanged)   (← fold-command)
