---
type: Task
title: scope-in-the-seal
status: done
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
  - S1 freeze/refreeze stamps a digest of its complete `scope:` list, and `_scoped_by_any` routes a path only through the latest freeze-class stamp when that digest still matches the node's current scope
  - S2 `quick_hit` classifies an open Task as scope owner through its latest matching freeze/refreeze scope seal
generated: { by: add/3.6.0, at: 2026-09-13 }
verified:
  - { by: "human:Tin Dang", at: 2026-09-19, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/1.md, answers: "A1=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-19, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/2.md, answers: "A2=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-19, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/3.md, answers: "A3=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-20, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/4.md, answers: "A4=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-20, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/5.md, answers: "A5=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-20, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/6.md, answers: "A6=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-22, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/7.md, answers: "E1=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-22, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/8.md, answers: "E2=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-23, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/9.md, answers: "R:LEGACY_SCOPE=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-23, act: interview, authority: human, interview: "sha256:34450395beb5dc59", receipt: /tasks/scope-in-the-seal.d/interviews/10.md, answers: "R:STALE_SCOPE=confirm" }
  - { by: "human:Tin Dang", at: 2026-09-23, act: freeze, authority: human, direction: "sha256:3ab369d20c2e2a2b", binding: "sha256:b85b43f28c97dd59", gives: "sha256:198c49a254981f14" }
  - { by: "cli", at: 2026-09-23, act: brief, authority: process, brief: "sha256:ab66a07a3e611910" }
  - { by: "process:run", at: 2026-09-23, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-in-the-seal.d/runs/1.md }
  - { by: "advisor:engine-notary", at: 2026-09-23, act: refute, authority: process, outcome: refuted, probes: 29, receipt: /tasks/scope-in-the-seal.d/runs/1.md, tier: T2, note: "quoted scope entry whitespace changed routing while the scope seal stayed equal", changed: "leading and trailing whitespace in one quoted scope entry" }
  - { by: "human:Tin Dang", at: 2026-09-23, act: refreeze, authority: human, direction: "sha256:3ab369d20c2e2a2b", binding: "sha256:b85b43f28c97dd59", gives: "sha256:198c49a254981f14", scope: "sha256:c0313a618272112a" }
  - { by: "cli", at: 2026-09-23, act: brief, authority: process, brief: "sha256:6fdeb5b66a03a162" }
  - { by: "process:run", at: 2026-09-23, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-in-the-seal.d/runs/2.md }
  - { by: "advisor:engine-notary", at: 2026-09-23, act: refute, authority: process, outcome: held, probes: 31, receipt: /tasks/scope-in-the-seal.d/runs/2.md, tier: T2, note: "compact-JSON exact-entry set held across scalar/list/block/Unicode/separator, stale/latest/signature/authority/state and twin/pin probes", changed: "scope entry representations, stamp chronology, signer/authority and task state" }
  - { by: "process:run", at: 2026-09-23, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/scope-in-the-seal.d/runs/3.md }
  - { by: "process:run", at: 2026-09-23, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/scope-in-the-seal.d/runs/4.md }
  - { by: "advisor:engine-notary", at: 2026-09-23, act: refute, authority: process, outcome: held, probes: 31, receipt: /tasks/scope-in-the-seal.d/runs/2.md, tier: T2, note: "compact-JSON exact-entry set held across scalar/list/block/Unicode/separator, stale/latest/signature/authority/state and twin/pin probes", changed: "scope entry representations, stamp chronology, signer/authority and task state" }
  - { by: "process:run", at: 2026-09-23, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-in-the-seal.d/runs/5.md }
  - { by: "advisor:engine-notary", at: 2026-09-23, act: refute, authority: process, outcome: held, probes: 31, receipt: /tasks/scope-in-the-seal.d/runs/5.md, tier: T2, note: "compact-JSON exact-entry set held across scalar/list/block/Unicode/separator, stale/latest/signature/authority/state and twin/pin probes", changed: "scope entry representations, stamp chronology, signer/authority and task state" }
  - { by: "human:Tin Dang", at: 2026-09-23, act: gate, authority: human, outcome: PASS, receipt: /tasks/scope-in-the-seal.d/runs/5.md, brief: "sha256:4dd7d2ffce92f3b2", reason: "All ten security decisions approved; scoped receipt 5 and floor receipt 4 passed with bound test IDs; T2 refutation held across 31 adversarial probes; artifact twins and engine pin match." }
advised_by: engine-notary
---
## CARD
goal: a human freeze seals the scope it approved, so a later frontmatter edit cannot route a sensitive path without a human refreeze
why: a `human:` signature is authority only over the fields its seal names; current routing trusts mutable `scope:` entries that neither existing freeze digest covers
beat: done · next: add status

## RULES
<must>
- M1 every freeze-class stamp records a deterministic digest over the complete current `scope:` list, separate from `direction:` and `binding:` so existing seals retain their original meaning (from: /milestones/seal-what-you-signed.md EXIT 1 · fails-on: adding `scope:` to an existing direction digest and forcing every old node to refreeze)
- M2 `_scoped_by_any` accepts a route only from the latest `freeze` or `refreeze` stamp whose `by:` is `human:`, whose authority is human, and whose scope digest equals the node's current scope digest (from: /milestones/seal-what-you-signed.md EXIT 1 · fails-on: any earlier matching stamp or a stale current scope still routes)
- M3 the owner half of `quick_hit` reads every scope entry on an open Task and accepts either freeze-class act only when its latest scope digest matches (from: /milestones/seal-what-you-signed.md SCOPE · fails-on: a second scope entry or refreeze has no owner)
</must>
<reject>
- R:LEGACY_SCOPE a freeze-class stamp without a scope digest routes any path -> "LEGACY_SCOPE"
- R:STALE_SCOPE a scope changed after its latest seal routes a path before a human refreeze -> "STALE_SCOPE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 · the milestone does not say whether a `human:` string is identity-proof; taking it as the existing deliberate signer claim only, while owner classification retains its existing authority floor -> treating a notary as an identity provider would overstate the control
- A2 [which] covers: S1 S2 · the milestone does not say whether reordered or duplicate scope entries are semantically distinct; taking the normalized authored entries as a set, sorted and de-duplicated before hashing -> sealing raw YAML order would demand refreeze for a behaviorally identical scope
- A3 [when] covers: S1 S2 · the milestone does not say whether a legacy stamp may route during migration; taking fail-closed immediately -> older human-frozen work needs a discoverable refreeze before it can exempt or own a path
- A4 [absent] covers: S1 S2 · the milestone does not say what an absent or malformed scope digest means; taking it as unverified and non-routing -> fail-open would recreate the unsigned-scope bypass
- A5 [order] covers: S1 S2 · the milestone does not say which seal wins after refreezes; taking the latest freeze-class stamp only -> an earlier seal could authorize a scope the later approver did not approve
- A6 [experience] covers: S1 S2 · the milestone does not say how migration friction is presented to an operator; taking a refusal or diagnostic that names refreeze as the remedy -> an unexplained loss of routing could look like a broken quick lane

## PLAN
contract: add one scope-digest writer and one shared reader for the latest freeze-class stamp; preserve existing direction and binding digest meanings, and fail closed when the stamp cannot prove scope coverage. The tracked canonical and bundled `add.py` are the implementation pair; `.add/tooling/add.py` and `.claude/skills` copies are ignored generated runtime evidence, so they are verified by the existing parity/vendor path rather than authored here.
strategy: add the red routing fixture first, then implement canonical scope hashing and latest-stamp validation in the engine without altering unrelated stamp readers
regression: affected · python3 -m pytest add-method/tests/engine/test_scope_in_the_seal.py -q · run the full engine suite before a receipt because the stamp shape has many readers

## EDGES
- E1 Given a human freeze for scope A and a later human refreeze for scope B · When a lesson path lies only in B · Then routing follows the latest B seal and never the older A seal
- E2 Given a legacy human freeze that has no scope digest · When its current `scope:` names a sensitive path · Then it routes nothing until a human refreeze records scope coverage

## CHECKS
- test_freeze_and_refreeze_stamp_complete_scope · covers: M1 · unit · proves both freeze-class writers carry one deterministic digest for every scope entry
- test_scope_digest_normalizes_order_and_duplicates · covers: M1, A2 · unit · proves behaviorally identical scope sets keep one seal value
- test_latest_refreeze_wins_and_unchanged_scope_routes · covers: M2, E1 · acceptance · proves the latest matching seal routes and an earlier seal cannot outrank it
- test_legacy_and_changed_scopes_fail_closed · covers: R:LEGACY_SCOPE, R:STALE_SCOPE, E2 · acceptance · proves absent and stale scope coverage route nothing
- test_scope_owner_reads_refreeze_and_open_closed_states · covers: M3 · acceptance · proves the owner half reads a valid refreeze and preserves its existing Task/open-state boundary
red-first: `python3 -m pytest add-method/tests/engine/test_scope_in_the_seal.py -q` fails before Build because freeze writes no scope seal, mutable/legacy scopes route, and the owner reader ignores refreeze.

## EVIDENCE
receipt: /tasks/scope-in-the-seal.d/runs/5.md · kind: test-ids · 5/5 reported · exit 0 · 2026-09-23
refute: held · 31 probe(s) · tier T2 · by advisor:engine-notary · against /tasks/scope-in-the-seal.d/runs/5.md · 2026-09-23 · compact-JSON exact-entry set held across scalar/list/block/Unicode/separator, stale/latest/signature/authority/state and twin/pin probes · changed: scope entry representations, stamp chronology, signer/authority and task state
gate: PASS · authority human · by human:Tin Dang · receipt /tasks/scope-in-the-seal.d/runs/5.md · 2026-09-23 · All ten security decisions approved; scoped receipt 5 and floor receipt 4 passed with bound test IDs; T2 refutation held across 31 adversarial probes; artifact twins and engine pin match.

## LESSONS
none yet
- none filed — no lesson cites /tasks/scope-in-the-seal.md (add learn <lens> "<lesson>" --evidence /tasks/scope-in-the-seal.md)
