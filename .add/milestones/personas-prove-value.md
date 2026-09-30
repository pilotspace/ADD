---
type: Milestone
title: Personas prove value under a bounded external protocol
status: direction
depth: deep
kind: feature
sensitivity: architecture
generated: { by: add/3.6.0, at: 2026-09-16 }
verified: []
---
## CARD
goal: Establish a reproducible external protocol that can test persona routing value without confusing mechanism proof, model effectiveness, or human governance
why: persona instructions now match the engine mechanically, but that proves only that a selected lens is truthful and reachable. It does not show that selecting a fitting lens improves task outcomes, avoids severe misses, or earns its repair and token cost; an unbounded or post-hoc study could turn ordinary model variation into a product claim.
next: keep C2 separate: approve and pin one funded live-model protocol before invoking a model, then report task-level results without borrowing fixture authority.

## SCOPE
In: a versioned persona-evaluation corpus and protocol; acceptable-persona sets and explicit no-fit cases; neutral, routed-correct and plausible-wrong conditions; repeated task-level allocation; strict provenance, isolation, cap and reporting controls; deterministic fake-agent proof of the mechanism.
Out: paid or live model runs; a finding that personas are effective; changing Persona routing or instructions; changing `add.eval-trial/1`; human-governance recruitment, comprehension trials or authority decisions.

## GROUND
touches: benchmark/persona_eval/ · benchmark/tests/test_persona_eval_*.py · .add/tasks/persona-eval-protocol-harness.md
risks:
  - a fixture-green harness can be misreported as evidence that personas improve real model outcomes
  - condition-specific prompt, model, tool, budget, workspace or oracle differences can masquerade as a persona effect
  - post-hoc sample growth or a cap checked after invocation can spend beyond authorization and bias the reported result
  - treating probes or repetitions as independent tasks inflates the sample and hides task-level harm

## EXIT
- [x] C1 a strict dry-run-first harness freezes the corpus, allocation, provenance, isolation, prospective cap and task-level report semantics for neutral, acceptable routed and plausible-wrong persona conditions, with explicit no-fit behavior and discriminating fake-agent fixtures   (← persona-eval-protocol-harness · receipt 6 · T2 97/97 · plan PASS)
- [ ] C2 any later GPT-5.6 execution uses a separately approved pinned protocol and reports observed model effectiveness without converting mechanism fixtures into an empirical claim   (← future model-trial task)
- [ ] C3 any human governance study has its own participant protocol, authority and outcomes and consumes neither model trials nor persona agreement as a governance decision   (← future human-governance task)

## CLOSE
evidence: C1 requires the exact red-to-green fixture receipt and independent review; C2 and C3 remain pending until separately authored Tasks collect their own evidence.
