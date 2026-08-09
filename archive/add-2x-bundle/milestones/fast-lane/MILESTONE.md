# MILESTONE: fast-lane

goal: a maintainer can run a small task through ADD with far less ceremony — a collapsed flow and a minimal TASK.md that still freezes a contract, proves a green, and reads back cold in a later session
rationale: sub-milestone of the lean-pass major (make ADD's own method the most-effective prompt at optimized cost). Sibling to the merged flow-simplification; EXTENDS that theme by adding a lighter LANE for small tasks (collapses the per-task flow, where flow-simplification collapsed spawn/confirm/review). DEPENDS-ON the existing autonomy:auto auto-gate (v6/v7) + the one-approval bundle. No live milestone's goal covers it.
stage: mvp · status: active · created: 2026-06-23

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  an opt-in fast lane (`new-task --fast`) · a minimal TASK.md template variant · skill guidance for when/how to run it.
Out: reshaping the frozen 9-phase PHASES tuple / state.json machine contract (the fast lane runs the SAME phases, just collapsed in fill) · an engine heuristic that auto-classifies a task as "small" (human opts in; the engine never guesses ceremony) · dropping the contract freeze / red-test-before-build / verify gate · a fast lane for milestones or releases (task-level only).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Collapse, never skip.** The three non-negotiables — a FROZEN §3 contract · ≥1 red test before build · a recorded verify gate (security always HARD-STOP) — are preserved. Speed comes from fewer sections + auto-gating under `autonomy: auto`, not from removing the trust seam.
- **Human opts in.** `--fast` is explicit, like the autonomy header; the engine never auto-picks the ceremony level (consistent with "ceremony/identity is human-owned").
- **The minimal-template floor** is the frozen intent/contract (core value) + the §6 gate record (the proof). "Minimal enough to retrieve + persist core value" = those two always survive.
- glossary delta: new term **fast lane** — the collapsed, opt-in task path for small tasks (owned by `fast-lane-guide`).

## Shared / risky contracts (freeze these first)
- the kept-section set of the minimal template -> owning task `fast-lane-template`
- the `--fast` flag + `fast:` header marker -> owning task `fast-new-task-flag`
- the opt-in freeze-before-build gate (keyed on the milestone `await_confirm` switch) -> owning task `freeze-before-build-gate`

## Scope growth note (2026-06-23)
A build-phase discovery (empirically verified): the engine does NOT hard-enforce freeze-before-gate for ANY task today — a DRAFT §3 task advances through build→verify to gate=PASS unrefused (the freeze is a skill/human convention). To make "collapse-never-skip" REAL, the human chose to enforce freeze-before-build via the EXISTING `--await-confirm` opt-in switch (the proven path; an all-tasks guard breaks ~40 fixture files — the confirm-parent trap). Added a 4th task `freeze-before-build-gate`; `fast-new-task-flag`'s frozen §3 gets a v1→v2 correction (it had wrongly claimed the floor was "enforced upstream").

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] fast-lane-template       depends-on: none                   — the minimal TASK.md variant + its `_FALLBACK` circuit-breaker; decide which sections collapse to one-liners vs. drop, keeping the contract + gate-record floor.  **SHIPPED gate=PASS.**
- [x] freeze-before-build-gate depends-on: none                   — the opt-in freeze-before-build gate: a task under an `await_confirm` milestone may not cross into build until §3 is FROZEN (sibling to contract-fill + build-expectations gates; zero ripple). Makes the floor REAL.  **SHIPPED gate=PASS.**
- [x] fast-new-task-flag       depends-on: freeze-before-build-gate — `add.py new-task --fast` scaffolds the minimal template, seeds the `fast:` marker, status/audit tolerate the minimal shape. **v1→v2 "fast implies floor": a `--fast` task is freeze-gated under ANY milestone.  SHIPPED gate=PASS.**
- [x] fast-lane-guide          depends-on: fast-new-task-flag      — `phases/fast-lane.md`: when to choose the fast lane + how to run specify→contract→tests as one batched approval; SKILL.md + book pointer + glossary entry.  **SHIPPED gate=PASS.**

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py new-task <slug> --fast` yields a TASK.md with materially fewer sections than the full template   (← fast-lane-template, fast-new-task-flag) (verify: test_fast_lane_template.py asserts the fast template's section set == {0,1,3,4,5,6} < the full {0..7}; test_fast_new_task_flag.test_fast_scaffolds_minimal_and_marks_state asserts the live `--fast` scaffold parses to {0,1,3,4,5,6})
- [x] a `--fast` task still cannot reach gate=PASS without a FROZEN §3 contract and a recorded §6 outcome   (← fast-new-task-flag) (verify: test_fast_new_task_flag.test_fast_floor_holds_under_plain_milestone — `advance` refuses `contract_not_frozen` on an unfrozen fast task; test_fast_task_completes_through_gates — reaches PASS only after freeze, §6 Outcome stamped PASS)
- [x] under an opted-in (`await_confirm`) milestone — OR any `--fast` task — a task is REFUSED at tests→build while §3 is unfrozen; a plain non-fast task is unaffected   (← freeze-before-build-gate + fast-new-task-flag v2) (verify: test_freeze_before_build_gate.py — `contract_not_frozen` fires when await_confirm is True; test_fast_new_task_flag.test_plain_task_not_freeze_gated — a plain non-fast task is NOT gated, zero ripple)
- [x] the minimal TASK.md, read cold in a later session, still shows the task's intent/contract + its verify outcome   (← fast-lane-template) (verify: test_fast_lane_template.py asserts §3 CONTRACT `Status:` + §6 `### GATE RECORD` both present in the scaffold — the retrieve+persist floor)
- [x] the skill names WHEN to pick the fast lane and HOW to run it as one approval   (← fast-lane-guide) (verify: test_fast_lane_guide.py asserts phases/fast-lane.md present ×3 + names the floor + no bypass phrasing + the SKILL.md pointer + the glossary term)
- [x] full suite green; engine pin updated across trees if the engine changed   (← all) (verify: `add.py check` 396 passed / 0 failed; full suite 1634 green; test_engine_repin_parity + test_shared_engine_pin green; add.py md5 d4807ff9 byte-identical ×3)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add.py` — NEW `--fast` flag on `new-task` (renders the minimal `TASK.fast.md`, records `state.tasks[slug].fast=True`) · the freeze-before-build gate (`contract_not_frozen` at the `nxt=="build"` crossing, firing on `_optin OR fast`, BEFORE the build-expectations gate) · a `_FALLBACK_TASK_FAST` circuit-breaker + `_render_template` fast fallback · a ` · fast` marker on the `status` active line. NEW `templates/TASK.fast.md.tmpl` (sections {0,1,3,4,5,6}). ENGINE_MD5 cb7ddd03 → 280daae8 → 80985fc3 → d4807ff9 (re-pinned ×3 trees). Lean fence `test_skill_lean.py` rebaselined for the new guide (ratios kept).
- skill   : NEW `phases/fast-lane.md` (when/how/floor, ×3 trees) + a SKILL.md "Beyond the bundle" pointer (×3).
- book    : `appendix-c-glossary.md` "fast lane" term (×4 mirrors) + `.add/GLOSSARY.md` survivor entry.

### Cross-task evidence   (one row per task)
- fast-lane-template       : gate=PASS · tests=25 green (test_fast_lane_template.py) · residue=none (disclosed: §3 "6<9" annotation, true 6<8; binding seam correct)
- freeze-before-build-gate : gate=PASS · tests=6 green (test_freeze_before_build_gate.py) + mutation-verified · residue=none (sibling-fixture fix: test_build_expectations_gate freezes its 2 opted-in fixtures)
- fast-new-task-flag       : gate=PASS · tests=8 green (test_fast_new_task_flag.py) + mutation-verified · residue=none (v1→v2 change-request: "fast implies floor", human-approved)
- fast-lane-guide          : gate=PASS · tests=6 green (test_fast_lane_guide.py) · residue=none (lean-fence rebaseline + wording-surface 28→29, human-approved, declared in §5)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — criteria 1+4 ← fast-lane-template + fast-new-task-flag; 2 ← fast-new-task-flag; 3 ← freeze-before-build-gate + fast-new-task-flag v2; 5 ← fast-lane-guide; 6 ← `add.py check` 396/0 + full suite 1634 green + pin parity.
- goal: a maintainer can run a small task through ADD with far less ceremony — a collapsed flow + a minimal TASK.md that still freezes a contract, proves a green, and reads back cold. PROVEN: `new-task --fast` scaffolds {0,1,3,4,5,6} (drops scenarios+observe) yet a fast task is REFUSED `contract_not_frozen` until §3 is frozen and reaches PASS only with a stamped §6 — the floor is collapsed, never skipped.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] consolidate open deltas (`add.py fold`) at close, then commit the milestone on a feature branch.
- [ ] open a PR from the ship-review above; the human reviews + merges (admin-merge as TinDang97).
- [ ] bundle into the next release cut (this is a sub-milestone of the lean-pass major; release deferred — 1.9.0 pending).
