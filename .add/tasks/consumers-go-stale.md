---
type: Task
title: A refreeze that moves a gives: marks every consumer stale, and the consumer's gate holds
status: done
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
verified:
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: freeze, authority: plan, direction: "sha256:45972331994270bd", binding: "sha256:bd1235c2e1600e93" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:862d5cc6dc38908c" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/1.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/2.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 3, receipt: /tasks/consumers-go-stale.d/runs/1.md, tier: T2, note: "one consumer with needs: [/tasks/q.md#gives, /tasks/p.md#gives] and BOTH providers moved — doctor emits needs_stale in written order ['/tasks/q.md', '/tasks/p.md'], not sorted by (consumer, provider) cid as A5 states" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:9bdd5c808e1430c9", binding: "sha256:69e14c1306e71f45", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:dbbdbe572f3431fa" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/3.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/4.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 3, receipt: /tasks/consumers-go-stale.d/runs/3.md, tier: T2, note: "one consumer with needs: [/tasks/p.md#gives, /tasks/p.md#gives] and p's gives moved — doctor emits TWO needs_stale warns for the one (c, p) pair, todo doubles the hint, the gate names /tasks/p.md#gives twice; stale_needs sorts but never dedupes (M3: one per pair)" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:79df0bc5c48e5027", binding: "sha256:bbab0c662dde5a9e", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:ae7062d8f5aae396" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/5.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/6.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 3, receipt: /tasks/consumers-go-stale.d/runs/5.md, tier: T2, note: "one consumer with needs: [/tasks/p.md#gives, p.md#gives] — two spellings _norm resolves to one target — freezes with the pin '/tasks/p.md#gives=…,p.md#gives=…': the provider is pinned twice (E7; M1 pins each target); needs_pins dedupes on the written ref, not the resolved target, and only set() downstream hides it" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:6e7ff4477539b878", binding: "sha256:493b1b4787770d3c", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:25c8b5fca14772ee" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/7.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/8.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/9.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/10.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 3, receipt: /tasks/consumers-go-stale.d/runs/9.md, tier: T2, note: "consumer c (needs: [/tasks/p.md#gives]) frozen while p is authored but NEVER frozen — the stamp pins /tasks/p.md#gives=d54762d1 (p's draft digest), not '?' as A3 states, and p's FIRST freeze then flags c needs_stale and refuses R:STALENEEDS; root: needs_pins/stale_needs/the refreeze note read the LIVE gives: list, never the provider's stamped gives: key S1 says doctor/todo/gate read — same root flags and refuses c on a silent edit of p's gives with no refreeze, and a v1→v2→v1 round trip names c 'now stale' while stale_needs(c)==[]" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:d6aeb2991906b67d", binding: "sha256:c18baf8c208200d5", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:bc0e8902ae10555b" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/11.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/12.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 9, receipt: /tasks/consumers-go-stale.d/runs/11.md, tier: T2, note: "consumer d with needs: [/tasks/p.md#gives=deadbeef] freezes pinning '/tasks/p.md#gives=deadbeef=?' (M1's ?), but _pins_of partitions on the FIRST '=' and reads ('/tasks/p.md': 'deadbeef=?') -> doctor needs_stale, todo hint and gate R:STALENEEDS with nothing moved (A2: never reported; M3: no attested digest differs); same root: needs: '/tasks/p.md#gives, /tasks/q.md#gives' (scalar, edges() resolves to p) pins q at p's digest and never pins p — the pin string is ','/'='-delimited with no escaping" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:a661f2b5e0dfae8e", binding: "sha256:87d58f15e4a47829", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:9a1214874d750c0c" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/13.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/14.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 7, receipt: /tasks/consumers-go-stale.d/runs/13.md, tier: T2, note: "consumer d with needs: [/tasks/p.md#findings, /tasks/p.md#gives] freezes pinning ONLY '/tasks/p.md#findings=?' — the #gives need is dropped from the stamp (M1: each #gives target pinned; A2: only the #findings ref is '?'); when p's gives moves the refreeze note, doctor and todo name c but never d, and gate d PASS lands (M2/M3/M5); root: needs_pins dedupes on _norm's node cid, which strips the fragment, so E8's first-spelling rule collapses #findings and #gives (and E13's '?' spelling written before an honest #gives ref) into one key — the unit must be (resolved node, fragment)" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:35dc0ed57138a6ed", binding: "sha256:fcef5eaa5fe995fd", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:ae1ef1a36c2b7462" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/15.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/16.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 5, receipt: /tasks/consumers-go-stale.d/runs/15.md, tier: T2, note: "consumer d with needs: [/tasks/p.md#gives=deadbeef,/tasks/q.md#gives=cafebabe] (or just [/tasks/p.md#gives=deadbeef,]) freezes pinning '...=?' per E13, but _pins_of splits on ',' BEFORE rpartition('=') and reads (/tasks/p.md: deadbeef) -> doctor needs_stale, todo hint and gate R:STALENEEDS (deadbeef -> d54762d1) with nothing moved — M1/E13 'reader recovers every ? whatever the ref's text' and A2 'never reported stale' fail; root: the reader tokenises on the outer delimiter the writer never escaped" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:ad0142262193452b", binding: "sha256:4a0c2afb6e5f3c0d", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:fa4457f78392c2f6" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/17.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/18.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 5, receipt: /tasks/consumers-go-stale.d/runs/17.md, tier: T2, note: "consumer d with needs: ['/tasks/x'.md#gives', '/tasks/p.md#gives'] freezes writing needs: '/tasks/x'.md#gives=?,/tasks/p.md#gives=d54762d1' — _split_commas flips on the inner quote and the honest p pin is dropped on read (_pins_of == ()), so p's move names c but never d in the note, doctor, todo or gate (M1/M2/M3/M5); same root with '(' in a ref: _block's quote-blind brace count merges the brief stamp INTO the freeze stamp (act reads brief, stamped_gives(d) None — the seal vanishes); needs_pins strips the PIN's delimiters (,=) but bypasses _oneline, so the STAMP's own delimiters ride raw into the flow map" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:e58b3b8cf13fd8b8", binding: "sha256:aa9c8a448ade3f09", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:b1f20a6b6e348b95" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/19.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/20.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 6, receipt: /tasks/consumers-go-stale.d/runs/19.md, tier: T2, note: "consumer c frozen pinning /tasks/p.md#gives, then its frontmatter needs: deleted by hand with no refreeze (unsealed: direction_digest unchanged), then p moves — the refreeze note names NO consumer (consumers_of walks live needs: edges) while doctor warns needs_stale on c, todo hints c and gate c PASS refuses R:STALENEEDS d54762d1->88397781 (all three read the stamp's pin): M2's 'exactly the consumers now stale, by the same comparison M3 makes' fails whenever the live needs: list and the latest stamp's needs: key disagree; root: consumers_of is the one pin reader not sourced from the stamp" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:3049f2973a593058", binding: "sha256:5e521bab3e82ee3c", gives: "sha256:58710af7bbb42cab" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:590530bbb5e19455" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/21.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/22.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: held, probes: 11, receipt: /tasks/consumers-go-stale.d/runs/21.md, tier: T2, changed: "nine T2 reads moved the pin's unit to (STAMPED digest, resolved node, fragment), sourced every reader from the stamp and made the pin string round-trip under the serializer's whole alphabet (E6–E18)" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: gate, authority: plan, outcome: PASS, receipt: /tasks/consumers-go-stale.d/runs/21.md, brief: "sha256:38623bf39be907ca" }
---
## CARD
goal: doctor and todo emit needs_stale for each node whose needs: cites a #gives whose digest moved after that node's freeze; the consumer's gate PASS refuses R:STALENEEDS until it re-crosses; FORMAT §3.5 is written; the four 'flagged stale' sentences become true
why: intake.md, build.md, appendix-c and appendix-d all promise that a refreeze leaves dependents "flagged stale", and cite a FORMAT §3.5 that was never written; the refreeze branch writes one stamp and tells no consumer — a contract can move under a task that was verified against the old shape, and nothing in the loop reads that as anything
beat: done · next: add status

## RULES
<must>
- M1 every freeze and refreeze stamp carries `gives: <sha>` — a digest over the node's canonical `gives:` list alone — and, when the node declares `needs:`, `needs: "<target>#gives=<sha8>[,…]"` pinning each `#gives` target's digest AS ITS LATEST FREEZE STAMP ATTESTS IT — never the live list; a `needs:` target that is not a `#gives` fragment, that resolves to no node, or whose node carries no freeze stamp with `gives:`, or whose written text carries a pin or stamp delimiter (`,` `=` `"` `'` `{` `}` `[` `]` or whitespace) and so cannot be serialized, is pinned as `?` under its text with those characters STRIPPED — the stamp string never carries an inner delimiter — and the reader accepts only exact `<ref>=<sha8|?>` tokens, so it recovers every `?` the writer wrote, whatever the ref's text
- M2 a refreeze whose `gives:` digest moved names, in its success note, every OPEN Task (not `done`, `dropped` or `archived`) whose `needs:` pins this node's `#gives` at a digest other than the one just stamped — exactly the consumers now stale, by the same comparison M3 makes — and names the fix (`add freeze <consumer>`); a refreeze that kept `gives:` byte-identical, or that no open consumer's pin differs from, names none
- M3 `doctor` emits one `warn` finding `needs_stale` per (open consumer, provider) pair — the unit is the RESOLVED target, so two spellings of one provider are one pair — whose pinned digest differs from the provider's STAMPED `gives:` digest (its latest freeze or refreeze stamp — a silent edit of the live list moves nothing), naming both nodes and both digests; a consumer whose latest freeze stamp carries no `needs:` key (frozen before the pin existed) yields no finding
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
- A3 [when] covers: S1 S2 S3 · the request does not say when the pin is taken; taking the consumer's OWN freeze (and every refreeze), never the provider's — the consumer pins what it read, and a pin taken at the provider's freeze would say nothing about what the consumer built on; what it reads is the provider's STAMPED digest, so a consumer frozen before the provider ever froze pins `?` and is never flagged, which is honest -> cost if wrong: a provider frozen pre-3.7 (stamp without `gives:`) reads as `?` to its consumers until its next refreeze — the pre-pin silence A4 grants, applied symmetrically · probe: freeze c against an unfrozen p, then freeze p — c's pin is `?` and doctor is silent
- A4 [absent] covers: S1 S2 S3 · the request does not say what a stamp without `needs:` means; taking pre-3.7 = UNKNOWN — no finding, no refusal, and FORMAT says so; a refreeze writes the pin and turns the node into a pinned one -> cost if wrong: every consumer in every 3.6 bundle refuses at its next gate
- A5 [order] covers: S1 S2 S3 · the request does not say how `doctor` orders many stale pairs; taking sorted by (consumer, provider) cid so two runs over one bundle are byte-identical, as every other finding list is -> cost if wrong: a CI diff of doctor output churns
- A6 [experience] covers: S1 S2 S3 · the request does not say who reads the finding and what would make it hard for them; the readers are the consumer's author (at `todo`, `doctor`, the gate) and the provider's author (at the refreeze note); hard for them is a finding that names a digest and not a verb — taking every surface to end in the exact next command, and the provider's note to list consumers by slug -> cost if wrong: a stale consumer is a number nobody acts on

## PLAN
contract: `gives_digest(node) -> sha` · `needs_pins(graph, node) -> str` · the two stamp keys · `stale_needs(graph, cid) -> [(provider_cid, pinned8, current8)]` read by `doctor` (`needs_stale`, warn), `todo` (hint) and `gate` (`R:STALENEEDS`, evidence-class, rung-bound) · the refreeze note lists consumers
strategy: one digest helper over `_canon` of the gives list; the pin string is scalars only so the stamp stays a flat flow-map; consumers are found by walking every open Task's latest freeze stamp for a pin on this node — the one source every reader shares — never the live `needs:` list (unsealed, a draft until a freeze pins it) and never a stored back-reference (Law 1, graph as view); the gate rung lands after the floor rung; FORMAT §3.5 is written between §3.4 and §4; the four doc sentences are rewritten to name the finding and bound by one skill check; four twins, pin re-aimed, three skill trees
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/skill/add add-method/src/add_method/_bundled/skill/add .claude/skills/add add-method/tests/skill add-method/FORMAT.md add-method/docs
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change (method.md bind)
port: `add.freeze` · `add.doctor` · `add.todo` · `add.gate` on a two-node fixture bundle

## EDGES
- E1 Given provider P frozen and consumer C (`needs: [/tasks/p.md#gives]`) frozen · When P's `gives:` changes and P refreezes · Then P's note names C and `add freeze c`
- E2 Given that state · When `doctor` · Then one `needs_stale` warn names C, P, the pinned and the current digest; `todo`'s row for C carries the hint
- E3 Given P refreezes with `gives:` unchanged · When `doctor` · Then no `needs_stale` finding and the note names no consumer
- E4 Given C rung-bound, built and refuted against the old P · When `gate c PASS` after P moved · Then R:STALENEEDS; when C refreezes, briefs, runs and refutes again · Then PASS
- E5 Given C's latest freeze stamp carries no `needs:` key · When `doctor` and `gate` · Then nothing is reported and nothing refused
- E6 Given one consumer whose `needs:` lists two providers in reverse cid order and both moved · When `doctor` and `gate` · Then the findings and the refusal name the providers in cid order — the pin's written order decides nothing (found by the T2 refute)
- E7 Given a consumer whose `needs:` names the same provider twice · When it freezes and the provider moves · Then the pin carries the provider once, `doctor` emits ONE warn, `todo` one hint, and the refusal names it once — the unit is the pair, decided at the source (found by the second T2 refute)
- E8 Given a consumer whose `needs:` names one provider under two spellings (`/tasks/p.md#gives` and `p.md#gives`) · When it freezes · Then the pin carries that provider ONCE, under the first spelling written — the writer dedupes by resolved target, not by text (found by the third T2 refute)
- E10 Given consumer C frozen while provider P is authored but NOT yet frozen · When P freezes for the first time · Then C's pin reads `/tasks/p.md#gives=?`, `doctor` is silent and `gate c PASS` is not refused for it — the pin's unit is the provider's stamped digest (found by the fourth T2 refute)
- E11 Given P and C both frozen · When P's `gives:` is edited in the file with NO refreeze · Then `doctor`, `todo` and `gate` say nothing about C — the live list moves no pin; a silent edit is P's own tamper problem (found by the fourth T2 refute)
- E12 Given P moved v1→v2 and C never re-crossed · When P refreezes back to v1 · Then the note names no consumer and `doctor` is silent — the note is the M3 comparison, never a `prev != new` proxy (found by the fourth T2 refute)
- E13 Given a consumer whose `needs:` ref carries a pin delimiter — `/tasks/p.md#gives=deadbeef` (pasted stamp text) or a comma-joined scalar `/tasks/p.md#gives, /tasks/q.md#gives` · When it freezes and nothing moves · Then the pin is `?`, `doctor`, `todo` and `gate` say nothing, and `_pins_of(needs_pins(...))` round-trips for every ref text — the writer's `?` is never misread as a digest (found by the fifth T2 refute)
- E14 Given a consumer whose `needs:` names one provider under two FRAGMENTS (`/tasks/p.md#findings` then `/tasks/p.md#gives`), or a delimiter-carrying spelling before an honest one (`/tasks/p.md#gives=deadbeef` then `/tasks/p.md#gives`) · When it freezes and the provider moves · Then the `#gives` pin is written at the stamped digest whatever the written order, and the note, `doctor`, `todo` and the gate treat the consumer as stale — the pin's unit is (resolved node, fragment); E8's first-spelling rule dedupes only true spellings of ONE fragment (found by the sixth T2 refute)
- E15 Given a provider whose `gives:` is written as a scalar string · When it freezes · Then its `gives:` digest equals the digest of the same text as a one-item list — a scalar is one surface, never a string of characters (the sixth read's concern, ruled here)
- E16 Given a consumer whose one `needs:` item carries BOTH delimiters — a whole pasted stamp value `/tasks/p.md#gives=deadbeef,/tasks/q.md#gives=cafebabe`, or a trailing comma `/tasks/p.md#gives=deadbeef,` — · When it freezes and nothing moves · Then the stamp's `needs:` string carries no delimiter inside any token, `_pins_of` reads `{}`, and `doctor`, `todo` and the gate say nothing; and for every ref text built from `,`, `=`, `#gives` and a resolvable path, `_pins_of(needs_pins(...))` names exactly the honest `#gives` refs at the stamped digest (found by the seventh T2 refute)
- E17 Given a consumer whose `needs:` carries a ref with the STAMP line's own delimiter (`/tasks/x".md#gives` or `/tasks/{p.md#gives`) beside an honest `/tasks/p.md#gives` · When it freezes, briefs, and the provider moves · Then the honest pin survives the round trip through the flow map, the brief stamp is still its own item, `stamped_gives` still reads the freeze, and the note, `doctor`, `todo` and the gate treat the consumer as stale; the E16 property holds over every character of the serializer's alphabet (found by the eighth T2 refute: the pin bypassed the discipline every interpolated value takes)
- E18 Given C frozen pinning P, then C's frontmatter `needs:` deleted (or retargeted to Q) by hand with no refreeze — an unsealed edit · When P moves · Then the refreeze note names C exactly as `doctor`, `todo` and the gate do — every reader sources the consumer set from the stamp's pin, never the live list; `add freeze c` then clears all four at once (found by the ninth T2 refute)
- E9 Given a consumer already `done` (or dropped) · When its provider moves · Then the refreeze note, `doctor` and `todo` say nothing about it — `add freeze` is not a verb a closed task can take (the third read's spec silence, ruled here)

## CHECKS
- test_freeze_stamp_pins_gives_and_needs · covers: M1, A2 · acceptance · both keys land; a `#findings` need pins `?`
- test_refreeze_with_moved_gives_names_consumers · covers: M2, E1, E3 · acceptance · the note lists C only when the digest moved
- test_doctor_reports_needs_stale · covers: M3, E2, E3, A5 · acceptance · one warn per pair, sorted, both digests named; none when unchanged
- test_todo_hints_the_stale_consumer · covers: M4, E2 · acceptance · the row carries the hint and the verb
- test_consumer_gate_refuses_then_passes_after_recross · covers: M5, R:STALENEEDS, E4 · acceptance · refused after the move; passes after the consumer refreezes
- test_rung_is_evidence_class_and_never_blocks_the_provider · covers: M6, R:PROVIDERBLOCKED, R:CLOCKPIN · acceptance · RISK-ACCEPTED lands; P gates PASS with stale consumers; a consumer whose stamp date is LATER than P's refreeze is still stale (digests, not dates)
- test_unpinned_freeze_reports_nothing · covers: M3, E5, A4 · acceptance · a stamp with no needs key yields no finding and no refusal
- test_format_and_docs_state_it · covers: M7 · static · FORMAT §3.5 and the four sentences name the finding or the rung
- test_two_moved_providers_report_in_cid_order · covers: E6, A5 · acceptance · a reversed two-provider pin reports and refuses in (consumer, provider) cid order
- test_duplicate_need_is_one_pair · covers: E7, M3 · acceptance · a provider named twice in needs: pins once, warns once, hints once, is refused once
- test_two_spellings_pin_one_target · covers: E8, M1 · acceptance · the stamp's pin names the provider once under its first spelling
- test_closed_consumers_are_not_told_to_refreeze · covers: E9, M2, M3 · acceptance · a done and a dropped consumer draw no note, no warn, no hint
- test_unfrozen_provider_pins_unknown · covers: E10, A3, M1 · acceptance · a consumer frozen before its provider pins `?`; the provider's first freeze flags nothing
- test_silent_edit_moves_no_pin · covers: E11, M3 · acceptance · a gives: edit without a refreeze draws no warn, no hint, no refusal
- test_round_trip_names_no_consumer · covers: E12, M2 · acceptance · v1→v2→v1 leaves the pin current and the note silent
- test_pin_round_trips_through_delimiters · covers: E13, M1, A2 · acceptance · a ref carrying `=` or `,` pins `?`, draws no warn, no hint, no refusal; the reader recovers the writer's pins for every delimiter-carrying ref
- test_two_fragments_of_one_provider_both_pin · covers: E14, M1, M3 · acceptance · `#findings` before `#gives`, and a `=`-spelling before an honest one, still pin `#gives` at the digest and flag the consumer when it moves
- test_scalar_gives_digests_as_one_item · covers: E15, M1 · acceptance · a scalar `gives:` and the one-item list digest alike
- test_pin_string_never_carries_an_inner_delimiter · covers: E16, E13, M1, A2 · acceptance · a ref with both delimiters pins `?` with the delimiters stripped; a property over every delimiter combination round-trips; no warn, no hint, no refusal
- test_pin_survives_the_stamp_lines_own_delimiters · covers: E17, M1, M3 · acceptance · a `"` or `{` in a sibling ref neither drops the honest pin nor swallows the next stamp; the property sweeps the serializer's alphabet
- test_note_and_readers_share_one_consumer_source · covers: E18, M2, M3 · acceptance · an unsealed `needs:` delete or retarget leaves the note naming exactly what doctor, todo and the gate name; one refreeze clears all four
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/consumers-go-stale.d/runs/21.md · kind: test-ids · 21/21 reported · exit 0 · 2026-09-11
refute: held · 11 probe(s) · tier T2 · by advisor:engine-notary · against /tasks/consumers-go-stale.d/runs/21.md · 2026-09-11 · changed: nine T2 reads moved the pin's unit to (STAMPED digest, resolved node, fragment), sourced every reader from the stamp and made the pin string round-trip under the serializer's whole alphabet (E6–E18)
gate: PASS · authority plan · by plan:loop-that-closes · receipt /tasks/consumers-go-stale.d/runs/21.md · 2026-09-11

## LESSONS
- [quality · Q38 · open] The unit of a pin is the RESOLVED target, never its written text: three T2 reads found order, duplicates and two spellings, each a property decided on the pin string in the writer while the readers healed it. Dedupe and order where the pin is MADE, keyed on _norm(), and vary the SPELLING in the bound check (evidence: /tasks/consumers-go-stale.md)
