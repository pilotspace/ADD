# Quality — the TDD spec

project: AIDD / ADD Methodology · seeded: 2026-07-17 · stage: mvp

> Living document — how we know it works: test strategy, floors, evidence (TDD).
> Keep the sections below CURRENT (state, not history); lessons land under
> Deltas the moment they are learned: `add.py delta-append tdd "<lesson>"`.
> A delta that changes the standing picture is folded UP into the sections
> above it and marked `[folded]` — the Deltas list is the inbox, not the spec.

## Now
<!-- migrated from PROJECT.md §Spec (test-strategy lessons) @ fv66 (foundation-split) -->
- The regression floor is the full tooling suite (`add-method/tooling/./t`) + `add.py check`
  0-failed; targeted modules gate in-session, the full suite runs backgrounded/CI.

## Decisions that bind
- The suite IS the behavior contract for a prose compaction — wording slips surface only under the FULL suite, never a subset; gate compactions on the full run. [fv46 · skill-core-compact]
- A new CLI subcommand ripples into test_min_pillar LIFECYCLE + _NONZERO_OK classification + the tri-tree ENGINE_MD5 pin — pre-list those traps in §5 Known-problem fixes and the build is trap-free. [fv58 · components-validator]
- The guideline block has TWO lean guards, not one — `test_guidelines` pins no byte budget but `test_v8_onramp::test_block_stays_a_pointer` caps the WHOLE block at ≤22 non-blank lines; a freeze that measures only the first mis-sizes an inline addition. [fv61 · roster-portable-shape]
- YAML 1.1 parses a bare `on:` key as boolean True — a workflow-shape test must read `cfg.get("on", cfg.get(True))` or it silently asserts against a missing key. [fv49 · pages-deploy]

## Deltas (newest first)
- [open · 2026-07-22] lock-reclaim race probe flakes under CI runner contention — peak-holders=2 on slow 2-core runners, passes on rerun; 5 consecutive branch CI runs red until rerun. Widen the reclaim grace under CI or make the probe retry-tolerant (evidence: run 29893983512 fail→rerun-pass, 2026-07-22) (task:round-visible-runs)
<!-- prepended by `add.py delta-append tdd "<text>"` — one line per lesson, `- [open · <date>] <lesson>` + the active-task stamp; fold a delta upward, then retag [open]->[folded] -->
