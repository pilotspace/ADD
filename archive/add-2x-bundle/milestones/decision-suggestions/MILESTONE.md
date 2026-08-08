# MILESTONE: Decision suggestions — a recommended pick + described alternatives at every human gate

goal: At every human decision point (baseline-lock, contract freeze, verify, intake, scope, milestone close, graduation, release, human-gated advance) ADD presents a highlighted recommended choice plus its real described alternatives, so the human decides with the recommendation and its consequences in view instead of a bare next-step line.
rationale: new-major — a new decision-point UX theme no active milestone's goal covers; sibling to v23 (the decision arc) and next-step-seams (the engine `next:` footer), extending the SAME presentation layer. Presentation-only, tool-agnostic, NO engine change (the human chose convention-only — locus=presentation, shape=recommended-pick + described-alternatives, coverage=all human gates).
stage: mvp · status: active · created: 2026-06-16

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
- `report-template.md` — the DECISION block (block 2) becomes a recommended-pick-with-described-alternatives structure: one highlighted recommended option (`▶ … (recommended)`) + 1–3 real alternatives, each a one-line description (what it means · what it unlocks/costs), plus the AskUserQuestion composition (recommended option first · `(Recommended)` label · per-option `description`). (← suggestion-block — freezes the convention)
- Wire a one-line convention cue into every human-gate guide: `phases/0-setup.md` (baseline-lock) · `phases/3-contract.md` (freeze) · `phases/6-verify.md` (gate) · `intake.md` · `scope.md` · `loop.md` (milestone-close) · `graduate.md` · `release.md` · the human-gated phase advance. Mirror the v23 arc-gate-wiring pattern. (← gate-wiring)
- Book + GLOSSARY describe the convention (1 glossary headword + a book line in the reports/governance chapter); skill mirror (`add-method/skill/add` ↔ `.claude/skills/add`) + book trees byte-identical + parity tests. (← suggest-book-align)

Out:
- NO engine change — `add.py`'s `next:` footer / DECIDE NEXT / driver marker stay byte-identical (the human chose convention-only).
- NOT an enforced gate — a docs-accord lint guards PRESENCE of the cue in each guide, never engagement (prose ≠ enforcement; the accepted ceiling, like the least-sure flag).
- NOT at AI-only steps — at an `auto` phase-advance the AI just proceeds (`[you drive]`); the convention fires only where a HUMAN chooses (`[human gate]`). No recommended-pick noise on autonomous transitions.
- No new ask-tooling — ADD stays tool-agnostic; the convention describes how to USE whatever ask surface the agent has (AskUserQuestion on Claude Code; a numbered menu elsewhere).
- No re-freeze of any frozen data contract — this is the presentation/layout layer that iterates WITHOUT a re-freeze (foundation invariant).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Recommended pick is highlighted + labeled** — exactly one option carries `▶`/`(recommended)`; never zero, never two. The AI's own confidence self-score (`confidence.md`) informs the pick; the human overrides freely.
- **Every option gets a one-line description** — what it means + what it unlocks/costs; no bare labels; ≤1 line each (leanness is a UX constraint — fv16).
- **1–3 real alternatives** — only genuine, takeable options (no strawmen); if there is truly one path, present the single recommended step + description (the degenerate case), never invent filler.
- **Composes with the ARC + 5 blocks** — refines block 2 (DECISION) only; the ARC · FLAGS · EVIDENCE · NEXT are unchanged. Show-before-ask still holds: the described choice is the ASK, rendered AFTER EVIDENCE.
- **Human decision points only** — fires at `[human gate]`, never `[you drive]`.
- **Glossary deltas** — `guided decision` (a decision point presented as a highlighted recommended pick + described alternatives) · `recommended pick` (the one highlighted option).

## Shared / risky contracts (freeze these first)
- **the decision-suggestion convention** (the recommended-pick marker + the one-line-description rule + the 1–3-alternatives rule + the AskUserQuestion composition + the human-gate-only scope) -> owning task `suggestion-block`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] suggestion-block    depends-on: none              — extend `report-template.md`'s DECISION block into the recommended-pick + described-alternatives convention (the marker · the one-line-description rule · the 1–3-alternatives rule · the AskUserQuestion composition · the human-gate-only scope). Freezes the convention.
- [x] gate-wiring         depends-on: suggestion-block   — add the one-line convention cue to every human-gate guide (the 8: setup·contract·verify·intake·scope·close·graduate·release), mirroring arc-gate-wiring (no double-cue, one slot per guide). [reconciled: phase-advance is engine-mechanical with no own guide — its human moments are the freeze + verify gates, both wired]
- [x] suggest-book-align  depends-on: gate-wiring        — book + GLOSSARY describe the guided-decision convention; skill mirror + book trees byte-identical + parity tests.

## Exit criteria (observable; map each to the task that delivers it)
- [x] `report-template.md`'s DECISION block specifies a highlighted recommended pick + 1–3 described alternatives + the AskUserQuestion composition, scoped to human gates   (← suggestion-block)   (verify: a lint asserts the recommended-marker + the described-alternatives rule + the AskUserQuestion-composition + the human-gate-only tokens are present in `report-template.md` across the skill mirror)
- [x] every human-gate guide — the 8: setup·contract·verify·intake·scope·close·graduate·release — cues the convention   (← gate-wiring)   (verify: a guard greps each of the 8 guides for the "guided choice" cue; phase-advance is engine-mechanical, folded into the freeze + verify gates)
- [x] book + GLOSSARY describe the guided-decision convention, the skill mirror + book trees are byte-identical, and parity passes   (← suggest-book-align)   (verify: `test_book_parity` + `test_bundle_parity` green AND grep finds the glossary headword + the book line)
