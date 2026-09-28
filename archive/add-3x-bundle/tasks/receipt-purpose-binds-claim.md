---
type: Task
title: Receipt purpose binds the claim
status: direction
depth: standard
kind: feature
sensitivity: security
milestone: evidence-has-a-purpose
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - .add/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/tests/engine/test_receipt_purpose_binds_claim.py
gives:
  - S1 local Run receipt purpose and CLI selection
  - S2 purpose-aware Task evidence selectors and code gate
  - S3 Explore findings citation and sources gate
generated: { by: add/3.6.0, at: 2026-09-16 }
verified: []
---
## CARD
goal: Support receipts cannot become code-gate proof
why: A green diagnostic command can currently be selected as the latest narrow run and change what a gate claims to have proven.
beat: scaffold · next: author receipt-purpose-binds-claim's RULES, ASSUMPTIONS and CHECKS, then add freeze receipt-purpose-binds-claim

## RULES
<must>
- M1 A local Run records exactly one purpose: bound, floor, or support; its receipt and task run stamp agree, while kind, freshness, reported ids, and exit remain independently observed.
- M2 A missing purpose reads as floor when legacy floor: regression is present and bound otherwise. A contradictory purpose and floor marker is refused or treated as unentitled, never promoted.
- M3 Only a fresh green bound receipt may satisfy a Task's code gate, CHECKS binding, refute citation, Build/Verify beat, latest narrow command hint, and release code anchor. A later support or floor run cannot displace the bound receipt.
- M4 Only a fresh green floor receipt may satisfy a declared regression floor; bound and support cannot satisfy that obligation. Keep the legacy floor marker and command form readable.
- M5 A support receipt may be cited in Explore FINDINGS as diagnostic evidence, but its presence cannot switch an Explore to the executable receipt gate; frozen questions, budget, and source references still govern its sources gate.
- M6 A local run cannot claim protected holdout origin; reject that selection before executing the command or writing a receipt. External holdout and release attestations, when introduced, bind their own subjects and provenance rather than inheriting local Run authority.
- M7 Purpose does not lower the computed security/human authority floor, the named security lens requirement, the human approval of frozen direction, or the refute and regression requirements of a bound code PASS.
</must>
<reject>
- R:SUPPORTASGATE a support probe becomes the executable gate's receipt -> "SUPPORTASGATE"
- R:FLOORASGATE a floor probe becomes the bound narrow receipt -> "FLOORASGATE"
- R:LOCALHOLDOUT a local command self-labels protected evidence -> "LOCALHOLDOUT"
- R:PURPOSECONFLICT a contradictory legacy floor marker promotes another purpose -> "PURPOSECONFLICT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3 · local callers may classify their own command as support, but cannot attest protected holdout origin; taking protected origin as external-only -> a future external adapter must be explicit.
- A2 [which] covers: S1, S2, S3 · existing receipts and floor markers predate purpose; taking absent purpose as bound unless floor: regression exists -> old task histories stay readable.
- A3 [when] covers: S1, S2, S3 · a support run may arrive before or after a bound or floor run; taking purpose filtering before newest selection -> later diagnostics cannot erase earlier proof.
- A4 [absent] covers: S1, S2, S3 · a Task may have only support receipts or an Explore may have support plus findings; taking absence of bound as no code proof and absence of FINDINGS references as open questions -> the two gates remain distinct.
- A5 [order] covers: S1, S2, S3 · receipt numbers and append-only stamps order runs, but purpose chooses eligibility first; taking newest eligible receipt within each class -> deterministic hints and refute citations.
- A6 [experience] covers: S1, S2, S3 · a builder needs to know which command to repeat; taking the refusal to name the missing bound or floor command and the support label in evidence views -> diagnosis does not masquerade as proof.

## PLAN
contract: `add run <task> [--purpose bound|support] [--floor] -- <caller command>` stamps `receipt.purpose` and run-stamp purpose; `--floor` remains regression floor and implies purpose floor. `holdout` is unavailable to local run. One normalizer maps absent purpose with legacy `floor: regression` to floor and absent purpose otherwise to bound. Code selectors consume bound, floor selector consumes floor, Explore FINDINGS may cite support but the sources gate remains authoritative.
regression: full · python3 -m pytest add-method/tests/engine -q · receipt selection touches the whole gate and beat loop
- O1 covers: M3, M5 · signal support-as-gate attempts · window each gate · threshold zero · action alert

## EDGES
- E1 A newer support receipt reports passing ids for every Must while no bound receipt exists.
- E2 A bound receipt is followed by support and floor receipts; each selector still returns the newest receipt of its authorized class.
- E3 An Explore's cited support receipt reports a failed command; source findings stay the gate's evidence class, while a code Task never accepts it as bound proof.
- E4 A legacy receipt lacks purpose; its floor marker determines only floor eligibility, including when a hand-edited contradictory purpose appears.
- E5 A local holdout request must leave no command side effect, receipt, or run stamp.

## CHECKS
- test_run_stamps_bound_support_and_floor_purpose · covers: M1, M4, E2 · receipt and stamp purpose agree and the legacy floor marker remains.
- test_legacy_purpose_normalization_and_conflict · covers: M2, E4, R:PURPOSECONFLICT · absent purpose stays compatible and contradiction never authorizes proof.
- test_support_only_cannot_enter_code_gate_or_build_beat · covers: M3, E1, R:SUPPORTASGATE · green reported ids alone cannot entitle code PASS.
- test_newer_support_does_not_displace_bound_refute_or_hint · covers: M3, E2 · bound-only selection governs refute, beat and remembered narrow command.
- test_floor_selector_ignores_support_and_bound · covers: M4, E2, R:FLOORASGATE · floor run remains separate from code proof.
- test_explore_support_preserves_sources_gate · covers: M5, E3, R:SUPPORTASGATE · cited diagnostic evidence cannot switch gate semantics.
- test_local_holdout_refuses_before_execution · covers: M6, E5, R:LOCALHOLDOUT · protected origin cannot be self-declared.
- test_security_floor_stays_human_with_support · covers: M7 · support cannot lower human authority or named-lens requirement.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
