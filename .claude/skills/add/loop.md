# The loop — observe → learn → the next spec delta

A milestone is done when its **GOAL** is met, not when its tasks are. This guide turns what each
task leaves behind — open lessons, work found out of scope — into the next tasks, until every exit
criterion holds. You **gather and propose**; the **human confirms**; `add new Task` creates each.
The engine never picks the next task — that is judgment.

> **Command status.** `add status · new · done · learn · milestone-done · deltas · reopen · fold ·
> milestone-archive` are all **wired** (the real `add` CLI) — the whole loop surface is dispatched.

## Release deliberately, then watch

Verify proved the change against everything you anticipated. Ship it behind a scope-limiting
mechanism — flag, gradual rollout, or both — so a miss touches a few users and rolls back, not
everyone. Release is not the finish line; it is where the most reliable signal about the feature
finally arrives.

## Reuse the CHECKS as monitors

The `## CHECKS` that drove the red/green build have a second life. Each Must/Reject scenario becomes
a live monitor: the overall error rate, each named rejection token (a spike in one is signal, not
noise), and the latency of anything under load. Same definition of "correct" — now it drives alerts.

## Turn observation into the next spec delta

Every defect, surprise, or new need is written as a **delta** re-entering at DIRECTION (`deltas.md`):
tagged, evidence-carried, `open`. The AI may cluster telemetry and *draft* the delta; the production
calls — what to roll back, what to prioritise — stay human.

## The goal-gate (what holds the loop open)

`add milestone-done <slug>` REFUSES to close while any exit criterion is unchecked — it stops with
`milestone_goal_unmet` and the milestone stays active. The `- [x]`/`- [ ]` boxes in the milestone node (`milestones/<slug>.md`)
ARE the human's goal-met affirmation: the engine reads the tally, never judges the goal. Checking
the last box releases the gate. The gate fires only when criteria exist — write exit criteria to
hold a milestone open. `milestone-done` is the only path to `done`; `milestone-archive` refuses a
milestone not done. One gate, no quiet way around it.

## The loop

Every task done but the goal unmet? `add status` shows `goal not met (m/n exit criteria)`. That is
the cue:

1. **Gather** the carried inventory:
   - open lessons — `add deltas` (still `open`);
   - planned-but-unscaffolded tasks — the plan-vs-state line in `add status`;
   - any reopened task — one a deepened verify returned to the flow (below).
2. **Propose** the next tasks — with the best-fit advisor-flow persona loaded BEFORE drafting
   (`personas.md` § planning; a roster-less bundle skips silently): for each carried item worth
   doing now, draft a one-line task (slug + title + why). Group trivial ones; no noise.
3. **Confirm** — the human accepts, edits, or declines each. No task is created without this.
4. **Create** each accepted task — `add new Task <slug> --title "..."` — and run it through the
   normal 3-beat loop (direction → build → verify).
5. **Repeat** until the work the goal needs is done.

## Close — GOAL-gated, ship review, then fold

When the goal is genuinely met, close deliberately:

1. **Ship review first.** Write the milestone's `## Close — ship review` — the whole-milestone,
   cross-task evidence the human READS (evidence, **not a gate**):
   - **Ship by domain** — what changed per bounded context (`tooling · skill · book`, or "untouched");
   - **Cross-task evidence** — one row per task (`gate · tests · residue`);
   - **Goal met?** — each exit criterion tied to the evidence that satisfies it.
2. **Present the close as a guided choice** via `gate.md` — open with the ARC (goal · done · plan),
   render the choice — **before `milestone-done`/`milestone-archive` run, not after.**
3. **Check the boxes** — read that evidence, then check the exit-criteria boxes in the milestone node (`milestones/<slug>.md`)
   (the single affirmation); now `add milestone-done <slug>` succeeds.
4. **Fold the deltas** — file every `open` delta into its living `.add/specs/` spec (`add fold`,
   or `add learn <dd>` per delta) — newest-first, append-only. The AI never self-folds (`deltas.md`).
5. **Define the release steps** — write `## Release steps`: merge is one small step among PR, asset
   export, tag/publish. The human owns the cut; this file never re-specifies it.

## Reopen is the verb; this loop is the trigger

When a deepened verify finds a criterion unmet on a task already `done`, `add reopen <task> --to
<beat> --reason "..."` returns it to the flow with a recorded reason and a reset gate — fired by
this loop's judgment, not the engine's. A reopen fires while the milestone is still **active** (the
goal-gate held it open). The one residual — reopening a task inside an already-closed milestone — is
surfaced by `add status --check` as incoherent and resolved by hand for now.

<constraints>
- **Goal-gated close** — never close on tasks-done; the exit-criteria boxes are the only release.
- **Ship review is evidence, not a gate** — it informs the box-check; it never replaces it.
- **AI drafts deltas, the human folds** — no self-consolidation at close (`deltas.md`).
</constraints>
