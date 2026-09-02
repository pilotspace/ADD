---
type: Task
title: a receipt is never written for a node that does not exist
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 add.run() — the refusal for a node that does not exist
  - S2 the receipt dir a run would otherwise create
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-02, act: freeze, authority: human, direction: "sha256:a9dc6736ea6f7468", binding: "sha256:22249aa61fd2594e" }
  - { by: "Tin Dang", at: 2026-09-02, act: brief, authority: process, brief: "sha256:18c77a4e6dee1ff9" }
  - { by: "process:run", at: 2026-09-02, act: run, authority: process, outcome: PASS, receipt: /tasks/run-refuses-a-phantom-node.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-02, act: gate, authority: plan, outcome: PASS, receipt: /tasks/run-refuses-a-phantom-node.d/runs/1.md, brief: "sha256:0e274effe8a74a90" }
---
## CARD
goal: a receipt is never written for a node that does not exist.
why: measured — `add run auth-fx -- true` on a typo printed `receipt 1 recorded (exit 0)`.
beat: done · next: add status

## RULES
<must>
- M1 `run` refuses an unresolvable cid and writes nothing
- M2 a real node still records its receipt
</must>
<reject>
- R:PHANTOMRECEIPT the engine manufactures the debris `doctor` later reports -> "PHANTOMRECEIPT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A2 [which] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A3 [when] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A4 [absent] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A5 [order] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A6 [experience] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `run` looks the cid up in the graph and refuses like every other verb, keeping its dict return shape so `cli.py` prints a note and exits non-zero.
scope: add-method/tooling/, add-method/tests/

## EDGES
- E1 the orphan_receipt finding `doctor` reported one verb too late

## CHECKS
- test_run_refuses_a_node_that_does_not_exist · covers: M1, R:PHANTOMRECEIPT · the measured typo
- test_run_still_records_for_a_real_node · covers: M2 · the guard refuses phantoms, not runs
- test_the_phantom_refusal_leaves_no_orphan_for_doctor · covers: M1, E1 · no manufactured debris
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- `or {}` on a lookup turns a missing subject into an invented one -> add learn add
