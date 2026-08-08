# MILESTONE: Persona template completeness

goal: The persona template is one coherent artifact: the guidance names four legs with a bar each, the book cites no retired file and describes the load set the surfaces actually read, three planner personas exist at task/milestone/release altitude, and the 12 orphaned preset templates stop shipping. (AMENDED mid-milestone: the original goal said "all 12 presets carry ORIENT + a per-flow stance + an Escalation section" — grounding that task showed the presets have no consumer, so the honest outcome is retirement, not a fold. Recorded rather than quietly rewritten.)
rationale: bucket `new-major` — a distinct theme no active milestone's goal covers (`lock-reclaim-hardening` is 1/1 done and unrelated), and four tasks wide. A research pass over the whole persona surface found the template is three disagreeing artifacts: the guidance (`persona-author/references/`) is two folds ahead of the 12 preset `.tmpl` files people actually copy, `## Abilities` is authored by every real persona and loaded by no apply surface, and `18-personas.md` still points at a `_template.md.tmpl` that no longer exists.
stage: mvp · status: active · created: 2026-07-25T07:45:40+00:00
relations: relates-to: persona-domain-fit, dynamic-personas, persona-learning-loop

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/PLAN.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the persona authoring guidance (`persona-author/references/contract.md` + `patterns.md`); the 12 preset persona templates; three new planner personas under `.add/personas/`; the persona chapter `18-personas.md`. All mirror trees for each.
Out: the engine schema itself (`constants.PERSONA_REQUIRED_SECTIONS` stays 4-section, presence-based); any `add_engine/*` edit — including the stale `_template.md` mention in `io_state.py:273`, which would force an `ENGINE_PKG_MD5` repin for zero behavior gain (filed as an `add` delta instead); renaming existing sections to literal Role/Process/Standards/Rules (breaks 6 personas, 12 presets, the engine constant, the book, and benchmark fixtures for no behavior change).

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols):
- guidance ×3 skill trees: `.claude/skills/add/persona-author/` · `add-method/skill/add/persona-author/` · `add-method/src/add_method/_bundled/skill/add/persona-author/` (each holds `SKILL.md`, `references/{contract,patterns,seeding}.md`, `assets/example-{,design-}persona.md`)
- presets: RETIRED at `preset-patterns-fold`. The templates tree is FOUR-way, not three — `add-method/tooling/` · `.add/tooling/` · `add-method/src/add_method/_bundled/tooling/` · `add-method/.add/tooling/` (the dogfood install inside add-method/). The original three-way note here was wrong and the full-suite floor caught the partial deletion.
- roster: `.add/personas/*.md` (6 real personas today)
- book ×2 twins: `18-personas.md` · `add-method/docs/18-personas.md`

