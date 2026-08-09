# 14 · The foundation and the five living specs

[← 13 The add command reference](./13-command-reference.md) · [Contents](./README.md) · Next: [15 Foundations and lineage →](./15-foundations-and-lineage.md)

---

## The engine needs ground

The three-beat loop in [Part II](./02-the-flow.md) is the *engine*: Direction
(rules · plan · red checks) → Build → Verify, run as a tight loop. TDD and ADD turn
inside that engine — author the failing check, let the AI generate code to green,
repeat.

But an engine needs something to stand on. Every loop quietly assumes context that
no single task owns: *what the words mean*, *what we are building right now*, and
*how its users experience it*. When that context lives only in someone's head, each new session —
and each new milestone — starts cold, and the AI fills the gap with plausible
guesses. That is the same failure the method exists to prevent ([00](./00-introduction.md)),
one level up.

The **foundation** is the layer that holds this context and *outlives every
milestone*. It is not new ceremony; it is the [living documentation](./12-bundle-format.md)
the method already names, made explicit as five living specs.

## Three concerns, one foundation

![The engine needs ground — the TDD ⇄ ADD engine runs on a DDD · SDD · UDD foundation: context feeds up, and any loop may send a correction back down](./add-foundation.png)

- **DDD — Domain.** The shared, precise language and the boundaries it lives in:
  the core concepts, the contexts they belong to, and the invariants that
  must always hold — the domain model behind the names. One name
  per concept — the same names the spec, the contract, and the code all use. (The
  [GLOSSARY](./appendix-c-glossary.md) holds the full term list; the foundation
  holds the model those terms describe.)

- **SDD — Spec.** *The living document.* What is being built right now and what is
  settled versus still open. This is not a frozen plan written once — it is the
  layer that changes as the loop learns ([01](./01-principles.md)). In ADD it does
  not duplicate the work; it **points** to the active milestone and the frozen
  contracts that other tasks build against.

- **UDD — UI/UX.** *Users use the interface, not the spec.* The experience designed
  before code: the **user flows** (happy and alternative paths), the **UI states**
  every screen must handle (loading · empty · error · success), and a design source
  of truth. The AI can generate a prototype from a design system; a person owns the
  empathy — what the user is trying to do, and what "good" feels like from their
  side. The checks ([Direction](./03-direction.md)) test that behaviour; the
  foundation keeps the design intent that makes a screen worth building.

These three concerns are the foundation the engine stands on. Together with the
**TDD ⇄ ADD** engine of [Part II](./02-the-flow.md), they are ADD's five
competencies. The first four feed context to the fifth, where the AI executes on it:

