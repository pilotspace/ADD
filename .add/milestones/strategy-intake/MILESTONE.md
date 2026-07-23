# MILESTONE: personas as ADD's adaptive project-management brain

goal: A fitting persona becomes the project-management AND user-experience brain — it shapes each milestone's strategy, owns how every human gate is communicated and paced (replacing the fixed report-template ceremony), and designs that gate as a UDD user-experience artifact (UDD redefined from UI-design into experience-driven development: UI + interaction/gate UX, first-class). Personas adapt per project; one floor stays hard — security is always HARD-STOP.
rationale: bucket new-major, re-specced from "strategy session before a milestone" into the bigger vision the user set — "remove ceremony, make ADD more flexible via persona-led project management that adapts per project; retire the fixed report-template constraint; maximize personas' value." Today the report-template.md pins a fixed section list (banner · ARC · PLAN/SHAPE · SUMMARY · FLAGS · DECIDED · EVIDENCE · APPROVE · NEXT) at EVERY gate, and personas apply only at design/build/verify/advisor as advisory lenses. This milestone lifts personas to own the WHOLE project-management surface: intake strategy, gate structure, and gate cadence — no fixed template, adapted per project/domain. The engine still records; the persona (through the skill) drives.
stage: mvp · status: active · created: 2026-07-16T02:53:49+00:00 · risk: high
release: pending
extends: persona-learning-loop, dynamic-personas, scope-loop
relates-to: risk-proportional-ceremony, expectations-first, ceremony-to-effort, engine-output-trim

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a fitting persona selected (or drafted) BEFORE a milestone is shaped, framing intake through its lens; a milestone-scope `## Strategy` slot the persona fills with the optimized task DAG (freeze-first contracts · wave parallelism · first unblocking slice, tradeoffs named, SOFT like §5); the persona OWNS the gate report — its structure, emphasis, length and cadence (WHEN/HOW to seek the human) adapt per project, NOT a fixed section list; the report-template.md becomes persona-adaptive PRINCIPLES (what a gate must convey) rather than a required skeleton; **UDD redefined from UI-design into experience-driven development** — the pillar covers UI AND interaction/gate UX, its four design axes generalize to any experience surface (text/CLI included), and the persona-owned gate report is hosted as a UDD text-mode UX artifact designed through the UDD lens; a confidence-gated persona-framed discuss loop (interview-to-~95%); an advisor pressure-test trigger for a high-uncertainty milestone; a risk-proportional SKIP for micro/`--fast` scope.
Out: dissolving the ONE hard floor — security is always HARD-STOP, un-forceable (see Shared decisions: the strikeable carve-out); no engine auto-creation of milestones (the human confirm-before-create floor stays); the AI PROACTIVELY inventing milestones unprompted (deferred — this milestone shapes a request you raise); no change to the 6-phase task flow; no re-added per-turn ceremony/cost (personas REMOVE ceremony, never add it).

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): add-method/skill/add/report-template.md (the fixed section list → persona-adaptive principles) · SKILL.md (the report-template mandate line) · run.md (gate/verify presentation rules) · intake.md · scope.md · strategy.md (NEW) · MILESTONE.md.tmpl (the `## Strategy` slot) · docs/18-personas.md · agents/add-persona.md · add-advisor.md · add-method/tooling/add.py (new-milestone scaffold · persona apply-surface — NO engine gate on `## Strategy`)
Anchors: the report-template ARC + section list (what personas take over) · the persona schema (`flow:` · `## Abilities` · `## Anti-patterns`) · the per-task §5 build-strategy facets (Approach · Data · Pattern · Optimization) this milestone lifts to milestone scope · add-persona's selection/return contract · the four report floors — show-before-ask · one-approval-at-freeze · never-pre-stamp · security-HARD-STOP (first three become persona-owned; the last stays hard)
Honors (conventions): the run/entry invariants · NO re-added per-turn ceremony/cost (the engine-minimalism thread) · security is ALWAYS HARD-STOP · the engine records + the skill/persona drives (the engine never spawns, never auto-creates scope, never gates on `## Strategy`)
Issues/Risks (shared): retiring the fixed report-template is method-defining (risk: high) — three trust floors move from a hard template into persona JUDGMENT, so the persona contract must carry them explicitly or trust erodes; the persona-fit nudge is today PASSIVE ("confirm one fits") — bolting an active PM session on without a risk-proportional skip would re-add the very per-turn cost just removed; strategy stays SOFT so it never becomes a covert gate

