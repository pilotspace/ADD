# MILESTONE: Flow enforcement — turn convention fill-seams into engine gates

goal: the method's three fill-seams are engine-enforced rather than convention, so a task is detailed, built, and gated only after the milestone contracts, the build-expectations, and the gate outcome are actually present in the file
rationale: `sub-milestone` (intake) — a slice of the live method-quality theme, too big for one task. Discovered while dogfooding `flow-simplification`: three places where the engine RECORDS a boolean/phase transition but leaves the rich pre-condition as prose the AI is merely trusted to fill. The proof it bites: `flow-simplification` itself never set `confirmed` (opt-in, un-exercised), `confirm-parent`'s §6 GATE RECORD reads `awaiting human` while state says PASS, and `cmd_advance` has no §6 check. *extends* flow-simplification (which added the confirm SEAM; this makes the seam content-aware).
stage: mvp · status: active · created: 2026-06-23

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) make `milestone-confirm` CONTENT-aware — refuse `milestone_contracts_unfilled` when the
     `## Shared / risky contracts` section is still a `<placeholder>`, so "confirmed" means the
     cross-task contracts are actually present, not just that a human ran the command. (2) a
     tests→build gate: `cmd_advance` refuses `build_expectations_unfilled` when §6 "Build
     expectations" is empty/placeholder — verify-expectations must exist BEFORE build. (3) gate
     write-back: `add.py gate <outcome>` stamps the outcome + reviewer + date into the TASK.md §6
     `### GATE RECORD`, and `audit` flags a state↔file divergence.
Out: judging WHAT the contracts/expectations should SAY (still human/AI authorship — the engine
     only checks PRESENCE, never quality); the opt-in nature of `--await-confirm` (unchanged — this
     only hardens what "confirmed" means once opted in); any new human gate; weakening security/
     spec-first; retro-redding existing tasks (grandfather pre-existing records, like every prior seam).

## Shared decisions & glossary deltas   (living — every task must honor these)
- PRESENCE, not quality: every new gate checks a section is FILLED (no `<…>` placeholder, non-empty),
  never that its content is "good" — same line the method already draws for scope/flag gates.
- Grandfather by absence: a record/section that predates the gate (no marker) is never retro-refused —
  mirrors `_milestone_confirmed`, `flag_verified`, and the §5 scope snapshot.
- Validate-then-write on every new refusal: die BEFORE any scaffold/state mutation (fail-closed).
- One reject code per seam, named: `milestone_contracts_unfilled` · `build_expectations_unfilled` ·
  (write-back is additive, no new refusal) — each surfaced by `add.py check`/`audit`.

## Shared / risky contracts (freeze these first)
- placeholder-detection contract — the single predicate "is this MILESTONE.md / §6 section still a
  template placeholder?" (the `<…>` / empty test) reused by both new gates, so confirm and build
  agree on what "unfilled" means -> owning task `contract-fill-gate`
- gate write-back shape — what `add.py gate` writes into `### GATE RECORD` (outcome line · reviewer ·
  date) and how `audit` detects state↔file divergence without breaking grandfathered tasks
  -> owning task `gate-record-writeback`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] contract-fill-gate       depends-on: none              — `milestone-confirm` parses the MILESTONE.md and refuses `milestone_contracts_unfilled` while `## Shared / risky contracts` is a placeholder; owns the shared placeholder-detection predicate
- [ ] build-expectations-gate  depends-on: contract-fill-gate — `cmd_advance` (tests→build) refuses `build_expectations_unfilled` when §6 "Build expectations" is empty/placeholder, reusing the predicate
- [ ] gate-record-writeback    depends-on: none              — `add.py gate <outcome>` stamps outcome+reviewer+date into §6 `### GATE RECORD`; `audit` flags a state↔file gate divergence

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `milestone-confirm <slug>` refuses (`milestone_contracts_unfilled`) while the contracts section is a placeholder, and proceeds once it is filled — a pre-existing milestone with no marker is never refused (← contract-fill-gate) (verify: test_contract_fill_gate green)
- [ ] `add.py advance` from tests→build refuses (`build_expectations_unfilled`) with an empty §6 Build-expectations block, and proceeds once filled; an undeclared/legacy task is grandfathered (← build-expectations-gate) (verify: test_build_expectations_gate green)
- [ ] after `add.py gate PASS`, the task's §6 `### GATE RECORD` shows `Outcome: PASS` + reviewer + date (no stale `<…>`), and `audit` flags a state↔file divergence (← gate-record-writeback) (verify: test_gate_record_writeback green)
- [ ] guardrail: 3 trees byte-identical; full suite + `add.py check` green; every refusal is validate-then-write (a blocked command mutates nothing) (← every task at its verify) (verify: suite green + check 0-fail + md5 parity ×3)

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
- [ ] open a PR from branch `feat/flow-enforcement-seams` → main; the human reviews + merges (admin-merge via TinDang97)
- [ ] this milestone bundles with the lean-pass major (PRs #50/#51) — decide together-or-separate at the cut
- [ ] tag / publish / deploy is a SEPARATE release-altitude step (release.md), human-run
