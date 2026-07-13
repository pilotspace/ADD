# MILESTONE: Call floor: drain the measured residual waste

goal: Close the gap the WM1 re-measure named: mean engine calls 18.7 -> ~12 and always-loaded read burden -> <=30KB, floors untouched — every lever engine-mechanical or additive, none prose-only
rationale: sub-milestone — human 'fix all' on the assessed levers 2026-07-13; every lever is evidence-traced to a measured residual in the WM1 re-measure; extends ceremony-to-effort's open meter criteria
stage: mvp · status: active · created: 2026-07-13T15:52:21+00:00
release: pending
extends: ceremony-to-effort

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  message/engine mechanics for the 5 measured residuals — init resume pointer · new-milestone lane nudge · scope coverage hint at freeze · opt-in compound ticks (freeze --cross · gate-from-build) + recipe update · SKILL.md orient split (always-loaded read <=~8K)
Out: gate-semantics changes (freeze refusal etc. — separate re-intake) · default tick sequences (3488 fixtures pin them; compression is OPT-IN + recipe-advertised) · stdout terseness · agent-side prompting (wrapper text is the benchmark's, not the method's)

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Ground
Evidence = the ceremony-to-effort WM1 re-measure (benchmark/results/2026-07-ceremony-remeasure.md,
runs ceremony-r1..r3): mean 18.7 engine calls (bar <=12) · 134t/$3.51 (bar 77.7t/$2.97) · fid 0.98 ·
0 regressions. Residual anatomy, per rep: double-init +2 (arm setup already init'd; agent re-inits,
eats `already initialised`) · milestone bait r1 +9-10 (3x new-milestone despite the oneshot wrapper) ·
re-cross repairs x2 (declared scope too NARROW — tokens resolved [ok] but the build touched Touches
paths outside them; NOT the dead-token class scope-echo already renders) · status re-reads x3 ·
--help ~1. Read burden: fast lane 37KB, SKILL.md 12.8K = the dominant always-loaded read.
Oneshot lane floor today = 8-9 calls, of which freeze->tests and build->verify->gate are pure ticks
with no work between: compressible by OPT-IN flags (default sequences byte-identical — 3488 fixtures
pin them; the kickoff recipe advertises the compressed forms).

## Shared decisions & glossary deltas   (living — every task must honor these)
- <cross-cutting rule, named from GLOSSARY.md>

## Shared / risky contracts (freeze these first)
- <contract name> -> owning task <slug>

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] init-resume-pointer   depends-on: none — the `already initialised` refusal gains a resume pointer (status), so the observed double-init dead-ends in one call; dup-failure hint covers the retry
- [ ] milestone-lane-nudge  depends-on: none — new-milestone success output gains one advisory line naming the oneshot lane for single-task work (the bait point, where r1 lost 9-10 calls)
- [ ] scope-coverage-hint   depends-on: none — freeze's scope echo ALSO lists §3 Touches paths OUTSIDE the declared scope (`note: ... outside the declared scope`) — the too-narrow class behind the re-cross repairs; propose-not-impose
- [ ] compound-ticks        depends-on: none — OPT-IN `freeze --cross` (stamp then land in tests) + `gate <outcome>` accepted at build (auto-cross build->verify, then record); defaults byte-identical; the new-task recipe advertises the compressed forms (oneshot lane 8-9 -> 6-7 calls)
- [ ] skill-orient-split    depends-on: none — SKILL.md keeps ONLY the orient path (~8K); intake summary + beyond-the-bundle + depth-by-stage move to an on-demand guide; pools re-anchored (human-signed restructure); fast-lane read path <=30KB

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `init` on an initialised project points at `status` in the same refusal — test-pinned   (<- init-resume-pointer)
- [ ] `new-milestone` output names the oneshot lane — test-pinned   (<- milestone-lane-nudge)
- [ ] a freeze whose §3 Touches cite paths outside the declared scope prints the coverage note; TASK.md untouched — test-pinned   (<- scope-coverage-hint)
- [ ] `freeze --cross` lands in tests · `gate PASS` from build records after auto-cross · bare defaults byte-identical · the recipe prints the compressed forms — test-pinned   (<- compound-ticks)
- [ ] SKILL.md <= ~8.5K with the orient path intact; moved content reachable on demand; all parity/pool fences green; fast-lane read path <= 30KB — test-pinned   (<- skill-orient-split)
- [ ] floors untouched: full suite green, ENGINE_MD5 re-pinned, twin parity holds   (<- all)
- [ ] (paid, human-gated) next WM1 re-measure: mean calls <= 12 on recipe-following reps   (<- all)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
