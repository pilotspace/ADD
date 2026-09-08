---
type: Task
title: a scope guard names the range it guards
status: done
depth: quick
milestone: rules-that-hold-for-us
scope:
  - add-method/tests/skill/test_claimed_output_guard.py
  - add-method/tests/engine/test_cut_flags.py
  - add-method/tests/engine/test_scope_guard_ranges.py
gives:
  - S1 the suite's scope-tripwire shape: what a check may assert about a file it claims was not changed
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: freeze, authority: process, direction: "sha256:c6a04091074da4d5", binding: "sha256:e9a79d98e3503d91" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:4b0c835645af4d2f" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-guard-names-its-range.d/runs/1.md }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: gate, authority: process, outcome: PASS, receipt: /tasks/scope-guard-names-its-range.d/runs/1.md, brief: "sha256:e9e47b650d40ed0a" }
---
## CARD
goal: no guard in the suite is satisfied by running `git commit`, and none diffs a path git cannot see
why: `test_no_engine_output_was_added` reports RED on every branch that touches the engine for any reason, and GREEN the moment you type `git commit` — it guards the working tree, not the claim. It has failed once per session all week and been dismissed once per session, which is what a guard nobody believes costs
beat: done · next: add status

## RULES
<must>
- M1 no check in the suite is satisfied by running `git commit` — a guard that goes green on a commit guards the working tree, not the claim
- M2 no check diffs a path git cannot see: a guard aimed at a gitignored or absent path asserts its PREMISE instead, so a restored subject turns it red
- M3 a meta-check ENUMERATES every `git diff` in the suite and holds each one to M1 and M2 — the shape cannot be written again without turning it red
- M4 a retired guard leaves a record naming what it protected and why the claim is settled — a check deleted in silence is a claim withdrawn in silence
</must>
<reject>
- R:COMMITCLEAN a check whose subject is a working-tree diff, so `git commit` alone makes it pass -> "COMMITCLEAN"
- R:BLINDPATH a check that diffs a path git does not track, so it reports success for every possible working tree -> "BLINDPATH"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who reads a scope-guard failure; taking "whoever is mid-branch on unrelated work — so a guard must not fire on them at all, rather than fire and be dismissed" -> the guard trains its reader to ignore it, which is worse than not shipping it
- A2 [which] covers: S1 · the request does not say which guards are in; taking "every `git diff` call in the suite — three, all of the broken shape; no legitimate range-named guard exists to preserve" · found: tests/skill/test_claimed_output_guard.py:367 (working-tree, R:COMMITCLEAN), tests/engine/test_cut_flags.py:68 (working-tree AND gitignored AND the file is absent), tests/engine/test_evidence_ids.py:126 (already re-aimed onto its premise in an earlier task — the pattern to copy) (evidence: grep -rn "git diff" add-method/tests) -> a guard is left in the broken shape and the meta-check goes red on the first run
- A3 [when] covers: S1 · the request does not say when a scope claim stops being checkable; taking "at MERGE — `this task did not touch X` is settled once the branch lands, and no diff can re-litigate it, so the guard is retired with a record rather than re-aimed at a range that is empty by construction" -> the guard is 'fixed' into a range diff that is vacuously empty forever, trading one silent pass for another
- A4 [absent] covers: S1 · the request does not say what a MISSING subject means; taking "an absent or untracked path is a premise assertion (the evidence_ids pattern), never a diff" -> the guard reports success because git returned nothing, which is the R:BLINDPATH failure itself
- A5 [order] covers: S1 · the request does not say how the meta-check treats a legitimate future range diff; taking "a `git diff` naming an explicit revision RANGE (`A...B` or `A..B`) is allowed; only a bare working-tree or `HEAD` diff is refused" -> a real range guard cannot be written later without editing the meta-check
- A6 [experience] covers: S1 · the request does not say what the meta-check says when it fires; taking "file, line and the offending argv, plus the two legal alternatives (name a range, or assert the premise)" -> the author is told a shape is wrong and not what to write instead

## PLAN
contract: two guards retired with a recorded reason, and one meta-check that makes the shape unwritable. `test_no_engine_output_was_added` and `test_gated_node_untouched` both claim a MERGED task did not touch a file — settled at merge (A3), and the second is vacuous three times over (working-tree, gitignored path, absent file). They are replaced by `test_no_scope_guard_is_satisfied_by_a_commit`, which walks every test module's AST for a `git diff` invocation and refuses one whose arguments name no revision range.
strategy: write the meta-check first and let it name its own offenders; retire what it names.

## EDGES
- E1 a `git diff` whose args include an explicit range (`main...HEAD`) — allowed, and the meta-check must say so
- E2 a `git diff --name-only HEAD -- <gitignored path>` — refused, and the message must name BOTH faults, not stop at the first
- E3 the meta-check must scan itself without flagging its own string literals — it names `git diff` in prose and in its own message
- E4 a retired check leaves its reason in the file it left, not only in a commit message nobody greps

## CHECKS
- test_no_scope_guard_is_satisfied_by_a_commit · covers: M1, M3, R:COMMITCLEAN, A5, A6, E1, E3 · the meta-check: every `git diff` in the suite names a revision range, or the check fails naming file, line and argv
- test_no_guard_diffs_a_path_git_cannot_see · covers: M2, R:BLINDPATH, A4, E2 · a guard aimed at an untracked or absent path asserts its premise, and the premise assertion goes red when the subject returns
- test_the_retired_guards_left_a_record · covers: M4, A3, E4 · both retired checks name what they protected and why the claim is settled, in the module they were removed from
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
