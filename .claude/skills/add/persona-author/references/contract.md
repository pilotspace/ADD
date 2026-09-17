# The ADD persona contract

The engine validates node schema, not authoring quality. Missing frontmatter/type draws
`missing_frontmatter`/`type_empty`; an invalid declared `flow` or `task-kinds` draws
`persona_routing_key`. Optional routing may be absent. Body quality stays author-reviewed;
`references/patterns.md` is the judgment that fills the schema well.

## The four legs

A persona carries four kinds of judgment. The headings below guide a human or agent reading the
body; engine routing reads only frontmatter and does not match or validate these headings.

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
- Avoid `_`-prefixed slugs: they look like scaffolds, but the engine currently includes them in
  its Persona roster and routing checks.

## Frontmatter

```yaml
---
type: Persona
title: <persona title — e.g. Payments API Engineer>
vibe: <one-line essence — what this persona keeps true>  # OPTIONAL authored slot
flow: <design | build | advisor | verify>                # OPTIONAL authored slot; comma-separate if >1
task-kinds: <from the closed taxonomy, comma-separated>  # OPTIONAL authored slot
use-when: <pushy should-select line — enumerate triggers> # OPTIONAL authored slot
not-when: <the near-miss that belongs to a named sibling> # OPTIONAL authored slot
description: <one line for a cold catalogue reader>      # OPTIONAL authored slot; OKF-recommended
sources: <teacher file(s) distilled from>                # OPTIONAL authored slot; OKF provenance family
---
```

- **`type` · `title`** — the Persona node keys written by `add new Persona`; `type` is exactly
  `Persona`, and `title` is the display name. Teaching templates use authoring inputs `name:` and
  singular `source:`; conversion maps them to node `title:` and `sources:` respectively.
- **The seven authored slots** — `vibe`, `flow`, `task-kinds`, `use-when`, `not-when`,
  `description`, and `sources` — are scaffolded with prompts, but their authored values are
  optional and `new` does not validate their content. Fill or delete each prompt before use.
- **`flow`** — the beats this lens loads at. The ONLY valid values are
  `design` · `build` · `advisor` · `verify` (single-sourced in the skill's `personas.md`).
  The engine reads `flow` and `task-kinds` for routing; `doctor` reports invalid values
  with the allowed sets. Surfaces: **design** = the Direction-beat authoring lens (RULES ·
  ASSUMPTIONS · `gives:` before the freeze) · **build** = the working lens the brief injects
  (`<persona ref=… inject="frontmatter">`) · **advisor** = the delegation lens `advise` and
  `wave` record on a beat · **verify** = the evidence-judging lens on the gate report.
- **`task-kinds`** — the persona's ROUTING KEY, from the closed taxonomy:
  `feature · refactor · test · docs · ui · security · data · infra · release · integration ·
  explore`.
  It says which kinds of task should reach for this lens; a value outside the taxonomy
  routes nothing — and `doctor` now says so, at `info`, naming the value and the allowed set
  (`PERSONA_TASK_KINDS` in the engine is the single source both this list and the check read).
- **`use-when` / `not-when`** — the selection boundary. Selectors under-trigger on essence lines,
  so `use-when` ENUMERATES the concrete contexts that should pick THIS persona; `not-when` names
  the sibling that owns the near-miss (e.g. `CI permissions → security-gatekeeper`).
- **`description` / `sources`** — the two OKF keys (Open Knowledge Format v0.2, whose trust
  layer — `type:`, `generated:`, `verified:` events, `human:<id>` actors — ADD's node format
  already speaks). `description` is one line for a cold catalogue reader; `sources` records the
  teacher file(s) or material this lens was distilled from — provenance, not routing.
  `add new Persona` scaffolds these slots; routing values are checked by `doctor`.

## Sections

**AUTHORING REQUIRED (reviewed by the author, not enforced by the engine):**

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

`init` seeds every shipped starting-persona template into `.add/personas/`, never overwrites
an existing project persona, and reports the names it newly seeded. These are starting lenses:
inspect and adapt them to the project before relying on their judgment. Additional lenses can
be scaffolded with `add new Persona <slug>` or distilled using `references/seeding.md`.
The separately vendored teacher corpus and routing index are reference material, not Persona nodes.

- **Never clobber.** Existing project personas outrank templates on re-init. `doctor --sync`
  recompiles the index; it does not replace authored persona judgment.
- **Prove fit, not index presence.** Check the lens's `flow`, `task-kinds`, and selection
  boundary against the task. `doctor --sync` repairs the orientation catalogue; routing reads
  Persona nodes directly.

## The author's own final sweep

`doctor` reports structural and routing-vocabulary findings; the author still judges fitness.

- **flow typo** — resolve the reported value against `design · build · advisor · verify`.
- **bare placeholder** — a `<…>` token left outside backtick spans and HTML comments (a half-filled
  copy). Backticked (`` `<slug>` ``) and commented (`<!-- <x> -->`) angle brackets are content, not
  placeholders. Sweep every real `<…>` before you finish.

Valid scalar or YAML-list routing terms clear doctor routing findings; the author still sweeps
bare placeholders. `python3 .add/tooling/cli.py doctor --sync` then lists the lens in `.add/index.md`.
