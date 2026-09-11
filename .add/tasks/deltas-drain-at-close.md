---
type: Task
title: a milestone close drains its own lessons, and a drained lesson can bind
status: done
depth: standard
sensitivity: architecture
milestone: loop-that-drains
scope:
  - add-method/tooling
  - add-method/tests
  - add-method/.add/tooling
  - add-method/src/add_method/_bundled/tooling
  - add-method/skill
  - add-method/src/add_method/_bundled/skill
  - .claude/skills/add
  - .add/tooling
gives:
  - S1 `fold --reject` — the first verb for the `rejected` status, which the grammar has always named and no command could ever produce
  - S2 `fold --bind` — a decision written into a spec's `## Decisions that bind`, citing the lessons it came from
  - S3 the `R:UNDRAINED` rung on `milestone-done`, windowed to the lessons the closing milestone itself filed
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:d1e0882a5a999764", binding: "sha256:3510f4566bf49d20" }
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: refreeze, authority: plan, direction: "sha256:efe54abfca6bf0ef", binding: "sha256:3510f4566bf49d20" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:91376774a64b197f" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/deltas-drain-at-close.d/runs/1.md }
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: gate, authority: plan, outcome: PASS, receipt: /tasks/deltas-drain-at-close.d/runs/1.md, brief: "sha256:492fc5a731d2b9b9" }
---
## CARD
goal: a lesson filed inside a milestone is resolved before that milestone closes, and resolving it can promote it to a decision every later brief reads
why: `rejected` is one of three statuses in a frozen grammar and no command can produce it, so the only honest verdict on a lesson that turned out wrong is a hand edit. `fold` is a status flip that writes nothing anywhere else, so 75 lessons became 75 retagged lines and never once a decision. And every `brief` in this bundle reports all five `## Decisions that bind` as unauthored, which is true and has been true through eighteen closes. This task connects `learn` to `brief`, and puts the drain at the one seam the human already owns.
beat: done · next: add status

