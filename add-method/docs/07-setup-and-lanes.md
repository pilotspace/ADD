# 07 · Setup and the four lanes

[← 06 Learn — lessons, milestones, the report](./06-the-loop.md) · [Contents](./README.md) · Next: [19 Explore — when the answer is the deliverable →](./19-dynamic-workflow.md)

---

## Setup: install the skill, let the agent write the bundle

Install once from the project root, with whichever ecosystem you have:

```bash
npx @pilotspace/add init                              # Node / npm
pip install pilotspace-add && pilotspace-add init     # Python / pip
```

Or, in Claude Code, as a plugin: `/plugin marketplace add pilotspace/ADD`, then `/plugin install add@add-method`.

The installer drops files only: the `add` skill into `.claude/skills/add/`, the starter personas into `.add/personas/` (never overwriting one you already have), the persona source material, and — for agents other than Claude Code — a short managed ADD block in `AGENTS.md` or `CLAUDE.md` that points the agent at the skill. It runs nothing and opens no network connection.

**The bundle is the agent's first move.** In Claude Code, type `/add` and say what you want. On a project with no `.add/PROJECT.md` yet, the agent creates it — `goal:`, `invariants:`, `test_cmd:` — along with empty `specs/`, `milestones/` and `tasks/`, finds the test command, and continues with your request. On an existing codebase it drafts from the code; on an empty one it asks you briefly.

```markdown
---
type: Project
title: payments
goal: let customers hold and move money between their own accounts
invariants:
  - money is never created or destroyed by a transfer
  - the test suite runs offline with no credentials
test_cmd: pytest
stage: mvp
---
## CARD
goal: let customers hold and move money between their own accounts
state: accounts exist; transfers not started
next: transfer between own accounts
```

The `invariants:` bind every change from then on, including the smallest.

---

## The four lanes: size the request before you create scope

Not every request deserves a task file; forcing one onto a typo is ceremony. The agent sizes each request as it arrives and routes it to the **lightest lane that is safe**. Nobody approves the route in advance; the human sees it in the report and can say "make it a task" next time.

| the request | lane | what persists |
|---|---|---|
| mechanical, or a small behavior: ≤3 adjacent files, one sitting, no unknowns | **Quick** | a red→green test + one commit |
| one behavior worth a written contract | **Task** | `.add/tasks/<slug>.md` + its commits |
| the answer IS the deliverable — investigate · evaluate · research | **Explore** ([19](./19-dynamic-workflow.md)) | the task's `## FINDINGS` |
| a theme, or more than one task | **Milestone** | `.add/milestones/<slug>.md` + its tasks |

**Quick.** Write the failing test, watch it fail, make it pass, run the suite, review your own diff, and commit `<type>(<scope>): <what>` with a one-line why. No task file. `invariants:` still hold. Skipped ceremony is never skipped review: the check is still written and run red.

**Task.** One behavior worth a contract: the full loop of chapters [03](./03-direction.md)–[05](./05-verify.md).

**Explore.** When the primary work is answering a question — why does this fail, which library, is this approach viable — not editing code. One unknown that would change a contract's shape is already reason to explore first: sealing a contract on a guess ships the wrong thing with a perfect test run.

**Milestone.** A theme, or a slice too big for one task: goal, in/out scope, exit criteria, and a breadth-first task list ([06](./06-the-loop.md)).

### The floor — what always sizes up

Anything touching **security · data · architecture**, or a surface other code consumes, is **at least a Task** — never Quick, however small the diff. When in doubt, size up.

> **Do:** route a typo or a config value to Quick — a test, a commit, done.
> **Don't:** send anything touching auth, stored data, or an architectural boundary to Quick, however trivial it looks.

### Changing something already sealed

A request that changes a sealed contract or a shipped `gives:` surface is not new scope. It goes back to the task that owns it: a `refreeze(<slug>): <why>` commit if the task is still open, or a new task that names the one it changes if that task is done — and every task whose `needs:` cites the surface is re-verified.

---

The pace of a project is set by judgment and verification capacity, not by how fast the AI types. More agents do not compress verification; they only fill the time around it — which is what [parallel work](./08-parallel-work.md) is for.
