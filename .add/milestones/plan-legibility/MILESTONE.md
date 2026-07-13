# MILESTONE: Plan legibility — surface the build plan at the freeze + structured task relations

goal: Make the plan and its relationships legible to the human: the freeze report surfaces the full §3 build-strategy plan-of-action (approve HOW, not just WHAT), and every task carries a structured, synced Relations surface (depends-on · extends · relates-to) at task and milestone altitude, with a validate/sync guard.
rationale: sub-milestone (human-confirmed 2026-07-13) — a legibility follow-on to expectations-first: the plan phase now unifies ground+contract+build-strategy, but the AI's build plan-of-action is NOT surfaced at the one freeze (the human approves WHAT, not HOW), and task relations are scattered (milestone `depends-on`, §3 Related-intent, SEAMS pointers) with no sync. Sequenced BEFORE expectations-first's T4 (book-align), per the human.
stage: mvp · status: active · created: 2026-07-13T05:13:25+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (A) the DECIDE/freeze report (`decide_data`/`render_decide`) + `report-template.md` surface the FULL §3 Build-strategy plan-of-action — ordered batches · Scope (may touch) · approach · persona · spawn isolation — so the human approves HOW the AI will build, at the existing freeze. (B) a structured Relations surface per task — `depends-on · extends · relates-to` — at task AND milestone altitude, surfaced at `status`/plan, with a validate/sync guard (like the backlink guards) that flags a stale/dangling relation.
Out: NO new approval gate — surface within the EXISTING one freeze (the plan freeze stays the only approval). NO auto-inference of relations — the AI/human declares; the guard validates, never invents edges. expectations-first's T4 (book-align: deep Contract→Plan narrative + GLOSSARY term) — separate, after. Deep book-narrative chapters for these surfaces — light guide/report/template updates only.

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): `add.py:decide_data` (~6077) + `render_decide` (~6124) + `_decide_next*` — the task-level DECIDE/freeze report facts + render (surfaces `judgment` from §6/§1/§3 markers + `deps`, but NOT the §3 Build-strategy) · `report-template.md` (skill ×3) — the ONE human-gate report shape (PLAN/SHAPE/SUMMARY/…) · `add.py:_parse_deps` (~729) + state `depends_on` key (~824) + status/ready deps render (~2812/4369/4388) + advisory SHA-freshness deps check (~2622) · §3 Build-strategy sub-block via `_raw_phase_bodies`/`_contract_frozen` · MILESTONE.md task-list `depends-on:` parser · TASK.md.tmpl §3 (Build-strategy + Related-intent line).
Anchors: `decide_data`/`render_decide`/`_decide_next_pair` · `_parse_deps`/`depends_on` · `_raw_phase_bodies`/`_contract_frozen` · report-template.md sections · MILESTONE.md `depends-on:` parser · `_task_done`.
Honors (conventions): report-template.md is the ONE human-gate report shape (show-before-ask · never pre-stamp) · the freeze is the ONE approval (surface, don't add a gate) · `decide_data` is PURE + frozen-shape (extend without breaking the digest) · 3-tree skill parity · engine-pin re-aim (ENGINE_MD5 + ENGINE_PKG_MD5) · byte-budget pools · state.json schema-migration tolerance (old tasks lack new keys) · relations are DECLARED not inferred.
Issues/Risks (shared): `decide_data`/`render_decide` are PURE + pinned-shape — Task A must extend them without breaking the engine digest · the §3 Build-strategy body is SOFT free-text — extraction must be robust (phase-body-extraction seam: line-start `##`/bare `---`) · adding `extends`/`relates_to` to state needs a migration-tolerant read (old tasks lack the keys, like `depends_on` defaults) · a sync guard too strict false-flags — make it ADVISORY (mirror the SHA-freshness deps check at ~2622, never writes/blocks) · byte budgets bind report-template.md + the guides.

> Gather this ONCE per milestone (the drafting step in `scope.md`). Each task's `specify`
> PROJECTS its §1 expectations from here + the specific request — light, not re-grounded per task.

## Shared decisions & glossary deltas   (living — every task must honor these)
- The freeze stays the ONE approval — both tasks SURFACE within it (report/status), never add a gate.
- Relations vocabulary (GLOSSARY delta, task B): `depends-on` (blocks) · `extends` (builds on a prior task's shipped surface) · `relates-to` (shares context, non-blocking). Declared, not inferred.
- Any state.json read of a new key defaults for old tasks (migration-tolerant) — mirror `depends_on`.

## Shared / risky contracts (freeze these first)
- `decide_data`/`render_decide` shape (Task A extends the frozen digest) -> owning task plan-in-report
- state `relations` schema (`extends`/`relates_to` keys) -> owning task relations-surface

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] plan-in-report     depends-on: none   — surface the FULL §3 Build-strategy plan-of-action (batches · scope · persona · spawn) in the DECIDE/freeze report (`decide_data`+`render_decide`) + `report-template.md`, so the human approves HOW at the freeze.
- [x] relations-surface  depends-on: none   — structured Relations (`depends-on · extends · relates-to`) per task + milestone, surfaced at `status`/plan, with an advisory validate/sync guard for stale/dangling edges.

## Exit criteria (observable; map each to the task that delivers it)
- [x] At the freeze, the human sees the AI's FULL build-strategy plan-of-action (ordered batches + scope + persona/spawn) in the report — not just the contract shape        (← plan-in-report)
- [x] Each task declares `depends-on · extends · relates-to` (task + milestone altitude), surfaced at `status`/plan                                                          (← relations-surface)
- [x] A validate/sync pass FLAGS a stale or dangling relation (advisory), keeping cross-task/cross-milestone relations current                                              (← relations-surface)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `decide_data`/`render_decide` now emit a BUILD PLAN block (§3 build-strategy fields) at the front/pre-freeze seam (`_build_plan`, single-physical-line capture); state gains migration-tolerant `extends`/`relates_to` task keys + `_task_relations`/`_milestone_relations` readers + the PURE `_relations_health` guard; `cmd_status` shows `ext=`/`rel=`/`relations: N dangling · M self`; `cmd_check` resolves+flags dangling/self; templates: GLOSSARY (3 relation terms), TASK.md.tmpl (autonomy-header relations note, net-compressed under the frozen lean ceilings), MILESTONE.md.tmpl (`relations:` header). ENGINE_MD5 re-pinned; SEAMS `_declared_scope` anchor re-pinned.
- skill   : `report-template.md` (×3 twins) gains the "BUILD PLAN is the HOW" bullet — the freeze report surfaces HOW, not just WHAT.
- book    : untouched (deep Contract→Plan narrative + GLOSSARY term is expectations-first's T4 book-align, explicitly deferred — Out of scope).

### Cross-task evidence   (one row per task)
- plan-in-report    : gate=PASS · tests=27 green (test_decide_digest incl. the dogfood field-bleed regression) · residue=none (`331306b`)
- relations-surface : gate=PASS · tests=15 green (test_relations) · full suite 3441 green · residue=none (`ed48dc5`); a mis-declared frozen §5 scope was corrected + human-signed re-crossed (Tin Dang), §3 stayed frozen.

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
  - EC1 (freeze shows the FULL build plan) ← plan-in-report: `render_decide` BUILD PLAN block + report-template "BUILD PLAN is the HOW" bullet (`331306b`).
  - EC2 (task+milestone declare depends-on·extends·relates-to, surfaced) ← relations-surface: new-task flags + state keys + `status` ext=/rel= + MILESTONE.md header (`ed48dc5`).
  - EC3 (advisory pass FLAGS stale/dangling) ← relations-surface: `_relations_health` + `cmd_check` dangling/self findings, PURE, never blocks (`ed48dc5`).
- goal: plan + relationships are legible to the human — the freeze report now surfaces the AI's full build-strategy plan-of-action (approve HOW), and every task/milestone carries a declared, status-surfaced, guard-validated Relations surface. Proof: EC1–EC3 each map to a PASS'd task; full suite 3441 green.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] push branch `feat/flow-reorder` and open a PR (commits `331306b` + `ed48dc5`); PR body = this Close ship-review; human reviews + merges (needs push auth).
- [ ] this milestone is a method/engine change, not a package cut — DEFER the release (version bump / npm / PyPI) to a later release scope that bundles it with sibling flow-reorder milestones (per release.md).
- [ ] no tag/publish for this milestone alone.
