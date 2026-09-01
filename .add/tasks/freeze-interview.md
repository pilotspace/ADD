---
type: Task
title: The ONE approval asks its questions out loud
status: build
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/tests/engine
  - .claude/skills/add
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
gives:
  - S1 the `interview` verb — compiles the node's open decisions into numbered questions
  - S2 the `interview` verb under `--answer` — records an answered interview as a stamp
  - S3 the `freeze` verb at a human floor — refuses an uninterviewed node (R:UNINTERVIEWED)
  - S4 the skill's direction beat — the prose that drives the interview before the stamp
generated: { by: add/3.2.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:6a8d4230fc9e4e79" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:2f5727fcff92fce4" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:2f5727fcff92fce4" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/freeze-interview.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-01, act: refreeze, authority: human, direction: "sha256:61e2a81eb66a8bfd" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:069293bef06c9602" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/freeze-interview.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-01, act: gate, authority: plan, outcome: PASS, receipt: /tasks/freeze-interview.d/runs/2.md, brief: "sha256:069293bef06c9602" }
  - { by: loop, at: 2026-09-01, act: reopen, to: build, reason: "interview_gap returns on the FIRST digest-matching stamp, so a partial interview cannot be completed by a second pass" }
advised_by: method-steward
---
## CARD
goal: at a human floor, `freeze` refuses until every open decision in the node has been put to a human and answered.
why: `freeze` already refuses an incomplete contract eight ways — placeholders, an unauthored `gives:`, collapsed surfaces, unswept (dim, surface) pairs, an unbudgeted explore. Every one of those checks the DOCUMENT. None checks the CONVERSATION. `## ASSUMPTIONS` is by construction a list of silences the AI filled in on the human's behalf, each carrying a reading and a cost-if-wrong, and the ONE approval ADD asks for is a single stamp that says nothing about whether the human ever saw one of them. The sweep made the AI WRITE DOWN what it decided; this makes it ASK.
beat: done · next: add status

