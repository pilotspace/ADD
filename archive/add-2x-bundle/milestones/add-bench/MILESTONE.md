# MILESTONE: Add Bench

goal: a reproducible, automated benchmark under `benchmark/` proving (or falsifying) ADD's long-term-project claim — five method arms (ADD · vanilla Claude Code · plan-mode-first · GSD · GitHub spec-kit) each build the same longitudinal greenfield workload (task/booking REST API + CLI, 3 sequential milestones) headlessly, and the harness auto-scores regression rate, spec fidelity, tokens/cost, context-rot slope, and time-to-first-edit into one arm-vs-arm pilot report
rationale: new-major — an automated benchmark harness is a new product theme no active milestone's goal covers (all prior milestones ship the method/engine/book; only archived book chapters *reference* GSD/spec-kit). Confirmed at intake 2026-07-07.
stage: mvp · status: active · created: 2026-07-07T09:14:41+00:00
release: 1.18.0

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  `benchmark/` tree (workload spec + oracle suites · arm definitions · headless runner · scorers · pilot report); pilot envelope = 5 arms × 3 workload milestones × 1 rep; runner designed for failure (per-run timeout, resume from last completed workload milestone, sandboxed workspaces, transcript+token capture).
Out: statistical scale-up (3+ reps), brownfield track, non-Claude-Code agents (Cursor/Codex), CI scheduling of benchmark runs, publishing results as a book chapter (a later milestone once the pilot is trusted).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **arm** — one method configuration driving Claude Code headlessly (`claude -p`) with a fixed per-arm system-prompt/setup recipe; arms never share workspace state.
- **workload milestone** — one of the 3 fixed evolution steps of the target app (WM1 core CRUD → WM2 business rules + auth → WM3 breaking-change refactor, regression-bait); identical prompts across arms.
- **oracle suite** — the harness-owned pytest suite per workload milestone that scores an arm's output; NEVER visible to the arm under test (kept outside its workspace) — showing it would contaminate the benchmark.
- Fairness floor: every arm gets the same raw request text per workload milestone, the same model, the same turn/token ceiling; method-specific ceremony (docs, plans, ADD phases) counts inside the arm's token budget.
- Metrics (frozen names): `regression_rate` (earlier-WM oracle tests broken by later WMs) · `spec_fidelity` (rubric-judge 0–1) · `tokens_total`/`cost_usd` per shipped WM · `context_rot_slope` (fidelity trend WM1→WM3 + cold-resume success) · `time_to_first_edit` (seconds/turns until first Edit/Write tool call).

## Shared / risky contracts (freeze these first)
- run-record JSON schema (per arm×WM: status, metrics, artifact paths) -> owning task bench-scaffold
- runner CLI surface (`benchmark/run.py run|resume|score|report`) -> owning task bench-runner

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] bench-scaffold     depends-on: none            — `benchmark/` tree: workload spec (3 WMs of the task/booking API+CLI), oracle suites, 5 arm definitions, run-record schema
- [x] bench-runner       depends-on: bench-scaffold  — headless `claude -p` runner: sandboxed workspace per arm, WM sequencing with resume, timeout/retry, transcript+token capture
- [x] bench-scoring      depends-on: bench-scaffold  — scorers for the 5 frozen metrics (oracle re-runs, rubric judge, token ledger, first-edit timer)
- [x] bench-pilot-report — depends-on: bench-runner, bench-scoring — execute the 5×3×1 pilot, render the arm-vs-arm report (markdown table + per-arm evidence links)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `python3 benchmark/run.py run --arm add --wm 1` completes one arm×WM headlessly and writes a schema-valid run record        (← bench-runner)  (DONE — 12 records on disk (runs/{add,spec-kit}/wm1-6), schema-valid via RunRecord.validate)
- [x] A killed run resumes from the last completed WM without redoing finished work        (← bench-runner)  (DONE — pilot resume exercised repeatedly (degraded-chain quarantine + relaunch, wm6 rerun skipped wm1-5))
- [x] `score` computes all 5 frozen metrics for a finished run from artifacts alone (re-runnable, no live agent)        (← bench-scoring)  (DONE — score_record re-ran offline for add wm6 re-judge 2026-07-08 (artifacts only))
- [x] The full pilot (5 arms × 3 WMs × 1 rep) runs unattended and `report` renders the arm-vs-arm comparison with evidence links        (← bench-pilot-report)  (DONE — pilot 5×3×1 executed 2026-07-07; results of record in benchmark/BENCHMARK.md)
- [x] Oracle suites are provably isolated from arm workspaces (a check fails loudly if leaked)        (← bench-scaffold)  (DONE — check_isolation.py; every oracle_report records isolation_clean:true)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">
- benchmark : <benchmark/* — what shipped>

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)  (DONE — evidence inline above; per-run records + transcripts under benchmark/runs/)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from the Close ship-review above; the human reviews + merges
- [ ] attach the pilot report as the PR's headline evidence
- [ ] (later milestone) publish pilot findings into the book once trusted
