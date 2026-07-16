# MILESTONE: Thin engine, loop-in-SKILL, 6→3 phases

goal: A task runs read-SKILL→edit→freeze→gate with ≤3 add.py calls (from 5), loop driven by the SKILL, mechanical floor intact (verify: add-bench call census ≤3 median AND test_freeze_*/test_gate_*/test_audit_* stay green)
rationale: sub-milestone of the ceremony/token line (token-anatomy → call-residuals → engine-output-trim proved calls×context is the cost, calls dominate 3.3×); this is the CALL-COUNT collapse those milestones deferred — the flow itself thins: three phases, three engine calls, the loop narrated by the SKILL not the engine. Extends strategy-intake's inversion (personas route ceremony) down to the task lane.
stage: mvp · status: active · created: 2026-07-16T06:52:20+00:00
release: pending
extends: engine-output-trim, call-residuals, six-phase-loop
relates-to: strategy-intake, risk-proportional-ceremony, token-anatomy

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  collapse the task state machine 6→3 phases (`direction` = specify+plan+tests · `build` · `verify`) with the SAME two seams (one human freeze · one recorded gate); `freeze` compound-crosses direction→build and `gate` compound-crosses build→done so a task completes in ≤3 engine calls (`new-task` · `freeze` · `gate`); ONE TASK.md.tmpl (delete TASK.fast.md.tmpl — `--fast` renders the full template minus a `_FAST_SECTIONS` set, subset by construction) AND a lean-pass over the whole template family — MILESTONE.md.tmpl, personas/_template.md.tmpl, PROMPT.persona.md.tmpl — cutting instructional comment ceremony that re-enters context on every scaffold while keeping every machine-read line; the whole loop narrated inline in SKILL.md so phase guides become on-demand REFERENCE (7 phase files → 3), zero mandatory guide reads per ordinary task; the fitting persona PROPOSES each task's route + depth (full/fast/oneshot — all three lanes already exist; the persona replaces flag-recall · plus which reference guides load), recorded in the TASK header and RATIFIED by the human at the existing freeze — ceremony becomes persona-proposed, human-ratified, never engine-guessed; a usage-mined engine strike-list (dead/low-use subcommands + internal dedup) the human confirms at that task's freeze — minimal kernel, same performance.
Out: dissolving any floor (frozen §3 before build · red test before build · recorded gate · security HARD-STOP — all four bind every route); pillar REMOVAL beyond the confirmed strike-list (persona/component/release/graduate/book pillar retirement stays roadmap todo #35, human-owned); milestone/intake-level ceremony (strategy-intake owns the PM-session surface — risk-proportional-skip, persona-at-intake); the GEPA route-learning loop (queued follow-up milestone persona-gepa-loop — this milestone records route outcomes, it does not yet evolve rules from them); re-adding ANY per-turn output ceremony (engine-output-trim holds).

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): add-method/tooling/add.py — `cmd_advance` (l.1683) · `cmd_freeze` (l.1133) · `cmd_gate` (l.2207) · `cmd_new_task` (l.728) · the phase-enum/order constants + `cmd_phase`/`cmd_recross`/`cmd_heal` (tamper/heal path reads phase names) · `cmd_mine` (usage evidence for the strike-list) · add-method/tooling/templates/TASK.md.tmpl + TASK.fast.md.tmpl (delete) · add-method/skill/add/SKILL.md (9497/9500 ceiling) · phases/{0-setup,1-specify,3-plan,4-tests,5-build,6-verify,fast-lane}.md (7→3) · beyond.md · run.md (bundle/run seam text) · agents/add-design.md + add-build.md (phase-bundle columns rename)
Anchors: the `phase:` header marker in TASK.md (single source of truth, `add.py phase`) · the freeze snapshot (tests→build tamper tripwire — re-hashed at gate; the snapshot POINT moves with the collapsed cross) · `advance --fill` · the §5/§3 `Scope (may touch)` scope-lock · `_FAST_SECTIONS` (to create — the decided template-unify design) · `Persona (required)` line in §3 Build-strategy (the route hook extends it) · ENGINE_PKG_MD5 pin + SEAMS.md line refs (repin on every add.py edit)
Honors (conventions): run/entry invariants (bare python3 stdlib — the kernel gains NO dependency) · the engine records / the skill drives (engine never classifies, never spawns) · measure-not-block for new lints (route recording is audit-measured, never engine-blocked) · engine edits repin ENGINE_PKG_MD5 + SEAMS.md; doc/template edits do NOT · orchestration dedup fence (pool ≤ 41300) · SKILL.md ≤ 9500B (fund additions by compressing) · 3 git-tracked twin trees stay byte-identical (skill/agents/templates; todo #31 sync-twins is the propagation)
Issues/Risks (shared): 206 live + 267 archived task records carry 6-phase `phase:` values — the collapse NEEDS a back-compat read map (specify/plan/tests→direction) or status/audit break on every old task; the pinned-phrase census on phase names in engine tests is LONG (six-phase-loop lesson) — grep before rename, migrate value-pins forward; SKILL.md sits 3B under its ceiling — the loop-fold must FUND itself by deleting the phase table + beyond-index duplication; strategy-intake edits SKILL.md/fast-lane semantics in a sibling worktree — MERGE ORDER: strategy-intake lands first, this rebases (parallel-branch divergence is a recorded failure mode); `advance` deep-links guide filenames the fold renames (grep `phases/` across engine output); the .add/tooling dogfood twin is ALREADY diverged from canonical (md5 mismatch) — sync it as step 0 of the first engine task, never ground against it.

## Shared decisions & glossary deltas   (living — every task must honor these)
- glossary: "route" (a task's persona-proposed ceremony depth: `full | fast | oneshot` — the three existing lanes, plus which reference guides load) · "direction phase" (the collapsed specify+plan+tests span ending at the freeze) · "strike-list" (the named engine subcommands proposed for deletion, human-confirmed at a freeze — never a silent cut)
- THE INVERSION, task-lane form: ceremony is persona-PROPOSED, human-RATIFIED at the freeze (supersedes fast-lane.md's "ceremony is human-owned; the engine never guesses" — the engine STILL never guesses; the persona proposes, the ratifying human still owns it; zero new gates)
- the four floors bind EVERY route: frozen §3 before build · red test before build · exactly one recorded gate outcome · security is always HARD-STOP (strategy-intake's strikeable carve-out binds here too)
- ≤3 calls is the HAPPY PATH, not a cap — heal/re-cross/reopen calls on trouble are correct, never gamed away to hold a census number
- phase names are a READ-compatibility surface: old `phase:` values map forward on read; no bulk rewrite of archived task files
- engine minimal ≠ engine slow: the kernel stays stdlib-only, no new deps, startup and status latency may not regress (perf floor: `time add.py status --brief` no worse than baseline)
- WORDY-TEST REMOVAL AUTHORIZED (human, 2026-07-16): a test that pins prose/recipe WORDING rather than a floor may be DELETED outright instead of migrated (continues the 421b7ca de-ossification); tests that exercise freeze/gate/tamper/audit/scope FLOORS are never deleted or weakened — that distinction is reviewed at each task's freeze

## Shared / risky contracts (freeze these first)
- the 3-phase enum + compound-cross semantics (what `freeze` and `gate` each validate and cross) -> owning task phase-collapse-3 — every other task cites it
- the unified TASK.md.tmpl section→phase map + `_FAST_SECTIONS` set -> owning task template-unify
- the route header line (`route: full|fast|oneshot · routed-by: persona:<slug> — <why>`) -> owning task persona-routes-depth

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] phase-collapse-3      depends-on: none              — engine: 6→3 phase enum (direction·build·verify); freeze compound-crosses direction→build (snapshot point moves with it); gate compound-crosses build→done; back-compat read map for old phase values; repin
- [ ] template-unify        depends-on: phase-collapse-3  — ONE TASK.md.tmpl under 3 phase banners with inline exit gates; delete TASK.fast.md.tmpl; `--fast` = full minus `_FAST_SECTIONS` (subset by construction); lean-pass the whole template family (MILESTONE.md.tmpl · personas/_template.md.tmpl · PROMPT.persona.md.tmpl) — machine-read lines kept, comment ceremony cut
- [ ] skill-loop-fold       depends-on: phase-collapse-3, template-unify — SKILL.md narrates the whole 3-beat loop inline; phases/ 7→3 on-demand reference files (direction.md · build.md · verify.md; fast-lane absorbed into routing); zero mandatory guide reads on the ordinary path; ≤9500B
- [ ] persona-routes-depth  depends-on: template-unify    — the fitting persona proposes route+depth at new-task, recorded in the TASK header, ratified at the freeze; audit measures a missing route record (measure-not-block); fast-lane doctrine updated
- [ ] engine-kernel-trim    depends-on: phase-collapse-3  — usage-mined strike-list (mine/doctor evidence) + internal dedup; human confirms every strike at the freeze; stdlib-only, perf floor held; repin
- [ ] call-census-proof     depends-on: skill-loop-fold, persona-routes-depth, engine-kernel-trim — run the add-bench call census on a WM: median add.py calls ≤3, fidelity floor held; record the evidence in the ship review

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A task walks new-task → freeze → gate to done in exactly 3 engine calls; old 6-phase task records still read cleanly in status/audit  (verify: test_freeze_*/test_gate_* green + a 3-call walkthrough test)  (← phase-collapse-3)
- [ ] One TASK.md.tmpl serves both lanes; TASK.fast.md.tmpl is gone; a `--fast` scaffold is a strict subset of the full render; every template in the family measurably leaner with all machine-read lines intact  (verify: template render test + byte ledger)  (← template-unify)
- [ ] An ordinary task completes with ZERO phase-guide file reads — SKILL.md alone carries the loop; phases/ holds 3 reference files; SKILL.md ≤9500B  (verify: file census + byte assert)  (← skill-loop-fold)
- [ ] A new task's header records `route: … routed-by: persona:…` proposed before the freeze and ratified by it; all four floors hold on the fast route  (verify: audit lint test)  (← persona-routes-depth)
- [ ] add.py sheds every human-confirmed strike with the full engine suite green and `status --brief` latency not regressed  (verify: suite + timed run)  (← engine-kernel-trim)
- [ ] add-bench call census records median ≤3 add.py calls per task on a WM run with the fidelity floor held  (verify: bench census artifact)  (← call-census-proof)

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
- [ ] rebase onto feat/strategy-intake after it merges (merge order: strategy-intake first — shared SKILL.md surface)
- [ ] open the PR from the Close ship-review; human reviews + merges
- [ ] sync the 3 twin trees + `update --global` mirror (todo #32) · tag/publish per release.md (human-run)
