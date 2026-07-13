# MILESTONE: Expectations-first flow: plan phase

goal: Reorder the task flow to expectations-first — specify/scenarios become light projections of a milestone-level Ground (gathered once) + the request; grounding, the frozen contract, and build strategy unify into one 'plan' phase carrying the single human freeze. Fewer stops, no re-grounding per task, grounding floor preserved.
rationale: sub-milestone (method redesign of the core lifecycle). Origin: human analysis 2026-07-12 — the current `ground → specify` order is inverted (grounding serves the HOW, not the WHAT; the WHAT flows down from the milestone). Replaces the abandoned `plan-phase-merge` branch, which only merged ground→specify and mis-modelled where grounding belongs.
stage: mvp · status: active · created: 2026-07-12T08:16:14+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`.

## Scope
In:  The task lifecycle is reordered and one phase is collapsed. New work order:
     `specify → scenarios → plan → tests → build → verify → observe → done`.
     - `specify` / `scenarios` (the WHAT / expectations) become LIGHT: projected from
       the milestone-level Ground + the specific request, not re-invented per task.
     - The old `ground` and `contract` phases COLLAPSE into one new `plan` phase (the
       change plan = real-code grounding + the frozen contract + the build strategy).
       The single human freeze moves to `plan`. Contract stays HARD; build-strategy stays
       SOFT (preferred, self-improvable) inside the same plan artifact.
     - A milestone gains a `## Ground` (shared real-code context gathered ONCE) that seeds
       every task's expectations — the speed win: no re-grounding shared context per task.
     Surfaces: engine (constants.py PHASES/groups/owners/agents/guides + add.py phase/advance/
     freeze/seams/footers/migration), templates ×3 trees, phase guides ×3 trees, SKILL.md ×3,
     book chapters + GLOSSARY. Grounding floor preserved (the contract may cite only anchors
     named in the plan's grounding sub-block). Legacy `ground`/`contract` task states still load.
Out: No change to tests/build/verify/observe SEMANTICS (only their §-numbers shift). No new
     human gates (still ONE freeze). No milestone-ground ENGINE enforcement beyond a template
     section + guide wording (a heavy milestone-ground validator is deferred). No release/
     graduate/component flow changes. No benchmark re-measure (separate milestone).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Phase names** (confirmed at milestone gate 2026-07-12): the collapsed phase is `plan`;
  `specify`/`scenarios` keep their names but are reframed as "expectations". GLOSSARY `ground:`
  and `contract:` terms fold into a `plan:` term (grounding + contract + build-strategy).
- **The freeze** moves from `contract` to `plan`: entering `tests` requires §3 PLAN FROZEN
  (the least-sure flag + human approval live there now).
- **Grounding floor is invariant**: the frozen contract may cite ONLY anchors named in the
  plan's `### Grounding` sub-block — carried verbatim from the current ground floor.
- **DIRECTION bundle** = `specify, scenarios, plan, tests` (was ground/specify/scenarios/contract/tests).

## Shared / risky contracts (freeze these first)
- The `PHASES` tuple + freeze-phase + template §-map -> owning task **plan-phase-core** (T1);
  every other task consumes it. Freeze T1 before T2–T4 build.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] plan-phase-core        depends-on: none              — engine + templates ×3: reorder, collapse ground+contract→plan, move freeze to plan, migrate legacy states + tests
