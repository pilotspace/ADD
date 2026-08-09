# MILESTONE: Audit hardening — close gate/atomicity/coverage gaps

goal: make the engine enforce at gate-time the invariants the post-hoc audit catches — no PASS against an unfrozen or stale contract, crash-safe state writes, and a monotonic heal counter — closing the gaps the 2026-06-25 deep audit surfaced
rationale: new-major intake — a deep multi-agent audit found gate/atomicity/coverage holes where the engine TRUSTS what it should ENFORCE (admin override skips the build guards, a crashed state write splits the marker, --force resets the heal counter, setup reaches build with no red test, a stale consumer pin only warns). Each is a one-task engine/method fix; bundled because they share the "enforce the invariant at the seam" theme.
stage: mvp · status: active · created: 2026-06-25

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  five gate-time / atomicity / coverage enforcement fixes (F4 phase-build guard · F7+F12 crash-safe state + durable-state-before-marker · F8 force preserves heal · F6 setup drafts the red suite before build · F5 stale-consumer gate).
Out: the deferred follow-ups seeded as deltas (a build-boundary engine gate refusing the first crossing when §4/tests/ is empty; doctor referential-set widening; doctor --json) — recorded, not in this milestone.

## Shared decisions & glossary deltas   (living — every task must honor these)
- Enforce at the seam, never relax the trust seam: each fix ADDS a guard (refuse / fail-closed / preserve), never weakens an existing one. Security-class findings stay HARD-STOP.
- Completing-gate guards (tamper · scope · consumer-stale) all run BEFORE the waiver write and never on a HARD-STOP outcome — a refusal is not launderable through RISK-ACCEPTED.
- Every engine change re-mirrors 3 trees + re-pins ENGINE_MD5; red/green TDD per task.

## Shared / risky contracts (freeze these first)
- cmd_gate completing-block guard order (tamper → scope → consumer-stale, all pre-waiver) -> owning tasks consumer-stale-gate / phase-build-guard

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] phase-build-guard        depends-on: none              — F4: cmd_phase refuses phase=build on an unfrozen §3 (heal-loop exempt)
- [x] save-state-harden        depends-on: none              — F7+F12: save_state fail-closed on OSError + durable state BEFORE the task marker (no split-brain)
- [x] force-preserve-heal      depends-on: none              — F8: new-task --force preserves the monotonic heal counter
- [x] setup-tests-before-build depends-on: none              — F6: 0-setup drafts §1–§4 incl. the §4 red suite; exit gate requires it RED before build
- [x] consumer-stale-gate      depends-on: phase-build-guard — F5: cmd_gate refuses a completing outcome on a stale consumer contract pin

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py phase build` on an unfrozen-contract task is REFUSED (contract_not_frozen), the heal loop exempt   (← phase-build-guard)
- [x] a failed state write fails closed (state_write_failed) and durable state is persisted before the task marker — no split-brain   (← save-state-harden)
- [x] `new-task --force` on an existing task preserves its heal counter   (← force-preserve-heal)
- [x] the setup guide drafts the §4 red suite and its exit gate requires the suite RED before build opens   (← setup-tests-before-build)
- [x] `add.py gate PASS|RISK-ACCEPTED` on a task whose pinned consumer contract drifted is REFUSED (contract_consumer_stale)   (← consumer-stale-gate)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py — new guards `_consumer_stale_guard`, the cmd_phase build-freeze guard (F4), `save_state` fail-closed wrap (F7), durable-state-before-marker reorder in cmd_phase/advance/gate/reopen (F12), `new-task --force` heal-preserve (F8); engine_pin re-pinned per task (final ENGINE_MD5 310a8ed7); +15 tests across test_state_hardening / test_heal_then_escalate / test_cross_component_contract / test_setup_tests_before_build.
- skill   : phases/0-setup.md — step 3 + exit gate now require the §4 red suite before build (F6, mirrored ×3); test_skill_lean phases pool rebaselined 37920→38298 (ratio kept).
- book    : untouched.

### Cross-task evidence   (one row per task)
- phase-build-guard        : gate=PASS · suite=1780 green · residue=none (heal-loop exemption proven)
- save-state-harden        : gate=PASS · suite=1784 green (+4) · residue=none (no-split-brain marker test)
- force-preserve-heal      : gate=PASS · suite=1787 green (+3) · residue=none (tripwire-preserve correctly dropped as a no-op — heal-only, recorded as a competency delta)
- setup-tests-before-build : gate=PASS · suite=1792 green (+5) · residue=engine-gate follow-up seeded as a SPEC delta (guide is the primary seam)
- consumer-stale-gate      : gate=PASS · suite=1797 green (+5) · residue=none (unreadable-snapshot stays a cmd_check warning, by design)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — all 5 criteria map 1:1 to the 5 task rows above; final suite 1797/0, seam audit clean (86 tasks).
- goal: enforce at gate-time the invariants the post-hoc audit catches — proven: every one of the 5 audit findings is now a RED test that refuses/fail-closes the bad path (suite 1797/0), where before each was only a post-hoc warning or an unguarded override.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] push `docs/audit-fixes-readme` (all 5 commits) and update PR #66 with this ship-review; human reviews + merges
- [ ] after merge, fold the milestone's confirmed deltas (`add.py fold`) and archive
- [ ] bundle into the next release cut (release.md) — version bump + CHANGELOG + tag/publish are human-gated
