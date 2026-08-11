---
type: Task
title: OKF-aligned Persona scaffold — the contract's routing keys get slots
status: done
milestone: v3-final-collateral
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/test_persona_okf_slots.py
  - add-method/skill/add/persona-author/references/contract.md
gives:
  - S1 `new()` Persona scaffold — frontmatter slots for vibe · flow · task-kinds · not-when · description · sources
  - S2 `tests/engine/test_persona_okf_slots.py` — the suite pinning the slots
  - S3 `references/contract.md` frontmatter block — documents `description:` and `sources:` (OKF provenance)
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "human:tindang", at: 2026-08-11, act: freeze, authority: process, direction: "sha256:e7702f38e73b5931" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:c87281785d434593" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/okf-persona-template.d/runs/1.md }
  - { by: "human:tindang", at: 2026-08-11, act: refreeze, authority: process, direction: "sha256:28e89d393fd35f44" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:4c2d170a9b29481f" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/okf-persona-template.d/runs/2.md }
  - { by: "human:tindang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/okf-persona-template.d/runs/2.md, brief: "sha256:4c2d170a9b29481f" }
---
## CARD
goal: `add new Persona` scaffolds a slot for every contract-recommended routing key plus OKF's description/sources — an instruction with no slot to fill is an instruction that does not happen
why: the contract calls vibe/flow/task-kinds routing-critical, yet the scaffold offers none of them; OKF (Open Knowledge Format v0.2) names description recommended and sources the provenance family, and ADD's trust layer is already OKF-shaped
beat: done · next: add status
## RULES
<must>
- M1 the Persona scaffold writes a placeholder slot for every contract-recommended routing key (vibe, flow, task-kinds, use-when, not-when) — and a caller-supplied value always wins over the placeholder
- M2 OKF-recommended `description:` and provenance `sources:` slots are scaffolded, using OKF's key names
- M3 the slots are scaffolding, never validation — `new` refuses nothing about their content (the engine stays a notary)
</must>
<reject>
- R:CLOBBER a placeholder overwriting a caller-supplied field value -> "CLOBBER"
</reject>
## ASSUMPTIONS
- A1 [who] covers: S1,S2,S3 · the request does not say who fills the slots; taking "the authoring human or agent after scaffold — the engine never checks them" -> cost if wrong: authors expect lint that never comes
- A2 [which] covers: S1,S2,S3 · the request does not say which OKF fields are in scope; taking "description + sources only, in scaffold, suite and doc alike — OKF doc-status and stale_after excluded by user decision (status collides with ADD task-lifecycle)" -> cost if wrong: rework lands in 3.1 · probe: the scaffold carries no OKF doc-status key
- A3 [when] covers: S1,S2,S3 · the request does not say when slots appear; taking "at `new` time only — existing authored personas are never edited, the suite pins new-time behavior, the doc describes the new-time scaffold" -> cost if wrong: retroactive edits to authored rosters
- A4 [absent] covers: S1,S2,S3 · the request does not say what an absent caller field means; taking "absent -> placeholder written; supplied -> recorded verbatim — pinned by the suite, stated by the doc" -> cost if wrong: clobbered authoring or mute slots
- A5 [order] covers: S1,S2,S3 · the request does not say slot order; taking "contract.md's frontmatter block order: vibe -> flow -> task-kinds -> use-when -> not-when -> description -> sources; the suite asserts presence, never order" -> cost if wrong: cosmetic diff churn only
## PLAN
contract: the Persona branch of `new()` (BODIES untouched — slots are frontmatter) plus the contract.md frontmatter block naming the two OKF keys
scope: add-method/tooling/add.py · add-method/tests/engine/test_persona_okf_slots.py · add-method/skill/add/persona-author/references/contract.md
## EDGES
- E1 caller supplies some-but-not-all keys — supplied values verbatim, the rest get placeholders
## CHECKS
- test_scaffold_offers_every_routing_slot · covers: M1 · vibe/flow/task-kinds/use-when/not-when each present as a frontmatter slot
- test_scaffold_offers_okf_description_and_sources · covers: M2 · OKF's `description:` and plural `sources:` are scaffolded
- test_caller_values_survive_the_scaffold · covers: M1,E1,R:CLOBBER · supplied fields verbatim, missing ones placeholdered
- test_no_okf_doc_status_key · covers: A2 · the probe: no `status:` on a Persona, OKF doc-status stays out
- test_slots_are_placeholders_not_validation · covers: M3 · a garbage `flow:` value is recorded, not refused
red-first: every check MUST fail first.
## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>
## LESSONS
- <lesson> -> add learn <lens>
