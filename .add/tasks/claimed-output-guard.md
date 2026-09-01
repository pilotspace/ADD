---
type: Task
title: A skill claim about what the engine prints is bound to the engine printing it
status: direction
depth: standard
sensitivity: architecture
milestone: affordance-truth
scope:
  - .claude/skills/add
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - add-method/tests/skill
  - add-method/tooling
gives:
  - S1 the registry binding each skill-tree claim about engine OUTPUT to the command that must emit it and the bundle state that makes it observable
  - S2 the guard in `add-method/tests/skill/` that drives every registered claim against a real bundle
  - S3 `loop.md`'s Gather step, with its two false claims repaired in all three skill trees
  - S4 the failure message an unbacked claim produces
generated: { by: add/3.2.0, at: 2026-08-17 }
verified:
  - { by: "Tin Dang", at: 2026-08-17, act: freeze, authority: human, direction: "sha256:44a8759bd6f4ceca" }
---
## CARD
goal: Bind every skill-tree sentence that says the engine PRINTS something to a driven command that proves it prints it, and repair the two `loop.md` claims that do not.
why: `promised-capability-guard` closed this class for the READMEs and its own `why:` named the gap it
  left — those guards "check nouns the engine EXPOSES ... and never capabilities the prose PROMISES".
  `loop.md` is where that gap bit: `:41` says "`add status` shows `goal not met (m/n exit criteria)`. That
  is the cue" and `:46` sends the reader to "the plan-vs-state line in `add status`". Neither exists.
  The first string lives only at `add.py:1424`, inside `milestone_done()`'s REFUSAL — so an existence
  anchor of the kind the README guard uses would resolve it and pass. The second has no implementation at
  all. Both sit in the loop's Gather step and the first is named as THE cue that starts the loop, so an
  agent following the skill waits for a signal the engine never sends. A claim about output cannot be
  checked by finding a string in a source file; it has to be checked by running the command.
beat: direction · next: add freeze claimed-output-guard

