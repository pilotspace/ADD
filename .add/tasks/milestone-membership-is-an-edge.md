---
type: Task
title: Milestone membership is an edge the graph can walk, not a slug only todo can string-match
status: done
depth: standard
sensitivity: architecture
milestone: okf-graph-lookup
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/scripts/validate_bundle.py
  - add-method/FORMAT.md
  - add-method/tests/engine
gives:
  - S1 add.edges(graph) — a `milestone:` value that is a bare slug yields an edge whose target is that slug under `/milestones/`, suffixed `.md`; a value already carrying a `.md` ref resolves as it does today, to the identical target
  - S2 scripts/validate_bundle.py edges() — the second oracle learns the identical resolution, so one value reads one way in both readers
  - S3 FORMAT.md §3.2 — the documented membership rule: which key resolves a bare slug, to which directory, and why no other key does
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:b9213c531f16db26", binding: "sha256:69e14c1306e71f45" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:beb7ce7360f6145e" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/milestone-membership-is-an-edge.d/runs/1.md }
  - { by: "builder", at: 2026-09-04, act: replan, authority: process, note: "residue sweep (architecture): a bare slug 'index' or 'log' mapped to /milestones/index.md · /milestones/log.md — the RESERVED compiled bodies (NOT_A_NODE). No traversal is reachable and no live instance exists, but a membership edge into a compiled body is wrong. Excluding the reserved names in both oracles, with a check; seal untouched." }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/milestone-membership-is-an-edge.d/runs/2.md }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:8d14a8f72e1b16da", binding: "sha256:69e14c1306e71f45" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:b2bc38354a5ce413" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/milestone-membership-is-an-edge.d/runs/3.md }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: gate, authority: plan, outcome: PASS, receipt: /tasks/milestone-membership-is-an-edge.d/runs/3.md, brief: "sha256:b2bc38354a5ce413" }
---
## CARD
goal: the Task-to-Milestone link becomes traversable in both oracles, without entering any dependency adjacency.
why: `milestone:` is in `EDGE_KEYS` and is declared on 45 nodes, yet `edges()` yields zero edges for it — every value is a bare slug and both oracles skip any ref without `.md`. The bundle's most load-bearing structural link is invisible to the graph, so a neighbourhood walk from a Milestone returns nothing and a walk from a Task returns only its receipts.
beat: done · next: add status

## RULES
<must>
- M1 a `milestone:` value that is a bare slug yields an edge whose target is `/milestones/<slug>.md`, in `add.edges()` AND in `validate_bundle.edges()`
- M2 both spellings resolve to the identical target: `milestone: okf-graph-lookup` and `milestone: /milestones/okf-graph-lookup.md`
- M3 the membership key never enters the dependency adjacency of `cycles()` or of `wave()`, and a check reds if it is added
- M4 `FORMAT.md` §3.2 states the membership rule, naming the one key it applies to and the one directory it resolves into
</must>
<reject>
- R:GENERALISE a bare slug under any key other than `milestone` must never resolve — `depends_on: foo` stays unresolved, because no key but this one names a directory -> "GENERALISE"
- R:ESCAPE a membership value must never resolve outside the bundle root; containment is decided after the slug is mapped, never before -> "ESCAPE"
- R:SILENTCYCLE the exclusion from `cycles()` must be held by a check of its own, never left to the current allowlist happening to omit the key -> "SILENTCYCLE"
- R:DRIFT the two oracles must not disagree about any membership value — one value, one target, both readers -> "DRIFT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · n/a · membership resolution is a pure read over frontmatter already present; it grants no capability and no verb, so there is no actor whose rights change
- A2 [which] covers: S1 S2 S3 · the request does not say which keys take a bare slug; taking `milestone` ALONE, because it is the only key whose target directory is implied by the ADD node taxonomy — `depends_on` may name a Task or a Milestone and has no default dir · probe: a bare slug under `depends_on:` still reports no target, before and after -> if wrong, every bare string in the bundle becomes a speculative edge and `edge_unresolved` stops meaning anything
- A3 [when] covers: S1 S2 · the request does not say where the boundary falls between a slug and a ref; taking the dispatch both oracles ALREADY branch on — the structural test `".md" not in ref` — so only its else-arm changes and no new branch point is invented · found: add.py:459 and validate_bundle.py:253 carry that identical test today -> if wrong, a value carrying a path but no suffix maps to the wrong directory in both readers at once
- A4 [when] covers: S3 · n/a · a FORMAT paragraph has no runtime boundary of its own; the boundary it describes is S1's and is swept on A3
- A5 [absent] covers: S1 S2 S3 · the request does not say what a `milestone:` naming no milestone file means; taking `edge_unresolved` at info — the code the family already uses for a named-but-missing node — never an error · found: all 45 live references across 13 distinct milestones resolve, so this arm ships with zero live instances and must be proven on a fixture -> if wrong, an archived milestone turns every one of its tasks into an error finding
- A6 [order] covers: S1 S2 · the request does not say what orders the emitted edges; taking NO change — `edges()` iterates `EDGE_KEYS` in a fixed tuple over a dict built from `sorted(rglob)`, and adding an else-arm to one key emits in that same position -> if wrong, `graph.json` and every diffable listing reorder for 45 nodes and every downstream pin churns
- A7 [order] covers: S3 · n/a · a documented rule has no emission order; FORMAT §3.2's paragraph position is editorial, not a contract
- A8 [experience] covers: S1 S2 · the receiver is `doctor` and the neighbourhood walk, and what would make this hard for them is a NEW finding class appearing on a bundle that was clean; taking the existing `edge_unresolved` code rather than a membership-specific one, so no consumer learns a new string · found: zero dangling references today, so a clean bundle stays clean -> if wrong, every bundle in the wild reports unfamiliar findings on upgrade
- A9 [experience] covers: S3 · the reader is the next engine author deciding whether their new key should resolve a bare slug; taking a FORMAT rule that states the REASON (one key, one implied directory) rather than the mechanism, so it reads as a judgment to apply instead of a recipe to copy -> if wrong, the next key added quietly resolves bare slugs into the wrong directory and both oracles agree on the wrong answer

