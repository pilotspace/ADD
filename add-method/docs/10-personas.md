# 10 · Personas — the team as lenses

[← 09 Governance](./09-governance.md) · [Contents](./README.md) · Next: [11 Adoption →](./11-adoption.md)

---

## The team is a set of lenses, not a set of chairs

Older methods model a team as a fixed org chart — a product owner here, an architect there, a fixed title accountable for each column. ADD keeps the *judgment* those titles carried and drops the chart. The unit is a **persona**: a project-fit requirements lens the agent adopts so its work matches *this* codebase's standards, not a generic default. A persona is not a job title and not a chat costume — it is a small, versioned file the design, build, and verify surfaces load as **advice**.

Why lenses instead of roles: an AI agent does not sit in a chair, and the same agent can build behind a payments engineer's caution on one task and a UI designer's contrast rules on the next. What you want to preserve is not *who* attends the meeting but *what judgment gets applied* — the rules a domain refuses to wave through, the smells it suspects, the done-bar it measures against. A persona carries exactly that, and nothing else: tone and the deliverable's shape live in the agent's return contract, so a persona duplicating voice or layout is dead weight.

The persona loop has three moves — **seed → grow → apply** — and it is opt-in and additive: a project with no personas behaves exactly as before.

## Seed — a corpus, offered at setup

ADD does not invent personas from nothing; it learns them from a **teacher** — a corpus of worked agent definitions. `add init` vendors this corpus into `.add/personas-teacher/` so a standalone bundle carries its own teacher, read off-build by the AI while drafting and never a runtime dependency. Setup proposes a starter persona or two that fit the domain (from the living domain and system specs); a human confirms. Seeding writes a persona node and nothing else — no behavior changes until a task applies one.

A seeded persona is a typed node in the bundle, created like any other:

```
add new Persona payments-engineer
```

Don't start blank: distil the nearest teacher entry down to its load-bearing parts — the stance with earned scars (*a payments engineer who treats money as exact*), the non-negotiable rules each with its *why*, the one default requirement, the measurable success metrics — then own it.

## Grow — lenses sharpen over time

Personas are living documents; they improve through the same delta loop the specs use. In a task's observe beat the AI emits a **persona delta** — a one-line, tagged proposal to add or sharpen a rule, a metric, or an anti-pattern, filed `open` with evidence:

```
- [UDD · open · persona:ui-designer · success-metric] 4.5:1 contrast (evidence: audit)
```

At close, a **human** folds confirmed deltas into the persona file — the hinted section only, never clobbering what is there. The engine never edits a persona and the AI never self-folds, so a persona gets *more* accurate every milestone instead of drifting. Two habits keep growth honest: run one task with the persona and compare it to the un-lensed result, and prune any rule that fired zero times this milestone.

## Apply — record a lens, on sequential work and parallel

A persona has no effect until a task adopts it. There are two ways in, matching the two ways ADD runs work.

**On a sequential beat**, record the lens with `advise`:

```
add advise <task> --persona payments-engineer
```

This stamps the task with `advised_by:` and nothing more. It is a NO-EXEC record: the engine writes down *which lens the agent chose*; it never runs, spawns, or judges the persona. The named persona must be a real seeded node — advising an unseeded name is refused (`R:BADPERSONA`) — and re-advising re-routes the lens rather than stacking a second one.

**On parallel streams**, personas ride the wave surface. `add wave <milestone>` plans a parallel wave from the task DAG and records the streams; each stream runs behind its own frozen contract in a git worktree, under its own lens. `add join` folds the finished stream bundles back — PASS-only, unioning their deltas. The same sensitivity floor that governs a sequential task carries into the wave: a stream whose task touches data, architecture, or security is held to its floor regardless of which lens advised it.

## Who owns the residue — recast as lenses plus the floor

The old org chart's real value was answering *who owns the dangerous surfaces* — security, architecture, testing. ADD keeps the answer and changes its form: the residue is owned by a **lens plus the sensitivity floor**, not a fixed title.

- **Security.** The lens that assumes the AI will hardcode a secret and invent a package name — and gates against both from setup. But the ownership is not the lens's to grant: a `security` task's floor is `human`, and a security finding is always `HARD-STOP`. Recording a security lens is, in fact, required — the gate refuses a `PASS` on a security-sensitive node with no lens on record (`R:NOCOVERAGE`). The lens does the seeing; the floor does the stopping.
- **Architecture.** The lens that treats the frozen contract as a one-way door and reads every change against the project's layering. Its floor is `plan` — a real task node with a human at the freeze — so a change to a load-bearing surface can never be quietly derived.
- **Testing.** The lens that makes "done" machine-checkable and never lets a check be weakened to pass. It is enforced by the gate's bound-receipt rule, not by a person's vigilance: every rule must trace to a passing check.

A sequential task that touches one of these surfaces but carries no lens is surfaced by `add doctor` as `unadvised_sensitive` — a nudge for the data and architecture floors, a `warn` for security — so an unseen sensitive task stays visible.

## The non-negotiable — a persona never lowers a gate

A persona changes *how carefully* the work is done; it never changes *what passes*.

- **Security stays `HARD-STOP`**, always, whatever lens advised. A stronger persona is expertise, not permission, and never buys back a security finding.
- **A high-risk scope still escalates** to the human at its sensitivity floor. The lens advises the freeze; it does not replace it.
- **The engine stays a NO-EXEC notary.** It records that a lens is present; it never runs the method, spawns an agent, or lets a persona freeze or gate. Selecting, loading, and applying the lens is the orchestrating agent's judgment. Direction, the freeze, the evidence, and the gate stay exactly as strict as before.

---

> **Do:** grow a small corpus of lenses that carry your project's hard-won judgment, and record which lens advised each sensitive beat. **Don't:** treat a persona as a title with authority, or expect a lens to soften a gate — the floor and the gate are unmoved by whoever is looking.
