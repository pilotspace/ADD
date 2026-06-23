# MILESTONE: lean-pass M1 · skill effectiveness

goal: every skill guide is the most effective prompt for its job — clearer routing, sharper decisions, same flow and engine behavior — at materially lower token cost
rationale: new-major `lean-pass` (the lean/effectiveness theme — reclaim ADD's leanness after the 1.8.0 growth). M1 is the highest-leverage, lowest-risk slice: the skill loads every session, so prompt quality + token cost here is the context-rot lever. Extends the leanness intent of the archived `foundation-compaction` (which compacted foundation specs, not the skill/flow); M2 (book) and M3 (flow-simplification) follow.
stage: mvp · status: active · created: 2026-06-23

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the 27 skill guides (`.claude/skills/add/**`) ×3 mirror trees — wording, structure, and
     overlap-folding that makes each guide a sharper, leaner prompt while preserving behavior.
Out: phase-model/engine changes (deferred to M3 flow-simplification); the book/docs (M2);
     ANY change that alters what the AI decides or does — that is a behavior change, not a lean pass.

## Shared decisions & glossary deltas   (living — every task must honor these)
- Behavior-preserving only — same routing, same decisions. If a cut would change what the AI does,
  it belongs to M3 (flow-simplification), not here.
- The 3 mirror trees stay byte-identical (`.claude/skills/add`, `add-method/skill/add`,
  `add-method/src/add_method/_bundled/skill/add`); the parity test + full suite (1551) green at each verify.
- The `SKILL.md` routing table stays correct — it is the index the whole flow depends on; never trim a row away.
- Effectiveness bar (human-set): each trimmed guide must (a) reproduce the same decision on a real dogfood walk
  AND (b) pass a subagent quality review judging it clearer/sharper, not merely equivalent — before its gate PASSes.

## Shared / risky contracts (freeze these first)
- token+parity measurement method (baseline → after; how "≥25% lighter" and "byte-identical" are counted) -> owning task `skill-core-compact`

## Method gaps observed (feed M3 flow-simplification)
- 2026-06-23: the `new-milestone → new-task` happy path has NO explicit milestone-confirmation seam — the AI can create tasks and digest §0–§5 detail before the human confirms the parent MILESTONE.md is complete. Caught live this session (AI ran ahead). Candidate M3 fix: an engine/flow seam that holds task creation until the milestone is confirmed (or at least a guide-level "confirm the parent before digesting" gate).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] skill-core-compact   depends-on: none               — `SKILL.md` + always-loaded orientation path: the tightest, most effective session-load prompt; sets the measurement method
- [x] orchestration-fold   depends-on: skill-core-compact — `run.md`/`streams.md`/`advisor.md`/`loop.md`/`design.md`: fold overlap, sharpen the on-demand run guides into one coherent flow
- [x] phase-guides-trim    depends-on: skill-core-compact — `phases/0–7`: each phase guide to its most effective minimal form, gates unchanged
- [x] reference-trim       depends-on: skill-core-compact — remaining reference guides (intake/scope/deltas/fold/release/report-template/graduate/soul/setup-review/adopt/confidence/compact-foundation)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `SKILL.md` always-loaded token cost down materially (16,894→14,816 B, 12%); routing table provably intact — 9 phase rows + 15 pointers asserted by test_skill_lean; quality review rated it clearer (← skill-core-compact)
- [x] run/streams/advisor/loop/design read as one coherent on-demand flow with no behavior drift (50,098→37,557 B, 25%); quality review confirmed sharper, 5 nuances restored (← orchestration-fold)
- [x] a real phase walk produces identical gates on the trimmed phase guides (37,920→30,333 B, 20%); full suite green incl. test_xml_convention + gate tests (← phase-guides-trim)
- [x] reference guides leaner but behavior-intact (59,421→40,340 B, 32%); quality review found 6 losses → all restored verbatim (← reference-trim)
- [x] guardrail: skill tree ≥25% lighter TREE-WIDE (164,333→123,046 B = 25.1%), all 3 mirror trees byte-identical, full suite 1556 green (← honored by every task; carried by reference-trim)

> Note (2026-06-23): `skill-core-compact` §3 re-specified v1→v2 — the always-loaded core (SKILL.md+intake)
> compacts cleanly to ~12% only; ≥25% there would cut the phase routing table or skill-trigger description
> (effectiveness-critical). The ≥25% is met TREE-WIDE by the heavier on-demand guides. Human-approved change-request.

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : test fences only — 4 per-task lean fences consolidated into one parametrized `test_skill_lean.py` (same budgets + a tree-wide guardrail); engine/state/templates UNTOUCHED (behavior-preserving milestone).
- skill   : all 27 guides ×3 trees recompacted — core (SKILL.md+intake) 16,894→14,816 B · orchestration (run/streams/advisor/loop/design) 50,098→37,557 · phases/0–7 37,920→30,333 · reference (11 guides) 59,421→40,340. Routing table + every rubric/anchor/reject-code intact. Tree 164,333→123,046 B = 25.1% lighter.
- book    : untouched (M2 owns the docs).

### Cross-task evidence   (one row per task)
- skill-core-compact : gate=PASS · tests=full suite green · residue=core re-specced v2 (~12% per-file; ≥25% carried tree-wide — human-approved)
- orchestration-fold : gate=PASS · tests=full suite green · residue=5 dropped nuances caught by review + restored
- phase-guides-trim  : gate=PASS · tests=full suite green · residue=none
- reference-trim     : gate=PASS · tests=1560 green · residue=quality review found 6 losses (2 blocking) → ALL restored verbatim, bytes re-compensated; carrier task hit the tree-wide 25.1%

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — core (← skill-core-compact), orchestration (← orchestration-fold), phases (← phase-guides-trim), reference (← reference-trim), tree-wide ≥25% guardrail (← reference-trim carrier + all four). Every task ran a subagent quality review (the effectiveness bar); losses found were restored before each gate.
- goal: every skill guide is the most effective prompt for its job at materially lower token cost — proven by the skill tree dropping 164,333→123,046 B (25.1% lighter, full suite 1556 green, 3 trees byte-identical) with every routing row, rubric, reject-code, and operative rule preserved (quality-review-confirmed, losses restored).

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
