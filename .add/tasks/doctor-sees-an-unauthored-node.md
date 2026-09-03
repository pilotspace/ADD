---
type: Task
title: doctor sees an unauthored node
status: done
kind: feature
depth: quick
gives:
  - S1 add.doctor() — the unauthored_node finding
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:799892880c2c82dc", binding: "sha256:66eb975a05423ae8" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:5c1e5f2461589fbd" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/doctor-sees-an-unauthored-node.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/doctor-sees-an-unauthored-node.d/runs/1.md, brief: "sha256:7879bee800992f8b" }
---
## CARD
goal: `doctor` reports a node still standing in its scaffold instead of reporting no findings.
why: measured — on a bundle whose only task is 100% template, `doctor` prints "no findings"; `placeholders_in` already detects exactly this and only the gate calls it, so the verb people run to ask "is my bundle OK" answers yes over a bundle nobody has authored.

## RULES
<must>
- M1 `doctor` reports a finding for a node whose RULES, ASSUMPTIONS or CHECKS still hold template tokens
- M2 the finding names the node and at least one standing token, so the author knows where to write
- M3 an authored node produces no such finding
- M4 the finding reuses `placeholders_in` — the oracle the gate already trusts — rather than a second detector
</must>
<reject>
- R:GREENBUNDLE a bundle nobody has authored is reported as conformant -> "GREENBUNDLE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · doctor reports and never writes; no authority changes what a scaffold is
- A2 [which] covers: S1 · the request does not say which nodes are in; taking every LIFECYCLE node doctor already walks -> a Persona has no RULES to author, so including it would report a finding no author can clear · probe: a seeded Persona produces no unauthored_node finding
- A3 [when] covers: S1 · the request does not say at what severity; taking `warn`, not `error` -> a fresh scaffold is unwritten, not broken, and an error would make `init` produce a red bundle · probe: the finding's severity is warn
- A4 [absent] covers: S1 · the request does not say what a node with no ASSUMPTIONS section means; taking `placeholders_in`'s own answer, unchanged -> a second reading would let the gate and doctor disagree about the same node · probe: doctor calls placeholders_in rather than re-implementing it
- A5 [order] covers: S1 · the request does not say where the finding sorts; taking doctor's existing per-node order -> n/a, doctor's output is already sorted by cid
- A6 [experience] covers: S1 · the request does not say who reads it; taking the newcomer who just ran `init` and wants to know what to do -> "no findings" over an unwritten bundle tells them they are done · probe: the finding names a token they must replace

## PLAN
contract: `doctor` calls `placeholders_in` for every lifecycle node and emits a `warn`-severity `unauthored_node` finding naming the node and a standing token. Authored nodes and non-lifecycle types are unaffected.
scope: add-method/tooling/add.py, add-method/tests/engine/test_doctor_sees_an_unauthored_node.py

## EDGES
- E1 a partly-authored node — RULES written, CHECKS still template
- E2 a Persona and a Run, which have no RULES to author

## CHECKS
- test_doctor_reports_a_fully_template_node · covers: M1, A3, R:GREENBUNDLE · the measured "no findings"
- test_the_finding_names_the_node_and_a_token · covers: M2, A6 · the fix is to write the node, so say where
- test_an_authored_node_produces_no_finding · covers: M3 · the guard reports scaffolds, not nodes
- test_a_partly_authored_node_is_still_reported · covers: M1, E1 · one standing token is enough
- test_doctor_and_the_gate_read_the_same_oracle · covers: M4, A4, A2, E2 · one detector, not two
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- an oracle wired to one caller is a guard for one caller; the reader that answers "is this OK" needs it most -> add learn method
