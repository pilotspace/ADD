---
type: Task
title: The regression floor is a PLAN line the freeze demands and the gate reads
status: done
depth: standard
sensitivity: architecture
milestone: loop-that-closes
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine
  - add-method/tooling/engine_pin.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
  - add-method/FORMAT.md
  - add-method/docs
gives:
  - S1 the PLAN line `regression: full | affected · <cmd> · <why>` or `regression: none · <why>` — read by `freeze`, `gate` and the next-verb hint
  - S2 `add run <slug> --floor -- <cmd>` — a receipt carrying `floor: regression`, kept out of `latest_receipt` and answered by `latest_floor_receipt`
generated: { by: add/3.6.0, at: 2026-09-11 }
verified:
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/regression-floor.d/runs/1.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/regression-floor.d/runs/2.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/regression-floor.d/runs/3.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/regression-floor.d/runs/4.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/regression-floor.d/runs/5.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/regression-floor.d/runs/6.md }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: freeze, authority: plan, direction: "sha256:a0eb478ba61aa5c1", binding: "sha256:6153bfae5edf6614" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:f60d4b4bb2c18fd8" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/regression-floor.d/runs/7.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/regression-floor.d/runs/8.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 3, receipt: /tasks/regression-floor.d/runs/7.md, tier: T2, note: "a floor-only run (A5 floor-first order, no narrow receipt) flips _beat_of (any act:run with no floor filter) to verify: status reports [verify] and next says add gate PASS while latest_receipt is (None, None) — the narrow run's binding lost behind the floor, E7's class" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:b8f434844b67741a", binding: "sha256:e3a5a84e6519dc87" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:79db9eb42ee912d9" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/regression-floor.d/runs/9.md }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/regression-floor.d/runs/10.md }
  - { by: "advisor:engine-notary", at: 2026-09-11, act: refute, authority: process, outcome: held, probes: 3, receipt: /tasks/regression-floor.d/runs/9.md, tier: T2, changed: "two prior T2 reads moved three readers: E7 _latest_run_cid · E8 test_cmd memory · E9 _beat_of" }
  - { by: "plan:loop-that-closes", at: 2026-09-11, act: gate, authority: plan, outcome: PASS, receipt: /tasks/regression-floor.d/runs/9.md, brief: "sha256:19ebffaf8b639572" }
---
## CARD
goal: PLAN carries `regression: full|affected|none · cmd · why`; freeze refuses a rung-bound task without it (R:NOFLOOR); run --floor records a floor receipt; gate PASS refuses a declared floor never run fresh (R:FLOORUNRUN)
why: direction.md lists "the regression floor" among what PLAN carries and nothing gives it a grammar, a slot, or a reader — the 3.2 cut shipped a task green over a red host exactly because the floor was remembered practice; a receipt narrowed to the bound checks is the method's own advice, so the host suite needs its own object or it is nobody's
beat: done · next: add status

