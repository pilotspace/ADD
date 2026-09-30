---
type: Task
title: Persona instructions match the schema commands references and authority they claim
status: done
depth: standard
kind: test
scope:
  - add-method/tests/skill
  - add-method/tests/skill/skill_budget.py
  - add-method/tests/skill/test_surface.py
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/tooling/test_tree_parity.py
  - add-method/tooling/templates/personas
  - add-method/src/add_method/_bundled/tooling/templates/personas
  - .add/tooling/templates/personas
  - add-method/skill/add/personas.md
  - add-method/skill/add/streams.md
  - add-method/skill/add/persona-author
  - add-method/src/add_method/_bundled/skill/add/personas.md
  - add-method/src/add_method/_bundled/skill/add/streams.md
  - add-method/src/add_method/_bundled/skill/add/persona-author
  - .claude/skills/add/personas.md
  - .claude/skills/add/streams.md
  - .claude/skills/add/persona-author
  - .add/personas
gives:
  - S1 the mechanical Persona node contract: `type: Persona`, `title:`, the seven routing/provenance slots, and the template-to-node mapping
  - S2 the closed `flow` and `task-kinds` vocabularies that the roster actually selects on
  - S3 every command in an ORIENT paragraph executes through the current `python3 .add/tooling/cli.py` entry point on a representative bundle
  - S4 resolvable full and shorthand teacher/source references, synchronized canonical/bundled/Claude skill copies, and synchronized source/package/live templates
  - S5 bounded authority language: the engine may read Persona frontmatter for routing and brief injection but never spawns or evaluates the lens, while persona advice never grants permission, lowers a gate, or replaces a human decision
