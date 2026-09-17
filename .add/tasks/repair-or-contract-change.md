---
type: Task
title: repair-or-contract-change
status: direction
depth: standard
milestone: state-that-tells-truth
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/tests/engine/test_repair_or_contract_change.py
gives:
  - S1 `repair` routes a frozen open Task with a recorded cause to Build for an implementation defect or Direction for an unknown or changed contract
generated: { by: add/3.6.0, at: 2026-09-15 }
verified: []
---
## CARD
goal: a failing build can be repaired under its approved intent, while an open decision or changed requirement visibly returns to Direction
why: `replan` currently records any nonblank steering note and says keep building; `gate` later catches some digest drift, but an open frozen Task has no Direction-return verb, and `scope:` is not compared with the old approval.
beat: direction · next: review the route, rejected shortcuts, and red checks, then freeze with the authority this scope computes

## RULES
<must>
- M1 on an open frozen Task, an implementation failure with unchanged frozen RULES, CHECKS, EDGES/probed obligations, `gives:` and scope records its concrete cause and stays in Build (from: /milestones/state-that-tells-truth.md EXIT 4 · fails-on: a harmless code defect triggers routine reapproval)
- M2 a changed Must, Reject, check obligation, published surface, or scope returns the Task to Direction, records the cause, and leaves the old freeze stamp intact until a new freeze/refreeze (from: /milestones/state-that-tells-truth.md EXIT 4 · fails-on: a changed contract is repaired under old authority)
- M3 uncertainty or silence about what the frozen requirement means returns the Task to Direction even when its text digest is unchanged (from: /milestones/state-that-tells-truth.md EXIT 4 · fails-on: a builder silently chooses a new rule)
- M4 a Build run/green receipt and PASS cannot use an old freeze after a Direction return; refreeze must reapply the computed authority floor before Build resumes (from: /milestones/state-that-tells-truth.md EXIT 4 · fails-on: a `process` note becomes a substitute human/security approval)
</must>
<reject>
- R:CAUSELESS a repair route with no concrete cause is recorded -> "CAUSELESS"
- R:SEAL_TOUCH a caller labels frozen text or scope drift as an implementation defect and stays in Build -> "SEAL_TOUCH"
- R:OLDSEAL a Direction return is briefed, run, or gated on the prior freeze -> "OLDSEAL"
- R:WRONGNODE a Milestone or done Task is routed as an open Build repair -> "WRONGNODE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · an implementation defect can be diagnosed by the builder, but a semantic silence cannot be adjudicated by the engine; taking the cause class as an explicit operator declaration guarded by structural comparisons -> a dishonest declaration still needs review
- A2 [which] covers: S1 · the milestone calls out frozen requirements and scope; taking RULES, CHECKS, `gives:`, EDGES/probed A ids and `scope:` as the mechanically compared surfaces -> a moved authority floor cannot hide behind an unchanged rule text
- A3 [when] covers: S1 · this route is for active frozen Tasks; taking done Task corrections through the existing `reopen`/successor rule -> closed history stays intact
- A4 [absent] covers: S1 · an unexplained failure is not enough to distinguish implementation from intent; taking blank cause as refusal and explicit unknown as Direction -> no silent Build decision
- A5 [order] covers: S1 · the old seal remains evidence while intent is reauthored; taking a Direction return as invalidating Build entry before a second freeze -> no stale brief or receipt crosses the boundary
- A6 [experience] covers: S1 · the author needs a runnable next step; taking the result as Build fix/run or Direction revise/interview/refreeze with the cause named -> the route is visible in `status` and the record

## PLAN
contract: expose one Task repair route with `implementation | change | unknown` cause classes, compare the old freeze's structural contract and scoped authority inputs, and append a cause-bearing return stamp. An implementation declaration cannot override observed drift. A return to Direction preserves prior stamps but resets Build entry until a later freeze/refreeze. `freeze` continues to compute its authority; the route never issues a human/security signature.
strategy: seal scope alongside the current direction/binding digests for new freezes; compare all sealed surfaces before choosing Build; make the current beat and Build-entry readers respect a Direction return. Preserve legacy freeze behavior explicitly as unknown rather than retroactively treating missing scope snapshots as clean.
regression: affected · python3 -m pytest add-method/tests/engine/test_repair_or_contract_change.py -q · run the full engine suite after implementation because freeze, brief, run and gate are shared readers

## EDGES
- E1 Given a frozen Task whose check fails because code rejects a valid input but no approved surface moved · When an implementation repair with a concrete cause is routed · Then the Task stays in Build and its cause is stamped
- E2 Given a frozen Task whose Must, Reject, check, `gives:` or scope changed · When the builder claims an implementation repair · Then it cannot remain in Build, and Direction/refreeze is named
- E3 Given unchanged text but a requirement silence discovered in Build · When unknown is routed · Then Direction is recorded and the prior freeze cannot authorize a run/gate
- E4 Given a Direction return on a human-floor Task · When the old signer or a process claim attempts to resume Build · Then refreeze requires the freshly computed human floor

## CHECKS
- test_same_contract_defect_records_cause_and_stays_build · covers: M1, R:CAUSELESS, E1 · acceptance
- test_drift_cannot_be_called_implementation_and_returns_direction · covers: M2, R:SEAL_TOUCH, E2 · acceptance
- test_scope_move_returns_direction_and_recomputes_authority · covers: M2, M4, E2, E4 · acceptance
- test_unknown_requirement_returns_direction_and_old_seal_cannot_run · covers: M3, M4, R:OLDSEAL, E3 · acceptance
- test_existing_replan_preserves_seal_as_steering_control · covers: A1 · control
red-first: `python3 -m pytest add-method/tests/engine/test_repair_or_contract_change.py -q` must fail the four acceptance routes before Build; the old `replan` control must pass.

## EVIDENCE
receipt: pending — Direction-only RED evidence follows in the working report
gate: pending — no approval or Build authorization is inferred from this draft

## LESSONS
none yet
