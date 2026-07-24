# Strategy — the persona-framed PM loop that fills the `## Strategy` slot

A multi-task or high-uncertainty milestone earns a plan over its tasks *before* they are
built. This guide drives that plan: a short **DISCUSS → OPTIMIZE → CONVERGE** loop that fills
the milestone's `## Strategy` slot (`MILESTONE.md`) with a sequenced, optimized task DAG.

**Trigger:** a milestone with several tasks or real uncertainty, at intake or when it activates.
**Skip:** a micro / `--tiny` milestone — a **drafted-blank** slot is valid, run nothing (risk-proportional).

The persona already loaded at intake (`intake.md`) **drives** this loop — you don't re-select
one. It frames the sequencing WITH the project's PM lens; it stays advisory throughout.

## Run the loop (with the intake persona)

1. **DISCUSS** — surface the task DAG: the dependencies, the shared/risky contracts, the
   tradeoffs. Reflect the milestone goal, name what's in and out. Ask **one load-bearing
   question per live lens** — an interview toward ~95% confidence, not a survey.
2. **OPTIMIZE** — sequence the DAG. Fill the slot's four facets (defined there, not restated
   here): **approach** (risk-first | dependency-first | first-slice-unblocks — and WHY) ·
   the **freeze-first** contract(s) · the **parallel waves** behind those frozen contracts ·
   the **first unblocking slice**. Name the alternative decompositions you rejected.
3. **CONVERGE** — before you record, pressure-test the plan. If the milestone is
   **high-uncertainty** (the sequencing is contested, or the self-score won't clear its bar),
   spawn `add-advisor` in **refute** mode to try to **break** the strategy — the approach, the
   freeze-first choice, the wave partition. Fold what survives; concede what holds. A
   low-uncertainty / micro / `--tiny` milestone **skips** the spawn — no forced ceremony.
   Then self-score with the existing six-dimension confidence self-score (`phases/direction.md`);
   refine until it clears its bar (no dimension < 0.9 ≈ ~95% confident). Do **not** invent a
   second threshold — that bar IS convergence. Record the converged plan in the `## Strategy` slot.

The refute is **advisory**: the advisor hands back the concrete break — it **cannot block**.
The human still confirms the strategy at the human decision point, through the persona-owned
gate (`gate-udd.md`) — the persona decides the report's shape and cadence. Security stays **HARD-STOP**.

## It stays SOFT

The `## Strategy` slot is the **preferred** plan, exactly like a task's §5 Build-strategy: the
build loop may deviate and records what it actually did. It is **advisory** — **never a new
gate**, and it never lowers a floor. Security stays **HARD-STOP** everywhere. A milestone is
never blocked on reaching a confidence bar; the bar guides the draft, it does not gate the work.

## How deep? (risk-proportional)

Loop depth scales with the milestone's risk/size — more risk/size, more depth:

- **micro / `--tiny`** → skip the loop. A drafted-blank `## Strategy` is valid; the loop runs
  nothing — **zero added per-turn cost**.
- **multi-task, low-uncertainty** → run DISCUSS → OPTIMIZE → CONVERGE; no advisor.
- **high-uncertainty** (contested sequencing, or the self-score won't clear its bar) → the full
  loop **plus** the `add-advisor` refute at CONVERGE.

This is the skill's judgment, reusing the Trigger / Skip and CONVERGE signals above — **never an
engine gate** on `## Strategy`. The ladder is **SOFT**: a run may go deeper or shallower and
records what it did. Security stays **HARD-STOP**.
