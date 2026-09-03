---
type: Task
title: the tested human-seam bypass is deleted, not documented
status: done
depth: quick
sensitivity: security
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 the census that forbids one call spanning the human seam
  - S2 the removal of add.quick()
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: interview, authority: human, interview: "sha256:07959cf1781fbaea", receipt: /tasks/delete-the-unwired-quick-lane.d/interviews/1.md, answers: "A1=confirm|A2=confirm|A3=confirm|A4=confirm|A5=confirm|A6=confirm|R:BYPASS=confirm" }
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: human, direction: "sha256:edf25662317660ce", binding: "sha256:a12e478238a10bd3" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:0b530abe0b56c30b" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/delete-the-unwired-quick-lane.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: human, outcome: PASS, receipt: /tasks/delete-the-unwired-quick-lane.d/runs/1.md, brief: "sha256:2e4c2c1c589d772b" }
advised_by: gate-security-reviewer
---
## CARD
goal: a tested bypass of the ONE human approval is deleted, not documented.
why: `add.quick()` walked new -> freeze(process) -> run -> gate PASS in ONE call, wired to no verb and kept green by four assertions.
beat: done · next: add status

## RULES
<must>
- M1 no public engine function both opens a node and closes it
- M2 the removal is pinned by SHAPE, not by name, so the lane cannot return under another
- M3 an unreachable writer is deleted or wired, never left tested-but-dead
</must>
<reject>
- R:BYPASS a single call carries a node from creation to closed with no human seam -> "BYPASS"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say whose approval the lane skipped; taking the ONE freeze approval, since `quick` froze at `process` with no authority argument -> a lane that closes at `process` is the seam's whole point defeated · probe: no public function calls both `new` and `done`/`gate`
- A2 [which] covers: S1, S2 · the request does not say which functions to census; taking every PUBLIC function in add.py, since a private helper is reached only through one -> a private bypass would go unseen · probe: the census enumerates ast.FunctionDef names not starting with `_`
- A3 [when] covers: S1, S2 · the request does not say whether to delete or wire; taking DELETE for `quick` — it was reachable from no verb and named in no doc, so nothing depended on it -> deleting a used feature would break callers · probe: zero references remain outside the guard
- A4 [absent] covers: S1, S2 · the request does not say what to do with the OTHER unreachable writer the census found; taking DELETE, per the human — `checks_sync` was the dead WRITER, while `checks_verify` is live (`doctor` calls it for `checks_citation`) and stays -> deleting both would have removed a shipped check · probe: `checks_sync` is gone, `checks_verify` still runs under doctor, and the census passes with no xfail
- A5 [order] covers: S1, S2 · the request does not say whether the guard or the deletion lands first; taking the guard FIRST so it is observed red -> a guard written after the fact proves only that the code compiles · probe: the guard names the shape, not `quick`
- A6 [experience] covers: S1, S2 · the request does not say who reads the census failure; taking the engineer adding a convenience verb months from now -> a bare "assertion failed" teaches nothing · probe: the message names the function, its line, and both call sets
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `add.quick()` is removed with its four assertions. An AST census over every public function in add.py refuses any that calls both `new` and `done`/`gate`; a second census reports a writer reachable from neither the CLI nor another engine function.
scope: add-method/tooling/add.py, add-method/tests/engine/

## EDGES
- E1 a writer another engine function calls is an internal step, not a lane of its own
- E2 `gate` calls `done` to auto-close a PASS — it opens nothing, so it must not trip the census

## CHECKS
- test_no_public_function_both_opens_and_closes_a_node · covers: M1, M2, R:BYPASS, A1, A2, A5, A6, E2 · the shape, not the name
- test_every_public_function_is_reachable_or_a_library_read · covers: M3, A4, E1 · the second census, now passing outright
- test_both_type_oracles_agree_on_the_census · covers: M3 · a type the engine emits that one oracle does not know
- test_the_deleted_lane_is_gone · covers: M2, A3 · the specific function, pinned so it cannot return

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a tested bypass is one refactor away from being reachable; delete it and pin the SHAPE -> add learn add
