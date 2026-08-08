# MILESTONE: Multi-active state model + migration (team-collaboration foundation)

goal: ADD's engine tracks N truly-parallel active milestones — state.json holds a SET of active milestones, each with its own active task — with a backward-compatible migration from the single-active schema and the ENGINE_MD5 pin deliberately re-established.
rationale: new-major **team-collaboration** (git-native, multi-user, N parallel-active milestones — confirmed intake 2026-06-22). This is milestone 1 of that major: the engine-state foundation every later slice (user-identity · ownership-assignment · git-merge-safety · multi-active-UX) depends on. Relationship to the map: EXTENDS the v4-1 machine-state-json line (it reshapes the same state.json) and is a PREREQUISITE for the rest of the team-collaboration siblings; OVERLAPS nothing live (no active milestone's goal covers parallel activation). The rare major that intentionally edits the byte-pinned engine — so it carries risk:high + lowered autonomy.
stage: mvp · status: active · created: 2026-06-22

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A multi-active state.json schema — `active_milestones` (a SET/list) replacing the scalar
     `active_milestone`, and a per-milestone `active_task` replacing the single global `active_task`.
     A forward, idempotent, fail-soft MIGRATION that upgrades any existing single-active state
     (the N=1 case) with zero data loss on first load. A single ACCESSOR seam (read/write helpers)
     that every one of the ~20 engine call sites routes through, so single-active behavior is just
     N=1 and stays byte-for-decision identical for solo users. Multi-active COMMANDS: activate /
     deactivate a milestone in the set, switch the active task within a milestone, and a `status`
     view that renders the active set as parallel streams. All THREE byte-identical `add.py` copies
     (tooling · .add/tooling · _bundled/tooling) edited in lockstep and the ENGINE_MD5 pin
     re-established (re-pinned, never bypassed).
Out: User IDENTITY / actor stamping (`whoami`) — sibling `user-identity`. Task/milestone OWNERSHIP
     or assignment fields — sibling `ownership-assignment`. Git-merge conflict tooling / state
     sharding / divergence guards — sibling `git-merge-safety`. Multi-active UX beyond a basic
     parallel `status` (waves spanning active milestones, "my work" filters) — sibling
     `multi-active-UX`. ANY server / daemon / hosted backend (decided: git-native only). NO change
     to the per-task 0–7 phase flow or any phase guide. NO change to release/graduation semantics
     beyond making them read the active SET through the accessor.

## Shared decisions & glossary deltas   (living — every task must honor these)
- active set (NEW term) — `active_milestones`: the list of milestones a project has activated at
  once; the scalar `active_milestone` becomes "the set with one member". Add to GLOSSARY.
- per-milestone active task (NEW term) — each active milestone carries its own `active_task`; the
  old global `active_task` migrates to the active task of the migrated single active milestone.
- superset migration — the upgrade is additive and idempotent: old single-active state loads as the
  N=1 case, never a destructive rewrite; re-running the migration is a no-op (design-for-failure:
  load stays fail-soft, a malformed/old state never crashes the engine).
- backward-compatible solo behavior — with exactly one active milestone, every command's decisions
  are identical to today (no regression for single-user projects); this is a verify check on each task.
- engine-edit discipline — this milestone INTENTIONALLY edits the pinned engine. Every task edits
  all THREE add.py copies byte-identically AND re-pins ENGINE_MD5 in the SAME commit, so the 3-tree
  parity + pin tests stay GREEN throughout the milestone (the pin tracks HEAD per task; it is never
  lifted or deferred). The final `engine-repin-parity` task is therefore a consolidated parity AUDIT
  + parity-test hardening (assert the new multi-active invariants), not a deferred re-pin.

## Shared / risky contracts (freeze these first)
- the multi-active state.json SCHEMA + migration rule (field shapes, the N=1 upgrade, idempotency,
  fail-soft load) -> owning task `state-schema-migration`
- the active-milestone / active-task ACCESSOR API (the single read/write seam every call site uses)
  -> owning task `active-accessors`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] state-schema-migration  depends-on: none                   — Define the multi-active state.json schema + the idempotent, fail-soft forward migration from single-active (N=1); freeze the schema contract. risk:high.
- [ ] active-accessors        depends-on: state-schema-migration — Add the read/write accessor seam for active milestone(s)/task and route all ~20 engine call sites through it; single-active stays byte-for-decision identical. risk:high.
- [ ] multi-active-commands   depends-on: active-accessors       — `activate`/`deactivate`/`use` operate on the active SET: add/remove a milestone, switch the active task within one; refuse activating an unknown/done milestone. risk:high.
- [ ] parallel-status-view    depends-on: multi-active-commands  — `status` renders the active SET as parallel streams (per-milestone active task + phase), not a single active line. risk:high.
- [ ] engine-repin-parity     depends-on: parallel-status-view   — Consolidated parity AUDIT: assert all 3 add.py copies byte-identical, ENGINE_MD5 current, and harden the parity test to cover the new multi-active invariants. risk:high.

