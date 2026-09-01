---
type: Task
title: RISK-ACCEPTED signs for weak evidence, never for a missing seal
status: done
depth: standard
sensitivity: security
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine
gives:
  - S1 the `gate` verb under a RISK-ACCEPTED verdict — the integrity refusals it must still honour
  - S2 the `done` verb — which gate stamps entitle a close
  - S3 the `_paths_touch` predicate — when a scope entry and a pattern can name the same file
needs:
  - /tasks/sealed-gate-enforcement.md
generated: { by: add/3.2.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:2c0e615b723a34ec" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:5be869916c46e4ff" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/risk-accepted-integrity.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-01, act: refreeze, authority: human, direction: "sha256:69506b1080e819bd" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:27284dc7695f1698" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/risk-accepted-integrity.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-01, act: gate, authority: human, outcome: PASS, receipt: /tasks/risk-accepted-integrity.d/runs/2.md, brief: "sha256:27284dc7695f1698" }
advised_by: engine-notary
---
## CARD
goal: every integrity refusal in `gate` holds for RISK-ACCEPTED too; only evidence-quality refusals stay PASS-only.
why: all 16 refusals in `gate` are conditioned on `verdict == "PASS"`. Measured 2026-09-01: a task created seconds earlier, still carrying `goal: <one line>` and every template section, never frozen and never briefed, reached `done` in three calls — `add run <slug> -- true`, `add gate <slug> RISK-ACCEPTED`, `add done <slug>`. R:UNSEALED, drift, R:UNBRIEFED, the placeholder check and R:UNDECLARED_SENSITIVE all read PASS only, so the lane that is supposed to be the SCRUTINISED one is the lane with no scrutiny at all. This is 3.2's own lesson repeating: #206 found that skipping `freeze` did not FAIL the post-freeze guards, it SWITCHED THEM OFF — and closed that hole for PASS while leaving the identical hole open one verdict over.
beat: done · next: add status

## RULES
<must>
- M1 gating RISK-ACCEPTED refuses a node carrying no `freeze`/`refreeze` stamp, with the same R:UNSEALED code and remedy the PASS path already gives.
- M2 gating RISK-ACCEPTED refuses a node whose RULES/CHECKS digest differs from the one its freeze sealed — a contract changes by refreezing, under every verdict.
- M3 gating RISK-ACCEPTED refuses a node still carrying template placeholders, naming them exactly as the PASS path names them.
- M4 gating RISK-ACCEPTED refuses under R:UNDECLARED_SENSITIVE when the build changed a path matching `index.md`'s `sensitive_paths:` that no `scope:` entry covers — accepting a risk is never the way around the security floor.
- M5 The refusals that judge EVIDENCE QUALITY stay PASS-only and are named in one list in the source: a stale receipt, a non-zero command exit, an unbound `covers:` referent, a coverage gap. Signing for imperfect evidence is what the verdict is FOR.
- M6 `done` refuses a node whose entitling gate stamp is not preceded by a `freeze`/`refreeze` stamp, even when that gate is at or above the required authority.
- M7 `_paths_touch` matches on whole path SEGMENTS: `srcfoo/x` does not match `src`, and `secrets_public/x` does not match `secrets/**`.
- M8 A `sensitivity:` value that `SENSITIVITY_FLOOR` does not recognise refuses at `new` and reads as `human` at `authority_for` — an unreadable declaration is never the LOWEST floor.
</must>
<reject>
- R:HATCH a verdict other than PASS must never reach a state PASS could not reach from the same node -> "R:HATCH"
- R:SILENT_FLOOR an unrecognised `sensitivity:` must never silently degrade to `process` -> "R:SILENT_FLOOR"
- R:WIDEN no existing refusal is narrowed, and no existing test is weakened, to make this build pass -> "R:WIDEN"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the method does not say whether RISK-ACCEPTED is a WEAKER verdict or a DIFFERENT one; taking different — it signs for evidence quality at the same integrity bar as PASS -> if wrong, every RISK-ACCEPTED in flight starts refusing and the escape hatch the method intends becomes unusable · probe: a node that is frozen, briefed, unstubbed and scope-clean still records RISK-ACCEPTED with a stale receipt and a non-zero exit.
- A2 [which] covers: S1 · the request does not say which of the 16 PASS-only refusals are integrity and which are evidence; taking the split M1–M4 integrity / M5 evidence, on the test "would PASS on this node be a FABRICATED RECORD, or merely an OPTIMISTIC one?" -> if wrong, a refusal lands in the wrong tier and either blocks a legitimate acceptance or leaves a hole · probe: the source carries one named list per tier, and every `verdict == "PASS"` site is in exactly one.
- A3 [when] covers: S2 · the request does not say whether M6 applies to gates recorded before this change; taking it applies to all of them — `done` reads the stamps present, and a pre-change RISK-ACCEPTED on an unfrozen node is exactly the record this task exists to stop trusting -> if wrong, a bundle that used the hatch legitimately cannot close its task without a refreeze · probe: `done` names the freeze verb as the remedy, so the path forward is one call.
- A4 [absent] covers: S3 · the request does not say what an EMPTY `scope:` entry or an empty pattern means to `_paths_touch`; taking both as matching nothing -> if wrong an empty string matches every path and the A17 floor fires on every node · probe: `_paths_touch("", "src/**")` and `_paths_touch("src", "")` are both false.
- A5 [order] covers: S1 · the request does not say where the new refusals sit relative to the existing ones; taking integrity-before-evidence, so a never-frozen node hears R:UNSEALED and not "the receipt is stale" -> if wrong the operator is sent to fix the receipt on a node whose real problem is the missing seal · probe: an unfrozen node with a stale receipt refuses with R:UNSEALED.
- A6 [experience] covers: S1, S2, S3 · the request does not say who reads these refusals; taking an agent mid-loop that will act on the `next:` line without a human — so every new refusal names the exact verb that clears it -> if wrong the agent retries the refused call or, worse, routes around it · probe: each new refusal's message carries a `next:` naming a runnable command.
- A7 [who] covers: S2, S3 · n/a · `done` and `_paths_touch` take no actor and read no identity; authority is computed by `authority_for`, whose actor dimension A1 already covers.
- A8 [which] covers: S2 · n/a · `done` already selects gates by authority and by reopen position; this task adds a predicate, not a selection.
- A9 [when] covers: S3 · n/a · `_paths_touch` is a pure string predicate with no temporal boundary.
- A10 [absent] covers: S1, S2 · the request does not say what a node with NO `verified:` stamps at all should hear; taking the existing "no receipt recorded" and "a gate stamp (none recorded)" messages unchanged -> if wrong the first-time user meets a security refusal before they have done anything wrong · probe: a fresh scaffold gated with no receipt still hears the receipt message, not R:UNSEALED.
- A11 [order] covers: S2, S3 · n/a · `done`'s stamp ordering is already fixed by the reopen rule this task does not touch, and `_paths_touch` is order-free.
- A13 [when] covers: S1 · the request does not say whether the integrity refusals also bind HARD-STOP; taking yes for M1–M3 and moot for M4 — a HARD-STOP records a finding and never closes a task, so refusing it would only stop the finding being written down; the boundary is "does this verdict CLOSE the node" -> if wrong a security finding on an unfrozen node cannot be recorded at all · probe: gating HARD-STOP on a never-frozen node still records the stop.
- A14 [which] covers: S3 · the request does not say which separator counts as a segment boundary; taking `/` only, on POSIX-style bundle paths as `_changed_paths` already emits them -> if wrong a Windows-authored `scope:` with backslashes stops matching and the floor drops · probe: a `scope:` entry containing a backslash is left unmatched rather than silently split.
- A12 [experience] covers: S3 · n/a · `_paths_touch` is internal and prints nothing; its experience is carried by the two refusals that call it.

## PLAN
contract: `gate` grows two named tuples — the integrity refusals, which run for every verdict, and the evidence refusals, which stay PASS-only — and its `verdict == "PASS"` conditions are rewritten to read from them rather than being repeated inline. `done` gains a freeze-precedes-gate predicate. `_paths_touch` gains segment-boundary matching. `SENSITIVITY_FLOOR` lookups go through one accessor that refuses an unrecognised value at `new` and returns `human` at `authority_for`.
scope: add-method/tooling/add.py, add-method/tests/engine

## EDGES
- E1 a node frozen, then edited, then gated RISK-ACCEPTED — drift must refuse (M2) even though the verdict is not PASS.
- E2 a `refreeze` with no preceding `freeze` — M1 and M6 accept it; the seal is what matters, not which verb wrote it.
- E3 a RISK-ACCEPTED recorded before this change, on a node that WAS properly frozen — `done` must still close it (M6 is about the seal, not the change date).
- E4 `scope: src` with a changed file `srcfoo/secret.yaml` matching `sensitive_paths: ["**/secret*"]` — M7 means the scope entry no longer exempts it, so R:UNDECLARED_SENSITIVE fires.
- E5 `sensitivity: high` on an EXISTING node in a bundle written before M8 — `authority_for` reads `human`; the node is not retroactively rejected, only floored.
- E6 the security-floored refusal at add.py:3225 — already PASS-only; it must move to the integrity tier, since a security floor that a verdict can step over is not a floor.

## CHECKS
- test_risk_accepted_refuses_an_unfrozen_node · covers: M1 · gate RISK-ACCEPTED on a never-frozen node refuses with R:UNSEALED.
- test_risk_accepted_refuses_a_drifted_contract · covers: M2, E1 · RULES edited after freeze, RISK-ACCEPTED refuses.
- test_risk_accepted_refuses_template_placeholders · covers: M3 · a scaffold body is named stub-by-stub under RISK-ACCEPTED.
- test_risk_accepted_refuses_an_undeclared_sensitive_path · covers: M4, E6 · R:UNDECLARED_SENSITIVE fires under RISK-ACCEPTED.
- test_evidence_refusals_stay_pass_only · covers: M5, A1 · a clean, frozen, briefed node records RISK-ACCEPTED with a stale receipt and a non-zero exit code.
- test_every_pass_only_site_is_in_exactly_one_tier · covers: M5, A2 · each `verdict == "PASS"` site in gate() is reachable from exactly one of the two named lists.
- test_done_refuses_a_gate_that_no_freeze_precedes · covers: M6, A3 · the three-call walk to done is refused, and the message names the freeze verb.
- test_done_still_closes_a_properly_frozen_risk_accepted · covers: M6, E3 · the legitimate hatch still closes.
- test_refreeze_alone_satisfies_the_seal · covers: E2 · a lone refreeze stamp entitles gate and done.
- test_paths_touch_matches_whole_segments · covers: M7, E4 · srcfoo/x vs src and secrets_public/x vs secrets/** are both false; src/x vs src stays true.
- test_paths_touch_empty_matches_nothing · covers: M7, A4 · an empty entry and an empty pattern each match nothing.
- test_paths_touch_leaves_a_backslash_entry_unmatched · covers: A14 · `/` is the only segment separator.
- test_hard_stop_is_still_recordable_on_an_unfrozen_node · covers: A13 · refusing a HARD-STOP would only lose the finding.
- test_new_refuses_an_unrecognised_sensitivity · covers: M8, R:SILENT_FLOOR · new Task with `--sensitivity high` refuses and lists the recognised values.
- test_authority_for_reads_an_unknown_sensitivity_as_human · covers: M8, E5 · an existing node declaring `high` floors at human, not process.
- test_integrity_refusals_precede_evidence_refusals · covers: A5 · an unfrozen node with a stale receipt hears R:UNSEALED.
- test_every_new_refusal_names_a_next_verb · covers: A6 · each new refusal message carries a runnable `next:`.
- test_a_receiptless_gate_still_hears_the_receipt_message · covers: A10 · the first-call experience is unchanged.
- test_no_existing_refusal_was_narrowed · covers: R:WIDEN · the incumbent gate/done suite passes unchanged.
- test_risk_accepted_reaches_no_state_pass_could_not · covers: R:HATCH · for a fixed node, the set of refusals under RISK-ACCEPTED is a subset of those under PASS.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- A guard written for one verdict is a guard for one verdict; when a refusal protects the RECORD rather than the EVIDENCE, condition it on the node, never on the verdict -> add learn add
