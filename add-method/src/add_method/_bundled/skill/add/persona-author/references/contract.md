# The ADD persona contract

What the ADD engine reads and validates. Miss the required parts and the persona fails
`add.py check`; miss the recommended frontmatter and no apply-surface loads it. This is the
hard schema — `references/patterns.md` is the judgment that fills it well.

## The four legs

A persona carries four kinds of judgment. The section names below are what the engine and every
apply-surface match **literally** — the legs are how you *read* the schema, never a rename of it.

| Leg | Lives in | The bar it must clear |
|-----|----------|-----------------------|
| **Role** | `## Identity` | States what this lens has SEEN succeed or fail — a scar, not a résumé. A reader can point to the experience that made the Anti-patterns below inevitable. |
| **Rules** | `## Critical Rules` | Every line is something the lens would REFUSE to wave through, bold clause first. A rule nothing could violate is prose wearing a rule's clothes. |
| **Standards** | `## Default Requirement` + `## Success Metrics` | One requirement present in every deliverable, then metrics stated as INVARIANTS — each naming the failure mode it catches, each checkable IN-SESSION by the agent holding the lens. |
| **Process** | `## Abilities` + `## Playbook` | Abilities open with the ORIENT commands the lens runs on load, and every entry is doable NOW against a real file, tool, or command. The Playbook, when present, carries ordered moves with provenance tags — never a tutorial. |

Process is the leg authors most often leave thin, and it is the one with the sharpest cost: a lens
that knows what "good" looks like but not what to RUN first will re-derive ground truth it could
have read in one command. If you write only one Process line, make it the ORIENT command.

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

- `## Abilities` — the first half of the Process leg. **Loaded by:** the roster agent reads the
  body of the persona it becomes and runs that persona's lead commands before drafting
  (`.claude/agents/add-worker.md` §2). Abilities is what turns "become this lens" into "run these
  commands first", so it is where ORIENT-first (`patterns.md` #6) and design-for-failure (#7) land
  — a persona that omits it starts every beat blind.

**OPTIONAL (absence is conformant):**

- `## Anti-patterns`
- `## Playbook`
- `## Escalation` — the stop-condition: what makes THIS lens refuse to proceed rather than proceed
  carefully. Distinct from a Critical Rule (an always-do the build must satisfy) and from an
  Anti-pattern (a smell the lens treats as guilty until proven innocent): an Escalation names the
  point where the lens hands the decision to a human or to a named sibling. Write one for any
  persona that owns a gate report; omit it for a lens that only advises. Never restate the
  universal floor here — a security finding is always HARD-STOP whatever persona is loaded; this
  section is for the stop-conditions specific to the domain. See `patterns.md` #11.
  **Routable:** a retrospective can file `- [ADD · open · persona:<slug> · escalation] …` and the
  fold transcribes it into this section. The gate is the CLOSED hint vocabulary documented in
  `deltas.md` (`critical-rule|success-metric|anti-pattern|ability|escalation`) — not the engine:
  `add.py` never edits a persona, so the fold is the human's or the AI's transcription, and a
  section that no hint names cannot be grown this way.

## What ADD ships vs what you author

ADD seeds exactly three personas into `.add/personas/` at `init` and `migrate` —
`task-planner`, `milestone-planner`, `release-planner` (`constants.METHOD_PERSONAS`).
Everything else on your roster is yours to author.

The line between them, and why it is drawn here rather than left to taste:

> **Ship a persona only if it is a METHOD LENS** — one that reasons about ADD's own
> artifacts: PLAN.md sections, the frozen §3 contract, the milestone DAG, the release
> cut. **Never ship a DOMAIN lens** — one that reasons about a project's subject matter:
> security, data, UX, a framework, an industry.

A method lens is correct in every project by construction: every ADD project has the same
contract, the same DAG, the same gate. A domain lens asserts what *your* project's
judgment should be, and no author who has not read your code can do that.

This is a scar, not a style preference. Twelve preset personas (`security-gatekeeper`,
`data-steward`, `ux-experience-lead`, and nine more) shipped in every npm tarball and pip
wheel for months while **nothing loaded them** — authoritative-looking and dead. They were
retired at `preset-patterns-fold`. Eleven of the twelve fail the criterion above; the
honest near-miss is `release-manager`, which would have passed. The line is narrow, not
comfortable.

Two obligations come with seeding, both test-enforced:

- **Never clobber.** A seeded persona you have edited is returned untouched by any later
  `init` or `migrate` (`_seed_persona_file` mirrors the `_seed_spec_file` survivor idiom).
  Seeding fills gaps; it never rewrites your judgment.
- **Prove the load, not the presence.** A seeded persona must appear in the `status --all`
  roster as `slug [flow] — vibe`. A presence-only test is what let the presets pass a green
  suite while dead, so `test_seed_method_personas` asserts the rendered roster line.

Adding a slug to `METHOD_PERSONAS` without meeting the criterion re-opens that failure.

## Quality WARNs `add.py check` surfaces (non-blocking, measure-not-block)

- **flow typo** — a `flow:` value outside the four is named in the finding (loaded by no surface).
- **bare placeholder** — a `<…>` token left outside backtick spans and HTML comments (a half-filled
  copy). Backticked (`` `<slug>` ``) and commented (`<!-- <x> -->`) angle brackets are content, not
  placeholders. Sweep every real `<…>` before you finish.

These are WARNs, never failures — but a roster-ready persona clears all of them.