![ADD's five competencies — DDD · SDD · UDD · TDD · ADD: the first four are human-led and feed context to ADD, which is AI-led under your direction](./add-competencies.png)

> The diagram's foundation (DDD · SDD · UDD) and the method's own words — living
> documentation · the foundation · ubiquitous language — name the same three ideas. This
> chapter is where the diagram and the text finally meet.

## A thin index over living specs

A foundation that takes a week to write is a foundation no one keeps current. So
ADD keeps it **thin and split**: a single `.add/index.md` project card that every
session reads first, pointing into the **five living specs** under `.add/specs/`
where the standing picture actually lives — one file per competency, the same file
lessons land in as the loop learns.

```
.add/index.md                   — the project card, read first
  goal · invariants             — the bundle's standing direction
  sensitive_paths:              — the paths that pin the authority floor (§ governance)
  a compiled map into .add/specs/ and the active milestone

.add/specs/                     — the standing 5-DD picture (lessons land here)
  domain.md      (DDD)  — concepts · contexts · invariants
  system.md      (SDD)  — the spec stance: settled vs still open, architecture, conventions
  experience.md  (UDD)  — UI/UX: user flows · states · design intent
  quality.md     (TDD)  — testing + quality conventions
  method.md      (ADD)  — the loop and gate rules the engine runs on
```

Each spec has the same three sections — a `## Now` standing picture, a
`## Decisions that bind` ledger (the one section a compiled brief may cite), and a
`## Deltas` inbox where each new lesson prepends. Keep `index.md` to one screen: the
goal, the `invariants:` every task must hold, the `sensitive_paths:` floor, and the
pointers. The detail lives in the specs (and, past one screen, in a milestone or a
frozen contract), never relocated back up. You do not hand-write the whole thing:
at setup the AI **drafts** the foundation — silently from an existing codebase, or
from a short interview on a greenfield repo — and **seeds** the five specs; a single
human **confirms** that draft as committed direction (the setup-level analog of a
contract freeze). `add learn <lens>` then streams each loop's lessons straight into
the matching spec's `## Deltas`, so the picture stays current without a separate
write-up.

## How it feeds the engine — and takes feedback back

The arrow runs both ways, which is the whole point of a re-entrant method:

- **Down → up.** At the start of any session or milestone, read `index.md`
  (and, through its pointers, the `.add/specs/` picture) before touching a task. It
  is the cheapest way to point the AI in the right direction. `add status` prints
  a pointer to the foundation for exactly this reason.
- **Up → down.** When a loop reveals that the domain model was wrong, the spec
  stance has shifted, or a user assumption did not survive contact with reality,
  you **stop and update the foundation** — then come forward again. A passing check
  built on a broken foundation is still the wrong software, fast.

## Where it sits in the hierarchy

The foundation is the **Project tier** of the node hierarchy
([12 · The `.add/` bundle](./12-bundle-format.md)) — created once, kept for the
life of the product, owned above any single milestone.

![Three tiers of documents — Project (the foundation: .add/index.md + .add/specs/) → Milestone → Task: scope narrows and lifespan shortens down the stack](./add-hierarchy.png)

| Tier | Lives in | Lifespan | Holds |
|------|----------|----------|-------|
| **Project** (foundation) | `.add/index.md` + `.add/specs/` | whole product | invariants · decisions + the 5-DD standing picture (domain · spec stance · users · quality · method) |
| **Milestone** | `.add/milestones/<slug>.md` | one depth-bounded goal | scope · shared ground · exit criteria (CARD · SCOPE · GROUND · EXIT · CLOSE) |
| **Task** | `.add/tasks/<slug>.md` | one feature | one atomic node (CARD · RULES · PLAN · CHECKS · EVIDENCE · LESSONS) |

A milestone is a *version bump* to the foundation, not a fresh start: when it
closes, consolidate what it validated into the `.add/specs/` foundation (a settled
domain term into `domain.md`, a spec-stance shift into `system.md`, a confirmed user
journey into `experience.md`) — and open the next one against the same, now-richer,
ground. The consolidation is not informal: each loop emits **lessons** (tagged
`ddd · sdd · udd · tdd · add`) as they land, and at milestone close a person gathers
the open ones and folds them — into the matching spec's `## Now` /
`## Decisions that bind`, never clobbering what is there. See
[06 · The loop](./06-the-loop.md#lessons-learned-and-the-five-living-specs)
for the grammar, the ritual, and the tooling (`add deltas`, `add fold`).

## In the tooling

- `add init` scaffolds the bundle: the `index.md` project card and the five
  `.add/specs/` files as living-doc seeds; the AI then drafts their content and a
  single human confirmation freezes it as committed direction. Like every
  living-doc file, `init` **never overwrites a hand-edited one**.
- `add status` shows a one-line pointer to the foundation, so a fresh session
  re-orients on context before code.
- The guideline block written into `CLAUDE.md` / `AGENTS.md` tells any agent the
  same thing: run `status`, read the foundation, then work the loop.

> **The thesis, one level up.** The engine builds the thing right; the foundation
> keeps the engine pointed at the right thing — across every milestone, not just
> the current one.
