# MILESTONE: Advisor-Gated Autonomy

goal: Make auto+parallel a first-class, persisted, advisor-guarded run mode so high-speed builds stay safe without a human on every step
rationale: sub-milestone (intake) — extends the v6 dynamic-run/autonomy-dial + v7 auto-default + the team-collaboration streams/waves work, and UPGRADES (not duplicates) the existing refute-read seam; depends-on nothing new. No existing or archived milestone delivers advisor-gating or run-mode persistence, so not a duplicate_goal.
stage: mvp · status: active · created: 2026-06-29T03:00:09+00:00

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
- [ ] risk-sensitivity-taxonomy depends-on: none                                    — add a `sensitivity:` dimension (security|data|architecture|mechanical) to the TASK.md header + parser/validator + status/check surfacing; human declares at freeze; engine never classifies.
- [ ] persist-dag-plan          depends-on: none                                    — materialize a SNAPSHOT of the computed task DAG plan (waves · critical path · tiers) as a committed/auditable artifact with a freshness check vs live `depends_on` edges (drift → stale); live `waves` recompute stays the source of truth.
- [ ] setup-run-mode-prompt     depends-on: persist-run-mode                        — update the setup phase (phases/0-setup.md + engine support) to explicitly ASK the human to choose the run mode (auto+parallel vs conservative) and persist the answer via persist-run-mode's home; EOF-tolerant, byte-identical non-interactive default.
- [ ] advisor-review-step       depends-on: risk-sensitivity-taxonomy               — upgrade the refute-read into a tier-aware SINGLE advisor running a 3-lens sequential checklist (security→concurrency→architecture) on EVERY auto-pass; verdict BINDING for mechanical-high-risk, advisory elsewhere.
- [ ] step-spawn-hint           depends-on: persist-run-mode, risk-sensitivity-taxonomy — engine emits a per-phase advisory subagent-spawn hint (idiom + tier) in status/guide, keyed off run_mode + risk; advisory only, never spawns (mirrors the `waves` tier hint).
- [ ] advisor-verdict-audit     depends-on: advisor-review-step                      — `add.py audit` MEASURES (not blocks): advisor verdict recorded on every auto-pass · reviewer ≠ author · residue-found-on-mechanical = mis-tier flag.
- [ ] advisor-gate-relax        depends-on: advisor-verdict-audit, risk-sensitivity-taxonomy — relax `unguarded_high_risk_auto` so `risk:high` + `sensitivity:mechanical` + recorded advisor-PASS + no-residue auto-completes via `gate PASS`; sensitive + any security still escalate.
- [ ] docs-align                depends-on: advisor-gate-relax, step-spawn-hint      — glossary + book chapter on risk-tiered advisor-gated autonomy + the new `run_mode`/`sensitivity` header fields + a SKILL.md pointer.

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `add.py status` shows the persisted run_mode (autonomy + streams posture), with the streams posture read from its persisted home (not prose-only)   (← persist-run-mode)
- [ ] a task header declares `sensitivity:`; status/check surface it; an invalid value is rejected                  (← risk-sensitivity-taxonomy)
- [ ] a persisted DAG-plan snapshot exists and `add.py` surfaces it; changing a `depends_on` edge marks the snapshot stale vs the live edges   (← persist-dag-plan)
- [ ] the setup phase asks the human to choose run mode (auto+parallel vs conservative) and persists the answer; non-interactive setup stays byte-identical to today   (← setup-run-mode-prompt)
- [ ] every auto-PASS records a single-advisor 3-lens verdict in §6; on mechanical-high-risk it gates, elsewhere it is advisory   (← advisor-review-step)
- [ ] `add.py status`/`guide` prints a per-phase spawn hint (idiom + tier) for the active phase, and nothing where delegation doesn't fit (e.g. contract)   (← step-spawn-hint)
- [ ] `add.py audit` flags a missing advisor verdict, an author-reviewed verdict, and a mechanical task with advisor-found residue — measure only, no block   (← advisor-verdict-audit)
- [ ] a `risk:high` + `sensitivity:mechanical` task with a recorded advisor PASS + no residue auto-completes; a `sensitivity:security` task (or any residue) still refuses/escalates   (← advisor-gate-relax)
- [ ] glossary + book + headers + SKILL.md document risk-tiered advisor-gated autonomy and the new header fields   (← docs-align)

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
