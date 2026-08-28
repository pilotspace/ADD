---
type: Task
title: A node that was never authored is never advised to freeze
status: direction
depth: standard
sensitivity: high
milestone: affordance-truth
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine
  - add-method/tooling
  - add-method/src/add_method/_bundled/tooling
  - add-method/.add/tooling
  - add-method/conftest.py
  - add-method/tests/skill
gives:
  - S1 `BEAT_NEXT` in `add-method/tooling/add.py` — the beat→verb map, gaining the scaffold state it cannot express today
  - S2 `add status`'s frontier `next:` line
  - S3 `add todo`'s per-open-task arrow line, which names the next verb
  - S4 `add new`'s returned `next:` line
  - S5 the `beat: … · next: …` line `BODIES["Task"]` writes into every new node's `## CARD`
generated: { by: add/3.2.0, at: 2026-08-17 }
verified:
  - { by: "Tin Dang", at: 2026-08-17, act: freeze, authority: human, direction: "sha256:41b3ac4db4d97b63" }
  - { by: "Claude (owner-delegated, Tin Dang 2026-08-17)", at: 2026-08-17, act: replan, authority: process, note: "A5's taken reading is FALSIFIED, found minutes after the freeze by the freeze itself. A5 took 'write-time correction for new, plus the existing card_drift repair thereafter'. card_drift cannot repair this: it compares the CARD's beat token against the RAW frontmatter status: field (add.py:1534, said != status), and freeze does not move status: — the beat is DERIVED from _is_frozen. So both nodes frozen today read 'beat: direction · next: add freeze <slug>' in their own CARD while todo and status derive 'build', and add doctor reports them CLEAN. A freshly frozen node advertises the verb it has already passed, and the drift detector calls it current. This is the SAME root cause a fourth time — two notions of beat, one raw and one derived, with different surfaces reading different ones — so it belongs to S5, which this task already declares. Scope consequence: the corrected derivation must be what card_drift compares against, not status:, and test_new_card_line_names_authoring gains a sibling proving a frozen node's CARD names brief. RULES and CHECKS were NOT edited; this records the amendment against the seal rather than reopening it." }
---
## CARD
goal: Make every surface that derives a `next:` for an unauthored node name the authoring work instead of `add freeze`, using the same predicate the refusals already use.
why: `direction.md` states the design — "There is no author verb — you fill those sections by editing that
  file directly" — and no affordance in the engine knows it. `BEAT_NEXT["direction"]` maps the whole beat
  to `add freeze {slug}`, so five surfaces recommend a verb that `add.py:1260` is guaranteed to refuse. The
  cost is not the wasted call; it is that a scaffold and a finished contract are indistinguishable from
  `status`, so a node can sit unauthored for days inside a milestone that reads as in-progress.
beat: direction · next: add freeze authoring-beat-named

