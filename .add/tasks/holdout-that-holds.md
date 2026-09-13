---
type: Task
title: Can a CLI-only method hold a T4 holdout the builder never reads?
status: direction
depth: standard
kind: explore
milestone: loop-that-closes
scope:
  - add-method/docs
gives:
  - S1 <the surface this publishes — an endpoint, function, or section>
generated: { by: add/3.6.0, at: 2026-09-11 }
verified: []
---
## CARD
goal: answer whether a CI-only ref or an encrypted fixture can earn a receipt the builder never saw, and whether T4 then becomes recordable
why: the research asks for a protected holdout as a shipped mechanism; a CLI-only method cannot hide a file from an agent that reads the repo (verify.md: a prompt is not isolation) — the answer decides the next milestone, not this one
beat: direction · next: add freeze holdout-that-holds

## RULES
<must>
- M1 the explore answers, with a cited mechanism or a cited impossibility, whether a receipt can be produced by checks the building agent cannot read before the gate — a CI-only ref (a branch or ref the runner reads and the agent's checkout lacks), an encrypted fixture (decrypted only in CI), or a third route found on the way
- M2 for each route that produces such a receipt, the explore states how the engine would RECORD it without executing it — which existing stamp (`run` with a receipt the runner wrote, `refute --tier T4` today refused R:BADTIER) or which new claim — and what the record can and cannot bind (FORMAT §10: presence, never honesty)
- M3 the explore names what the builder can still see or influence in each route (the test names in CHECKS, the fixture's shape, the CI config) and rules whether the holdout holds against an agent that reads the whole repo
</must>
<reject>
- R:SHIPPEDHOLDOUT the explore building or shipping a holdout mechanism — it answers, the next milestone decides -> "SHIPPEDHOLDOUT"
- R:UNCITED a finding with no evidence pointer (a file:line, a CI run, a command run here) -> "UNCITED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who the adversary is; taking the building agent with read access to the whole repository and its own CI config, but not to CI secrets -> cost if wrong: an agent with secret access defeats every route; the finding says so
- A2 [which] covers: S1 · the request does not say which CI; taking GitHub Actions as the worked example (this repo's `publish.yml` exists) with the route stated generally -> cost if wrong: another runner needs its own reading; the mechanism, not the YAML, is the finding
- A3 [when] covers: S1 · the request does not say when the holdout runs; taking at the gate — the receipt must exist before `gate PASS`, so the route must run on a push before the verdict -> cost if wrong: a holdout that runs after the gate is a monitor, and observes-slot already has that
- A4 [absent] covers: S1 · the request does not say what "recordable" means when no route works; taking a cited impossibility as a complete answer — the explore's gate judges sufficiency, not success -> cost if wrong: none
- A5 [order] covers: S1 · the request does not say which route to try first; taking the CI-only ref first (no crypto, no secret) then the encrypted fixture -> cost if wrong: none; both are read
- A6 [experience] covers: S1 · the request does not say who reads the findings; the reader is the planner of the next milestone; hard for them is a finding without a next step — taking every F line to end with what a shipped mechanism would need -> cost if wrong: the next milestone re-derives it

## PLAN
contract: three findings F1–F3 answering M1–M3, each cited; a fourth if a third route appears
budget: 25 tool calls · 6 sources · no engine edit

## EDGES
- E1 Given a CI-only ref the agent's checkout lacks · When the runner reads it · Then whether `add run` can record a receipt it did not execute is answered by reading `run`'s receipt shape (`computation:`, `head:`, `committed:`)

## CHECKS
- F1 answers M1 · covers: M1 · a route (or its impossibility) is named with a citation to the runner's docs or a command run here
- F2 answers M2 · covers: M2 · the record's stamp and its binding limit are named against FORMAT §8/§10
- F3 answers M3 · covers: M3 · what the builder still sees is enumerated and the verdict "holds / does not hold" is stated per route
judged at the gate against ## FINDINGS, not by pytest.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## FINDINGS
<empty until the loop runs — then one line per finding:
 F1 (answers M1) · <what was found> · (evidence: <file:line | url | command>)>

## LESSONS
- <lesson> -> add learn <lens>
