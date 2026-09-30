# 10 · Personas — expert lenses

[← 09 Governance — verdicts, floors, review after](./09-governance.md) · [Contents](./README.md) · Next: [11 Adoption →](./11-adoption.md)

---

## The team is a set of lenses, not a set of chairs

Older methods model a team as an org chart: a product owner here, an architect there. ADD keeps the *judgment* those titles carried and drops the chart. The unit is a **persona** — a small file of distilled expertise the agent loads before a beat, so its work meets *this* project's standards instead of a generic default.

An agent does not sit in a chair. The same agent can work behind a payments engineer's caution on one task and a UI designer's contrast rules on the next. What a persona preserves is *what judgment gets applied*: the rules a domain refuses to wave through, the smells it suspects, the done-bar it measures against. Tone and the shape of the deliverable are the agent's own; a persona that duplicates them is dead weight.

Personas are optional. A project with none runs the loop exactly the same.

## What a persona file holds

`.add/personas/<name>.md`, markdown with frontmatter:

```markdown
---
type: Persona
title: Security Reviewer
flow: verify, advisor                  # the beats it serves
task-kinds: security, test, infra
use-when: any change to who may do what and on what evidence
not-when: work with no authorization surface → build-craftsman
---
## Identity
## Critical Rules
## Default Requirement
## Success Metrics
```

- **Identity** — the stance, with earned scars (*a reviewer who has watched a control fail because it read the wrong field*).
- **Critical Rules** — the non-negotiables, each with its *why*.
- **Default Requirement** — the one thing it adds to every deliverable.
- **Success Metrics** — the measurable done-bar.

## Where personas come from

- **Starter personas.** The installer seeds nine into `.add/personas/` — `task-planner`, `milestone-planner`, `release-planner`, `build-craftsman`, `security-reviewer`, `data-steward`, `interface-designer`, `docs-writer`, `explore-investigator`. They are yours from the moment they land: edit, replace or delete them. A re-install never overwrites one.
- **The teacher corpus.** `.add/personas-teacher/` holds a vendored library of worked agent definitions across many domains, routed by `.add/personas-index/use-when.md`. It is source material, read while authoring — never loaded at run time.
- **The `persona-author` skill.** To write a new lens or sharpen one, use the `persona-author` sub-skill that ships with `add`. It distills the nearest teacher entry into the four parts above rather than starting from a blank page.

## Apply — load the one that fits

Before Direction or Verify, the agent reads the `use-when:` and `not-when:` lines and loads the persona that fits the task; none fits, it proceeds without one. The lens shapes *how carefully* the beat is done: which surfaces the assumption sweep presses on, which residue it reads hardest, which refute probes it tries.

▶ For the transfer task, `security-reviewer` fits at Verify: the ownership check on the source account is an authorization boundary, so the residue read starts there.

## Grow — lenses sharpen with use

Personas improve the way the specs do. When a task teaches something about a domain's judgment — a rule that caught a real defect, one that never fired — the agent records a delta with evidence in `.add/specs/method.md`, and the persona file is edited to match. Two habits keep growth honest: run a representative task with and without the lens and compare, and prune any rule that never fired in a milestone.

## The non-negotiable — a persona never lowers a rule

A persona is expertise, not permission.

- A **security** finding is a `HARD-STOP` whatever lens was loaded.
- The floor still holds: security, data and architecture work is at least a Task, whoever is looking.
- A persona never edits a sealed check, never moves a `gives:` surface, never writes a verdict the evidence does not support.

---

> **Do:** keep a small set of lenses that carry your project's hard-won judgment, and load them where they fit.
> **Don't:** treat a persona as a title with authority. The loop is exactly as strict with a lens as without one.