## RULES
<must>
- M1 Every skill-tree sentence claiming a command SHOWS, PRINTS or DISPLAYS something is registered, and every registered claim is proven by DRIVING that command against a bundle put into the state the claim describes. Existence of the string in `add.py` proves nothing and satisfies nothing.
- M2 An unregistered claim fails the guard BY NAME — quoting the sentence and naming its file and line — so a new claim cannot join the skill tree silently. This is `promised-capability-guard`'s M3 applied to a different corpus, deliberately the same shape.
- M3 The two false `loop.md` claims are repaired in ALL THREE live skill trees — `.claude/skills/add/`, `add-method/skill/add/`, `add-method/src/add_method/_bundled/skill/add/`. A two-tree repair ships a mirror gap that fails at publish.
- M4 The default repair is REWORD-to-truth: the skill is corrected to what the engine does today. Building the missing `status` surface is a real option and a real improvement, and it is a SEPARATE task — this one must not grow an engine feature under a guard's cover.
- M5 A claim whose bundle state cannot be constructed is reported as UNPROVABLE by name, never silently skipped and never counted as passing. A guard that quietly drops the claims it finds hard is the ritual this task exists to prevent.
- M6 The Gather step still works after the repair: the loop's entry cue names something an agent can actually observe, so correcting the claim does not leave the step with no trigger at all.
</must>
<reject>
- R:GREP_ANCHOR Satisfying a claim by finding its string anywhere in `add.py` or in the skill tree. `goal not met (m/n exit criteria)` IS in `add.py` — at `:1424`, in a different verb — which is exactly how this claim survived. The anchor is captured stdout from a driven command. -> "GREP_ANCHOR"
- R:SELF_PROVING Satisfying a claim by the sentence's own words appearing elsewhere in the corpus — `promised-capability-guard`'s R:LOOSE, restated for this corpus because the same shortcut is available here. -> "SELF_PROVING"
- R:CULL Reaching green by deleting a sentence whose claim the engine actually keeps. A true statement about engine output belongs in the skill. -> "CULL"
- R:FEATURE_CREEP Adding the missing `status` lines inside this task to make a false claim true. That inverts the fix, and it means the guard ships having never once refused anything. -> "FEATURE_CREEP"
- R:TWO_TREE Repairing fewer than all three live skill trees, or registering claims from one tree only. -> "TWO_TREE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3, S4 · the request does not say WHO adds a claim later; taking anyone editing the skill tree, with no reviewer assumed — which is why M2's failure must quote the sentence rather than merely fail -> if wrong the guard protects only today's sentences and the next skill edit reopens the hole · probe: a newly added unregistered claim fails by its own text
- A2 [which] covers: S1, S2 · the request does not say WHICH sentences count as output claims; taking sentences naming a command AND a thing it shows/prints/displays/reports, not sentences describing what a verb DOES or what the method means -> if wrong the registry either misses a claim phrased unusually or demands stdout for a sentence explaining a concept · probe: the registry's own boundary is stated in the guard and a describing sentence is shown not to be demanded
- A3 [which] covers: S3, S4 · the request does not say WHICH files in the skill tree are in; taking every `.md` under each skill root, since `loop.md` is where the misses were found but nothing makes it special -> if wrong a false claim in `gate.md` or `intake.md` survives the guard built to catch its twin, and the message never ranges over it · probe: the guard enumerates every skill file, not a named list
- A4 [when] covers: S1, S2 · the request does not say WHEN the claim must hold; taking every test run against the working tree, so a `status` change that drops a line breaks the skill's checks in the same commit -> if wrong the skill and the engine diverge exactly as they did here, and a reader finds it instead · probe: removing a claimed line from the engine turns the guard red
- A5 [when] covers: S3, S4 · the request does not say WHEN a repaired sentence is verified — at repair time or continuously; taking continuously, via the same registry, so a repair is not a one-off edit -> if wrong the two sentences are corrected today and rot again with no guard on them · probe: the repaired sentences are themselves registry entries
- A6 [absent] covers: S1, S2 · the request does not say what to do with a claim that is TRUE but whose bundle state is expensive or impossible to construct; taking M5's UNPROVABLE report — named, counted, and visible — rather than a skip or a pass -> if wrong the guard's green means "the easy ones passed" while reading as "the skill is honest" · probe: the guard's output states how many claims were proven and how many were unprovable
- A7 [absent] covers: S3, S4 · the request does not say what an ABSENT registry entry means versus a registered claim whose command fails, nor what to do with a sentence that has no truthful replacement; taking the two failures as DISTINCT with distinct messages, and an unreplaceable sentence as a deletion that must state what was lost -> if wrong one message covers two causes and the reader guesses which · probe: the two failures read differently
- A8 [order] covers: S1, S2, S4 · the request does not say whether repair precedes the guard or follows it; taking guard-first-red, then repair, so the guard is proven to REFUSE the two known-false claims before anything is corrected -> if wrong the guard ships green having never refused anything, which is indistinguishable from a guard that cannot refuse · probe: the guard is red on the unrepaired tree, naming both sentences
- A9 [order] covers: S3 · the request does not say which of the three skill trees is the source of truth; taking `add-method/skill/add/` as source and the other two as mirrors, matching how the engine twins are handled -> if wrong an edit lands in a mirror and is overwritten by the next sync · probe: the repair is authored in the source tree and mirrored
- A10 [experience] covers: S2, S4 · the request does not say who the failure is FOR; taking whoever edits the skill months from now with no knowledge of this task, so the message must quote the sentence, give its file and line, name the two ways to satisfy it (register a driven proof, or reword to what the engine does) and say that rewording is the intended outcome rather than a workaround -> if wrong the next author reads it as an obstacle and registers a vague anchor, which is worse than no guard because it now reads as verified · probe: the failure message names both remedies
- A11 [experience] covers: S1, S3 · the request does not say who reads the repaired `loop.md`; taking the agent entering the loop's Gather step cold as the reader, since that is the sentence's job -> if wrong the sentence becomes literally true and operationally useless, and the step loses its trigger · probe: the repaired sentence names an observable an agent can obtain in one command
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: A registry, keyed per skill file, binding each output claim to (command, bundle state,
  expected observable). The guard builds each state in a scratch bundle, runs the command, captures
  stdout, and asserts the observable appears — never reading `add.py`. Claims with no constructible
  state are reported UNPROVABLE by name and counted in the guard's own summary line. An unregistered
  claim fails quoting its sentence, file and line, naming both remedies. `loop.md:41` and `:46` are
  reworded to what `status` actually emits, in the source skill tree and mirrored to the other two.
