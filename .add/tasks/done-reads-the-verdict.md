---
type: Task
title: done refuses a gate whose verdict was not a pass
status: done
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
  - { by: "Tin Dang", at: 2026-09-03, act: interview, authority: human, interview: "sha256:e4747bf3cc7b14b6", receipt: /tasks/done-reads-the-verdict.d/interviews/2.md, answers: "A1=confirm|A2=confirm|A3=confirm|A4=confirm|A5=confirm|A6=confirm|R:STOPSHIPS=confirm" }
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: human, direction: "sha256:dfae07ad68204006", binding: "sha256:33682cbd80ad5626" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:875a671fdff6a713" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/done-reads-the-verdict.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:dfeebe243d5a679c" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/done-reads-the-verdict.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: human, outcome: PASS, receipt: /tasks/done-reads-the-verdict.d/runs/2.md, brief: "sha256:dfeebe243d5a679c" }
advised_by: gate-security-reviewer
---
## CARD
goal: a gate stamp entitles `done` only when the verdict it carries CLOSES.
why: measured — a security task with a red run took `gate HARD-STOP` and then closed.
beat: done · next: add status

## RULES
<must>
- M1 `done` refuses a node whose latest gate verdict is `HARD-STOP`
- M2 the refusal holds at the security floor, where the stop is mandatory
- M3 the refusal names the verdict that caused it and a next verb
- M4 `PASS` and `RISK-ACCEPTED` still close, and a resolving `PASS` after a stop still closes
- M6 a human may force-close a stopped node with `--override "<why>"`, and never without a reason
- M7 `gate` refuses a `HARD-STOP` on a node that was never frozen, and refuses nothing else
- M8 a gate stamp carrying no readable `outcome` still closes
- M9 every file the engine writes is a node its own `doctor` accepts
</must>
<reject>
- R:STOPSHIPS a node closes on a verdict that recorded a finding rather than a shipment -> "STOPSHIPS"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say whether a human may ship over a recorded finding; taking YES but only as a DELIBERATE ACT (`done --override "<why>"`), never from the computed floor — a gate's authority is derived, so on a security node every stop is stamped `human` and authority alone would reopen the measured walk -> an override with no reason would be the floor granting it again, one flag over · probe: a stopped node refuses `done`, and closes under `--override` with a reason recorded
- A2 [which] covers: S1, S2 · the request does not say which gate is read when several exist; taking the ones that POSTDATE the last `reopen` — the human confirmed the existing rule is right, so a reopen clears a stop and the loop's reopen semantics are untouched -> a stale pre-reopen stop would block a reopened node forever · probe: a HARD-STOP before a `reopen` does not block a later PASS
- A3 [when] covers: S1, S2 · the request does not say whether `gate` should ever refuse a stop; taking ONLY the seal — a stop is a RECORD against a node and a record needs the approval that says the node exists (3.3.0's argument for RISK-ACCEPTED), while every evidence refusal stays open so writing a finding never gets hard -> refusing more would make recording a security finding the hard part · probe: `gate HARD-STOP` is refused on an unfrozen node and accepted on a sealed one
- A4 [absent] covers: S1, S2 · the request does not say what an absent `outcome` means on an old stamp; taking it as CLOSING — an engine that recorded no verdict field left nodes that cannot be re-gated, so this fails open rather than stranding them -> an unreadable verdict closes a node nobody could re-verify · probe: a gate stamp with no `outcome` still closes
- A5 [order] covers: S1, S2 · the request does not say which verdict wins when a node carries both; taking the LATEST, so resolving a stop is the normal path -> n/a, this is the measured expectation · probe: a PASS recorded after a HARD-STOP closes the node
- A6 [experience] covers: S1, S2 · the request does not say who reads the refusal; taking it as the builder who just recorded the finding -> a refusal that only says "no" strands them · probe: the refusal names the verdict AND the next verb
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `done` reads each entitling gate's `outcome` against CLOSING_VERDICTS = (PASS, RISK-ACCEPTED). A node whose only post-reopen gates are HARD-STOP is refused with a message naming the verdict and pointing at the resolving PASS. `gate` is untouched: all three verdicts stay recordable.
scope: add-method/tooling/add.py, add-method/tests/engine/test_done_reads_the_verdict.py

## EDGES
- E1 a RISK-ACCEPTED node still needs its separate `done` call and still gets it
- E2 a HARD-STOP recorded before a `reopen` must not block the reopened node's later PASS
- E3 an override answers the VERDICT only — it never buys the ONE human approval

## CHECKS
- test_done_refuses_a_node_whose_only_gate_was_a_hard_stop · covers: M1, A3, A4 · the measured walk, stopped at the verb that writes done
- test_the_security_walk_that_shipped_is_closed · covers: M2 · security floor, red run, HARD-STOP, done
- test_the_refusal_names_the_verdict_and_a_next_verb · covers: M3, A6 · every refusal names its fix
- test_a_pass_after_a_hard_stop_still_closes · covers: M4, A5 · a resolved stop is the normal path
- test_pass_and_risk_accepted_still_close · covers: M4, E1 · the two closing verdicts are untouched
- test_a_hard_stop_before_the_reopen_does_not_block_a_later_pass · covers: E2, A2 · reopen resets the gate
- test_a_human_may_force_close_a_stopped_node_with_a_reason · covers: M6, A1 · the human's resolution
- test_the_override_is_recorded_with_its_reason · covers: M6 · a silent override is the floor again
- test_an_override_without_a_reason_is_refused · covers: M6, R:STOPSHIPS · the decision must be explained
- test_the_override_does_not_bypass_the_seal · covers: M6, E3 · it answers the verdict only
- test_gate_refuses_a_hard_stop_on_a_node_that_was_never_frozen · covers: M7, A3 · a record needs a seal
- test_a_hard_stop_on_a_sealed_node_is_still_always_recordable · covers: M7 · findings stay writable
- test_a_gate_stamp_with_no_readable_outcome_still_closes · covers: M8, A4 · fails open
- test_an_interview_sidecar_is_a_conforming_node · covers: M9, R:UNSCANNABLE · found by this task's own interview
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a guard that asks whether a stamp is well-formed has not asked whether what it attests is true -> add learn add
