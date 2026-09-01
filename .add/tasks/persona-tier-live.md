---
type: Task
title: A fresh bundle loads a persona, and a project with none reaches the corpus
status: direction
depth: standard
sensitivity: architecture
milestone: live-persona-tier
scope:
  - add-method/tooling/add.py
  - add-method/agents
  - add-method/tests
gives:
  - S1 the `init` persona seed — what a freshly created bundle carries in `.add/personas/`
  - S2 the roster's selection ladder — the tiers both agent files search before the generic fallback
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:2d8c673ac30b496a" }
  - { by: "Tin Dang", at: 2026-09-01, act: replan, authority: process, note: "A2 read the seed set as the three existing planner templates. Measured at build: their flow: values cover design, advisor and verify but NOT build, so M2 — every roster beat has a seeded match — is unsatisfiable with those three alone. Seeding a fourth, a flow: build working lens, distilled from the corpus the same way the planners were. The seal is untouched: M2 was always the binding rule and A2 was the reading of how to satisfy it." }
---
## CARD
goal: A freshly initialised bundle carries at least one selectable persona, and an agent whose `.add/personas/` yields no match routes through the generated index into the 232-lens teacher corpus before it falls back to a generic specialist.
why: "Personas carry the expertise; this agent carries the discipline" is the method's headline value claim, and it is false on every fresh install. `3.0 seeds no personas`, so `.add/personas/` is empty and the selector both agents run — `flow:` first, then `task-kinds:` — has nothing to search. The corpus cannot rescue it: measured 2026-09-01, ZERO of 232 teacher personas carry `flow:` and ZERO carry `task-kinds:`, and neither agent file names `.add/personas-teacher/` or `.add/personas-index/use-when.md` at all, though the installer lands both in every bundle. The three planner templates that DO carry both keys sit in `tooling/templates/personas/` and are seeded by nothing — `init` never touches that directory and `_vendor_tooling` copies only the engine files and the corpus — while `CHANGELOG.md:194` claims they are "seeded at init and migrate". So the steady state is the generic fallback, taken silently, on every project that is not this one. Nothing in the receipt records that it fired, which makes it the worst shape of failure for a trust-based method: the run looks identical to one where an expert was loaded. This repo is the proof — 109 closed nodes, a 232-lens corpus, and a roster of two hand-written personas that exists only because the maintainer wrote it.
beat: direction · next: add freeze persona-tier-live

