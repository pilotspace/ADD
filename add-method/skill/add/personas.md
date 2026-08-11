# Personas — a project-fit lens (seed → grow → apply)

A **persona** is a project-fit requirements LENS the agent adopts so its work matches *this*
codebase's standards, not a generic default. It is not a chat costume: it is a small, versioned file
under `.add/personas/<slug>.md` that the design/build/verify/advisor surfaces load as **advice**.
The loop is **opt-in and additive** — a project with no personas behaves exactly as before.

A persona is a **lens, not a voice**. Tone and the deliverable's shape live in the agent's return
contract; the persona owns *judgment* — the rules it refuses to wave through, the smells it suspects,
the done-bar it measures against. A persona duplicating voice or shape is dead weight.

> **Command status.** Persona growth rides the delta loop — `add learn` (emit), `add fold`
> (consolidate at close), and `add status` (orient) are all **wired** (the real `add` CLI).

## The four machine-readable parts (what the engine checks, presence-based)

- **Identity** — the stance, with *earned perspective*: what this lens has seen succeed or fail.
  Scars, not a résumé (e.g. *a payments engineer who treats money as exact*).
- **Critical Rules** — the non-negotiables for this domain, each `**bold clause** — then the why`.
  Carry two default stances: **surface tradeoffs** (name the choice + its cost, never silently pick)
  and the **qualification gate** (name the simplest baseline that meets the contract — if it wins,
  take it and stop). Prefer a **named budget over an adjective** (`p95 < 200 ms`, `44×44 px`) — only
  a number the expert would defend and the lens can check in-session.
- **Default Requirement** — the one requirement in every deliverable by default.
- **Success Metrics** — MEASURABLE outcomes as INVARIANTS (true as the project grows, not a today
  snapshot), each sharpened by **the failure it guards against**. An invented statistic
  (`engagement +40%`) is the signature rot of weak persona corpora — never write one.

Frontmatter: `add new Persona` scaffolds `use-when:` (the boundary that routes THIS persona over
its siblings); `flow:` (design · build · advisor · verify — the surfaces that load it) and
`not-when:` are recommended, hand-authored, and read by nothing. Optional `## Abilities` (lead with
the ORIENT commands the lens runs on load), `## Anti-patterns` (guilty-until-proven instincts;
always include **read-before-you-assert**), `## Escalation`. Full schema: the persona-author
reference — referenced, never inlined.

## Planning loads through the advisor flow

Planning is a loading surface too — without a new vocabulary word: an **intake proposal** for the
milestone lane, a **milestone draft**, and the loop's **next-task proposal** each load the best-fit
persona whose `flow:` includes **advisor** (design also fits a design-shaped draft) BEFORE the
drafting starts, and the confirmed artifact records the lens (`add advise`). The load is by fit and
by roster: a bundle with no personas skips silently and behaves exactly as before.

This is the schema for a persona **you author**. The teacher corpus at
`.add/personas-teacher/` is a byte-verbatim third-party snapshot on its own schema and carries
neither key; route to one via `.add/personas-index/use-when.md`, the generated `use-when:` index vendored
beside it.

## Seed — at setup, from the teacher (full flow: `seed.md`)

ADD does not invent personas from nothing; it learns them from a **teacher** — a corpus of worked
agent definitions at the engine's `.add/personas-teacher/`, read **off-build** by the AI while
drafting, **never a runtime dependency** (nothing in the engine imports or needs it). `add init`
vendors this corpus into `.add/personas-teacher/` so a standalone bundle carries its own
teacher. Setup proposes a starter persona
or two that fit the domain (from `.add/specs/domain.md` + `system.md`); the human confirms. Seeding
writes `.add/personas/<slug>.md` and nothing else — no behaviour changes until a task applies one.
Don't start blank: distil the nearest teacher entry down to the four parts, then own it.

## Grow — observe → delta → fold (the human folds)

Personas are living documents; they improve through the delta loop (`deltas.md`). In a task's OBSERVE
beat the AI emits a **persona delta** — a one-line tagged proposal to add or sharpen a critical-rule,
success-metric, anti-pattern, or ability, written `open` with evidence, its hint naming the target
section:

```
- [UDD · open · persona:ui-designer · success-metric] 4.5:1 contrast (evidence: audit)
```

At close the **human** folds confirmed deltas into the persona file — the hinted section only,
**never clobbering** existing content, newest-first. The **engine never edits a persona**; the AI
never self-folds. So a persona gets *more* accurate every milestone instead of drifting. Two habits
keep growth honest: run one task **with** the persona and compare to the un-personaed result; and
prune any Critical Rule that fired zero times this milestone (a human-approved edit at the same close).

## Apply — four surfaces, all treat it as advice

An authored persona names its surfaces in `flow:`; `use-when:` / `not-when:` route it over a
sibling. For a teacher persona, the routing line is in `.add/personas-index/use-when.md`.

- **design (UDD)** — frames which rules and metrics a UI/UX slice must satisfy for these users.
- **advisor / streams** — a delegated subagent selects the best-fit persona; the returned verdict
  records which persona did the work, with severity markers (🔴 blocker · 🟡 concern · 💭 note).
- **verify** — the evidence-judging lens for the earned-green refute-read and the gate record.
- **build** — a domain-identity **lens** layered over the project's own standards: the persona is the
  domain stance, and it never overrides a trust rule or a frozen contract.

## The non-negotiable — a persona NEVER lowers a gate

A persona changes *how carefully* the work is done; it never changes *what passes*.

<constraints>
- **security = HARD-STOP** — always, whatever persona was adopted. A stronger persona never buys it back.
- **High-risk scope still escalates** to the human; a persona is expertise, not permission.
- **The engine stays NO-EXEC** — it never spawns, runs, or reads a persona on the build path. Select,
  load, and apply is the orchestrating agent's judgment; the engine only records that the record is
  present. Direction, freeze, evidence, and the gate stay exactly as strict as before.
</constraints>
