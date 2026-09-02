---
type: Task
title: The persona contract the skill documents is the contract the roster selects on
status: done
depth: quick
milestone: live-persona-tier
scope:
  - add-method/skill/add
  - add-method/tests/skill
gives:
  - S1 the persona frontmatter contract as documented in `personas.md` and the persona-author references
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:b5577b87fe6edeb1" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:bee43dac8bc86778" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-contract-truth.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-01, act: refreeze, authority: human, direction: "sha256:dcb9bbc077c33155" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:55054946e1a2bb67" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-contract-truth.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-01, act: gate, authority: process, outcome: PASS, receipt: /tasks/persona-contract-truth.d/runs/2.md, brief: "sha256:55054946e1a2bb67" }
---
## CARD
goal: The skill documents the frontmatter keys the roster actually selects on, and every teacher archetype the seed guide names resolves to a real file under a guard that would have caught it.
why: `personas.md:30-31` tells an author that `flow:` and `not-when:` are "recommended, hand-authored, and read by nothing". `flow:` is in fact the PRIMARY selector in both roster agents (add-worker.md:37-39, add-advisor.md:36), and `task-kinds:` — never mentioned in `personas.md` at all — is the second. `add new Persona` scaffolds seven keys, not one. So an author who follows the file that owns the schema leaves `task-kinds:` at its placeholder believing nothing reads it, the selector then fails to match, and the persona silently never loads: no refusal, no warning, just a generic agent. That is the guard-class hole this project has already been burned by twice — a capability the prose promises with no noun to check it. Compounding it, `seed.md:26` names three teacher archetypes to distil from — `backend-systems` · `security-reviewer` · `frontend-ux` — and all three resolve to ZERO files; the real slugs are `engineering/engineering-backend-architect`, `security/security-architect`, `design/design-ux-architect`, which `streams.md:99-101` names correctly and which `tests/skill/test_streams.py:159` already guards. The guard exists and scans the wrong file: its regex requires the `personas-teacher/` prefix, so seed.md's bare backticked slugs are invisible to it, and seed.md's own test asserts only that the literal string "personas-teacher" appears somewhere.
beat: done · next: add status

## RULES
<must>
- M1 `personas.md` states the full scaffolded key set and marks `flow:` and `task-kinds:` as the keys the roster's selector reads, citing the roster.
- M2 No shipped skill file describes a key the roster selects on as unread.
- M3 Every teacher archetype named anywhere in the skill tree resolves to a real corpus file.
- M4 The existing roster-resolution guard is extended to scan the seed guide, not only the streams roster, and matches a bare slug as well as a prefixed path.
</must>
<reject>
- R:PHANTOMLENS a shipped file must never name a teacher archetype that resolves to nothing -> "R:PHANTOMLENS"
- R:UNREADKEY the schema owner must never describe a routing key as unread while a shipped selector reads it -> "R:UNREADKEY"
</reject>

## ASSUMPTIONS
- A1 [which] covers: S1 · the request does not say which keys are contractual; taking the seven `add new Persona` actually scaffolds, read from the scaffold writer rather than from prose -> if wrong the document and the scaffold drift again · probe: the documented set is enumerated from the scaffold source.
- A2 [absent] covers: S1 · the request does not say what an ABSENT routing key means; taking "routes nothing, and that is a finding" rather than a silent generic — which is the sibling task's engine work, referenced here, not duplicated -> if wrong the two tasks disagree about the same key · probe: this task changes prose and a guard only, never the selector.
- A3 [experience] covers: S1 · the request does not say what the author needs; taking a pointer to the roster file that reads the key, so the claim is verifiable by the reader rather than merely asserted -> if wrong the author trusts prose again · probe: the sentence cites the roster file by path.
- A4 [who] covers: S1 · n/a · a documented schema is read identically by every author.
- A5 [when] covers: S1 · n/a · documentation has no temporal boundary; nothing already authored is invalidated.
- A6 [order] covers: S1 · n/a · the key descriptions are independent of one another.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `personas.md`'s frontmatter paragraph is replaced with the real scaffolded key set, marking the two selector keys and citing the roster; `seed.md`'s three archetype names become their real division/slug paths; the streams resolution guard is generalised to scan every skill file and to match bare slugs.
scope: add-method/skill/add, add-method/tests/skill

## EDGES
- E1 `streams.md`'s roster, which already resolves — must keep passing the generalised guard.
- E2 a slug written bare in backticks rather than as a full path — the generalisation's whole point (M4).
- E3 a persona named in illustrative prose that is deliberately hypothetical — the guard must not demand a file for an example it is told is one.
- E4 the persona-author references, which restate parts of the contract — must not contradict the corrected `personas.md`.

## CHECKS
- test_personas_md_states_the_scaffolded_key_set · covers: M1, A1 · the documented set is enumerated from the scaffold source.
- test_no_skill_file_calls_a_selector_key_unread · covers: M2, R:UNREADKEY · the false clause is gone everywhere.
- test_every_named_archetype_resolves · covers: M3, R:PHANTOMLENS · enumerated across the whole skill tree.
- test_the_guard_scans_the_seed_guide · covers: M4, E2 · a bare backticked slug in seed.md is caught.
- test_the_streams_roster_still_resolves · covers: E1 · the incumbent case is unchanged.
- test_a_hypothetical_example_is_not_flagged · covers: E3 · the guard scopes to real references.
- test_the_persona_author_references_agree · covers: E4, A3 · no reference contradicts the corrected schema.
- test_this_task_changed_prose_and_a_guard_only · covers: A2 · the selector's closed vocabularies are untouched; an absent key is a finding, never a default.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
