---
type: Task
title: domains.md — the checker recipe, floor mapping, lens re-author
status: done
depth: standard
sensitivity: architecture
milestone: all-domain-evidence
scope:
  - add-method/skill/add/domains.md
  - add-method/tests/skill
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
gives:
  - S1 the domain-checker recipe — how a non-code domain earns a bound receipt
  - S2 the floor-vocabulary map — a domain's own word routed onto an existing floor
  - S3 the lens re-author table — how a domain bundle gets its 5-DD framing
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:6ee899f76dc53453" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:95d062f0525ce67c" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/domain-evidence-recipe.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:4f032c462e6b2137" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:bf0f5b1e387fee35" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/domain-evidence-recipe.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: plan, outcome: HARD-STOP, receipt: /tasks/domain-evidence-recipe.d/runs/2.md, brief: "sha256:bf0f5b1e387fee35", reason: "architecture residue: adding domains.md to the canonical tree broke both mirror-parity tests; the mirror trees are outside the frozen scope, so the fix is a change-request back to Direction" }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:c3f7f6c1a2c2dca5" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:73262b6fa07a16ab" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/domain-evidence-recipe.d/runs/3.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: plan, outcome: PASS, receipt: /tasks/domain-evidence-recipe.d/runs/3.md, brief: "sha256:73262b6fa07a16ab" }
---
## CARD
goal: a loaded-on-demand ref that makes ADD's existing trust spine reachable from a non-code domain
why: the capability is already there and invisible — nothing tells an agent it may WRITE a checker instead of FIND a runner
beat: done · next: add status

## RULES
<must>
- M1 the recipe must yield a receipt at `kind: test-ids` with every `covers:` referent bound, demonstrated by executing it end-to-end on a non-code domain node — never asserted in prose
- M2 every floor the map targets must be one of `security · data · architecture`, and a domain word must route to a floor no weaker than its own stakes imply
- M3 `domains.md` must exist and leave total skill surface within its 1500-line pin
- M4 the ref must land byte-identical in ALL THREE skill trees — canonical, package payload and dogfood mirror. Added at the third freeze: the architecture residue lens found that shipping it to one tree alone broke both mirror-parity tests, and the first scope was narrower than the change's real blast radius
</must>
<reject>
- R:NEWFLOOR introducing a floor name outside `security · data · architecture` -> "NEWFLOOR"
- R:GATEBUY showing any path to a verdict on weaker evidence than the code path takes — a pack configures what is AUTHORED, never what PASSES -> "GATEBUY"
- R:PHANTOMPROFILE instructing `add init --profile <x>` for any `x` the engine does not ship -> "PHANTOMPROFILE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say whether the AI may author the threshold it is then judged against; taking "yes, because the threshold lives in the frozen RULES the human approves, not in the checker" · found: the live recon node carried `M1 variance <= 0.5% of gross` in frozen RULES and the checker only compared against it (evidence: scratchpad/dom/.add/tasks/recon.md + runs/1.md, kind test-ids) -> if wrong, the AI marks its own homework and the receipt is theatre
- A2 [which] covers: S1 · the request does not say which domains the recipe claims; taking "only those that can state a machine-comparable threshold or a resolvable reference — taste-quality domains are named as out" -> if wrong, ADD overclaims and a brand-voice task ships a vacuous green
- A3 [when] covers: S1 · n/a · the recipe carries no temporal boundary; it rides the loop's existing beats
- A4 [absent] covers: S1 · the request does not say what happens when a domain has no digestible file; taking "freshness degrades to mtime and the receipt says so out loud" -> if wrong, a domain user believes they have stale-green protection they do not have
- A5 [order] covers: S1 · n/a · the recipe's steps are ordered by the beats they sit in, not by a rule of its own
- A6 [who] covers: S2 · n/a · floors are computed by the engine from `sensitivity:`; no actor chooses one
- A7 [which] covers: S2 · the request does not say whether the word list is exhaustive; taking "a closed starter set, explicitly extensible, never complete" -> if wrong, a reader treats an absent word as evidence of no floor
- A8 [when] covers: S2 · n/a · a floor binds at gate wherever the word appears; the map adds no timing
- A9 [absent] covers: S2 · the request does not say what floor an unmapped domain word takes; taking "the closed-floor rule already answers it — when in doubt, size up" -> if wrong, an unmapped sensitive word silently lands at `process`
- A10 [order] covers: S2 · n/a · the map is a lookup; no entry precedes another
- A11 [who] covers: S3 · n/a · the agent re-authors the lenses, as it authors any bundle content
- A12 [which] covers: S3 · the request does not say which lenses get rewritten; taking "all four `## Now` lines the `doc` profile ships" -> if wrong, a half-framed bundle gets cited by a frozen contract
- A13 [when] covers: S3 · the request does not say when re-authoring happens; taking "immediately after `init`, before the first task is created" -> if wrong, a contract freezes against code-framed lenses
- A14 [absent] covers: S3 · the request does not say what happens when a human already edited a spec; taking "never clobber — `init`'s own rule is that a human's file outranks a template" -> if wrong, human authoring is destroyed silently
- A15 [order] covers: S3 · n/a · lens order binds nothing

## PLAN
contract: one loaded-on-demand ref publishing three sections, proven by a dogfood test that EXECUTES the recipe rather than pinning its phrases
strategy: write the dogfood test first (red — the ref does not exist), then author `domains.md` until it goes green. Every check asserts the file exists BEFORE asserting anything about its content — a "must never contain X" test passes vacuously on a missing file, which is the assert-nothing trap the method warns about.
scope: add-method/skill/add/domains.md, add-method/tests/skill

## EDGES
- E1 a domain with no digestible artifact — the recipe must say the freshness degrade out loud, not omit it
- E2 a domain word the map does not carry — must route to size-up, never to silence

## CHECKS
- test_recipe_earns_bound_test_ids · covers: M1 · the recipe, run end-to-end on a non-code domain node, records kind test-ids with every covers referent reported passing
- test_floor_map_targets_only_existing_floors · covers: M2 · every floor named as a target resolves to security, data or architecture
- test_domains_exists_within_surface_budget · covers: M3 · the ref exists AND the surface stays within its pin — existence is what makes this red before the build
- test_introduces_no_new_floor_name · covers: R:NEWFLOOR · no floor-shaped token outside the closed three
- test_recipe_buys_no_gate · covers: R:GATEBUY · the ref names no weaker-evidence route to a verdict
- test_names_no_phantom_profile · covers: R:PHANTOMPROFILE · every --profile it instructs is one the engine ships
- test_states_freshness_degrade · covers: E1 · the ref says the mtime degrade out loud
- test_unmapped_word_routes_to_size_up · covers: E2 · an unmapped domain word routes to size-up, never to silence
- test_skill_bundle_matches_canonical · covers: M4 · the package payload tree matches canonical
- test_dogfood_skill_matches_canonical_when_present · covers: M4 · the dogfood mirror matches canonical
red-first: every check MUST fail first — EXCEPT the two E-checks, added at the second freeze after the gate exposed E1/E2 as unbound referents. Their behavior already shipped, so they are regression guards, not test-driven. Recorded here rather than manufactured red by deleting working prose and restoring it.
citation form: BARE test names. The first freeze cited `path.py::name`, which `cite_hits` resolves neither as a qualified ID nor as a bare name, so nothing bound and the gate refused all eight referents.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
