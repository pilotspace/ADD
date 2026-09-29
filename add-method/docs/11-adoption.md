# 11 · Adoption

[← 10 Personas — expert lenses](./10-personas.md) · [Contents](./README.md) · Next: [12 The .add/ bundle — ABF-1 format →](./12-bundle-format.md)

---

## A 90-day rollout

Adopt the method on one real product, not as an all-at-once mandate.

1. **Days 1–15 — Lay the foundation.** Install the skill on one pilot service. Let the agent write `.add/PROJECT.md` from the existing code — goal, `invariants:`, the test command — and seed the five specs. Read what it wrote and correct it; the invariants you keep bind every change from then on.
2. **Days 16–45 — One task, end to end.** Run a single real feature through the loop and read everything it leaves: the task file, the `freeze` commit, the evidence, the report. Most of the learning is in the assumptions it took.
3. **Days 46–75 — Trust the evidence.** Re-run the commands in a task's `## EVIDENCE` yourself at the recorded commit. Plant a defect a check should catch and confirm it goes red. Make a security finding and confirm it reaches the top of the report as a `HARD-STOP`.
4. **Days 76–90 — Widen.** Let the agent size freely across Quick, Task, Explore and Milestone; run a first set of independent tasks in parallel worktrees; keep promoting lessons that held into `## Decisions that bind`.

## Sizing — lanes, not a mode

There is no project-wide dial. Each request is routed by its size and by what it touches ([07](./07-setup-and-lanes.md)): Quick for small, mechanical work; a Task for one behavior worth a contract; Explore when the answer is the deliverable; a Milestone for a theme. Security, data and architecture are always at least a Task.

## Onboarding: enter from the build end

The most common onboarding mistake is starting newcomers at the most abstract work. Bring people in from the concrete end:

1. **Weeks 1–4 — Read the evidence.** Review finished tasks: does the verdict follow from the recorded output? Would you have taken the same assumptions?
2. **Weeks 5–8 — Checks and residue.** Improve a task's checks so they fail on a plausible wrong implementation; practise the security, concurrency and architecture read.
3. **Weeks 9–12 — Rules and assumptions.** Write the direction for a real request; sweep the six dimensions; see what you would have left silent.
4. **Beyond — Domain.** Decide what the project should be true about. That is the senior skill, not the entry skill.

## Tool portability

The method is plain text that refers to files in the repository; its seal is a git commit; its evidence is your own test command's output. Nothing depends on one agent.

| Concern | Where it lives |
|---|---|
| The method | `.claude/skills/add/SKILL.md` (and its four references) |
| Working state | `.add/PROJECT.md`, the open task and milestone files |
| Seal and history | git: `freeze(<slug>)`, `refreeze(<slug>)`, `verify(<slug>)` commits |
| Evidence | each task's `## EVIDENCE` |

Claude Code loads the skill natively (`/add`). Other agents read the managed ADD block the installer writes into `AGENTS.md` (and `CLAUDE.md`), which points them at the same skill file; if `.gemini/` exists, the installer also adds `AGENTS.md` to Gemini CLI's context files. An agent that reads neither file can be pointed at `.claude/skills/add/SKILL.md` directly. Switching agents changes who reads the bundle, nothing else.

## Coming from ADD 3.x

A 3.x bundle reads as-is; the extra files are history. See [20 · What changed in 4.0](./20-whats-new-in-4.md).

---

> Adoption is a loop too. Every cycle should fold improvements back into your own specs, invariants and personas.
