# MILESTONE: persona-led strategy session before a milestone is born

goal: Before a milestone is committed, the skill shapes it through a persona-led, risk-proportional strategy discussion that optimizes its task plan with the user.
rationale: bucket new-major — a method capability no active milestone's goal covers. Today intake.md classifies into a bucket and scope.md runs a GENERIC co-specify; neither loads a persona and neither optimizes the task decomposition (personas apply only at design/build/advisor/verify; strategy reasoning is per-task §5 only). Lift both to milestone scope.
stage: mvp · status: active · created: 2026-07-16T02:53:49+00:00
release: pending
extends: persona-learning-loop, dynamic-personas, scope-loop
relates-to: risk-proportional-ceremony, expectations-first

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a persona-led, risk-proportional strategy discussion at intake/scope — persona selected (or drafted) BEFORE shaping; a milestone-scope `## Strategy` slot (optimized task DAG · freeze-first contracts · wave parallelism · first unblocking slice, tradeoffs named, SOFT like §5); a confidence-gated discuss loop (interview-to-~95%); an advisor pressure-test trigger for a high-uncertainty milestone; a risk-proportional SKIP for micro/`--fast` scope.
Out: no new HARD gate (`## Strategy` is advisory — never lowers a gate); no engine auto-creation of milestones (the human confirm-before-create floor stays); the AI PROACTIVELY inventing milestones unprompted (deferred — this milestone shapes a request you raise, it does not originate scope); no change to the 6-phase task flow; no re-added per-turn ceremony/cost.

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): add-method/skill/add/intake.md · scope.md · strategy.md (NEW) · MILESTONE.md.tmpl · docs/18-personas.md · add-method/tooling/add.py (new-milestone scaffold · persona apply-surface · the `## Strategy` slot) · agents/add-persona.md · add-advisor.md
Anchors: the persona schema (`flow:` · `## Abilities` · `## Anti-patterns`) · the per-task §5 build-strategy facets (Approach · Data · Pattern · Optimization) this milestone lifts to milestone scope · the report-template.md ARC · add-persona's selection/return contract
Honors (conventions): the run/entry invariants · NO new HARD gate, NO re-added per-turn ceremony/cost (the engine-minimalism thread) · security is always HARD-STOP · the engine records + the skill drives (the engine never spawns, never auto-creates scope)
Issues/Risks (shared): the persona-fit nudge already fires at new-milestone but is PASSIVE ("confirm one fits") — the trap is bolting an active session on top without a risk-proportional skip, which would re-add the very per-turn cost just removed; strategy must stay SOFT so it never becomes a covert gate

## Shared decisions & glossary deltas   (living — every task must honor these)
- new glossary term "strategy session" (the persona-led pre-milestone discuss→optimize loop) and "milestone strategy" (the `## Strategy` artifact)
- the milestone strategy is SOFT (preferred plan); the loop/builder may deviate and records what it actually did — mirrors strategy-soft-not-hard for §5
- a persona at intake is ADVISORY: it frames the discussion, never lowers or relaxes a gate (the persona floor, same as design/build)

## Shared / risky contracts (freeze these first)
- the `## Strategy` section schema -> owning task strategy-section   (every other task cites its shape)
- the persona-at-intake apply contract (what add-persona returns for the intake surface) -> owning task persona-at-intake

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] strategy-section       depends-on: none                              — add a drafted-blank `## Strategy` slot to MILESTONE.md.tmpl + engine section handling; the schema the rest cites
- [ ] persona-at-intake      depends-on: none                              — extend add-persona selection + `persona:` routing to the intake/scope surface; intake.md/scope.md load the fitting persona
- [ ] strategy-guide         depends-on: strategy-section, persona-at-intake — new strategy.md driving the persona-framed discuss→optimize→converge loop to ~95% confidence
- [ ] advisor-strategy-trigger depends-on: strategy-guide                   — extend the add-advisor spawn trigger to refute a high-uncertainty milestone's strategy before commit
- [ ] risk-proportional-skip depends-on: strategy-guide                     — the skip rule: micro / `--fast` bypasses the session; depth scales by risk/size (no added ceremony for small work)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A MILESTONE.md carries a `## Strategy` slot, drafted-blank, filled risk-proportionally        (← strategy-section)
- [ ] Intake/scope loads a fitting persona (selected or drafted) before shaping the milestone        (← persona-at-intake)
- [ ] The strategy guide drives a persona-framed discuss loop that converges an optimized task DAG   (← strategy-guide)
- [ ] A high-uncertainty milestone can spawn the advisor to refute its strategy before commit        (← advisor-strategy-trigger)
- [ ] A micro / `--fast` milestone skips the session with zero added per-turn cost                   (← risk-proportional-skip)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
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
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
