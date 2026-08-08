# MILESTONE: Ground phase — build against the real codebase

goal: A task's contract, tests and build are grounded in the real current codebase: a new ground phase (a phase-0 preamble before the seven steps) gathers the actual files, symbols, signatures, patterns and conventions the work touches, surfaced as anchors the frozen contract cites — so the AI builds against reality, not assumption.
rationale: new-major — a request to add a planning phase that gathers the real codebase before specify/contract/tests/build. Method-defining (changes every task's lifecycle), risk:high, run conservative. Shape confirmed by the human: a new distinct phase before specify · a lean grounding map · flag-at-freeze (measure, never block).
stage: mvp · status: active · created: 2026-06-10

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
- A per-task `ground` phase in the engine ladder, positioned **phase-0 before specify** (the seven steps stay specify→observe = §1–§7). `new-task` starts a task at `ground`; `advance` moves ground→specify. **AI-owned** (`PHASE_OWNER["ground"]="AI"`), **no new human gate** — the single approval stays at the contract freeze. (→ ground-phase-engine)
- The **lean grounding map** — a `## 0 · GROUND` section in TASK.md: the real files/symbols/signatures the task touches + the patterns/conventions it must honor + the **anchor points** the contract cites. Defers to PROJECT.md / CONVENTIONS.md for architecture; gathers only the **task-specific delta** (never re-runs the setup brownfield-scan). A new phase guide drives it. (→ ground-phase-engine)
- The contract-freeze checklist gains one line — *"is this contract grounded? cite the anchors"* — and `add.py status` / `check` **surface** the task's grounding state (a flag, **measure-never-block**, human-readable surface only, never `--json`). (→ ground-bundle-wiring)
- The book + skill phase-table + GLOSSARY name the `ground` phase and render it as the §0 preamble to the seven steps, synced across canonical · dogfood · bundled (· book) trees. (→ ground-prose-align)

Out (deferred — the anti-scope-creep list):
- A **mechanical gate** that blocks freeze/build until grounded — deferred (flag-now, gate-later; the chosen teeth are *measure*).
- **Auto-generating** the contract/tests from the gathered code — re-introduces hallucination; grounding *informs* a human-approved contract, it does not author it.
- Rebranding "the 7-step flow" → "8-step" — ground is the §0 preamble; the seven steps keep their identity.
- Changing the one-time **setup brownfield-scan** (project-init) — separate concern.
- The spec-bundle structure (specify→scenarios→contract→tests) — unchanged; ground feeds it additively.
- A GSD-style heavy RESEARCH.md / PATTERNS.md — rejected for the lean map.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **ground (phase-0 preamble)** — a new per-task phase before specify; the AI gathers the real current codebase the task touches into a lean grounding map. The seven steps (specify→observe) keep their numbering and brand. (new GLOSSARY term)
- **grounding map / anchors** — the §0 artifact: real files/symbols/conventions + the anchor points the frozen contract cites. Task-specific delta only; defers to PROJECT.md / CONVENTIONS.md for architecture. (new GLOSSARY term)
- **measure-not-block** — grounding surfaces as a freeze-checklist line + a `status` / `check` flag, never a hard gate this milestone (mirrors goal-auto-ready's flag-at-freeze).

## Shared / risky contracts (freeze these first)
- **phase-ladder shape** (insert `ground` as phase-0 before specify) + the **§0 GROUND artifact shape** -> owning task `ground-phase-engine` (risk:high — changes every task's lifecycle; ~12 test files carry a start-phase / `specify` token).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] ground-phase-engine    depends-on: none                 — insert `ground` as phase-0 (PHASES / PHASE_OWNER=AI / PHASE_GUIDE / _PHASE_GUIDE_FILES; new-task→ground; advance ground→specify) + the `## 0 · GROUND` TASK.md template (×3) + the new phase guide (×3/×4) + the ~12 downstream test updates. risk:high — the spine.
- [x] ground-bundle-wiring   depends-on: ground-phase-engine  — the contract-freeze "grounded? cite anchors" checklist line + `add.py status`/`check` surface grounding state (measure, never block; human-readable only).
- [x] ground-prose-align     depends-on: ground-phase-engine  — book + skill phase-table + GLOSSARY name `ground` + render the §0-preamble-to-seven-steps flow, synced ×3/×4.

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py new-task <s>` starts the task at phase `ground`, `add.py advance` moves ground→specify, and TASK.md carries a `## 0 · GROUND` section  (verify: test_add.py start-phase + advance-hop tests green)  (← ground-phase-engine)
- [x] the contract-freeze checklist asks the human to confirm the contract is grounded + cites anchors, and `add.py status`/`check` surface grounding state without ever blocking  (verify: test_ground_wiring.py — surface present, no red)  (← ground-bundle-wiring)
- [x] the book + skill + GLOSSARY name `ground` and render it as the §0 preamble to the seven steps, byte-synced across trees  (verify: test_ground_prose.py + engine-pin/sync check)  (← ground-prose-align)
