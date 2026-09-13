---
type: Task
title: A rule names the runtime signal that would show it broken
status: done
depth: standard
sensitivity: mechanical
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
gives:
  - S1 the PLAN line grammar `- O<n> covers: M<n>[, …] · signal <metric> · window <w> · threshold <t> · action alert|rollback` read by `observes(node) -> [{id, covers, signal, window, threshold, action}]`
  - S2 `brief` renders the lines in an `<observes>` block and `show` carries them; `freeze` notices a human-floor task with none
  - S3 no gate reads them — whether a monitor fired is production's evidence, not the bundle's
generated: { by: add/3.6.0, at: 2026-09-11 }
verified:
  - { by: "plan:loop-that-closes", at: 2026-09-12, act: freeze, authority: plan, direction: "sha256:65eedd21c687f8d9", binding: "sha256:ddd24738e4f17fa0", gives: "sha256:5bbe13292f67268e" }
  - { by: "cli", at: 2026-09-12, act: brief, authority: process, brief: "sha256:b53ec9bcb1baa11e" }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, outcome: PASS, receipt: /tasks/observes-slot.d/runs/1.md }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, floor: regression, outcome: FAIL, receipt: /tasks/observes-slot.d/runs/2.md }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, outcome: PASS, receipt: /tasks/observes-slot.d/runs/3.md }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/observes-slot.d/runs/4.md }
  - { by: "plan:loop-that-closes", at: 2026-09-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/observes-slot.d/runs/3.md, brief: "sha256:43fe452b5528870b" }
---
## CARD
goal: PLAN accepts `- O<n> covers: M<n> · signal <metric> · window <w> · threshold <t> · action alert|rollback` lines; `brief` and `show` render them; `freeze` notices a human-floor task with none; no gate reads them
why: loop.md says the CHECKS have a second life as monitors, but no slot holds which signal would show a rule broken — a task with observes lines shows nothing today (C7, as a slot not a gate)
beat: done · next: add status

