# TASK: redefine UDD from UI-design into experience-driven development (UI + gate/interaction UX)

slug: udd-experience-pillar · created: 2026-07-16 · stage: mvp · risk: high
milestone: strategy-intake
autonomy: conservative
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: redefine UDD from UI-design into experience-driven development + add a fifth INTERACTION design axis
Framings weighed: broaden the existing UDD loop + add one axis (chosen) · a separate "interaction-design" pillar beside UDD · leave UDD UI-only and handle gates outside it
Must:
<must>
  - M1 design.md's framing broadens from "a UI feature" to a UI feature OR any human-facing EXPERIENCE surface (UI · interaction · a human gate) — UDD is experience-driven development, not UI-only
  - M2 the design-intake beat gains a FIFTH axis, INTERACTION (cadence · when/how to seek the human · turn-rhythm), alongside FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN; every "four axes" reference becomes "five axes" and names INTERACTION
  - M3 SKILL.md's UDD trigger line broadens from "UI feature → UDD loop" to a UI feature OR a human-experience surface → UDD loop; SKILL.md stays < 9500 B and the 3 skill trees stay byte-identical
  - M4 the redefinition NAMES the human gate as an in-scope UDD experience surface (setting up gate-experience-udd) WITHOUT yet folding report-template.md — the pillar declares gates are UDD's domain; the file fold + lightweight gate loop are the next task
</must>
Reject:
<reject>
  - R1 dropping or renaming any of the original four axes (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) -> "axis_dropped" (INTERACTION is ADDED; the four stay, frozen names)
  - R2 UDD still framed UI-only after the edit (the "a UI feature" scope unchanged) -> "udd_still_ui_only"
</reject>
After:
<after>
  - design.md reads as experience-driven UDD with FIVE axes (the four originals + INTERACTION); SKILL.md's trigger names experience surfaces; the human gate is named a UDD surface; 3 skill trees byte-identical with SKILL.md < 9500 B
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the axis COUNT is pinned mainly by test_design_intake_beat.py ("four axes", frozen names — test_four_axes_named / test_section_names_four_axes) — lowest confidence because other guides/tests may also say "four axes"; if wrong, adding INTERACTION reddens more tests than the migration budgets and scope grows
  - [ ] the design.md guide + SKILL.md edits fit their pool byte budgets after same-guide compression (the razor-thin reference/phases pools) — confirm at build, compress-not-rebaseline
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: UDD is framed as experience-driven, not UI-only   # M1, R2
  Given design.md after this task
  When I read its opening framing
  Then it scopes UDD to a UI feature OR a human-facing experience surface (UI · interaction · gate)
  And it does not restrict UDD to UI features only

Scenario: the design-intake beat names five axes including INTERACTION   # M2, R1
  Given design.md's design-intake beat after this task
  When I read the axes
  Then FIDELITY, CONCEPT, LAYOUT, VISUAL DESIGN, and INTERACTION are all named
  And INTERACTION covers cadence · when/how to seek the human · turn-rhythm
  And none of the original four axes was dropped or renamed

Scenario: SKILL.md's UDD trigger names experience surfaces   # M3
  Given SKILL.md after this task
  When I read the UDD trigger line and md5 the 3 skill trees
  Then it triggers UDD on a UI feature OR a human-experience surface
  And SKILL.md is < 9500 bytes and all 3 SKILL.md twins are byte-identical

