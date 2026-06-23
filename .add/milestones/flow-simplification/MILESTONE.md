# MILESTONE: lean-pass M3 · flow simplification

goal: the flow surface is simpler — the spawn/delegation machinery and any redundant ceremony live in one place, and a task can't be detailed before its milestone is confirmed — with no gate, security stop, or spec-first discipline weakened
rationale: sub-milestone M3 of the confirmed `lean-pass` new-major (the structural, behavior-aware tail after M1 mechanical compaction). Extends M1 `skill-effectiveness` — M1 made each guide leaner in isolation; M3 removes the cross-guide DUPLICATION M1 couldn't (the spawn/delegation surface repeated across run/streams/advisor) and closes the one flow HOLE M1 surfaced (no confirm-parent seam). Depends-on M1 (done). Skips M2 book-compaction (user deferred). This is the HIGH-risk milestone: it is allowed to change frozen flow behavior, so every change rides a contract freeze; security + spec-first are never weakened to look lean.
stage: mvp · status: active · created: 2026-06-23

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) fold the duplicated worker-spawn/delegation surface — the PROMPT.md/persona/touch_boundary
     template + vendor-neutral model tiers repeated across `run.md`, `streams.md`, `advisor.md` —
     into ONE canonical source the others reference (behavior-preserving). (2) a CONFIRM-PARENT
     seam: the engine/flow holds `new-task` until the parent MILESTONE.md is confirmed well-formed
     (closes the logged M1 gap; a real behavior change, contract-frozen). (3) drop ONLY
     provably-redundant guide/phase ceremony (e.g. boilerplate the engine already enforces) —
     never a phase or gate that carries meaning.
Out: the book/docs (M2, deferred); ANY weakening of a gate, the security HARD-STOP, the spec-bundle
     (specify→scenarios→contract→tests stays four steps), or the verify auto-gate; pure wording
     (M1 done); merging the 5 scope LEVELS or the 9 phases away — the phase model stays intact.

## Shared decisions & glossary deltas   (living — every task must honor these)
- Behavior changes are ALLOWED here (unlike M1) but each one rides a §3 contract freeze and a
  red→green test; a fold that is behavior-preserving still proves it with a dogfood walk.
- The 3 mirror trees stay byte-identical; full suite + `add.py check` green at every verify.
- Never weaken to "look lean": a gate, a security stop, or a spec-first step is removed ONLY if it
  is provably redundant (the engine already enforces it elsewhere) — otherwise it stays.
- One canonical home per concept: after spawn-fold, the worker contract + model tiers have exactly
  one source; run/streams/advisor POINT at it (no copy).

## Shared / risky contracts (freeze these first)
- worker-contract single-source shape (what the canonical PROMPT.md/touch_boundary/tiers block is,
  and how run/streams/advisor reference it) -> owning task `spawn-fold`
- confirm-parent seam contract (the guard: which command, what "confirmed" means, the reject code,
  and the escape hatch so solo/fast flows aren't over-constrained) -> owning task `confirm-parent`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] spawn-fold      depends-on: none         — consolidate the worker-spawn/delegation + model-tier surface (run.md/streams.md/advisor.md) into one canonical source the others reference; behavior-preserving
- [ ] confirm-parent  depends-on: none         — engine/flow seam holding `new-task` until the parent MILESTONE.md is confirmed well-formed (closes the logged M1 gap); contract-frozen behavior change with an escape hatch
- [ ] phase-review    depends-on: spawn-fold   — audit phases/guides for provably-redundant ceremony the engine already enforces; drop ONLY what carries no meaning (may find nothing — that is a valid result)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] the worker contract + model tiers have exactly ONE source; run/streams/advisor reference it with no copy; a dogfood spawn produces the same worker prompt as before (← spawn-fold)
- [ ] `add.py new-task` refuses (named reject code) when the parent MILESTONE.md is not yet confirmed well-formed, and proceeds once it is; the escape hatch works for solo/fast flows (← confirm-parent)
- [ ] every dropped ceremony item is provably redundant (engine enforces it) — a dogfood walk shows identical gates/decisions; nothing meaningful removed (← phase-review)
- [ ] guardrail: flow guides materially leaner with ZERO behavior drift except the one intended confirm-parent gate; 3 trees byte-identical; full suite + `add.py check` green (← every task at its verify)

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
