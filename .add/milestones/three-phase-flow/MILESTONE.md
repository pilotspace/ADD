# MILESTONE: Three Phase Flow

goal: let the AI drive a clear, small/medium, or benchmark task through ADD's 8 phases as 3 agent-owned bundles — auto-verifying the DIRECTION gate and skipping only the optional ceremony (scenarios · observe) — while the frozen-contract · red-suite · recorded-gate · security-HARD-STOP floor holds in every mode
rationale: sub-milestone of the lean / risk-proportional-ceremony line (user-signaled 2026-07-09). EXTENDS `fast-lane` (the existing collapse-never-skip minimal lane — make it faster by skipping the non-important steps for oneshot/small/medium tasks) and `advisor-gated-autonomy` (which only lets `mechanical` sensitivity be advisor-gated — this raises the AI gate to the DIRECTION/contract boundary with a security/data/architecture→human floor). OVERLAPS `flag-first-freeze` (the freeze + autonomy dial). The benchmark measured the big-milestone premium as turn-fragmentation + done-phase ceremony, not the spec phases; this cuts the human-wait and optional ceremony where risk is low, never the floor.
stage: mvp · status: active · created: 2026-07-08T17:51:23+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) a first-class **phase-bundle** grouping — the 8 phases render as 3 bundles DIRECTION (ground·specify·scenarios·contract·tests) / BUILD (build) / VERIFY (verify·observe), with a PER-PHASE preferred roster agent (add-design for ground..contract, add-build for tests+build, add-verify for verify+observe — tests∈DIRECTION prefers add-build) and "agent-call-preferred" documented as the default execution mode. The DIRECTION→BUILD freeze gate sits at the contract→tests boundary (tests are the last direction-fixing step, red before build). (2) a two-way DIRECTION gate: `gate_mode` = `human` | `ai-plan-verify` — the AI-plan-verify path lets an AI verify the frozen direction bundle and auto-pass the contract freeze, EXCEPT security/data/architecture sensitivity, which always fall back to the human (security = HARD-STOP). (3) a faster fast lane: an `--oneshot` flag + benchmark-mode + the existing fast/small-medium lane declare an AI-chosen skip-set drawn ONLY from {scenarios, observe}; the contract is AI-auto-frozen (never skipped); every skip is recorded (no silent skips).
Out: collapsing the engine to 3 phase-STATES (kept at 8 + bundle metadata — decided in intake); a benchmark-arm rerun to re-measure the premium (belongs to the benchmark milestone, not here); any change to the human-mode default (human mode keeps today's gate); auto-selecting sensitivity for a task (the AI keeps declaring it; unchanged).

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Trust floor holds in EVERY mode** (oneshot · benchmark · fast · small/medium): a frozen contract exists (may be AI-auto-frozen), ≥1 red test precedes build, a §6 gate is recorded, and security is always HARD-STOP. Skips are drawn ONLY from the optional set {scenarios, observe} — never contract, tests, build, or verify.
- **AI-plan-verify-gate NEVER auto-passes security/data/architecture** — those sensitivities force the human freeze even under `autonomy:auto` / benchmark-mode. Mirrors and extends `advisor-gate-relax` (was: only `mechanical` advisor-gatable).
- **No silent skips** (rule #4): every skipped step is recorded with a one-line reason in the TASK header/§6; `status`/`guide` surface the active skip-set and gate-mode.
- New GLOSSARY terms: `phase bundle` (DIRECTION/BUILD/VERIFY) · `oneshot mode` · `AI-plan-verify-gate` · `benchmark mode`.

## Shared / risky contracts (freeze these first)
- `PHASE_GROUPS` bundle map + the "which bundle am I in" resolver -> owning task `phase-bundles`
- `gate_mode` state shape + the sensitivity→human fallback predicate (security/data/architecture) -> owning task `ai-plan-verify-gate`
- skip-set declaration shape (subset of {scenarios, observe}) + contract-auto-freeze semantics -> owning task `fast-lane-skips`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] phase-bundles       depends-on: none              — group the 8 phases into 3 agent-owned bundles (DIRECTION/BUILD/VERIFY); `status`/`guide` show the active bundle; document "agent-call-preferred" as the default execution mode
- [ ] ai-plan-verify-gate depends-on: phase-bundles      — two-way DIRECTION gate `gate_mode=human|ai-plan-verify`; AI verifies the frozen direction bundle and auto-passes the contract freeze EXCEPT security/data/architecture (→ human; security HARD-STOP)
- [ ] fast-lane-skips      depends-on: ai-plan-verify-gate — `--oneshot`/benchmark-mode + the fast/small-medium lane declare an AI-chosen skip-set from {scenarios, observe}; contract AI-auto-frozen (never skipped); every skip recorded

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `status`/`guide` show a task's active phase-bundle (DIRECTION/BUILD/VERIFY) and "agent-call-preferred" is the documented default execution mode        (← phase-bundles)
- [ ] a non-security/data/architecture task under `autonomy:auto` passes the DIRECTION gate via AI-plan-verify with no human freeze; a security/data/architecture task still requires the human freeze (security HARD-STOP)        (← ai-plan-verify-gate)
- [ ] a `--oneshot` (or benchmark/fast/small-medium) task runs with the AI's declared {scenarios, observe} skips, the contract AI-auto-frozen (never skipped), a red test before build, and every skip recorded — no silent skips        (← fast-lane-skips)

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
