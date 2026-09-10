---
type: Task
title: R:UNREFUTED and R:REFUTED — a PASS at a plan-or-higher floor needs a refute recorded after the gated run
status: done
depth: standard
sensitivity: architecture
milestone: evidence-over-tests
scope:
  - add-method/tooling
  - add-method/FORMAT.md
  - add-method/tests
  - add-method/src/add_method/_bundled
  - add-method/skill/add
  - .claude/skills/add
  - add-method/agents
  - add-method/docs
  - .add/tooling
gives:
  - S1 `add gate <slug> PASS` refusals `R:UNREFUTED` and `R:REFUTED` — evidence-class (PASS only), at `standard|deep` × computed floor `plan|human`, not `kind: explore`
  - S2 the verify-beat next verb (`status` · `todo`) names `add refute <slug> …` before the gate line when the latest run has no refute stamp at floor ≥ plan
  - S3 FORMAT §8.4's rung sentence, and one line each in verify.md §3 and gate.md naming the refusal
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:5bcfa090d8ae7e0b", binding: "sha256:882cf8210471dfac" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:a9aa340946d3350c" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-gate-rung.d/runs/1.md }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-gate-rung.d/runs/2.md }
  - { by: "builder:claude (same session, tier T1)", at: 2026-09-10, act: refute, authority: process, outcome: held, probes: 3, receipt: /tasks/refute-gate-rung.d/runs/2.md, note: "P1 a refute stamp citing the receipt cid in a different case cites nothing → R:UNREFUTED · P2 a quick-depth data node's hint after a run names the gate, never refute · P3 refuted, held, refuted on one run reads as refuted (latest wins)" }
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: gate, authority: plan, outcome: PASS, receipt: /tasks/refute-gate-rung.d/runs/2.md, brief: "sha256:92d0e9b5b545041f" }
advised_by: engine-notary
---
## CARD
goal: a PASS at a plan-or-higher floor needs a refute recorded AFTER the gated run — the gate reads the stamp's presence and outcome by chronology, exactly as it reads the brief entry, and refuses in the same voice
why: T4 made the refute a record; a record nothing reads is a note. The rung is what makes "was this green read against?" a fact the gate can order — and it binds PRESENCE only, because a notary that judged a probe would be a guard (law 3)
beat: done · next: add status

## RULES
<must>
- M1 at `standard|deep` depth on a Task whose computed floor is `plan` or `human`, `add gate <slug> PASS` refuses `R:UNREFUTED` when no `act: refute` stamp cites the gated receipt's cid
- M2 the same gate refuses `R:REFUTED` when the latest refute stamp citing that receipt carries `outcome: refuted`, and its `next:` names the fix, the re-run and the re-refute — never a verdict
- M3 a refute stamp with `outcome: held` citing the gated receipt satisfies the rung; every other gate rung keeps binding unchanged
- M4 `depth: quick`, a computed floor of `process`, and `kind: explore` are exempt — the rung never fires on them
- M5 at the verify beat on a rung-bound Task whose latest run stamp has no refute citing it, `_next_verb` (`status` · `todo`) names `add refute <slug> --by "<name>" --held|--found "<input>"` instead of the gate line
- M6 FORMAT §8.4 states the rung in one sentence naming both codes and the three exemptions; verify.md §3 and gate.md each name it in one line
</must>
<reject>
- R:NOTINTEGRITY the rung is evidence-class: `RISK-ACCEPTED` and `HARD-STOP` are never refused by it — signing for an unrefuted green is what a signed risk is for -> "NOTINTEGRITY"
- R:NOJUDGE the rung reads `receipt:` and `outcome:` only — never `probes:`, the note text, or who signed; a stamp with `probes: 0` satisfies it -> "NOJUDGE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3 · the request does not say whose refute counts; taking any `by:` — the engine binds presence, the tier ladder (C6) and the persona bind who should have done it -> a builder's self-refute passes the rung; the record shows it was the builder, which is the honest state
- A2 [which] covers: S1, S2, S3 · the request does not say which refute stamp the gate reads when several cite the receipt; taking the LATEST citing stamp — a refuted-then-held sequence on one run reads as held -> a refuted verdict could be overwritten by a later held on the same run; both stamps stay on the record, and reading the latest is what `interview_gap` does for answers · probe: a refuted then a held on the same receipt → PASS allowed
- A3 [when] covers: S1, S2, S3 · the request does not say whether nodes frozen before this engine owe a refute; taking the seal as the key exactly as `unbriefed` does — every sealed rung-bound node owes one, with no version gate — unless the live bundle's own history replays red, in which case the key becomes the node's `generated.by` engine version and this line is corrected -> a historical PASS at plan floor would be refused on replay; measured by the full suite before the receipt
- A4 [absent] covers: S1, S2, S3 · the request does not say what a refute stamp without `receipt:` means; taking it as citing nothing — it satisfies no gate, and the refusal names `add refute` -> a hand-written stamp cannot satisfy the rung by omitting the field
- A5 [order] covers: S1, S2, S3 · the request does not say where the rung sits among the gate's refusals; taking after `unbriefed` and before the covers binding — a green that was never read against is refused before its bindings are counted -> a task learns it owes a refute before it learns of an unbound rule; both are named in the same voice
- A6 [experience] covers: S1, S2, S3 · the request does not say who reads the refusal; taking the agent at the verify beat — so `status`/`todo` already point at `add refute` before the gate refuses, and the refusal's `next:` is copy-pasteable -> without the hint the first contact with the rung is a refusal, which is the affordance-truth failure this bundle already closed once

