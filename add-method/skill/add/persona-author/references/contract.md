# The ADD persona contract

What the ADD engine reads and validates. Miss the required parts and the persona fails
`add.py check`; miss the recommended frontmatter and no apply-surface loads it. This is the
hard schema — `references/patterns.md` is the judgment that fills it well.

## File

- Path: `.add/personas/<slug>.md` — `<slug>` is kebab-case (e.g. `payments-api-engineer`).
- **Never overwrite** an existing persona file; author a new slug or fold into the named one.
- **Never** name a persona `_`-prefixed — the engine treats `_`-prefixed files as scaffolds and
  skips them (they are excluded from the roster, emptiness checks, and quality WARNs).

## Frontmatter

```yaml
---
name: <persona name — e.g. Payments API Engineer>      # REQUIRED
vibe: <one-line essence — what this persona keeps true>  # REQUIRED
flow: <design | build | advisor | verify>                # RECOMMENDED — comma-separate if >1
task-kinds: <from the closed taxonomy, comma-separated>  # RECOMMENDED
use-when: <pushy should-select line — enumerate triggers> # RECOMMENDED
not-when: <the near-miss that belongs to a named sibling> # RECOMMENDED
folded: <consolidation history, newest first>            # OPTIONAL
source: <teacher file(s) distilled from>                 # OPTIONAL
---
```

- **`name` · `vibe`** — REQUIRED. Absence fails the schema check.
- **`flow`** — the apply-surfaces this lens loads at. The ONLY valid values are
  `design` · `build` · `advisor` · `verify` (single-sourced as `constants.PERSONA_FLOW_VALUES`).
  Any other value is a typo that no surface loads — `add.py check` emits a `persona_quality` WARN
  naming it. Surfaces: **design** = the UDD requirements lens · **build** = the domain-identity
  overlay on SOUL.md · **advisor** = the subagent/streams delegation lens · **verify** = the
  evidence-judging lens (earned-green refute-read + gate record).
- **`task-kinds`** — the persona's SCOREBOARD KEY, from the closed taxonomy:
  `feature · refactor · test · docs · ui · security · data · infra · release · integration`.
  Route-outcome traces join a task's `kind:` header to this claim, so performance is measurable
  per kind. A value outside the taxonomy scores as nothing.
- **`use-when` / `not-when`** — the selection boundary. Selectors under-trigger on essence lines,
  so `use-when` ENUMERATES the concrete contexts that should pick THIS persona; `not-when` names
  the sibling that owns the near-miss (e.g. `CI permissions → security-gatekeeper`).

## Sections

**REQUIRED (engine-checked, presence-based):**

- `## Identity`
- `## Critical Rules`
- `## Default Requirement`
- `## Success Metrics`

**RECOMMENDED (a surface can't fully use the lens without them):**

- `## Abilities`

**OPTIONAL (absence is conformant):**

- `## Anti-patterns`
- `## Playbook`

## Quality WARNs `add.py check` surfaces (non-blocking, measure-not-block)

- **flow typo** — a `flow:` value outside the four is named in the finding (loaded by no surface).
- **bare placeholder** — a `<…>` token left outside backtick spans and HTML comments (a half-filled
  copy). Backticked (`` `<slug>` ``) and commented (`<!-- <x> -->`) angle brackets are content, not
  placeholders. Sweep every real `<…>` before you finish.

These are WARNs, never failures — but a roster-ready persona clears all of them.
