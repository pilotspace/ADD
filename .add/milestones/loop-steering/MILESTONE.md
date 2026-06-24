# MILESTONE: Loop Steering

goal: make the dynamic loop GUIDED, not just gated: the orient surfaces an agent reads first (status, guide) must route into the loop when an active milestone's tasks are all done but its goal is unmet — today only report<ms> carries that cue
rationale: micro-milestone (one-task-gap rule) — a ~1-task method fix that fits no active milestone; a fresh micro-milestone gives it ledger attribution + exit criteria without inflating scope. NOT a change-request: no frozen contract's promise changes — this ADDS milestone-aware steering the orient surfaces never had. Evidence: live probe at the loop juncture showed `status` resume says "start the next feature" and `guide` routes to 02-the-flow.md; only `report<ms>` DECIDE NEXT carries "goal not met → propose next tasks". loop.md misattributes that cue to `status`.
stage: mvp · status: active · created: 2026-06-24

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  status + guide done-task resume becomes milestone-goal-aware (engine); loop.md cue
     attribution corrected to match the engine (doc). One fast-lane task.
Out: report VERDICT `DONE`→`IN-LOOP` rename (cosmetic, separate concern) — deferred as a
     delta; multi-active-milestone resume rollups; any change to the goal-gate itself (it
     is correct + tested — this milestone only adds STEERING, never touches the gate).

## Shared decisions & glossary deltas   (living — every task must honor these)
- The goal-gate is unchanged: the engine still never JUDGES the goal (reads the [x]/[ ] tally).
  This milestone only makes the orient surfaces POINT at the loop; the human still checks boxes.
- "loop juncture" = an active milestone whose member tasks are ALL done while its exit criteria
  are not all met (total>0 and met<total) — the state that holds the loop open.

## Shared / risky contracts (freeze these first)
- status/guide done-task resume copy (the new milestone-aware branch text) -> owning task loop-aware-orient

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] loop-aware-orient   depends-on: none   — status+guide route into the loop at the loop juncture; fix loop.md cue

## Exit criteria (observable; map each to the task that delivers it)
- [x] At the loop juncture, `add.py status` resume names the unmet milestone goal and points to the loop (not "start the next feature")   (← loop-aware-orient)  (verify: test_loop_aware_orient status assertions)
- [x] At the loop juncture, `add.py guide` routes to 09-the-loop.md (not 02-the-flow.md)   (← loop-aware-orient)  (verify: test_loop_aware_orient guide assertions)
- [x] When the goal IS met (all boxes checked), status/guide point to `milestone-done <ms>`; when there are NO criteria, behavior is byte-identical to today   (← loop-aware-orient)  (verify: test_loop_aware_orient met + no-criteria cases)
- [x] loop.md no longer claims `status` shows `goal not met (m/n)` unless the engine actually prints it   (← loop-aware-orient)  (verify: test_loop_aware_orient doc-accord assertion)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py — new pure `_done_resume` helper; `cmd_status` done-branch + `cmd_guide` human & --json done-branch route via it (override only when chapter≠02-the-flow.md, so PLAIN is byte-identical). 3-tree parity propagated; ENGINE_MD5 27f840e7→ba1f21fbfbf5df15702bec9a14511155. New test_loop_aware_orient.py [9].
- skill   : untouched — loop.md needed NO edit: the engine now prints "goal not met (m/n exit criteria)" so loop.md's existing status-attribution became TRUE (cue healed at the source).
- book    : untouched — 09-the-loop.md already names the goal-gate; nothing claimed falsely.

### Cross-task evidence   (one row per task)
- loop-aware-orient : gate=PASS · tests=9 new green (suite 1666/0) · residue=one deferred `[SPEC · open]` (report VERDICT DONE→IN-LOOP) · scope anchor corrected (multi-line §5 → flat dir-tokens)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
  - EC1 (status names unmet goal + loop) ← test_status_loop_juncture_names_goal_and_loop + LIVE dogfood: `status` resume on this very repo shows "milestone 'loop-steering' goal not met (0/4 exit criteria) … 09-the-loop.md"
  - EC2 (guide routes to 09-the-loop.md) ← test_guide_loop_juncture_routes_to_loop_chapter + test_guide_json_loop_juncture_chapter; LIVE `guide`/`guide --json` both → .add/docs/09-the-loop.md
  - EC3 (goal-met → milestone-done; no-criteria byte-identical) ← test_status_goal_met_points_to_milestone_done + test_status_no_criteria_keeps_plain_resume + test_guide_no_criteria_keeps_flow_chapter
  - EC4 (loop.md not a false claim) ← test_loop_md_cue_matches_engine (engine prints the cue loop.md quotes)
- goal: make the dynamic loop GUIDED, not just gated — proven by the live dogfood: status/guide/--json on this repo now steer the open milestone into 09-the-loop.md instead of "start the next feature".

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] branch `feat/loop-steering`, commit the build (engine + test + pin + .add ledger)
- [ ] open a PR (base main) from this Close ship-review; human reviews + admin-merges (TinDang97)
- [ ] bundle into the next release cut (release.md) — small MINOR-worthy method fix; not a standalone publish
