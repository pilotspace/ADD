---
type: Task
title: the 78 open deltas resolve to folded, rejected or bound
status: direction
depth: quick
milestone: loop-that-drains
scope:
  - .add/specs
gives:
  - S1 five drained lenses — every pre-existing delta folded, rejected or bound, and the decisions those lessons earned
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:742bb025384dc886", binding: "sha256:f9ee0a7a08abbda6" }
---
## CARD
goal: the pile becomes a constitution — every carried lesson resolved, and the ones that settle something written where every future brief reads them
why: the drain and the promotion path now exist and are proven on fixtures. Until they are run on the real backlog, all five specs still report `unauthored` to every worker and `status` still names a number nobody has acted on. This is the sitting the machinery was built for.
beat: direction · next: add freeze backlog-drain

## RULES
<must>
- M1 every delta that was open before this milestone began ends folded, rejected or bound — none is left open and none is deleted
- M2 a lesson whose claim has since been made FALSE by shipped work is rejected, not folded: folding it would record a lesson that still reads as carried truth
- M3 every decision written binds something a future brief can act on, cites the lesson it came from, and is not a restatement of the lesson text
- M4 no delta id is renumbered and no delta line is removed — ids retire in place
</must>
<reject>
- R:BULKFOLD the pile must never be cleared by a blanket fold that writes no decision -> "BULKFOLD"
- R:FALSECARRY a lesson contradicted by shipped work must never be recorded as folded -> "FALSECARRY"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who decides each verdict; taking the reading that the human decides and the agent types, exactly as `fold` has always assumed · probe: every verdict in this task traces to a human answer recorded in the session, not to an agent's judgment
- A2 [which] covers: S1 · the request does not say which lessons deserve promotion; taking the reading that a lesson binds when it constrains FUTURE work rather than explaining a past fix — guard-craft folds, rules bind · probe: each bound decision is stated as a constraint, never as a narrative of what went wrong
- A3 [when] covers: S1 · the request does not say when this runs; taking the reading that it runs AFTER the drain machinery is gated, so the sitting uses the real verbs and dogfoods them -> running it earlier would mean hand edits, which is the failure this milestone exists to end
- A4 [absent] covers: S1 · the request does not say what an undated legacy delta means here; taking the reading that it is resolved like any other — the missing date excuses it from the WINDOW, never from the drain
- A5 [order] covers: S1 · the request does not say what order the lenses are drained in; taking the reading that order is irrelevant to the outcome because each spec is written independently, so the sitting proceeds lens by lens for the reader's sake only
- A6 [experience] covers: S1 · the receiver is the human answering 78 verdicts in one sitting, and what would make this hard is being asked 78 separate questions; taking the reading that the proposal arrives grouped by lens with a recommended verdict per delta, so the answer is an approval or a correction rather than an authoring task · probe: the proposal is presented grouped, with a verdict already proposed for every delta

## PLAN
contract: no engine change and no code. The deliverable is the five drained spec files and the decisions they now carry. Every write goes through `add fold` with its flags — never a hand edit, because a hand-edited drain would prove nothing about the verbs this milestone shipped.

## EDGES
- E1 a delta already made false by shipped work (D1 and M27 are both known cases) is rejected rather than folded
- E2 a lesson that settles a rule reachable by future work is bound, and the spec it lands in stops reporting `unauthored` to `brief`

## CHECKS
- check_no_open_deltas_remain · covers: M1, M4 · `add deltas` reports 0 open, the total line count of delta lines is unchanged from before the sitting, and no id was reused
- check_every_spec_binds_something · covers: M3, E2 · all five specs carry at least one real decision, and `add brief` on a live task reports none of them `unauthored`
- check_false_lessons_were_rejected · covers: M2, R:FALSECARRY, E1 · at least the two lessons known to be contradicted by shipped work read `rejected`, not `folded`
- check_the_drain_was_not_a_bulk_fold · covers: R:BULKFOLD, A2 · the number of bound decisions is greater than zero and every one cites a delta id
red-first: every check MUST fail first — all four are false against the bundle as it stands.

## EVIDENCE
receipt: pending
gate: pending

## LESSONS
- pending
