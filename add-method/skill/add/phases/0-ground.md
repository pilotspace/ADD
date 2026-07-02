# Phase 0 — Ground (the real codebase)

Goal: before you specify, gather the REAL working folder the task touches — files, symbols,
signatures, docs, config, data, conventions — so the contract/tests/build are grounded in what
exists, not assumed. Fill **§0 GROUND** in TASK.md: a per-task preamble to the seven steps,
**AI-owned** — no human gate (the one approval stays at the §3 freeze).

If you cannot name the files and symbols the task touches, you do not yet understand it —
gathering them IS the job.

## Gather (in TASK.md §0)

- **Touches** — the real files · symbols · signatures the task reads or changes, named from the
  actual code (code-navigation tools — grep / symbol search, never memory). Each as `path:symbol — what it is / how keyed`; cite the **symbol**, not a bare line number (`l.NNN` rots at build; symbols survive).
- **Context (working folder)** — NON-code artifacts touched: docs/textbase (`*.md`) · TODOs (`TODO`/`FIXME`) · config/manifests (`pyproject`/`package`/CI) · data/fixtures. Task-delta only.
- **Honors** — patterns/conventions the work must respect, cited from `PROJECT.md`/`CONVENTIONS.md`. Task-delta only — never re-derive the architecture.
- **Anchors the contract cites** — the specific symbols §3 CONTRACT will name. The contract may cite only anchors that appear here.
- **Issues/Risks (→ feed §1)** — concrete problems · traps · untestable risks you find in the real code while grounding; §1 SPECIFY builds on these, not on assumptions. Task-delta only.
- **Related intent** — the WHY: `PROJECT.md §` · `GLOSSARY` term(s) · the originating request/milestone rationale (intent, not Honors' conventions). Task-delta.
- **Ground SHA** — the commit you grounded against (`git rev-parse --short HEAD`); any line ref is "as of" it. `check` warns on a §0 that cites line numbers with no SHA.

**How:** sweep BROAD cheaply (small-model subagent / fast index / skim → compact map), then DEEPEN on what THIS task needs — don't lock a shallow pass.

## Greenfield / first task

The first task runs ground too. With little/no code (greenfield) or mid-setup, your grounding IS
the foundation docs / brownfield scan you produced — point at them, don't re-scan. An honest
"new module, no code; honors CONVENTIONS.md §X" is complete.

## AI prompt

<prompt>
Role: an engineer who reads the real code before designing against it.
Read first: PROJECT.md · CONVENTIONS.md · the files the task touches.
Objective: fill §0 GROUND from the codebase — files/symbols/signatures + conventions + the
anchors §3 cites + issues/risks found; never assumed.
Steps:
  0. Sweep broad cheaply (small-model subagent / fast index / skim), then deepen task-specifically.
  1. Locate the files/symbols the task reads or changes (code tools, not memory).
  2. Record signatures/keying; cite conventions (task-delta); note risks for §1; name §3's anchors.
Never: invent a file, symbol, or signature you have not opened.
</prompt>

## Exit gate

<exit_gate>
- [ ] **Touches** — the real files/symbols the task touches are named (from the code, not assumed).
- [ ] **Context** (working folder) — the non-code artifacts touched (docs · config · data) are named, task-delta only.
- [ ] **Honors** — the patterns/conventions to honor are cited (task-delta; no architecture re-scan).
- [ ] **Anchors** — the anchors §3 will cite are listed (§3 names only anchors here).
- [ ] **Issues/Risks** — the problems/risks found are recorded for §1 (or an honest none).
- [ ] **Related intent** — the PROJECT/GLOSSARY/origin intent is linked (or an honest none).
- [ ] **Ground SHA** — the commit grounded against is recorded (line refs read "as of" it).
</exit_gate>

**Grounding is complete when** every field is filled from real assets (a `<…>` placeholder = weak;
all non-optional). Skipping **Context** (beyond code) is the usual silent gap. §3 cites only anchors here.

> **Advisor · Confidence** — a broad sweep is the canonical spawn (advisor.md); self-score before you specify (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/1-specify.md`.
Book: `docs/02-the-flow.md` (the flow; ground is the §0 preamble to the seven steps).
