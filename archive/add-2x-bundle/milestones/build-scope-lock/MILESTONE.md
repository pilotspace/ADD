# MILESTONE: Build Scope Lock

goal: a build's scope of impact is declared before it starts and engine-enforced when it ends — touched is a subset of declared, so a passing build cannot quietly modify files outside its frozen scope
rationale: sub-milestone of the trust theme (human-confirmed intake 2026-06-11) — the third side of the triangle: §3 freezes the SHAPE, §4 freezes the PROOF, this freezes the SCOPE OF IMPACT; today a green build may touch anything
stage: mvp · status: active · created: 2026-06-12

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  §5 BUILD `Scope:` file-touch allowlist + ordered `Strategy:` batches, declared with the bundle and frozen at the contract freeze; engine gate enforcement (touched ⊆ declared, named refusal); violations routed into the existing bounded self-heal loop (shared cap)
Out: per-batch progress tracking · IDE integration · auto-generated scope from §0 · enforcing the Strategy ORDER (only the Scope set is enforced; the order is guidance)

## Shared decisions & glossary deltas   (living — every task must honor these)
- the engine stays tool-agnostic: touch detection NEVER shells out to git — it works from engine-owned snapshots (the tamper-tripwire precedent)
- a scope violation is cheat-class plumbing, not a new discipline: it reuses heal/heal_exhausted, never a parallel loop
- Scope/Strategy are part of the specification bundle: ONE human approval at the contract freeze covers them (no new gate)

## Shared / risky contracts (freeze these first)
- git-free touched-file detection (snapshot mechanism: content-hash vs mtime, scope of the snapshot set) -> owning task scope-gate-enforce
- the §5 Scope/Strategy declaration grammar (parseable by the engine, writable by any agent) -> owning task scope-decl-template

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] scope-decl-template     depends-on: none                 — §5 gains Scope/Strategy template lines; phase guides teach declare-at-bundle, freeze-at-contract   (done 2026-06-12, gate=PASS)
- [x] scope-gate-enforce      depends-on: scope-decl-template  — engine snapshots declared scope at tests→build, verifies touched ⊆ declared at the gate (named refusal)   (done 2026-06-12, gate=PASS human-held; 3 contract versions, 2 refute passes)
- [x] scope-violation-heal    depends-on: scope-gate-enforce   — a violation routes into the bounded self-heal loop — honest redo, never a silent pass   (done 2026-06-12, gate=PASS human-held; recoverable findings heal, erased baselines die-in-place, shared HEAL_CAP)

## Exit criteria (observable; map each to the task that delivers it)
- [x] A fresh TASK.md §5 carries Scope/Strategy lines that freeze with the bundle        (← scope-decl-template · verify: test_scope_decl_template.test_scaffold_carries_scope_of_impact_lines)
- [x] The verify gate refuses a build that touched an undeclared file, with a named code (← scope-gate-enforce · verify: test_scope_gate_enforce.GateTest.test_gate_out_of_scope_modify_refused)
- [x] A scope violation lands in the self-heal loop and counts against the shared cap    (← scope-violation-heal · verify: test_scope_violation_heal.ViolationHealsTest.test_cap_is_shared_across_sources)
