# Canonical text checklist — verify EVERY label after render (text accuracy is the gate)

Source of truth: the book chapters. A misspelled/dropped label = reject, re-render.

## 1 · add-flow.png — The flow: 3 phases, 7 beats (ch02)
Phase bands (engine walk — direction · build · verify; done is bookkeeping, not a card):
- direction = beats 1–4, one span ending at the single freeze approval
- build = beat 5 · verify = beats 6–7 (verify owns Observe)
Exact beat order + essence (spelling must match):
1. Specify — the rules
2. Scenarios — pass/fail cases
3. Plan — ground the code, freeze the contract
4. Tests — failing-first suite (red)
5. Build — AI writes code
6. Verify — evidence + checks
→ Observe — in production
Loop: Observe → "what you learn becomes the next Specify" → back to 1 Specify
Bands: 1–2 human-led · 3–4 frozen decision point · 5–6 AI-led · Verify=human · Observe=loop
Primary flow = SOLID arrows, never skipping a card. Backward correction = DASHED.
Backward-correction arcs (must be present, dashed, quieter than the primary flow):
  - Verify → Build   labelled "evidence fails - back to Build"
  - Build → Specify  labelled "a missing rule - back to Specify"
Engine: a small two-way DASHED loop between Tests and Build, labelled "red / green".
Note present: "any phase may return to an earlier one".

## 2 · add-competencies.png — Five competencies (ch00/14)
Five, in order, each: acronym — name · essence · key artifacts
- DDD — Domain-Driven · "the language & boundaries" · domain model · context map
- SDD — Spec-Driven · "the living document" · SPEC.md · acceptance checklist
- UDD — UI/UX-Driven · "users use the interface" · user flows · UI states
- TDD — Test-Driven · "the failing-first suite" · test suite · coverage
- ADD — AI-Driven · "you command, AI executes" · working code · reviewed PR
Banner: DDD · SDD · UDD · TDD = context engine → feeds → ADD
Note: first four human-led (AI assists); ADD = AI-led under direction

## 3 · add-foundation.png — Engine on ground (ch14)
- Top box: "TDD ⇄ ADD — the engine"  (per-feature loop)
- Arrow up: "feeds context up"
- Foundation, 3 stacked (living docs · cross-milestone):
  - UDD — UI/UX · user flows · UI states
  - SDD — Spec · what we build now (living)
  - DDD — Domain · the language & boundaries
- Arrow down: "any loop may send a correction back down"
- Margin: "the foundation outlives every milestone"

## 4 · add-hierarchy.png — Three tiers (ch14 / appendix-f)
Three tiers, each: tier · lives in · lifespan · holds
- Project (foundation) · .add/PROJECT.md · whole product · domain · spec · users · decisions
- Milestone · .add/milestones/<slug>/MILESTONE.md · one goal · scope · contracts · exit criteria
- Task · .add/tasks/<slug>/TASK.md · one feature · the seven-step artifacts
Note: "a milestone is a version bump to the foundation, not a fresh start"

## Acronyms that get garbled — check each glyph
DDD  SDD  UDD  TDD  ADD   (NOT ADD→ADO, SDD→SDO, etc.)
Specify Scenarios Plan Tests Build Verify Observe  (7, in order)
