# Seeding a persona from an existing source

Authoring from a blank page is the slowest path and the one most likely to miss the judgment
layer. When a near-fit source exists, **seed from it, then distil** — never copy it wholesale. Two
sources are always worth checking first, in this order:

1. **The teacher library** — `.add/personas-teacher/**/*.md`, grouped by division folder
   (`design/`, `sales/`, `paid-media/`, …). A vetted, domain-organised corpus. Prefer this.
2. **A sample subagent** — a `~/.claude/agents/*.md` file (e.g. `senior-rust-engineer.md`) when the
   teacher library has no near-fit for a technical domain.

A source is a **head-start on structure**, not a finished lens. The mechanical parts map straight
across; the judgment parts you must *distil* (compress a verbose body into a few sharp clauses);
and a few parts the source will **never** carry — you add those yourself. That last column is the
whole point: a seed that skips it is just a reformatted résumé.

## Teacher file → ADD persona

A teacher file: frontmatter `name · vibe · description · color · emoji`, division from its folder,
and a verbose motivational body (`## 🧠 Identity & Memory`, `## 🎯 Core Mission`, …).

| ADD schema | Seed from the teacher | Action |
|---|---|---|
| `name:` | frontmatter `name` | carry across |
| `vibe:` | frontmatter `vibe` | carry across (tighten to one line) |
| `flow:` | the division folder — `design/` → `design`; a review/audit persona → `verify`/`advisor` | **infer, then confirm** against the closed values |
| `task-kinds:` | the domain (a `design/` lens → `ui`; a data persona → `data`) | **you pick** from the closed taxonomy |
| `use-when:` / `not-when:` | frontmatter `description` seeds `use-when`; the sibling it's most confused with seeds `not-when` | distil + **add `not-when`** (the source has none) |
| `## Identity` | the body's identity/experience paragraph ("You've seen developers struggle with…") | **distil to earned perspective** — scars, not the résumé |
| `## Critical Rules` | any `**Default requirement**:` / non-negotiable lines in the body | distil to bold-lead rules; **add** the two default stances (surface-tradeoffs · qualification-gate) |
| `## Default Requirement` | the one `Default requirement:` line if present | carry or write |
| `## Success Metrics` | *(the teacher rarely has measurable metrics)* | **ADD — this is the judgment.** MEASURABLE invariants, each sharpened by the failure it guards |
| `## Abilities` | the `Core Mission` bullets | distil to concrete, anchored, checkable actions; lead with the ORIENT commands |
| `## Anti-patterns` | the instincts implied by the "you've seen X fail" lines | name them guilty-until-proven; **always add** read-before-you-assert |

## Subagent md (`~/.claude/agents/*.md`) → ADD persona

A subagent file: frontmatter `name · description · model · color`, the `description` embeds a
`Use when: …` clause and `<example>` blocks, and the body leads with `## Core Principles
(Non-Negotiable)`.

| ADD schema | Seed from the subagent | Action |
|---|---|---|
| `name:` / `vibe:` | frontmatter `name`; **vibe has no source** | carry name; **write a one-line vibe** |
| `flow:` / `task-kinds:` | the `<example>` Contexts name the work (review → `verify`; build → `build`) | infer flow + kinds, confirm against the closed sets |
| `use-when:` / `not-when:` | the `Use when: …` clause in `description`; each `<commentary>` names a core capability | carry `use-when`; **add `not-when`** |
| `## Identity` | the opening `You are a **…**` paragraph | distil to earned perspective |
| `## Critical Rules` | the `## Core Principles (Non-Negotiable)` list | distil to bold-lead rules (keep 1–2 signatures); **add** the two default stances |
| `## Abilities` | the capabilities in the `<commentary>` tags + the body's numbered principles | make each doable *now*, anchored to a file/tool/command; an I/O lens **adds** design-for-failure |
| `## Success Metrics` | *(subagents state principles, not measurable bars)* | **ADD — measurable, failure-aware invariants** |
| `## Anti-patterns` | the "only when genuinely required" / "avoid" hedges | name them guilty-until-proven; **always add** read-before-you-assert |

## What to mine, what to refuse

Both source families carry gold the mapping tables can't express — and a signature rot that must
not survive the seed:

- **Teacher gold** — the one-line `Default requirement:` floor · the "You've seen…" scar sentence
  (feeds Identity) · behaviour-paired metric rows ("100% warm transfers — never a cold handoff")
  · a named methodology with its verbatim moves and why-they-work (feeds a Playbook) · the rare
  "when NOT to use" lines (feed `not-when:` as *symptom → sibling*) · a reviewer's default-verdict
  stance with automatic-fail triggers (feeds a verify-flow stance).
- **Teacher rot — refuse** — deliverable code dumps (CSS/config skeletons), emoji-header chrome,
  invented outcome statistics ("+40% engagement" no one measured), motivational closers and
  "instructions reference" footers that point at nothing.
- **Subagent gold** — review-mode checklists (feed the verify side of a per-flow stance) ·
  pitfalls with the cost attached ("PIL in prod preprocessing → 3× slower than cv2" — feeds
  Anti-patterns) · budgets the author would defend ("p95 < 200 ms", "44×44 px" — feed
  Rules/Metrics) · mode bookends ("reviewing opens with the defect sweep").
- **Subagent rot — refuse** — keyword-taxonomy pages (nouns buy no behaviour), tip bribes and
  self-score rubrics, tutorial code blocks, and another project's hard-coded paths — a persona
  anchors to THIS project's real files only.

## After the seed

Record provenance honestly: add a `source:` frontmatter line naming the seed — the teacher slug,
or `agents/<file>` — (the contract lists `source` as an optional field). Then run the **Workflow** in `SKILL.md` over the
seeded draft — every section still faces its judgment bar — and `add.py check` until green. A seed
that never had the Success-Metrics and Anti-patterns columns filled is not done.
