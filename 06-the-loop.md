# 06 · The loop — observe, learn, close

[← 05 Verify — evidence, residue lenses, the gate](./05-verify.md) · [Contents](./README.md) · Next: [07 Setup and the three lanes →](./07-setup-and-lanes.md)

---

## The flow is a loop, not a line

Older mental models end at "ship." That framing is the source of a common pathology: teams treat release as a finish line, and so they hide defects to protect the line rather than manage them in the open. In ADD, release is not the end of the flow — it is the point where the most reliable information about the feature finally becomes available: how it behaves with real users, real data, and real load.

That information is the input to the next cycle. What you learn in production becomes the next task's Direction, and the flow returns to [Direction](./03-direction.md). The cycle is continuous.

## Release deliberately

Release behind a mechanism that limits the scope of a mistake — a feature flag, a gradual rollout, or both. Verification established that the feature is correct against everything you anticipated; a controlled release is your protection against what you did not anticipate. If something is wrong, you want to affect a few users and roll back, not affect everyone and scramble.

## Reuse the checks as monitors

The `## CHECKS` that drove the red/green build have a second life here. They described the behavior you expected; in production they become the behavior you monitor. The same definition of "correct" that drove the build now drives the alerts.

**What to watch (▶ example):**

- the overall transfer error rate;
- the rate of each named rejection (`amount_invalid`, `same_account`, `insufficient_funds`, `forbidden`) — a sudden spike in one is a signal, not noise;
- latency, especially of the atomic balance update under load.

## Turn observation into the next spec

Every defect, surprise, or new need is written up as a **delta** that re-enters the flow at [Direction](./03-direction.md). An error rate that is too high, a rejection that fires more than expected, a user behavior nobody designed for: each becomes a concrete, specified next task rather than a vague intention.

This is also where the AI returns to a useful role: summarizing telemetry, clustering errors into themes, and *drafting* the proposed delta for a person to review. But the production decisions — what to roll back, what to prioritize — remain human.

## Lessons learned and the five living specs

A delta feeds the *next task*. But a loop also teaches the **method itself** — that the domain model missed a boundary, that a whole class of scenario was never checked, that a build convention helped or hurt. ADD captures those as **lessons**: each one a single tagged learning that names which of the five competencies it sharpens, and each folds into one of the **five living specs** under `.add/specs/`.

| lens | competency | folds into `.add/specs/` | a delta here means you learned about… |
|------|------------|--------------------------|----------------------------------------|
| `ddd` | Domain | `domain.md` | an entity, rule, or boundary the spec assumed wrong |
| `sdd` | Spec | `system.md` | a missing or wrong must-do / must-reject requirement |
| `udd` | UI/UX | `experience.md` | a flow, affordance, or wording that misled |
| `tdd` | Test | `quality.md` | a missing scenario, a flaky or hollow check |
| `add` | AI/build | `method.md` | a harness, prompt, or convention that helped or hurt |

Each delta is one tagged entry — `- [<COMPETENCY> · <status>] the learning (evidence: <pointer>)` — and the evidence is **required**: a failing scenario, a production signal, a review note. No evidence means it is an opinion, not a delta. The AI **emits** deltas as `open`; it never consolidates its own. Consolidation is judgment, and judgment is the human's — the same verify/observe decision point that keeps the AI from grading its own work.

**File a lesson the moment it lands** — any beat, any task:

```
add learn <lens> "<lesson>" --evidence <ref>
```

`add learn` prepends one `open` line (newest-first) into the lens's living spec under `.add/specs/`. `add deltas` lists every open delta across the specs, so nothing waiting to be consolidated is invisible. At close, a person folds each one into its matching spec with `add fold <lens> "<delta>"` — flipping it `folded` (merged) or leaving a `rejected` line in place so the trail survives. Running `fold` *is* the human's confirmation; the engine never decides *which* lessons to keep.

## Re-entrancy: the loop is the whole point

Two principles converge here. *The flow is re-entrant* — any beat can send you back to an earlier one — and *the flow is a loop* — production feeds the next task's Direction. Together they mean the artifacts you built are never "finished"; they are living documents that the next cycle refines.

A team operating this way does not experience requirements changing as a failure of planning. It experiences it as the system working: reality is teaching the specs, and the specs are teaching the next build.

## The milestone holds until its goal is met

A single feature loops through Observe back to Direction; a **milestone** has the same shape at a larger scale, and a gate to match. A milestone is not finished when its tasks are done — it is finished when its **goal** is met, expressed as the exit criteria in the milestone node's `## EXIT` section. So `add milestone-done` is **goal-gated**: it refuses to close a milestone while any exit criterion is still unchecked, and holds the milestone open until every box is checked. Those checkboxes are the human's affirmation that the goal is genuinely met — the engine reads the tally, it never judges the goal itself. `milestone-done` is the only path to `done`, and `add milestone-archive` refuses anything not yet done, so the one gate cannot be slipped.

While the milestone is held open, the work each task leaves behind — open lessons, and items discovered but out of scope — becomes its next tasks: the AI proposes them, the human confirms, and the loop continues until the goal is reached.

And when a deepened verify finds a criterion unmet on a task already `done`, `add reopen <task> --to <beat> --reason "…"` returns it to the flow with a recorded reason and a reset gate. A reopen fires while the milestone is still active — the goal-gate is exactly what held it open. The milestone is the loop made concrete; the exit criteria are its finish line.

> **Do:** release small, watch the checks, and feed every learning back into a spec.
> **Don't:** treat shipping as the end. The most valuable information about a feature arrives *after* it ships.
