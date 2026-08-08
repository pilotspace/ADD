# MILESTONE: Method ergonomics

goal: every recurring rule an agent must recall at a gate becomes a form the engine presents at that moment, cutting per-task ceremony across all execution paths without moving the safety floor
rationale: sub-milestone — a slice of the live lean/method-quality theme (extends lean-pass + flow-simplification; depends-on the advisor-gated-autonomy gate model; overlaps delta-drain's carried archived-delta-verbs delta, reopened here). Source: the 2026-07-06 whole-methodology review — 11 optimization items across the 8 steps × 5 competencies × 5 execution paths.
stage: mvp · status: active · created: 2026-07-06T14:10:45+00:00
release: 1.17.0

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  engine-scaffolded §6 verify record (audit lints collapse to one) · composed gate-decision answer (`gate --explain`) · bundle-phase advance compression + a legal post-freeze re-cross verb · single-source generation of the worker-contract stanzas across roster/streams/advisor · a `worktree-prep` command mechanizing streams' three documented footguns · fast-lane minimal §0 · SKILL.md↔run.md dedup (skill-lean reclaim) · batched intake+freeze presentation for task-bucket items · per-domain test-form mapping in 4-tests.md · delta verbs reaching archived tasks
Out: any change to the safety floor (frozen-contract immutability · security HARD-STOP · one human approval per contract — all untouched) · new autonomy levels or gate semantics · book chapter rewrites (pointer updates only) · parallel-streams redesign · non-Claude adapter implementations · release/graduation machinery

## Shared decisions & glossary deltas   (living — every task must honor these)
- "engine presents, agent fills": a recurring per-task obligation moves from prose-recall to an engine-stamped skeleton/answer; prose keeps only the WHY (extends the lean-over-budget-bump rule)
- skill-lean budget is the frozen floor: every guide-prose task must land net-≤0 bytes against the pool, or reclaim from the same guide (no rebaseline without human sign-off)
- ENGINE/PKG MD5 pins move only via the recorded pin-update path; every engine task re-pins in its own build, never mid-suite
- audit lint vocabulary is append-frozen: collapsing lints keeps the old tokens as aliases for one release before removal

## Shared / risky contracts (freeze these first)
- §6 VERIFY RECORD skeleton shape (block names + order — audit and guides both read it) -> owning task verify-record-scaffold
- `gate --explain` output contract (line format CI/agents can parse) -> owning task gate-explain

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] verify-record-scaffold    depends-on: none                    — engine stamps the §6 skeleton (expectations · 3-lens · deep-check · refute-read · Reported) at tests→build; audit collapses 4 lints to `verify_record_incomplete`; move the declare-before-build instruction to 4-tests.md
- [x] gate-explain              depends-on: none                    — `add.py gate --explain <slug>` prints the composed auto-pass/escalation answer from autonomy · risk · sensitivity · residue
- [x] bundle-advance            depends-on: none                    — `advance --to tests` collapses the bundle's bookkeeping crossings; `add.py re-cross` legally re-snapshots after a human-approved post-freeze test addition
- [x] worker-contract-sync      depends-on: none                    — one canonical boundary/return stanza template stamped into roster agents + streams/advisor blocks at sync time, with a parity test
- [x] worktree-prep             depends-on: none                    — `add.py worktree-prep <slug>` cuts the worktree, materializes gitignored engine/book, echoes the fork base into the WAVE.md row
- [x] fastlane-ground-lite      depends-on: none                    — fast-lane §0 minimal form: Touches + Anchors + Ground SHA required, the rest optional-with-default
- [x] archived-delta-verbs      depends-on: none                    — carry/drop/reopen-delta operate on archived on-disk TASK.md when slug ∉ state.tasks (reopens delta-drain's carried delta)
- [x] task-md-optimize          depends-on: none                    — leaner TASK.md.tmpl: trim instructional comment bloat, machine-parsed markers untouched (user-added 2026-07-06)
- [x] intake-freeze-batch       depends-on: none                    — task-bucket intake proposal may merge into the freeze presentation: one report, one answer (prose: intake.md · report-template.md)
- [x] domain-test-mapping       depends-on: none                    — 4-tests.md names a "test = any machine-checkable assertion" mapping with per-domain forms (metric threshold · reconciliation query · plan-diff)
- [x] skill-dedup               depends-on: fastlane-ground-lite, intake-freeze-batch, domain-test-mapping — SKILL.md keeps one line + pointer per item duplicated in run.md; reconciles the whole milestone's lean-budget ledger last

## Exit criteria (observable; map each to the task that delivers it)
- [x] At tests→build the engine writes an empty §6 VERIFY RECORD skeleton into TASK.md, and `audit` reports one `verify_record_incomplete` where it reported the 4 shape lints (verify: engine test)        (← verify-record-scaffold)
- [x] `add.py gate --explain <slug>` prints the composed gate path for any live task, matching the run.md rules (verify: engine test)        (← gate-explain)
- [x] A drafted bundle advances ground→tests in one call, and a post-freeze human-approved test addition re-crosses without tripping build_tampered (verify: engine test)        (← bundle-advance)
- [x] The boundary/return stanzas in the 5 roster agents hold one worker-contract floor, proven by a parity + floor-census guard (generation was the task's other half; DECLINED per the self-contained-prompt invariant — recorded in the task's §3) (verify: test_worker_contract_sync)        (← worker-contract-sync)
- [x] `add.py worktree-prep <slug>` yields a worktree whose engine runs and whose fork-base row is filled with the pasted echo (verify: engine test)        (← worktree-prep)
- [x] A --fast task's §0 passes check with the minimal form (verify: engine test)        (← fastlane-ground-lite)
- [x] `carry-delta`/`drop-delta`/`reopen-delta` succeed against an archived task slug (verify: engine test)        (← archived-delta-verbs)
- [x] TASK.md.tmpl is measurably smaller with every parser/census test green (verify: test suite + byte diff)        (← task-md-optimize)
- [x] intake.md + report-template.md document the merged task-bucket intake+freeze presentation (verify: guide test)        (← intake-freeze-batch)
- [x] 4-tests.md carries the per-domain test-form mapping (verify: guide test)        (← domain-test-mapping)
- [x] test_skill_lean passes with the pool at or below its pre-milestone floor (verify: test_skill_lean)        (← skill-dedup)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from feat/method-ergonomics (stacked on feat/sequential-default-and-fastlane-nudge) with the Close ship-review as body; human reviews + merges
- [ ] fold this milestone's confirmed deltas; drain any new carried ones
- [ ] bundle into the next MINOR release (release.md) — new engine verbs are features
