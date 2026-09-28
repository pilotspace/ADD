# Canonical text checklist — verify EVERY label after render (text accuracy is the gate)

Source of truth: the book chapters. A misspelled/dropped label = reject, re-render.

## 1 · add-flow.png — The loop (ch02)
Cards, in order, each: number · word · phrase
1. Direction — rules · assumptions · failing checks
2. Build — red to green, inside scope
3. Verify — seal intact · fresh run · verdict
→ Learn — lessons into the specs
Arrow Direction → Build labelled "freeze commit" (the only coral accent).
Loop: Learn → "what you learn shapes the next direction" → back to Direction.
Primary flow = SOLID arrows, never skipping a card. Backward correction = DASHED.
Backward-correction arcs (dashed, quieter than the primary flow):
  - Verify → Build      labelled "a probe breaks it - back to Build"
  - Build → Direction   labelled "a rule was wrong - refreeze"
A small dashed loop on Build labelled "red / green".
Margin notes: "the decisions survive — the code is disposable" · "the human reviews the report".

## 2 · add-competencies.png — Five competencies (ch14)
Five, in order, each: acronym — name · essence · key artifacts
- DDD — Domain-Driven · "the language & boundaries" · domain model · context map
- SDD — Spec-Driven · "the living document" · living spec · binding decisions
- UDD — UI/UX-Driven · "users use the interface" · user flows · UI states
- TDD — Test-Driven · "the failing safety net" · test suite · coverage
- ADD — AI-Driven · "you command, AI executes" · working code · reviewed PR
Banner: DDD · SDD · UDD · TDD = context engine → feeds → ADD

## 3 · add-foundation.png — The loop on its ground (ch14)
- Top box: "TDD ⇄ ADD — the engine"  (per-feature loop)
- Arrow up: "feeds context up"
- Foundation, 3 stacked:
  - UDD — UI/UX · user flows · UI states
  - SDD — Spec · what we build now (living)
  - DDD — Domain · the language & boundaries
- Arrow down: "any loop may send a correction back down"
- Margin: "the foundation outlives every milestone"

## 4 · add-hierarchy.png — Three tiers (ch14)
Three tiers, each: tier · lives in · lifespan · holds
- Project (the foundation) · .add/PROJECT.md · the whole product · domain · spec · users · decisions
- Milestone · .add/milestones/<slug>.md · one goal · scope · exit criteria · task list
- Task · .add/tasks/<slug>.md · one change · rules · assumptions · checks · evidence
Note: "a milestone is a version bump to the foundation, not a fresh start"

## Words that get garbled — check each glyph
DDD  SDD  UDD  TDD  ADD   (NOT ADD→ADO, SDD→SDO, etc.)
Direction  Build  Verify  Learn  (4, in order)
