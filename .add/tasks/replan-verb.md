---
type: Task
title: Engine replan stamp + build.md steering-vs-contract amendments
status: done
depth: standard
sensitivity: architecture
milestone: dynamic-flow
scope:
  - add-method/tooling
  - .add/tooling
  - add-method/skill/add
  - .claude/skills/add
  - add-method/src/add_method/_bundled/skill/add
  - add-method/tests/skill
  - add-method/src/add_method/_bundled/tooling
  - add-method/tests/engine
  - add-method/docs/13-command-reference.md
  - 13-command-reference.md
gives:
  - S1 the `replan` verb — a recorded steering amendment on a frozen task, one act stamp carrying the note, process authority
  - S2 the refusal set — an unfrozen task refuses (nothing is being steered) and an empty note refuses (invisible steering)
  - S3 the seal boundary — replan touches no body section, no direction sha, no check; a gate after N replans behaves byte-identically
  - S4 `phases/build.md` § steering amendments — the documented split between steering (replan) and contract change (change-request, refreeze)
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "Tin Dang", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:b95ec88325a0a3dd" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:e523d5793d17c467" }
  - { by: "Tin Dang", at: 2026-08-11, act: refreeze, authority: human, direction: "sha256:b95ec88325a0a3dd" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:ffcad39b6f243ba4" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/replan-verb.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-11, act: refreeze, authority: human, direction: "sha256:49cca8291fe7882b" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:7603a03fb4dba3f4" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/replan-verb.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-11, act: gate, authority: plan, outcome: PASS, receipt: /tasks/replan-verb.d/runs/2.md, brief: "sha256:7603a03fb4dba3f4" }
---
## CARD
goal: mid-build discovery has a recorded, cheap lane — a replan stamp carries the steering note on the node's own trail — while every contract change keeps the full change-request ceremony
why: today the only recorded correction is a re-freeze; everything cheaper happens off the record, which is exactly where method-bypassing starts

## RULES
<must>
- M1 `add replan` on a frozen task appends one act stamp to the node's trail — the note text, process authority, nothing else written
- M2 the refusals hold: an unfrozen task refuses with what-to-do-instead; a missing or blank note refuses — steering that says nothing records nothing
- M3 the seal is untouched: the node body is byte-identical after a replan, the freeze stamp's direction sha is unchanged, and a green gate passes after N replans exactly as after zero
- M4 `phases/build.md` documents the split: strategy shifts, discovered facts and approach notes are steering — recorded with the replan verb; a frozen `gives:` or check change stays a change-request back to Direction
- M5 the engine pins are re-aimed and every tooling twin ships the same bytes — the parity suite stays green
</must>
<reject>
- R:SEAL_TOUCH replan rewrites any body section, resets a freeze, or alters a check — the stamp is additive or it is refused -> "SEAL_TOUCH"
- R:SILENT_STEER a steering event lands with no note, or on a task whose direction was never frozen -> "SILENT_STEER"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who may replan; taking: the builder at process authority — steering is the builder's record, the human reads it at the gate -> cost: none material
- A2 [who] covers: S4 · the request does not say who classifies steering vs contract; taking: the builder, against the doc's split — the tripwires (frozen gives, checks) already catch a misclassification mechanically -> cost: a mislabelled steer is caught late, at the gate
- A3 [which] covers: S1 · the request does not say which fields the stamp carries; taking: act, by, at, authority, note — the existing stamp grammar, one new act word, no new key style -> cost: none material
- A4 [which] covers: S4 · the request does not say which amendments qualify as steering; taking: anything that changes NO frozen surface — strategy, sequencing, discovered constraints, scope observations -> cost: none material · probe: build.md states the no-frozen-surface test
- A5 [when] covers: S1 · the request does not say when replan may fire; taking: any time between freeze and close — a steering note after the gate is a lesson, not a replan -> cost: none material
- A6 [when] covers: S3 · the request does not say whether a replan re-arms the brief-entry check; taking: no — the brief entered the build once; steering does not restart it -> cost: a stale brief steers on · probe: gate passes with the original brief after a replan
- A7 [absent] covers: S2 · the request does not say what an empty note means; taking: refusal — an empty note is the silent steering this verb exists to end -> cost: none material · probe: the refusal test
- A8 [absent] covers: S3 · the request does not say what replan does on a node with no freeze; taking: refusal naming the freeze as what is missing -> cost: none material · probe: the refusal test
- A9 [order] covers: S1, S3 · the request does not say how N replans order; taking: append-only on the trail, newest last — the same order every stamp already uses -> cost: none material
- A10 [which] covers: S2 · [which] n/a · the refusal set is closed by M2 — two conditions, no selection semantics
- A11 [which] covers: S3 · [which] n/a · the boundary names what replan may never touch; it selects nothing
- A12 [when] covers: S2 · [when] n/a · refusals are immediate, not scheduled
- A13 [when] covers: S4 · the request does not say when the doc split is consulted; taking: at the moment of discovery, before any edit — build.md places it with the three-lines rules -> cost: none material
- A14 [absent] covers: S1 · the request does not say what a replan on a missing node does; taking: the standard no-such-node refusal every verb already gives -> cost: none material
- A15 [absent] covers: S4 · [absent] n/a · the doc section either exists (checked) or the build is not done
- A16 [order] covers: S2 · [order] n/a · two refusal conditions with no precedence semantics — either refuses alone
- A17 [order] covers: S4 · [order] n/a · a documentation split carries no ordering semantics
- A18 [who] covers: S2 · [who] n/a · refusals are engine-mechanical; no actor distinction exists
- A19 [who] covers: S3 · [who] n/a · the seal boundary binds the verb itself, whoever invokes it

