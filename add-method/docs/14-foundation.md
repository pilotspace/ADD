# 14 · The foundation and the five living specs

[← 13 Files and commits](./13-files-and-commits.md) · [Contents](./README.md) · Next: [15 Foundations and lineage →](./15-foundations-and-lineage.md)

---

## The loop needs ground

The three-beat loop of [Part II](./02-the-flow.md) is the engine of the method: write the failing checks, build to green, verify on evidence, repeat. But every loop quietly assumes context no single task owns — *what the words mean*, *how the system is built*, *who uses it*. When that context lives only in someone's head, each new session starts cold and the agent fills the gap with plausible guesses. That is the failure the method exists to prevent ([00](./00-introduction.md)), one level up.

The **foundation** holds that context and outlives every milestone: `.add/PROJECT.md` plus five living specs under `.add/specs/`.

![The loop needs ground — the TDD ⇄ ADD loop runs on a DDD · SDD · UDD foundation: context feeds up, and any loop may send a correction back down](./add-foundation.png)

## Five lenses, one file each

| lens | file | holds |
|---|---|---|
| **domain** (DDD) | `domain.md` | the business language and rules — one name per concept, the invariants that must hold |
| **system** (SDD) | `system.md` | architecture and interfaces — what is settled, what is still open |
| **experience** (UDD) | `experience.md` | users and their journeys, the states every screen must handle |
| **quality** (TDD) | `quality.md` | tests, reliability, performance — what counts as proof here |
| **method** (ADD) | `method.md` | how this team works — conventions that helped or hurt |

Together with the loop they are ADD's five competencies. The first four feed context; the fifth — the agent, building under direction — executes on it.

![ADD's five competencies — DDD · SDD · UDD · TDD · ADD: the first four feed context to ADD, which executes on it](./add-competencies.png)

## A thin index over living specs

A foundation that takes a week to write is one nobody keeps current. So it stays **thin and split**. `PROJECT.md` is one screen: the goal, the `invariants:` every change must hold, the test command, and a CARD saying where things stand. The detail lives in the specs, each with the same three sections:

- `## Now` — what is true today, in a few lines.
- `## Decisions that bind` — decisions every future task must follow, each with evidence. Direction reads these while grounding.
- `## Deltas` — lessons as they land, newest first, each `open` until it is `folded` into a decision or `rejected`.

You do not hand-write it all. On first use the agent drafts `PROJECT.md` and seeds the specs — from the code on an existing project, from a short conversation on an empty one — and you correct what it got wrong.

## How it feeds the loop — and takes feedback back

- **Down → up.** Every session starts by reading `PROJECT.md`; every Direction reads the `## Decisions that bind` that apply. It is the cheapest way to point the agent in the right direction.
- **Up → down.** When a task shows the domain model was wrong, or an architecture assumption did not survive, the lesson goes into the spec as a delta with evidence. When it holds on later work, it becomes a binding decision. A passing check built on a broken foundation is still the wrong software, fast.

## Where it sits

![Three tiers — Project (the foundation) → Milestone → Task: scope narrows and lifespan shortens down the stack](./add-hierarchy.png)

| Tier | Lives in | Lifespan | Holds |
|------|----------|----------|-------|
| **Project** | `.add/PROJECT.md` + `.add/specs/` | the whole product | goal · invariants · the five-lens standing picture |
| **Milestone** | `.add/milestones/<slug>.md` | one goal | scope · exit criteria · task list |
| **Task** | `.add/tasks/<slug>.md` | one change | rules · assumptions · plan · checks · evidence |

<sub>The drawing predates 4.0's flat file names; the table is current.</sub>

A milestone is a version bump to the foundation, not a fresh start: when it closes, what it validated is folded into the specs, and the next milestone begins on richer ground.

> **The thesis, one level up.** The loop builds the thing right; the foundation keeps the loop pointed at the right thing — across every milestone, not just the current one.
