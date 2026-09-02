---
type: Task
title: The beat status and brief report is the beat the stamps derive
status: done
depth: standard
sensitivity: architecture
milestone: first-run-truth
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine
gives:
  - S1 the `status` node line — the beat an orienting reader is shown per node
  - S2 the `brief` phase attribute — the beat the composed prompt declares to any agent
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:bfa8ea2e5c28cbda" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:80446f507d9910fd" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/beat-read-truth.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-01, act: refreeze, authority: human, direction: "sha256:d907a14a00f85c11" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:92e2ddf6245132db" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/beat-read-truth.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-01, act: gate, authority: plan, outcome: PASS, receipt: /tasks/beat-read-truth.d/runs/2.md, brief: "sha256:92e2ddf6245132db" }
---
## CARD
goal: `status` and `brief` report the beat DERIVED from a node's stamps, so a frozen task never reads `direction` and the two verbs never contradict each other.
why: `freeze` calls `_transition(root, cid, appends=[("verified", …)])` with no `sets=` (add.py:1527), so the frontmatter `status:` field never advances past `direction`. Both reader verbs print that raw field — `status` at add.py:2239, `brief` at add.py:3208 — while `todo` and `doctor` use the derived beat. Reproduced 2026-09-01: one `status` call after a freeze prints `· transfer [direction] Task` beside `next: add brief transfer`, `todo` groups the same node under `build:`, and `doctor` reports `card_drift: CARD beat says scaffold, status is build`. Three verbs, three answers, one node. README.md:191-192 sells `cli.py status` and `cli.py brief` as the portable path every non-Claude agent follows; a Codex or Cursor agent resuming a frozen task is handed `phase="direction"` and re-does Direction on a sealed contract. The engine already computes the right answer — `_beat_of` derives scaffold · direction · build · verify from the stamps — and two readers ignore it. Fixing on the READ side rather than stamping on write also heals every already-frozen node in every existing bundle on the next read, and covers `reopen` and `replan`, which a write-side fix would leave to drift again.
beat: done · next: add status

## RULES
<must>
- M1 `status` prints the DERIVED beat for every node that has one, never the raw `status:` frontmatter field.
- M2 `brief` resolves its `phase` attribute from the derived beat, so a frozen node briefs its build beat.
- M3 The derivation reads frontmatter only — no node body is loaded to answer orientation, so the T2-scan read tier holds.
- M4 A node type with no beat (Project · Spec · Persona · Run) prints exactly what it prints today.
- M5 `status`, `todo`, `brief` and `doctor` agree on the beat of any one node.
</must>
<reject>
- R:BEATLIE a reader must never report a beat that contradicts the node's own stamps -> "R:BEATLIE"
- R:T2SCAN orientation must never read a node body to answer -> "R:T2SCAN"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say whose view changes; taking every reader of orientation, since a beat that differs by caller is the defect itself -> if wrong one caller keeps the stale reading · probe: the derivation is one function both verbs call.
- A2 [which] covers: S1 · the request does not say WHICH node types carry a beat; taking Task and Milestone — the types `_beat_of` already derives — and leaving every other type's line byte-identical -> if wrong a Spec or Persona line changes shape and breaks a pinned output · probe: a Spec node's status line is unchanged.
- A3 [when] covers: S2 · the request does not say when `brief` should prefer an explicit phase argument; taking the caller's explicit `phase` when given, and the derived beat only as the default that today reads the raw field -> if wrong an explicit `brief --phase verify` is overridden · probe: an explicit phase argument still wins.
- A4 [absent] covers: S1 · the request does not say what an ABSENT status field means; taking the derived beat, which is the whole point — a node with no stamps derives `scaffold` or `direction` on its own -> if wrong a scaffolded node reads as an em-dash and orientation teaches nothing · probe: a never-authored node reports `scaffold`.
- A5 [order] covers: S2 · the request does not say what wins when the stored field and the stamps disagree; taking the STAMPS, because they are the append-only ledger and the field is a cache -> if wrong the cache overrides the ledger · probe: a node whose stored field says `direction` and whose stamps carry a freeze reports `build`.
- A6 [experience] covers: S1 · the request does not say what the reader should see; taking the same one-word beat vocabulary `todo` already prints, so the two verbs read as one system -> if wrong the reader learns two vocabularies for one fact · probe: the beat words `status` prints are exactly the ones `todo` groups by.
- A7 [who] covers: S2 · n/a · `brief` composes for whatever agent asks; the phase does not vary by actor.
- A8 [which] covers: S2 · n/a · `brief` is only ever called on a Task or an Explore Task, both of which derive.
- A9 [when] covers: S1 · n/a · orientation is a point-in-time read with no boundary of its own.
- A10 [absent] covers: S2 · n/a · A4's reading governs both surfaces: absence derives rather than defaults.
- A11 [order] covers: S1 · n/a · A5 fixes ledger-over-cache for every reader.
- A12 [experience] covers: S2 · n/a · `brief`'s consumer is an agent reading an attribute, not a human reading a line.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `status`'s per-node line and `brief`'s phase default both resolve through the existing frontmatter-only beat derivation instead of `fm.get("status")`. No stamp is written, no bundle is migrated, and no node file changes on disk.
scope: add-method/tooling/add.py, add-method/tests/engine

## EDGES
- E1 a reopened task — the reset gate means the derived beat must fall back to the beat `reopen` returned it to, not to `verify`.
- E2 a node with a freeze stamp and a LATER refreeze — the derivation reads the newest seal.
- E3 a Spec, Persona, Project or Run node — line unchanged (M4).
- E4 a never-authored scaffold — reports `scaffold`, the fourth beat SKILL.md's orient paragraph omits.
- E5 a done task — still reads `done`, which is a status, not a beat.

## CHECKS
- test_status_reports_the_derived_beat_after_a_freeze · covers: M1, A5, R:BEATLIE · a frozen node reads `build`, never `direction`.
- test_status_and_todo_agree_on_every_node · covers: M5, A6 · the beat words match for every node in a fixture bundle.
- test_brief_phases_the_build_beat_on_a_frozen_node · covers: M2 · the composed prompt declares `phase="build"`.
- test_brief_still_honours_an_explicit_phase · covers: A3 · an explicit argument wins over the derivation.
- test_orientation_reads_no_node_body · covers: M3, R:T2SCAN · the derivation is proved to touch frontmatter only.
- test_a_scaffold_reports_the_scaffold_beat · covers: A4, E4 · a never-authored node is not reported as direction-in-progress.
- test_a_reopened_task_reports_its_reset_beat · covers: E1 · reopen's beat survives the derivation.
- test_a_refrozen_task_reads_the_newest_seal · covers: E2 · the latest freeze governs.
- test_non_beat_node_types_are_unchanged · covers: M4, A2, E3 · Spec/Persona/Project/Run lines are byte-identical.
- test_a_done_task_still_reads_done · covers: E5 · a closed task is not re-derived into a beat.
- test_every_reader_derives_the_beat_through_one_function · covers: A1 · status, todo and brief all reach the beat through `_beat_of`, and no second derivation exists.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
