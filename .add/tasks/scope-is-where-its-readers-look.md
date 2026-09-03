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
  - S2 phantom_scope — the gate refusal that could not fire
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: human, direction: "sha256:ab1ffc9d4b028e95", binding: "sha256:66eb975a05423ae8" }
  - { by: "Tin Dang", at: 2026-09-03, act: refreeze, authority: human, direction: "sha256:f0f1b7e3cfd6c1ef", binding: "sha256:66eb975a05423ae8" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:4ba23b6a3e3e50df" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-is-where-its-readers-look.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: plan, outcome: PASS, receipt: /tasks/scope-is-where-its-readers-look.d/runs/1.md, brief: "sha256:ba20d9fc6d9b955f" }
---
## CARD
goal: `new` offers the `scope:` slot in frontmatter, where every reader looks, so a declared scope is a read scope.
why: measured — the Task scaffold's only `scope:` slot sits in `## PLAN`; the sole reader is `fm.get("scope")`. Fill the slot the template offers and the gate answers "the node declares no `scope:`", and `phantom_scope` — the refusal for a scope naming paths that do not exist — has never been able to fire on a scaffolded node.

## RULES
<must>
- M1 `new` writes a `scope:` slot into a Task's frontmatter
- M2 the `## PLAN` section no longer offers a slot no reader reads
- M3 a node whose frontmatter `scope:` is filled is read by `scope_digest` and by the freshness check
- M4 `phantom_scope` fires on a scaffolded node whose declared scope names a path that does not exist
- M5 every node already carrying a frontmatter `scope:` is unaffected
</must>
<reject>
- R:DEADSLOT a template offers a slot whose value no reader reads -> "DEADSLOT"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · the slot's location is structural; no authority moves where a reader looks
- A2 [which] covers: S1, S2 · the request does not say whether Milestones get the same slot; taking Tasks only, since `scope:` drives the receipt digest and only a Task earns a receipt -> a Milestone slot would be a second dead slot, the defect itself · probe: a new Milestone has no frontmatter scope slot
- A3 [when] covers: S1, S2 · the request does not say whether to seed the slot empty or with a placeholder; taking EMPTY, against the `gives:` precedent — measured: a placeholder turned 29 green tests red, because every reader then sees a declared scope and degrades freshness or refuses an edit outside it -> `gives:` is descriptive and `scope:` is ENFORCED, so the reasoning that made a placeholder right there makes it wrong here; the KEY's presence in frontmatter is the prompt, and its emptiness is what every reader already means by no scope · probe: a fresh node declares no scope and draws no freshness note
- A4 [absent] covers: S1, S2 · the request does not say what an unfilled slot means; taking it as no scope declared, which every reader already does -> treating the placeholder as a real path would make `phantom_scope` fire on every fresh node · probe: a fresh scaffold earns no phantom_scope finding
- A5 [order] n/a · frontmatter key order is set by the existing `order` list, which already places `scope` before `gives`
- A6 [experience] covers: S1, S2 · the request does not say who reads the slot or the refusal; taking the author filling in a fresh node top to bottom -> a slot in `## PLAN` reads as the place scope belongs and they will not look for a second one, and a `phantom_scope` refusal that names no path leaves them with nothing to correct · probe: only one scope slot exists in a fresh node, and the refusal names the missing path

## PLAN
contract: `new` seeds a Task's frontmatter with an EMPTY `scope:` key, and the `## PLAN` body no longer carries a `scope:` line. An empty scope is what every reader already means by none declared, so a fresh node degrades nothing and refuses nothing; a filled one is read, digested, and can earn `phantom_scope`.
scope: add-method/tooling/add.py, add-method/tests/engine/test_scope_is_where_its_readers_look.py

## EDGES
- E1 a node written before this change, carrying a `## PLAN` scope line and no frontmatter one
- E2 the seeded empty value, which must never be read as a declared scope

## CHECKS
- test_a_fresh_task_carries_a_frontmatter_scope_slot · covers: M1, A6 · the slot where readers look
- test_the_plan_body_offers_no_scope_slot · covers: M2, A6, R:DEADSLOT · one slot, not two
- test_a_filled_scope_is_read_by_its_readers · covers: M3, A2 · declared is read
- test_phantom_scope_fires_on_a_scaffolded_node · covers: M4, S2 · the refusal that never could
- test_a_fresh_scaffold_earns_no_phantom_scope · covers: M5, A4, E1, E2 · the seeded value is not a scope
- test_a_fresh_node_declares_no_scope · covers: A3, M5 · the measured regression: 29 tests red on a placeholder
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a template slot no reader reads is worse than a missing one: it consumes the author's attention and returns nothing -> add learn method
