---
type: Task
title: a slug names one node, so a receipt cannot cross nodes
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/tests/engine/
gives:
  - S1 add.new() — the bundle-wide slug collision refusal
  - S2 the receipt stream a task addresses by its bare slug
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-02, act: freeze, authority: human, direction: "sha256:3ddc2d0b42c1059f", binding: "sha256:a12e478238a10bd3" }
  - { by: "Tin Dang", at: 2026-09-02, act: brief, authority: process, brief: "sha256:037c0df48842a7a5" }
  - { by: "process:run", at: 2026-09-02, act: run, authority: process, outcome: PASS, receipt: /tasks/slug-is-unique-across-types.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-02, act: refreeze, authority: human, direction: "sha256:ae283e2f41b6bd7f", binding: "sha256:a12e478238a10bd3" }
  - { by: "Tin Dang", at: 2026-09-02, act: brief, authority: process, brief: "sha256:160af7447a1dda07" }
  - { by: "process:run", at: 2026-09-02, act: run, authority: process, outcome: PASS, receipt: /tasks/slug-is-unique-across-types.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-02, act: gate, authority: plan, outcome: PASS, receipt: /tasks/slug-is-unique-across-types.d/runs/2.md, brief: "sha256:160af7447a1dda07" }
---
## CARD
goal: a slug names one node bundle-wide, so a receipt cannot cross nodes.
why: measured — a red Task walked to done on a Milestone's green receipt.
beat: done · next: add status

## RULES
<must>
- M1 `new` refuses a slug already held by a node of ANY type
- M2 the refusal names the node that holds it
- M3 distinct slugs are unaffected
- M4 a task's latest receipt is always its own
</must>
<reject>
- R:CROSSRECEIPT a gate reads evidence produced by a different node -> "CROSSRECEIPT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who may reuse a slug; taking nobody, since the collision is structural not a permission -> n/a, no authority makes a shared receipt path safe · probe: the refusal is unconditional on authority
- A2 [which] covers: S1, S2 · the request does not say which directories count; taking every directory in TYPE_DIR -> a type added later would silently reopen the hole · probe: the guard iterates TYPE_DIR rather than a hand list
- A3 [when] covers: S1, S2 · the request does not say whether to fix `new` or widen the receipt path; taking `new`, because `_resolve` also silently retargets on a collision -> widening the path alone leaves every other verb ambiguous · probe: the collision itself is refused, not just its receipt effect
- A4 [absent] covers: S1, S2 · the request does not say what happens to bundles that ALREADY hold a collision; taking them as untouched, since `new` guards creation only -> an existing collision keeps its shared stream until renamed · probe: the guard is in `new`, so existing nodes are not rewritten
- A5 [order] covers: S1, S2 · the request does not say which node wins a pre-existing collision; taking scan order, unchanged -> n/a, out of scope for a creation guard · probe: `_resolve` is untouched
- A6 [experience] covers: S1, S2 · the request does not say who reads the refusal; taking the author who just picked a name -> "slug already taken" without the holder's path makes them hunt · probe: the refusal names the holding node's path
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `new` scans every directory in TYPE_DIR for `<slug>.md` before writing, and refuses with the holder's path and R:DUPSLUG. Existing bundles are not rewritten.
scope: add-method/tooling/add.py, add-method/tests/engine/test_slug_names_one_node.py

## EDGES
- E1 the collision in both directions — Task-then-Milestone and Milestone-then-Task
- E2 a Persona sharing a Task's slug, which has no receipt stream of its own

## CHECKS
- test_new_refuses_a_slug_taken_by_another_type · covers: M1, A1, A3 · the collision the per-directory check could not see
- test_the_refusal_names_the_node_that_holds_it · covers: M2, A6 · the fix is to pick another slug, so name the holder
- test_collision_is_refused_in_both_directions · covers: M1, E1, E2, A2 · a bundle-wide census, not a special case
- test_distinct_slugs_are_untouched · covers: M3 · the guard refuses collisions, not creation
- test_a_receipt_cannot_be_earned_by_a_different_node · covers: M4, A4, A5, R:CROSSRECEIPT · the measured walk
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a per-directory uniqueness check is not uniqueness when the addressing scheme is flat -> add learn sdd
