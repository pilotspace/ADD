# MILESTONE: V21

goal: a reader of the ADD book can trace the method's intellectual lineage — recursive self-improvement, spec-driven development, agentic + tests-first research — and see ADD as the human-gated, evidence-trusted instance of 'closing the loop', grounded in verified, citable sources woven through the book
rationale: new-major — grounding/documentation scope with its own goal that no active milestone covers (v20 just shipped). Confirmed via intake interview 2026-06-08; full grounding pass + curated source set, both human-chosen. ~40 sources gathered by deep research (cached: tmp/v21-references-research.md), curated to ~20-25 verified.
stage: mvp · status: active · risk: low · created: 2026-06-08

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
  1. a curated, annotated references appendix (~20-25 VERIFIED sources, grouped: RSI · agentic
     workflows · SDD/spec-kit · tests-first), each with a "how ADD relates" line;
  2. a spec-kit ↔ ADD phase-comparison table (shared DNA: constitution↔contract · specify↔specify ·
     plan↔contract · tasks↔waves · implement↔build — and where ADD diverges: tests-first gate +
     observe→fold + dynamic goal-loop);
  3. a "Foundations & Lineage" narrative chapter (the RSI "closing the loop" story + the evidence
     chain: METR time-horizon · 80%-AI-authored · Automated Alignment Researchers);
  4. inline citations woven into the existing specify / process / loop chapters at the points the
     research grounds, resolving to the appendix;
  5. all in the AIDD book, mirrored across all 4 doc copies, every link verified.
Out: any engine/method BEHAVIOR change (docs-only — no add.py edit) · citations in the agent-facing
  skill guides (the book is grounding's home; the skill stays lean) · an exhaustive academic survey
  (curated, not complete) · live/auto link-checking (a stale-link sweep is manual) · shipping any
  [UNVERIFIED] source (drop or re-verify) · a spec-kit feature bake-off beyond the phase model.

## Shared decisions & glossary deltas   (living — every task must honor these)
- every cited link is VERIFIED before it ships — no [UNVERIFIED] source reaches the book (the 2
  flagged arXiv items + the future-dated SDD paper are re-checked or dropped).
- grounding lives in the BOOK, not the skill guides (keep the agent surface lean — v16/v20 UDD leanness).
- the references appendix + the chapter are mirrored across all 4 book copies byte-identical (dogfood-parity).
- a new book file trips the v20-folded instrument reaction: bundle/tree parity + (if on the wording-lint
  surface) the surface-count contract — pre-declared per CONVENTIONS instrument-reaction-by-artifact.
- citations use ONE consistent inline form resolving to the appendix (frozen in references-appendix §3).

## Shared / risky contracts (freeze these first)
- the references appendix FORMAT — citation schema (fields · grouping · the "how ADD relates" column) +
  the spec-kit↔ADD table shape -> owning task references-appendix. The chapter and inline citations cite
  INTO it, so its format is frozen before they start.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] references-appendix   depends-on: none                                    — curated annotated bibliography (grouped by theme, "how ADD relates" each) + spec-kit↔ADD phase table; book appendix ×4; every link verified
- [x] foundations-chapter   depends-on: references-appendix                     — narrative "Foundations & Lineage" chapter: RSI closing-the-loop story + spec-kit divergence + evidence chain; cites the appendix
- [x] inline-citations      depends-on: references-appendix,foundations-chapter — weave citations into existing specify / process / loop chapters at grounded points, resolving to the appendix

## Exit criteria (observable; map each to the task that delivers it)
- [x] the AIDD book carries a references appendix (4 copies byte-identical) — curated VERIFIED sources grouped by theme, a "how ADD relates" line each, + the spec-kit↔ADD phase table; no [UNVERIFIED] source present   (← references-appendix)
- [x] the book carries a "Foundations & Lineage" chapter naming the RSI closing-the-loop framing, the spec-kit↔ADD divergence (tests-first gate + fold + dynamic loop), and the evidence chain                              (← foundations-chapter)
- [x] the specify / process / loop chapters carry inline citations resolving to the appendix at the grounded points                                                                                                          (← inline-citations)
