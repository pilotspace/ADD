# 18 · Personas — the project-fit learning loop

[← 17 Components](./17-components.md) · [Contents](./README.md) · Next: [Appendix A Templates →](./appendix-a-templates.md)

---

A **persona** is a project-fit requirements lens the agent adopts so its work matches *this*
codebase's standards instead of a generic default. It is not a chat costume: a persona is a small,
versioned file under `.add/personas/<slug>.md` with four machine-readable parts —

- **Identity** — the stance the worker takes (e.g. *a payments engineer who treats money as exact*).
- **Critical Rules** — the constraints that must hold (the non-negotiables for this domain).
- **Default Requirement** — the one requirement the persona includes in every deliverable by default.
- **Success Metrics** — the measurable done-bar (what "good" looks like, in numbers where it can).

Those four are what the engine checks (presence-based). The persona **template**
(`templates/personas/_template.md.tmpl`) is the canonical enumeration of the full schema — it also
recommends `flow:` and `use-when:`/`not-when:` frontmatter plus an `## Abilities` section, and
allows optional `## Anti-patterns` and `## Playbook` sections.

The **persona loop** is how those files come to exist, improve, and get used: **seed → grow →
apply**. The loop is opt-in and additive — a project with no personas behaves exactly as before.

## Where personas come from — the teacher

ADD does not invent personas from nothing. It learns them from a **teacher**: a corpus of worked
agent definitions that ADD ships as a vendored local library at `.add/personas-teacher/`.
The teacher is read **off-build**, by the AI, while drafting a persona — it is a *source of ideas*,
**never a runtime dependency**: nothing in the engine imports it, fetches it, or needs it present to
run. You distil a teacher entry down to the three-part shape above and commit the result; from then
on the project owns that persona outright.

## Seed — at setup

The first personas are **seeded** during project setup, from the foundation (`PROJECT.md`'s domain
and standards). Setup proposes a starter persona or two that fit the project's domain; the human
confirms. Seeding writes `.add/personas/<slug>.md` and nothing else — no behaviour changes until a
task actually applies one.

## Grow — observe → delta → consolidate

Personas are **living documents**: they improve through the same loop the foundation uses. In a
task's **observe** phase the AI emits a **persona delta** — a one-line, tagged proposal to add or
sharpen a critical-rule, success-metric, anti-pattern, or ability, written `open` with evidence (just like a lesson learned).
At a retrospective the human **consolidates** confirmed deltas into the persona file (the same
`fold` step the foundation uses), bumping it forward. The consolidation is judgment-free
transcription: the engine routes a confirmed delta into the named
persona's `## Critical Rules`, `## Success Metrics`, `## Anti-patterns`, or `## Abilities` section and **never clobbers** existing content.
So a persona gets *more* accurate every milestone instead of drifting.

Growth is additive, but it should not be unmeasured. Two retrospective habits keep it honest:
after seeding or a major consolidation, run one representative task **with** the persona loaded
and compare it to the un-personaed result — growth without a check risks rules that never pull
their weight. And ask which Critical Rules fired zero times this milestone; pruning a dead rule
is a human-approved edit at the same retrospective, so the persona stays lean instead of accreting.

## Apply — three surfaces

A seeded, grown persona earns its keep when work adopts it. A persona names which of these
surfaces load it in its `flow:` frontmatter, and its `use-when:`/`not-when:` lines tell a selector
when to pick it over a sibling. Three surfaces apply a persona, and all
three treat it the same way — as **advice**, never authority:

- **UDD (design).** At the design-definition loop a persona frames the requirements lens: which
  rules and metrics a UI/UX slice must satisfy for this project's users.
- **advisor / streams (delegation).** When you delegate a piece of your plan to a subagent, its
  `<persona>` block **selects** the best-fit `.add/personas/<slug>.md` and the returned verdict
  **records** which persona did the work. The independent earned-green refute-read selects a
  **Code-Reviewer** persona whose findings carry severity markers — 🔴 blocker · 🟡 concern · 💭 note.
  The same canonical persona body rides every runner (Claude, Cursor, Copilot, Codex), so a
  **cross-runner subagent** behaves identically wherever it is spawned.
- **build (overlay).** While building, the orchestrating agent may load the active persona as a
  domain identity **overlay** layered on `SOUL.md`: SOUL is the voice and trust rules; the persona is
  the domain stance. The overlay **never rewrites** SOUL.md (it is human-owned) and never overrides a
  trust rule. Convention: load Identity + Critical Rules + Anti-patterns as the overlay; pull the
  Playbook in only at the work moment it scaffolds.

## The non-negotiable — a persona never lowers a gate

A persona changes *how carefully* the work is done; it never changes *what passes*. This is the one
hard rule across every surface:

- A **security** finding is always a **HARD-STOP**, whatever persona was adopted.
- High-risk scope still escalates to the human; a stronger persona never buys back a gate.
- The engine stays **NO-EXEC** throughout: it never spawns a subagent, never runs a persona, never
  reads one on the build path. Selecting, loading, and applying a persona is the orchestrating
  agent's judgment — the engine only records what was used (for the audit trail) and measures that
  the record is present; it never auto-passes on a persona's say-so.

In short: a persona makes the agent *fit the project*. Direction, freezing, evidence, and the gate
are exactly as strict as they were before — the loop adds expertise, not permission.

---

[← 17 Components](./17-components.md) · [Contents](./README.md) · Next: [Appendix A Templates →](./appendix-a-templates.md)
