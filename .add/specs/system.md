# System — the SDD spec

project: AIDD / ADD Methodology · seeded: 2026-07-17 · stage: mvp

> Living document — how it is built: architecture, contracts, data shapes (SDD).
> Keep the sections below CURRENT (state, not history); lessons land under
> Deltas the moment they are learned: `add.py delta-append sdd "<lesson>"`.
> A delta that changes the standing picture is folded UP into the sections
> above it and marked `[folded]` — the Deltas list is the inbox, not the spec.

## Now
<!-- migrated from PROJECT.md §Spec @ fv66 (foundation-split) -->
- The spec is a LIVING document: the active milestone (`.add/milestones/<slug>/MILESTONE.md`,
  see `add.py status`) + the frozen §3 contracts other work builds against are the current
  build truth; this file holds the cross-milestone SDD rules. Shipped-feature history
  (fv21–fv65 ship bullets) is rolled — see PROJECT.md §Spec's pointer + git.

## Decisions that bind
- A task's §6 summary checkboxes silently drift stale against fresh Refute-read/Advisor verdict prose across rebuild rounds — reconcile checkboxes to verdicts BEFORE any `report --decide` gate read; for a high-risk/conservative task the gap misrepresents resolved work at the one mandatory sign-off. [fv63 · global-lock-followups + project-scope-install-lock]
- One glossary term touches 9 files across 3 sync regimes (book ×4 · template ×3 · dogfood ×1), each in that type's NATIVE format (appendix `**T** — d` · template/dogfood `t: d`) — parity guards catch byte-divergence, per-type FORMAT is a judgment the test must pin per type. [fv37 · close-book-accord]
- A new runtime dependency falsifies any "zero-dep" prose — grep + fix the claim in the SAME change. [fv38 · installer-prompts]
- The wording-lints have two blind-spot rules: skill-guide status/process slang must ride in `code spans` (a bare "fold" turned the suite red), and new docstrings must document grammar abstractly, never spelling status words. [fv37/fv36 · close-guide + spec-delta-grammar]
- A frozen DESCRIPTIVE parenthetical can mis-count while the binding SEAM holds — honor the seam, disclose the stale number at verify, never retro-edit the frozen contract. [fv48 · fast-lane-template]

## Deltas (newest first)
- [open · 2026-07-26] Three independent defects in one meter all biased the same way — artifacts unread, one sentence credited to every item, and a plan-write closing the surfacing window — and all three penalised methods that reason on disk while rewarding ones that narrate in chat. When several errors in a measurement point the same direction, treat the coincidence as evidence of a shared assumption rather than as bad luck: here it was that the transcript is where thinking happens. (task:ambiguity-meter-fixes)
- [open · 2026-07-26] A workload PROMPT written by analogy to a longitudinal one inherits assumptions the harness does not honour: amb1 said 'build onto the existing app' and 'keep every previous behaviour working', but the runner only seeds a workspace when wm>1, so amb1 always started empty and the base endpoints its probes depend on were never specified. When adding the FIRST milestone of a new workload family, check what the harness actually hands the agent rather than copying the prose shape of an existing family. (task:amb1-checklist-oracle)
<!-- prepended by `add.py delta-append sdd "<text>"` — one line per lesson, `- [open · <date>] <lesson>` + the active-task stamp; fold a delta upward, then retag [open]->[folded] -->