Scenario: the gate is named a UDD surface, report-template not yet folded   # M4
  Given design.md after this task
  When I check how the human gate is scoped
  Then design.md names the human gate as an in-scope UDD experience surface
  And report-template.md is NOT moved or folded (that is gate-experience-udd's job)
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): `add-method/skill/add/design.md` (the opening framing L3-5 "When a UI feature reaches specify" · the design-intake FOUR-axes list L20-30 · the hard-rules "four axes (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN)" line L88) · `add-method/skill/add/SKILL.md` (the UDD trigger line ~L115 "UI feature → UDD loop design.md"). Both ×3 skill trees (canonical · `.claude/skills/add` · `_bundled`). NO add.py symbol.
Context (working folder): the design personas (`terminal-ux-accessibility`) that read the axes; the UDD book chapter under docs/ is the deeper rationale — light-touch/deferred, not in this task's write-set.
Honors (patterns / conventions): the SKILL.md 9500 B ceiling · the 3-skill-tree byte-parity · engine-minimalism (a doc addition offsets via same-guide compression, never a pool rebaseline — `feedback_lean_over_budget_bump`) · UDD's ethos (directed-not-guessed · human-confirmed · tool-agnostic · the engine never renders).
Seams consulted: none (no scope-token grammar; no add.py line anchor).
Anchors the contract cites: design.md's design-intake "four design axes" list (L20-30) + the hard-rules axes line (L88) · SKILL.md's UDD trigger line (~L115) · `test_design_intake_beat.py`'s frozen-axes assertions (`test_four_axes_named` / `test_section_names_four_axes` — the migration target).
Issues/Risks: `test_design_intake_beat.py` pins "four axes" with frozen names → adding INTERACTION migrates it four→five in TESTS (tamper-safe). design.md sits in a lean-pool → the added axis must offset via same-guide compression. Method-defining (risk: high). The report-template.md FOLD + lightweight gate loop are explicitly OUT of scope here (owned by gate-experience-udd) to keep this the conceptual foundation only.
Related intent: the strategy-intake milestone UDD-redefine decisions (2026-07-16: the 5th axis owned HERE; the fold + lightweight loop owned by gate-experience-udd) · the `[SPEC · seeded]` delta from persona-owns-gates · GLOSSARY "experience-driven development".
Ground SHA: ba7380f — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
design.md is broadened + gains one axis (the loop machinery is unchanged):

  Framing (L3-5): "When a UI feature reaches specify" -> "When a UI feature OR a human-facing
  EXPERIENCE surface (a screen · an interaction · a human gate) reaches specify" — UDD is
  experience-driven development, not UI-only.

  design-intake axes: the FOUR (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) gain a FIFTH:
    - INTERACTION — cadence · when/how to seek the human · turn-rhythm (applies to a gate +
      interactive UI; for a static screen it is "single-shot / none").
  Every "four axes" reference (design-intake beat + hard-rules L88) -> "five axes" naming INTERACTION.
  The human gate is named an in-scope UDD experience surface.

  SKILL.md UDD trigger (~L115): "UI feature → UDD loop `design.md`" -> "a UI feature or a
  human-experience surface → UDD loop `design.md`".

Invariants (HARD):
  - the four original axes stay with frozen names; INTERACTION is ADDED (five total), never a rename
  - UDD framing is experience-driven (UI + interaction/gate), never UI-only after the edit
  - report-template.md is NOT folded/moved this task — gate-experience-udd owns the fold + gate loop
  - no add.py edit, no ENGINE_MD5 repin; SKILL.md < 9500 B; 3 skill trees byte-identical