## Shared decisions & glossary deltas   (living — every task must honor these)
- glossary: "strategy session" (the persona-led pre-milestone discuss→optimize loop) · "milestone strategy" (the `## Strategy` artifact) · "persona-owned gate" (a human gate whose report structure + cadence the fitting persona decides, not the fixed template)
- personas OWN the gate SURFACE and CADENCE — report structure, tone, emphasis, length, and WHEN/HOW to seek the human — adapted per project; there is NO required report-template section list
- three trust floors move into the persona CONTRACT (the persona must satisfy them in its own voice, not a fixed layout): show-before-ask · one-approval-at-the-freeze · never-pre-stamp-a-human-seam
- **STRIKEABLE CARVE-OUT — the one hard floor:** security is ALWAYS HARD-STOP, un-forceable — kept HARD against the "floors become persona judgment" choice because it is written into the method constitution (release readiness floor is un-`--force`-able) and the operating rules forbid authoring a security auto-pass. The human may strike this line to dissolve it too; until struck, it binds every task.
- the milestone strategy is SOFT (preferred plan); the loop/builder may deviate and records what it did — mirrors strategy-soft-not-hard for §5
- a persona is ADVISORY on direction: it frames + paces, the human still decides at whatever gate the persona surfaces
- UDD-redefine decisions (2026-07-16, user-chosen): (1) AXES — add a FIFTH axis INTERACTION (cadence · when/how to seek the human · turn-rhythm) alongside the four visual axes; the four originals stay (owner: udd-experience-pillar). (2) HOME — report-template.md FOLDS into the UDD doc family (rename/merge; re-point the 8 phase guides + ~14 tests) (owner: gate-experience-udd). (3) LOOP — the gate uses a LIGHTWEIGHT text-mode UDD variant (no wireframe/screen-capture beat; persona designs via the axes + a confirm) (owner: gate-experience-udd)

## Shared / risky contracts (freeze these first)
- the `## Strategy` section schema -> owning task strategy-section   (FROZEN @ v1 — every task cites its shape)
- the persona-owned-gate contract (what a persona must convey + the 3 in-contract floors + the security carve-out) -> owning task persona-owns-gates   (freeze BEFORE strategy-guide/intake cite it)
- the persona-at-intake apply contract (what add-persona returns for the intake surface) -> owning task persona-at-intake

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] persona-owns-gates      depends-on: none                                    — DONE (gate PASS): retired the fixed report-template section list; personas own gate structure + cadence; report-template.md is persona-adaptive PRINCIPLES carrying the four floors + the security carve-out. The contract the rest cites
- [ ] strategy-section        depends-on: none                                    — FROZEN @ v1: drafted-blank `## Strategy` slot in MILESTONE.md.tmpl; the persona records the optimized task plan here
- [x] udd-experience-pillar   depends-on: none                                    — DONE (gate PASS): design.md reframed experience-driven (a UI feature OR any human-facing experience surface — screen · interactive flow · human gate); the design-intake beat gained a FIFTH axis INTERACTION (cadence · seek · turn-rhythm); SKILL.md's trigger names experience surfaces; 3 trees byte-identical, SKILL.md 9490<9500. DESIGN.md.tmpl+glossary INTERACTION field deferred (§7 SPEC·open)
- [ ] gate-experience-udd     depends-on: udd-experience-pillar, persona-owns-gates — host the persona-owned gate report as a UDD text-mode UX artifact; the persona designs the gate experience through the UDD lens; report-template.md points up to UDD as its home
- [ ] persona-at-intake       depends-on: none                                    — extend add-persona selection + `persona:` routing to the intake/scope surface; intake.md/scope.md load the fitting persona before shaping
- [ ] strategy-guide          depends-on: strategy-section, persona-owns-gates, persona-at-intake — new strategy.md: the persona-framed discuss→optimize→converge PM loop to ~95% confidence, using the persona-owned gate
- [ ] advisor-strategy-trigger depends-on: strategy-guide                          — extend the add-advisor spawn trigger to refute a high-uncertainty milestone's strategy before commit
- [ ] risk-proportional-skip  depends-on: strategy-guide                          — the skip rule: micro / `--fast` bypasses the session; depth scales by risk/size (personas REMOVE ceremony for small work)

## Exit criteria (observable; map each to the task that delivers it)
- [x] Gate reports are persona-owned — structure + cadence adapt per project; no fixed template section list; the four floors are met in the persona's voice and security stays HARD-STOP  (← persona-owns-gates, DONE)
- [x] A MILESTONE.md carries a `## Strategy` slot the persona fills risk-proportionally               (← strategy-section, DONE 2026-07-23)
- [x] UDD is redefined as experience-driven development — the pillar (design.md + SKILL.md trigger + the FIVE axes incl. INTERACTION) covers UI AND interaction/gate UX  (← udd-experience-pillar, DONE)
- [x] The persona-owned gate report is a UDD text-mode UX artifact, designed through the UDD lens      (← gate-experience-udd, DONE 2026-07-23)
- [ ] Intake/scope loads a fitting persona (selected or drafted) before shaping the milestone          (← persona-at-intake)
- [ ] The strategy guide drives a persona-framed discuss loop that converges an optimized task DAG     (← strategy-guide)
- [ ] A high-uncertainty milestone can spawn the advisor to refute its strategy before commit          (← advisor-strategy-trigger)
- [ ] A micro / `--fast` milestone skips the session with zero added per-turn cost                     (← risk-proportional-skip)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides / report-template.md — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
