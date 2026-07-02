# MILESTONE: Advisor-Gated Autonomy

goal: Make auto+parallel a first-class, persisted, advisor-guarded run mode so high-speed builds stay safe without a human on every step
rationale: sub-milestone (intake) — extends the v6 dynamic-run/autonomy-dial + v7 auto-default + the team-collaboration streams/waves work, and UPGRADES (not duplicates) the existing refute-read seam; depends-on nothing new. No existing or archived milestone delivers advisor-gating or run-mode persistence, so not a duplicate_goal.
stage: mvp · status: active · created: 2026-06-29T03:00:09+00:00
release: 1.15.0

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  persist the auto+parallel run mode as machine state set at setup and read by status/guide/waves · an explicit setup-phase run-mode CHOICE (auto+parallel vs conservative) that writes that persisted home · a persisted SNAPSHOT of the computed task DAG plan (waves · critical path · tiers) with a freshness check vs live edges · a `sensitivity:` header dimension the human declares at freeze · a tier-aware single advisor (3-lens sequential checklist) reviewing every auto-pass · a per-phase advisory subagent-spawn hint · audit measures for advisor coverage + mis-tier + author-review · relax of the high-risk guard for mechanical-high-risk under a binding advisor verdict · docs/glossary/book alignment.
Out: perspective-diverse advisor PANEL (single advisor only this milestone) · the engine ever SPAWNING a subagent (stays orchestrator-side, always) · auto-classifying sensitivity (the human always declares it) · advisor-gating for SECURITY or sensitive scope (never — human floor) · a new autonomy LEVEL name (reuse auto/conservative/manual) · cross-runner spawn adapters beyond the documented Claude Code reference.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Engine never spawns.** The advisor, the worker, and the spawn-hint are all orchestrator-side; the engine only RECORDS verdicts and MEASURES/AUDITS them. (honors run.md / advisor.md / streams.md)
- **Security is HARD-STOP + human in EVERY tier.** The risk-tiering only ever routes NON-security high-risk; no tier and no advisor verdict auto-passes a security finding.
- **Persist only what you gate or audit.** `run_mode` (autonomy + streams posture) and `sensitivity` persist (HOME is an open spec decision — a PROJECT.md declaration mirroring autonomy vs a state.json field). **GROUNDING CORRECTION:** autonomy already persists in PROJECT.md (read live by `_project_autonomy`), NOT state.json as first assumed — only the *streams posture* is genuinely unpersisted.
- **DAG: edges are truth, the plan is a snapshot.** The dependency *edges* stay the source of truth (state.json `depends_on`) and the *schedule* stays recomputable by `add.py waves`; `persist-dag-plan` materializes a SNAPSHOT of the computed plan as a committed/auditable artifact — never the authority — with a freshness check vs live edges (drift → stale flag). Persisting a recomputable projection is the design tension that task must resolve at its freeze.
- **Measure before relax.** The audit measures (`advisor-verdict-audit`) ship BEFORE the guard relax (`advisor-gate-relax`) — earn the autonomy with instrumentation first.
- **This milestone is risk: high + method-defining** → every task builds `conservative` / human-gated. You cannot auto-gate the feature that relaxes auto-gating (dogfood).
- New glossary terms: `run_mode` (persisted autonomy+streams) · `sensitivity` (header dimension: security|data|architecture|mechanical) · `advisor-gated auto` (mechanical-high-risk auto-pass under a binding advisor verdict) · `3-lens sequential checklist` · `step-spawn-hint`.

