# TASK: UDD captured-screen confirm uses UI-Designer + UX-Researcher persona success-metrics as an evidence checklist

slug: udd-persona-loop · created: 2026-06-29 · stage: mvp
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
  - `add-method/skill/add/design.md` — the UDD design-definition loop; beat **4 · render-capture-confirm** (≈54-63) is where the design-confirm happens. THIS task adds a persona-sourced evidence checklist to that beat. 3 skill trees (canonical · `.claude/skills/add` · `_bundled/skill/add`).
  - `add-method/skill/add/design.md:## The hard rules` (≈85-99) — the `<constraints>` block; a new rule ("confirm against the matched personas' success-metrics") joins here.
  - `.add/personas/<slug>.md:## Success Metrics` — the measurable lines this task renders as confirmable checklist items (schema FROZEN by persona-setup). Read-only consumer.
  - `add-method/tooling/test_design_loop_guide.py` — the doc-truth test pattern for design.md (asserts the guide documents a beat); the new dimension-coverage test mirrors it.
Context (working folder):
  - `.add/milestones/persona-learning-loop/MILESTONE.md` — shared decision: UDD sources TWO personas (UI-Designer: visual + WCAG-AA; UX-Researcher: methodology-first, evidence-not-assumption). The checklist carries BOTH; a UI-less project skips.
  - TEACHER (read off-build by the AI, never the engine): agency-agents `ui-designer` + `ux-researcher` — their critical-rules + measurable success-metrics seed the project's two UI personas at setup (persona-setup).
  - `.add/GLOSSARY.md` — term home if a new term is added.
Honors (patterns / conventions):
  - the engine NEVER renders / NO-EXEC — the checklist is a guide step run by the AI's own tools; the image + checklist are evidence, not engine artifacts.
  - bind-don't-break — design.md reads `.add/personas/*` read-only; the persona schema is unchanged (a change to it is a change request to persona-setup).
  - a persona NEVER lowers a gate — the success-metrics are a confirm checklist the human approves, not an auto-pass (reinforces ADD principle 2).
  - 3-tree skill parity (byte-identical), enforced by parity tests; red/green TDD.
Anchors the contract cites: design.md beat 4 render-capture-confirm · the persona `## Success Metrics` section · the design-confirm checklist shape (success-metrics → confirmable items, two dimensions) · the hard-rules `<constraints>` block.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Persona-sourced design-confirm checklist — at the UDD render-capture-confirm beat, BEFORE the human design-confirm, the AI matches the screen to the project's seeded UI personas and renders their `## Success Metrics` as an evidence checklist presented WITH the captured image. The checklist carries TWO dimensions: UI-Designer (visual + accessibility — "is the screen right?") and UX-Researcher (methodology-first — "validated by user evidence, not assumed?"). Tool-agnostic; the engine never renders; the checklist is confirm evidence, never an auto-pass.
Framings weighed: source BOTH personas' success-metrics into the existing design-confirm (chosen — one checklist, two dimensions, reinforces evidence-over-assumption) · a single merged "design quality" persona (rejected — loses the methodology-vs-visual distinction) · a separate post-build UX audit step (rejected — confirm-before-build is the UDD floor)
Must:
<must>
  - design.md beat 4 (render-capture-confirm) documents: before design-confirm, render the matched UI personas' `## Success Metrics` as a confirmable checklist shown with the captured image.
  - The checklist carries BOTH dimensions explicitly: UI-Designer (visual / WCAG-AA accessibility) AND UX-Researcher (methodology-first, evidence-not-assumption validation). Both are named in the guide.
  - Each checklist item is traceable to a persona success-metric line (success-metrics → confirmable items); the human confirms the screen against them — the checklist is evidence, never an auto-pass (a persona never lowers a gate).
  - Degrade-safe: a project with NO UI personas seeded still reaches design-confirm (generic confirm, never blocks); a UI-LESS project skips the beat entirely (unchanged).
  - The engine performs NO render and NO new gate — this is a guide step; `add.py` behavior is unchanged (or at most a never-red nudge consistent with the existing `missing_capture` WARN).
  - 3-tree skill parity: design.md carries the change byte-identically across the canonical, `.claude/skills/add`, and `_bundled/skill/add` trees.