## RULES
<must>
- M1 No surface that derives a `next:` recommends `freeze` for a node that `freeze` would refuse. Proven by DRIVING each of S1–S5 against a real scaffold node, not by reading the source or grepping for a string.
- M2 The advice-time predicate is the refusal-time predicate — `placeholders_in` (and `gives_unauthored`) CALLED, never re-implemented. The engine ends this task with exactly one notion of "authored".
- M3 The corrected advice names the authoring work and the verb that follows it, matching the sentence `freeze`'s refusal already produces (`author <slug>'s RULES, ASSUMPTIONS and CHECKS, then add freeze <slug>`), so meeting it early and meeting it late read as one instruction rather than two.
- M4 A node carrying a freeze stamp is untouched: its `brief` · `run` · `gate` · `done` affordances are byte-identical before and after.
- M5 All four live engine twins carry the change — `add-method/tooling/`, `add-method/src/add_method/_bundled/tooling/`, `add-method/.add/tooling/`, and this bundle's `.add/tooling/` — and the `ENGINE_MD5` / `ENGINE_PKG_MD5` pins are re-aimed. Both test roots (`add-method/tests/` and `add-method/tooling/`) are green.
- M6 `tests/engine/test_new_scaffold.py`'s pinned affordance assertion is RE-AIMED at the corrected string, not deleted. The scaffold's `next:` stays a pinned interface; it is the value that was wrong, not the pinning.
- M7 `freeze` REFUSES a Milestone whose CARD, SCOPE, GROUND or EXIT are still template. Today it accepts one and records the stamp — measured, not inferred: `add new Milestone probe-ms` followed by `add freeze probe-ms` returns `freeze recorded at authority process` with `goal: <one line>` untouched. `placeholders_in` reads only RULES · ASSUMPTIONS · CHECKS (add.py:2270), and a Milestone body has none of those sections, so the guard is Task-only by construction and silently vacuous on the other lifecycle type.
</must>
<reject>
- R:SECOND_TRUTH Introducing a new predicate, flag or frontmatter field meaning "authored" alongside the one the refusals use. Two notions is how advice and refusal come to disagree, which is the defect one layer up. -> "SECOND_TRUTH"
- R:NEW_VERB Adding an `add draft` / `add author` verb. `direction.md` rules against it deliberately — the engine records, it never writes the method for you. This task changes what the engine SAYS. -> "NEW_VERB"
- R:GREEN_BY_SOURCE Closing M1 with a test that greps `add.py` for the new string. That proves the string exists, not that any surface emits it — the exact shape of check that let the current defect ship. -> "GREEN_BY_SOURCE"
- R:STATUS_ENUM Changing the `status:` frontmatter vocabulary. The beat is DERIVED, exactly as `_is_frozen` derives the next one; a new enum value ripples into every bundle in the wild and into `add upgrade`. -> "STATUS_ENUM"
- R:ONE_TREE Shipping the edit in fewer than all four live twins, or leaving an MD5 pin aimed at the old engine. -> "ONE_TREE"
- R:VACUOUS_GUARD Extending the Milestone guard by naming section headings that a Milestone body does not contain, or by any construction that returns clean because it looked in the wrong place. The guard must be proven against a real scaffold that it REFUSES, never against a fixture that merely fails to trip it. -> "VACUOUS_GUARD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3, S4, S5 · the request does not say WHO the affordance addresses — a human reading a terminal, or an agent pattern-matching `next: add <verb>`; taking BOTH, so the new text must instruct a human AND leave an agent a resolvable cue -> if wrong, an agent that matches on a leading `add ` loses its cue entirely and stalls where today it at least attempts freeze and reads a useful refusal · probe: the emitted line carries a runnable `add …` continuation, not prose alone
- A2 [which] covers: S1, S2 · the request does not say WHICH node types get the corrected advice — Tasks only, or Milestones too; taking BOTH lifecycle types, since `v3-final-collateral` in this bundle is the Milestone instance of the same defect -> if wrong, milestones keep the old advice and the bundle that proved the bug goes on reproducing it · probe: an unauthored Milestone is advised to author, not to freeze
- A3 [which] covers: S3, S4, S5 · the request does not say WHICH placeholders count as unauthored — any `<…>` in the body, or only what `freeze` refuses on; taking exactly `placeholders_in`'s answer -> if wrong the engine grows a second definition and a node the advice calls ready is refused by freeze · probe: the advice predicate and the freeze predicate are the same call
- A4 [when] covers: S1, S2, S3 · the request does not say WHEN the beat flips from scaffold to authored — on the first real edit, or only when every placeholder is gone; taking all-gone, matching freeze exactly -> if wrong a half-authored node is advised to freeze and refused, which is today's defect with a smaller window · probe: a node with one remaining placeholder still reads unauthored
- A5 [when] covers: S4, S5 · the request does not say WHEN the CARD's baked `next:` is corrected — at write time only, or re-derived on every read; taking write-time for `new` plus the existing `card_drift` repair thereafter, since the CARD line is a static string by design -> if wrong the CARD contradicts `status` for any node whose beat moved without a `doctor --sync` run · probe: `card_drift` reports a CARD whose next disagrees with the derived beat
- A6 [absent] covers: S1 · the request does not say what an ABSENT beat key means in `BEAT_NEXT`; taking the existing `.get(beat, "add status")` fallback unchanged -> if wrong an unrecognised beat raises instead of degrading to a safe default, turning a cosmetic gap into a crashed `status` · probe: an unknown beat still resolves to `add status`
- A7 [absent] covers: S2, S3 · the request does not say what an unreadable or unparseable node BODY means at advice time; taking "cannot read -> advise authoring", the conservative direction -> if wrong a node whose body failed to parse is advised to freeze, and the refusal is the first its author hears of it · probe: a node whose body cannot be read is never advised to freeze
- A8 [absent] covers: S4, S5 · the request does not say whether an absent `gives:` is a separate condition from template RULES; taking `gives_unauthored` as one more scaffold signal, since `todo` already reports it and `freeze` already refuses on it -> if wrong a node with authored RULES but template `gives:` is advised to freeze and refused on the surface sweep · probe: authored RULES plus template `gives:` still reads unauthored
- A9 [order] covers: S1, S2, S3, S4, S5 · the request does not say what ORDER the states resolve in when a node is both placeholder-carrying and frozen; taking frozen-wins, since the current guard makes that combination reachable only from a pre-3.0 bundle -> if wrong an upgraded legacy bundle is dragged backwards into authoring advice on nodes it already approved · probe: a node carrying a freeze stamp is never advised to author
- A10 [order] covers: S2, S3 · the request does not say which node the frontier picks when several are unauthored; taking `ready()`'s existing order, unchanged -> if wrong this task silently re-orders every user's worklist, a change nobody asked for and nobody would attribute to it · probe: frontier ordering is identical before and after
- A11 [experience] covers: S2, S3 · the request does not say who reads `status` and `todo`; taking the agent resuming a session cold as the reader — it reads `next:` and acts, having read nothing else -> if wrong the resumed agent runs freeze, reads a refusal, and spends a turn rediscovering what `status` could have said in the first line it printed · probe: the cold-resume path reaches authoring without first running a verb that refuses
- A12 [experience] covers: S1, S4, S5 · the request does not say what the CARD line owes someone who opens the file directly rather than running a command; taking "the file must state its own next step unaided", since a scaffold is most often met by opening it -> if wrong the file's own card sends its reader to the refusal · probe: a freshly created node's CARD names authoring
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: A derived third direction state. `_beat_of` gains a `scaffold` reading between "created" and
  "frozen", computed from `placeholders_in` + `gives_unauthored` — the same calls the refusals make, not a
  copy. `BEAT_NEXT` gains the matching entry. `status` (:1777), `todo`, `new` (:1242) and `BODIES["Task"]`
  (:1092) all resolve through it, so one map stays the single source. `_is_frozen` is consulted FIRST so a
  stamped node is never re-read as scaffold. No verb is added; no `status:` value changes; every refusal
  message stays exactly as it is.
scope: add-method/tooling/add.py · add-method/tests/engine · add-method/tooling ·
  add-method/src/add_method/_bundled/tooling · add-method/.add/tooling · add-method/conftest.py ·
  add-method/tests/skill
strategy (preferred): land the derivation + `BEAT_NEXT` entry first with S2 red-first against a real
  scaffold; then the remaining four surfaces one at a time, each red before green; then re-aim
  `test_new_scaffold.py`; then mirror the twins and re-aim the MD5 pins in one commit, since a partial
  mirror is the failure mode `test_tree_parity` catches late.
regression floor: both test roots green — `add-method/tests/` and `add-method/tooling/`.

## EDGES
- E1 Authored RULES with a still-template `gives:` — `placeholders_in` says authored, `gives_unauthored` says not. The two predicates disagree, and freeze refuses on the second.
- E2 A node carrying BOTH a freeze stamp and placeholders — reachable only from a pre-3.0 bundle, since the 3.0 guard forbids creating it.
- E3 An empty frontier: no open task at all. `status` must keep emitting its existing `add new task <slug>` / `add new milestone <slug>` affordance untouched.
- E4 A Milestone scaffold. `placeholders_in` reads only RULES · ASSUMPTIONS · CHECKS (add.py:2270) and scans only lines beginning `- ` (:2272); a Milestone body has none of those three sections, so the predicate returns `[]` for ANY milestone and `freeze` stamps it approved — measured on a scratch bundle, not inferred. The `why:` gap surfaces only at `milestone-done` (:1409), which is the far end of the milestone. This is the M7 case and the reason `v3-final-collateral` has read as a live milestone since 2026-08-11.
- E5 The `quick` one-call lane (add.py:2970-2978) rewrites the body to `beat: build · next: add run` and freezes inside the same call. It must be untouched — a scaffold detector that fired on its `<cmd>` / `<PASS>` slots would make the one-call lane unclosable by construction.

## CHECKS
- test_status_advises_authoring_for_a_scaffold_task · covers: M1, R:GREEN_BY_SOURCE · drives `status` against a real unauthored task node; the `next:` line names authoring and contains no `add freeze`
- test_todo_advises_authoring_for_a_scaffold_task · covers: M1, R:GREEN_BY_SOURCE · drives `todo`; the per-node arrow no longer contradicts its own `(gives: unauthored)` annotation
- test_new_returns_authoring_advice · covers: M1, R:GREEN_BY_SOURCE · the message `new` returns for a freshly written Task names authoring
- test_new_card_line_names_authoring · covers: M1, M6 · the `beat:` line inside the created FILE names authoring, read back from disk
- test_status_advises_authoring_for_a_scaffold_milestone · covers: M1, A2 · the Milestone path gets the same treatment as the Task path
- test_advice_and_freeze_agree_over_a_fixture_table · covers: M2, A3, R:SECOND_TRUTH · for every fixture, "advised to freeze" and "freeze accepts" are the same boolean — no node is advised toward a refusal and none is advised away from a stamp it would earn
- test_authoring_advice_matches_the_freeze_refusal_sentence · covers: M3, A1 · the advice string and the refusal's `next:` are the same instruction, and it carries a runnable `add …` continuation
- test_frozen_node_affordances_are_unchanged · covers: M4, A9 · a stamped node's `brief`/`run`/`gate`/`done` affordances are byte-identical to the pre-change engine
- test_unknown_beat_still_falls_back_to_status · covers: A6 · an unrecognised beat resolves to `add status` rather than raising
- test_unreadable_body_advises_authoring · covers: A7 · the conservative direction, driven with a body that fails to parse
- test_authored_rules_with_template_gives_reads_unauthored · covers: E1, A8 · the two predicates are combined, not chosen between
- test_freeze_stamp_wins_over_placeholders · covers: E2, A9 · a pre-3.0 stamped node is not dragged back to authoring
- test_empty_frontier_affordance_is_unchanged · covers: E3, M4 · the no-open-task path is untouched
- test_freeze_refuses_a_pure_milestone_scaffold · covers: M7, E4 · `add new Milestone` then `add freeze` — refused, naming the template sections; red against today's engine, which records the stamp
- test_milestone_guard_names_sections_the_body_actually_has · covers: R:VACUOUS_GUARD · the guard is driven against a scaffold it must refuse AND an authored milestone it must accept, so a guard looking in an absent section fails the first half rather than passing both
- test_quick_lane_is_unaffected · covers: E5, R:NEW_VERB · the one-call lane still opens, runs and gates in one call
- test_frontier_order_is_unchanged · covers: A10 · `ready()` ordering is identical before and after
- test_new_scaffold_pins_the_corrected_affordance · covers: M6 · the re-aimed assertion, still pinning a literal string
- test_no_new_verb_in_the_cli_surface · covers: R:NEW_VERB · the verb list is unchanged at 22
- test_status_frontmatter_vocabulary_is_unchanged · covers: R:STATUS_ENUM · no new `status:` value is written or accepted
- test_tree_parity · covers: M5, R:ONE_TREE · all four twins byte-identical and the MD5 pins re-aimed (existing check, extended to this change)
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
