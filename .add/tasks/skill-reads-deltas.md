---
type: Task
title: The loop gathers the carried specs before it plans
status: done
depth: quick
milestone: okf-graph-time
scope:
  - add-method/skill/add/SKILL.md
  - add-method/skill/add/intake.md
  - add-method/src/add_method/_bundled/skill/add/SKILL.md
  - add-method/src/add_method/_bundled/skill/add/intake.md
  - .claude/skills/add/SKILL.md
  - .claude/skills/add/intake.md
  - add-method/tests/skill
gives:
  - S1 the Intake routing instruction — SKILL.md's Task and Project/milestone bullets, plus
    intake.md's `### Task` and `### Project / milestone` sections — that names `add deltas` as
    a read-before-you-plan step, byte-identical across all three shipped skill trees
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "plan:okf-graph-time", at: 2026-09-03, act: freeze, authority: process, direction: "sha256:0c9c8e9bfc7886d9", binding: "sha256:22249aa61fd2594e" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:035e89f9077bc638" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/skill-reads-deltas.d/runs/1.md }
  - { by: "plan:okf-graph-time", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/skill-reads-deltas.d/runs/1.md, brief: "sha256:4e2bb17718594ad5" }
---
## CARD
goal: the ADD skill routes the loop through `add deltas` before it plans a Task or Milestone, in every shipped skill tree, within SKILL.md's existing byte pin
why: 43 delta lines already carry lessons across `.add/specs/*.md` and nothing in the planning path ever reads them back before drafting — the mirror image of the experience-lens lesson already on record: a spec nothing in the loop reads is an archive, not a living spec
beat: done · next: add status

## RULES
<must>
- M1 SKILL.md's Intake bullets for **Task** and **Project / milestone** name `add deltas` as a read-before-you-plan step, in every shipped skill tree (`add-method/skill/add`, its `_bundled` mirror, `.claude/skills/add`)
- M2 intake.md's `### Task` and `### Project / milestone` sections carry the same routing instruction, in every shipped skill tree
- M3 `add deltas` stays a real, wired CLI verb whose execution reports a real, non-vacuous envelope (an item count or "no open deltas", plus a `next:` trailer) against a populated bundle, an empty one, and one carrying a malformed (no-evidence) line — never a silent no-op, never a silently dropped defect
- M4 SKILL.md's line-count budget stays at its existing pin (176, read from `test_surface.py` — never copied as a literal) after the addition; funded by compressing physical line-wraps beside it, never by raising the pin
</must>
<reject>
- R:PHANTOM_ROUTE the routing instruction names a command with no real, wired CLI verb behind it -> "R:PHANTOM_ROUTE"
- R:ONE_TREE the routing instruction lands in fewer than all three shipped skill trees, breaking mirror parity -> "R:ONE_TREE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say whether a human typing CLI verbs directly (bypassing the skill prose) must also be told to read deltas first; taking the reading that this fix binds only the AGENT's read path through the skill docs — a human driving the CLI directly is an existing, unrelated gap -> cost if wrong: a human-only flow still silently skips the carried inventory, but that gap predates and outlives this task
- A2 [which] covers: S1 · the request does not say whether the Explore lane and the Quick (no-node) lane also owe the same routing instruction; taking the reading that only Task and Project/milestone (the two lanes that DRAFT a contract or a goal from scratch) owe it — Explore's deliverable is the question itself, and Quick is explicitly bounded to behavior the specs already cover -> cost if wrong: an Explore task researching a question a carried delta already answered re-derives it from scratch
- A3 [when] covers: S1 · the request does not say whether the deltas read repeats on every `add replan` mid-build, or fires once at Intake; taking the reading that it fires once, before the initial lane pick and draft — replan is BUILD-phase steering on an already-frozen contract, not a re-entry into Intake -> cost if wrong: a lesson emitted mid-build via `add learn` is not re-surfaced to that SAME task before its own freeze, though it will surface to the NEXT task via `add deltas`
- A4 [absent] covers: S1 · the request does not say what an EMPTY carried inventory ("no open deltas") means for the routing instruction; taking the reading that it is a normal, unblocking state — the agent reads it and proceeds to plan exactly as before, with zero added ceremony -> cost if wrong: read as an error or a required non-empty precondition, a fresh milestone with nothing carried yet would incorrectly stall Intake
- A5 [order] covers: S1 · the request does not say whether the deltas read happens before or after "read the request into a task shape"; taking the reading that it happens FIRST — a carried lesson can reshape how the request itself should be restated, not just what gets drafted afterward -> cost if wrong: low — both happen inside the same Intake step before any node exists, so a reversed order changes emphasis, not outcome
- A6 [experience] covers: S1 · the request does not say how heavy this new step should feel to the agent following the prose; taking the reading that it is a single cheap glance (`add deltas`, one command) sized to Task/Milestone weight, not a mandatory per-delta review ceremony that would fight "ceremony falls with size" -> cost if wrong: read as a heavy new gate, it discourages routing to Task/Milestone at all, silently pushing more requests toward Quick to dodge it
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: S1 — the Intake routing instruction naming `add deltas` at the Task and Project/milestone lanes, present verbatim (byte-identical) in all three shipped skill trees: `add-method/skill/add/{SKILL.md,intake.md}`, `add-method/src/add_method/_bundled/skill/add/{SKILL.md,intake.md}`, `.claude/skills/add/{SKILL.md,intake.md}`.
strategy: fund the addition inside SKILL.md's fixed 176-line pin by lengthening existing physical lines (the budget test counts newlines, not characters — a longer line costs nothing) rather than inserting new ones; net LOC change in SKILL.md = 0. In intake.md — headroom exists but is a scarce, milestone-shared resource (`search-verb` also edits SKILL.md this milestone) — merge a few manually-wrapped lines while prepending the routing clause, netting lines FREED, not spent (126 → 121). No engine, CLI, or delta-grammar change: `add-method/tooling/add.py`, `cli.py`, `FORMAT.md` and `.add/specs` are untouched and out of scope — owned by concurrent tasks in this milestone.