## RULES
<must>
- M1 `fold --reject` retags every matched open delta `rejected` and closes its validity interval exactly as a fold does, sharing one code path with the fold so the two verdicts can never drift apart
- M2 `fold --bind` writes the given sentence into that spec's `## Decisions that bind`, citing every delta id the same call retagged, and drops the scaffold line when the scaffold is the only thing there
- M3 `--reject` together with `--bind` refuses: a lesson judged wrong cannot also be a decision that binds
- M4 `milestone-done` refuses `R:UNDRAINED` while an open delta carries a `valid_from` on or after the closing milestone's creation date, naming each one and the flags that resolve it
- M5 the rung never refuses on a delta filed before that date, and never on an undated legacy delta whose filing date the engine does not have
- M6 a milestone whose creation date is unreadable skips the rung and says so in its close note, rather than refusing on a window it cannot compute or passing as though it had
- M7 the rung is reached only after the existing why-gate and goal-gate, so an unmet goal is still the first thing a closer is told
</must>
<reject>
- R:BACKLOGBLOCK the rung must never refuse on a lesson filed before the closing milestone existed -> "BACKLOGBLOCK"
- R:BINDLOSS writing a decision must never drop, reorder or overwrite a decision already there -> "BINDLOSS"
- R:REJECTBINDS a rejected lesson must never reach `## Decisions that bind` -> "REJECTBINDS"
- R:SILENTSKIP a rung that did not run must never leave the close looking as though it had -> "SILENTSKIP"
- R:NEWVERB the drain adds no verb: it is two flags on `fold` and one rung on `milestone-done` -> "NEWVERB"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who may reject or bind; taking the reading that both stay exactly as human-owned as `fold` already is — the engine records the human's call and never decides which lesson is wrong or which sentence binds -> an engine that judged consolidation would be judging the method, which law 3 forbids
- A2 [who] covers: S3 · the request does not say whose lessons a milestone owns; taking the reading that ownership is by DATE and not by authorship or by task, because a lesson filed during a milestone is that milestone's residue whoever typed it · probe: a delta filed by any author inside the window is named by the refusal
- A3 [which] covers: S3 · the request does not say which date anchors the window; taking the reading that it is the milestone's own `generated.at`, discharged by probe rather than by the drafted "or its first verified stamp, whichever is earlier" — creation always precedes every stamp, so the second clause can never change the answer · probe: the anchor equals `generated.at` on a milestone carrying freeze and gate stamps
- A4 [which] covers: S1 · the request does not say which deltas a reject may match; taking the reading that it matches exactly what a fold matches — open, well-formed, substring — so the two verdicts see one set · probe: a reject and a fold given the same match retag the same lines
- A5 [which] covers: S2 · the request does not say which lesson a decision cites when the match hits several; taking the reading that it cites them all, because consolidating several lessons into one decision is the drain working, not an ambiguity to refuse · probe: a bind whose match retags three deltas cites three ids
- A6 [when] covers: S3 · the request does not say whether the boundary is inclusive; taking the reading that a delta filed ON the creation date is IN the window, since a milestone created and taught on the same day is the common case, not an edge · probe: a same-day delta is named by the refusal
- A7 [when] covers: S1, S2 · the request does not say when the decision is written relative to the retag; taking the reading that both land in one write of the spec file, so a decision can never cite a lesson the same call failed to retag -> two writes would allow a decision citing an id that is still open
- A8 [absent] covers: S3 · the request does not say what an undated delta means; taking the reading that no filing date means the engine cannot place it in any window, so it never blocks a close and is instead named in the close note as carried -> inventing a date to make the rung fire would be the fiction `_as_date` already refuses
- A9 [absent] covers: S3 · the request does not say what an absent milestone creation date means; taking the reading that the rung is SKIPPED and the skip is stated, never silently passed (this is R:SILENTSKIP) -> a close that looks drained and was not is worse than one that admits it did not check
- A10 [absent] covers: S2 · the request does not say what an absent `## Decisions that bind` section means; taking the reading that the section is created when missing, because a spec the engine wrote should not have to be repaired by hand before it can hold a decision -> refusing would push the human into the hand edit this task exists to end
- A11 [order] covers: S2 · the request does not say where a new decision goes; taking the reading that it is PREPENDED, matching the newest-first convention `## Deltas` already follows in this corpus -> appending would bury the newest decision under the oldest, the ordering the foundation-compaction milestone already rejected
- A12 [order] covers: S3 · the request does not say where the rung sits among the existing gates; taking the reading that it runs LAST, after why and goal, so the closer never sees a drain refusal while their goal is still unmet (this is M7) -> a rung that jumps the queue re-ranks an already-tuned refusal order
- A13 [order] covers: S1 · the request does not say how ids order when several are retagged at once; taking the reading that they are cited in the order they appear in the file, which is the newest-first order already on disk -> sorting them would impose a second ordering on a file that has one
- A14 [experience] covers: S3 · the receiver is a human at a close who wants to be done, and what would make this hard is a refusal that names a count and no way through; taking the reading that the refusal names each blocking lesson by address AND the three flags that resolve it · probe: the refusal text names fold, --reject and --bind
- A15 [experience] covers: S1, S2 · the receiver is an agent typing what the human decided, and what would make it hard is having to compose an address; taking the reading that both flags take the same substring `fold` already takes, so nothing new must be learned -> a new addressing scheme at the drain would make the batch it exists to enable harder than the hand edit
- A17 [absent] covers: S1 · the request does not say what a reject records when no reason is given; taking the reading that it records none — the delta text already states the lesson and git already states who retired it, so a mandatory reason would be a second place for the same fact -> if a reason proves needed it is an additive flag later, never a change to the frozen head grammar
- A16 [experience] covers: S3 · n/a beyond A14 — the skipped-rung note in M6 has the same receiver and the same hardship, and its own line would restate A14 with one word changed

