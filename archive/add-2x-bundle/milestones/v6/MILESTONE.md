# MILESTONE: The Self-Driving Run

goal: Once a task's contract is frozen, run the build->verify half as a dynamic,
self-improving workflow that converges in-run and auto-gates on evidence — pulling
the human in only for the residue tests cannot catch — without losing ADD's
human-led front or its delta learning.
stage: mvp · status: active · created: 2026-06-01

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> ADD already hands off from human-led to AI-led at the frozen contract (the seam in
> the flow). Today the far side is a manual, sequential build. v6 makes the **far side
> dynamic**: scope-lock flips the task into an autonomous run that fans out, converges
> in-run (loop-until-dry · adversarial verify · completeness-critic), auto-gates verify
> on evidence, and emits competency deltas into v5's human-gated fold loop. The
> human-led FRONT (Specify·Scenarios·Contract) does not move; what runs after the lock does.

## Scope
In:  the autonomous execution layer for a LOCKED scope — (1) a **scope-lock trigger**: the
     frozen CONTRACT (phase 3) flips a task from human-led to autonomous-run, with a defined
     touch-boundary; (2) a **dynamic run engine** for build->verify — fan-out orchestration +
     within-run convergence (loop-until-dry · adversarial verify · completeness-critic),
     defined as a method rubric (`run.md`), NOT add.py judgment; (3) **evidence auto-gate**:
     verify records PASS automatically when tests + blind-spot checks pass, the human pulled in
     only on the residue (security/concurrency/architecture); (4) the run **emits competency
     deltas** into v5's OBSERVE/fold loop (within-run convergence + persisted learning);
     (5) an **autonomy dial** — auto-gate is a per-scope setting (principle 5), conservative
     default; (6) a **principle reframe** — reword principles 6/7 in the book so automated
     verification is admitted and the non-automatable residue is named.
Out: any change to the human-led FRONT — Specify·Scenarios·Contract stay human (v6 touches
     only the build->verify far side); any autonomous edit of the FROZEN contract or the locked
     SCOPE — the run executes a lock, it never re-locks (a discovered gap is still backward-
     correction -> human, never an autonomous scope rewrite); any autonomous FOLD — deltas still
     fold human-gated (v5 holds: the run emits `open`, the human folds); any ML/model training
     ("self-improving" = in-run convergence + tracked deltas, same as v5); any NEW always-loaded
     doc (Minimal pillar v2 holds — `run.md` is on-demand); any re-cut of the 7-phase sequence.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Scope-lock is the autonomy seam — it does not move.** The frozen contract (phase 3) is
  already where ADD hands off human->AI. v6 changes what runs on the far side (a dynamic run,
  not a manual build), not where the seam sits.
- **Auto-gate is principle 2 at full autonomy — and a DIAL, not a default (principle 5).**
  Trusting passing evidence over inspection IS principle 2. Auto-gating verify is that taken to
  its limit. It is opt-in per scope, conservative by default; you raise it where evidence is
  strong and risk is low, lower it anywhere else.
- **Principles 6 & 7 are REFRAMED, not broken (human ruling required before the auto-gate
  contract freezes).** P6 ("cannot move faster than you can verify") holds because the
  *verification is automated* — the evidence IS the verification. The residue P2 names ("the
  narrow set tests cannot catch": security · concurrency · architecture) is NOT auto-gateable —
  it always escalates to a human; **security is always HARD-STOP**. Without that boundary,
  auto-gate would be a silent skip and violate P7. The reframing is owned by a v6 task
  (`principle-reframe`) and the human confirms it before `evidence-auto-gate` freezes.
- **Engine is truth; the harness is intelligence (v4-1).** The run rubric — orchestration
  patterns, convergence loops, gate logic — is JUDGMENT -> method/skill (`run.md`). `add.py` may
  *record* an auto-gate outcome; it must not *decide* it.
- **Self-improving = in-run convergence + emit v5 deltas.** Same definition as v5. The run
  converges in-turn AND feeds the human-gated fold loop. No autonomous fold.
- **The Minimal pillar holds (v2).** `run.md` is on-demand like other phase rubrics; v6 adds
  autonomy, not always-loaded surface.
- New glossary terms: **Scope-lock**, **Dynamic run**, **Evidence auto-gate**, **Autonomy dial**.
- All design forks are decided with the human (AskUserQuestion) before a contract freezes.

## Shared / risky contracts (freeze these first)
- the **scope-lock -> run handoff** — what state flips when the contract freezes; what the run
  MAY touch (code, tests-green, evidence) vs MUST NOT (the frozen contract, the locked scope).
  Everything else depends on it; freeze first  -> scope-lock-trigger
- the **evidence auto-gate contract** — exactly what evidence auto-PASSes verify, what residue
  always escalates to a human, how the one outcome is recorded (P7). The riskiest contract in
  the milestone; depends on the principle reframe landing first  -> evidence-auto-gate

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] scope-lock-trigger   depends-on: none                              — the contract-freeze -> autonomous-run handoff: what flips, what the run may/may not touch
- [ ] principle-reframe    depends-on: none                              — reword book principles 6/7: automated verification IS verification; name the non-automatable residue (a change-request to docs/01-principles.md)
- [ ] dynamic-run-engine   depends-on: scope-lock-trigger                — `run.md`: fan-out build->verify with in-run convergence (loop-until-dry · adversarial verify · completeness-critic); method-only
- [ ] evidence-auto-gate   depends-on: scope-lock-trigger,principle-reframe — the auto-gate contract: evidence that auto-PASSes verify + the residue (security/concurrency/arch) that always escalates; one recorded outcome
- [ ] run-emits-deltas     depends-on: dynamic-run-engine                — the run's completeness-critic findings emit as `open` competency deltas into v5's OBSERVE block (wires v6 run -> v5 fold)
- [ ] autonomy-dial        depends-on: evidence-auto-gate                — auto-gate as a per-scope setting (principle 5), conservative default, opt-in to full auto; surfaced in status (lightest; cuttable)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] a frozen contract flips a task into an autonomous run with a defined touch-boundary        (← scope-lock-trigger)
- [ ] book principles 6/7 admit automated verification and name the non-automatable residue       (← principle-reframe)
- [ ] the build->verify half runs as a documented fan-out workflow that converges in-run          (← dynamic-run-engine)
- [ ] verify auto-PASSes on evidence; security/blind-spot residue always escalates + records one outcome  (← evidence-auto-gate)
- [ ] a run's findings appear as `open` competency deltas in the task's OBSERVE block             (← run-emits-deltas)
- [ ] the auto-gate level is a per-scope setting visible in status, conservative by default       (← autonomy-dial)
