---
type: Task
title: A routing key outside its closed taxonomy is a finding, never a silence
status: done
depth: quick
milestone: live-persona-tier
scope:
  - add-method/tooling/add.py
  - .add/personas
  - add-method/tests
gives:
  - S1 a `doctor` finding — a routing key whose value falls outside its closed taxonomy
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:44449e6cb5a9a1e1" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:8753e7f5edd37ce4" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-routing-keys-checked.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-01, act: gate, authority: process, outcome: PASS, receipt: /tasks/persona-routing-keys-checked.d/runs/1.md, brief: "sha256:ecb0b469d8c6428f" }
---
## CARD
goal: `doctor` reports a Persona node whose `flow:` or `task-kinds:` carries a value outside its closed set, `explore` joins the task-kind taxonomy, and ADD's own two personas pass the check they should always have passed.
why: Both routing keys are documented as CLOSED vocabularies — `flow:` over `design · build · advisor · verify`, `task-kinds:` over ten values — and `references/contract.md:52-53` admits outright that any other value "is a typo that no surface loads, and NOTHING warns". `grep -n task-kinds` over the engine finds it only in the scaffold writer, never in a validator. The consequence is silent misrouting, the worst kind: the agent takes the generic fallback and reports success. ADD's own dogfood roster proves it — `engine-notary.md:6` carries `task-kinds: engine, tooling, testing` and `method-steward.md:6` carries `planning, documentation, method-design`; five of six values are outside the taxonomy, so by the method's own contract both of ADD's personas route nothing. Separately the taxonomy is missing a value it needs: `--kind explore` is a whole shipped lane with its own freeze refusal and its own gate path, and `explore` is not in the ten, so for EVERY explore task the selector's `task-kinds:` predicate is unsatisfiable — the rung ADD reserves for "do not guess" is the one rung guaranteed to get a generic agent. A closed set is exactly the precondition for a cheap enumerating check, and this project's own lesson says a rule that quantifies over a set must enumerate that set, both directions.
beat: done · next: add status

## RULES
<must>
- M1 `doctor` emits a finding naming the node, the key and the offending value when a Persona's `flow:` or `task-kinds:` falls outside its closed set.
- M2 The check enumerates each taxonomy from its single source in the engine, never from a list copied into the check.
- M3 `explore` is a member of the task-kind taxonomy, in the engine and in every file that states the taxonomy.
- M4 The finding is informational — it never gates, and `doctor` stays a reporter.
- M5 ADD's own personas carry in-taxonomy values and the check passes on this bundle.
</must>
<reject>
- R:SILENTMISROUTE a routing key outside its closed set must never pass unreported -> "R:SILENTMISROUTE"
</reject>

## ASSUMPTIONS
- A1 [which] covers: S1 · the request does not say which nodes are checked; taking Persona nodes only, since the keys are meaningless elsewhere -> if wrong a Task's unrelated frontmatter is flagged · probe: a Task carrying a stray `flow:` is not reported.
- A2 [absent] covers: S1 · the request does not say what an ABSENT key means; taking silence — a persona may legitimately declare neither and be selected by `use-when:` prose -> if wrong every corpus persona becomes a finding · probe: a persona with no routing keys produces no finding.
- A3 [order] covers: S1 · the request does not say how multiple offenders are reported; taking one finding per node per key, ordered by node id, because a stable order is diffable -> if wrong the report churns run to run · probe: findings are ordered and one-per-offence.
- A4 [experience] covers: S1 · the request does not say what the reader needs; taking the node, the key, the bad value AND the closed set, because a taxonomy violation is unfixable without knowing the taxonomy -> if wrong the reader is told they are wrong without being told what is right · probe: the finding prints the allowed values.
- A5 [who] covers: S1 · n/a · `doctor` is read-only and identical for every caller.
- A6 [when] covers: S1 · n/a · conformance is evaluated at read time with no boundary of its own.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: the two taxonomies become named constants in the engine; `doctor` gains an info-severity finding enumerating Persona routing keys against them; `explore` joins the task-kind set there and in the skill and reference files that state it; ADD's two personas are corrected to in-taxonomy values.
scope: add-method/tooling/add.py, .add/personas, add-method/tests

## EDGES
- E1 a persona declaring NEITHER key — no finding (A2).
- E2 a comma-separated list where one value is bad and the rest are good — the finding names the offending value only.
- E3 a non-Persona node carrying a stray `flow:` — not reported (A1).
- E4 the corpus personas, which carry neither key — must not turn 232 files into findings.
- E5 the taxonomy's own statements in `contract.md` and `personas.md` — must gain `explore` in lockstep with the engine (M3).

## CHECKS
- test_doctor_reports_an_out_of_taxonomy_flow · covers: M1, R:SILENTMISROUTE · the finding names node, key and value.
- test_doctor_reports_an_out_of_taxonomy_task_kind · covers: M1, E2 · only the offending value is named.
- test_the_check_enumerates_the_taxonomy_from_source · covers: M2 · no copied list.
- test_explore_is_in_the_task_kind_taxonomy · covers: M3, E5 · engine and every stating file agree.
- test_the_finding_never_gates · covers: M4 · `doctor` exits as a reporter.
- test_this_bundles_personas_pass · covers: M5, A4 · ADD's own roster is in taxonomy.
- test_a_persona_with_no_routing_keys_is_silent · covers: A2, E1, E4 · absence is not an offence.
- test_a_non_persona_node_is_not_checked · covers: A1, E3 · scope holds.
- test_findings_are_ordered_and_one_per_offence · covers: A3 · the report is stable.
- test_the_finding_prints_the_allowed_values · covers: A4 · the reader is told what is right.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
