# The ADD persona contract

What the ADD engine reads and validates. Miss the required parts and the node draws `add doctor`
findings (`missing_frontmatter`, `type_empty`); miss the recommended frontmatter and no
apply-surface loads it — SILENTLY, because the engine is a notary and does not lint routing
fields. This is the hard schema — `references/patterns.md` is the judgment that fills it well.

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
description: <one line for a cold catalogue reader>      # OPTIONAL — OKF-recommended
folded: <consolidation history, newest first>            # OPTIONAL
sources: <teacher file(s) distilled from>                # OPTIONAL — OKF provenance family
---
```

- **`name` · `vibe`** — REQUIRED. The engine will not refuse their absence (it is a notary,
  not a linter) — but every surface that renders the roster prints them, so a missing `vibe`
  is a blank line where your lens's one-sentence essence should be.
- **`flow`** — the beats this lens loads at. The ONLY valid values are
  `design` · `build` · `advisor` · `verify` (single-sourced in the skill's `personas.md`).
  Any other value is a typo that no surface loads — and NOTHING warns: the engine reads only
  `use-when:` for the roster, so a `flow:` typo fails silently. Check the four values yourself
  before finishing. Surfaces: **design** = the Direction-beat authoring lens (RULES ·
  ASSUMPTIONS · `gives:` before the freeze) · **build** = the working lens the brief injects
  (`<persona ref=… inject="frontmatter">`) · **advisor** = the delegation lens `advise` and
  `wave` record on a beat · **verify** = the evidence-judging lens on the gate report.
- **`task-kinds`** — the persona's ROUTING KEY, from the closed taxonomy:
  `feature · refactor · test · docs · ui · security · data · infra · release · integration`.
  It says which kinds of task should reach for this lens; a value outside the taxonomy
  routes nothing.
- **`use-when` / `not-when`** — the selection boundary. Selectors under-trigger on essence lines,
  so `use-when` ENUMERATES the concrete contexts that should pick THIS persona; `not-when` names
  the sibling that owns the near-miss (e.g. `CI permissions → security-gatekeeper`).
- **`description` / `sources`** — the two OKF keys (Open Knowledge Format v0.2, whose trust
  layer — `type:`, `generated:`, `verified:` events, `human:<id>` actors — ADD's node format
  already speaks). `description` is one line for a cold catalogue reader; `sources` records the
  teacher file(s) or material this lens was distilled from — provenance, not routing.
  `add new Persona` scaffolds a slot for every key in this block; fill or delete each, because
  the engine validates none of them.

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

3.0 seeds **no personas**. What `init` vendors is the read-only teacher corpus
(`personas-teacher/`, 232 reference lenses, byte-verbatim third-party snapshot) and its
generated routing sidecar (`personas-index/use-when.md`). Every Persona NODE on your
roster is yours to author — scaffolded with `add new Persona <slug>`, or distilled from a
teacher file by the seeding flow in `references/seeding.md`. The corpus is referenced,
never copied into your roster: a teacher file teaches; a Persona node routes and advises.

The line governing what this project would ever ship as a preset, and why it is drawn
here rather than left to taste:

> **Ship a persona only if it is a METHOD LENS** — one that reasons about ADD's own
> artifacts: a Task's RULES and CHECKS, the frozen `gives:` contract and its seal, the
> milestone graph, the gate report. **Never ship a DOMAIN lens** — one that reasons about
> a project's subject matter: security, data, UX, a framework, an industry.

A method lens is correct in every project by construction: every ADD bundle has the same
node grammar, the same freeze seal, the same gate. A domain lens asserts what *your*
project's judgment should be, and no author who has not read your code can do that.

This is a scar, not a style preference. Twelve preset personas (`security-gatekeeper`,
`data-steward`, `ux-experience-lead`, and nine more) shipped in every npm tarball and pip
wheel for months while **nothing loaded them** — authoritative-looking and dead. They were
retired at `preset-patterns-fold`. Eleven of the twelve fail the criterion above; the
honest near-miss is `release-manager`, which would have passed. The line is narrow, not
comfortable — and it is why 3.0 ships a corpus to READ and an empty roster to AUTHOR
rather than presets to trust.

Two obligations survive the 2.x seeding machinery they were learned on:

- **Never clobber.** `init` is idempotent — an existing file always outranks a template
  (R:CLOBBER), and `doctor --sync` is the only asked-for refresh. Nothing ever rewrites
  your authored judgment.
- **Prove the load, not the presence.** A roster persona must appear in the compiled
  `index.md` roster with its `use-when:` line (that is what `doctor --sync` renders from
  frontmatter). A presence-only check is exactly what let the dead presets pass a green
  suite, so prove the rendered line, never the file.

## The author's own final sweep (the engine does NOT check these)

The 3.0 engine is a notary: `add doctor` reports structural findings only. The two classic
half-finished-persona defects fail silently, so they are YOUR checklist, not a WARN to wait for:

- **flow typo** — a `flow:` value outside the four is loaded by no surface. Re-read it against
  `design · build · advisor · verify` verbatim.
- **bare placeholder** — a `<…>` token left outside backtick spans and HTML comments (a half-filled
  copy). Backticked (`` `<slug>` ``) and commented (`<!-- <x> -->`) angle brackets are content, not
  placeholders. Sweep every real `<…>` before you finish.

A roster-ready persona clears both, and its line appears in `.add/index.md` after
`cli.py doctor --sync`.