## RULES
<must>
- M1 `interview <slug>` compiles one numbered question per non-`n/a` ASSUMPTIONS line and per Reject, each carrying the reading taken and the cost if wrong, and prints them without recording anything.
- M2 `interview <slug> --answer <id>=<verdict>` records answers; the accepted verdicts are `confirm`, `correct` and `defer`, and an unknown verdict is refused by name.
- M3 A completed interview appends ONE `act: interview` stamp carrying a digest of exactly what was interviewed, and writes the questions and answers to a `.d/interviews/<n>.md` sidecar the stamp references.
- M4 `freeze` refuses when the computed floor is `human` and no interview stamp matches the node's current interview digest -> "R:UNINTERVIEWED", naming the unanswered ids.
- M5 The refusal keys on `authority_for`, never on the `--authority` argument, so passing `--authority process` cannot switch the interview off.
- M6 An interview is incomplete while any item is unanswered or answered `correct`; `freeze` names those ids and refuses. `correct` is cleared by editing the item, which moves the digest and requires a fresh interview.
- M7 An interview whose digest no longer matches the node is stale and does not satisfy M4 — editing an assumption after the interview re-opens it.
- M8 A node whose compiled question set is EMPTY needs no interview and freezes as before.
- M9 The interview refusal runs LAST in freeze's ladder, after every existing refusal — you cannot interview a node still carrying placeholders or unswept pairs.
- M10 The skill's direction beat instructs the agent to drive the interview as a real question to the human before the stamp, in all three live skill trees.
</must>
<reject>
- R:UNINTERVIEWED a human-floor freeze must never record approval for a decision no human was shown -> "R:UNINTERVIEWED"
- R:SELFANSWER the agent must never record an answer it was not given by a human -> "R:SELFANSWER"
- R:RENUMBER no existing body section is renumbered or removed; the engine keys sections by name and number -> "R:RENUMBER"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S2 · the request does not say who may record an answer; taking the `--by` name recorded verbatim, exactly as `freeze --by` already works — the engine is a notary and cannot verify a human typed it -> if wrong an agent self-answers and the guard becomes theatre · probe: the sidecar and the stamp both carry the `--by` value, and R:SELFANSWER is prose in the skill, not an engine claim.
- A2 [which] covers: S1 · the request does not say which items are open decisions; taking non-`n/a` ASSUMPTIONS lines plus Rejects — an `n/a` retirement is self-justifying and a Must came FROM the human -> if wrong the interview either asks noise or misses a real decision · probe: a node with three `n/a` lines and two Rejects compiles exactly (non-n/a count + 2) questions.
- A3 [when] covers: S3 · the request does not say when an interview goes stale; taking any change to the interviewed text, by digest, the same shape `direction:` and `brief:` already use -> if wrong a stale interview approves text nobody read · probe: editing one assumption after an interview makes `freeze` refuse again.
- A4 [absent] covers: S1, S3 · the request does not say what an EMPTY question set means; taking nothing-to-ask as nothing-to-refuse (M8) -> if wrong every `quick` node at a security floor, which is sweep-exempt, becomes unfreezable · probe: a quick node with no ASSUMPTIONS and no Rejects freezes at a human floor with no interview.
- A5 [order] covers: S3 · the request does not say where in freeze's ladder this sits; taking LAST (M9) -> if wrong the human is interviewed about assumptions that are still template text · probe: a node with placeholders hears the placeholder refusal, not R:UNINTERVIEWED.
- A6 [experience] covers: S1, S4 · the request does not say what form the questions take; taking one screen per item with the reading and the cost stated in the author's own words, since the reader is a human being asked to accept a risk and a bare id tells them nothing -> if wrong the human clicks through and the ceremony buys nothing · probe: each compiled question prints the reading and the cost-if-wrong, not just the id.
- A7 [who] covers: S1, S3, S4 · n/a · compiling questions and refusing a freeze read no identity; the actor appears only at S2, which A1 covers.
- A8 [which] covers: S2, S3 · n/a · S2 records what S1 compiled and S3 reads the resulting stamp; neither selects a different item set.
- A9 [when] covers: S1, S2, S4 · n/a · compiling and recording are point-in-time; the only temporal boundary is staleness, which A3 covers for S3.
- A10 [absent] covers: S2 · the request does not say what an answer for an id that does not exist means; taking a refusal naming the valid ids -> if wrong a typo records an answer against nothing and the item stays silently unanswered · probe: `--answer A99=confirm` on a five-item interview refuses and lists the five.
- A11 [order] covers: S1, S2, S4 · n/a · questions carry their author-assigned ids, so presentation order changes nothing that is recorded.
- A12 [experience] covers: S2, S3 · the request does not say who reads the refusals; taking an agent mid-loop that will act on `next:` without a human, so R:UNINTERVIEWED names the interview verb and lists the unanswered ids -> if wrong the agent retries the freeze or routes around it · probe: the refusal carries a runnable `next:` and the ids.
- A13 [which] covers: S4 · the request does not say which skill trees; taking all three live trees, since a two-tree edit has shipped a mirror gap in this repo before -> if wrong one installed agent never learns to interview · probe: a check asserts the instruction in all three trees.
- A14 [absent] covers: S4 · n/a · the skill prose is either present or the check fails; there is no missing-value reading to take.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `interview(root, cid, answers=None, by=None)` — with no answers it compiles and returns the question list; with answers it validates ids and verdicts, writes `.d/interviews/<n>.md`, and appends `{ act: interview, by, interview: "sha256:…", receipt: /…/interviews/<n>.md }`. `interview_digest(node)` hashes exactly the interviewed text (non-`n/a` ASSUMPTIONS lines + the reject block). `freeze` gains one final refusal reading `authority_for` and that digest. `cli.py` gains the verb with repeatable `--answer <id>=<verdict>` and `--by`. The skill's direction beat gains the instruction to ask the human for real.
scope: add-method/tooling/add.py, add-method/tooling/cli.py, add-method/tests/engine, and the three skill trees

