---
type: Task
title: Prevention earns binding
status: direction
depth: standard
kind: feature
sensitivity: architecture
milestone: learning-earns-binding
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - .add/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/tests/engine/test_prevention_earns_binding.py
gives:
  - S1 escape binding validation receipt contract
  - S2 later independent eligibility reader
generated: { by: add/3.6.0, at: 2026-09-16 }
verified: []
---
## CARD
goal: Escape prevention cannot bind until a later independent Task validates it
why: a resolvable node or file address proves that a proposed prevention exists, but the filing Task can still bind its own proposal before anyone exercises the prevention.
beat: direction · next: close dependencies, review Direction, then freeze at plan authority

## RULES
<must>
- M1 `fold <lens> <match> --bind <decision> --validation /tasks/<later>.d/runs/<n>.md` is required only when any matched open delta is an escape; ordinary fold, `--reject`, and non-escape `--bind` preserve their current contracts.
- M2 validation names a receipt owned by a distinct Task, and that Task has a run stamp plus a later PASS gate that both cite the same receipt. The receipt is green, fresh, committed, and purpose `bound`; legacy or other-purpose evidence cannot bind an escape.
- M3 Git proves the validation receipt's committed `head` descends from the committed filing revision containing the exact delta id and tail. A calendar date, file mtime, list position, signer string, or same working tree is never ordering evidence.
- M4 the prevention's repo file is in the later Task receipt's sealed scope and `scope_digest` with the exact Git blob named by the receipt. Node-only and `file::check` prevention addresses remain valid for ordinary fold, but cannot earn policy without a concrete scoped file subject.
- M5 every matched escape is preflighted before any delta retag or decision write. One ineligible item refuses the whole call as `R:UNVALIDATED`, naming the delta, prevention and missing/conflicting receipt fact.
- M6 a filing delta needs a durable commit anchor. The engine locates the earliest reachable commit containing the exact delta id and canonical tail; absent, ambiguous or rewritten history is ineligible rather than inferred.
</must>
<reject>
- R:UNVALIDATED an escape binds without later independent eligible validation -> "UNVALIDATED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · independence means a distinct Task identity plus later committed evidence, not merely a different actor label · probe: the filing Task's own receipt refuses
- A2 [which] covers: S1, S2 · only escape `--bind` gains the rung · probe: ordinary fold, reject and plain lesson bind retain compatibility
- A3 [when] covers: S1, S2 · Git ancestry and the filing commit establish later order · probe: same-day records with no ancestry refuse
- A4 [absent] covers: S1, S2 · missing commit, purpose, scope seal, blob, run stamp or matching gate refuses atomically · probe: delete each subject independently
- A5 [order] covers: S1, S2 · purpose and scope eligibility are checked before receipt chronology · probe: a newer support receipt cannot validate
- A6 [experience] covers: S1, S2 · refusal names delta, prevention and the one fact to repair · probe: multi-match call reports the first stable failing id and writes nothing

## PLAN
contract: add an explicit `--validation` fold argument and one pure eligibility reader. Resolve the filing commit, validation receipt owner/stamp/gate, bound purpose, sealed scope and exact blob before the existing atomic retag/bind write. Do not broaden what counts as a prevention.
depends-on: `scope-in-the-seal` for scope authority and `receipt-purpose-binds-claim` for bound entitlement; this Task cannot enter Build until both are gated.
regression: full · `python3 -m pytest add-method/tests/engine -q` · fold, receipts, Git and stamps cross the trust spine

## EDGES
- E1 filing Task cites its own later-looking receipt -> R:UNVALIDATED with no write
- E2 distinct Task has a same-day green receipt but no committed ancestry -> refusal
- E3 descendant receipt is green but support-purpose, stale, ungated, or scopes another file/blob -> refusal
- E4 distinct later Task has a committed descendant bound receipt and PASS gate over the exact prevention blob -> bind succeeds
- E5 several matched escapes include one ineligible validation -> all remain open and no decision is written

## CHECKS
- test_escape_bind_requires_explicit_validation · covers: M1, R:UNVALIDATED, A2 · acceptance · escape bind refuses while compatible fold routes remain green
- test_self_or_date_only_validation_refuses · covers: M2, M3, E1, E2, A1, A3 · acceptance · identity and Git order both matter
- test_receipt_stamp_gate_and_bound_purpose_must_agree · covers: M2, E3, A4, A5 · acceptance · hand-edited and support receipts never authorize
- test_exact_sealed_scope_blob_is_required · covers: M4, E3, A4 · acceptance · file and blob subject match
- test_committed_descendant_validation_can_bind · covers: M2, M3, M4, M6, E4 · acceptance · positive eligibility control
- test_mixed_match_refuses_atomically_with_actionable_reason · covers: M5, E5, A6 · acceptance · no partial retag or decision
red-first: every new eligibility check MUST fail before Build; compatibility controls remain green.

## EVIDENCE
receipt: pending
gate: pending; dependencies are not yet closed

## LESSONS
- pending
