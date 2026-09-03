---
type: Task
title: an advisory nudge names a node you can still advise
status: done
depth: quick
kind: feature
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 <the surface this publishes — an endpoint, function, or section>
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:9fdf0952e0e1351f", binding: "sha256:66eb975a05423ae8" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:37c7474b66d9eac4" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/doctor-nudges-what-you-can-act-on.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/doctor-nudges-what-you-can-act-on.d/runs/1.md, brief: "sha256:13e8cfbf6dc13b5b" }
---
## CARD
goal: `unadvised_sensitive` reports only nodes that can still take a lens, so `doctor`'s output is the set of things you can act on.
why: measured 2026-09-03 on this bundle — 23 of doctor's 25 findings are `unadvised_sensitive`, and every one names a task already `done`. The advice each gives ("advise it") is unreachable: the node is closed, its gate is stamped, and re-opening it to attach a retrospective lens is not something anyone will do. A reader learns to skim the whole report, which is how the two findings that ARE actionable get missed.

## RULES
<must>
- M1 `unadvised_sensitive` is not reported for a node whose status is `done`
- M2 an OPEN sensitive node with no lens is still reported, at the severity it has today
- M3 the severity split is untouched — `security` stays `warn`, the softer floors stay `info`
- M4 no other finding changes which nodes it reports
</must>
<reject>
- R:BLINDCLOSE a closed node hides a finding that was never about the lens at all -> "BLINDCLOSE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · the report is the same for every reader; no authority sees a different finding set
- A2 [which] covers: S1 · the request says "open nodes" and does not say which statuses count as open; taking `done` as the ONLY exclusion -> a node in `verify` can still be advised before its gate, and excluding it would hide a finding while it is still actionable · probe: a `verify` node with no lens is still reported
- A3 [when] covers: S1 · the request does not say whether to drop the closed ones or tally them; taking DROP -> a tally line is still a line the reader must decide to ignore, and the archived record is the node itself, which keeps its own frontmatter · probe: no summary line replaces the dropped findings
- A4 [absent] covers: S1 · the request does not say what an ABSENT status means; taking absent-as-open -> a node with no status has not been closed, and hiding a finding on a malformed node is R:BLINDCLOSE · probe: a node with no `status:` is still reported
- A5 [order] covers: S1 · n/a · the finding is emitted inside one sorted pass and the exclusion does not reorder it
- A6 [experience] covers: S1 · the request is about what a reader can ACT on; taking the report as a worklist, not an audit log -> if the archived count matters later it is recoverable by reading the bundle, which is where it already lives · probe: the finding count on this bundle drops to the actionable set

## PLAN
contract: `doctor`'s `unadvised_sensitive` loop skips a node whose `status:` is `done`. Every other condition — type, sensitivity floor, lens presence, severity split — is unchanged, and no other finding is touched.

## EDGES
- E1 a node with no `status:` at all — absent is not closed
- E2 a `security` node that is done — the HARD floor does not survive closure either, or M1 is not a rule

## CHECKS
- test_a_done_node_is_not_nudged_for_a_lens · covers: M1, A3, A6 · the 23 measured findings
- test_an_open_node_is_still_nudged · covers: M2, A2 · the finding must not go silent
- test_a_node_with_no_status_is_still_nudged · covers: A4, E1, R:BLINDCLOSE · absent is not closed
- test_the_severity_split_survives · covers: M3, E2 · security warns while open, silent when done
- test_no_other_finding_changed_its_reach · covers: M4 · the exclusion is scoped to one finding
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a report is read as a worklist whether or not it was written as one -> add learn method