</must>
Reject:
<reject>
  - a design-confirm step that renders only ONE dimension when both UI personas exist -> "persona_checklist_one_dimension" (documented anti-pattern; the doc-truth test asserts both are present)
  - treating a persona success-metric as an auto-pass that skips the human design-confirm -> "persona_autopass_forbidden" (a persona never lowers a gate)
  - reshaping the persona schema or `prototypes/<name>.json` to fit the checklist -> "contract_reshape_forbidden" (bind-don't-break; that is a change request elsewhere)
</reject>
After:
<after>
  - design.md (all 3 trees) documents the persona-sourced design-confirm checklist with BOTH the UI-Designer and UX-Researcher dimensions named; a doc-truth test asserts both dimensions.
  - The checklist is described as confirm evidence the human approves, never an auto-pass; the engine still never renders.
  - A no-UI-persona project and a UI-less project both still flow (degrade / skip), unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the project's two UI personas are discoverable by a stable convention (e.g. role/slug `ui-designer` + `ux-researcher`, or a `vibe`/name match) so design.md can "match the screen to the UI personas" deterministically — lowest confidence because persona-setup froze the schema but NOT a role taxonomy/slug convention; if wrong: the guide must hand-wave the match ("the personas whose role is UI/UX") or persona-setup reopens to add a role field. (Mitigation: phrase the match as "the seeded personas covering visual design and UX research" — presence-based, no new schema field.)
  - [ ] a pure doc-truth test (guide names both dimensions + the checklist shape) is sufficient verification for a guide-only task — if wrong: add a tiny engine nudge (UI project with prototypes but no UI personas → never-red WARN) and test that.
  - [ ] both dimensions belong in ONE checklist at design-confirm (not split across two beats) — if wrong: UX-Researcher validation moves to a later observe-time check.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the design-confirm checklist sources both UI personas' success-metrics
  Given a UI project with .add/personas/ui-designer.md and .add/personas/ux-researcher.md seeded
  When the render-capture-confirm beat reaches design-confirm
  Then design.md documents rendering each matched persona's "## Success Metrics" as a confirmable checklist shown with the captured image
  And the checklist carries BOTH the UI-Designer (visual/accessibility) AND the UX-Researcher (methodology-first, evidence-not-assumption) dimensions

Scenario: the guide names both dimensions explicitly (doc-truth)
  Given the design.md UDD guide in all three skill trees
  When the persona-checklist section is read
  Then it names the UI-Designer dimension (visual / WCAG-AA accessibility)
  And it names the UX-Researcher dimension (validated by user evidence, not assumed)

Scenario: a persona success-metric is evidence, never an auto-pass
  Given the persona-checklist step at design-confirm
  When the guide describes how the checklist is used
  Then the human confirms the screen against the checklist (show-before-ask, before build)
  And the guide states a success-metric never auto-passes the design-confirm (a persona never lowers a gate)

Scenario: a project with no UI personas still confirms (degrade-safe)
  Given a UI project with NO UI personas seeded
  When the render-capture-confirm beat runs
  Then design-confirm still proceeds with a generic confirm
  And the loop is not blocked

Scenario: a UI-less project skips the beat (unchanged)
  Given a project with no UI surface (DESIGN.md deleted)
  When the flow runs
  Then the persona-checklist step does not apply
  And the non-UI flow is unchanged

Scenario: the change is byte-identical across the three skill trees
  Given the design.md edit
  When the three skill trees are compared
  Then the persona-checklist section is byte-identical in each
  And the skill parity test passes
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

DESIGN-CONFIRM PERSONA CHECKLIST — added to `design.md` beat 4 (render-capture-confirm)
  (described inline — no bare triple-dash / line-start `##` so the §3 span stays intact)
  • INPUT (read-only): the project's seeded UI personas under `.add/personas/` — the one(s)
    covering visual design and UX research (presence-based match; NO new schema field, NO role
    taxonomy added — uses the FROZEN persona schema as-is).
  • RENDER: each matched persona's `## Success Metrics` lines become confirmable checklist
    items, presented WITH the captured image at design-confirm (show-before-ask, before build).
  • TWO DIMENSIONS (both required in the guide prose):
      - UI-Designer  → visual + WCAG-AA accessibility metrics ("is the screen right?")
      - UX-Researcher → methodology-first, evidence-not-assumption validation
        ("validated by user data, not assumed?") + inclusive-research default.
  • USE: the human confirms the screen against the checklist. The checklist is EVIDENCE, never an
    auto-pass — a persona never lowers a gate (reinforces ADD principle 2: trust evidence, not
    assumptions). A security/correctness gate is untouched.
  • DEGRADE: no UI personas → generic design-confirm, never blocked. UI-less project → beat skipped.

ENGINE: UNCHANGED on this task — NO render, NO new gate, NO-EXEC preserved. (If a nudge is later
  wanted, it is a never-red WARN consistent with the existing `missing_capture`; out of scope here.)

BIND-DON'T-BREAK: design.md reads `.add/personas/*` and `prototypes/<name>.json` read-only; neither
  the persona schema nor the prototype data contract is reshaped (a reshape = change request elsewhere).

ERROR CODES (every §1 Reject has a documented response)
  persona_checklist_one_dimension -> the guide MUST present both dimensions when both personas exist
                                     (doc-truth test asserts both are named).
  persona_autopass_forbidden      -> a success-metric is a confirm checklist item, never an auto-pass.
  contract_reshape_forbidden      -> the persona schema + prototype data contract stay unchanged.

PARITY — the design.md change lands byte-identical in all 3 skill trees
  (`add-method/skill/add` · `.claude/skills/add` · `_bundled/skill/add`).

VERIFICATION — a doc-truth test asserts design.md (all 3 trees) documents the persona-sourced
  checklist AND names BOTH dimensions; the existing skill parity + lean-fence tests still pass.

Least-sure flag surfaced at freeze: ⚠ [contract] the persona match is presence-based ("the seeded
personas covering visual design and UX research") — there is NO role/slug taxonomy in the frozen
persona schema, so the guide describes the match in prose rather than a deterministic key. If a
deterministic match is later needed, persona-setup reopens to add a `role:` field (change request).
Mitigation: presence-based prose keeps THIS task additive and avoids reopening the frozen schema.

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject scenario has one assertion (doc-truth + parity)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_design_confirm_sources_persona_metrics: design.md documents rendering matched personas' "## Success Metrics" as the design-confirm checklist
  - test_checklist_names_both_dimensions: design.md names BOTH the UI-Designer (visual/accessibility) AND UX-Researcher (methodology/evidence-not-assumption) dimensions
  - test_metric_is_evidence_not_autopass: design.md states a success-metric is confirm evidence, never an auto-pass (a persona never lowers a gate)
  - test_degrade_no_ui_personas: design.md states design-confirm still proceeds when no UI personas exist (never blocks)
  - test_persona_checklist_3tree_parity: the persona-checklist section is byte-identical across the 3 skill trees
  - test_engine_unchanged_no_render: ENGINE_MD5 unchanged by this task (guide-only; no engine edit) — assert add.py/engine pins untouched
</test_plan>

Tests live in: `add-method/tooling/test_udd_persona_checklist.py` · MUST run red (guide not yet edited) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/design.md` `.claude/skills/add/design.md` `add-method/src/add_method/_bundled/skill/add/design.md` `add-method/tooling/test_udd_persona_checklist.py` `.add/GLOSSARY.md`
Strategy (ordered batches): 1. edit `design.md` beat 4 (render-capture-confirm) + the hard-rules `<constraints>` block to document the persona-sourced two-dimension checklist (evidence-not-autopass · degrade-safe). 2. mirror byte-identically to the other 2 skill trees (cp). 3. add the doc-truth + parity tests. 4. re-run lean fence — reclaim bytes from design.md prose if the addition pushes the pool over budget (ratios kept). Run red→green.
Known-problem fixes: lean fence (test_skill_lean) may trip — design.md is in the phases/guides pool → reclaim from the same guide's prose, never weaken the budget · wording-lint may flag new terms → match GLOSSARY casing · a guide-only task must NOT touch the engine pins (ENGINE_MD5/PKG) — if a pin test goes red, an engine file was edited by mistake.
Strategy actually used: as planned (edit design.md beat 4 + add a hard-rules constraint → mirror ×3 → doc-truth/parity tests → reclaim lean-fence bytes). The persona checklist + constraint added ~1170 B to the frozen orchestration pool; reclaimed every byte from the SAME guide's prose (intro, design-intake, beats 1–4, tool-agnostic-capture, binds paragraph) — ratios kept, never re-baselined the budget, never edited the out-of-scope test_skill_lean.py. Engine untouched (guide-only).
Safety rule (feature-specific): the engine stays render-free / NO-EXEC; the checklist is guide prose + the human's confirm, never an engine auto-pass.
Code lives in: `add-method/skill/add/`
Constraints: do NOT change any test or the contract; do NOT reshape the persona schema or prototype data contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2434/0
- [x] coverage did not decrease — 6 new doc-truth/parity tests added; none removed
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; only design.md prose edited
- [x] the green was EARNED — doc-truth tests assert real content tokens; read the final design.md beat 4 + constraints in full, prose is coherent (not token-stuffed); the two dimensions are genuinely distinct
- [x] concurrency / timing — n/a (guide-only prose; no engine/runtime change)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no code, no dependency
- [x] layering & dependencies follow CONVENTIONS.md — change confined to design.md; engine pins untouched (test asserts add.py md5 == pin)
- [x] reviewed — auto-resolved under `autonomy: auto` (no residue); self refute-read (doc-truth, content-mapped) + human spot-audit backstop

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] reading design.md beat 4 shows the persona-sourced checklist step with both dimensions named — CONFIRMED by reading the final guide
- [x] both dimensions (UI-Designer visual/accessibility + UX-Researcher methodology/evidence) appear in the guide prose — CONFIRMED by the doc-truth test + a manual read
- [x] the guide states the checklist is evidence, never an auto-pass, and degrades safely — CONFIRMED by the relevant tests + a read
- [x] design.md is byte-identical across the 3 skill trees and the engine pins are untouched — CONFIRMED by the parity test + the engine-unchanged (add.py md5 == pin) test

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — n/a (guide-only); the 6 new test methods are all referenced/run by the suite
- [x] DEAD-CODE (code) — no new unused symbol (no production code added)
- [x] SEMANTIC (prose) — read the edited design.md beat 4 + the hard-rules constraint in full: the persona evidence checklist coherently sources the matched UI personas' Success Metrics, carries two genuinely distinct dimensions (UI-Designer "is the screen right?" visual/accessibility vs UX-Researcher "the right screen?" evidence-not-assumption), states evidence-not-auto-pass + degrade-safe; the trimmed beats still read cleanly.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: whether the doc-truth tests could pass on token-stuffed/incoherent prose. They map to real content; I read the final design.md in full — the two dimensions are substantively different (not duplicated keywords), evidence-not-auto-pass is stated, degrade path is real. The ~1170 B reclaimed from existing prose preserved meaning (verified each trimmed beat reads cleanly). Low-risk doc-truth change → self refute-read is proportionate (vs the independent-agent reads used for the engine task persona-setup).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self (diff review)
1. Security: CLEAR — guide prose only; no code, no secrets, no dependency, no injection surface.
2. Concurrency: CLEAR — no runtime/engine change; design.md is read by humans/agents, not executed.
3. Architecture: CLEAR — confined to design.md across 3 trees (parity held); engine untouched (pin test green); bind-don't-break honored.
Verdict: PASS
Residue: none
Binding: advisory — sensitivity: docs/method-prose (guide-only)

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (autonomy: auto, no residue) — owner Tin Dang · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <persona-checklist adoption / one-dimension regressions>

### Decisions (ADR)
- [AI] specify — chose source BOTH personas' success-metrics into the existing design-confirm; rejected a single merged "design quality" persona (rejected — loses the methodology-vs-visual distinction) · a separate post-build UX audit step (rejected — confirm-before-build is the UDD floor)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned (edit design.md beat 4 + add a hard-rules constraint → mirror ×3 → doc-truth/parity tests → reclaim lean-fence bytes). The persona checklist + constraint added ~1170 B to the frozen orchestration pool; reclaimed every byte from the SAME guide's prose (intro, design-intake, beats 1–4, tool-agnostic-capture, binds paragraph) — ratios kept, never re-baselined the budget, never edited the out-of-scope test_skill_lean.py. Engine untouched (guide-only).
- [AI] verify — gate PASS (reviewed by auto-resolved (autonomy: auto, no residue) — owner Tin Dang)

### Spec delta
Forward changes for the next loop — one line each, tagged `[SPEC · open|seeded|dropped]`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency (`DDD · SDD · UDD · TDD · ADD`), status `open`.
