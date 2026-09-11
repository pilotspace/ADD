---
type: Task
title: A refreeze that moves a gives: marks every consumer stale, and the consumer's gate holds
status: direction
depth: standard
sensitivity: architecture
milestone: loop-that-closes
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine
  - add-method/tooling/engine_pin.py
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
  - add-method/FORMAT.md
  - add-method/docs
gives:
  - S1 the freeze stamp keys `gives: <sha>` (the provider's published surface) and `needs: <target#gives=sha8,…>` (the consumer's pins) — written by `freeze`, read by `doctor`, `todo` and `gate`
  - S2 the `doctor` finding `needs_stale` (warn) and the `todo` hint on a stale consumer
  - S3 the gate refusal `R:STALENEEDS` on a rung-bound consumer, and the refreeze notice naming the consumers a moved `gives:` leaves stale
generated: { by: add/3.6.0, at: 2026-09-11 }
verified: []
---
## CARD
goal: doctor and todo emit needs_stale for each node whose needs: cites a #gives whose digest moved after that node's freeze; the consumer's gate PASS refuses R:STALENEEDS until it re-crosses; FORMAT §3.5 is written; the four 'flagged stale' sentences become true
why: intake.md, build.md, appendix-c and appendix-d all promise that a refreeze leaves dependents "flagged stale", and cite a FORMAT §3.5 that was never written; the refreeze branch writes one stamp and tells no consumer — a contract can move under a task that was verified against the old shape, and nothing in the loop reads that as anything
beat: direction · next: add freeze consumers-go-stale

## RULES
<must>
- M1 every freeze and refreeze stamp carries `gives: <sha>` — a digest over the node's canonical `gives:` list alone — and, when the node declares `needs:`, `needs: "<target>#gives=<sha8>[,…]"` pinning each `#gives` target's digest as it stood at that freeze; a `needs:` target that is not a `#gives` fragment, or that resolves to no node, is pinned as `?`
- M2 a refreeze whose `gives:` digest moved names, in its success note, every Task whose `needs:` cites this node's `#gives` — the consumers now stale — and names the fix (`add freeze <consumer>`); a refreeze that kept `gives:` byte-identical names none
- M3 `doctor` emits one `warn` finding `needs_stale` per (consumer, provider) pair whose pinned digest differs from the provider's current `gives:` digest, naming both nodes and both digests; a consumer whose latest freeze stamp carries no `needs:` key (frozen before the pin existed) yields no finding
- M4 `todo` appends `(needs stale: <provider>#gives moved — add freeze <slug>)` to a stale consumer's row at any beat
- M5 at the refute rung's arming (standard|deep × computed floor plan|human × not explore), `gate PASS` on a consumer with a stale pin refuses `R:STALENEEDS` naming the provider and the fix — re-cross: read the new fragment, then `add freeze` — and passes once the consumer refroze against the moved digest
- M6 the rung is evidence-class: `RISK-ACCEPTED` and `HARD-STOP` are never refused by it, and the provider's own gate is never touched by its consumers' state
- M7 FORMAT §3.5 exists and states the refreeze, the two stamp keys, `needs_stale`, `R:STALENEEDS` and the pre-pin silence; intake.md, build.md, appendix-c and appendix-d name `needs_stale` or `R:STALENEEDS` where they promise the flagging
</must>
<reject>
- R:STALENEEDS a rung-bound consumer gated PASS while a `#gives` it froze on has moved -> "STALENEEDS"
- R:PROVIDERBLOCKED a provider refused or delayed because of what its consumers pinned — the provider cannot know its consumers' intent -> "PROVIDERBLOCKED"
- R:CLOCKPIN staleness decided by comparing stamp dates across nodes instead of digests — two nodes' clocks are not one chronology -> "CLOCKPIN"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · stamps are written by the verb that already writes them; no new actor
- A2 [which] covers: S1 S2 S3 · the request does not say which `needs:` entries are pinned; taking ONLY `#gives` fragments — a `needs:` naming `#findings` (an explore brief) or a bare file is pinned `?` and never reported stale, because only `gives:` is a frozen contract the direction digest already seals -> cost if wrong: a task building on a re-gated explore brief is not told the brief changed · probe: a `needs: /tasks/x.md#findings` consumer yields no needs_stale after x is edited
- A3 [when] covers: S1 · the request does not say when the pin is taken; taking the consumer's OWN freeze (and every refreeze), never the provider's — the consumer pins what it read, and a pin taken at the provider's freeze would say nothing about what the consumer built on -> cost if wrong: a consumer frozen before the provider ever froze pins `?` and is never flagged, which is honest
- A4 [absent] covers: S1 S2 S3 · the request does not say what a stamp without `needs:` means; taking pre-3.7 = UNKNOWN — no finding, no refusal, and FORMAT says so; a refreeze writes the pin and turns the node into a pinned one -> cost if wrong: every consumer in every 3.6 bundle refuses at its next gate
- A5 [order] covers: S2 · the request does not say how `doctor` orders many stale pairs; taking sorted by (consumer, provider) cid so two runs over one bundle are byte-identical, as every other finding list is -> cost if wrong: a CI diff of doctor output churns
- A6 [experience] covers: S2 S3 · the request does not say who reads the finding and what would make it hard for them; the readers are the consumer's author (at `todo`, `doctor`, the gate) and the provider's author (at the refreeze note); hard for them is a finding that names a digest and not a verb — taking every surface to end in the exact next command, and the provider's note to list consumers by slug -> cost if wrong: a stale consumer is a number nobody acts on

