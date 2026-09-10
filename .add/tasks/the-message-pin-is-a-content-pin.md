---
type: Task
title: a refusal message is pinned to content, not to a diff
status: done
depth: standard
kind: test
milestone: checks-that-hold-in-ci
scope:
  - add-method/tests/engine/test_refuse_with_one_shape.py
gives:
  - S1 the baseline `test_the_messages_are_untouched` reads: what it compares the engine's refusal messages against, and what it does when that baseline cannot be established
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:checks-that-hold-in-ci", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:500c3a5247f7e24a", binding: "sha256:a046adc15422753b" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:f0719bbed8236cd3" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/the-message-pin-is-a-content-pin.d/runs/1.md }
  - { by: "plan:checks-that-hold-in-ci", at: 2026-09-10, act: gate, authority: process, outcome: PASS, receipt: /tasks/the-message-pin-is-a-content-pin.d/runs/1.md, brief: "sha256:4d07294c1faee8dd" }
advised_by: engine-notary
---
## CARD
goal: the refusal-message guard holds against a pinned digest of the messages themselves, so it runs on CI's shallow checkout and keeps holding after the branch that wrote it is merged
why: it went red on CI for a reason that has nothing to do with refusal messages: `git merge-base HEAD origin/main` returns 128 on `actions/checkout`'s depth-1 clone, and the check read that as the claim being false. Underneath, its baseline was a merge-base that CONTAINS the change once merged — so the day CI could run it, it would prove nothing
beat: done · next: add status

## RULES
<must>
- M1 the guard resolves its baseline from a pinned digest in the module, never from a git ref, so it runs identically on a shallow clone, a fresh checkout and a working tree
- M2 the claim is UNCHANGED — a refusal message that is reworded or lost turns it red, and the failure names which verb and which message
- M3 the pin records the task that aimed it and the reason, the way `test_skill_tree_prose_unedited_by_this_task` and `engine_pin.py` already do (R:SILENTREPIN)
- M4 the digest is computed from the same `(verb, message)` extraction the check already performs, so there is no second reading of what a refusal message is
</must>
<reject>
- R:SKIPTOGREEN the guard is made to skip, pass, or degrade when its baseline is unavailable — a green that proves nothing is worse than the red it replaces -> "SKIPTOGREEN"
- R:SILENTREPIN the pin is re-aimed with no task and no reason recorded beside it -> "SILENTREPIN"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who re-aims the pin; taking "whoever reworded the message, in the same commit — the failure text tells them to restore the wording or re-aim WITH the reason, which is the only moment the reason is known" -> the pin is re-aimed later by someone reconstructing why, and the record says nothing
- A2 [which] covers: S1 · the request does not say which returns are in the digest; taking "exactly the set `_returns()` already yields — the falsy-first-element two-tuples — because a digest over a different set than the check reads would be a second definition (M4)" · probe: the digest is computed by calling the module's own extractor -> two readings of what a refusal is, and they drift
- A3 [when] covers: S1 · the request does not say when the pin may move; taking "only when a human deliberately changes a message, never to make a build pass — the same rule `engine_pin.py` and the prose pin already live under" -> the pin becomes a build step and stops being a guard
- A4 [absent] covers: S1 · the request does not say what an unavailable git binary means now; taking "nothing at all — the guard no longer runs git, so the whole question is retired rather than answered" · probe: no `subprocess` call remains in this check -> the failure mode is fixed for `origin/main` and left live for every other ref
- A5 [order] covers: S1 · the request does not say how the set is ordered before hashing; taking "sorted, so the digest is a function of the CONTENT and not of the order `ast.walk` happens to yield" -> the digest changes when an unrelated edit moves a function, and gets re-aimed as noise until nobody reads it
- A6 [experience] covers: S1 · the request does not say what the failure tells the author; taking "a digest mismatch cannot name which message moved, so the check reports the COUNT delta and the two exits — restore the wording, or re-aim with the reason" -> the author gets a hex mismatch and re-aims the pin without looking at what changed
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `MESSAGE_DIGEST` — a module-level `sha256` over the sorted `(verb, message)` pairs `_returns()` yields, with the aiming task and reason on the same line.
strategy: compute the digest from the current engine, pin it, delete the git baseline, and prove the check red by rewording one message.

## EDGES
- E1 <a boundary or failure case a check must cover — optional>

## CHECKS
- test_the_messages_are_untouched · covers: M1, M2, M4, A2, A4, A5, A6 · a reworded refusal message turns it red, with no git ref read anywhere
- test_the_pin_records_why_it_points_here · covers: M3, R:SILENTREPIN, A1, A3 · the pin line names the task that aimed it and the reason
- test_the_guard_never_degrades_to_green · covers: R:SKIPTOGREEN · the module contains no skip, no try/except and no early return around the assertion
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