## EDGES
- E1 `--authority process` passed explicitly on a `security` node — M5 means the interview is still required.
- E2 a node interviewed, then a Must edited (not an assumption, not a reject) — the interview still binds; Musts came from the human.
- E3 a node interviewed, then one assumption reworded — the digest moves and freeze refuses again (M7).
- E4 a refreeze on an unchanged node — the existing interview stamp still satisfies M4; no re-interview for an unrelated CHECKS edit.
- E5 every item answered `defer` — a legitimate complete interview; deferring IS an answer.
- E6 an item answered `correct` and never edited — incomplete, refused by name (M6).
- E7 a `quick` node at a security floor with no ASSUMPTIONS section — M8, freezes with no interview.
- E8 two interviews recorded, the first stale — freeze reads the one matching the current digest, not the latest.

## CHECKS
- test_interview_compiles_one_question_per_open_decision · covers: M1, A2 · non-n/a assumptions plus rejects, nothing else.
- test_interview_prints_the_reading_and_the_cost · covers: M1, A6 · each question carries the taken reading and the cost-if-wrong.
- test_bare_interview_records_nothing · covers: M1 · no stamp, no sidecar, when called without answers.
- test_interview_records_a_stamp_and_a_sidecar · covers: M3 · one `act: interview` stamp referencing `.d/interviews/1.md`.
- test_interview_refuses_an_unknown_verdict · covers: M2 · `--answer A1=maybe` refuses and names confirm/correct/defer.
- test_interview_refuses_an_unknown_id · covers: A10 · `--answer A99=confirm` refuses and lists the real ids.
- test_freeze_refuses_an_uninterviewed_human_floor_node · covers: M4, R:UNINTERVIEWED · the headline refusal, naming unanswered ids.
- test_freeze_refusal_keys_on_the_computed_floor · covers: M5, E1 · `--authority process` on a security node still refuses.
- test_freeze_accepts_a_completed_interview · covers: M4 · every item confirmed, freeze stamps.
- test_all_deferred_is_a_complete_interview · covers: E5 · deferring is answering.
- test_a_corrected_item_leaves_the_interview_incomplete · covers: M6, E6 · freeze names the corrected id.
- test_editing_an_assumption_makes_the_interview_stale · covers: M7, E3, A3 · the digest moves, freeze refuses.
- test_editing_a_must_does_not_stale_the_interview · covers: E2 · the Musts came from the human.
- test_a_refreeze_needs_no_second_interview · covers: E4 · an unchanged node refreezes.
- test_freeze_reads_the_matching_interview_not_the_latest · covers: E8 · a stale later stamp does not satisfy a moved digest.
- test_an_empty_question_set_needs_no_interview · covers: M8, A4, E7 · a quick sweep-exempt node still freezes.
- test_interview_runs_last_in_the_ladder · covers: M9, A5 · a node with placeholders hears the placeholder refusal.
- test_a_process_floor_node_is_never_interviewed · covers: M4 · no human in the room, no interview.
- test_the_refusal_names_a_next_verb_and_the_ids · covers: A12 · a runnable `next:` and the unanswered ids.
- test_the_interview_instruction_is_in_all_three_skill_trees · covers: M10, A13 · one assertion per tree, named per tree.
- test_no_body_section_was_renumbered · covers: R:RENUMBER · the section census is unchanged.
- test_selfanswer_is_carried_by_prose_not_by_an_engine_claim · covers: R:SELFANSWER, A1 · the discipline is shipped prose, on one line, in every tree.
- test_the_by_name_is_recorded_verbatim · covers: A1 · the notary records the name it is given and judges nothing.
- test_a_partial_interview_is_completed_by_a_second_pass · covers: M6 · answers accumulate across passes over the same text.
- test_a_later_correct_overrides_an_earlier_confirm · covers: M6 · folding is in order, and later wins.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- Eight refusals checked the document and none checked the conversation; when a gate exists to protect a human decision, check that the decision was PUT to them -> add learn add
