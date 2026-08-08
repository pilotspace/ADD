# MILESTONE: Correct · Shippable

goal: Make ADD correct under misuse and safe to publish: refuse unsafe gates, guard the docs/build invariants, ship clean
stage: mvp · status: active · created: 2026-05-29 · scope-audited: 2026-06-03

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope audit (2026-06-03)
v3 was planned (5 breadth-first tasks) but never scaffolded — 0 TASK.md files. An
audit against the shipped code shows the milestone's theme was largely delivered by
*later* milestones, leaving two genuine residual gaps. Verdict per original task:

| Original task | Verdict | Why |
|---------------|---------|-----|
| gate-time-waiver | **superseded by design** | The gate refuses *incomplete*/before-verify waivers; expiry is caught by `check` as the standing monitor — a deliberate choice (see test_waiver.py: "the gate stored it; check is the standing monitor that catches it"). The deeper intent (an expired waiver can never silently pass) is met. |
| ascii-docs-guard | **obsolete (direction rejected)** | The book deliberately uses `·`, `→`, `⇄`, em-dashes and renders with `ensure_ascii=False`. An English-only ASCII guard would now turn the whole suite red. The project rejected this in practice. |
| stable-guideline-markers | **delivered (v1-2)** | `_GUIDE_BEGIN`/`_GUIDE_END` (`<!-- ADD:BEGIN/END -->`) markers + unbalanced-marker warning, covered by test_guidelines.py. |
| prepublish-guard | **residual gap → carried** | Manifest/version guard exists as tests + CI at tag time, but `package.json` has no `prepublishOnly` hook, so a local `npm publish` is not blocked. |
| project-cmd | **residual gap → carried** | No `add.py project` subcommand. Partially covered by `status` printing the foundation path, but the one-command print/open affordance is absent. |

The two residual gaps are folded into one small task below; the three resolved items
are recorded here and not re-opened.

## Scope (post-audit)
In:  the two ship-clean residuals — (a) `prepublishOnly` runs the manifest guard so a
     dirty/incomplete tree cannot `npm publish`; (b) `add.py project` prints/opens
     `.add/PROJECT.md` (the "read first" foundation) in one command.
Out: gate-time waiver refusal (superseded by the `check` monitor); the ASCII docs guard
     (obsolete — the book is intentionally Unicode); stable guideline markers (already
     delivered in v1-2). Plus the original v3 out-of-scope set (ergonomics, diagram
     re-render, FINDING-C boundary, Vietnamese onboarding).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Fail-closed, read-only stays the rule** (carried from v2): a new guard FAILS on a
  missing/unparseable/ambiguous input, never silently passes; `check` and guards never
  mutate state.
- **Every new guard is a behavioral proof, not a source-grep** (v2 circularity bar): the
  test must go red for a REAL regression, not merely because a file was edited.
- All design forks are decided with the human (AskUserQuestion) before a contract freezes.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] ship-clean   depends-on: none   — bundle the two v3 residuals: `prepublishOnly` wired to the manifest guard, and `add.py project` opens the foundation. (Independent concerns; split into two tasks if a single frozen contract proves awkward.)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `npm publish` from a dirty/incomplete tree is blocked by the guard via `prepublishOnly`  (← ship-clean)
- [x] `add.py project` prints (or opens) the foundation in one command                          (← ship-clean)

## Close note (2026-06-03)
ship-clean gated PASS (conservative dial — human-recorded after evidence review); both exit
criteria met. Milestone **done**. v3 was planned as 5 tasks but the scope audit found 3 already
superseded/delivered/obsolete; only the 2 residuals were real, bundled into one task. One accepted
limitation carried forward: concern (A) is wiring-linkage proof, not a live `npm publish` (see
ship-clean §6 / OBSERVE — `npm pack` + tarball-content assertion is the next rung if it ever bites).