scope: .claude/skills/add · add-method/skill/add · add-method/src/add_method/_bundled/skill/add ·
  add-method/tests/skill · add-method/tooling
strategy (preferred): build the registry and the driver with the two false claims registered and
  UNREPAIRED, so the first run is red naming both — the evidence that the guard can refuse. Then sweep
  the remaining skill files into the registry. Then reword the two sentences in the source tree and
  mirror. The guard's ability to refuse is proven before anything is corrected, never after.
regression floor: both test roots green — `add-method/tests/` and `add-method/tooling/`.

## EDGES
- E1 `goal not met (m/n exit criteria)` IS present in `add.py` — at `:1424`, inside `milestone_done()`. A source-grep anchor resolves it and passes. This is the exact case that must be red.
- E2 A claim naming a command that takes a flag whose output differs by mode — `add status` versus `--all` versus `--check`. Observed: on this bundle all three printed the same lines and exited 0, so a guard that drives only the bare form may prove or disprove the wrong thing.
- E3 A claim whose state needs a milestone with every task done and an exit box unchecked — constructible, but only by driving a full task through freeze, run and gate in a fixture. Cost lands here, and E3 is the reason M5 exists.
- E4 A sentence that names a command inside a parenthetical while making a different point, e.g. "(`add milestone-done` is wired — it refuses to close while a goal box is unchecked)". That IS an output claim and is true; it must be registered, not filtered out as prose.
- E5 The three skill trees may already have drifted from one another on some other sentence. The guard reads every tree, so a pre-existing mirror gap surfaces here as an unrelated red — real, and it must be reported rather than normalised away.

## CHECKS
- test_registry_covers_every_output_claim · covers: M1, M2, A3 · every sentence in every skill file matching the claim shape has a registry entry; an unregistered one fails quoting its text, file and line
- test_each_claim_is_proven_by_driven_stdout · covers: M1, R:GREP_ANCHOR · each entry is proven from captured stdout of a real command against a real bundle; the guard never reads `add.py`
- test_source_presence_alone_does_not_satisfy_a_claim · covers: R:GREP_ANCHOR, E1 · the `goal not met` claim is red while the string exists at `add.py:1424` — the anchor that would have passed is shown to fail
- test_claim_not_satisfied_by_its_own_words_elsewhere · covers: R:SELF_PROVING · a claim whose text appears in another skill file is still unproven
- test_unprovable_claims_are_named_and_counted · covers: M5, A6 · the summary states proven and unprovable counts; an unconstructible state is named, never skipped
- test_unregistered_and_failing_read_differently · covers: A7 · the two failure causes produce distinct messages
- test_failure_message_names_both_remedies · covers: A10 · register a driven proof, or reword to what the engine does, with rewording named as intended
- test_guard_is_red_on_the_unrepaired_tree · covers: A8, M2 · driven against the tree as it stands today, the guard names both `loop.md` sentences
- test_loop_claims_are_repaired_in_all_three_trees · covers: M3, R:TWO_TREE · neither false sentence survives in any live skill tree
- test_repaired_sentences_are_registered · covers: A5, M6 · the replacements are themselves entries, and each names an observable obtainable in one command
- test_repaired_gather_step_still_has_a_trigger · covers: M6, A11 · the Gather step's entry cue names something an agent can actually observe
- test_no_engine_output_was_added · covers: M4, R:FEATURE_CREEP · `add.py` is untouched by this task; the engine emits exactly what it emitted before
- test_no_true_claim_was_deleted · covers: R:CULL · the skill's claim count and the surviving sentences are what the contract says
- test_status_flag_modes_are_driven_as_registered · covers: E2 · a claim naming a flagged form is proven against that form, not against the bare command
- test_parenthetical_claims_are_registered · covers: E4 · the `milestone-done` parenthetical resolves as an entry rather than being filtered as prose
- test_skill_tree_mirror_parity · covers: E5, R:TWO_TREE · the three trees are identical, and a pre-existing gap is reported rather than normalised
red-first: every check MUST fail first. The guard is authored and run RED against the unrepaired tree before any sentence is corrected — a guard that has never refused is not evidence.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