## PLAN
contract: `edges()` keeps its `(src, key, ref, target)` tuple shape. Its `.md`-absent branch gains one arm: when `key == "milestone"` and the value is a bare slug (no `/`, no `.md`), the target becomes `/milestones/<slug>.md`, subject to the same containment test every other target takes. `validate_bundle.edges()` takes the identical arm. Nothing on disk changes; 45 nodes become traversable at once. `cycles()` and `wave()` are untouched — they already allowlist their keys — and gain a guard proving they stay that way.
strategy: write the guards first against today's engine, confirm the membership guards red and the two adjacency guards GREEN (they already hold), then land the resolution in `add.py`, mirror to the second oracle and the three twins, re-aim `ENGINE_MD5`, and re-run.

## EDGES
- E1 a bare slug under `depends_on:` resolves to nothing, before and after (R:GENERALISE)
- E2 `milestone: /milestones/x.md` and `milestone: x` yield the identical target (M2)
- E3 a `milestone:` naming a file that does not exist reports `edge_unresolved` at info, and never raises
- E4 a membership value shaped to escape (`../../outside`) carries a `/`, so it is not a bare slug and takes no membership arm; if it takes the `.md` arm it is still tested for containment (R:ESCAPE)
- E5 `cycles()` returns the identical cycle list before and after, on this bundle and on a fixture with a Task-Milestone loop present (M3, R:SILENTCYCLE)
- E6 `wave()` returns the identical level plan for a milestone before and after (M3)

## CHECKS
- test_milestone_slug_resolves_to_a_milestone_node · covers: M1 · a bare-slug `milestone:` yields a target under `/milestones/` in `add.edges()`
- test_second_oracle_resolves_membership_identically · covers: M1, R:DRIFT · both readers over one bundle: a resolving membership is silent in each, a dangling one is reported by each
- test_both_membership_spellings_name_one_target · covers: M2, E2 · the bare slug and the explicit `.md` ref produce the same target cid
- test_membership_never_enters_cycle_adjacency · covers: M3, E5, R:SILENTCYCLE · a fixture whose Task and Milestone reference each other reports no cycle, with both legs asserted resolved first
- test_cycles_still_finds_a_real_dependency_cycle · covers: M3, R:SILENTCYCLE · the acyclic claim above is not vacuous — a real `depends_on` cycle is still reported
- test_wave_levels_unchanged_by_membership · covers: M3, E6 · `wave()` keeps two independent members in ONE parallel level
- test_only_the_milestone_key_resolves_a_bare_slug · covers: R:GENERALISE, E1, A2 · A2's probe, enumerated over `add.EDGE_KEYS` itself rather than a hand list
- test_membership_value_cannot_escape_the_bundle · covers: R:ESCAPE, E4 · a `../`-bearing membership value never resolves to a target outside the root
- test_reserved_names_are_not_membership_targets · covers: R:ESCAPE, A5 · `index` and `log` are compiled bodies (§3.1) and never become membership targets — found at VERIFY by the architecture lens, recorded by `add replan`
- test_second_oracle_excludes_reserved_names_too · covers: R:DRIFT · the reserved-name exclusion is mirrored, so one value reads one way in both oracles
- test_missing_milestone_is_unresolved_not_error · covers: A5, E3 · a `milestone:` naming no file reports `edge_unresolved` at info severity and raises nothing
- test_format_states_the_membership_rule · covers: M4 · FORMAT §3.2 names the key, the bare-slug form, and the directory
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/n.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