## RULES
<must>
- M1 `observes(node)` reads every `- O<n> covers: <M ids> · signal <text> · window <text> · threshold <text> · action <alert|rollback>` line in `## PLAN` into `{id, covers, signal, window, threshold, action}`; a line missing a field, with a `<placeholder>`, or with an action outside the two, is not an observe and is reported by `doctor` as `observe_malformed` (info) naming the line
- M2 `brief` renders the observes in a `<observes>` block after the contract — one `<o id covers action>signal · window · threshold</o>` per line — and `show`'s body carries the PLAN lines as written; a node with none renders no block
- M3 `freeze` on a task whose computed floor is `human` appends `notice: no observes: line — name the runtime signal that would show M<n> broken (PLAN, O<n>)` when `observes(node)` is empty — a notice, never a refusal (R:OBSERVEASREFUSAL); at plan and below nothing is said
- M4 no gate, rung or hint reads an observe: `gate`, `_next_verb`, `todo` and `doctor` (beyond `observe_malformed`) are byte-for-byte indifferent to the lines (R:OBSERVEASGATE)
- M5 the scaffold PLAN gains the `O<n>` slot line; direction.md's PLAN bullet and loop.md's monitors paragraph name it; the skill surface stays line-neutral vs HEAD and the three trees identical
</must>
<reject>
- R:OBSERVEASGATE a verdict, refusal or hint decided by an observes line — production's evidence is not the bundle's -> "OBSERVEASGATE"
- R:OBSERVEASREFUSAL a freeze refused for lacking one -> "OBSERVEASREFUSAL"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · the request does not say who writes the lines; taking the author at direction, as every PLAN line — the persona (site-reliability or the domain's) advises them at the same beat -> cost if wrong: a builder writes them at build; the seal ignores PLAN, so nothing drifts
- A2 [which] covers: S1 · the request does not say what `signal`, `window` and `threshold` may contain; taking free text separated by `·` — the engine can name a slot, not judge a metric -> cost if wrong: a threshold nobody can measure is recorded; the reviewer reads it in the brief · probe: `signal p99 latency · window 5m · threshold > 800ms` round-trips as three strings
- A3 [when] covers: S2 · the request does not say when the notice fires; taking the freeze (and refreeze) of a human-floor task only — the one beat where the human reads the whole node -> cost if wrong: a plan-floor payment-adjacent task carries no observes and no one is told; the router's persona step still asks
- A4 [absent] covers: S1 S2 S3 · the request does not say what a node with no O lines means; taking nothing — no block, no finding, no notice below human -> cost if wrong: every pre-3.7 node is silent, which is what it was
- A5 [order] covers: S1 S2 · the request does not say the order of the fields; taking the written order `covers · signal · window · threshold · action`, fixed, so one regex reads every line and the brief prints them the same way -> cost if wrong: a hand-written line in another order is `observe_malformed`, named by doctor
- A6 [experience] covers: S1 S2 S3 · the request does not say who reads the block; the reader is the agent at build (the brief) and the on-call reader at observe (`show`); hard for them is a monitor named without the rule it watches — taking `covers:` as required, so every observe names the Must it would show broken -> cost if wrong: an observe covering nothing is malformed, and doctor says so
- A7 [which] covers: S2 · the request does not say which renderers carry the lines; taking `brief` (the agent's contract for the beat) and `show`'s body, not `status` and not the JSON payload's own key — a summary line per observe would cost every reader width for a slot no verb reads -> cost if wrong: a tool that wants them parses the PLAN lines `show` already prints
- A8 [which] covers: S3 · the request does not say which readers must stay indifferent; taking every verdict-bearing one — `gate`, `_next_verb`, `todo`, and `doctor` beyond its one `observe_malformed` info — because an observe that moves ANY outcome makes production's evidence the bundle's (R:OBSERVEASGATE) -> cost if wrong: a hint shifts under a line nobody checked; E4 gates two copies and compares
- A9 [when] covers: S1 · the request does not say when a line may be written or edited; taking ANY time — PLAN is sealed by no digest, so an observe added after the freeze is neither drift nor a re-cross -> cost if wrong: a line added late is invisible to a brief already composed; the next brief carries it
- A10 [when] covers: S3 · the request does not say when the prose takes effect; taking THIS engine forward with no migration — every pre-3.7 node has no O line and stays exactly as silent as A4 says -> cost if wrong: nothing; silence is the pre-3.7 state
- A11 [order] covers: S3 · the request does not say the order of the doc edits across the trees; taking the source tree first and mirrored byte-for-byte, never edited per-tree, with the surface line-neutral vs HEAD -> cost if wrong: one installed tree promises a slot another does not carry · probe: the three trees compare equal

## PLAN
contract: `OBSERVE_LINE` regex · `observes(node) -> list` · `doctor` finding `observe_malformed` · `brief` `<observes>` block · `freeze` notice at floor human · scaffold PLAN slot · direction.md and loop.md sentences
strategy: the lines ride PLAN, which no digest seals and no gate reads, so M4 holds by construction and is bound by a check that gates a node with and without the lines to identical outcomes; four twins, both pins, three skill trees line-neutral
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/skill/add add-method/src/add_method/_bundled/skill/add .claude/skills/add add-method/tests/skill
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change (method.md bind)
port: `add.observes`, `add.brief`, `add.freeze`, `add.doctor` on a node fixture with O lines

## EDGES
- E1 Given `- O1 covers: M1 · signal 5xx rate on /list · window 5m · threshold > 1% · action alert` · When `observes` · Then one record with the six fields; `brief` carries `<o id="O1" covers="M1" action="alert">`
- E2 Given `- O2 covers: M1 · signal x · action page` (no window, no threshold, bad action) · When `doctor` · Then `observe_malformed` info naming O2; `observes` returns only O1
- E3 Given a security task with no O line · When `freeze` · Then the note carries the notice; with one · Then no notice; a data task with none · Then no notice
- E4 Given two copies of a rung-bound node, one with O lines and one without · When each is briefed, run, refuted and gated · Then the outcomes and the hints are identical

## CHECKS
- test_observes_reads_the_grammar · covers: M1, A2, A5, E1 · acceptance · six fields, free text round-trips
- test_malformed_lines_are_named_not_read · covers: M1, E2 · acceptance · doctor info, observes skips
- test_brief_renders_the_block · covers: M2, E1 · acceptance · the block and the per-line element; none when empty
- test_freeze_notices_only_at_human · covers: M3, R:OBSERVEASREFUSAL, A3, E3 · acceptance · notice at security; none with a line; none at data
- test_no_gate_reads_an_observe · covers: M4, R:OBSERVEASGATE, E4 · acceptance · identical gate outcomes and hints with and without
- test_scaffold_and_docs_carry_the_slot · covers: M5, A11 · static · new's PLAN has the O line; direction.md and loop.md name it; trees identical; line-neutral
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/observes-slot.d/runs/3.md · kind: test-ids · 6/6 reported · exit 0 · 2026-09-12
gate: PASS · authority process · by plan:loop-that-closes · receipt /tasks/observes-slot.d/runs/3.md · 2026-09-12

## LESSONS
- none filed — no lesson cites /tasks/observes-slot.md (add learn <lens> "<lesson>" --evidence /tasks/observes-slot.md)
