---
type: Task
title: Explore lane — 4th intake lane + phases/explore.md research loop
status: done
depth: standard
milestone: dynamic-flow
scope:
  - add-method/skill/add
  - .claude/skills/add
  - add-method/src/add_method/_bundled/skill/add
  - add-method/tests/skill
gives:
  - S1 `phases/explore.md` — the Explore phase guide (scope+budget · loop · compress · sufficiency gate)
  - S2 `intake.md` § Explore — the 4th lane entry with its routing criteria and veto
  - S3 `SKILL.md` — the Explore lane named in the always-loaded router (compression-funded)
  - S4 the explore node convention — `Task` + `kind: explore` + `## FINDINGS`, consumed downstream by a `needs:` edge carrying the `#findings` fragment
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "Tin Dang", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:8365f5dd1b253b92" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:eeadeefd20f8ad77" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/explore-lane.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-11, act: refreeze, authority: human, direction: "sha256:cb47bab1411d23a1" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:2cc1261527d584ef" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/explore-lane.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/explore-lane.d/runs/2.md, brief: "sha256:2cc1261527d584ef" }
---
## CARD
goal: a research/spike request has a first-class lane — scoped questions + budget in, a compressed cited `## FINDINGS` brief out, closed by a sufficiency gate on the existing Task lifecycle
why: work whose deliverable is *finding out* currently has no home — Quick is mechanical-only and Task forces a frozen contract on the unknown

## RULES
<must>
- M1 `intake.md` documents Explore as a 4th lane: what routes to it (the primary work is answering questions, not editing), the AI routes / human vetoes, and the closed sensitivity floor still applies
- M2 `phases/explore.md` defines the full loop: freeze = the questions + budget approval → query/read/reflect/refine (broad → narrow) → compress to a cited `## FINDINGS` section (raw dumps discarded) → gate = the sufficiency verdict recording which questions closed
- M3 `SKILL.md` names the Explore lane inside the 150-line router budget — funded by compressing existing prose, never by raising the budget
- M4 `phases/explore.md` documents downstream consumption: a later task declares `needs: [/tasks/<explore>.md#findings]` and `add brief` compiles the brief into its Direction (existing §3.3 fragment rules, no engine change)
- M5 all three git-tracked skill trees stay identical (canonical · `.claude/skills/add` · `_bundled`)
</must>
<reject>
- R:PHANTOM_VERB `phases/explore.md` names an `add <verb>` the CLI does not dispatch — the lane runs entirely on wired verbs (`new --kind explore` · `freeze` · `run` · `gate`) -> "PHANTOM_VERB"
- R:FLOOR_DROP the lane text weakens any floor — security HARD-STOP, the human freeze seam, or receipt binding -> "FLOOR_DROP"
- R:BUDGET any budget breached — SKILL.md > 150 lines, explore.md > 350, total surface > 1500 -> "BUDGET"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who may record the sufficiency gate; taking: identical to any Task — quick-depth self-pass rules and the sensitivity floor apply unchanged -> cost: over-autonomy on research verdicts · probe: explore.md states the floor verbatim
- A2 [who] covers: S2 · the request does not say who scores "uncertainty" at intake; taking: the AI routes silently and the human vetoes, exactly as the three existing lanes -> cost: mis-routed requests
- A3 [which] covers: S2 · the request does not say which requests qualify; taking: primary work = answering questions (investigate · evaluate · research), whatever the eventual code size -> cost: lane abused as a slow path for normal tasks
- A4 [which] covers: S4 · the request does not say which node type carries an explore; taking: `Task` + `kind: explore` — the ABF type vocabulary is closed and only Task carries lifecycle -> cost: none if wrong late; a type change would be a FORMAT edit
- A5 [when] covers: S1 · the request does not say when the loop stops; taking: a sufficiency judgment against the frozen questions, with the declared budget as the hard backstop -> cost: unbounded loops or premature stops · probe: explore.md names both stop conditions
- A6 [absent] covers: S1 · the request does not say what happens when no budget is declared; taking: the guide REQUIRES a budget line in PLAN before freeze (doc-enforced now; engine enforcement is `sources-receipt`) -> cost: an unbounded explore until the engine task lands
- A7 [absent] covers: S4 · the request does not say what a missing `## FINDINGS` means at gate; taking: gate cannot honestly PASS without it (doc-enforced now; receipt-enforced in `sources-receipt`) -> cost: hollow explores until then
- A8 [order] covers: S1 · the request does not say the search order; taking: broad → progressively narrow as guidance, never a gate -> cost: none material
- A9 [when] covers: S3 · the request does not say which SKILL.md prose funds the two-line headroom; taking: compress the depth-dial section — highest redundancy with phase guides; pinned phrases stay intact -> cost: a value-pin test breaks · probe: full skill test dir green at build
- A10 [absent] covers: S3 · [absent] n/a · the router line either exists or the check fails — no third state
- A11 [who] covers: S3 · [who] n/a · SKILL.md has no actor semantics; the router only names the lane
- A12 [which] covers: S1 · the request does not say which evidence kinds an explore receipt may carry; taking: the existing ladder unchanged; the `sources` rung is `sources-receipt`'s scope, this task only references it forward -> cost: a dangling forward reference if that task is cut
- A13 [order] covers: S2, S4 · [order] n/a · lane entries and node conventions carry no ordering semantics
- A14 [when] covers: S2 · the request does not say when Explore wins over Task on a tie; taking: uncertainty dominates size — explore-first, then the informed Task -> cost: occasional double ceremony
- A15 [absent] covers: S2 · the request does not say what an explicit "research X" request with low apparent unknowns does; taking: the explicit ask wins — still Explore -> cost: none material
- A16 [who] covers: S4 · the request does not say who may consume a findings brief; taking: any later task via a `needs:` edge, unrestricted — findings are facts, not authority -> cost: none material
- A17 [which] covers: S3 · [which] n/a · the router line only names the lane; it selects no rows or cases
- A18 [when] covers: S4 · the request does not say when `## FINDINGS` must exist; taking: by the sufficiency gate, not at freeze — an explore starts with questions, not answers -> cost: none material
- A19 [order] covers: S3 · [order] n/a · a router mention carries no ordering semantics

