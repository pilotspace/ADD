# Experience — the UDD spec

project: AIDD / ADD Methodology · seeded: 2026-07-17 · stage: mvp

> Living document — how it feels to use: flows, surfaces, the humans served (UDD).
> Keep the sections below CURRENT (state, not history); lessons land under
> Deltas the moment they are learned: `add.py delta-append udd "<lesson>"`.
> A delta that changes the standing picture is folded UP into the sections
> above it and marked `[folded]` — the Deltas list is the inbox, not the spec.

## Now
<!-- migrated from PROJECT.md §Users @ fv66 (foundation-split) -->
- No-UI project: ADD ships as a CLI + a Claude skill — the "interface" is the `add.py` /
  `npx @pilotspace/add` command surface and the text it prints. Core flow: `init` → fill
  foundation → `new-task` → run the loop → gate → resume any session with `status`.
- Primary users & jobs: the author shipping ADD as a product; **AI agents** that load the
  skill; **developers** adopting ADD who must read/trust/follow the method.
- What "good" feels like: never lose context across sessions; less doc time than GSD; one
  command to know "where am I and what's next". Design source of truth: the skill prose
  (`SKILL.md` + `phases/*`) and the book.
- OPEN forward gaps (fv29 · udd-design-foundation, still live): (a) DTCG `$type`-inheritance —
  the `got ∉ _TOKEN_TYPES` skip-guard is the settled boundary, never re-flag upstream concerns;
  (b) compact-dialect value-form strictness under-pinned in three spots (`fontWeight` any
  string · weight floats rejected · negative dimensions pass) — tighten when real token files
  hit them; (c) `GOAL_UNSET` sentinel text slightly stale ("add a goal: line" → should say
  "fill in the goal: value"); (d) `_section0_anchors` reads only INLINE Anchors content, not a
  bulleted list — teach the parser or make inline-only explicit.
- Known gap (fv21, still live): the dogfood book copy `.add/docs/` is gitignored and outside
  `test_bundle_parity` — accepted as a known-throwaway install artifact, not silently trusted.

## Decisions that bind
- "UI states" for a CLI = output states: a clear success line, an empty/idle state, and actionable errors with named exit codes — never a bare trace. [pre-fv21]
- TUI rendering house rule (stdlib-only, no `wcwidth`/`rich`): richness on width-neutral channels (color on tty only, honoring `NO_COLOR`/`TERM`); only ASCII-safe text in `len()`-aligned columns; Unicode glyphs at line-END or non-aligned row starts; persisted render is PLAIN + fixed-width, color/adaptive-width a tty-only skin. [v9 · UDD]
- Two render idioms chosen by PURPOSE: a ROLLUP (`report <m>`) collapses prose into `len()`-aligned columns; a DRILL (`report <task>`) preserves physical lines + indent, soft-wraps, never clips — the shared frozen thing is the DATA seam, not the layout. [v9-1 · UDD]
- A design feature opens with the four-axis intake (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) BEFORE the domain read — the look is directed, not guessed. [fv53 · design-intake-beat]
- Setup SUGGESTS, never interrogates: propose the first milestone + run-mode as show-before-ask, not a questionnaire. [fv32 · setup-run-mode]
- One next step at the most-lost moment: when the user is most lost, status shows exactly ONE next move — competing hints dilute the only correct action. [v12-1]
- A review prompt lives AT the seam, sized to real attention (one minute · six lines · ⚠-first) — a separate review artifact competes with the decision instead of aiming it. [v14]
- Precise promises beat catchy absolutes: name the exact honest boundary, never a slogan the product can't literally keep. [v15]
- Leanness is a UX constraint on a dual-audience prose file (agent + human): markup vocabulary sized for readability — block-level tags only, skeleton labels stay plain text. [v16]
- The goal-gate prevents theater only if the human writes REAL checkable exit-criteria — the engine reads the tally, the human earns the boxes. [v20]
- Identity values are human-owned: design tokens (brand color, palette, type) surface AT specify for the human to fill; the AI never auto-picks — DESIGN.md identity ships as prompts, never pre-filled values (`identity_prefilled` guard). [fv29 · udd-design-foundation]
- The ubiquitous-language ban is PROSE-ONLY: a banned term survives inside a `code span` or fenced block — guides reference machine names as code-spans and use domain terms in prose. [fv31 · foundation-compaction]

## Deltas (newest first)
<!-- prepended by `add.py delta-append udd "<text>"` — one line per lesson, `- [open · <date>] <lesson>` + the active-task stamp; fold a delta upward, then retag [open]->[folded] -->
