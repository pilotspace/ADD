---
type: Task
title: streams.md: free fan-out for read-only beats; waves reserved for builds
status: done
depth: standard
milestone: dynamic-flow
scope:
  - add-method/skill/add
  - .claude/skills/add
  - add-method/src/add_method/_bundled/skill/add
  - add-method/tests/skill
gives:
  - S1 `streams.md` § read fan-out — read-only work (grounding · residue lenses · explore research) fans out to N parallel readers with no wave and no worktree
  - S2 the read/write boundary — findings are facts and merge freely; builds carry implicit decisions and keep the wave machinery whole
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "Tin Dang", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:4d81bd7055c752a3" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:fb5be1c347396c9a" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/read-fanout.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/read-fanout.d/runs/1.md, brief: "sha256:fb5be1c347396c9a" }
---
## CARD
goal: parallel reads are free — grounding, residue lenses and explore research fan out with zero wave ceremony — while parallel writes keep every proof the wave machinery provides
why: the wave's disjoint-scope proof exists to serialize DECISIONS; imposing it on fact-gathering taxes the safe case and discourages the fan-out that research wants

## RULES
<must>
- M1 `streams.md` documents read fan-out: N parallel read-only delegates need no wave plan, no worktree, no disjoint-scope proof
- M2 the boundary is stated with its reason: reads return facts and facts merge; builds carry implicit decisions, so write parallelism keeps the wave's disjoint-scope machinery unchanged
- M3 the floors are restated for the fan-out: no reader owns a gate, findings fold back through the main thread, and a security finding from ANY reader is a HARD-STOP
- M4 all three git-tracked skill trees stay identical
</must>
<reject>
- R:WAVE_WEAKENED the wave section's write-safety is not touched — no wording change lets a WRITING stream skip the wave, the worktree, or the disjoint-scope refusals -> "WAVE_WEAKENED"
- R:BUDGET streams.md over 350 lines or total surface over 1500 -> "BUDGET"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who spawns the readers; taking: the main thread, exactly as single-advisor delegation today — selection and fold stay its judgment -> cost: none material
- A2 [who] covers: S2 · the request does not say who classifies a beat as read-only; taking: the main thread, by what the delegate is ASKED to do — a reader given edit instructions is a mis-spawn, and the guide says so -> cost: a writing delegate escapes the wave · probe: streams.md pins read-only to the spawn instruction
- A3 [which] covers: S1 · the request does not say which beats qualify; taking: grounding, residue lenses, explore research, and any advisory read — the named set plus the read-only test -> cost: none material
- A4 [which] covers: S2 · the request does not say which side a read-then-write delegate falls on; taking: write — one write instruction anywhere makes the whole delegate wave-gated -> cost: none material · probe: streams.md states the one-write-taints rule
- A5 [when] covers: S1 · the request does not say when readers may run; taking: any beat, any time, concurrently with a build — reads cannot race a writer that owns its scope -> cost: a reader observes a mid-build tree; findings must carry their read time
- A6 [when] covers: S2 · [when] n/a · the boundary is definitional, not temporal
- A7 [absent] covers: S1 · the request does not say what no-findings means; taking: a reader returning nothing folds nothing — silence from a reader is a result, never a block -> cost: none material
- A8 [absent] covers: S2 · [absent] n/a · the boundary has no absent case — every delegate is on one side by A4
- A9 [order] covers: S1 · the request does not say fold order; taking: fold as they return; contradictory findings surface to the human, the same divergence rule join already uses -> cost: none material
- A10 [order] covers: S2 · [order] n/a · a definitional boundary carries no ordering semantics

## PLAN
contract: S1–S2 as `gives:` — one edited doc (`streams.md`), no engine edit; the wave section's write-safety text untouched
scope: add-method/skill/add/streams.md → mirrored to the two twin trees; checks in add-method/tests/skill/test_read_fanout.py
strategy: red suite first → add the read fan-out section to streams.md (free-reads rule · the boundary + reason · floors) placed before the Parallel-streams section → sync twins → green
regression floor: add-method/tests/skill (all) + add-method/tooling/test_tree_parity.py stay green

## EDGES
- E1 the wave section (R:INTRADEP · R:OVERLAP · R:CYCLE refusals) must survive verbatim — the fan-out text may reference it, never reword it
- E2 streams.md is 166 lines — the addition must stay well under 350

## CHECKS
- test_streams_documents_read_fanout · covers: M1, A2 · a read fan-out section exists — no wave, no worktree for read-only delegates, read-only pinned to the spawn instruction
- test_streams_states_boundary_with_reason · covers: M2, A4 · facts-merge vs decisions-serialize is stated, with the one-write-taints rule
- test_streams_fanout_keeps_floors · covers: M3 · no reader gates, fold through the main thread, security HARD-STOP from any reader
- test_wave_refusals_survive_verbatim · covers: R:WAVE_WEAKENED, E1 · the three wave refusal codes and the disjoint-scope invariant text are untouched
- test_streams_within_budget · covers: R:BUDGET, E2 · streams.md ≤ 350 lines
- test_skill_bundle_matches_canonical · covers: M4 · canonical and bundled trees byte-identical
- test_dogfood_skill_matches_canonical_when_present · covers: M4 · canonical and dogfood trees identical
- test_total_surface_within_budget · covers: R:BUDGET · total skill surface ≤ 1500 lines
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