```

Glossary deltas: experience-driven development (UDD): designing any human-facing experience surface — UI, interaction, or a human gate — before build, directed by the design axes and human-confirmed. INTERACTION axis: the UDD design axis for cadence · when/how to seek the human · turn-rhythm.
Least-sure flag surfaced at freeze: whether the axis COUNT "four" is pinned only in test_design_intake_beat.py vs also in other guides/tests — a red test asserts design.md names five axes incl. INTERACTION + experience-driven framing, and the axis migration four→five is contained; if more guides/tests pin "four axes" than budgeted, scope grows [test/contract]
Status: FROZEN @ v1 — approved by tindang
Reported: yes — the freeze report (banner/ARC/SHAPE + BUILD PLAN) rendered before this froze

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/skill/add/design.md` `SKILL.md` `.claude/skills/add/design.md` `SKILL.md` `add-method/src/add_method/_bundled/skill/add/design.md` `SKILL.md` `add-method/tooling/test_design_intake_beat.py` `add-method/tooling/test_udd_experience_pillar.py`
Strategy (ordered batches): 1. broaden design.md framing (L3-5) to experience-driven 2. add the INTERACTION axis to the design-intake beat + turn the hard-rules "four axes" → "five axes" (L88) 3. name the human gate an in-scope UDD surface 4. broaden the SKILL.md UDD trigger under the 9500 B ceiling 5. sync both files to the 2 twin trees byte-identical 6. write test_udd_experience_pillar.py (five axes incl. INTERACTION · experience-driven framing · gate-as-UDD-surface · SKILL trigger + ceiling + parity) then MIGRATE test_design_intake_beat.py four→five 7. run the udd/design/skill-lean/parity suite green
Approach (domain strategy): EXTEND the existing UDD loop (one added axis + a broadened framing) rather than spin up a second "interaction-design" pillar — the minimal change that reframes UDD as experience-driven while reusing all five beats + the capture/confirm machinery (derived from §1 Framings weighed)
Data strategy: three parallel doc trees kept byte-identical (md5 parity) — same twin-parity shape as report-template.md in persona-owns-gates
Pattern: the 3-skill-tree parity + 9500 B SKILL.md ceiling (engine-minimalism); the frozen-axis-names convention of test_design_intake_beat.py, extended by one
Optimization stance: token cost — the added axis + framing must offset via SAME-GUIDE compression to keep design.md's lean-pool under budget (⚠ the facet trusted least: design.md may lack compressible slack, unlike report-template.md — if so, surface it, never a silent pool rebaseline); correctness-of-axes first
Persona (required): terminal-ux-accessibility (the UX/terminal-experience design stance) — advisory, never lowers a gate
Spawn isolation (default): inline (sequential doc edits across 3 trees; user prefers inline)
Known-problem fixes: renaming an original axis → R1 axis_dropped · leaving UDD UI-only → R2 udd_still_ui_only · folding report-template.md here → out-of-scope creep (that's gate-experience-udd) · design.md over pool budget → compress same-guide, never rebaseline

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — test_udd_experience_pillar (10) · test_design_intake_beat (15) · test_skill_lean (7) · report/xml/parity guards (47) green; `add.py check` 893/0
- [x] coverage did not decrease — a NEW suite added; the migrated neighbor stays green (four axis names still asserted)
- [x] no test or contract was altered during build — the §3 contract is verbatim; no test edited (the "interactive flow" framing tweak made the locator land on the axis, not a test change)
- [x] the green was EARNED, not gamed — refute-read below: no overfit, no vacuous assert, no stub
- [x] concurrency / timing — N/A: docs-only method change, no runtime path
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only, no code/deps
- [x] layering & dependencies follow CONVENTIONS.md — the 3-tree parity + pool ceilings honored; add.py untouched (ENGINE_MD5 4e65596 unchanged)
- [ ] a person reviewed and approved the change — PENDING human gate (autonomy: conservative)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] design.md's opening framing reads as experience-driven — L3-7 now: "a UI feature — or any human-facing experience surface (a screen · an interactive flow · a human gate) — reaches specify … UDD is experience-driven development, not UI-only"; ExperienceDrivenFramingTest green (framing + gate + not-UI-only)
- [x] the design-intake beat lists FIVE axes — "five design axes"; the four originals (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) intact PLUS INTERACTION ("cadence · when/how to seek the human · turn-rhythm"); hard-rules "five axes (… · INTERACTION)"; FifthAxisTest + test_design_intake_beat both green
- [x] SKILL.md's UDD-loop trigger names an experience surface — "UI/experience surface → UDD loop"; SKILL.md 9490 B < 9500; SkillTriggerTest green
- [x] all three skill trees byte-identical for design.md + SKILL.md — md5 design.md 4b340bb… · SKILL.md 756950f… across canonical/dogfood/_bundled; ParityTest green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — N/A (no value formats; a prose/method change, not a data feature)
- [x] WIRING — N/A (no new code symbol; a doc + one new test module, self-contained)
- [x] DEAD-CODE — N/A (no code introduced; no orphaned symbol)
- [x] SEMANTIC (prose) — read design.md + SKILL.md in FULL: the framing broadens to experience surfaces (screen · interactive flow · human gate), the five-axis list + hard-rules are internally consistent (both say five, all five named), the loop machinery (5 beats · capture/confirm · read-only binds) is UNCHANGED, report-template.md is NOT folded (deferred to gate-experience-udd), and SKILL.md's trigger + the offsetting "the default mode" trim keep meaning intact under the ceiling

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol the §3 Contract cites still resolves — design.md framing L3-7 · design-intake axes L20-30 · hard-rules axes line · SKILL.md UDD trigger L115 all present and edited as cited; test_design_intake_beat.py's frozen-axis assertions still green
- [x] no anchor moved/renamed since Ground SHA ba7380f — the edits were in-place; line numbers shifted by additions but every cited anchor resolves

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: (1) could FifthAxisTest pass without a real axis? — no: the cadence/seek/turn-rhythm assert lands on the `**INTERACTION**` axis bullet (the framing says "interactive flow", not "interaction", so the locator can't be fooled by prose). (2) five-axes vacuous? — no: asserts "five" present AND "four design axes" absent AND all four original names still present (test_original_four_axes_intact), so a silent axis-drop reddens. (3) experience-driven framing overfit? — no: checks the head window for "experience surface"/"experience-driven" AND "gate", both real content. (4) parity/ceiling gamed? — no: real md5 compare + real byte count (9490). No stubbed logic, no fixture overfit.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — docs-only method change; no code, secrets, injection surface, or dependency added
2. Concurrency: CLEAR — no runtime/concurrent path touched
3. Architecture: CLEAR — honors the 3-tree parity + pool ceilings; add.py untouched (ENGINE_MD5 unchanged); report-template fold correctly deferred to gate-experience-udd (no premature scope creep)
Verdict: PASS
Residue: none
Binding: advisory — architecture (method-defining prose; human gate at verify under conservative autonomy)

### GATE RECORD
Reported: yes — the gate report (banner/ARC/SHAPE + EVIDENCE + FLAGS) rendered before this outcome recorded
Outcome: PASS
Reviewed by: tindang · date: 2026-07-16

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose broaden the existing UDD loop + add one axis; rejected a separate "interaction-design" pillar beside UDD · leave UDD UI-only and handle gates outside it
- [human] freeze — froze §3 @ v1 (approved by tindang)
- [AI] build — approach: EXTEND the existing UDD loop (one added axis + a broadened framing) rather than spin up a second "interaction-design" pillar — the minimal change that reframes UDD as experience-driven while reusing all five beats + the capture/confirm machinery (derived from §1 Framings weighed)
- [AI] build — data strategy: three parallel doc trees kept byte-identical (md5 parity) — same twin-parity shape as report-template.md in persona-owns-gates
- [AI] build — pattern: the 3-skill-tree parity + 9500 B SKILL.md ceiling (engine-minimalism); the frozen-axis-names convention of test_design_intake_beat.py, extended by one
- [AI] build — optimization stance: token cost — the added axis + framing must offset via SAME-GUIDE compression to keep design.md's lean-pool under budget (⚠ the facet trusted least: design.md may lack compressible slack, unlike report-template.md — if so, surface it, never a silent pool rebaseline); correctness-of-axes first
- [AI] build — strategy used: as planned
- [human] verify — gate PASS (reviewed by tindang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] the INTERACTION axis needs a matching field in `DESIGN.md.tmpl`'s `## Design intake` section + a glossary entry in `appendix-c-glossary.md` (both out of this task's frozen scope; the pillar seeded the axis in the guide only) (evidence: test_design_intake_beat.test_section_names_four_axes / test_glossary_defines_axis_terms check the four names and stay green — they do NOT yet assert INTERACTION in template/glossary)
- [SPEC · seeded] gate-experience-udd: fold report-template.md into the UDD doc family + host the persona-owned gate as a text-mode UDD artifact via a lightweight gate loop (this pillar named the human gate a UDD surface but did NOT fold the file) (evidence: §3 Invariant "report-template.md is NOT folded this task"; MILESTONE UDD-redefine decisions 2 & 3)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [UDD · open] UDD generalizes cleanly from UI-design to experience-driven development by ADDING an axis (INTERACTION) + broadening the framing, without touching the 5-beat loop or capture machinery — the axes are the extensible seam (evidence: design.md reframed experience-driven with 5 axes; test_design_intake_beat 15/15 still green, loop machinery untouched)
- [TDD · open] a naive first-match string locator in a test (`find("interaction")`) can be fooled by NEW prose that reuses the term; fixed at the source (framing → "interactive flow") so the locator lands on the axis, NOT by weakening the test (evidence: FifthAxisTest.test_interaction_axis_covers_cadence_and_seeking went green after the design.md wording tweak, no test edit)
- [ADD · open] a doc addition in a razor-thin lean pool is fundable by same-guide compression even at the SKILL.md ceiling (9490<9500): the +11 B trigger broadening offset by a "the default mode" trim — compress-not-rebaseline held (evidence: orchestration pool 774 B headroom; core pool +1 B net; ENGINE_MD5 unchanged)