generated: { by: add/3.6.0, at: 2026-09-14 }
verified:
  - { by: "plan:codex", at: 2026-09-14, act: freeze, authority: plan, direction: "sha256:15d79fc5bf887fe0", binding: "sha256:5b236f0e13444a03", gives: "sha256:2104e1f7bfb89628" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:deb648a95cfdf9f6" }
  - { by: "process:run", at: 2026-09-14, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/1.md }
  - { by: "agent:gpt-5.6-continuity-design", at: 2026-09-14, act: refute, authority: process, outcome: refuted, probes: 28, receipt: /tasks/persona-instruction-truth.d/runs/1.md, tier: T2, note: "retired or unqualified ORIENT commands escape extraction; author contract falsely says flow/task-kinds are unread and unwarned; seeding still teaches singular source; initialization prose falsely says no Persona nodes are seeded" }
  - { by: "plan:codex", at: 2026-09-14, act: refreeze, authority: plan, direction: "sha256:4754638433135d16", binding: "sha256:4d7ca83e0cec0cea", gives: "sha256:2104e1f7bfb89628" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:2ddf35547ceac967" }
  - { by: "plan:codex", at: 2026-09-14, act: refreeze, authority: plan, direction: "sha256:779027086d433df5", binding: "sha256:4d7ca83e0cec0cea", gives: "sha256:2104e1f7bfb89628" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:c18c9eb7b2ed3ffa" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:c18c9eb7b2ed3ffa" }
  - { by: "plan:codex", at: 2026-09-14, act: refreeze, authority: plan, direction: "sha256:869b6a9d8e69c724", binding: "sha256:4d7ca83e0cec0cea", gives: "sha256:2104e1f7bfb89628" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:75a76012c82a589b" }
  - { by: "process:run", at: 2026-09-14, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/2.md }
  - { by: "process:full-regression", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 1, receipt: /tasks/persona-instruction-truth.d/runs/2.md, tier: T1, note: "tooling templates differ from src/add_method/_bundled/tooling/templates; BundleParity.test_templates_bundle_matches_canonical fails after the scoped source-template edits" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:e873c65e41c8fdbf", binding: "sha256:4d7ca83e0cec0cea", gives: "sha256:2104e1f7bfb89628" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:40275831718902df" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/3.md }
  - { by: "agent:gpt-5.6-persona-v2-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 43, receipt: /tasks/persona-instruction-truth.d/runs/3.md, tier: T2, note: "persona guidance invents engine-checked body sections and underscore-file skipping, NO-EXEC falsely denies frontmatter reads, ORIENT extraction skips three commands, the live installed templates are stale, and mirror/source-resolution guards do not sweep their claimed surfaces" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:34c543bf2a23f738", binding: "sha256:4d7ca83e0cec0cea", gives: "sha256:28b7ebd5961daeaa" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:1160f3f0e75e87a4" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/4.md }
  - { by: "agent:gpt-5.6-persona-v3-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 24, receipt: /tasks/persona-instruction-truth.d/runs/4.md, tier: T2, note: "persona guide still invents engine-checked body sections, denies routing-vocabulary diagnostics and fallback when task-kinds is absent, and includes unqualified learn/fold commands in an ORIENT paragraph" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:6878dae9c8cfc8b0", binding: "sha256:60b3aed15d2d819b", gives: "sha256:28b7ebd5961daeaa" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:8a2f61975189652a" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/5.md }
  - { by: "agent:gpt-5.6-persona-v4-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 7, receipt: /tasks/persona-instruction-truth.d/runs/5.md, tier: T2, note: "off-index Persona still routes and reaches brief; doctor falsely diagnoses valid YAML list routing values; ORIENT section extractor misses commands after blank lines" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:5d71f3c5415d7993", binding: "sha256:caac6915b8d3ab50", gives: "sha256:28b7ebd5961daeaa" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:0a85f466766db553" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:0d85d5e21f99f5c3", binding: "sha256:caac6915b8d3ab50", gives: "sha256:28b7ebd5961daeaa" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:978b7f35f2867c29" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/6.md }
  - { by: "agent:gpt-5.6-persona-v6-fresh-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 1, receipt: /tasks/persona-instruction-truth.d/runs/6.md, tier: T2, note: "persona-author contract says the engine literally matches Persona body section names, but headingless Persona still routes and briefs without doctor findings" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:d29c574b3f43b558", binding: "sha256:f74837c0e944fff8", gives: "sha256:28b7ebd5961daeaa" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:a5b55c98cb4e897c" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/7.md }
  - { by: "agent:gpt-5.6-persona-v7-independent-refute", at: 2026-09-15, act: refute, authority: process, outcome: held, probes: 78, receipt: /tasks/persona-instruction-truth.d/runs/7.md, tier: T2, note: "78 bound tests including 11 disposable persona instruction probes held; reviewed engine, author guidance, templates, and mirrors; no model-effectiveness or external-provenance inference" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:d29c574b3f43b558", binding: "sha256:f74837c0e944fff8", gives: "sha256:28b7ebd5961daeaa" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:52c738ad6157cf3a" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/8.md }
  - { by: "agent:gpt-5.6-persona-v8-receipt-refute", at: 2026-09-15, act: refute, authority: process, outcome: held, probes: 78, receipt: /tasks/persona-instruction-truth.d/runs/8.md, tier: T2, note: "78/78 JUnit cases, all 12 frozen check IDs, 104 scope hashes, and five disposable runtime counterexample families held; receipt7/8 build hashes identical" }
  - { by: "agent:codex", at: 2026-09-15, act: gate, authority: process, outcome: PASS, receipt: /tasks/persona-instruction-truth.d/runs/8.md, brief: "sha256:a9f0caf6e33f0787" }
advised_by: method-steward
---
## CARD
goal: make every persona instruction mechanically true against the current ADD engine and its three shipped skill trees
why: schema, routing, command, source, and initialization prose can each look plausible while contradicting the engine that authors and reads Persona nodes
beat: done · next: add status

## RULES
<must>
- M1 the project-node schema is stated from `add.new`: frontmatter has `type: Persona` and `title:`; `vibe`, `flow`, `task-kinds`, `use-when`, `not-when`, `description`, and `sources` are named as slots with their actual optionality. Any template/example using `name` or singular `source` explicitly labels those as teaching input and states the conversion to `title`/`sources`.
- M2 `flow` is exactly `design | build | advisor | verify`, and `task-kinds` is exactly the engine's closed taxonomy (`feature | refactor | test | docs | ui | security | data | infra | release | integration | explore`). The canonical skill, bundled skill, Claude skill, templates, and examples cannot teach another value, deny doctor diagnostics for authored invalid values, or claim omitted `task-kinds` blocks routing when the engine treats absence as a broad fit. `doctor` and `persona_candidates` must agree on valid scalar and YAML-list forms of both keys.
- M3 every ADD CLI command in an ORIENT section or paragraph names a command that exists in the current CLI parser and executes from repository root against a representative ADD bundle, including commands after a blank line or wrapped onto continuation lines. The canonical form is `python3 .add/tooling/cli.py`; a retired `add.py` path or any unqualified backticked `add <verb>` is not an executable ORIENT contract. Non-ADD example commands remain project-specific advice, not ADD CLI claims.
- M4 every local teacher/source reference in project personas, templates, examples, and author guidance resolves to a shipped file or directory, including shorthand references that inherit the `personas-teacher/` root; every reference to a skill section or command resolves in all three skill trees.
- M5 persona language is advisory and bounded: the engine truthfully reads Persona frontmatter to present routing candidates and inject an already selected lens into a brief, but it never spawns, executes, or evaluates a Persona/body. A persona never authorizes a freeze/gate, lowers a security HARD-STOP, or substitutes for an explicit human decision. Body-section completeness and `_`-prefixed naming are authoring rules unless the engine actually diagnoses them. The index is an orientation catalogue; a Persona omitted there can still be discovered by graph-based routing and brief compilation.
- M6 the three skill trees remain byte-identical for the persona guide, streams guide, and complete persona-author tree; source persona templates remain byte-identical with both the Python package's bundled tooling templates and this repository's live `.add/tooling` templates used by the mandated entry point. Any prose growth is paid from the existing skill budget; this direction task does not re-pin or stamp it.
- M7 persona-author guidance states the current initialization behavior: `init` seeds every shipped starting-persona template, never overwrites an existing project persona, and reports what it newly seeded. The old 3.0 “no personas” and method-lenses-only rules are historical, because the approved current roster contains method and domain starting lenses that projects own and adapt. (from: current `_seed_personas` behavior and `/tasks/persona-tier-live.md` · fails-on: teaching authors to create a roster from nothing or reject templates init already installed)
</must>
<reject>
- R:PERSONA_SCHEMA a project Persona is documented as `name`/singular `source` only, or a teaching template's conversion is left implicit -> "PERSONA_SCHEMA"
- R:BAD_VOCABULARY a flow or task kind outside the engine's closed set is taught, an authored invalid value is called undiagnosed, absent task-kinds is called unroutable, or doctor misdiagnoses valid YAML lists that the selector routes -> "BAD_VOCABULARY"
- R:PHANTOM_ORIENT an ORIENT paragraph points at `add.py`, an absent subcommand/flag, or an unqualified backticked `add <verb>` even on a wrapped continuation line -> "PHANTOM_ORIENT"
- R:UNRESOLVED_REFERENCE a named local teacher file, directory, skill section, or command cannot be resolved -> "UNRESOLVED_REFERENCE"
- R:FALSE_AUTHORITY persona prose claims the engine never reads frontmatter, claims execution/evaluation/permission/gate weakening/human approval, assigns an unimplemented diagnostic to the engine, or claims index absence makes graph-based routing impossible -> "FALSE_AUTHORITY"
- R:TREE_DRIFT one shipped skill tree, source/package/live persona-template set, or its budget/pin owner diverges without a scoped, reviewed reason -> "TREE_DRIFT"
- R:STALE_INIT persona guidance says init seeds no personas, every roster node must be manually scaffolded, or domain starting lenses can never ship despite the current template set -> "STALE_INIT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2,S3,S4,S5 · the request names the method steward as author and the engine/agent/human as distinct authorities; taking persona text as an authority grant would weaken every published instruction surface -> reject false authority.
- A2 [which] covers: S1,S2,S3,S4,S5 · the sweep includes project Persona nodes, all nine source/package/live templates, every persona-author asset/reference, the persona and streams guides, complete ORIENT sections and paragraphs, initialization claims, doctor/candidate parity, and all three skill trees; taking only `.add/personas` would leave shipped teaching surfaces stale -> reject unresolved or drifting guidance.
- A3 [when] covers: S1,S2,S3,S4,S5 · truth is required at init, authoring, and orientation time on the current branch, while routing effectiveness and external provenance belong to later trials -> make only present-tense mechanism claims.
- A4 [absent] covers: S1,S2,S3,S4,S5 · an omitted optional slot/reference is legal only when the contract says optional; a missing required schema key, vocabulary, command, reference, initialization fact, or boundary is a finding -> do not invent defaults.
- A5 [order] covers: S1,S2,S3,S4,S5 · derive schema/vocabulary/init behavior from the engine, then execute commands and resolve references, then compare authority language and mirrors; otherwise prose can validate itself against its own stale claim -> checks follow that dependency order.
- A6 [experience] covers: S1,S2,S3,S4,S5 · the recipient is a future persona author or router working from a cold checkout; a plausible but non-executable command, stale init claim, unresolved source, or authority claim silently misroutes work -> every check names the concrete failure.
every `gives:` surface is swept on every dimension; none is retired. The new three-case red run is 3 failed/8 deselected; earlier receipts remain in the append-only record. No real model effectiveness or CI provenance is claimed.

## PLAN
contract: one exact instruction-truth guard file at `add-method/tests/skill/test_persona_instruction_truth.py`, plus this direction contract; doctor parity and prose/template fixes stay inside the listed scope, and the engine pin is re-aimed only with an explicit receipt
regression: affected · `python3 -m pytest -q add-method/tests/skill/test_persona_instruction_truth.py add-method/tests/engine/test_persona_routing_keys.py add-method/tests/skill/test_persona_contract_truth.py add-method/tests/skill/test_surface.py add-method/tests/skill/test_one_budget_one_guard.py add-method/tooling/test_tree_parity.py add-method/tests/skill/test_claimed_output_guard.py --junitxml=/private/tmp/persona-instruction-truth-v8.xml` · proves doc/doctor parity, the fixed ORIENT discovery, mirror/pin integrity, existing routing controls, and reported check IDs after the three-case red run
- O1 covers: M1,M2 · signal node schema and vocabulary assertions · window all listed skill trees/templates/personas · threshold zero stale claims · action refuse Build until the contract or source is corrected
- O2 covers: M3 · signal command discovery plus subprocess exit status on a representative bundle · window every ORIENT section and paragraph · threshold zero retired/unexecutable commands · action refuse
- O3 covers: M4,M5,M6 · signal resolved references, bounded authority language, and mirror equality · window all scoped copies · threshold zero unresolved/authority/tree violations · action refuse

Build boundary: locally implementable work covers deterministic schema/prose/reference/command checks, mirror parity, and the doctor routing-key normalizer shared with candidates. Real model routing quality, human judgment/trial outcomes, authenticated external CI provenance, package registry install/upgrade provenance, and any trial schema/security task remain outside this task and require their separately scoped work. Teaching templates retain `name`/`source` input and state the `name`→`title`, `source`→`sources` conversion; every ORIENT section uses the repository-root `python3 .add/tooling/cli.py` executable; NO-EXEC describes frontmatter reads without claiming the engine executes or evaluates a lens.
The scoped engine pin is re-aimed with its previous literal preserved in the annotation and verified source/bundled/live byte parity. No security-task or trial-schema edit is authorized. Skill prose stays within the existing budget and all three trees in scope.

## EDGES
- E1 a template may legitimately retain `name` as author-facing input only when the conversion to the actual `type: Persona`/`title` node is explicit; otherwise R:PERSONA-SCHEMA.
- E2 a command can parse successfully yet be unusable from a fresh bundle, and a line-only extractor can miss a wrapped command; paragraph-wide subprocess execution covers the working-directory and bundled-tooling boundary, not merely parser membership.
- E3 teacher references are off-build material and never runtime dependencies; resolution proves provenance honesty without making the engine load the corpus.
- E4 a persona can advise a security-sensitive task, and the engine may read its frontmatter into a brief, but neither event executes/evaluates the lens or clears the security HARD-STOP; authority checks cover this asymmetry.
- E5 mirrored skill or source/package/live tooling-template files can be individually plausible while disagreeing byte-for-byte; all parity sets are checked before any budget/pin decision.
- E6 a document can contain one canonical command while adjacent ORIENT instructions remain retired or unqualified; discovery enumerates every ORIENT section and command candidate before execution, including blank-line-separated bullets.
- E7 initialization guidance can be internally coherent and still contradict the templates the current engine actually seeds; the check compares prose with a real fresh bundle.
- E8 a project Persona with `flow: build` and no `task-kinds` can appear in the build candidate set for a declared `kind: security`; omission broadens fit while the security floor remains unchanged.
- E9 an index row can be absent while a valid Persona frontmatter node still appears in `persona_candidates` and `brief`; `doctor --sync` repairs orientation, not permission to route.
- E10 valid YAML-list routing values can fit candidates yet become false doctor findings if doctor stringifies their Python list representation; both readers must use the same normalized terms.
- E11 a Persona with no recommended body headings can still appear in candidates and briefs without a doctor body-section finding; the four-leg section list is author guidance, not a literal engine matcher.

## CHECKS
- test_persona_contract_names_the_engine_persona_node_shape · covers: M1,R:PERSONA_SCHEMA · proves the contract states the actual `type: Persona`/`title:` wire shape and maps teaching `name`/`source` inputs.
- test_persona_docs_enumerate_the_closed_routing_vocabularies · covers: M2,R:BAD_VOCABULARY,E8 · proves all three persona guides and author contracts enumerate the exact engine sets, diagnose invalid authored values, and describe omitted task-kinds as broad fit.
- test_doctor_and_candidates_agree_on_yaml_list_routing_keys · covers: M2,R:BAD_VOCABULARY,E10 · proves both readers accept valid YAML-list flow/task-kinds and doctor still diagnoses an invalid list member.
- test_persona_orient_commands_are_real_and_executable · covers: M3,R:PHANTOM_ORIENT,E2,E6 · proves every ADD command across each complete ORIENT section or paragraph uses the current CLI and exits successfully on a representative bundle.
- test_orient_extractor_keeps_blank_line_bullets · covers: M3,R:PHANTOM_ORIENT,E6 · proves a heading-separated ORIENT command remains in discovery.
- test_persona_references_resolve_to_local_teacher_material · covers: M4,R:UNRESOLVED_REFERENCE,E3 · proves full and shorthand project-persona, template, asset, and author-reference provenance resolves locally.
- test_persona_material_uses_the_engine_source_key_or_declares_conversion · covers: M1,M4,R:PERSONA_SCHEMA,E1 · catches singular `source:` teaching anywhere in persona-author material with no explicit conversion.
- test_persona_authority_boundary_is_explicit_in_all_skill_trees · covers: M5,R:FALSE_AUTHORITY,E4 · proves frontmatter really reaches briefs without body execution and every guide/project lens states the matching advice/NO-EXEC/gate boundary.
- test_index_absence_does_not_block_persona_routing · covers: M5,R:FALSE_AUTHORITY,E9 · proves an off-index node reaches candidates and brief while the author guidance describes the index as orientation only.
- test_body_section_names_are_author_reviewed_not_engine_matched · covers: M5,R:FALSE_AUTHORITY,E11 · proves a headingless Persona still routes and the author contract assigns heading completeness to the author.
- test_persona_skill_mirrors_are_byte_identical · covers: M6,R:TREE_DRIFT,E5 · proves canonical/bundled/Claude persona surfaces and source/package/live tooling templates agree completely.
- test_persona_initialization_claim_matches_seeded_templates · covers: M7,R:STALE_INIT,E7 · proves the author guidance and legacy guard match a real fresh bundle's seeded, project-owned roster and non-overwrite behavior.
red-first: three new bound checks failed before receipt 6; the fresh T2 review then exposed one more false body-heading claim despite 77 green scoped checks. Do not turn that red green by weakening a check.

## EVIDENCE
receipt: /tasks/persona-instruction-truth.d/runs/8.md · kind: test-ids · 78/78 reported · exit 0 · 2026-09-15
refute: held · 78 probe(s) · tier T2 · by agent:gpt-5.6-persona-v8-receipt-refute · against /tasks/persona-instruction-truth.d/runs/8.md · 2026-09-15 · 78/78 JUnit cases, all 12 frozen check IDs, 104 scope hashes, and five disposable runtime counterexample families held; receipt7/8 build hashes identical
gate: PASS · authority process · by agent:codex · receipt /tasks/persona-instruction-truth.d/runs/8.md · 2026-09-15

## LESSONS
- The generic engine writes Persona `type`/`title` while authoring templates currently teach `name`/`source`; keep the conversion explicit before changing either surface -> add learn method-steward
- A narrow green can hide adjacent contradictions; enumerate command candidates and compare initialization prose with a fresh bundle before calling instruction truth held -> add learn method-steward
- none filed — no lesson cites /tasks/persona-instruction-truth.md (add learn <lens> "<lesson>" --evidence /tasks/persona-instruction-truth.md)
