---
type: Task
title: every covers: referent class is inside the freeze seal
status: direction
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 add.binding_digest() — the seal over the referent set
  - S2 the gate refusal when a frozen obligation was retired
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-02, act: freeze, authority: human, direction: "sha256:6093581b4397061a", binding: "sha256:33682cbd80ad5626" }
  - { by: "Tin Dang", at: 2026-09-02, act: brief, authority: process, brief: "sha256:192cf0d06535c1fe" }
---
## CARD
goal: every class of id the gate binds is inside a freeze seal.
why: measured — deleting a frozen `E1` and unprobing `A1` post-freeze gated clean.
beat: direction · next: add freeze seal-covers-what-binds

## RULES
<must>
- M1 retiring a frozen edge or unprobing a frozen assumption is refused as drift
- M2 the refusal binds every verdict, because it protects the record not the evidence
- M3 rewording a referent without retiring it is NOT drift
- M4 a refreeze records the change and clears the refusal
- M5 a node frozen before this field shipped still gates
</must>
<reject>
- R:SHEDBIND a frozen contract sheds an obligation without the change appearing in the record -> "SHEDBIND"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who may retire an obligation; taking anyone who can refreeze, since the freeze already carries the authority -> a process actor could shed a human-approved obligation, which the floor governs separately · probe: the refusal fires regardless of the stamping authority
- A2 [which] covers: S1, S2 · the request does not say which surface to seal; taking the REFERENT SET only, not the prose around it -> over-sealing makes authors refreeze reflexively and the seal decays · probe: a reword that retires nothing is accepted
- A3 [when] covers: S1, S2 · the request does not say whether to widen `direction:` or add a field; taking a SECOND digest -> widening would re-digest every already-frozen node and strand it · probe: direction_digest does not move when EDGES change
- A4 [absent] covers: S1, S2 · the request does not say what an absent `binding:` means; taking "cannot verify", never "verified dirty" -> a pre-seal node would be stranded · probe: a stamp with no binding field still gates
- A5 [order] covers: S1, S2 · the request does not say which freeze is read when several exist; taking the most recent, matching sealed_direction -> n/a, the existing reader sets the precedent · probe: sealed_binding reads the latest freeze/refreeze
- A6 [experience] covers: S1, S2 · the request does not say who reads the refusal; taking the builder who just deleted the line -> "drifted" alone does not say WHICH kind of thing moved · probe: the refusal names edges and probed assumptions, not just "drift"
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `binding_digest(node)` digests the sorted set of real `E<n>` ids and probed `A<n>` ids. `freeze` writes it as `binding:` beside `direction:`. `gate` refuses, in the same integrity tier as `drift`, when a recorded `binding:` no longer matches. Absent field = n/a.
scope: add-method/tooling/add.py, add-method/tests/engine/test_seal_covers_what_binds.py

## EDGES
- E1 the measured attack: delete the `E1` line entirely
- E2 the measured attack's other half: strip `· probe:` so the assumption stops binding
- E3 a stamp written by a pre-seal engine, carrying no `binding:` at all

## CHECKS
- test_the_fixture_binds_both_unsealed_classes · covers: M1 · the fixture really carries E and probed A ids
- test_deleting_a_frozen_edge_is_drift · covers: M1, E1 · the measured repair is refused
- test_unprobing_a_frozen_assumption_is_drift · covers: M1, E2, A6 · retiring a probe is a contract change
- test_the_drift_refusal_binds_every_verdict · covers: M2, A1 · not PASS-only
- test_refining_the_prose_around_a_referent_is_not_drift · covers: M3, A2 · the seal does not over-reach
- test_a_refreeze_records_the_change_and_clears_it · covers: M4, A5 · the repair path works
- test_a_node_frozen_before_the_seal_still_gates · covers: M5, E3, A4 · no node is stranded
- test_the_direction_digest_is_unchanged · covers: M5, A3 · the existing seal did not move
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- what a gate BINDS and what a freeze SEALS must be the same set, or the cheapest repair is to delete the obligation -> add learn add