## PLAN
contract: S1 · S2 · S3 — `_refute_of(stamps, receipt_cid)` returns the latest citing outcome or None; `gate` adds `unrefuted` to `EVIDENCE_REFUSALS` and refuses after the `unbriefed` block; `_next_verb` prefers the refute line at the verify beat by the same predicate; FORMAT §8.4 gains the rung sentence; verify.md §3 and gate.md gain one line; the message-digest and engine pins re-aim; four engine twins sync.
strategy: red suite in tests/engine/test_refute_gate_rung.py first; engine, then prose; full suite before the receipt (the live bundle's history decides A3); this task gates itself through the rung it ships.
port: `add.gate(root, cid, "PASS", by)` and `add._next_verb(graph, cid)` — the tests drive both, and the CLI once

## EDGES
- E1 Given a held refute citing run 1 · When run 2 is recorded and gated · Then `R:UNREFUTED` — a refute of an earlier green entered nothing for this one
- E2 Given a `kind: explore` Task at a data floor with a run receipt · When gated PASS · Then the rung is silent and the explore path decides

## CHECKS
- test_pass_refused_unrefuted_at_plan_floor · covers: M1, A4 · acceptance · data-floor standard Task, bound fresh receipt, no refute (and a refute stamp lacking receipt:) → R:UNREFUTED naming add refute
- test_pass_refused_when_latest_refute_is_refuted · covers: M2, A2 · acceptance · --found then gate → R:REFUTED with fix/run/refute in next; a later --held on the same run → PASS
- test_held_refute_lets_the_pass_through · covers: M3 · acceptance · --held --probes 0 → PASS, task done
- test_quick_process_and_explore_are_exempt · covers: M4, E2 · acceptance · three nodes gate PASS with no refute stamp
- test_refute_of_an_earlier_run_enters_nothing · covers: E1 · acceptance · refute run 1, record run 2, gate → R:UNREFUTED
- test_risk_accepted_and_hard_stop_are_never_refused_by_the_rung · covers: R:NOTINTEGRITY · acceptance · both verdicts recorded on an unrefuted plan-floor node
- test_rung_reads_presence_and_outcome_only · covers: R:NOJUDGE · acceptance · probes 0, no note, by "x" → PASS
- test_verify_hint_names_refute_first_at_plan_floor · covers: M5 · acceptance · _next_verb after a green run names add refute; after a held refute names the gate; process floor names the gate straight away
- test_format_and_skill_name_the_rung · covers: M6 · static · FORMAT §8.4, verify.md §3, gate.md each carry R:UNREFUTED
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
