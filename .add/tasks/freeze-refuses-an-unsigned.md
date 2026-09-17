---
type: Task
title: freeze-refuses-an-unsigned
status: direction
depth: standard
sensitivity: security
milestone: seal-what-you-signed
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/tests/engine
  - add-method/FORMAT.md
  - add-method/CHANGELOG.md
gives:
  - S1 `freeze` records lifecycle approval only when a computed human floor has an explicit human signer, and it refuses records that have no lifecycle to seal
generated: { by: add/3.6.0, at: 2026-09-13 }
verified: []
advised_by: engine-notary
---
## CARD
goal: a computed human floor cannot be satisfied by freeze's default `cli` signer, and non-lifecycle documents cannot receive a lifecycle seal
why: the prior signature repair still lets a default CLI freeze claim human authority, while a Persona can acquire a freeze stamp despite having no direction lifecycle
beat: direction · next: add interview freeze-refuses-an-unsigned, then add freeze freeze-refuses-an-unsigned --by "human:<name>"

## RULES
<must>
- M1 `freeze` refuses its default `by: cli` when `authority_for` computes human, before writing any freeze-class stamp (from: /milestones/seal-what-you-signed.md EXIT 2 · fails-on: a sensitive scope receives `authority: human` without a deliberate human signer)
- M2 `freeze` accepts only `Task` and `Milestone` lifecycle nodes, leaving Persona and other records without freeze-class stamps (from: /milestones/seal-what-you-signed.md EXIT 2 · fails-on: a document with no lifecycle is made to look like approved direction)
</must>
<reject>
- R:UNSIGNED default CLI identity is accepted as a human freeze at a computed human floor -> "UNSIGNED"
- R:NOTATASK a non-lifecycle node receives a freeze or refreeze stamp -> "NOTATASK"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the milestone does not say whether `human:` proves a person; taking it as the deliberate signer syntax already used by routing -> the notary could be mistaken for identity verification
- A2 [which] covers: S1 · the milestone does not say whether all future ABF types may gain a lifecycle; taking the current `LIFECYCLE_TYPES` registry as the closed allowlist -> a new lifecycle type would require an explicit engine change rather than silently inheriting freeze
- A3 [when] covers: S1 · the milestone does not say whether an explicit non-human signer may freeze at human floor; taking every signer below human as refused -> a weaker claim could silently satisfy a human gate
- A4 [absent] covers: S1 · the milestone does not say how an omitted `--by` should be represented; taking the existing default `cli` as unsigned at a human floor -> a bare command remains distinguishable from a named human claim
- A5 [order] covers: S1 · the milestone does not say whether type validation precedes signer validation; taking lifecycle validation first -> an invalid document receives the most direct repair regardless of flags
- A6 [experience] covers: S1 · the milestone does not say whether the refusal should expose internal floor computation; taking a concise R code plus runnable next step -> operators can correct the signer or choose a lifecycle node without guessing

## PLAN
contract: add actionable R:UNSIGNED and R:NOTATASK refusals to `freeze`, with no write on either refusal and no weaker authority fallback. The tracked canonical and bundled `add.py` are the implementation pair; ignored runtime copies are parity/vendor evidence, not manually edited scope.
strategy: exercise the bare sensitive freeze and a Persona freeze through the public function; implement the shared lifecycle guard and signer check before stamp creation
regression: affected · python3 -m pytest add-method/tests/engine/test_freeze_refuses_an_unsigned.py -q · run the full engine suite before a receipt because `freeze` is shared infrastructure

## EDGES
- E1 Given an authored task whose scope computes to human · When `freeze` is called with its default signer · Then it returns R:UNSIGNED and records no stamp
- E2 Given a newly created Persona · When `freeze` is called with a human-looking signer · Then it returns R:NOTATASK and records no stamp

## CHECKS
- test_default_cli_human_floor_refuses_without_a_write · covers: M1, R:UNSIGNED, E1 · acceptance · proves the default signer has no stamp or byte-level record effect
- test_non_lifecycle_freeze_refuses_without_a_write · covers: M2, R:NOTATASK, E2 · acceptance · proves a Persona cannot receive a lifecycle seal
- test_explicit_empty_or_placeholder_human_signer_refuses_without_a_write · covers: M1 · acceptance · proves human authority requires a deliberate non-placeholder signer claim
- test_explicit_human_signer_is_recorded_as_a_claim · covers: M1, A1, A3 · control · proves the refusal does not reject a deliberate human claim or pretend to authenticate it
red-first: `python3 -m pytest add-method/tests/engine/test_freeze_refuses_an_unsigned.py -q` fails before Build because invalid signer and non-lifecycle calls currently record stamps.

## EVIDENCE
receipt: pending — targeted red run is recorded in tmp/seal-direction-evidence.md
gate: HARD-STOP until the human answers the open assumptions, rejects, and edges

## LESSONS
none yet
