---
type: Task
title: a kind is from the closed taxonomy
status: done
kind: feature
depth: quick
gives:
  - S1 add.new() — the unreadable-kind refusal
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:85e198bf2ab521c3", binding: "sha256:66eb975a05423ae8" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:a6501419f6654db7" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/a-kind-is-from-the-taxonomy.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/a-kind-is-from-the-taxonomy.d/runs/1.md, brief: "sha256:edb5c1f6089db763" }
---
## CARD
goal: `new` refuses a `kind:` outside the closed taxonomy and names the taxonomy.
why: measured — `--kind frontend` is accepted and `doctor` reports no findings; the routing guard validates the Persona's `task-kinds:` and never the Task's `kind:`, so the two sides of the match are held to different standards.

## RULES
<must>
- M1 `new` refuses a `kind:` that is not in PERSONA_TASK_KINDS
- M2 the refusal names the closed taxonomy, so the fix is readable from the message
- M3 every kind in the taxonomy is still accepted
- M4 an absent `kind:` is untouched — the field is optional, and absence is not an unreadable value
</must>
<reject>
- R:SILENT_KIND a kind the router can never match is recorded as if it routed -> "SILENT_KIND"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · the taxonomy is closed for every author; no authority makes an unroutable kind routable
- A2 [which] covers: S1 · the request does not say which taxonomy is authoritative; taking PERSONA_TASK_KINDS, the same tuple the routing guard reads -> a second list would let the two sides drift again, which is the defect · probe: the guard reads the constant, never a hand list
- A3 [when] covers: S1 · the request does not say whether to refuse at `new` or report at `doctor`; taking `new`, matching the `sensitivity` and `--profile` refusals already shipped -> a finding nobody runs doctor to see is not a guard · probe: the refusal is returned by `new`, before any file is written
- A4 [absent] covers: S1 · the request does not say what an omitted kind means; taking it as untouched -> refusing absence would break every node created without --kind · probe: a node with no kind is still created
- A5 [order] covers: S1 · the request does not say which refusal wins when a node is both a dup slug and a bad kind; taking the existing order, slug first -> n/a, both refuse and write nothing
- A6 [experience] covers: S1 · the request does not say who reads the refusal; taking the author who just typed a plausible-but-wrong word -> "unknown kind" without the list makes them guess again · probe: the refusal enumerates the taxonomy

## PLAN
contract: `new` validates `kind` against PERSONA_TASK_KINDS before writing, refuses with the enumerated taxonomy and R:SILENT_KIND, and writes nothing. Absent kinds are unaffected.
scope: add-method/tooling/add.py, add-method/tests/engine/test_a_kind_is_from_the_taxonomy.py

## EDGES
- E1 the empty string and None — absence, not an unreadable value
- E2 a kind differing only in case, which the router would not match

## CHECKS
- test_new_refuses_a_kind_outside_the_taxonomy · covers: M1, A3, R:SILENT_KIND · the measured `--kind frontend`
- test_the_refusal_names_the_taxonomy · covers: M2, A6 · the fix is to pick a real kind, so list them
- test_every_kind_in_the_taxonomy_is_accepted · covers: M3, A2 · enumerated from the constant, never a hand list
- test_an_absent_kind_is_untouched · covers: M4, A4, E1 · absence is not an unreadable value
- test_a_refused_kind_writes_nothing · covers: M1, A5, E2 · a refusal that left a file behind is not a refusal
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- when two sides of a match are validated to different standards, the unvalidated side is where the drift lands -> add learn method