## PLAN
contract: S1–S4 as `gives:` — one new guide file, two edited docs, one documented node convention; no engine edit, no new node type, no new verb
scope: add-method/skill/add/{phases/explore.md,intake.md,SKILL.md} → mirrored to .claude/skills/add and _bundled; checks in add-method/tests/skill/test_explore_lane.py
strategy: write the red suite first (this beat) → build explore.md (~90 lines) → add the intake lane (~15 lines) → compress SKILL.md depth-dial prose to fund the router line → sync the two mirror trees byte-for-byte → green
regression floor: add-method/tests/skill (all) + add-method/tooling/test_tree_parity.py stay green

## EDGES
- E1 explore.md references only wired verbs even in prose examples — the surface tests scan every ```bash block
- E2 SKILL.md at exactly 150 lines is a pass; 151 is the breach
- E3 a `#findings` fragment on a node with no `## FINDINGS` heading resolves to `edge_unresolved` (info) — the doc must say the gate, not the graph, is what demands the section

## CHECKS
- test_explore_guide_exists_within_budget · covers: M2 · explore.md exists in the canonical tree, ≤350 lines, and names all four loop stages
- test_explore_guide_keeps_floors · covers: R:FLOOR_DROP, A1 · explore.md states security HARD-STOP + the human freeze seam verbatim
- test_explore_guide_names_stop_conditions · covers: M2, A5 · both stop conditions present — sufficiency judgment + hard budget backstop
- test_intake_names_explore_lane · covers: M1 · intake.md carries an Explore lane section with routing criteria and the human veto
- test_router_names_explore_within_budget · covers: M3, R:BUDGET, E2, A9 · SKILL.md names the Explore lane AND stays ≤150 lines after the compression
- test_explore_guide_uses_only_wired_verbs · covers: R:PHANTOM_VERB, E1 · every `add <verb>` in explore.md — bash blocks included — is a real CLI dispatch verb
- test_findings_fragment_contract_documented · covers: M4, E3 · explore.md documents `## FINDINGS` and the `#findings` needs-edge consumption
- test_skill_bundle_matches_canonical · covers: M5 · canonical and `_bundled` skill trees byte-identical
- test_dogfood_skill_matches_canonical_when_present · covers: M5 · canonical and `.claude/skills/add` trees identical
- test_total_surface_within_budget · covers: R:BUDGET · total skill surface stays ≤ 1500 lines
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
