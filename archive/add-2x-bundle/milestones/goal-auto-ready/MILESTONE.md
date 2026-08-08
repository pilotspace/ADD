# MILESTONE: Goal-auto-ready — goal-clarity earns autonomy

goal: a goal is auto-ready when its acceptance criteria are concrete enough for the engine to self-verify the result against — so autonomy is earned by goal-clarity, not assumed (with auto seeded as the project default)
rationale: sub-milestone of the live autonomy theme (v6→v7→flag-first-freeze). NORTH-STAR (recorded direction, NOT this milestone's deliverable): challenge the spine — drive toward fewer/zero human gates. This milestone builds the PREREQUISITE — a goal the engine can self-verify against; whether the freeze gate is actually relaxed is deferred to its own later milestone. This scope itself runs risk: high + lowered autonomy (the method gating its own redefinition).
stage: mvp · status: active · created: 2026-06-10

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
- a PROJECT-level `autonomy: auto` default written at init (PROJECT.md), inherited by new tasks, surfaced in status   [init-auto-default]
- a definition + check of "auto-ready goal": the acceptance-criteria bar a goal must carry to be machine-self-verifiable, wired to the existing milestone goal-gate (`milestone_goal_unmet`) + exit-criteria checkboxes   [goal-auto-ready-gate]
- book/glossary/skill name "auto-ready goal" + the goal→autonomy link (prose ≡ enforcement)
Out:
- removing/relaxing the freeze gate or the one-human-approval floor — DEFERRED (the spine decision; its own later milestone)
- closing the high-risk-guard "undeclared scope passes" hole — recorded ceiling, a separate concern
- the AI auto-GENERATING goals/criteria — would re-introduce circular trust
- any change to the per-task 3-mode autonomy contract just frozen in flag-first-freeze — additive only

## Shared decisions & glossary deltas   (living — every task must honor these)
- auto-ready goal — a goal whose acceptance criteria are concrete/observable enough that the engine can verify a result against them without human judgement (new GLOSSARY term).
- irreducible-floor rule — the human anchor cannot reach zero; it MOVES from "approve the frozen contract" toward "declare the risk + approve the goal." Recorded, not enforced this milestone.

## Shared / risky contracts (freeze these first)
- what makes a goal "auto-ready" (the acceptance-criteria bar + its check shape) -> owning task goal-auto-ready-gate (risk: high — method-defining → lowered autonomy)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] init-auto-default     depends-on: none               — project seeds autonomy: auto at init; new-task inherits; status surfaces it
- [ ] goal-auto-ready-gate  depends-on: init-auto-default   — define + check an auto-ready goal (machine-checkable acceptance criteria); risk: high

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py init` writes `autonomy: auto` into the new PROJECT.md, and `add.py status` shows the inherited project default   (← init-auto-default) (verify: `test_init_auto_default.py`)
- [x] a goal lacking machine-checkable acceptance criteria reads NOT-auto-ready (engine/check); one carrying them passes   (← goal-auto-ready-gate) (verify: `test_goal_auto_ready_gate.ClassifierTest`)
- [x] GLOSSARY + book name "auto-ready goal" + the goal→autonomy link, synced ×3   (← goal-auto-ready-gate) (verify: `test_goal_auto_ready_gate.DocsAccordTest`)
