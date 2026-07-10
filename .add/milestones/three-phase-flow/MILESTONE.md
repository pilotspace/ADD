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
- [x] phase-bundles       depends-on: none              — group the 8 phases into 3 agent-owned bundles (DIRECTION/BUILD/VERIFY); `status`/`guide` show the active bundle; document "agent-call-preferred" as the default execution mode   (gate PASS `1af4c1e`)
- [x] ai-plan-verify-gate depends-on: phase-bundles      — two-way DIRECTION gate `gate_mode=human|ai-plan-verify`; AI verifies the frozen direction bundle and auto-passes the contract freeze EXCEPT security/data/architecture (→ human; security HARD-STOP)   (gate PASS `38efd8f`)
- [x] fast-lane-skips      depends-on: ai-plan-verify-gate — `--oneshot`/benchmark-mode + the fast/small-medium lane declare an AI-chosen skip-set from {scenarios, observe}; contract AI-auto-frozen (never skipped); every skip recorded   (gate PASS `ea0462a`)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `status`/`guide` show a task's active phase-bundle (DIRECTION/BUILD/VERIFY) and "agent-call-preferred" is the documented default execution mode        (← phase-bundles; PHASE_GROUPS + `_phase_bundle` resolver live, SKILL.md documents agent-call-preferred in all three skill trees)
- [x] a non-security/data/architecture task under `autonomy:auto` passes the DIRECTION gate via AI-plan-verify with no human freeze; a security/data/architecture task still requires the human freeze (security HARD-STOP)        (← ai-plan-verify-gate; PROVEN LIVE 2026-07-10: `prune-benchmark-deadweight` (mechanical) froze @v1 via `freeze --ai-plan-verify --by claude-fable-5` with a complete AI-verify record — the engine's double opt-in enforced gate_mode + autonomy + sensitivity; test_ai_plan_verify_gate.py 582 lines pin the sensitivity fallback)
- [x] a `--oneshot` (or benchmark/fast/small-medium) task runs with the AI's declared {scenarios, observe} skips, the contract AI-auto-frozen (never skipped), a red test before build, and every skip recorded — no silent skips        (← fast-lane-skips; PROVEN LIVE 2026-07-10: the same prune task ran the FULL oneshot lane end-to-end — skip rationale recorded in §0, contract frozen (never skipped), 3 guards red before build, one explicit TESTS re-cross mid-build, gate PASS — first real dogfood, zero engine friction)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py + add_engine (PHASE_GROUPS/_phase_bundle · _GATE_MODES + cmd_freeze --ai-plan-verify · _SKIPPABLE_PHASES + cmd_advance skip pre-pass + --oneshot flag) · TASK.fast.md.tmpl (oneshot/gate_mode/skips header + AI-verify record block) · engine pin re-aimed; all three engine trees byte-identical
- skill   : SKILL.md documents agent-call-preferred as the default execution mode + the oneshot lane (three skill trees in lockstep)
- book    : untouched (guides reference the bundles via the skill layer)
- harness (rider tasks): fair-meter (feature-delivery-only metering) · isolate-env (--strict-mcp-config isolation) · multirep (controlled N-rep aggregation) — benchmark-side, shipped under this milestone's confirm

### Cross-task evidence   (one row per task)
- phase-bundles : gate=PASS `1af4c1e` · tests=337-line pin suite green · residue=none
- ai-plan-verify-gate : gate=PASS `38efd8f` · tests=582-line pin suite green · residue=none
- fast-lane-skips : gate=PASS `ea0462a` · tests=646-line pin suite green · residue=none
- harness-fair-meter : gate=PASS `efc100b` · tests=suite green at close · residue=none
- harness-isolate-env : gate=PASS `2d9d238` · tests=suite green at close · residue=none
- harness-multirep : gate=PASS `94486bb` · tests=suite green at close · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (criterion 1 ← phase-bundles row + skill Ship line; criteria 2+3 ← their task rows AND the live end-to-end dogfood: prune-benchmark-deadweight ran the whole oneshot lane 2026-07-10 with the floor visibly held — AI freeze recorded, red-first guards, one explicit TESTS re-cross, gate PASS)
- goal: let the AI drive a clear/small/benchmark task through the 8 phases as 3 agent-owned bundles with the frozen-contract · red-suite · recorded-gate · security-HARD-STOP floor holding in every mode — PROVEN by the first real oneshot run: one AI-verified freeze replaced the human wait, zero silent skips, and the tamper/re-cross machinery still bound every test edit.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] merge via PR #142 (bundles this milestone + add-bench-v2 + risk-proportional-ceremony + tiny-plan; human authorized "prune, then merge one PR" 2026-07-10)
- [ ] bundle into the next release cut with the sibling closed milestones (release.md; engine records, human tags/publishes)
- [ ] follow-on (strategy A, human-picked): drive oneshot/tiny adoption, then one cheap pinned-meter WM1-3 re-run to verify the premium dropped toward 1.3×
