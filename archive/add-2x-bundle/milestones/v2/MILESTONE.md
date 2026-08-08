# MILESTONE: Transparent · Provable · Minimal

goal: Make ADD provable and explicitly two-surface (State/Story) without adding context-rot
stage: mvp · status: active · created: 2026-05-29

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the two-surface State/Story split made explicit in the book; a proof-harness so the
     method's promises fail loudly when Story and State drift; the RISK-ACCEPTED waiver path
     (sign · complete · expire); the flow diagram corrected to show non-waterfall loopback +
     the nested TDD⇄ADD engine; and a minimalism-and-coverage audit that proves the *Minimal*
     pillar and sweeps the requirements matrix.
Out: enforcing section-completeness or per-milestone document depth in the engine (a chosen
     boundary — the engine owns cheap structural invariants, the human owns judgement at the
     Verify gate); re-rendering the other three diagrams; a `diagrams/render.sh` wrapper.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **State vs Story** (principle 9): State = loaded each session (state.json, TASK.md, the
  survivor files); Story = the book (`docs/*`), referenced by pointer, **never auto-loaded**.
- Every method promise that the engine *can* enforce gets a named proof test (book-claim →
  engine-enforces → named test); a test must go red for a REAL change, not a cosmetic edit.
- All design forks are decided with the human (AskUserQuestion) before a contract freezes.

## Shared / risky contracts (freeze these first)
- the gate state machine (PASS / RISK-ACCEPTED / HARD-STOP; verify-phase guard) -> risk-accepted-gate
- the flow diagram's two-direction contract (solid forward / dashed correction) -> flow-diagram-refresh

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] state-story-architecture   depends-on: none              — name the two surfaces in the book; pin the vocabulary
- [x] proof-harness              depends-on: none              — ship the book-claim→engine→test harness (Matrix 4)
- [x] risk-accepted-gate         depends-on: proof-harness     — a signed waiver completes a task *and* its milestone
- [x] flow-diagram-refresh       depends-on: none              — diagram shows any-phase loopback + the red/green engine
- [x] minimalism-audit           depends-on: the above         — prove the Minimal pillar; expire waivers; sweep the matrix

## Exit criteria (observable; map each to the task that delivers it)
- [x] The book names State vs Story and says the Story is never auto-loaded   (← state-story-architecture)
- [x] Each enforced promise has a failing-if-broken proof test (Matrix 4)     (← proof-harness)
- [x] A signed RISK-ACCEPTED waiver completes its task and milestone          (← risk-accepted-gate)
- [x] The canonical flow diagram no longer contradicts principle 4            (← flow-diagram-refresh)
- [x] "The Story is never auto-loaded" is proved behaviorally, not just said  (← minimalism-audit)
- [x] `check` flags a lapsed waiver; the matrix sweep is recorded             (← minimalism-audit)
