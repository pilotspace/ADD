# 06 · Learn — lessons, milestones, the report

[← 05 Verify — evidence, residue, refute, verdict](./05-verify.md) · [Contents](./README.md) · Next: [07 Setup and the four lanes →](./07-setup-and-lanes.md)

---

## The flow is a loop, not a line

Older mental models end at "ship". That framing breeds a common pathology: release becomes a finish line, and defects get hidden to protect it. In ADD, a verified task is where the most useful information starts to arrive — what surprised you, which assumption was wrong, what production does with the change. That information is the input to the next task's Direction.

## Lessons go into the living specs

A lesson worth keeping — a surprise, a wrong assumption, an escaped defect — goes into the matching spec under `.add/specs/`, in its `## Deltas` section, with evidence:

```markdown
## Deltas
- 2026-09-28 open · a transfer's ownership check must run before any balance read, or timing leaks which account ids exist (evidence: verify(transfer-own-accounts) 99f2b86)
```

Five lenses, one file each:

| lens | file | a delta here means you learned about… |
|---|---|---|
| domain | `domain.md` | a business rule, term or boundary the spec had wrong |
| system | `system.md` | architecture, interfaces, dependencies |
| experience | `experience.md` | users, their journeys, what made it hard |
| quality | `quality.md` | tests, reliability, performance — a hollow or missing check |
| method | `method.md` | how this team works — a convention that helped or hurt |

**No evidence, no delta.** A lesson without a commit, a task or a command behind it is an opinion.

A delta that held on later work is **promoted** to `## Decisions that bind`, and from then on it binds every task: Direction reads it while grounding. A delta that turned out wrong is marked `rejected`, not deleted, so the trail survives. An **escaped defect** records why the checks missed it and the check that now prevents it.

## Reuse the checks as monitors

The checks that drove the build describe the behavior you expected. After release they describe the behavior to watch: the rate of each named refusal (`amount_invalid`, `insufficient_funds`, `forbidden`), the error rate, the latency of the atomic update under load. A spike in one refusal is a signal, not noise — and it becomes a delta, then a task.

## Milestones: done when the goal is met

A theme becomes `.add/milestones/<slug>.md`:

```markdown
## CARD
goal: users can move money between their own accounts safely
why: first payments slice

## SCOPE
In:  same-currency transfers between own accounts
Out: FX, scheduled transfers, transfers to other users

## EXIT
- [x] a transfer moves money atomically — evidence: verify(transfer-own-accounts) 99f2b86
- [ ] a refused transfer changes no balance under concurrency — evidence:

## TASKS
- transfer-own-accounts — move money between own accounts
- transfer-concurrency-probe — prove no overdraw under parallel load (after: transfer-own-accounts)
```

Ground once for the milestone, then run each task through the loop. **A milestone is done when every EXIT box is ticked with evidence on the line — not when its tasks are.** Tasks done but the goal unmet? Gather the open deltas and the out-of-scope finds, add the next tasks, and continue. Set `status: done` only when every box carries its evidence.

## The report — the human's review

Every session ends with a report the human can act on. It is the review surface that replaced up-front approval, so it is written to make disagreeing easy:

1. **`HARD-STOP`s and open risks first.** A security finding is never buried.
2. **Per task:** the goal, the verdict, the freeze commit, the evidence, and **every assumption the agent took, costliest if wrong first** — the decisions the human did not make. "Any caller may cancel any booking" goes above "errors are JSON".
3. **What is next.** Update `PROJECT.md`'s CARD (`state:` and `next:`).

Open a pull request when the repository uses them; the report is its description.

> **Do:** release small, watch the checks, and turn every surprise into a delta with evidence.
> **Don't:** treat a verified task as the end. The most useful information about a change arrives after it ships.