## RULES
<must>
- M1 a rung-bound task (standard|deep × computed floor plan|human × not explore) cannot freeze while its PLAN carries no well-formed `regression:` line — `full | affected · <cmd> · <why>`, or `none · <why>`; a template line (`<…>`) is no line
- M2 the rung arms exactly where the refute rung arms: `depth: quick`, a `process` floor and `kind: explore` freeze without the line
- M3 `run --floor` writes a receipt carrying `floor: regression` and a run stamp carrying the same key; `latest_receipt` never returns a floor receipt, and `latest_floor_receipt` returns the newest one
- M4 `gate PASS` on a rung-bound task whose PLAN declares `full` or `affected` refuses while no floor receipt exists, the newest one is stale against the tree, or its exit is not 0 — each refusal names which, and the fix is the PLAN's own command
- M5 the floor rung is evidence-class: `RISK-ACCEPTED` and `HARD-STOP` are never refused by it
- M6 at the verify beat the next-verb hint names `add run <slug> --floor -- <the PLAN's command>` while the declared floor has no fresh green receipt
- M7 the Task scaffold carries the `regression:` slot, FORMAT §8.5 states the grammar and both rungs, and direction.md and verify.md state the line and the flag
</must>
<reject>
- R:NOFLOOR a rung-bound task frozen with no regression line — the host suite left to memory -> "NOFLOOR"
- R:FLOORUNRUN a PASS over a declared floor that was never run, ran stale, or ran red -> "FLOORUNRUN"
- R:FLOORASGATE a floor receipt taken as the gated receipt — a full suite passed off as the bound narrow run, or the narrow run's binding lost behind it -> "FLOORASGATE"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · a PLAN line and a receipt have no actor; `run` records `process:run` as today
- A2 [which] covers: S1 S2 · the request does not say what `affected` means to the engine; taking NOTHING — the engine records the word and runs the command it is handed; which tests are affected is the author's claim, checked at review -> cost if wrong: an `affected` command that runs three tests reads exactly like a full run; the notary cannot tell, and says so in FORMAT
- A3 [when] covers: S1 S2 · the request does not say how fresh the floor receipt must be; taking the same digest rule as the gated receipt — every scope blob byte-identical to the tree at gate time — so a floor run before the last edit is stale, and the gated receipt and the floor receipt therefore both cite one tree -> cost if wrong: a floor that passed on yesterday's tree clears today's PASS · probe: an edit after the floor run refuses the gate
- A4 [absent] covers: S1 S2 · the request does not say what a missing line means at a process floor; taking absent = unarmed, not a refusal — the scaffold carries the slot and `todo` may count it, but a mechanical task never pays -> cost if wrong: every 3.6 node in the wild refuses at its next freeze
- A5 [order] covers: S1 S2 · the request does not say whether the floor runs before or after the narrow receipt; taking either order — the gate reads the newest floor receipt and demands only that it is fresh and green, so a floor recorded first is fine if nothing moved since -> cost if wrong: an author is forced into a ceremony order the evidence does not need
- A6 [experience] covers: S1 S2 · the request does not say who reads the line; the readers are `freeze` (presence), `gate` (mode), the hint (the command) and a reviewer (the why); hard for them is a line whose three fields cannot be told apart — taking `·` as the separator every other PLAN and CHECKS line already uses, mode first so a reader sees the decision before the command -> cost if wrong: a command containing `·` splits wrong; documented as the one character a floor command may not contain

## PLAN
contract: `regression_floor(node_t2) -> {mode, cmd, why} | None` · `run(..., floor=True)` · `latest_floor_receipt(root, cid)` · refusals `R:NOFLOOR` at freeze and `R:FLOORUNRUN` at gate · hint at the verify beat
strategy: parse the line with one regex beside the `budget:` reader in `freeze`; arm both rungs with `_rung_bound` so the exemptions cannot drift apart; the floor receipt is an ordinary `run` receipt plus one key, so freshness, exit and the digest root are inherited, and `latest_receipt` gains one filter; the gate rung lands right after the refute rung in the evidence class; mirror four twins, re-aim the pin; sync the three skill trees
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/tooling/cli.py add-method/src/add_method/_bundled/tooling/cli.py add-method/skill/add add-method/src/add_method/_bundled/skill/add .claude/skills/add add-method/tests/skill add-method/FORMAT.md add-method/docs
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change (method.md bind) — and this milestone's first floor line, dogfooded before the rung exists
port: `add.freeze` · `add.run` · `add.gate` · `add._next_verb` — every acceptance check drives a verb on a fixture bundle; none parses engine source

