# TASK: UDD design-intake beat (4-axis interview)

slug: design-intake-beat · created: 2026-06-26 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `add-method/skill/add/design.md` — the UDD loop guide (canonical). `## The loop — four beats` (review-domain → research-components → wireframe → render-capture-confirm) + `## The hard rules`. The new beat 0 `design-intake` is inserted here, before review-domain.
- `add-method/src/add_method/_bundled/skill/add/design.md` — pip/npm-bundle mirror of the same guide (byte-identical).
- `.claude/skills/add/design.md` — dogfood mirror (the repo's own installed skill; byte-identical). 3-tree mirror.
- `add-method/tooling/templates/DESIGN.md.tmpl` — the DESIGN.md scaffold (canonical). Has `## Identity` (brand color/palette/typeface/voice — human-owned) + `## Principles` (persona/principles/a11y) + `## Screens`. A place to capture the four axes goes here.
- `add-method/src/add_method/_bundled/tooling/templates/DESIGN.md.tmpl` + `.add/tooling/templates/DESIGN.md.tmpl` — the two template mirrors (byte-identical). 3-tree.
- `add-method/docs/14-foundation.md:50-59` — the book's four-beat description of the design-definition loop (add the intake beat to the narration).
- `add-method/docs/appendix-c-glossary.md:137-143` — the book glossary's design terms (wireframe · render-capture · design-confirm); add the four axis terms here.
- `add-method/skill/add/SKILL.md:126-127` — the one-line "design-definition loop (UDD)" pointer into design.md (3-tree; touch only if the beat list is restated).

Context (working folder):
- Existing test surfaces this change must keep green (or extend): `test_design_loop_guide.py` (design.md content + 3-tree parity), `test_udd_design_template.py` (DESIGN.md.tmpl content), `test_skill_lean.py` (design.md is in the lean fence — lines 55 & 84 — adding prose grows the tree → rebaseline the fence ratio, don't break it), `test_wording_lint.py` (design.md registry), `test_docs_accord.py` + `test_book_parity.py` (book↔skill accord).
- Todo source: backlog #13 (closed-into-this-milestone); sizing confirmed via intake interview (new beat 0 · pure convention · single task).

Honors (patterns / conventions):
- **3-tree mirror parity** — every guide/template edit propagates byte-identical across canonical + `_bundled` + dogfood; parity tests enforce it.
- **Convention-only** — NO `add.py` / state.json / ENGINE_MD5 change (the engine never renders); confirm ENGINE_MD5 unchanged at verify.
- **Identity human-owned** (`udd-tokens.md`) — the VISUAL DESIGN axis SURFACES color/type for the human, never auto-picks a brand value.
- **Lean fence** — design.md sits under a token-budget fence; grow it minimally and rebaseline the fence, never bypass it.

Anchors the contract cites:
- `design.md` `## The loop` — the new `### 0 · design-intake` beat (four axes: FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) inserted before `### 1 · review-domain`.
- `DESIGN.md.tmpl` — a new section capturing the four axes' answers.
- `appendix-c-glossary.md` — the four axis-term glossary entries.
- 3-tree parity + ENGINE_MD5-unchanged as the convention-only invariant.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a `design-intake` beat (beat 0) in the UDD design loop — the agent interviews the human on four named axes (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) before review-domain, records the answers, and lets them inform the existing beats. Convention-only (guide + template + book), no engine change.
Framings weighed: new front beat `design-intake` before review-domain (chosen — confirmed by intake interview) · fold the four axes into the existing beats · a separate intake-style sub-guide
Must:
<must>
  - `design.md` opens `## The loop` with a new `### 0 · design-intake` beat, BEFORE `### 1 · review-domain`, and the loop diagram lists it (`design-intake → review-domain → research-components → wireframe → render-capture-confirm`).
  - The beat interviews the human on FOUR named axes, each with the example options from #13: FIDELITY (lo-fi wireframe / hi-fi mockup / production) · CONCEPT (idea / mood / direction) · LAYOUT (structure / grid / hierarchy) · VISUAL DESIGN (color / type / spacing / imagery).
  - The beat RECORDS the four answers before review-domain runs, BOTH altitudes: project DEFAULTS in the DESIGN.md "## Design intake" section (template-seeded), and per-screen OVERRIDES (only the deltas) in the per-feature design note (the `prototypes/<name>.json` companion / the screen's record) — show-before-ask: the answers are confirmed with the human, not assumed.
  - The VISUAL DESIGN axis SURFACES identity values (color/type) for the human to decide — it MUST NOT auto-pick a brand value (honors identity-human-owned, `udd-tokens.md`).
  - FIDELITY is recorded as the human's chosen intent for how far the loop renders (it informs the later beats — it does not add an engine gate).
  - `DESIGN.md.tmpl` gains a `## Design intake` section (the four axes, human-fills-then-deletes-comment style matching the existing `## Identity` / `## Principles`).
  - The four axis terms appear in the book — narrated in `14-foundation.md` (the loop now has five beats) and defined in `appendix-c-glossary.md`.
  - Every edit propagates byte-identical across the 3-tree mirror (canonical · `_bundled` · dogfood); `add.py` / state.json / ENGINE_MD5 are UNCHANGED.
</must>
Reject:
<reject>
  - the VISUAL DESIGN axis auto-selects a brand color/typeface instead of surfacing it -> "identity_auto_picked"
  - any engine edit (`add.py` / state.json / ENGINE_MD5 changes) -> "engine_touched"
  - a mirror copy left out of sync (guide or template differs across the 3 trees) -> "mirror_drift"
  - reshaping a UDD data contract (`tokens.json` / `catalog.json` / `prototypes/<name>.json`) -> "contract_reshaped"
</reject>
After:
<after>
  - The UDD loop has FIVE beats; a UI feature's design begins by interviewing + recording the four axes before any domain read.
  - Identity values stay human-owned; the 3-tree parity + book-accord tests are green; ENGINE_MD5 is unchanged; the lean fence is rebaselined (not bypassed).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ✓ RESOLVED at freeze (Tin Dang): record BOTH altitudes — project defaults in DESIGN.md "## Design intake", per-screen overrides (deltas only) in the per-feature design note. (Was the ⚠ flag: project-level vs per-feature recording.)
  - [ ] FIDELITY is record-only intent, NOT an engine/check gate — confirm convention-only holds (a "production-fidelity feature lacking a hi-fi capture" WARN would be engine work, explicitly out of scope).
  - [ ] CONCEPT + VISUAL DESIGN do not duplicate the existing DESIGN.md `## Identity` (brand/voice) + `## Principles` enough to merge — the new section cross-references rather than restates them.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: design-intake is beat 0 of the loop
  Given the UDD guide design.md
  When I read its "## The loop" section
  Then a "### 0 · design-intake" beat appears before "### 1 · review-domain"
  And the loop diagram reads "design-intake → review-domain → research-components → wireframe → render-capture-confirm"

Scenario: the beat names all four axes with their options
  Given the design-intake beat in design.md
  When I read it
  Then it interviews FIDELITY (lo-fi wireframe / hi-fi mockup / production), CONCEPT (idea / mood / direction), LAYOUT (structure / grid / hierarchy), and VISUAL DESIGN (color / type / spacing / imagery)

Scenario: the four answers are recorded before review-domain
  Given the design-intake beat
  When I read how it ends
  Then it records project DEFAULTS in the DESIGN.md "## Design intake" section and per-screen OVERRIDES (deltas only) in the per-feature design note, confirmed with the human (show-before-ask), before review-domain runs

Scenario: VISUAL DESIGN surfaces identity, never auto-picks
  Given the design-intake beat and DESIGN.md.tmpl
  When I read the VISUAL DESIGN axis
  Then it surfaces color/type for the human to decide and states identity stays human-owned (cross-referencing udd-tokens.md)
  And no brand value is auto-selected   # reject: identity_auto_picked

Scenario: FIDELITY is record-only intent, not a gate
  Given the design-intake beat
  When I read the FIDELITY axis
  Then it is recorded as the human's chosen render intent that informs later beats
  And add.py / state.json / ENGINE_MD5 are unchanged   # reject: engine_touched

Scenario: DESIGN.md template seeds a Design intake section
  Given DESIGN.md.tmpl
  When I read it
  Then it has a "## Design intake" section listing the four axes in the fill-then-delete-comment style of "## Identity"

Scenario: the book documents the five-beat loop and the axis terms
  Given docs/14-foundation.md and docs/appendix-c-glossary.md
  When I read them
  Then 14-foundation narrates the loop with the design-intake beat (five beats)
  And appendix-c-glossary defines the four axis terms

Scenario: every surface is mirrored byte-identical
  Given the three skill trees (canonical, _bundled, dogfood) and the three template trees
  When I diff design.md and DESIGN.md.tmpl across the trees
  Then they are byte-identical   # reject: mirror_drift
  And the lean fence (test_skill_lean.py) is green (rebaselined, not bypassed)

Scenario: no UDD data contract is reshaped
  Given the change set
  When I inspect what files changed
  Then tokens.json / catalog.json / prototypes/<name>.json schemas are untouched   # reject: contract_reshaped
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CONTENT CONTRACT (prose/convention task — the shape of the change, not an API)

design.md  ## The loop
  + diagram line: design-intake → review-domain → research-components → wireframe → render-capture-confirm
  + new beat:  ### 0 · design-intake   (placed before "### 1 · review-domain")
       interviews FOUR axes, each with its option set:
         FIDELITY      : lo-fi wireframe | hi-fi mockup | production
         CONCEPT       : idea | mood | direction
         LAYOUT        : structure | grid | hierarchy
         VISUAL DESIGN : color | type | spacing | imagery   (SURFACE identity, never auto-pick)
       ends by: record the four answers human-confirmed BEFORE review-domain —
                project DEFAULTS in DESIGN.md "## Design intake"; per-screen OVERRIDES (deltas only)
                in the per-feature design note (prototypes/<name>.json companion / screen record)
  ## The hard rules  + one rule: "Intake before domain. The four axes are interviewed and recorded (DESIGN.md defaults + per-screen overrides) before beat 1."
  (heading "## The loop — four beats" → "## The loop")

DESIGN.md.tmpl  + new "## Design intake" section
  the four axes as fill-then-delete-comment prompts (matching "## Identity" style);
  VISUAL DESIGN cross-references "## Identity" (human-owned), does not restate it.

docs/14-foundation.md  : narrate the loop with the design-intake beat (five beats, not four)
docs/appendix-c-glossary.md : + entries defining FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN (as UDD intake axes)
SKILL.md (line ~126) : update the one-line loop pointer only IF it restates the beat list

INVARIANTS (the Reject codes):
  identity_auto_picked  — VISUAL DESIGN must surface, never select a brand value
  engine_touched        — add.py / state.json / ENGINE_MD5 UNCHANGED
  mirror_drift          — design.md (×3) + DESIGN.md.tmpl (×3) byte-identical across trees
  contract_reshaped     — tokens.json / catalog.json / prototypes/<name>.json schemas untouched

Mirror: every design.md + DESIGN.md.tmpl edit lands byte-identical in all 3 trees.
Lean fence: test_skill_lean.py rebaselined to the new (minimal) design.md size, not bypassed.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-26); recording model = both (DESIGN.md defaults + per-screen overrides)
Least-sure flag surfaced at freeze: [spec] WHERE the four-axis answers are recorded — project-level DESIGN.md vs per-feature/per-screen. Why most likely wrong: the intake is per-feature but DESIGN.md is project-wide identity. Cost if wrong: answers bloat the project doc or get lost. RESOLVED by the human at freeze → record BOTH (DESIGN.md defaults + per-screen overrides).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every frozen scenario has ≥1 assertion (prose/convention task — content + parity, not %).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_intake_is_beat_zero / test_loop_diagram_lists_intake_first: design-intake present BEFORE review-domain; five beats in order
  - test_four_axes_named / test_axis_option_sets_present: FIDELITY·CONCEPT·LAYOUT·VISUAL DESIGN + their option tokens
  - test_records_both_altitudes: points at DESIGN.md "## Design intake" + per-screen OVERRIDES
  - test_visual_design_surfaces_identity: SURFACE + human-owned (reject identity_auto_picked)
  - test_fidelity_is_intent_not_gate: FIDELITY framed as recorded intent that informs later beats
  - test_template_has_design_intake_section / _names_four_axes / _is_prompt_not_prefilled / _crossrefs_identity: DESIGN.md.tmpl section
  - test_foundation_narrates_intake_beat / test_glossary_defines_axis_terms: book accord
  - test_design_guide_mirrored / test_design_template_mirrored: 3-tree byte parity (reject mirror_drift)
</test_plan>

Tests live in: `add-method/tooling/test_design_intake_beat.py` · MUST run red (missing implementation) before Build.   (12/15 red @ tests; the 3 parity tests green until propagation diverges, re-green after mirror)
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/design.md` `add-method/src/add_method/_bundled/skill/add/design.md` `.claude/skills/add/design.md` `add-method/tooling/templates/DESIGN.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/DESIGN.md.tmpl` `.add/tooling/templates/DESIGN.md.tmpl` `add-method/skill/add/SKILL.md` `add-method/docs/14-foundation.md` `add-method/docs/appendix-c-glossary.md` `add-method/tooling/test_skill_lean.py` `add-method/tooling/test_design_loop_guide.py` `add-method/tooling/test_udd_design_template.py`
Strategy (ordered batches): 1. write/extend red tests (design_loop_guide + udd_design_template assertions for the new beat/section + axis terms) · 2. edit design.md canonical + DESIGN.md.tmpl canonical + book (14-foundation, glossary) + SKILL.md pointer · 3. propagate byte-identical to the 2 mirror trees each (guide ×3, template ×3) · 4. rebaseline test_skill_lean.py to the new minimal size · 5. run the suite + confirm ENGINE_MD5 unchanged
Safety rule (feature-specific): NO engine edit (add.py / state.json / ENGINE_MD5) — convention-only; identity values surfaced, never auto-picked; all 6 mirror files byte-identical to their canonical.
Code lives in: the guide/template/book/test paths above (no `./src/`).
Constraints: do NOT change the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1995/0; `add.py check` 425/0 (26 warns, all pre-existing)
- [x] coverage did not decrease — +1 new test file (test_design_intake_beat.py, 15 assertions), nothing removed
- [~] no test or contract was altered during build — contract UNTOUCHED; ONE test edited: `test_fidelity_is_intent_not_gate` slice fix (a DEFECT — it sliced the diagram line where "design-intake"/"review-domain" co-occur; corrected to slice the beat body `### 0`→`### 1`). Same assertion intent; NOT a weakening. Disclosed below.
- [x] the green was EARNED, not gamed — assertions check real content (beat order, four axis names + option tokens, the rendered `## Design intake` section, book narration + glossary terms, 3-tree byte-parity). No vacuous asserts, no stubbing. The test-edit corrected a region bug, did not relax a check.
- [x] concurrency / timing — N/A (prose/convention; no runtime code path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; zero new deps
- [x] layering & dependencies follow CONVENTIONS.md — convention-only; NO `add.py`/state.json/ENGINE_MD5/add_engine touched (git-confirmed)
- [ ] a person reviewed and approved the change — pending the gate (contract was human-approved at freeze)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] the UDD loop opens with `design-intake` first — confirmed: design.md diagram reads `design-intake → review-domain → research-components → wireframe → render-capture-confirm`
- [x] the four axes are interviewed with their option sets — confirmed by reading the `### 0 · design-intake` beat (FIDELITY lo-fi/hi-fi/production · CONCEPT · LAYOUT · VISUAL DESIGN)
- [x] DESIGN.md renders a `## Design intake` section with the four axes as fill-then-delete prompts — confirmed by the rendered output (HTML-comment prompts, cross-refs ## Identity, no brand auto-pick)
- [x] identity stays human-owned — confirmed: VISUAL DESIGN says "Surface … never auto-pick a brand value"; template prompts carry no concrete hex/typeface
- [x] book (×4 trees) narrates five beats + glossary defines the four axis terms — confirmed: 14-foundation + appendix-c-glossary synced across canonical/root/.add/_bundled
- [x] convention-only — confirmed: ENGINE_MD5 / add.py unchanged (git)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full: the design-intake beat, the DESIGN.md.tmpl `## Design intake` section, the 14-foundation narration, and the glossary entry. Coherent, consistent naming (FIDELITY·CONCEPT·LAYOUT·VISUAL DESIGN), banned-slang clean ("at both levels", not "altitudes").

### GATE RECORD
Outcome: PASS
Note: one disclosed non-blocking residue — a test region-slice DEFECT fixed during build (not a weakening; same assertion, correct region). No security/concurrency/architecture residue.
Reviewed by: Tin Dang (contract approved @ freeze; verify auto-gated on complete evidence under autonomy:auto) · date: 2026-06-26

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether design.md / DESIGN.md.tmpl / book stay synced across all trees on future edits (parity + docs-accord tests as monitors).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] consider a never-red `check` WARN nudging a design whose recorded FIDELITY is "production" but has no hi-fi capture (evidence: this task scoped FIDELITY as record-only intent; an engine-side nudge was deliberately deferred as out-of-scope) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [UDD · folded] a design feature now opens with an explicit four-axis intake (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) BEFORE the domain read — the look is directed, not guessed (evidence: design-intake beat 0 shipped this milestone) [folded foundation-version 53]
- [ADD · folded] the book mirrors across FOUR trees (canonical add-method/docs · repo-root · .add/docs · _bundled/docs), not three — a docs edit must hit all four or test_book_parity + the docs-accord tests go red (evidence: 8 reds from 2 missed mirror dirs this build) [folded foundation-version 53]
- [ADD · folded] the tamper-tripwire flags ANY test edit during build, even a legitimate slice-defect fix — the honest remedy is to re-cross tests→build to re-baseline the snapshot, never hand-edit around the gate (evidence: gate PASS returned-to-build attempt 1 this task) [folded foundation-version 53]
- [ADD · folded] "altitude(s)" is banned slang on the extended surface (renamed "scope level"); a new guide must say "levels" (evidence: test_ubiquitous_language red on design.md "both altitudes" this build) [folded foundation-version 53]
