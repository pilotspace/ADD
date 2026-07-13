# Phase 3 — Plan (ground · freeze the shape · build-strategy)

Goal: turn the specified rules + scenarios into ONE change plan and FREEZE it. The plan unites three
parts — **Grounding** the real code, the **Contract** (the external shape), and the **Build-strategy** —
into the single human approval. Below the freeze code is disposable; above it the Contract does not move.
Fill **§3 PLAN** in TASK.md. **The freeze is the one decision point** that makes the AI-led build safe.

## Produce (in TASK.md §3 — three parts)

<output_format>

### 1 · Grounding — the real code the contract will cite (gather BEFORE you freeze)
Project from the milestone `## Ground`, then gather the real code THIS task lands in — deepen only
there. Never invent a file/symbol you have not opened.
- **Touches** — real files · symbols · signatures, as `path:symbol — what it is / how keyed` (cite the
  symbol, not a bare line number — `l.NNN` rots at build; symbols survive). Use code-navigation tools, not memory.
- **Context (working folder)** — non-code artifacts touched: docs/textbase (`*.md`) · TODOs (`TODO`/`FIXME`) · config/manifests · data/fixtures. Task-delta.
- **Honors** — patterns/conventions from `PROJECT.md`/`CONVENTIONS.md` · seams consulted (`SEAMS.md`). Task-delta.
- **Anchors the contract cites** — the specific symbols §3's Contract will name. The Contract may cite ONLY anchors here.
- **Issues/Risks** — concrete traps/untestable risks found in the real code (feeds §1, not assumptions).
- **Related intent** — the WHY: `PROJECT.md §` · `GLOSSARY` term(s) · originating request/milestone rationale.
- **Ground SHA** — the commit grounded against (`git rev-parse --short HEAD`); any line ref is "as of" it.

**How:** sweep BROAD cheaply (small-model subagent / fast index / skim → compact map), then DEEPEN on
what THIS task needs. **Grounding is complete when** every field above is filled from real assets (a `<…>` placeholder = weak).
*Greenfield / first task:* grounding IS the foundation docs / brownfield scan you produced — point at them;
an honest "new module, no code; honors CONVENTIONS.md §X" is complete.

### 2 · Contract — freeze the external shape (HARD, tamper-guarded)
- Interfaces (endpoints/functions/messages) with inputs/outputs; request/response shapes + persistent schema (note transactional needs).
- Names drawn from `GLOSSARY.md` (same concept = same name everywhere); a response for **every** Reject code from §1.
- The Contract cites only anchors named in Grounding. Generate a mock + contract tests so dependent work can start.

### 3 · Build-strategy — the intended approach (SOFT: preferred; the builder self-improves and records actual at verify)
- **Scope (may touch)** — backticked path tokens; the freeze locks this. **Strategy** — ordered batches.
  **Approach / Data strategy / Pattern / Optimization stance** — the domain plan + the trust-least facet.
  **Persona** · **Spawn isolation** (inline vs parallel worktree) · **Known-problem fixes** (`SEAMS.md` traps).

Then mark `Status: FROZEN @ v1 — approved by <name>`.

</output_format>

## The freeze — the one approval

Present the bundle **lowest-confidence first**: the 1–2 points most likely wrong
(`⚠ [spec|scenario|contract|test] … — because …; if wrong: …`). Open with the ARC per `report-template.md`,
rendering SHAPE then the freeze APPROVE as a guided choice — **render before `FROZEN`, then record `Reported: yes`;
never on a timeout.** See `run.md`. The approval freezes the Contract (HARD) + the Build-strategy Scope.

## The freeze review checklist

The human's one minute, aimed. Walk these seven before saying yes:

- **⚠ flags first** — read the lowest-confidence flags; accept each knowing its cost if wrong. The engine refuses an unflagged freeze before build (`unflagged_freeze`).
- **Intent** — does §1 say what you actually want built?
- **Cases** — does every Must and Reject have an observable §2 scenario?
- **Shape** — glossary names, error codes, additive vs breaking: is THIS the shape to freeze?
- **Grounded** — does the Contract cite anchors that exist in the Grounding map? `status`/`check` surface this.
- **Risk** — high-risk or method-defining? Require `risk: high · autonomy: conservative` in the TASK.md header.
- **Tests** — will §4 go red for the right reason, asserting behavior rather than internals?

Reject any line → the bundle goes back to draft; the freeze stays the only gate.

## AI prompt

<prompt>
Role: an engineer who grounds in real code, then an interface architect; frozen contracts are immutable.
Read first: §1 · §2 · the milestone `## Ground` · GLOSSARY · CONVENTIONS · the files the task touches.
Objective: fill §3 PLAN — Grounding (real files/symbols, never assumed) → Contract (frozen shape, a
response for every Reject code) → Build-strategy (scope + ordered batches).
Steps:
  1. Ground: locate the real files/symbols (code tools); name §3's anchors + risks; record the Ground SHA.
  2. Contract: define shapes/schema named from the glossary; generate a mock + contract tests; no business logic.
  3. Build-strategy: scope, batches, persona, spawn isolation. Then mark FROZEN.
Never: invent a file/symbol you have not opened; change a frozen Contract — a change reopens Specify.
</prompt>

## Exit gate

<exit_gate>
- [ ] **Grounding** — Touches · Context · Honors · Anchors named from the code; Issues/Risks · Related intent · Ground SHA recorded (or an honest none).
- [ ] **Contract** — versioned and marked `FROZEN`; contract tests pass against the mock; every name matches the glossary; every §1 rejection has a contracted response.
- [ ] **Build-strategy** — Scope (may touch) declared; batches + persona + spawn isolation named.
- [ ] The Contract cites only anchors that appear in Grounding; the ⚠ lowest-confidence flag is surfaced.
</exit_gate>

> **Advisor · Confidence** — a broad ground sweep + a second opinion on a risky shape are canonical spawns (advisor.md); a low self-score is your cue to lower autonomy before you freeze (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/4-tests.md`.
Book: `docs/05-step-3-plan.md` (the plan phase unites grounding + the frozen contract + the build strategy).