## Shared / risky contracts (freeze these first)
- persisted `run_mode` state shape (autonomy + streams; setup-written, status/guide/waves-read) -> owning task `persist-run-mode`
- `sensitivity` header schema (enum + parser + validator) -> owning task `risk-sensitivity-taxonomy`
- advisor verdict record shape in §6 (binding vs advisory · the 3 lenses · residue) -> owning task `advisor-review-step`
- the relaxed `unguarded_high_risk_auto` predicate (mechanical + advisor-PASS + no-residue) -> owning task `advisor-gate-relax`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] persist-run-mode          depends-on: none                                    — persist the auto+parallel run mode (autonomy already in PROJECT.md; add the missing STREAMS posture) + surface the combined run_mode in status/guide/waves (no more prose-only streams).
- [x] risk-sensitivity-taxonomy depends-on: none                                    — add a `sensitivity:` dimension (security|data|architecture|mechanical) to the TASK.md header + parser/validator + status/check surfacing; human declares at freeze; engine never classifies.  [DONE — base closed enum]
- [ ] sensitivity-glossary       depends-on: risk-sensitivity-taxonomy               — (added 2026-06-29, user request) make the taxonomy PROJECT-EXTENSIBLE: `_project_sensitivity_values` = base ∪ domain classes from GLOSSARY.md `## Sensitivity classes`; freeze/status validate against the union; init seeds the section; a new skill guide + status/check nudge. Base four stay universal.
- [ ] persist-dag-plan          depends-on: none                                    — materialize a SNAPSHOT of the computed task DAG plan (waves · critical path · tiers) as a committed/auditable artifact with a freshness check vs live `depends_on` edges (drift → stale); live `waves` recompute stays the source of truth.
- [ ] setup-run-mode-prompt     depends-on: persist-run-mode                        — update the setup phase (phases/0-setup.md + engine support) to explicitly ASK the human to choose the run mode (auto+parallel vs conservative) and persist the answer via persist-run-mode's home; EOF-tolerant, byte-identical non-interactive default.
- [ ] advisor-review-step       depends-on: risk-sensitivity-taxonomy               — upgrade the refute-read into a tier-aware SINGLE advisor running a 3-lens sequential checklist (security→concurrency→architecture) on EVERY auto-pass; verdict BINDING for mechanical-high-risk, advisory elsewhere.
- [ ] step-spawn-hint           depends-on: persist-run-mode, risk-sensitivity-taxonomy — engine emits a per-phase advisory subagent-spawn hint (idiom + tier) in status/guide, keyed off run_mode + risk; advisory only, never spawns (mirrors the `waves` tier hint).
- [ ] advisor-verdict-audit     depends-on: advisor-review-step                      — `add.py audit` MEASURES (not blocks): advisor verdict recorded on every auto-pass · reviewer ≠ author · residue-found-on-mechanical = mis-tier flag.
- [ ] advisor-gate-relax        depends-on: advisor-verdict-audit, risk-sensitivity-taxonomy — relax `unguarded_high_risk_auto` so `risk:high` + `sensitivity:mechanical` + recorded advisor-PASS + no-residue auto-completes via `gate PASS`; sensitive + any security still escalate.
- [ ] docs-align                depends-on: advisor-gate-relax, step-spawn-hint      — glossary + book chapter on risk-tiered advisor-gated autonomy + the new `run_mode`/`sensitivity` header fields + a SKILL.md pointer.

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py status` shows the persisted run_mode (autonomy + streams posture), with the streams posture read from its persisted home (not prose-only)   (← persist-run-mode)   (verify: `add.py status` prints `run mode: parallel + auto`)
- [x] a task header declares `sensitivity:`; status/check surface it; an invalid value is rejected                  (← risk-sensitivity-taxonomy)   (verify: test_sensitivity_taxonomy)
- [x] a persisted DAG-plan snapshot exists and `add.py` surfaces it; changing a `depends_on` edge marks the snapshot stale vs the live edges   (← persist-dag-plan)   (verify: test_persist_dag_plan)
- [x] the setup phase asks the human to choose run mode (auto+parallel vs conservative) and persists the answer; non-interactive setup stays byte-identical to today   (← setup-run-mode-prompt)   (verify: test_setup_run_mode)
- [x] every auto-PASS records a single-advisor 3-lens verdict in §6; on mechanical-high-risk it gates, elsewhere it is advisory   (← advisor-review-step)   (verify: test_advisor_review_step)
- [x] `add.py status`/`guide` prints a per-phase spawn hint (idiom + tier) for the active phase, and nothing where delegation doesn't fit (e.g. contract)   (← step-spawn-hint)   (verify: test_step_spawn_hint)
- [x] `add.py audit` flags a missing advisor verdict, an author-reviewed verdict, and a mechanical task with advisor-found residue — measure only, no block   (← advisor-verdict-audit)   (verify: test_advisor_verdict_audit)
- [x] a `risk:high` + `sensitivity:mechanical` task with a recorded advisor PASS + no residue auto-completes; a `sensitivity:security` task (or any residue) still refuses/escalates   (← advisor-gate-relax)   (verify: test_advisor_gate_relax)
- [x] glossary + book + headers + SKILL.md document risk-tiered advisor-gated autonomy and the new header fields   (← docs-align)   (verify: test_docs_align)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py — `streams` cmd + `_project_streams` (run_mode persist) · `sensitivity:` enum + parser/validator + project-extensible `_project_sensitivity_values` · persisted DAG-plan snapshot + freshness check · `advisor_verdict_unrecorded` / `advisor_reviewer_is_author` / `advisor_residue_on_mechanical_mis_tier` audit glints (measure-not-block) · `advisor-gate-relax` predicate (`_advisor_slice`/`_advisor_verdict_is_pass`/`_advisor_no_residue`) relaxing `unguarded_high_risk_auto` ONLY for mechanical+PASS+no-residue (security/non-mechanical never). state.json: run_mode + dag-plan snapshot. templates: TASK.md.tmpl `### Advisor 3-lens verdict` §6 block + `sensitivity:` header; GLOSSARY.md.tmpl `## Sensitivity classes` + 4 advisor terms. ENGINE_MD5→d8ab19ea, ENGINE_PKG unchanged.
- skill   : new guide `sensitivity.md` · 6-verify.md Advisor 3-lens recording · advisor.md "3-lens sequential checklist at verify" · run.md advisor-gate-relax pathway + advisor_verdict_unrecorded · SKILL.md pointers · setup run-mode prompt + step-spawn hint. All 3 trees byte-identical; lean rebaselined (ratios kept).
- book    : `.add/GLOSSARY.md` + template gained the 4 advisor terms (advisor-gate-relax · advisor 3-lens verdict · binding verdict · advisory verdict); no new book chapter (folded into existing prose per the v1 least-sure flag — held).

