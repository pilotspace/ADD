---
type: Task
title: Engine: sources rung on evidence ladder + explore sufficiency gate
status: done
depth: standard
sensitivity: architecture
milestone: dynamic-flow
depends_on:
  - /tasks/explore-lane.md
needs:
  - /tasks/explore-lane.md#gives
scope:
  - add-method/tooling
  - .add/tooling
  - add-method/src/add_method/_bundled/tooling
  - add-method/tests/engine
gives:
  - S1 the explore budget floor — freeze on a kind-explore task refuses while its PLAN carries no budget line
  - S2 the sufficiency gate — a PASS on a kind-explore task demands every Must answered by a FINDINGS line that names it and carries an evidence ref; the refusal lists the open questions
  - S3 the sources record — a passing explore gate stamps evidence kind sources with the closed-question tally on the node's trail
  - S4 the untouched path — a task with no explore kind freezes and gates byte-identically to today
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "Tin Dang", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:c2c37c75e8eb7048" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:5a61988f3850f3b9" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/sources-receipt.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-11, act: refreeze, authority: human, direction: "sha256:fcc2b309fb918581" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:4ea8acde440b7dd5" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/sources-receipt.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-11, act: gate, authority: plan, outcome: PASS, receipt: /tasks/sources-receipt.d/runs/2.md, brief: "sha256:4ea8acde440b7dd5" }
---
## CARD
goal: the explore lane's two doc-enforced promises become engine-enforced — no budget, no freeze; open questions, no PASS — and the receipt ladder gains an honest rung for cited findings
why: explore-lane shipped with A6/A7 disclosed as doc-only gaps; a lane whose floor lives in prose alone will drift the first time it is inconvenient

## RULES
<must>
- M1 freeze on a task whose kind is explore refuses while `## PLAN` has no `budget:` line — the refusal names the missing line; with the line present it freezes normally
- M2 gate PASS on a kind-explore task binds FINDINGS to RULES: every `M<n>` must be answered by an `F` line naming it (the `answers M<n>` grammar) and carrying an `evidence:` ref; any unanswered Must refuses the PASS and the refusal lists the open question ids
- M3 a passing explore gate records evidence kind `sources` and the closed tally (n/m questions) on the gate stamp — visible on the trail, no runs/ file required for a findings-only explore
- M4 a task with no `kind: explore` is untouched: freeze and gate behave byte-identically to today, proven by the existing engine suite staying green unmodified
- M5 the engine pin is re-aimed and every tooling twin ships the same bytes — the parity suite stays green
</must>
<reject>
- R:HOLLOW_EXPLORE an explore gates PASS with an unanswered frozen question, or an F line closes a question with no evidence ref -> "HOLLOW_EXPLORE"
- R:UNBOUNDED an explore freezes with no declared budget -> "UNBOUNDED"
- R:REGRESS any behavior change on non-explore tasks -> "REGRESS"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S2 · the request does not say who judges sufficiency; taking: the gate binds the mechanical half (every question named, evidenced); WHETHER the answer suffices stays the gate-caller's judgment, exactly as check adequacy does today -> cost: none material
- A2 [who] covers: S1, S3 · [who] n/a · freeze refusals and stamp records are engine-mechanical; no actor distinction exists
- A3 [who] covers: S4 · [who] n/a · an untouched path has no new actors
- A4 [which] covers: S1 · the request does not say which budget forms qualify; taking: any non-empty text after the budget key — the engine checks presence, never arithmetic; enforcement of the NUMBER stays human, like exit criteria -> cost: a vacuous budget line passes · probe: the freeze test accepts any authored budget text
- A5 [which] covers: S2 · the request does not say which FINDINGS grammar binds; taking: the answers-M grammar the explore-lane guide froze, evidence ref required on the same line -> cost: guide and engine drift if the guide rewords · probe: the binding test quotes the guide's grammar
- A6 [which] covers: S3 · the request does not say which receipt kinds an explore may still use; taking: sources is additive — an explore that ran real commands may still gate on a run receipt; the sources path is for findings-only explores -> cost: none material
- A7 [which] covers: S4 · [which] n/a · untouched means all of it — no case selection
- A8 [when] covers: S1 · the request does not say when the budget must exist; taking: at freeze — the approval IS questions plus budget, per the frozen explore-lane contract -> cost: none material
- A9 [when] covers: S2 · the request does not say when FINDINGS is read; taking: at gate time, from the node body as it stands — the same read the gate already does for CHECKS binding -> cost: none material
- A10 [when] covers: S3, S4 · [when] n/a · a stamp records at the gate instant; the untouched path has no timing change
- A11 [absent] covers: S1 · the request does not say what a non-explore task with a budget line does; taking: nothing — the budget floor keys on the kind, never on the line -> cost: none material
- A12 [absent] covers: S2 · the request does not say what an explore with no Musts gates on; taking: refuse the PASS — an explore with no frozen questions has nothing to be sufficient about; the freeze scaffold already demands rules -> cost: none material
- A13 [absent] covers: S3 · the request does not say what RISK-ACCEPTED records; taking: the existing signed-reason path unchanged — open questions named in the reason, no sources kind claimed -> cost: none material
- A14 [absent] covers: S4 · [absent] n/a · the untouched path is the absent-kind case itself
- A15 [order] covers: S2 · the request does not say refusal precedence when budget AND questions both fail at gate; taking: the freeze already blocked the budgetless case, so the gate meets only open questions; existing refusal order otherwise unchanged -> cost: none material
- A16 [order] covers: S1, S3, S4 · [order] n/a · single refusal per verb, no ordering semantics

