---
type: Task
title: The refusals the docs promised, made real
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/tooling/spike_cli.py
  - add-method/tests/engine/test_enforcement_gaps.py
gives:
  - S1 `gate`'s refusal set — which verdicts it declines and what it says
  - S2 `run`'s receipt — the evidence rung it claims for a report
  - S3 `check`'s stamp — the name and the caller context it records
generated: { by: add/3.2.0, at: 2026-08-28 }
verified:
  - { by: "Tin Dang", at: 2026-08-28, act: freeze, authority: human, direction: "sha256:25d3813d66511f70" }
  - { by: "Tin Dang", at: 2026-08-28, act: brief, authority: process, brief: "sha256:ceba2babef90e069" }
  - { by: "process:run", at: 2026-08-28, act: run, authority: process, outcome: PASS, receipt: /tasks/sealed-gate-enforcement.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-28, act: refreeze, authority: human, direction: "sha256:0c0e0ce8b9622f98" }
  - { by: "Tin Dang", at: 2026-08-28, act: brief, authority: process, brief: "sha256:688f76b36f7087f2" }
  - { by: "process:run", at: 2026-08-28, act: run, authority: process, outcome: PASS, receipt: /tasks/sealed-gate-enforcement.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-28, act: gate, authority: plan, outcome: PASS, receipt: /tasks/sealed-gate-enforcement.d/runs/2.md, brief: "sha256:688f76b36f7087f2" }
---
## CARD
goal: Make the enforcement match the claim — every refusal ADD's docs promise is one the engine actually makes.
why: A four-lens adversarial review (method integrity · trust boundary · adoption cost · engine
  architecture) found ADD's mechanical enforcement sitting entirely inside `freeze` and `gate`, and both
  reachable around. The unifying defect: every guard fired on the PRESENCE of a malformed thing and never
  on the ABSENCE of a required one, so the way past each refusal was to DELETE rather than to forge. The
  ONE approval was the clearest case — every post-freeze guard (drift, brief entry, R:UNBRIEFED) was keyed
  off `if sealed:` with no else, so a node that skipped `freeze` did not FAIL those checks, it switched
  them off, and gated PASS with less scrutiny than one that went through the approval.
beat: done · next: add status

## RULES
<must>
- M1 `gate` refuses a PASS on a node carrying no freeze/refreeze stamp, at every Task depth
- M2 `run` claims `kind: test-ids` only for a report written during the run, and says so when it downgrades
- M3 a `scope:` entry that CONTAINS a sensitive path raises the floor, as an exact match does
- M4 `gate` refuses a PASS when a changed file matching `sensitive_paths:` is covered by no scope entry
- M5 a `--reason` cannot delete a stamp from the append-only ledger
- M6 `check` records the caller context beside the claimed name, and `milestone-done` marks unattended credit
</must>
<reject>
- R:UNSEALED a PASS is recorded against a node the human never approved -> "UNSEALED"
- R:STALEEVIDENCE a report that predates the command earns the strongest evidence rung -> "STALEEVIDENCE"
- R:WIDENINGDROPS declaring a BROADER scope lowers the authority a narrower one earned -> "WIDENINGDROPS"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say whose authority a refusal answers to; taking the reading that a refusal binds the ENGINE and never a human writing a stamp themselves -> the notary reads as a blocker
- A2 [who] covers: S3 · the request does not say whether `--by` may be trusted; taking the NAME as a claim and only the CALLER CONTEXT as fact -> a stamp reads as weaker evidence than it did
- A3 [which] covers: S1 · the request does not say which undeclared changes refuse; taking only paths matching `sensitive_paths:`, per the human's answer -> an ordinary undeclared edit still gates
- A4 [which] covers: S2, S3 · the request does not say which runs and ticks the new rules reach; taking ALL of them, with no opt-out flag -> an existing green drive turns red until its fixture is honest
- A5 [when] covers: S1 · the request does not say where the pre-seal tolerance ends; taking a missing DIGEST as tolerated and a missing STAMP as refusable -> a bundle frozen by a pre-3.0 engine still gates
- A6 [when] covers: S2, S3 · the request does not say how fresh a report must be; taking "written at or after the command started" -> a runner whose clock lags loses the ids rung
- A7 [absent] covers: S1, S2 · the request does not say what an absent thing means; taking absence as REFUSAL for the seal and as DOWNGRADE for the report, never as a silent pass -> a runner that writes no junit drops a rung
- A8 [absent] covers: S3 · the request does not say what an absent tty means; taking it as `via: process`, marked unattended, never as a refusal -> a piped tick reads as second-class
- A9 [order] covers: S1 · the request does not say where the new refusals sit; taking the security floor BEFORE the coverage gap, so the more serious fact is reported first -> a node with both faults hears only the lesser one
- A10 [order] covers: S2, S3 · the request does not say what orders the ledger; taking append order AS chronology, which is why a `--reason` may not break the parse -> a sanitised reason loses a brace the author typed
- A11 [experience] covers: S1, S2 · the request does not say who reads a refusal; taking the author mid-build, so every refusal names the missing thing AND the verb that supplies it -> a refusal that only says no
- A12 [experience] covers: S3 · the request does not say who reads the close; taking the reviewer months later, so `milestone-done` marks unattended credit inline rather than in a footnote -> the mark reads as an accusation