## PLAN
contract: S1–S4 as `gives:` — one engine function + one dispatch entry (add.py · cli.py), one doc section (build.md), pins re-aimed, twins synced
scope: add-method/tooling/{add.py,cli.py,engine_pin.py} · add-method/skill/add/phases/build.md · twins (.add/tooling, _bundled/tooling, skill mirrors) · checks in add-method/tests/engine/test_replan_verb.py + add-method/tests/skill/test_build_replan_doc.py
strategy: red suites first → implement add.replan (frozen-check · note-check · append stamp) → wire the cli verb → write the build.md split section → re-aim ENGINE_MD5 + ENGINE_PKG_MD5 → sync all twins → green
regression floor: add-method/tests/engine (all) + add-method/tests/skill (all) + add-method/tooling/test_tree_parity.py

## EDGES
- E1 a replan on a task that is frozen AND already gated done — refused as after-the-fact (the trail is closed; the note belongs in LESSONS)
- E2 the stamp must parse under the T0 frontmatter subset — the note is one inline-quoted line, never a block scalar
- E3 adding a verb the docs do not name breaks the orphan-verb guard — build.md must name replan in the same task

## CHECKS
- test_replan_stamps_note_on_frozen_task · covers: M1, A9 · a frozen task gains exactly one replan stamp carrying the note at process authority
- test_replan_refuses_unfrozen · covers: M2, R:SILENT_STEER, A8 · an unfrozen task refuses and stamps nothing
- test_replan_refuses_empty_note · covers: M2, R:SILENT_STEER, A7 · a missing or blank note refuses and stamps nothing
- test_replan_refuses_closed_task · covers: E1 · a done task refuses — the note belongs in LESSONS
- test_replan_leaves_seal_and_body_untouched · covers: M3, R:SEAL_TOUCH · body byte-identical, direction sha unchanged, node still frozen
- test_gate_unaffected_by_replans · covers: M3, A6, E2 · freeze → brief → replan ×2 → run → gate PASS succeeds exactly as with zero replans — the engine re-reads the stamped trail through T0 the whole way
- test_replan_is_dispatched · covers: S1, E3 · the cli parser owns a replan verb
- test_build_documents_replan_split · covers: M4, A4 · build.md names the replan verb and states the no-frozen-surface steering test
- test_add_py_matches_ENGINE_MD5 · covers: M5 · the add.py pin is re-aimed to the shipped bytes
- test_cli_py_matches_ENGINE_PKG_MD5 · covers: M5 · the cli.py pin is re-aimed to the shipped bytes
- test_engine_bundle_matches_canonical · covers: M5 · the bundled tooling twin ships the same bytes
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
