---
type: Task
title: Four checks gated PASS on claims they cannot test, repaired with floors
status: done
depth: standard
milestone: walk-truth
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/FORMAT.md
  - add-method/tests/engine

gives:
  - S1 the six repaired checks in tests/engine — each one fails when the defect it names is injected, proven by injecting it
  - S2 add.done(...)'s override branch — the seal is checked on the override path itself, not only by the refusal upstream of it
  - S3 FORMAT.md's statement of the walk's ceiling — the cap's VALUE is written down where a reader and a check can both find it
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:walk-truth", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:9782dbdcaa4b6cc4", binding: "sha256:33ee11d29cc8a55d" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:92bccb90d52c04f7" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:92bccb90d52c04f7" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/checks-that-cannot-fail.d/runs/1.md }
  - { by: "plan:walk-truth", at: 2026-09-04, act: gate, authority: process, outcome: PASS, receipt: /tasks/checks-that-cannot-fail.d/runs/1.md, brief: "sha256:f5c67b7a46842332" }
---
## CARD
goal: six checks that pass for the defect they name are repaired, each proven by injecting that defect; and the one real control-flow gap they were hiding is closed.
why: two review agents audited okf-graph-lookup by INJECTING defects rather than reading tests, and found the green was not load-bearing. A pin that reads a value out of the module and then finds it in the module's own source. An assertion whose first disjunct is always true. A cache-independence check that refreshes the cache first. A seal check that never reaches the seal. This repo's whole trust model is that a green gate proves the declared checks ran and passed — a check that cannot fail converts that into a lie, and these shipped inside a milestone that closed 7/7.
beat: done · next: add status

## RULES
<must>
- M1 the walk's ceiling is bound BY VALUE somewhere outside `add.py`, so changing the constant alone turns a check red
- M2 the refusal check reads the verb AFTER the word `add`, so a refusal naming a verb that does not exist turns it red
- M3 the cache-independence check makes the cache DISAGREE with the tree, so a walk that read the cache turns it red
- M4 the payload's field check has a floor asserting an authored key IS emitted, so an empty `fields` turns it red
- M5 one check compares the CLI's `--expand` default against `NEIGHBORHOOD_DEFAULT`, reading both declarations
- M6 the `done` override check reaches the seal: its setup produces a real HARD-STOP gate stamp on a sealed node, so the assertion is about the seal and not about a missing stamp
- M7 `done`'s override branch checks the seal on its own path, rather than relying on `gate` refusing upstream
</must>
<reject>
- R:SELFPIN a check must not read a value out of the code it guards and then look for that value in that same code -> "SELFPIN"
- R:DEADHALF a check must not carry a disjunct that is always true, which makes the other half unreachable -> "DEADHALF"
- R:UNPROVEN a repair must not be recorded as done until the defect it names has been INJECTED and the check observed to fail -> "UNPROVEN"
- R:WIDENING closing the seal gap must not change which nodes `done` accepts today; it removes a reliance, not a guard -> "WIDENING"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S3 · n/a · test and document repairs; no runtime path, no stamp, no authority, no new capability
- A2 [who] covers: S2 · the request does not say whose authority the override answers; taking it UNCHANGED — this task moves where the seal is checked, never who may override -> if wrong, a test repair quietly re-rates an authorization path
- A3 [which] covers: S1 · the request does not say which six; taking the four the vacuity audit demonstrated, the CLI/engine default pair, and the `done` seal check — every one proven by injection, none by reading -> if wrong, a check that merely looks weak is rewritten while a check that cannot fail is left standing
- A4 [which] covers: S3 · the request does not say where the cap's value belongs; taking FORMAT.md, because a reader needs the number and §3.4 already states the walk's other guarantees · probe: FORMAT.md contains no digit for the ceiling today -> if wrong, the number lives only in a test and the document still cannot be checked against the code
- A5 [when] covers: S2 · the request does not say when the seal must be re-checked; taking ON THE OVERRIDE PATH, at the moment the override is honoured — a guard that lives only upstream is a guard one refactor away from absent -> if wrong, the check is defence-in-depth that duplicates an existing refusal for no gain
- A6 [when] covers: S1 · the request does not say when a repair counts as done; taking WHEN THE INJECTION WAS OBSERVED RED, not when the assertion was rewritten — the audit found these precisely because reading a check does not reveal that it cannot fail -> if wrong, a repair is recorded on the same evidence that missed the defect
- A7 [absent] covers: S1 · the request does not say what an absent subject means; taking EVERY repaired check to carry an explicit floor proving its subject is non-empty, so none can degrade to a comparison of two empty things -> if wrong, a repaired check passes over nothing and is vacuous in a new way
- A8 [absent] covers: S2 S3 · the request does not say what happens where a value or a stamp is missing; taking the refusal that exists today, unchanged — an absent gate stamp is already its own message and must not be folded into the seal's -> if wrong, two distinct failures print one message and a reader cannot tell them apart
- A9 [order] covers: S1 S2 S3 · the request does not say what order the repairs land in; taking the injection FIRST in each case, then the repair, then the injection reverted — the check must be observed failing before it is believed -> if wrong, a repair is written against a defect that was never reproduced
- A12 [which] covers: S2 · the request does not say WHICH of `done`'s several guards moves; taking only the SEAL test out of the `elif` chain — the gate-stamp check and the verdict check stay exactly where they are, because each already fires on its own path -> if wrong, a targeted repair becomes a rewrite of an authorization branch
- A13 [when] covers: S3 · the request does not say when FORMAT's ceiling must change; taking WITH the constant, in the same change — a document that lags the code is believed and therefore worse than one that is silent -> if wrong, FORMAT states a ceiling the engine stopped enforcing
- A10 [experience] covers: S1 · the receiver is the next auditor; what would make it hard is not knowing which checks were already attacked, so each repaired check says in its docstring what was injected to prove it -> if wrong, the next audit re-derives this one from scratch
- A11 [experience] covers: S2 S3 · the receiver is a reader asking what bounds this walk and what guards this override; taking the answer written where they look — FORMAT.md for the ceiling, the override branch for the seal -> if wrong, both answers stay reachable only by reading the engine

