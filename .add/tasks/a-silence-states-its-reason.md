---
type: Task
title: a waived sweep dimension states its reason
status: done
kind: feature
depth: standard
gives:
  - S1 add.assumption_sweep() — the waiver that must carry a reason
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:8e515934fc85bfcc", binding: "sha256:e95a8e7843701b58" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:b4b48bebec2c0987" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/a-silence-states-its-reason.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/a-silence-states-its-reason.d/runs/1.md, brief: "sha256:dbeb6c352b8093a8" }
---
## CARD
goal: a dimension retired with `n/a` states why, which is what the function's own docstring already promises.
why: measured — `assumption_sweep` waives on `re.match(r"^n/?a\b", rest)` and checks for no reason, while the docstring one line above says "the dimension must be retired with `n/a` and a reason". Code and prose disagree, which is the exact class this branch exists to close.

## RULES
<must>
- M1 a waiver with no reason after `n/a` does not retire its dimension
- M2 a waiver stating a reason still retires its dimension, unchanged
- M3 the refusal names the dimension whose silence is unexplained
- M4 the docstring's promise and the code's behaviour agree — a guard proves it
</must>
<reject>
- R:CHEAPSILENCE a dimension is retired more cheaply than an honest assumption can be written -> "CHEAPSILENCE"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · no authority makes an unexplained silence explained; the requirement is on the text, not on who wrote it
- A2 [which] covers: S1 · the request does not say what counts as a reason; taking any non-empty text after the `·` separator the format already documents, not a length or quality bar -> a quality bar is unjudgeable by a notary and would push authors to pad · probe: a short honest reason is accepted
- A3 [when] covers: S1 · the request does not say whether existing nodes must be repaired; measured first — 4 waivers exist across both bundles and all 4 already state a reason, so the change refuses nothing already written -> had any been bare, the repair would have come before the guard · probe: this repo's own bundle still freezes
- A4 [absent] covers: S1 · the request does not say what a missing `·` separator means; taking it as no reason given -> accepting a run-on would let `n/a because` and `n/aX` both pass · probe: `n/a` with no separator is refused
- A5 [order] n/a · the sweep returns unswept pairs as a set and its ordering carries no meaning
- A6 [experience] covers: S1 · the request does not say who reads the refusal; taking the author who just wrote a waiver and believes the node is done -> naming the dimension without saying a reason is what is missing sends them looking for a surface · probe: the refusal says a reason is what is missing

## PLAN
contract: `assumption_sweep` retires a dimension only when `n/a` is followed by a separator and non-empty text. A bare `n/a` leaves the dimension unswept, and freeze refuses naming it. The docstring's wording becomes the behaviour a check enforces.
scope: add-method/tooling/add.py, add-method/tests/engine/test_a_silence_states_its_reason.py

## EDGES
- E1 `n/a` followed by whitespace only
- E2 `n/a` immediately followed by other text with no separator — not a waiver at all
- E3 all six dimensions waived bare, the total escape the finding describes

## CHECKS
- test_a_bare_n_a_does_not_retire_its_dimension · covers: M1, A4, E1, R:CHEAPSILENCE · the cheap total escape
- test_a_waiver_with_a_reason_still_retires · covers: M2, A2, A3 · every waiver already written stays legal
- test_the_refusal_names_the_unexplained_dimension · covers: M3, A6 · the fix is to write the why, so say which
- test_six_bare_waivers_do_not_empty_the_sweep · covers: M1, E3 · the measured shape of the escape
- test_the_docstring_promise_is_the_behaviour · covers: M4, E2 · code and prose read together, in one check
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- when a docstring states a stricter rule than its code, the docstring is the specification someone already reviewed -> add learn method
