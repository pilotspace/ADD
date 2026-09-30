<!-- ADD:BEGIN — managed by the ADD installer; do not edit inside -->
## ADD — how to work in this repo

This project uses **ADD (AI-Driven Development)**: the AI plans, builds and verifies; the human
owns direction and reviews the result. There is no CLI. The method is one skill file
(`.claude/skills/add/SKILL.md`), run with files, git and the project's own test command.

**Orient first, every session:** read `.add/PROJECT.md` (`goal:`, `invariants:`, `test_cmd:`),
then the open task and milestone files under `.add/tasks/` and `.add/milestones/` (any `status:`
that is not `done` or `dropped`), and the last few commits. Resume an open task; otherwise size
the work.

**Size the work. You route and go; the human reviews after.**

| the request | lane | what persists |
|---|---|---|
| mechanical, or a small behavior: ≤3 adjacent files, one sitting, no unknowns | Quick | a red→green test + one commit |
| one behavior worth a written contract | Task | `.add/tasks/<slug>.md` + its commits |
| the answer IS the deliverable: investigate · evaluate · research | Explore | the task's `## FINDINGS` |
| a theme, or more than one task | Milestone | `.add/milestones/<slug>.md` + its tasks |

Floor: anything touching security · data · architecture, or a surface other code consumes, is at
least a Task. When in doubt, size up.

Then follow the skill: Direction (rules · assumptions · failing checks, sealed by a
`freeze(<slug>)` commit) → Build (to green, sealed files untouched) → Verify (seal intact · fresh
green run · residue review · verdict in `## EVIDENCE`, committed as `verify(<slug>): <verdict>`).

Rules that bind: the `invariants:` in PROJECT.md hold for every change, Quick included. Never
weaken a sealed check or edit the contract to get green; changed intent is a visible
`refreeze(<slug>)` commit. A security finding is a HARD-STOP verdict, flagged at the top of the
report.

Book: https://pilotspace.github.io/ADD/. Edit outside the markers.
<!-- ADD:END -->