- [x] milestone-ground-seed  depends-on: plan-phase-core   — MILESTONE.md `## Ground`; specify projects expectations from milestone Ground + request (light)
- [x] guides-and-skill       depends-on: milestone-ground-seed — phase guides ×3 + SKILL.md realign to the expectations-first flow; retire 0-ground/3-contract into the plan guide
- [x] book-plan-align        depends-on: guides-and-skill  — book GLOSSARY plan term + diagram source; no stale ground-first/contract-phase prose (slug `book-plan-align`; `book-align` was taken by a done v12 task)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py` phase order is `specify, scenarios, plan, tests, build, verify, observe, done`; `ground`/`contract` are gone as phases — pinned by test   (← plan-phase-core)
- [x] entering `tests` requires §3 PLAN FROZEN; a bare/unflagged plan freeze is refused — pinned by test   (← plan-phase-core)
- [x] templates render §3 PLAN with `Grounding`/`Contract`/`Build-strategy` sub-blocks; the contract-cites-only-grounded-anchors floor still binds — pinned by test   (← plan-phase-core)
- [x] a task file left at legacy phase `ground` or `contract` still loads (migrates to `specify`/`plan`) — pinned by test   (← plan-phase-core)
- [x] `MILESTONE.md` carries a `## Ground`; a fresh task's `specify` guide + template cue projecting from it — pinned by test/render   (← milestone-ground-seed)
- [x] phase guides ×3 + `SKILL.md` describe the 7-work-phase expectations-first flow with no stale `ground`-first / `contract`-phase references — pinned by grep-test   (← guides-and-skill)
- [x] book ch02 + GLOSSARY name the plan phase and expectations-first order; diagram updated — pinned by grep-test   (← book-plan-align)
- [x] full suite green; ENGINE_MD5/ENGINE_PKG_MD5 re-pinned; ×3 tree byte-parity holds   (← all)

## Close — ship review   (AI fills when every task is done)
### Ship by domain
- tooling : `PHASES` reordered to specify→scenarios→plan→tests→build→verify→observe→done (ground/contract retired as phases); the freeze moved to plan→tests; §3 PLAN template (×4 twins) renders Grounding/Contract/Build-strategy sub-blocks; legacy `ground`/`contract` task states migrate to `specify`/`plan`; MILESTONE.md gains `## Ground` that a task's specify projects from. ENGINE_MD5 progressed 33f46b7d→…→9311ec35; ENGINE_PKG_MD5→28212a55 (chapter-path constant).
- skill   : `phases/3-plan.md` unifies the retired `0-ground.md` + `3-contract.md`; SKILL.md phase table + flow prose read the 7-work-phase order; dangling refs healed across scope/run/components/fast-lane guides.
- book    : ch02 flow + mermaid + CHECKLIST aligned (T3); the GLOSSARY now defines **Plan** + redefines **Ground** as Plan's first part + a **Contract** "within Plan" nod; appendix-g + the diagram render-source read "Plan"; a stale-prose grep-guard pins it. The add-flow.png RASTER regen is a flagged human visual-gate step.
### Cross-task evidence   (one row per task)
- plan-phase-core     : gate=PASS · tests=full suite green @ close · residue=none (`a8e179a`+`58d9d8e`+`cee79a0`)
- milestone-ground-seed : gate=PASS · tests=green · residue=none (`436d377`)
- guides-and-skill    : gate=PASS · tests=green · residue=book-narrative deferred to T4 (now closed) (`6b62f80`)
- book-plan-align     : gate=PASS · tests=3446 green · residue=add-flow.png raster = human visual-gate release step (`1f4d0fb`)
### Goal met?
- [x] each Exit criterion satisfied by a Cross-task evidence row or Ship-by-domain change (cite which)
  - EC1–EC4 ← plan-phase-core (PHASES order · plan-freeze gate · §3 sub-block template · legacy-state migration), all test-pinned.
  - EC5 ← milestone-ground-seed (MILESTONE.md `## Ground` + specify projection).
  - EC6 ← guides-and-skill (guides ×3 + SKILL.md, grep-pinned).
  - EC7 ← book-plan-align (book GLOSSARY names Plan + expectations-first order; diagram source updated; grep-pinned).
  - EC8 ← all (full suite 3446 green; ENGINE_MD5 9311ec35 / PKG 28212a55 re-pinned; ×3/×4 tree byte-parity green).
- goal: the flow now collapses ground+contract into ONE plan phase with a single freeze — fewer stops (8→7 work phases, one approval), no per-task re-grounding (specify projects from the milestone `## Ground`), and every trust floor preserved (frozen contract · red-before-green · verify gate all still bind). Evidence: EC1–EC8 each map to a PASS'd task; suite 3446 green.

## Release steps   (AI-DEFINED — human gate)
- [ ] rebase onto main once quality-floors PR #144 merges (this branch stacks on it)
- [ ] open a PR from the Close ship-review; human reviews + merges
- [ ] (release cut bundled separately per release.md)
