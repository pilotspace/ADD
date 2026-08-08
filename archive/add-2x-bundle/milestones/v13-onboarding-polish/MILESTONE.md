# MILESTONE: Onboarding & Orchestration Polish

goal: starting and running an ADD project feels guided and self-tuning — setup proposes the run-mode, first milestone, and per-drive domain depth; the engine schedules a milestone's tasks by their dependency DAG; and the AI's voice (SOUL.md) self-improves toward the human's wording
rationale: new-major enhancement theme (human-confirmed intake 2026-06-15) — no active milestone's goal covered guided setup, DAG-scheduled implementation, or a self-improving voice; sized as ONE milestone at the human's request (split_required folded into one line by choice)
stage: mvp · status: active · created: 2026-06-15

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  an `add.py waves` scheduler (topological waves + critical path + tier hint) and the streams.md
     strategy section it feeds; setup surfacing the autonomy×streams comparison table and proposing
     parallel+auto as the DEFAULT (confirm-to-keep); setup proposing a concrete first milestone
     (goal+flow+scenarios) after the scan/interview; a multi-turn per-drive domain deep-dive that
     captures ADRs and auto-completes all four drives in auto mode; SOUL.md as a living "voice" doc;
     an observe→confirm→rewrite loop that self-improves SOUL.md from the human's wordings + flow
Out: a TUI/visual DAG render; auto-spawning workers without human confirm; reading Claude's private
     memory store directly (SOUL learns from in-session wordings/flow, not the memory files);
     changing the irreducible one-approval-per-contract floor; multi-project shared SOUL

## Shared decisions & glossary deltas   (living — every task must honor these)
- the DAG scheduler READS deps from state; it never mutates state or reorders the human's intent
- the parallel+auto DEFAULT is a project-level choice recorded at setup (PROJECT.md Key Decisions),
  never a silent global flip — streams.md is updated to name the new opt-out default
- SOUL.md is identity-owned: the AI proposes voice deltas; the human's confirm is the only writer
- a "voice delta" follows the deltas.md status lifecycle (open→confirmed) like a foundation delta
- auto-mode "full context" never skips the contract-freeze approval — auto deepens drafting, not gates

## Shared / risky contracts (freeze these first)
- `add.py waves` output grammar — render-blind testable: wave list, critical path, tier hint, --json -> owning task dag-scheduler
- SOUL.md section schema — the stable target the self-improve loop rewrites -> owning task soul-artifact

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] dag-scheduler           depends-on: none           — `add.py waves` computes topological waves + critical path + tier hint from milestone deps; streams.md gains the strategy section
- [ ] setup-run-mode          depends-on: dag-scheduler  — setup shows the autonomy×streams comparison table + proposes parallel+auto as default (confirm-to-keep); streams.md default flips
- [ ] setup-suggest-milestone depends-on: none           — after brownfield scan / greenfield interview, setup proposes the first milestone with goal + flow + scenarios
- [x] setup-domain-deepdive   depends-on: none           — multi-turn per-drive (DDD·SDD·UDD·TDD) domain deepening that captures ADRs; auto mode auto-completes all four with full context
- [x] soul-artifact           depends-on: none           — SOUL.md living doc: schema, scaffolded at setup, shipped in the installer, read each session; voice content human-owned
- [x] soul-self-improve       depends-on: soul-artifact  — observe phase emits a confirmable "voice delta" from wordings+flow; confirm rewrites SOUL.md (deltas.md lifecycle + fold path)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py waves` emits topological waves + critical path + a per-tier hint, tested render-blind   (← dag-scheduler)
- [x] streams.md documents the DAG strategy AND the new parallel+auto default                          (← dag-scheduler + setup-run-mode)
- [x] setup prints the autonomy×streams comparison table and proposes parallel+auto, confirm-to-keep   (← setup-run-mode)
- [x] after the scan/interview, setup proposes a concrete first milestone with flow + scenarios         (← setup-suggest-milestone)
- [x] setup runs a multi-turn per-drive domain deep-dive capturing ADRs; auto mode auto-completes 4     (← setup-domain-deepdive)
- [x] SOUL.md exists, is scaffolded at setup, shipped by the installer, and read each session           (← soul-artifact)
- [x] the observe phase emits a confirmable voice delta that, once confirmed, rewrites SOUL.md          (← soul-self-improve)
