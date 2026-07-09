# MILESTONE: Risk Proportional Ceremony

goal: cut ADD's big-milestone cost premium (1.8x dollars / 2x wall-clock vs spec-kit) toward ~1.3x by scaling ceremony to task risk — never by lowering the trust floor (frozen contract, red suite, recorded gate hold in every lane)
rationale: sub-milestone (user-signaled after the add-bench WM4-6 verdict): the benchmark proved the premium is turn fragmentation + suite-run churn + done-phase ceremony on big milestones — not the spec phases (~3%) — and that ceremony pays only where risk lives; scale it to risk.
stage: mvp · status: active · created: 2026-07-08T08:28:21+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  cut ADD's per-feature TURN COUNT — the measured cost driver — by collapsing MECHANICAL engine round-trips, without lowering the trust floor. Live evidence (fixed-harness add WM1, 2026-07-09, `scratchpad/baseline-runs/add/wm1`): **63 turns / $3.99 / 4.03M tok (96% cache_read) / fidelity 0.96**; **26 of 63 turns (~41%) are `add.py` round-trips** — `advance`×7, `status`/`guide`×5, ceremony (`new-task`/`lock`/`freeze`/`gate`/`init`/`new-milestone`)×12. Each round-trip re-reads the full ~60K context (that IS the cost). Three levers: (1) collapse the `advance` chain, (2) fold `status`+`guide` orientation, (3) trim per-call stdout that grows cache_read.
Out: touching app-code turns (irreducible deliverable work); suite-run churn / done-phase ceremony on BIG milestones (separate lever — this milestone targets per-feature fast/oneshot round-trips); any change that skips a freeze, a red suite, or a recorded gate (the floor is non-negotiable); lean-agent roster work (shipped in [[add-lean-loop]]).

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Shared decisions & glossary deltas   (living — every task must honor these)
- TRUST FLOOR IS INVARIANT: every lane still requires a FROZEN §3 contract, a red suite before build, a recorded §6 gate, and security = HARD-STOP. A round-trip may be collapsed ONLY if it carries no human/proxy decision — freeze and gate are decision points and are never auto-crossed.
- MEASURE, DON'T ASSUME: each task states its before-number from the live baseline transcript and re-measures after; the milestone's proof is a fresh fixed-harness add WM1 run, not a code-reading argument.
- BACKWARD-COMPATIBLE CLI: existing subcommands/flags keep working; new behavior is additive (a flag or a smarter default that a bare call still honors) so the 3-tree byte-parity engine and its ~3k tests hold.

## Shared / risky contracts (freeze these first)
- `add.py advance` collapse semantics (where the chain STOPS) -> owning task advance-chain-collapse — the freeze/gate stop-points every other task assumes.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
> GROUND (2026-07-09) reshaped these: the `advance --to <phase>` bundle fast-forward ALREADY exists (add.py:1259, stops hard at `tests` to preserve the freeze gate) — the agent never used it. The live waste is the engine not HANDING the agent the exact/collapsed next command, so it spelunks `--help` ×7 + single-steps `advance` ×7. Root cause = `_next_footer` (add.py:5993) + `status` emit generic hints, not copy-pasteable commands.
- [ ] advance-chain-collapse   depends-on: none                    — the post-advance `next:` footer emits the COLLAPSED `advance --to <phase>` command (front drafting span → contract) so the agent uses the existing bundle-advance instead of N single steps. Floor intact: `--to` still stops at `tests`; freeze/gate never auto-crossed.
- [ ] status-guide-fold        depends-on: advance-chain-collapse  — `status` folds in the guide's next-action AND the `next:` footer emits the EXACT copy-pasteable command WITH its required flags (e.g. `freeze --by <name>`, `gate PASS`) — killing the 7 `--help` discovery turns + the 6 status/guide re-orientation turns.
- [ ] terser-engine-stdout     depends-on: none                    — trim the fattest per-call stdout (the outputs that grow cache_read on every later turn) while keeping gate-relevant info truthful/complete.

## Exit criteria (observable; map each to the task that delivers it)
- [ ] a fresh fixed-harness add WM1 run shows TURNS and COST below the 63-turn / $3.99 baseline, with fidelity ≥0.95 and app_reachable   (← all three, re-measured)
- [ ] `add.py advance` crosses multiple AI-owned phases in one invocation yet still halts at contract-freeze and verify-gate (floor intact)   (← advance-chain-collapse)
- [ ] `add.py status` surfaces the next phase action inline — an agent can proceed without a separate `guide` call   (← status-guide-fold)

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
