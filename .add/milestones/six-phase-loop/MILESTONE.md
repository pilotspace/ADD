# MILESTONE: Six-phase loop with bundle-owned subagents

goal: Merge specify+scenarios and verify+observe (8->6 phases), disclose phase guides into the lean roster's bundle agents so the orchestrator loads only SKILL.md, add per-phase persona presets + a build-entry spec echo
rationale: sub-milestone — the user's compress-steps + expert-subagent-per-step request, interview-confirmed 2026-07-14 (TRUE 8->6 merge · disclosure into bundle agents · presets · spec echo)
stage: mvp · status: active · created: 2026-07-13T17:03:37+00:00
release: 1.18.0
relations: <cross-MILESTONE edges — add header lines `depends-on:` / `extends:` / `relates-to:` with milestone slugs (comma-sep); omit if none. Non-blocking except depends-on; validated by `add.py check`>

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  <what this milestone delivers>
Out: <explicitly deferred — the anti-scope-creep list>

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Ground (current assets this builds on)
- 8-phase lifecycle (expectations-first, PR #145): setup · specify · scenarios · plan · tests · build · verify · observe; ONE freeze at plan->tests; compound ticks (call-floor 4/5) already collapse freeze->tests and build->verify->gate.
- Phase bundles exist in prose (SKILL.md table Bundle column: DIRECTION/BUILD/VERIFY, three-phase-flow milestone) but the ORCHESTRATOR still loads every phase guide inline.
- Lean 5-agent roster (add-design/add-build/add-verify/add-persona/add-advisor) spans bundles; dynamic teacher-grade personas infra shipped (PR #137); agents live in THREE trees incl _bundled.
- Read path after call-floor: SKILL.md 9498B + per-phase guide each phase (~33KB/task fast lane).
- Evidence for the spec-echo task: WM1 transcripts show drift starts at build entry (contract frozen, then built from memory).
- Human decisions recorded 2026-07-14 (AskUserQuestion): TRUE phase merge 8->6 · personas-per-phase on the lean roster (NOT a per-step agent rebuild) · build-entry spec echo YES · phase guides disclose INTO the bundle subagents, orchestrator loads SKILL.md only.

## Scope
IN: engine phase-list 8->6 (specify absorbs scenarios; verify absorbs observe) + section renumber + template updates + in-flight task migration; phase-guide re-cut to 6 files + pool re-anchor; bundle-guide disclosure into roster agents (orchestrator reads SKILL.md only); per-phase persona presets; build-entry spec echo; recipe/kickoff updates.
OUT: gate SEMANTICS (one recorded outcome, security HARD-STOP, tamper/scope guards — all unchanged) · the freeze position (plan->tests) · roster membership changes (stays 5) · stdout terseness · benchmark harness changes.

## Tasks (breadth-first; engine merges FIRST — guides/agents re-cut against the new truth)
- [x] phase-merge-specify   depends-on: none — scenarios fold INTO specify (§2 Given/When/Then becomes the §1 rules' scenario block; one drafting phase); engine PHASES list, section indices, advance/recipe paths, TASK.md.tmpl + fast twin; migration maps in-flight tasks (scenarios->specify) — the phase-index-vs-section bug class from expectations-first is the named trap
- [x] phase-merge-verify    depends-on: phase-merge-specify — observe folds INTO verify (§7 spec-delta capture becomes an optional post-gate block of §6; deltas/fold lifecycles unchanged, they read the file not the phase); gate stays the phase's one outcome; 6-phase list lands: setup · specify · plan · tests · build · verify
- [x] guide-recut           depends-on: phase-merge-verify — phases/*.md re-cut to 6 guides (1-specify absorbs 2-scenarios; 6-verify absorbs 7-observe); pools re-anchored (human-signed restructure, POOLS comments cite this milestone); orchestrator fast-lane read path <= 30KB finally lands
- [x] bundle-disclosure     depends-on: guide-recut — the orchestrator loads ONLY SKILL.md; each roster agent's prompt names + loads its bundle's guides (add-design <- specify+plan; add-build <- tests+build; add-verify <- verify); SKILL.md flow table routes to AGENTS for bundle work, guides stay readable inline for the no-spawn lane (inline remains first-class per the user's inline-over-heavy-spawns feedback)
- [x] persona-presets       depends-on: bundle-disclosure — per-phase teacher-grade persona preset lines in the three roster agent files (dynamic-personas infra); advisory, never lowers a gate
- [x] build-entry-spec-echo depends-on: phase-merge-verify — the tick INTO build (advance tests->build or freeze --cross chain) prints the §1 Must/Reject lines + frozen §3 contract summary (spec-in-context where drift starts; propose-not-impose, fail-open like the scope echo)

## Exit criteria (observable)
- [x] the 6-phase lifecycle is test-pinned end-to-end: new-task -> specify -> plan(freeze) -> tests -> build -> verify(gate) with compound ticks intact   (<- phase-merge-*)   (verify: test_phase_merge_specify.py + test_phase_merge_verify.py AdvanceAndGateTest; fence 3554 OK)
- [x] an in-flight 8-phase task migrates loud-and-safe (scenarios->specify, observe->verify) — test-pinned   (<- phase-merge-*)   (verify: test_phase_merge_verify.py LegacyStateTest — normalize-on-read, gate preserved)
- [x] 6 phase guides, pools green at re-anchored baselines, orchestrator fast-lane read path <= 30KB   (<- guide-recut)   (verify: test_guide_recut.py; phases pool 41605->40205 signed; SKILL.md 9442B + 1 guide/phase)
- [x] roster agent files name + load their bundle guides; SKILL.md carries no per-phase guide bodies   (<- bundle-disclosure)   (verify: test_bundle_disclosure.py — guide census + disclosure sentence + ceiling + x2 parity)
- [x] each of the 3 bundle agents carries per-phase persona preset lines   (<- persona-presets)   (verify: test_persona_presets.py — preset census, routing-first survives, never-lowers-a-gate)
- [x] the build-entry echo renders Must/Reject + contract summary; bare non-build ticks byte-identical — test-pinned   (<- build-entry-spec-echo)   (verify: test_build_entry_spec_echo.py 9 tests; self-proved live on the task's own re-cross)
- [x] floors untouched: full fence green, ENGINE_MD5 re-pinned, 3-tree parity, gate semantics byte-identical   (verify: fence 3554/3554 OK; ENGINE_MD5 bf89b033 @ build-entry-spec-echo; twin-parity tests green; zero tests weakened across 6 tasks)
- [x] (paid, human-gated) WM1 re-measure after merge: fidelity >= 0.97 held, calls <= 12   (verify: benchmark/results/2026-07-sixphase-remeasure.md — fidelity MET 0.98x3/0 regr/oracle 1.0; calls UNMET 20.7 mean, HUMAN-ACCEPTED-PARTIAL at close 2026-07-14 by Tin Dang — residuals are message-layer (double-init - re-cross - status re-reads - help), moved to the follow-on milestone)

## Risks
- The expectations-first migration class: phase-index vs §-section off-by-one (named trap in every merge task) · ~3500 fixtures pin phase sequences — merges are the two biggest test-ripple tasks this repo has attempted since flow-reorder · gate tamper tripwire fires if migration touches frozen §3s (recover via re-cross --by, precedent recorded).
