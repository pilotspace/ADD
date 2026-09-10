---
type: Task
title: freeze refuses with one falsy shape
status: done
depth: quick
milestone: rules-that-hold-for-us
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/test_one_refusal_shape.py
  - add-method/tests/engine/test_freeze_seal.py
  - add-method/tests/engine/test_milestone_freeze_is_interviewed.py
gives:
  - S1 freeze()'s return contract: the (node, message) pair every caller destructures
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: freeze, authority: process, direction: "sha256:3216892a6c058046", binding: "sha256:e9a79d98e3503d91" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:365bc072d4599db6" }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: refreeze, authority: process, direction: "sha256:65a601a24c7f3d3a", binding: "sha256:5b236f0e13444a03" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:7ee046e6806b9ee1" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/one-refusal-shape.d/runs/1.md }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: gate, authority: process, outcome: PASS, receipt: /tasks/one-refusal-shape.d/runs/1.md, brief: "sha256:c34f98cfc12853b4" }
---
## CARD
goal: every refusal rung of freeze hands a caller the same falsy first element, so `node is None` sees all of them
why: two inverted assertions in two different test files, hours apart, both written by a reader who had checked the OTHER rung — the shape is the bug, not the reader
beat: done · next: add status

## RULES
<must>
- M1 every refusal rung of `freeze` returns `None` as its first element — a caller writing `if node is None` sees all of them
- M2 a check ENUMERATES the rungs and drives each one for real, so a rung added later that returns a second shape is caught
- M3 the refusal's message is unchanged by this task — only the falsy first element moves
</must>
<reject>
- R:TWOSHAPES a single verb answers a refusal with two different falsy values -> "TWOSHAPES"
- R:NOTAREFUSAL an empty RESULT (`[]` from a query that ran and matched nothing) is rewritten as if it were a refusal -> "NOTAREFUSAL"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who consumes freeze()'s first element; taking "every caller and every test that destructures the pair, in-repo only — freeze is not part of a published Python API" · found: 170 in-repo `freeze(` sites, mixing two styles — truthiness (`assert node, note` ×7, `assert ok`/`assert not ok`) which is shape-agnostic and safe either way, and IDENTITY (`assert ok is None` ×2, `assert ok is not None`) which is wrong today on the one `False` rung. Nothing outside the repo consumes it. (evidence: grep add-method/tooling add-method/tests) -> a public consumer breaks on an unannounced contract change
- A2 [which] covers: S1 · the request does not say which of the engine's 33 verbs are in; taking "freeze ONLY — the milestone exit names freeze, and the bundle-wide question (11 verbs answer `False`) is a larger idea filed as a delta, not silently annexed" -> the task doubles in size and the exit criterion still is not met
- A3 [when] covers: S1 · the request does not say when a `[]` return is a refusal and when it is an empty result; taking "a rung is a REFUSAL when the verb did not do its work; `neighborhood`/`search`/`interview` return `[]` from a query that ran, and stay untouched" · found: all three sites sit AFTER the work — add.py:647 `if not rows` past the sort, :4224 past the match, :4785 `if not decisions` — each an honest empty result, not a refusal (evidence: add.py:647, :4224, :4785) -> an honest empty result is rewritten as a failure and callers lose the distinction
- A4 [absent] covers: S1 · the request does not say what a MISSING rung means; taking "the enumeration is the check's own list — a rung the check cannot drive is a check defect, not a passing case" -> a rung silently drops out of coverage and the guard reports green on nine of ten
- A5 [order] covers: S1 · the request does not say the order rungs are evaluated; taking "order is irrelevant to the shape — each rung is driven in isolation from a bundle built to reach exactly it" -> a check passes only because an earlier rung shadowed the one under test
- A6 [experience] covers: S1 · the request does not say who reads the failure; taking "the reader is whoever writes the NEXT freeze rung, so the guard fails naming the offending line number and its returned value" -> the guard says only 'shapes differ' and the author greps eleven returns by hand

## PLAN
contract: `freeze()` answers every refusal with `(None, message)`. One line changes — the milestone-scaffold rung at add.py:2244 returns `False` where its ten siblings return `None`. The guard is two-part: a BEHAVIOURAL enumeration that builds a bundle per rung and asserts `node is None` on each, plus a STATIC pass over `freeze`'s own AST asserting no `return <falsy>, ...` in it yields anything but `None` — so a rung added tomorrow cannot reintroduce the second shape without turning the guard red.
strategy: survey first (done: 4 of 33 verbs mix shapes, 3 of them legitimately), then the one-line fix, then the guard.

## EDGES
- E1 the milestone-scaffold rung — the one that returns `False` today; it must return `None` and keep its message byte-identical
- E2 a rung reached only on a Milestone (scaffold, uninterviewed) versus one reached only on a Task (unauthored `gives:`, unswept pairs) — the enumeration must cover both node types
- E3 the SUCCESS return `(node, message)` stays truthy — the fix must not make a successful freeze indistinguishable from a refusal
- E4 an empty-result `[]` elsewhere in the engine is left alone (R:NOTAREFUSAL)
- E5 a caller that asserted `is not None` and was GREEN only because the rung answered `False` — the fix turns it red, and the check's own premise, not its assertion, is what must be re-aimed

## CHECKS
- test_every_freeze_refusal_is_none · covers: M1, M2, M3, A4, A5, E1, E2 · drives each enumerated rung for real and asserts the first element is `None`, naming the rung when it is not
- test_no_freeze_return_is_a_second_falsy_shape · covers: M1, R:TWOSHAPES, A6 · an AST pass over `freeze` alone; fails naming the line number and the value it returned
- test_a_successful_freeze_is_still_truthy · covers: E3 · the PASS path returns a node, so `if node is None` never swallows a success
- test_a_non_lifecycle_node_is_unaffected · covers: E5 · (test_freeze_seal) a Milestone that is genuinely authored freezes — the check no longer passes on a refusal it mistook for a node
- test_nothing_to_ask_is_not_something_to_refuse · covers: E5 · (test_milestone_freeze_is_interviewed) `nothing to ask` re-aimed onto the state that is REACHABLE — a non-human authority — since a human-authority Milestone with zero EXIT boxes is a scaffold and can never freeze
- test_an_empty_result_is_not_a_refusal · covers: R:NOTAREFUSAL, E4 · `search`, `interview` and `neighborhood` still answer `[]` from a query that ran and matched nothing
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/one-refusal-shape.d/runs/1.md · kind: test-ids · 24/24 reported · exit 0 · 2026-09-08
gate: PASS · authority process · by plan:rules-that-hold-for-us · receipt /tasks/one-refusal-shape.d/runs/1.md · 2026-09-08

## LESSONS
- none filed — no lesson cites /tasks/one-refusal-shape.md (add learn <lens> "<lesson>" --evidence /tasks/one-refusal-shape.md)