Anchors (the floor each task's contract builds on):
- `add_engine/constants.py` — `PERSONA_FRONTMATTER_KEYS` (name, vibe) · `PERSONA_REQUIRED_SECTIONS` (Identity, Critical Rules, Default Requirement, Success Metrics) · `PERSONA_FLOW_VALUES` (design, build, advisor, verify) · `TASK_KINDS`
- `add_engine/predicates.py` — `_persona_missing` (presence-based) · `_persona_quality_warnings` (flow typo · task-kind typo · bare `<…>` placeholder)
- `add_engine/constants.py:287` — `_PERSONA_TAG_RE` parses the delta persona/section hint permissively, BUT the routing gate is the CLOSED hint vocabulary documented in `deltas.md`; `add.py` never edits a persona, so the fold is human/AI transcription. (CORRECTED during persona-docs-truth: the original note said "free text, validated against no closed set", which is true of the parse and wrong about the gate.)

Honors (conventions):
- ADD invariant: a persona never lowers a gate; a security finding is always HARD-STOP.
- NO-EXEC: the engine never reads a persona on a build path; selection/loading is the agent's judgment.
- Mirror discipline: every skill tree and every tooling-template tree stays byte-identical (the CI mirror-gap meta-test fails the publish otherwise).
- Guidance edits stay outside `ADD:BEGIN/END` managed blocks; a hand-edit inside one is eaten by `sync-guidelines`.

Issues/Risks (shared):
- **Pin blast radius is nil, and that is load-bearing.** `engine_manifest.package_files` walks `add_engine/*.py` only; `ENGINE_MD5` is `md5(add.py)`. Templates and skills are NOT pinned — no repin in this milestone. Any task that finds itself editing `add.py`/`add_engine/*` has left scope.
- **Near-duplicate risk on the roster.** `milestone-planner` sits adjacent to the existing `method-product-owner`. The agreed boundary: the owner keeps *sizing and exit criteria*; a planner owns *ordering, dependencies, and sequencing risk* at its altitude. If that line cannot be drawn cleanly, surface it — do not ship a near-twin (the persona-author skill's own rule: prefer select, then fold, then author).
- 36 preset files across 3 trees move in one task. Originally the risk was a hand-edited divergence shipping in the next wheel; after the repurpose the risk inverts — a PARTIAL deletion is the divergence, and `test_tree_parity`'s dynamic `templates/**/*.tmpl` glob is what catches it.

> Gathered ONCE per milestone (`scope.md`); each task's specify PROJECTS its §1 from
> here + the specific request — light, never re-grounded per task.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **The four legs** name existing sections; they never rename them. Role=`## Identity` · Rules=`## Critical Rules` · Standards=`## Default Requirement` + `## Success Metrics` · Process=`## Abilities` + `## Playbook`.
- **`## Abilities` is kept, not cut** — and the apply-surface load contract in `18-personas.md` is corrected to include it, so ORIENT-first and design-for-failure reach a surface that reads them.
- **`## Escalation` is OPTIONAL and routable** — documented in `contract.md`, named in the book's routable-section list, and added to the `deltas.md` hint vocabulary (which is what actually makes it routable). No engine change. It is NOT written into the presets: those are being retired, not folded.
- **Presence-based stays presence-based.** Nothing in this milestone promotes a section to engine-REQUIRED; quality remains the author's concern (measure-not-block).

## Shared / risky contracts (freeze these first)
- the four-leg vocabulary + the `## Escalation` section definition -> owning task `persona-template-legs` (tasks 2–4 all consume it)

## Tasks (breadth-first decomposition; detail lives in each PLAN.md)
- [x] persona-template-legs    depends-on: none                    — `contract.md` + `patterns.md` ×3 trees: name the four legs with a quality bar each (Process has none today), correct the Abilities load contract, define `## Escalation` OPTIONAL + routable.
- [x] persona-docs-truth       depends-on: persona-template-legs   — `18-personas.md` ×2 twins: retire the dead `_template.md.tmpl` claim, add Abilities to the build-overlay load set, name Escalation among the routable growth sections. Runs SECOND by human decision at the task-1 freeze: it is the task that proves `## Abilities` actually reaches an apply-surface, so the 36-file preset fold is not written on an unproven assumption.
- [x] preset-patterns-fold     depends-on: persona-docs-truth      — REPURPOSED at direction (no freeze had happened): **retire** the 12 preset templates from all 3 tooling trees. Grounding the fold showed the presets have NO consumer — `SETUP_FILES` has no persona entry, `cmd_init` creates `.add/personas/` empty, and `git log` on the dir ends at `e29ddac4` ("retire the static persona template"), which deleted `_template.md.tmpl` and left these 12 orphaned. Folding them would author ~48 sections into files nothing loads. Slug kept — the engine keys on it and there is no retitle verb.
- [x] planner-personas-seed    depends-on: persona-template-legs   — three planner personas (task · milestone · release altitude) authored against the new template, boundaries disjoint from `method-product-owner`.

## Exit criteria (observable; map each to the task that delivers it)
- [x] An author reading `contract.md` finds all four legs named with a quality bar each, and `## Escalation` documented as OPTIONAL + routable        (← persona-template-legs)  (verify: `contract.md` shows 4 leg rows each carrying a bar line, and 1 `## Escalation` OPTIONAL entry naming its routability)
- [x] The orphaned preset templates no longer ship — 11 removed from all FOUR tooling trees and the strongest one promoted into the skill's worked examples, with nothing depending on them        (← preset-patterns-fold)  (verify: 0 files match `templates/personas/*.tmpl` in any of the 4 tooling trees; FULL tooling suite green 0 failed; fresh `add.py init` still scaffolds an empty `.add/personas/`)
- [x] Three planner personas are selectable at task, milestone, and release altitude, each with a `not-when` that names `method-product-owner` for the sizing near-miss        (← planner-personas-seed)  (verify: `add.py check` reports 9 schema-conformant personas and 0 persona findings, and the `add.py status` roster line lists all three)
- [x] A reader of `18-personas.md` is sent to no file that does not exist, and the build-overlay load set it describes matches what the surfaces actually read        (← persona-docs-truth)  (verify: every path cited in `18-personas.md` resolves on disk, and its overlay list matches the sections named in `design.md` + `phases/verify.md`)
- [x] Every mirror tree is byte-identical — 3 skill trees, 3 tooling-template trees, 2 book twins        (← preset-patterns-fold · persona-docs-truth)  (verify: `python3 -m unittest test_tree_parity test_ci_tooling_mirror_gap test_bundle_parity` green, 0 failed)

## Strategy   (AI-drafted WITH the human — the optimized task plan; SOFT/advisory like a task's Build-strategy; drafted-blank for a micro/--tiny milestone)
> The persona-led strategy over THIS milestone's tasks — sequencing, freeze-first contracts,
> parallel waves, the first unblocking slice, tradeoffs named. SOFT: the preferred plan; the
> loop may deviate and records what it did. Drafted-blank is valid (risk-proportional).
- Approach (sequencing): risk-first, revised at the task-1 freeze. `persona-template-legs` still goes first — three tasks read its vocabulary, and freezing it stops each from inventing its own wording and needing a re-cross to reconcile. But `persona-docs-truth` was promoted to SECOND (human decision at the freeze gate): the milestone's largest assumption is that `## Abilities` should be kept and surfaced, and the book task is the one that proves it reaches an apply-surface. Paying 2 files to de-risk 36 is the right trade.
- Freeze-first: the four-leg vocabulary + the `## Escalation` definition (task 1's §3).
- Waves (parallel): task 1 alone → `persona-docs-truth` (the assumption check) → then `preset-patterns-fold` · `planner-personas-seed` may run concurrently, touching disjoint trees (tooling templates vs `.add/personas/`). Sequential is the default here; the wave is available only if wall-clock matters.
- Tradeoffs weighed: (a) *planners first, template second* — would give the template polish real authoring evidence, but forces authoring against a template known to be wrong and a likely rewrite of all three personas; rejected. (b) *collapse tasks 1+4 into one prose task* — fewer freeze gates, but mixes skill-tree and doc-twin mirroring in one scope, and the book edit genuinely depends on the vocabulary the guidance settles; rejected. (c) *one planner instead of three* — my own recommendation on roster-overlap grounds; the human chose three altitudes, so the boundary test moves into `planner-personas-seed`'s exit criterion rather than being decided by fiat. (d) *presets before the book* — the original plan; superseded at the freeze because it spends the 36-file edit before the Abilities bet is confirmed.

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Cross-task review the AI fills — the evidence behind the EXISTING milestone-done gate, NOT a new approval.

### Ship by domain   (what changed, per bounded context)
- tooling : 12 preset persona templates RETIRED from all four templates trees (2 git-tracked = 24 deletions; `.add/tooling/` and `add-method/.add/tooling/` are gitignored dogfood installs, removed on disk). One stale docstring line in `test_persona_task_kinds.py`. NO `add.py`/`add_engine/*` edit; ENGINE_MD5 and ENGINE_PKG_MD5 unchanged all milestone.
- skill   : `persona-author/references/contract.md` (four legs + bars, Abilities load contract, `## Escalation`), `patterns.md` (pattern 11 Escalation stance, leg-tagged Contents), `deltas.md` (hint vocabulary gains `escalation`), `SKILL.md` (third worked example), and the new `assets/example-architect-persona.md` — all × 3 skill trees, byte-identical.
- book    : `18-personas.md` × 2 twins — dead `_template.md.tmpl` pointer retired, build-overlay load set corrected to match `agents/add-worker.md` §2, "the engine routes a delta" corrected to "the engine never edits a persona", Escalation named among the growable sections.
- roster  : `.add/personas/` 6 → 9 — `task-planner`, `milestone-planner`, `release-planner`; `method-product-owner` folded (frontmatter only) to make the ordering boundary real.

### Cross-task evidence   (one row per task)
- persona-template-legs   : gate=PASS · 8/8 acceptance checks · test_tree_parity + test_ci_tooling_mirror_gap 15 tests OK · add.py check 298/0 · residue=one forward-pointing parenthetical, removed by the next task
- persona-docs-truth      : gate=PASS · 9/9 acceptance checks · +test_fold_persona_sections, 17 tests OK · add.py check 303/0 · residue=none
- planner-personas-seed   : gate=PASS · 8/8 acceptance checks · roster 9 schema-conformant, 0 findings, use-when disjoint across all 6 pairs · add.py check 308/0 · residue=boundary proven at prose level only, filed as a delta
- preset-patterns-fold    : gate=PASS · 10/10 acceptance checks · FULL suite 2316 tests OK (after catching a partial 4-way deletion) · wheel + npm tarball rebuilt and inspected clean · add.py check 313/0 · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
      1 four legs + Escalation -> persona-template-legs row (8/8 checks) · 2 presets retired -> preset-patterns-fold row (10/10, packages verified) · 3 three planners -> planner-personas-seed row (9 conformant, disjoint) · 4 book cites nothing dead -> persona-docs-truth row (9/9) · 5 mirrors byte-identical -> the parity tests in rows 1, 2 and 4.
- goal: the persona template is one coherent artifact — the guidance names four legs with a bar each, the book describes the load set the surfaces actually read, three planners cover task/milestone/release altitude, and the orphaned presets no longer ship. The single strongest evidence line: a rebuilt wheel and npm tarball both report `templates/personas=0` and `_template.md.tmpl=0` while carrying the promoted `example-architect-persona.md` and an intact 259-entry teacher corpus — the retirement is real in what users receive, not just in the repo.

NOTE ON THE GOAL AS ORIGINALLY WRITTEN: it promised "all 12 presets carry ORIENT + a per-flow stance + an Escalation section". Grounding that task showed the presets had no consumer, so the goal was AMENDED mid-milestone to retirement (recorded in the goal line and the task line, not quietly rewritten). Three of the milestone's most valuable findings came from checks refusing to pass rather than from planning: the 4-way templates tree, the wheel still shipping the file `e29ddac4` retired, and `## Abilities` already being read by `add-worker` all the while.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> AI-written steps for THIS milestone (hints, not engine commands); MERGE is one small step; the human runs the cut.
- [ ] run the full tooling suite + `add.py check` — 0 failed, 0 persona findings
- [ ] open a PR from the Close ship-review above; the human reviews + merges
- [ ] no version bump or publish required on its own — this milestone rides the next release cut (guidance/template/doc only, no engine pin moved)
