# 18 · Personas in practice — the project-fit loop

[← 17 Components — monorepo and multi-repo](./17-components.md) · [Contents](./README.md)

---

[Chapter 10](./10-personas.md) gives the model: a **persona** is a project-fit requirements
lens the agent adopts so its work matches *this* codebase's standards, not a generic default,
and it runs the loop **seed → grow → apply**. This chapter shows that model *applied* —
walked through one project, with the real verbs at each step. Nothing here is new mechanism;
it is chapter 10 on a workbench.

Take a small system with two parts: a payments API and a dashboard that spends against it.
Two lenses will earn their keep across a milestone — a `payments-engineer` and a
`ui-designer`.

## A persona is a small versioned file

A persona is not a chat costume. It is a typed node in the bundle,
`.add/personas/<slug>.md`, with four load-bearing parts the engine can check for presence:

- **Identity** — the stance the worker takes (*a payments engineer who treats money as exact*).
- **Critical Rules** — the non-negotiables for this domain, each with its *why*.
- **Default Requirement** — the one requirement the persona includes in every deliverable.
- **Success Metrics** — the measurable done-bar, in numbers where it can be.

Tone and the deliverable's shape live in the agent's return contract, not the persona — a
lens that duplicates voice or layout is dead weight.

## Seed — at setup, from the foundation

The first lenses are **seeded** during setup, distilled from the foundation (the domain and
standards in `.add/specs/domain.md` and `.add/specs/system.md`). ADD does not invent them
from nothing: `add init` vendors a **teacher** corpus into `.add/personas-teacher/`, read
off-build by the AI while drafting and never a runtime dependency. Setup proposes a starter
lens or two that fit the domain; a human confirms. Each is created like any other node:

```
add new Persona payments-engineer
add new Persona ui-designer
```

Don't start blank — distil the nearest teacher entry down to the four parts above (the
stance with earned scars, the rules each with its *why*, the one default requirement, the
measurable metrics), then own it. Seeding writes the node and nothing else: no behaviour
changes until a task applies one.

## Grow — observe → delta → fold

Personas are **living documents**; they sharpen through the same delta loop the specs use. In
a task's **observe** beat the AI emits a **persona delta** — a one-line, tagged proposal to
add or sharpen a rule, a metric, or an anti-pattern, filed `open` with evidence:

```
- [UDD · open · persona:ui-designer · success-metric] 4.5:1 contrast (evidence: audit)
```

At a retrospective the **human** folds confirmed deltas into the persona file — the hinted
section only, never clobbering what is there — with the same `add fold` step the foundation
uses. The engine never edits a persona and the AI never self-folds, so a lens gets *more*
accurate every milestone instead of drifting. Two habits keep growth honest: after a
consolidation, run one representative task **with** the lens and compare it to the un-lensed
result — a rule that never pulls its weight is dead weight — and prune any Critical Rule that
fired zero times this milestone.

## Apply — record the lens, on sequential work and parallel

A seeded, grown persona earns its keep only when work adopts it, and every surface treats it
the same way — as **advice**, never authority.

**On a sequential beat**, record the lens with `advise`:

```
add advise add-refund-endpoint --persona payments-engineer
```

This stamps the task `advised_by:` and nothing more — a NO-EXEC record of *which lens the
agent chose*. The named persona must be a real seeded node; advising an unseeded name is
refused (`R:BADPERSONA`), and re-advising re-routes the lens rather than stacking a second
one. Selecting and loading the lens — reading its Identity, Critical Rules, and metrics into
how the work is done — is the orchestrating agent's judgment; the engine only records that a
lens is present.

**On parallel streams**, personas ride the wave surface. `add wave payments-milestone` plans
the parallel wave from the task DAG and records the streams; the API stream runs behind the
`payments-engineer` lens in one git worktree while the dashboard stream runs behind the
`ui-designer` lens in another, each downstream of the frozen contract that orders them.
`add join <bundles…>` folds the finished stream bundles back — **PASS-only**, unioning their
deltas. The same lens body is plain text the agent loads regardless of which coding tool runs
the stream — tool-agnostic by construction ([01 · principle 8](./01-principles.md)).

**At verify**, the lens becomes the evidence-judging stance: the reviewer reads the diff
against the persona's Critical Rules and metrics, and its severity convention tags the
findings (🔴 blocker · 🟡 concern · 💭 note). On a security-sensitive node this is not
optional — the gate refuses a `PASS` with no lens on record (`R:NOCOVERAGE`): the lens does
the seeing, the floor does the stopping.

## The non-negotiable — a persona never lowers a gate

A persona changes *how carefully* the work is done; it never changes *what passes*. This is
the one hard rule across every surface:

- A **security** finding is always a **HARD-STOP**, whatever lens was adopted. A stronger
  persona is expertise, not permission, and never buys back a security finding.
- A **high-risk scope** still escalates to the human at its sensitivity floor. The lens
  advises the freeze; it never replaces it. A `data | architecture` task carries no lens on
  record is surfaced by `add doctor` as `unadvised_sensitive`, so an unseen sensitive beat
  stays visible.
- The engine stays a **NO-EXEC notary** throughout: it never spawns a subagent, never runs a
  persona, never reads one on the build path. It records that a lens is present and measures
  the record — it never auto-passes on a persona's say-so.

The persona layers a domain identity **over** the agent's baseline conduct and trust rules;
it never overrides a trust rule, and a trust rule is not a persona's to relax. In short: a
persona makes the agent *fit the project*. Direction, freezing, evidence, and the gate are
exactly as strict as they were before — the loop adds expertise, not permission.

---

> **Do:** grow a small corpus of lenses that carry your project's hard-won judgment, and
> record which lens advised each sensitive beat. **Don't:** treat a persona as a title with
> authority, or expect a lens to soften a gate — the floor and the gate are unmoved by
> whoever is looking.

---

[← 17 Components](./17-components.md) · [Contents](./README.md) · Next: [Appendix C Glossary →](./appendix-c-glossary.md)
