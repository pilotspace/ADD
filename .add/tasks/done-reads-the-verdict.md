---
type: Task
title: done refuses a gate whose verdict was not a pass
status: direction
depth: standard
sensitivity: security
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 add.done() — the verb that writes `status: done`
  - S2 the refusal it prints when the latest verdict does not close
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: interview, authority: human, interview: "sha256:be5498c778037f87", receipt: /tasks/done-reads-the-verdict.d/interviews/1.md, answers: "A1=correct|A2=correct|A3=correct|A4=correct|A5=defer|A6=defer|R:STOPSHIPS=defer" }
---
## CARD
goal: a gate stamp entitles `done` only when the verdict it carries CLOSES.
why: measured — a security task with a red run took `gate HARD-STOP` and then closed.
beat: direction · next: add freeze done-reads-the-verdict

## RULES
<must>
- M1 `done` refuses a node whose latest gate verdict is `HARD-STOP`
- M2 the refusal holds at the security floor, where the stop is mandatory
- M3 the refusal names the verdict that caused it and a next verb
- M4 `PASS` and `RISK-ACCEPTED` still close, and a resolving `PASS` after a stop still closes
</must>
<reject>
- R:STOPSHIPS a node closes on a verdict that recorded a finding rather than a shipment -> "STOPSHIPS"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say whether the stop binds every actor or only `process`; taking it as binding every authority, since the floor already governs WHO may stamp -> a human could not force-close a stopped node without reopening · probe: a HARD-STOP stamped at authority `human` still refuses `done`
- A2 [which] covers: S1, S2 · the request does not say which gate is read when several exist; taking the ones that POSTDATE the last `reopen`, which is the rule `done` already applies -> a stale pre-reopen stop would block a reopened node forever · probe: a HARD-STOP before a `reopen` does not block a later PASS
- A3 [when] covers: S1, S2 · the request does not say whether `gate` should also refuse the stop; taking NO — a security finding must always be recordable -> recording a finding would become the hard part · probe: `gate HARD-STOP` is still accepted on a sealed node
- A4 [absent] covers: S1, S2 · the request does not say what an absent `outcome` means on an old stamp; taking it as not-closing, so an unreadable verdict never entitles -> a pre-3.x stamp needs a re-gate · probe: only verdicts in CLOSING_VERDICTS entitle
- A5 [order] covers: S1, S2 · the request does not say which verdict wins when a node carries both; taking the LATEST, so resolving a stop is the normal path -> n/a, this is the measured expectation · probe: a PASS recorded after a HARD-STOP closes the node
- A6 [experience] covers: S1, S2 · the request does not say who reads the refusal; taking it as the builder who just recorded the finding -> a refusal that only says "no" strands them · probe: the refusal names the verdict AND the next verb
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `done` reads each entitling gate's `outcome` against CLOSING_VERDICTS = (PASS, RISK-ACCEPTED). A node whose only post-reopen gates are HARD-STOP is refused with a message naming the verdict and pointing at the resolving PASS. `gate` is untouched: all three verdicts stay recordable.
scope: add-method/tooling/add.py, add-method/tests/engine/test_done_reads_the_verdict.py

## EDGES
- E1 a RISK-ACCEPTED node still needs its separate `done` call and still gets it
- E2 a HARD-STOP recorded before a `reopen` must not block the reopened node's later PASS

## CHECKS
- test_done_refuses_a_node_whose_only_gate_was_a_hard_stop · covers: M1, A3, A4 · the measured walk, stopped at the verb that writes done
- test_the_security_walk_that_shipped_is_closed · covers: M2 · security floor, red run, HARD-STOP, done
- test_the_refusal_names_the_verdict_and_a_next_verb · covers: M3, A6 · every refusal names its fix
- test_a_pass_after_a_hard_stop_still_closes · covers: M4, A5 · a resolved stop is the normal path
- test_pass_and_risk_accepted_still_close · covers: M4, E1 · the two closing verdicts are untouched
- test_a_hard_stop_before_the_reopen_does_not_block_a_later_pass · covers: E2, A1, A2 · reopen resets the gate
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a guard that asks whether a stamp is well-formed has not asked whether what it attests is true -> add learn add
