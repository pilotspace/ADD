---
type: Task
title: the beat guides select a lens by fit, not the spawn
status: done
depth: standard
milestone: personas-load-by-fit
scope:
  - add-method/skill/add/phases/direction.md
  - add-method/skill/add/phases/build.md
  - add-method/skill/add/phases/verify.md
  - add-method/skill/add/SKILL.md
  - add-method/skill/add/streams.md
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill/test_persona_load_by_fit.py
  - add-method/tests/skill/test_surface.py
gives:
  - S1 the lens-selection instruction each beat guide gives an agent working the beat SEQUENTIALLY — which roster it reads, on which two keys, in which tier order, and the verb that records the pick
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:personas-load-by-fit", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:8b9bd8c52371b6c0", binding: "sha256:f8a8085abd2c4018" }
  - { by: "plan:personas-load-by-fit", at: 2026-09-10, act: refreeze, authority: plan, direction: "sha256:8b9bd8c52371b6c0", binding: "sha256:f8a8085abd2c4018" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:3894727de31af559" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-loads-on-every-path.d/runs/1.md }
  - { by: "plan:personas-load-by-fit", at: 2026-09-10, act: gate, authority: process, outcome: PASS, receipt: /tasks/persona-loads-on-every-path.d/runs/1.md, brief: "sha256:fac1311145013fcd" }
advised_by: method-steward
---
## CARD
goal: an agent working direction, build or verify reads the same lens selector a spawned subagent gets, so the persona is a function of fit and not of whether the human spawned an agent
why: <why this task exists — optional>
beat: done · next: add status

## RULES
<must>
- M1 each of `phases/direction.md`, `phases/build.md` and `phases/verify.md` instructs the agent to select a lens BEFORE the beat's work and to record it with `add advise`
- M2 the selector the three guides state is the SAME one `agents/add-worker.md` §2 already gives a spawned agent: the project roster first on `flow:` + `task-kinds:`, the teacher index second, proceed if neither fits
- M3 the four copies of that selector are ENUMERATED by a check, so a fifth surface cannot state a different rule and no copy can drift alone
- M4 `SKILL.md` no longer calls the LOAD opt-in — what is optional is the ROSTER, and a bundle with no personas still behaves exactly as before
- M5 every budget holds at its pinned ceiling; the added lines are funded by compression, never by a re-pin
</must>
<reject>
- R:DRIFTCOPY a guide states a selector on different keys or a different tier order from the one `add-worker.md` §2 gives -> "DRIFTCOPY"
- R:PINBUMP a budget literal in `tests/skill/skill_budget.py` is raised to make the addition fit -> "PINBUMP"
- R:MANDATORYROSTER a guide reads as though a bundle must carry personas, so a roster-less bundle is told it is missing something -> "MANDATORYROSTER"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who selects when the beat is worked sequentially; taking "the same agent that works the beat — there is no one else on this path, which is the whole defect" -> the instruction is written for a delegate that never arrives and the sequential path stays unlensed
- A2 [which] covers: S1 · the request does not say which guides; taking "the three EXECUTION beats — direction, build, verify. `explore.md` is a fourth beat guide and is deliberately out: an explore node's deliverable is cited findings, and its lens question is the advisor's, already covered by `intake.md`" · probe: the selector text appears in exactly the three named guides and not in `explore.md` -> a fourth guide gains an instruction nobody asked for and the surface budget pays for it
- A3 [when] covers: S1 · the request does not say when in the beat the load happens; taking "BEFORE the beat's work, matching `add-worker.md` §2's own words — a lens adopted after the drafting is a review, not a lens" -> the guide reads as a post-hoc record and the persona stops changing the work
- A4 [absent] covers: S1 · the request does not say what a bundle with NO fitting persona does; taking "proceed unchanged — the roster is optional and the load is by fit, so `seed.md` stays opt-in and a roster-less bundle behaves exactly as before (R:MANDATORYROSTER)" · probe: the three guides each name the no-fit exit -> a roster-less bundle is told at every beat that it is missing something it was never required to have
- A5 [order] covers: S1 · the request does not say which roster wins when both match; taking "project roster before teacher index, the order `add-worker.md` §2 and `add-advisor.md` §2 both already state — a project persona was authored for THIS bundle and a teacher entry never was" -> two agents pick different lenses for the same node and the record stops meaning anything
- A6 [experience] covers: S1 · the request does not say how long the instruction may be; taking "two lines per guide, appended to a paragraph that already exists so no blank line is spent — six lines total, funded by six compressed elsewhere" · probe: the measured surface total after the change is at or under what it was before -> the instruction is written at the length it deserves and the budget it shares with twenty other files pays for it
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: two lines appended to an existing paragraph in each of the three beat guides — the roster, the two keys, the tier order, the no-fit exit, and `add advise`. `SKILL.md`'s persona sentence is reworded so `opt-in` describes the ROSTER, not the load. The four copies are pinned to agree by a new `tests/skill/test_persona_load_by_fit.py`.
strategy: write the check first against the unedited guides (three misses), then edit the guides, then fund the six lines by compressing `streams.md` — the fattest file on the surface at 189 lines — and mirror all three git-tracked skill trees.

## EDGES
- E1 <a boundary or failure case a check must cover — optional>

## CHECKS
- test_every_execution_beat_guide_selects_a_lens · covers: M1, A1, A3 · each of the three guides names the roster, `add advise`, and puts the load before the beat's work
- test_the_four_copies_state_one_selector · covers: M2, M3, R:DRIFTCOPY, A5 · the three guides and `add-worker.md` §2 are enumerated and agree on both keys and the tier order
- test_the_roster_is_optional_and_the_load_is_not · covers: M4, A4, R:MANDATORYROSTER · SKILL.md stops calling the load opt-in, and every guide still names the no-fit exit
- test_only_the_execution_beats_gained_it · covers: A2 · `explore.md` is untouched, so the instruction landed where it was aimed
- test_the_addition_was_funded · covers: M5, A6, R:PINBUMP · the surface total did not rise and no budget literal moved
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/persona-loads-on-every-path.d/runs/1.md · kind: test-ids · 251/251 reported · exit 0 · 2026-09-10
gate: PASS · authority process · by plan:personas-load-by-fit · receipt /tasks/persona-loads-on-every-path.d/runs/1.md · 2026-09-10

## LESSONS
- [system · S13 · folded] `opt-in` described two different things and only one of them was true: the ROSTER is optional (a bundle may have none), the LOAD is not (if a persona fits, it loads). One word covering a subject and its object is how a capability turns itself off. (evidence: /tasks/persona-loads-on-every-path.md)
