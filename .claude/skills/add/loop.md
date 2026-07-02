# The dynamic loop — open deltas and extras become the next tasks

A milestone is not done when its tasks are done — it is done when its **GOAL** is met.
This guide drives a milestone toward that goal: turn what each task leaves behind (open lessons,
and work discovered but out of scope) into the next tasks, and keep going until the exit criteria
are all met.

You **gather and propose**; the **human confirms**; the existing `add.py new-task`
creates each one. The engine never decides what the next task is — that is judgment.

## The goal-gate (what holds the loop open)

`add.py milestone-done <slug>` REFUSES to close a milestone while its exit criteria are not
all met — it stops with `milestone_goal_unmet` and the milestone stays active. The exit-criteria
checkboxes in `MILESTONE.md` ARE the human's goal-met affirmation: the engine reads the
`- [x]`/`- [ ]` tally, it never judges whether the goal is met. Checking the last box is the
deliberate act that releases the gate.

The gate fires only when criteria exist. A milestone with no exit-criteria checkboxes closes as
before — write criteria into `MILESTONE.md` if you want the goal-gate to hold the milestone open.

`milestone-done` is the only way a milestone reaches `done`; `archive-milestone` and `compact`
both refuse a milestone that is not done. The one gate is enough — there is no quiet way around it.

## The loop

When every task is done but the goal is not, `add.py status` shows
`goal not met (m/n exit criteria)`. That is the cue:

1. **Gather** the carried inventory:
   - open lessons — `add.py deltas` (the §7 OBSERVE deltas still `open`);
   - the planned-but-unscaffolded tasks — the plan-vs-state line in `add.py status`;
   - any reopened task — one a deepened verify returned to the flow (see below).
2. **Propose** the next tasks: for each carried item worth doing now, draft a one-line task
   (slug + title + why) and show the human. Group the trivial ones; do not propose noise.
3. **Confirm** — the human accepts, edits, or declines each. No task is created without this.
4. **Create** each accepted task — `add.py new-task <slug> --title "..."` — and run it through
   the normal flow (specify → … → verify).
5. **Repeat** until the work the goal needs is done.
6. **Close** — when the goal is genuinely met, run the **ship review** before you close:
   - **Fill the ship review first** — write the milestone's `## Close — ship review` section:
     **Ship by domain** — what changed per bounded context (`tooling` · `skill` · `book`, or
     "untouched"); **Cross-task evidence** — one row per task (`gate` · `tests` · `residue`);
     and the **Goal met?** map — each exit criterion tied to the evidence that satisfies it.
     This is the whole-milestone cross-task evidence the human READS; it is evidence, not a gate.
   - **Check the boxes** — read that evidence, then check the exit-criteria boxes in `MILESTONE.md`
     (the single affirmation), and `add.py milestone-done <slug>` succeeds (then consolidate open
     deltas and archive — the `milestone-done → fold → compact → archive` lifecycle, per
     `fold.md` · `compact-foundation.md`).
   - **Define the release steps** — write the milestone's `## Release steps` (merge is one small
     step among them; PR, asset export, tag/publish are others). These **feed** the release scope —
     read `release.md` for the cut; loop.md never re-specifies it.
   Present the close via `report-template.md` — open with the ARC (goal · done · plan) and
   render as a guided choice (recommended next move + described alternatives).

## Reopen is the verb; this loop is the trigger

When a deepened verify finds a criterion unmet on a task already marked done,
`add.py reopen <task> --to <phase> --reason "..."` returns it to the flow with a recorded
reason and a reset gate — fired by this loop's judgment, not the engine's.

## The reactivation residual (deferred)

A reopen fired inside the loop happens while the milestone is still **active** — the goal-gate
held it open, so it never reached done. The one residual — reopening a task inside a milestone
that was already closed — is surfaced by `add.py check` (a done milestone with a live task reads
as incoherent). Re-activating a closed milestone is **deferred**: resolve it by hand for now,
until a later task makes milestone reactivation first-class.