## PLAN
contract: six checks repaired, each with the injection recorded in its docstring; `NEIGHBORHOOD_MAX`'s value stated in FORMAT.md and pinned by value in a test; `done`'s seal check moved out of the `elif` so the override path evaluates it directly.
strategy: for each of the six, INJECT the defect first and observe the current check pass — that observation is the red. Then repair, observe red, revert the injection, observe green.

## EDGES
- E1 the cap changed to another value turns the FORMAT pin and the value pin red
- E2 a refusal rewritten to name a nonexistent verb turns the refusal check red
- E3 a walk that reads a poisoned graph.json turns the cache check red
- E4 an empty `fields` dict turns the payload check red
- E5 the CLI default changed to disagree with the engine turns the default check red
- E6 a HARD-STOP on a SEALED node plus an override still refuses, and the message names the seal

## CHECKS
- test_the_cap_value_is_pinned_outside_the_engine · covers: M1, R:SELFPIN, E1, A4 · FORMAT.md states the ceiling and a test asserts the constant equals that literal
- test_refusal_names_a_verb_that_exists · covers: M2, R:DEADHALF, E2 · the verb AFTER `add` is read and checked against the parser's choices
- test_walk_ignores_a_poisoned_cache · covers: M3, E3 · graph.json is made to disagree with the tree and the walk still answers from the tree
- test_payload_emits_the_fields_it_has · covers: M4, E4, A7 · an authored key is present, alongside the absent-key assertion
- test_cli_and_engine_agree_on_the_default · covers: M5, E5 · argparse's default is read from the parser and compared to NEIGHBORHOOD_DEFAULT
- test_override_refuses_on_a_sealed_node_with_a_stop · covers: M6, M7, E6, A2 · the setup produces a real HARD-STOP on a FROZEN node, and the refusal names the seal
- test_the_override_path_evaluates_the_seal · covers: M7, R:WIDENING, A5 · the seal is checked on the override branch itself, asserted from the source, and no node accepted today is newly refused
- test_every_repair_records_its_injection · covers: R:UNPROVEN, A6, A9, A10 · each repaired check's docstring names the defect that was injected to prove it
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