## PLAN
contract: S1–S4 as `gives:` — two guarded branches in the engine (freeze · gate), one stamp extension, pins re-aimed, twins synced; no cli change, no new verb
budget: engine-only — roughly 40 lines of add.py, zero new files outside tests
scope: add-method/tooling/{add.py,engine_pin.py} · twins (.add/tooling, _bundled/tooling) · checks in add-method/tests/engine/test_explore_gate.py
strategy: red suite first → freeze budget-floor branch (kind gate) → gate FINDINGS binding branch (answers-M grammar, evidence ref, open-question refusal) → sources stamp on PASS → re-aim ENGINE_MD5 → sync twins → green
regression floor: add-method/tests/engine (all, unmodified) + add-method/tooling/test_tree_parity.py

## EDGES
- E1 an explore whose FINDINGS answers a question the RULES never froze — ignored by the binding (extra findings are welcome, only Musts bind)
- E2 the F-line grammar under the T0 parser — one physical line per finding, the same one-line discipline every bound grammar in the bundle uses
- E3 a kind-explore task that ALSO has executable checks — the run-receipt path still works; sources only replaces the receipt when none was recorded

## CHECKS
- test_freeze_refuses_explore_without_budget · covers: M1, R:UNBOUNDED, A8 · a budgetless explore refuses at freeze, naming the missing line
- test_freeze_accepts_explore_with_budget · covers: M1, A4 · any authored budget line unlocks the normal freeze
- test_gate_refuses_open_questions_naming_them · covers: M2, R:HOLLOW_EXPLORE, A12 · an unanswered Must refuses the PASS and the refusal names it
- test_gate_requires_evidence_ref_per_finding · covers: M2, R:HOLLOW_EXPLORE, A5 · an F line without an evidence ref does not close its question
- test_gate_pass_records_sources_kind_and_tally · covers: M3, A6, E2 · a fully-answered explore passes with kind sources and the n/m tally on the stamp — one-physical-line F entries read through the T0 section parser end-to-end
- test_explore_with_run_receipt_still_gates · covers: E3 · an explore that recorded a real run receipt gates on it unchanged
- test_non_explore_freeze_and_gate_unchanged · covers: M4, R:REGRESS, A11 · a normal task freezes and gates identically, budget line or not
- test_extra_findings_are_ignored · covers: E1 · an F line answering an unfrozen question neither binds nor blocks
- test_add_py_matches_ENGINE_MD5 · covers: M5 · the add.py pin is re-aimed to the shipped bytes
- test_engine_bundle_matches_canonical · covers: M5 · the bundled tooling twin ships the same bytes
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
