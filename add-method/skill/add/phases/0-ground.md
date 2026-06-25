# Phase 0 — Ground (the real codebase)

Goal: before you specify anything, gather the REAL current working folder the task will
touch — the actual files, symbols, signatures, docs, todos, config, data, patterns, and conventions — so the
contract, tests, and build are grounded in what exists, not in what you assume.
Fill **§0 GROUND** in TASK.md. Ground is a per-task preamble to the seven steps;
it is **AI-owned** — no human gate here (the one approval stays at the §3 freeze).

If you cannot name the files and symbols the task touches, you do not yet understand
the work — gathering them IS the job, not a detour.

## Gather (in TASK.md §0)

- **Touches** — the real files · symbols · signatures the task will read or change,
  named from the actual code (use code-navigation tools — grep / symbol search, never memory).
  Each as `path:symbol — what it is / how it is keyed`.
- **Context (working folder)** — NON-code artifacts the task touches: docs/textbase (README · `*.md` · design notes) · TODOs (`TODO.md` · `FIXME`/`TODO`/`HACK` comments) · config/manifests (configs · `.env.example` · `pyproject`/`package` · CI) · data/fixtures. Task-specific delta only — never index the whole repo.
- **Honors** — the patterns and conventions the work must respect, cited from `PROJECT.md` / `CONVENTIONS.md`. Task-specific delta only — never re-derive the architecture.
- **Anchors the contract cites** — the specific symbols §3 CONTRACT will name. The contract may cite only anchors that appear here.

**How — gather efficiently:** for the BROAD sweep, prefer a small-model subagent / fast
index / skim (offload to a cheap context, return a compact map); then DEEPEN on what THIS
task specifically needs — never lock a shallow first pass.

## Greenfield / first task

The first task of a project runs ground too. When there is little or no code yet
(greenfield), or you are mid-setup, your grounding IS the foundation docs / brownfield
scan you just produced — point at them; do not re-scan. An honest "new module, no
existing code; honors CONVENTIONS.md §X" is a complete grounding.

## AI prompt

<prompt>
Role: an engineer who reads the real code before designing against it.
Read first: PROJECT.md · CONVENTIONS.md · the actual files the task touches.
Objective: fill §0 GROUND with the real files/symbols/signatures + the conventions to
honor + the anchor points the contract will cite — gathered from the codebase, never assumed.
Steps:
  0. Sweep broad cheaply first — prefer a small-model subagent / fast index / skim — then deepen task-specifically.
  1. Locate the files and symbols the task reads or changes (code tools, not memory).
  2. Record their signatures / how they are keyed; cite the conventions to honor (task delta only).
  3. Name the anchors §3 will cite.
Never: invent a file, symbol, or signature you have not opened.
</prompt>

## Exit gate

<exit_gate>
- [ ] **Touches** — the real files/symbols the task touches are named (from the code, not assumed).
- [ ] **Context** (working folder) — the non-code artifacts the task touches (docs · todos · config · data) are named, task-delta only.
- [ ] **Honors** — the patterns/conventions to honor are cited (task-delta only; no architecture re-scan).
- [ ] **Anchors** — the anchors §3 will cite are listed — §3 names only anchors that exist here.
</exit_gate>

**Grounding is complete when** all four fields are filled from real assets: a STRONG grounding cites
actual files/symbols/docs/conventions you opened; a WEAK one leaves a `<…>` placeholder or names what you
assume. All four are non-optional — skipping **Context** (the working folder beyond code) is the usual
silent gap. §3 may cite only anchors that appear here.

> **Advisor · Confidence** — a broad sweep is the canonical spawn case (advisor.md); self-score your grounding before you specify against it (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/1-specify.md`.
Book: `docs/02-the-flow.md` (the flow; ground is the §0 preamble to the seven steps).
