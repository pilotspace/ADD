---
type: Task
title: A section the gate binds is a section the direction guide teaches
status: direction
depth: standard
scope:
  - add-method/skill/add
  - add-method/tests/skill
gives:
  - S1 the direction guide's section list — the node sections an author is taught to fill
  - S2 the `covers:` referent grammar as stated to an author
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:9ba6744ed826dc48" }
---
## CARD
goal: The direction guide teaches every node section the gate binds, including `## EDGES`, and states the full referent grammar an author may write in `covers:` — under a check that enumerates the grammar from the engine in both directions.
why: `## EDGES` is scaffolded into every Task (`- E1 <a boundary or failure case a check must cover — optional>`) and is a first-class gate referent: `referents_of` returns rules plus edges plus probed assumptions, and `unbound()` iterates it, so a filled-in `E1` with no passing check refuses the PASS. The skill corpus never once names it as a section, never states its id grammar, and never lists it as a `covers:` referent. `phases/direction.md:26` heads "## The four sections (all in the node body)" and enumerates RULES · ASSUMPTIONS · PLAN · CHECKS — EDGES is absent, and the same bullet documents an `After` part that appears nowhere in the format or the engine, so phantom vocabulary occupies the line where the real gate-binding section belongs. The two mentions that exist actively mislead: SKILL.md:79 places EDGES inside the RULES bullet, and direction.md:82 reads as prose within RULES. `direction.md:94-95` then states the grammar as `goal`/`G<n>` at quick depth and `M<n>`/`R:<CODE>` at standard, omitting both `E<n>` and `A<n>` though the engine's own referent pattern admits all five. FORMAT.md documents it correctly, and SKILL.md:173-175 explicitly tells the agent to read FORMAT.md only when a decision is genuinely unclear. So the author fills in the scaffolded line exactly as instructed and the gate refuses their PASS with "these rules have no reported passing check: E1", explained by nothing they were told to read. This repo has already been bitten and it is still undocumented at 3.3.0.
beat: direction · next: add freeze edges-documented

## RULES
<must>
- M1 The direction guide's section list includes `## EDGES` with its `E<n>` id grammar and states that a filled line is a gate-bound referent while an untouched placeholder owes nothing.
- M2 The stated `covers:` grammar matches the engine's referent pattern exactly — every form the engine admits is taught, and no form is taught that the engine rejects.
- M3 A check enumerates the referent forms from the ENGINE and from the guide and asserts the two sets are equal, in both directions.
- M4 The phantom `After` part is removed or made real; the guide names no node part the format does not have.
- M5 SKILL.md's one-line section summary no longer places EDGES inside RULES.
</must>
<reject>
- R:UNTAUGHTBINDING a section the gate binds must never be absent from the guide that teaches authoring -> "R:UNTAUGHTBINDING"
</reject>

## ASSUMPTIONS
- A1 [which] covers: S2 · the request does not say which referent forms to teach; taking every form the engine's referent pattern admits, read from the pattern itself -> if wrong the guide teaches a subset and an author's valid id looks invalid · probe: the taught set is derived from the engine constant.
- A2 [absent] covers: S1 · the request does not say what an UNFILLED edge line means; taking the scaffold placeholder as owing nothing, which is what the engine already does — only a filled line becomes a referent -> if wrong every scaffolded node is unpassable · probe: a node with an untouched E1 placeholder gates green.
- A3 [experience] covers: S1 · the request does not say what the author needs; taking the binding consequence stated at the point of authoring, because the cost lands far downstream at the gate with a message that names the id and not the rule -> if wrong the author learns it from a refusal · probe: the guide states the consequence beside the section.
- A4 [order] covers: S1 · the request does not say where EDGES belongs in the list; taking the order the scaffold writes, so the guide and the node file read the same way top to bottom -> if wrong the author hunts · probe: the guide's order matches the scaffold's.
- A5 [who] covers: S1 · n/a · the guide is read identically by every author.
- A6 [who] covers: S2 · n/a · the grammar applies to every author equally.
- A7 [when] covers: S1 · n/a · documentation has no temporal boundary; no existing node changes.
- A8 [when] covers: S2 · n/a · the grammar is evaluated at gate time, which this task does not change.
- A9 [absent] covers: S2 · n/a · an absent `covers:` is already an unbound check, refused today.
- A10 [order] covers: S2 · n/a · referent forms are alternatives, not a sequence.
- A11 [experience] covers: S2 · n/a · A3's reading covers both surfaces: the consequence is stated where the author writes.
- A12 [which] covers: S1 · n/a · the section set is the scaffold's, enumerated by M3's check.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: the direction guide's section list becomes complete and names EDGES with its grammar and binding consequence; the `covers:` grammar line states every engine-admitted form; the phantom `After` part goes; SKILL.md's summary stops nesting EDGES inside RULES; a check enumerates sections and referent forms from the engine against the guide, both directions.
scope: add-method/skill/add, add-method/tests/skill

## EDGES
- E1 an untouched `E1` placeholder — owes nothing, node gates green (A2).
- E2 a node at `--depth quick`, whose referents are `goal`/`G<n>` — the grammar must state the depth split correctly.
- E3 a probed assumption id `A<n>` — admitted by the engine and currently untaught.
- E4 FORMAT.md, which already documents EDGES correctly — must not contradict the corrected guide.
- E5 the SKILL.md line pin — the summary fix is a replacement, not an addition.

## CHECKS
- test_the_direction_guide_lists_every_scaffolded_section · covers: M1, A4, R:UNTAUGHTBINDING · sections enumerated from the scaffold.
- test_the_covers_grammar_matches_the_engine · covers: M2, M3, A1 · both directions, no form missing or invented.
- test_the_probed_assumption_form_is_taught · covers: E3 · `A<n>` appears in the stated grammar.
- test_the_quick_depth_referents_are_stated_correctly · covers: E2 · the depth split holds.
- test_an_untouched_edge_placeholder_owes_nothing · covers: A2, E1 · a scaffolded node gates green.
- test_the_guide_names_no_phantom_node_part · covers: M4 · `After` is gone or real.
- test_the_skill_summary_does_not_nest_edges_in_rules · covers: M5, E5 · the summary is corrected within the pin.
- test_the_binding_consequence_is_stated_at_authoring · covers: A3 · the guide says what a filled edge costs.
- test_format_md_and_the_guide_agree · covers: E4 · no contradiction between the two.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