## PLAN
contract: four refusals added to `gate`/`run`, one coercion, one sanitiser — no verb removed, no message weakened.
scope: add-method/tooling/{add.py,cli.py,spike_cli.py} + the four engine twins; tests/engine/test_enforcement_gaps.py

## EDGES
- E1 a node frozen by a pre-seal engine (freeze stamp, no digest) must still gate
- E2 a bundle whose parent is not a git working tree must still gate — `_changed_paths` returns `[]`
- E3 a single-entry `scope:` parses as a STRING and must not iterate per character

## CHECKS
- test_gate_refuses_pass_without_a_freeze_seal · covers: M1, R:UNSEALED · the ONE approval is not optional
- test_gate_refuses_without_a_seal_at_quick_depth_too · covers: M1 · quick is ceremony-tuned, not approval-exempt
- test_junit_not_written_during_the_run_downgrades_to_command_exit · covers: M2, R:STALEEVIDENCE · a report that predates the run
- test_junit_written_by_the_command_still_earns_test_ids · covers: M2 · the honest path still works
- test_sensitive_paths_match_through_a_directory_scope · covers: M3, R:WIDENINGDROPS · containment runs both ways
- test_gate_refuses_when_an_undeclared_sensitive_path_changed · covers: M4 · the declared scope vs the real diff
- test_gate_reason_cannot_swallow_the_next_stamp · covers: M5 · the ledger survives a brace
- test_receipt_numbering_never_overwrites · covers: M5 · numbering is max+1, not a count
- test_check_stamp_records_how_it_was_invoked · covers: M6 · tty vs process, beside the claimed name
- test_milestone_done_survives_a_malformed_stamp · covers: M6 · the reporting verb does not crash on one bad entry
- test_check_and_milestone_done_agree_on_exit_boxes · covers: M6 · the ticker and the tally read one boundary
- test_check_refuses_to_tick_a_template_placeholder · covers: M6, R:UNSEALED · unauthored text never releases a gate
- test_a_pre_seal_freeze_without_a_digest_still_gates · covers: E1 · the tolerance is for a missing digest, not a missing stamp
- test_a_bundle_outside_a_git_tree_still_gates · covers: E2 · git silence never invents a refusal
- test_a_single_entry_scope_is_not_iterated_per_character · covers: E3 · a string scope is one entry
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- A guard that fires on a malformed thing and not on a missing one is a guard you get past by deleting -> add learn method
- Every claim in the docs is a test that has not been written yet -> add learn quality