## PLAN
contract: `gives_digest(node) -> sha` · `needs_pins(graph, node) -> str` · the two stamp keys · `stale_needs(graph, cid) -> [(provider_cid, pinned8, current8)]` read by `doctor` (`needs_stale`, warn), `todo` (hint) and `gate` (`R:STALENEEDS`, evidence-class, rung-bound) · the refreeze note lists consumers
strategy: one digest helper over `_canon` of the gives list; the pin string is scalars only so the stamp stays a flat flow-map; consumers are found by walking `edges(graph)` for key `needs` whose ref carries `#gives` — never a stored back-reference (Law 1, graph as view); the gate rung lands after the floor rung; FORMAT §3.5 is written between §3.4 and §4; the four doc sentences are rewritten to name the finding and bound by one skill check; four twins, pin re-aimed, three skill trees
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/skill/add add-method/src/add_method/_bundled/skill/add .claude/skills/add add-method/tests/skill add-method/FORMAT.md add-method/docs
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change (method.md bind)
port: `add.freeze` · `add.doctor` · `add.todo` · `add.gate` on a two-node fixture bundle

## EDGES
- E1 Given provider P frozen and consumer C (`needs: [/tasks/p.md#gives]`) frozen · When P's `gives:` changes and P refreezes · Then P's note names C and `add freeze c`
- E2 Given that state · When `doctor` · Then one `needs_stale` warn names C, P, the pinned and the current digest; `todo`'s row for C carries the hint
- E3 Given P refreezes with `gives:` unchanged · When `doctor` · Then no `needs_stale` finding and the note names no consumer
- E4 Given C rung-bound, built and refuted against the old P · When `gate c PASS` after P moved · Then R:STALENEEDS; when C refreezes, briefs, runs and refutes again · Then PASS
- E5 Given C's latest freeze stamp carries no `needs:` key · When `doctor` and `gate` · Then nothing is reported and nothing refused

## CHECKS
- test_freeze_stamp_pins_gives_and_needs · covers: M1, A2 · acceptance · both keys land; a `#findings` need pins `?`
- test_refreeze_with_moved_gives_names_consumers · covers: M2, E1, E3 · acceptance · the note lists C only when the digest moved
- test_doctor_reports_needs_stale · covers: M3, E2, E3, A5 · acceptance · one warn per pair, sorted, both digests named; none when unchanged
- test_todo_hints_the_stale_consumer · covers: M4, E2 · acceptance · the row carries the hint and the verb
- test_consumer_gate_refuses_then_passes_after_recross · covers: M5, R:STALENEEDS, E4 · acceptance · refused after the move; passes after the consumer refreezes
- test_rung_is_evidence_class_and_never_blocks_the_provider · covers: M6, R:PROVIDERBLOCKED, R:CLOCKPIN · acceptance · RISK-ACCEPTED lands; P gates PASS with stale consumers; a consumer whose stamp date is LATER than P's refreeze is still stale (digests, not dates)
- test_unpinned_freeze_reports_nothing · covers: M3, E5, A4 · acceptance · a stamp with no needs key yields no finding and no refusal
- test_format_and_docs_state_it · covers: M7 · static · FORMAT §3.5 and the four sentences name the finding or the rung
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
