# The ADD persona contract

Nothing validates a persona but its author. The ADD skill reads a persona's frontmatter to pick
the lens that fits a beat, then reads its body as judgment. This file is the shape both need;
`references/patterns.md` is the judgment that fills the shape well.

## The four legs

A persona carries four kinds of judgment. The headings below guide a human or agent reading the
body; selection reads only frontmatter.

| Leg | Lives in | The bar it must clear |
|-----|----------|-----------------------|
| **Role** | `## Identity` | States what this lens has SEEN succeed or fail — a scar, not a résumé. A reader can point to the experience that made the Anti-patterns below inevitable. |
| **Rules** | `## Critical Rules` | Every line is something the lens would REFUSE to wave through, bold clause first. A rule nothing could violate is prose wearing a rule's clothes. |
| **Standards** | `## Default Requirement` + `## Success Metrics` | One requirement present in every deliverable, then metrics stated as INVARIANTS — each naming the failure mode it catches, each checkable IN-SESSION by the agent holding the lens. |
| **Process** | `## Abilities` + `## Playbook` | Abilities open with the ORIENT reads and commands the lens runs on load, and every entry is doable NOW against a real file, tool, or command. The Playbook, when present, carries ordered moves with provenance tags — never a tutorial. |

Process is the leg authors most often leave thin, and it is the one with the sharpest cost: a lens
that knows what "good" looks like but not what to READ or RUN first will re-derive ground truth it
could have had in one step. If you write only one Process line, make it the ORIENT line.

## File

- Path: `.add/personas/<slug>.md` — `<slug>` is kebab-case (e.g. `payments-api-engineer`).
- **Never overwrite** an existing persona file; author a new slug or fold into the named one.
- Avoid `_`-prefixed slugs: they read as scaffolds.

## Frontmatter

```yaml
---
type: Persona
title: <persona title — e.g. Payments API Engineer>
vibe: <one-line essence — what this persona keeps true>  # optional
flow: <design | build | advisor | verify>                # comma-separate if >1
task-kinds: <from the closed taxonomy, comma-separated>
use-when: <pushy should-select line — enumerate triggers>
not-when: <the near-miss that belongs to a named sibling>
description: <one line for a cold catalogue reader>      # optional
sources: <teacher file(s) distilled from>                # optional provenance
---
```

- **`type` · `title`** — `type` is exactly `Persona`; `title` is the display name. A seed that
  arrives with `name:` and singular `source:` converts them to `title:` and `sources:`.
- **`flow`** — the beats this lens loads at. The ONLY valid values are
  `design` · `build` · `advisor` · `verify`. **design** = the Direction lens (RULES · ASSUMPTIONS ·
  `gives:` before the freeze) · **build** = the working lens during Build · **advisor** = the
  planning lens for sizing, milestones and trade-offs · **verify** = the evidence-judging lens at
  Verify. A value outside the four is never selected.
- **`task-kinds`** — the persona's routing key, from the closed taxonomy:
  `feature · fix · refactor · test · docs · ui · security · data · infra · release · integration ·
  explore`. It says which kinds of task should reach for this lens; a value outside the taxonomy
  routes nothing.
- **`use-when` / `not-when`** — the selection boundary. Selectors under-trigger on essence lines,
  so `use-when` ENUMERATES the concrete contexts that should pick THIS persona; `not-when` names
  the sibling that owns the near-miss (e.g. `CI permissions → security-reviewer`).
- **`description` / `sources`** — `description` is one line for a cold catalogue reader;
  `sources` records the teacher file(s) or material this lens was distilled from — provenance,
  not routing.

## Sections

**REQUIRED (reviewed by the author):**

- `## Identity`
- `## Critical Rules`
- `## Default Requirement`
- `## Success Metrics`

**RECOMMENDED (a beat can't fully use the lens without them):**

- `## Abilities` — the first half of the Process leg. The agent that loads this lens runs its
  lead reads and commands before drafting. Abilities is what turns "become this lens" into "run
  these first", so it is where ORIENT-first (`patterns.md` #6) and design-for-failure (#7) land —
  a persona that omits it starts every beat blind.

**OPTIONAL (absence is fine):**

- `## Anti-patterns`
- `## Playbook`
- `## Escalation` — the stop-condition: what makes THIS lens refuse to proceed rather than proceed
  carefully. Distinct from a Critical Rule (an always-do the build must satisfy) and from an
  Anti-pattern (a smell the lens treats as guilty until proven innocent): an Escalation names the
  point where the lens returns a HARD-STOP or hands the decision to a named sibling. Write one for
  any persona that judges Verify; omit it for a lens that only advises. Never restate the
  universal floor here — a security finding is always a HARD-STOP verdict whatever persona is
  loaded; this section is for the stop-conditions specific to the domain. See `patterns.md` #11.
  A lesson filed in `.add/specs/` that names this persona can be folded into this section by hand.

## What ADD ships vs what you author

The installer seeds the shipped starter personas into `.add/personas/` and never overwrites an
existing file. These are starting lenses: inspect and adapt them to the project before relying on
their judgment. Author more by hand from the frontmatter above, or distil one from the vendored
teacher corpus (`.add/personas-teacher/`, routed by `.add/personas-index/use-when.md`) using
`references/seeding.md`. The corpus is reference material, not personas.

- **Never clobber.** Existing project personas outrank starter templates on re-install.
- **Prove fit.** Check the lens's `flow`, `task-kinds`, and selection boundary against the task.

## The author's own final sweep

Nothing lints a persona, so the author checks:

- **flow values** — each one of `design · build · advisor · verify`.
- **task-kinds values** — each one from the taxonomy above.
- **bare placeholder** — a `<…>` token left outside backtick spans and HTML comments (a half-filled
  copy). Backticked (`` `<slug>` ``) and commented (`<!-- <x> -->`) angle brackets are content, not
  placeholders. Sweep every real `<…>` before you finish.
