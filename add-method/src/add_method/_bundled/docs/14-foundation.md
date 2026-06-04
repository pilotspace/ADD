# 14 · The foundation: project context across milestones

[← 13 Adoption](./13-adoption.md) · [Contents](./README.md) · Next: [Appendix A Templates →](./appendix-a-templates.md)

---

## The engine needs ground

The flow in [Part II](./02-the-flow.md) is the *engine*: Specify → Scenarios →
Contract → Tests → Build → Verify, run as a tight loop. TDD and ADD turn inside
that engine — write the failing test, let the AI generate code, repeat.

But an engine needs something to stand on. Every loop quietly assumes context that
no single task owns: *what the words mean*, *what we are building right now*, and
*how its users experience it*. When that context lives only in someone's head, each new session —
and each new milestone — starts cold, and the AI fills the gap with plausible
guesses. That is the same failure the method exists to prevent ([00](./00-introduction.md)),
one level up.

The **foundation** is the layer that holds this context and *outlives every
milestone*. It is not new ceremony; it is the [survivor layer](./appendix-f-requirements-matrix.md)
the method already names, made explicit as three concerns.

## Three concerns, one foundation

![The engine needs ground — the TDD ⇄ ADD engine runs on a DDD · SDD · UDD foundation: context feeds up, and any loop may send a correction back down](./add-foundation.png)

- **DDD — Domain.** The shared, precise language and the boundaries it lives in:
  the core concepts, the modules/contexts they belong to, and the invariants that
  must always hold — the domain model and context map behind the names. One name
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
  of truth — a `DESIGN.md` or clickable prototype. The AI can generate a prototype
  from a design system; a person owns the empathy — what the user is trying to do,
  and what "good" feels like from their side. The scenarios ([04](./04-step-2-scenarios.md))
  test that behaviour; the foundation keeps the design intent that makes a screen
  worth building.

These three foundation competencies, together with the **TDD ⇄ ADD** engine of
[Part II](./02-the-flow.md), are ADD's five. The first four feed context to the
fifth, where the AI executes on it:

![ADD's five competencies — DDD · SDD · UDD · TDD · ADD: the first four are human-led and feed context to ADD, which is AI-led under your direction](./add-competencies.png)

> The diagram's foundation (DDD · SDD · UDD) and the method's own words — survivor
> layer · living document · ubiquitous language — name the same three ideas. This
> chapter is where the diagram and the text finally meet.

## One file, not three

A foundation that takes a week to write is a foundation no one keeps current. So
ADD realizes all three concerns as **one survivor document — `PROJECT.md`** — with
one short section each, plus an append-only record of key decisions:

```
.add/PROJECT.md
  ## Domain (DDD)                — concepts · contexts · invariants
  ## Spec / Living Document (SDD)— → active milestone + frozen contracts
  ## Users (UDD)                 — UI/UX: user flows · states · DESIGN.md / prototype
  ## Key Decisions               — append-only: date · decision · why · outcome
```

Keep it to one screen. If a section wants to grow into a manual, that is a signal
the detail belongs in a milestone or a contract, not the foundation. The foundation
is the *thin, durable* context the engine reads first — not a place to relocate the
work.

## How it feeds the engine — and takes feedback back

The arrow runs both ways, which is the whole point of a re-entrant method:

- **Down → up.** At the start of any session or milestone, read `PROJECT.md`
  before touching a task. It is the cheapest way to point the AI in the right
  direction. `add.py status` prints a pointer to it for exactly this reason.
- **Up → down.** When a loop reveals that the domain model was wrong, the spec
  stance has shifted, or a user assumption did not survive contact with reality,
  you **stop and update the foundation** — then come forward again. A passing test
  built on a broken foundation is still the wrong software, fast.

## Where it sits in the hierarchy

The foundation is the **Project tier** of the document hierarchy
([Appendix F](./appendix-f-requirements-matrix.md)) — created once, kept for the
life of the product, owned above any single milestone.

![Three tiers of documents — Project (the foundation, .add/PROJECT.md) → Milestone → Task: scope narrows and lifespan shortens down the stack](./add-hierarchy.png)

| Tier | Lives in | Lifespan | Holds |
|------|----------|----------|-------|
| **Project** (foundation) | `.add/PROJECT.md` + survivor files | whole product | domain, spec stance, users, decisions |
| **Milestone** | `.add/milestones/<slug>/MILESTONE.md` | one depth-bounded goal | scope, shared contracts, exit criteria |
| **Task** | `.add/tasks/<slug>/TASK.md` | one feature | the seven-step artifacts |

A milestone is a *version bump* to the foundation, not a fresh start: when it
closes, fold what it validated into `PROJECT.md` (a decision, a settled domain
term, a confirmed user journey) and open the next one against the same, now-richer,
ground. The fold is not informal: each loop emits **competency deltas** (tagged
`DDD · SDD · UDD · TDD · ADD`) in its Observe step, and at milestone close a person
gathers the open ones and folds them — append-only, with the `foundation-version:`
bumped — into the foundation. See [09 · The loop](./09-the-loop.md#competency-deltas-and-the-foundation-fold)
for the grammar, the ritual, and the tooling (`add.py deltas`, `add.py check`).

## In the tooling

- `add.py init` scaffolds `PROJECT.md` as a survivor file — and, like every
  survivor file, **never overwrites a hand-edited one**.
- `add.py status` shows a one-line pointer to the foundation, so a fresh session
  re-orients on context before code.
- The guideline block written into `CLAUDE.md` / `AGENTS.md` tells any agent the
  same thing: run `status`, read the foundation, then work the loop.

> **The thesis, one level up.** The engine builds the thing right; the foundation
> keeps the engine pointed at the right thing — across every milestone, not just
> the current one.
