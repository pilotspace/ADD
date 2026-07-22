# Quality — the TDD spec

project: AIDD / ADD Methodology · seeded: 2026-07-17 · stage: mvp

> Living document — how we know it works: test strategy, floors, evidence (TDD).
> Keep the sections below CURRENT (state, not history); lessons land under
> Deltas the moment they are learned: `add.py delta-append tdd "<lesson>"`.
> A delta that changes the standing picture is folded UP into the sections
> above it and marked `[folded]` — the Deltas list is the inbox, not the spec.

## Now
<the standing TDD picture — replace this placeholder as the project firms; task-delta updates, never a full re-scan>

## Decisions that bind
<the TDD-lens decisions every task must honor — one line each, with the task/ADR that set it — or leave the placeholder until the first one lands>

## Deltas (newest first)
- [open · 2026-07-22] lock-reclaim race probe flakes under CI runner contention — peak-holders=2 on slow 2-core runners, passes on rerun; 5 consecutive branch CI runs red until rerun. Widen the reclaim grace under CI or make the probe retry-tolerant (evidence: run 29893983512 fail→rerun-pass, 2026-07-22) (task:round-visible-runs)
<!-- prepended by `add.py delta-append tdd "<text>"` — one line per lesson, `- [open · <date>] <lesson>` + the active-task stamp; fold a delta upward, then retag [open]->[folded] -->