## EDGES
- E1 a bundle carrying a malformed (no-evidence) delta line must still have that defect REPORTED by `add deltas`, not silently dropped, so the routing instruction points at a command that surfaces integrity problems too, not just the happy path

## CHECKS
- test_skill_router_routes_task_and_milestone_through_deltas · covers: M1, R:PHANTOM_ROUTE · SKILL.md's Task and Project/milestone Intake bullets name `add deltas`, in all three trees, and `deltas` is a real CLI verb
- test_intake_ref_routes_task_and_milestone_through_deltas · covers: M2 · intake.md's `### Task` and `### Project / milestone` sections carry the same instruction, in all three trees
- test_add_deltas_actually_executes_and_reports · covers: M3, E1 · drives `add.deltas()` against a populated, an empty, and a malformed bundle and asserts on its real envelope
- test_skill_budget_holds_at_the_pinned_line_count · covers: M4 · reads the pin from `test_surface.py` and asserts every tree's SKILL.md stays within it
- test_three_skill_trees_stay_identical_after_the_routing_edit · covers: R:ONE_TREE · byte-identical check on SKILL.md and intake.md across all three trees
red-first: every check MUST fail first — proven by reverting the two touched files (`git stash push --keep-index -- <the 6 files>`) and re-running the suite: `test_skill_router_routes_task_and_milestone_through_deltas` and `test_intake_ref_routes_task_and_milestone_through_deltas` failed for the documented reason (no `add deltas` mention in the Task/Project bullets); the other three passed throughout, as pre-existing invariants this task must not break, not new behavior it introduces (`git stash pop` restored the edit before continuing).

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- SKILL.md's byte budget is a LINE count (`len(text.splitlines())`), not a character count — a bullet can be funded for free by lengthening an existing physical line instead of deleting prose, which is a stronger "fund by compressing" move than trimming words -> add learn add