## PLAN
contract: `fold(root, lens, match, reject=False, bind=None)`. One matcher, one write. `reject` swaps the word `folded` for `rejected` in the retagged head and nothing else. `bind` prepends `- <sentence> (from: /specs/<lens>.md#<ID>[, #<ID>…])` under `## Decisions that bind`, creating the section when absent and dropping the scaffold line when it is the section's only content; `_placeholder_only` then stops filtering it, so `bind_sections` and `brief` need no change at all. `milestone_done` gains one rung after the goal-gate: it reads `generated.at` off the closing milestone, lists open deltas whose `valid_from` is not None and not earlier than that date, and refuses naming each. No new verb — two flags in the `fold` parser, one rung in an existing function.
strategy: checks red first; the `bind` write reuses the existing section machinery rather than adding a FORMAT grammar (a `(from: …)` tail mirrors the `(evidence: …)` tail the delta line already carries, so nothing new is declared). Then the four engine twins, the three skill trees if any prose guard fires, the `engine_pin` re-aim, and the full suite BEFORE the receipt (M32 — this task edits a verb two other suites grep the source of).

## EDGES
- E1 a `--bind` whose match retags three deltas writes ONE decision citing three ids
- E2 a spec whose `## Decisions that bind` already holds a real decision gains the new one above it and keeps the old one byte-identical
- E3 a delta filed on the very day the milestone was created is INSIDE the window and blocks the close
- E4 a milestone carrying no readable creation date closes, and its note says the drain rung did not run
- E5 `fold --reject` whose match hits nothing refuses R:NOMATCH exactly as a bare fold does

## CHECKS
- test_reject_is_the_first_verb_for_rejected · covers: M1, A4, E5 · a rejected delta reads `rejected` with its interval closed, a fold and a reject given one match retag the same lines, and a match hitting nothing refuses R:NOMATCH
- test_bind_writes_a_decision · covers: M2, A5, A7, A10, E1 · the sentence lands under `## Decisions that bind` citing every id the same call retagged, the section is created when absent, and the retag and the decision arrive in one write
- test_bind_drops_the_scaffold_and_keeps_real_decisions · covers: M2, R:BINDLOSS, A11, E2 · the scaffold line goes when it is the only content, an existing real decision survives byte-identical, and the new decision is prepended above it
- test_reject_and_bind_together_refuse · covers: M3, R:REJECTBINDS · the two flags in one call refuse, and no byte of the spec moves
- test_bound_decision_reaches_the_brief · covers: M2, A1 · once a decision is bound, `brief` stops reporting that spec as unauthored
- test_close_refuses_undrained_lessons · covers: M4, A2, A14 · a milestone with an open delta filed inside its window refuses `R:UNDRAINED`, naming the delta address and the flags that resolve it
- test_close_never_blocks_on_the_backlog · covers: M5, R:BACKLOGBLOCK, A8, A13 · a delta filed before the milestone existed, and an undated legacy delta, neither blocks the close
- test_same_day_delta_is_inside_the_window · covers: A6, E3 · a delta filed on the milestone's creation date blocks the close
- test_unreadable_anchor_skips_and_says_so · covers: M6, R:SILENTSKIP, A9, E4 · a milestone with no readable creation date closes and its note names the rung that did not run
- test_the_rung_runs_after_the_goal_gate · covers: M7, A12 · a milestone with both an unchecked box and an undrained lesson reports the unmet goal, not the drain
- test_anchor_is_the_creation_date · covers: A3 · the window anchor equals `generated.at` on a milestone carrying later freeze and gate stamps
- test_the_drain_adds_no_verb · covers: R:NEWVERB, A15 · the CLI verb set is unchanged and both flags take the same substring `fold` already takes
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/deltas-drain-at-close.d/runs/1.md · kind: test-ids · 12/12 reported · exit 0 · 2026-09-08
gate: PASS · authority plan · by plan:loop-that-drains · receipt /tasks/deltas-drain-at-close.d/runs/1.md · 2026-09-08

## LESSONS
- pending
- none filed — no lesson cites /tasks/deltas-drain-at-close.md (add learn <lens> "<lesson>" --evidence /tasks/deltas-drain-at-close.md)