## RULES
<must>
- M1 `init` seeds the planner personas into `.add/personas/` as real Persona nodes, carrying `flow:` and `task-kinds:` values inside their closed taxonomies.
- M2 A seeded persona satisfies the roster's selector: for each of the beats the roster names, at least one seeded persona matches on `flow:`.
- M3 Both agent files name a corpus tier: no `.add/personas/` match routes through `.add/personas-index/use-when.md` into `.add/personas-teacher/` before the generic fallback.
- M4 The generic fallback remains, and remains last — an unmatched task never hard-fails.
- M5 `init` never overwrites an existing persona file, matching the verb's standing never-overwrite contract.
</must>
<reject>
- R:DEADTIER a selection tier the agents are told to search must never be one no shipped file can satisfy -> "R:DEADTIER"
- R:SILENTGENERIC the roster must never reach the generic fallback while an unsearched tier holds a match -> "R:SILENTGENERIC"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say whose personas these are; taking them as the PROJECT's from the moment they land — seeded, then owned and editable by the project, never engine-managed files a refresh would overwrite -> if wrong an author's edits are clobbered by the next update · probe: a seeded persona edited by hand survives a re-init.
- A2 [which] covers: S1 · the request does not say WHICH personas to seed; taking the three planner templates that already exist and already carry both routing keys, because authoring new ones is a separate judgement the corpus should inform -> if wrong the seed is thin but correct rather than rich and wrong · probe: the seeded set is the existing templates, unmodified in substance.
- A3 [which] covers: S2 · the request does not say which corpus entries are eligible; taking every indexed entry — the generated index is exactly the routable set, 232 of 256, the remainder documented non-personas -> if wrong the fallback reaches a README or a playbook · probe: the tier routes through the index, never by globbing the corpus.
- A4 [when] covers: S2 · the request does not say when the corpus tier fires; taking after `.add/personas/` yields no match and before the generic, so a project's own lens always wins -> if wrong a vendored lens overrides the project's own · probe: a matching project persona is selected while the corpus holds a closer-sounding one.
- A5 [absent] covers: S1 · the request does not say what an EXISTING `.add/personas/` means; taking never-overwrite, matching `init`'s standing contract -> if wrong re-running init destroys authored work · probe: an existing file is left byte-identical.
- A6 [absent] covers: S2 · the request does not say what an absent corpus means; taking a soft skip to the generic — the corpus is an OPTIONAL installed tree and may legitimately be missing -> if wrong the roster hard-fails on a lean install · probe: an agent with no corpus on disk still selects and proceeds.
- A7 [order] covers: S2 · the request does not say what breaks a tie inside the corpus tier; taking the index's `use-when:` boundary, then the division, then first — a documented order beats an arbitrary one -> if wrong selection is unreproducible run to run · probe: the tie-break is stated in the agent file.
- A8 [experience] covers: S2 · the request does not say what the agent should report; taking an explicit named tier in its return — which persona, from which tier — because a silent generic fallback is the defect · probe: the agent's return names the tier it selected from.
- A9 [experience] covers: S1 · the request does not say what the initialising user should see; taking one line in `init`'s note naming what was seeded and that it is theirs to edit -> if wrong the seed is invisible and never edited · probe: `init`'s note names the seeded personas.
- A10 [who] covers: S2 · n/a · the selection ladder is the same for both roster agents and every caller.
- A11 [when] covers: S1 · n/a · seeding happens once, at creation, with no boundary of its own.
- A12 [order] covers: S1 · n/a · the seeded files are independent; no order applies.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `init` writes the planner persona templates into `.add/personas/` under its existing never-overwrite rule and names them in its note; both agent files gain a corpus tier between the project roster and the generic fallback, routed through the generated index, with a stated tie-break and a tier named in the return.
scope: add-method/tooling/add.py, add-method/agents, add-method/tests

## EDGES
- E1 a bundle whose `.add/personas/` already holds files — untouched (A5, M5).
- E2 a lean install with no `personas-teacher/` and no index on disk — soft skip to generic, no failure (A6).
- E3 a task whose `kind:` matches nothing in any tier — the generic fallback, reached and NAMED (M4, A8).
- E4 a seeded persona edited by the project, then `init` re-run — the edit survives (A1).
- E5 the four live engine twins — a seeded-file change re-aims `ENGINE_MD5` and must land in every tracked twin.

## CHECKS
- test_init_seeds_selectable_personas · covers: M1, A2 · a fresh bundle holds Persona nodes carrying both routing keys.
- test_every_roster_beat_has_a_seeded_match · covers: M2, R:DEADTIER · each named beat matches at least one seeded persona on `flow:`.
- test_init_never_overwrites_an_existing_persona · covers: M5, A5, E1, E4 · existing files are byte-identical after re-init.
- test_init_names_what_it_seeded · covers: A9 · the note names the seeded personas.
- test_both_agents_name_the_corpus_tier · covers: M3, R:SILENTGENERIC · both files route through the index before the generic.
- test_the_corpus_tier_routes_through_the_index · covers: A3 · the tier names the index, never a corpus glob.
- test_a_project_persona_beats_a_corpus_lens · covers: A4 · tier order holds.
- test_the_generic_fallback_survives_and_is_last · covers: M4, E3 · an unmatched task proceeds, and the tier is named.
- test_a_missing_corpus_soft_skips · covers: A6, E2 · no corpus on disk still selects and proceeds.
- test_the_corpus_tier_states_its_tie_break · covers: A7 · the order is documented in the agent file.
- test_the_agent_return_names_its_tier · covers: A8 · the return distinguishes project, corpus and generic.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