### Cross-task evidence   (one row per task)
- persist-run-mode          : gate=PASS · `add.py status` → `run mode: parallel + auto` · residue=none
- risk-sensitivity-taxonomy : gate=PASS · test_sensitivity_taxonomy green · residue=none
- sensitivity-glossary      : gate=PASS · test_sensitivity_glossary green · residue=none
- persist-dag-plan          : gate=PASS · test_persist_dag_plan green · residue=none
- setup-run-mode-prompt     : gate=PASS · test_setup_run_mode green · residue=none
- advisor-review-step       : gate=PASS · test_advisor_review_step green · residue=none
- step-spawn-hint           : gate=PASS · test_step_spawn_hint green · residue=none
- advisor-verdict-audit     : gate=PASS · test_advisor_verdict_audit green · §3 re-frozen v2 · residue=none
- advisor-gate-relax        : gate=PASS · test_advisor_gate_relax green · security refute-read EARNED · residue=none (dual-block advisory note in §6)
- docs-align                : gate=PASS · test_docs_align (8) green + 8 restored prose-guards green · §3 re-frozen v2 · residue=none
- WHOLE SUITE: 2415/0 green.

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — all 9 criteria checked, each citing a green verifier (test or `add.py status`)
- goal: Make auto+parallel a first-class, persisted, advisor-guarded run mode so high-speed builds stay safe without a human on every step — PROVEN by advisor-gate-relax: a `risk:high`+`sensitivity:mechanical` task with a recorded advisor PASS + no residue now auto-completes, while security and every non-mechanical class still escalate to a human (test_advisor_gate_relax green; dogfooded — the whole milestone built conservative/human-gated).

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
