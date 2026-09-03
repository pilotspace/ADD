---
type: Task
title: scope is written where its readers look
status: done
kind: refactor
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 the Task scaffold's `scope:` slot
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: human, direction: "sha256:ab1ffc9d4b028e95", binding: "sha256:66eb975a05423ae8" }
  - { by: "Tin Dang", at: 2026-09-03, act: refreeze, authority: human, direction: "sha256:f0f1b7e3cfd6c1ef", binding: "sha256:66eb975a05423ae8" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:4ba23b6a3e3e50df" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-is-where-its-readers-look.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: plan, outcome: PASS, receipt: /tasks/scope-is-where-its-readers-look.d/runs/1.md, brief: "sha256:ba20d9fc6d9b955f" }
  - { by: loop, at: 2026-09-03, act: reopen, to: direction, reason: "M4 and S2 name a phantom_scope that does not exist: it is a gate refusal keyed on the CARD claiming a scope the frontmatter lacks, not a doctor code and not path existence. Both binding checks are vacuous — one filters doctor() for a code doctor cannot emit, the other is a tautology over what the test itself wrote." }
  - { by: "Tin Dang", at: 2026-09-03, act: refreeze, authority: human, direction: "sha256:5dc864420723f603", binding: "sha256:e95a8e7843701b58" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:2063ae6eabcebe08" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-is-where-its-readers-look.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-03, act: refreeze, authority: human, direction: "sha256:d3c9577b3a7cbb5a", binding: "sha256:e95a8e7843701b58" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:959e2a214435fe04" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-is-where-its-readers-look.d/runs/3.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: plan, outcome: PASS, receipt: /tasks/scope-is-where-its-readers-look.d/runs/3.md, brief: "sha256:959e2a214435fe04" }
---
## CARD
goal: `new` offers the `scope:` slot in frontmatter, where every reader looks, so a declared scope is a read scope.
why: measured — the Task scaffold's only `scope:` slot sits in `## PLAN`; the sole reader is `fm.get("scope")`. Fill the slot the template offers and the gate answers "the node declares no `scope:`", so the slot consumes the author's attention and returns nothing.

## RULES
<must>
- M1 `new` writes a `scope:` slot into a Task's frontmatter
- M2 the `## PLAN` section no longer offers a slot no reader reads
- M3 a node whose frontmatter `scope:` is filled is read by `scope_digest` and by the freshness check
- M4 RETIRED — the `phantom_scope` it named does not exist; the engine keys that refusal on the CARD, never on path existence, and a check proves the retirement rather than asserting it
- M5 every node already carrying a frontmatter `scope:` is unaffected
</must>
<reject>
- R:DEADSLOT a template offers a slot whose value no reader reads -> "DEADSLOT"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · the slot's location is structural; no authority moves where a reader looks
- A2 [which] covers: S1 · the request does not say whether Milestones get the same slot; taking Tasks only, since `scope:` drives the receipt digest and only a Task earns a receipt -> a Milestone slot would be a second dead slot, the defect itself · probe: a new Milestone has no frontmatter scope slot
- A3 [when] covers: S1 · the request does not say whether to seed the slot empty or with a placeholder; taking EMPTY, against the `gives:` precedent — measured: a placeholder turned 29 green tests red, because every reader then sees a declared scope and degrades freshness or refuses an edit outside it -> `gives:` is descriptive and `scope:` is ENFORCED, so the reasoning that made a placeholder right there makes it wrong here; the KEY's presence in frontmatter is the prompt, and its emptiness is what every reader already means by no scope · probe: a fresh node declares no scope and draws no freshness note
- A4 [absent] covers: S1 · the request does not say what an unfilled slot means; taking it as no scope declared, which every reader already does -> a seeded value read as a real declaration would degrade freshness and refuse edits on every fresh node · probe: a fresh node's `scope:` is falsy to `fm.get("scope") or []`
- A5 [order] n/a · frontmatter key order is set by the existing `order` list, which already places `scope` before `gives`
- A6 [experience] covers: S1 · the request does not say who reads the slot; taking the author filling in a fresh node top to bottom -> a slot in `## PLAN` reads as the place scope belongs and they will not look for a second one · probe: exactly one scope slot exists in a fresh node

## PLAN
contract: `new` seeds a Task's frontmatter with an EMPTY `scope:` key, and the `## PLAN` body no longer carries a `scope:` line. An empty scope is what every reader already means by none declared, so a fresh node degrades nothing and refuses nothing; a filled one is read by `fm.get("scope")` and digested by `scope_digest`.
scope: add-method/tooling/add.py, add-method/tests/engine/test_scope_is_where_its_readers_look.py

## EDGES
- E1 a node written before this change, carrying a `## PLAN` scope line and no frontmatter one
- E2 the seeded empty value, which must never be read as a declared scope
- E3 a CARD that claims a scope the frontmatter lacks — the REAL `phantom_scope`, untouched by this task

## CHECKS
- test_a_fresh_task_carries_a_frontmatter_scope_slot · covers: M1, A6 · the slot where readers look
- test_the_plan_body_offers_no_scope_slot · covers: M2, A6, R:DEADSLOT · one slot, not two
- test_a_filled_scope_is_read_by_its_readers · covers: M3, A2 · declared is read
- test_a_fresh_node_is_not_reported_as_misdeclared · covers: M5, A4, E1, E2 · the seeded value is not a scope
- test_the_real_phantom_scope_predicate_is_the_card · covers: M4, E3 · pinned from source: the retired Must is retired because the engine does not do it
- test_a_fresh_node_declares_no_scope · covers: A3, M5 · the measured regression: 29 tests red on a placeholder
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a template slot no reader reads is worse than a missing one: it consumes the author's attention and returns nothing -> add learn method
- I attached a second claim to a true finding without reading the guard I named: `phantom_scope` is keyed on the CARD, not on path existence, and both checks I wrote for it were vacuous. A guard's NAME is not its predicate -> add learn method
