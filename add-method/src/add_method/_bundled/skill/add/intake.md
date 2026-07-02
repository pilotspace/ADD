# Intake — size a request into versioned scope

Before a task exists, ADD turns a raw request into correctly-sized, versioned scope — the
**intake level** (the per-task flow is phases 0–7; intake is the step *before* a task). You
(the AI) **propose**; the human **confirms**. Never create scope without a confirmed proposal.

## Interview before you size

Run `add.py search <keyword> [<keyword> ...]` first — it surfaces overlapping/prior work in one
command instead of a full manual re-read. When the request arrives as a question, or its intent is
not sharp enough to place in one bucket: explore it WITH the user before classifying. Reflect the intent you heard, name what seems in and
out of scope, and offer 2–3 sized options with your own recommendation. Only then emit
`{ bucket, rationale, command }`. `ask_human` stays the floor: when interviewing cannot sharpen the
request, reject — never guess a bucket.

## The four buckets

Classify every request into exactly ONE bucket:

| Bucket | Decision test | Implied command |
|--------|---------------|-----------------|
| `new-major` | a new product theme/pillar no active milestone's goal covers | `add.py new-milestone vN` |
| `sub-milestone` | a slice of an EXISTING major theme, too big for one task | `add.py new-milestone vN-M` |
| `task` | fits within the ACTIVE milestone's stated scope | `add.py new-task <slug>` |
| `change-request` | modifies ALREADY-FROZEN scope (a frozen contract or a shipped promise) | `add.py phase specify\|contract <affected>` |

**Tie-break order: the frozen-scope test runs FIRST, before the size test.** Ask "does this change
already-frozen scope?" → if yes it is a `change-request` (never re-size frozen work as new scope).
Only if no, apply the size test: a new theme → `new-major`; a slice of a live theme → `sub-milestone`;
fits the active milestone → `task`.

**One-task gap rule.** If the request is ONE task but does NOT fit the active milestone's stated
scope, do not force it into `sub-milestone` (which requires "too big for one task"): create a new
micro-milestone to house it (`new-milestone` + `new-task`) — that gives the task ledger attribution
and clear exit criteria without inflating scope.

## What you emit (the proposal)

Present the proposal via `report-template.md` — open with the ARC (goal · done · plan): the goal this
request serves, what is already covered, and the plan the chosen bucket sets up. Render it as a guided
choice — the recommended bucket + its described alternatives (per `report-template.md`). For every
request, emit ONE of:

- **a classification** — `{ bucket, rationale, command }` — `rationale` names WHY (the theme, the
  slice, the fit, or the frozen scope touched) and `command` is the exact `add.py …` from the table.
  The human confirms or overrides before you run it.
- **a rejection** — `{ reject, rationale }` — create nothing, from this closed set:

<reject_codes>
- `ask_human` — too ambiguous/underspecified to size. Ask the human; never guess a bucket.
- `frozen_scope` — it changes frozen scope; route it as a `change-request` back to SPECIFY/CONTRACT of
  the affected task — never spawn a parallel milestone that forks the truth.
- `split_required` — it spans more than one bucket; propose the SMALLEST set of correctly-sized items,
  each with its own rationale; never force it into one milestone.
</reject_codes>

When confirmed, record the `rationale` in the artifact you create or affect — the new MILESTONE.md
goal/body, the new TASK.md, or a note in the affected TASK.md — never in state.json.

## Roadmap — a request that is several milestones

Some requests decompose into **N>1 milestones of the same line** — a roadmap, not one milestone.
Don't create only the first and lose the rest. Instead:

1. **Propose** the roadmap — the ordered milestone list, each with a one-line goal.
2. **Confirm** — the human confirms the roadmap before anything is created. Never auto-create N
   milestones unprompted — the intake floor (`ask_human`) still holds.
3. **Create** all N on confirm — the first with `add.py new-milestone <slug>` (active), the rest
   with `add.py new-milestone --queued <slug>` (status `queued`, not focused).
4. **Promote** one at a time — as each is started, `add.py activate <slug>` flips it queued→active.
   You work one active milestone at a time; the queue is the agreed backlog, surfaced at resume.

This is NOT `split_required`: that code is for a request spanning **different buckets** (propose the
smallest correctly-sized set). A roadmap is several milestones of the **same line**, created queued.

## Worked examples (from this project's own history)

| request | bucket | rationale |
|---------|--------|-----------|
| give ADD a hosted web dashboard | new-major | a new product theme no active milestone's goal covers → a fresh major line (v5) |
| add the build corridor + tests-red-before-build | sub-milestone | a slice of the live v4 "self-driving" theme, too big for one task → v4-2 |
| expose owner/stop as --json | task | fits the active v4-1 (intake interface) scope → one task |
| guide --json phase/gate should be nullable | change-request | changes the FROZEN machine-state-json contract → reopen its CONTRACT, do not make a new milestone |