## Exit criteria (observable; map each to the task that delivers it)
- [x] An existing single-active `.add/` project loads and auto-migrates to the multi-active schema with zero data loss; re-running the migration is a no-op   (← state-schema-migration)
- [x] Every engine command reads/writes the active milestone(s) and active task through the accessor seam; with one active milestone the engine's decisions are identical to today   (← active-accessors)
- [x] A user can activate ≥2 milestones at once and switch the active task within each; activating an unknown or done milestone is refused   (← multi-active-commands)
- [x] `status` shows the active set as parallel streams, each with its own active task + phase   (← parallel-status-view)
- [x] All THREE add.py copies stay byte-identical and ENGINE_MD5 is current and green; the parity test asserts the new multi-active invariants (the engine edit is pinned, not bypassed)   (← engine-repin-parity)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py (all 3 byte-identical copies) — the multi-active state model: `_migrate_state` (pure/idempotent/total forward migration wired into both load seams) · born-migrated `cmd_init` · the accessor seam (`_active_milestone`/`_active_task`/`_set_active_milestone`/`_set_active_task`) with every ~20 call site routed through it · the SET writers `_activate_milestone`/`_deactivate_milestone` + the `activate`/`deactivate` verbs + a milestone-aware `use` + archive routed to deactivate · the `status` parallel-`streams :` render + the additive `status --json` keys (active_milestones/active_tasks). engine_pin.py re-pinned per task (25c6fcc5 → … → fa8e9818). state.json gains `active_milestones` (list) + `active_tasks` (map); the scalars stay as the N≤1 mirror.
- skill   : untouched — no SKILL.md / phases/* / guide change (the 0–7 phase flow is unchanged, as scoped Out).
- book    : untouched — no docs/* change (this is an engine-state foundation; the team-collaboration narrative lands with the later UX slices).

### Cross-task evidence   (one row per task)
- state-schema-migration : gate=PASS · tests=11 green (test_multi_active_state) · residue=none (review nit PURE-copy fixed in-verify)
- active-accessors       : gate=PASS · tests=10 green (test_active_accessors) · residue=none (review nit stale-active_tasks-after-archive fixed in-verify; nit-2 cmd_use cross-milestone seeded → consumed by multi-active-commands)
- multi-active-commands  : gate=PASS · tests=13 green (test_multi_active_commands) · residue=none (review BLOCK: non-primary-archive stale scalar — fixed red→green in-verify; NOTE cmd_use re-activates a done milestone → §7 SPEC delta)
- parallel-status-view   : gate=PASS · tests=10 green (test_parallel_status_view) · residue=none (review MERGE-WITH-NITS: N=1 byte-identity unproven → 3 hardening assertions added)
- engine-repin-parity    : gate=PASS · tests=7 green (test_engine_repin_parity) · residue=none (review MERGE: 2 docstring over-claims + 1 derivation NOTE closed; file-level audit proven to bite on real drift, restored)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
  - migration/zero-loss/no-op ← state-schema-migration (11) + engine-repin-parity test_legacy_migrates_idempotent
  - accessor seam · N≤1 identical ← active-accessors (10) + the full suite as the byte-for-decision oracle (no test weakened across the milestone)
  - activate ≥2 · switch task · refuse unknown/done ← multi-active-commands (13: test_activate_reaches_n2 · test_use_switches_task_in_milestone · the 3 reject tests)
  - status parallel streams ← parallel-status-view (10: test_two_active_render_as_streams) + the eyeballed CLI run
  - 3 copies byte-identical · pin current · invariants asserted ← engine-repin-parity (7: ParityAudit + MultiActiveInvariants)
- goal: ADD's engine now tracks N truly-parallel active milestones (a SET + per-milestone active task) with a backward-compatible, idempotent migration and a deliberately re-established ENGINE_MD5 pin — proven by `add.py activate m1` reaching N=2 with `status` rendering parallel streams while the full 1427-test suite (the N≤1 oracle) stays green and all 3 engine copies match the current pin.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from this milestone's 5 commits (state-schema-migration → engine-repin-parity) for human review + merge to main (admin-merge via the TinDang97 gh account; push as TinDang97 over HTTPS — tindangtts is pull-only)
- [ ] this is milestone 1 of the team-collaboration major — do NOT release solo; bundle the cut with the sibling slices (user-identity · ownership-assignment · git-merge-safety · multi-active-UX) OR cut a foundation release once the human decides the SET-model is independently shippable (per release.md; the engine records, the human tags/publishes)
- [ ] on release: bump the 4 version sources in lockstep + migrate the forward-pinned test_release_X_Y_Z.py (see the release-gate pattern); the security HARD-STOP floor is un-forceable