## EDGES
- E1 Given an architecture-floored standard task whose PLAN has no regression line · When `freeze` · Then it refuses naming R:NOFLOOR and the line to add
- E2 Given the same task with `regression: none · a doc-only change` · When `freeze` · Then it freezes
- E3 Given a mechanical task, a quick task and an explore, none with the line · When `freeze` · Then each freezes
- E4 Given a narrow receipt then a `--floor` receipt · When `latest_receipt` · Then it answers the narrow one, and `latest_floor_receipt` the floor one
- E5 Given a frozen `full` task with a green narrow receipt, entered and refuted · When `gate PASS` with no floor receipt · Then R:FLOORUNRUN naming "never run" and the PLAN's command; after a green floor run, the gate passes
- E6 Given a green floor receipt and then an edit to a scope file · When `gate PASS` · Then R:FLOORUNRUN naming "stale"; given a floor run that exited 1 · Then R:FLOORUNRUN naming the exit
- E7 Given a narrow receipt, a refute citing it, and then a green fresh floor run · When the next verb is derived · Then it moves on to the gate (no second refute demanded) — every reader of "the latest run" skips a floor stamp, as `latest_receipt` does (found by the T2 refute)
- E8 Given a narrow run then a floor run · When the next build hint replays the remembered test command · Then it replays the NARROW command — a floor run never overwrites `index.md`'s `test_cmd` (found by the T2 refute)
- E9 Given a frozen, briefed task whose FIRST run is a floor run (A5's floor-first order) · When the beat is derived · Then it is still `build` and the hint still asks for the narrow run — a floor stamp never closes the build beat (found by the second T2 refute)

## CHECKS
- test_freeze_refuses_rung_bound_task_without_floor · covers: M1, R:NOFLOOR, E1 · acceptance · an architecture-floored task with no line refuses by name; a template line counts as none
- test_freeze_accepts_none_with_a_why · covers: M1, E2 · acceptance · `none · <why>` freezes; `none` alone does not
- test_exempt_lanes_freeze_without_the_line · covers: M2, E3 · acceptance · mechanical · quick · explore freeze with no line
- test_floor_receipt_is_marked_and_kept_out_of_latest · covers: M3, R:FLOORASGATE, E4 · acceptance · the floor receipt carries the key and the stamp; latest_receipt skips it
- test_gate_refuses_a_declared_floor_never_run · covers: M4, R:FLOORUNRUN, E5 · acceptance · full flow minus the floor run refuses naming the PLAN command; with it, passes
- test_gate_refuses_a_stale_or_red_floor · covers: M4, E6, A3 · acceptance · an edit after the floor run refuses "stale"; a red floor refuses naming exit 1
- test_floor_rung_never_refuses_risk_accepted · covers: M5 · acceptance · RISK-ACCEPTED lands with no floor receipt
- test_verify_hint_names_the_floor_run · covers: M6 · acceptance · the next verb at verify carries `--floor` and the PLAN's command
- test_scaffold_format_and_guides_state_the_floor · covers: M7 · static · the Task scaffold has the slot; FORMAT §8.5 names both rungs; direction.md and verify.md carry the grammar and the flag
- test_latest_run_readers_skip_the_floor_stamp · covers: E7, R:FLOORASGATE · acceptance · after a refuted narrow run and a green floor, `_latest_run_cid` still names the narrow receipt and the hint moves to the gate
- test_floor_run_never_overwrites_the_remembered_test_cmd · covers: E8, R:FLOORASGATE · acceptance · `test_cmd` on index.md stays the narrow command after a floor run
- test_floor_only_run_keeps_the_build_beat · covers: E9, R:FLOORASGATE · acceptance · after a floor-first run the derived beat is build and the hint names the narrow run, at T0 and T2
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/regression-floor.d/runs/9.md · kind: test-ids · 12/12 reported · exit 0 · 2026-09-11
refute: held · 3 probe(s) · tier T2 · by advisor:engine-notary · against /tasks/regression-floor.d/runs/9.md · 2026-09-11 · changed: two prior T2 reads moved three readers: E7 _latest_run_cid · E8 test_cmd memory · E9 _beat_of
gate: PASS · authority plan · by plan:loop-that-closes · receipt /tasks/regression-floor.d/runs/9.md · 2026-09-11

## LESSONS
- none filed — no lesson cites /tasks/regression-floor.md (add learn <lens> "<lesson>" --evidence /tasks/regression-floor.md)
