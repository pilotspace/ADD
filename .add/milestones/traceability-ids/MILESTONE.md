# MILESTONE: Traceability-ids

goal: Give every §1 rule a stable ID (M#/R#) that §2 scenarios and §4 tests reference, and lint coverage so no Must/Reject ships unscenarioed or untested.
rationale: sub-milestone of the artifact-trust roadmap (M4) — the PR40 audit found a rule restated 5× downstream (§1/§2/§3/§5/§6) with NO machine link between them: a Must can silently ship unscenarioed or untested, and a SPEC delta turned into a task has only a one-way pointer. Make the rule→scenario→test chain (and the delta→task lineage) machine-checkable, so coverage gaps surface as a WARN instead of being invisible.
stage: mvp · status: active · created: 2026-06-30T11:47:47+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  Two threads, both honoring engine NO-EXEC and warn-never-block (a `check` finding is a nudge, exit 0 — mirrors M2/M3).
  1. **rule-id-coverage** — formalize the rule IDs already used by convention: §1 Must lines are `M#`, Reject lines carry their `R:<error_code>`; §2 scenarios tag the rule(s) they exercise (`# M2, R:code`) and §4's test plan gains a `covers:` reference. `add.py check` parses §1 + §2 + §4 and WARNs when a Must ID or Reject code has NO scenario tag AND no test covering it (coverage gap). Template (§1/§2/§4) + the specify/scenarios/tests guides teach the convention.
  2. **delta-task-backlink** — complete the delta↔task link. `--from-delta` already writes the forward pointer (`[SPEC · seeded] … [→ slug]` + state `from_delta`); add the REVERSE — the seeded task's §0 Related-intent cites its originating delta — and a `check` WARN when a `seeded` delta's pointer task is missing/abandoned (a dangling lineage).
Out: auto-FIXING coverage (engine never writes scenarios/tests) · rule IDs that renumber on edit (IDs are author-stable, not engine-reflowed) · SEAMS.md for cross-task shared symbols (→ M5 seams) · any blocking gate (all findings are WARNs).

## Shared decisions & glossary deltas   (living — every task must honor these)
- Rule IDs are AUTHOR-STABLE: `M1, M2, …` for Musts, `R:<error_code>` for Rejects (the error_code IS the Reject's stable ID — already required by the contract). The engine reads them, never renumbers them.
- A `check` finding here is a WARN (nudge, exit 0), never a blocking gate — consistent with the artifact-graph/drift-guard WARNs.
- Engine stays NO-EXEC; every add.py edit re-pins ENGINE_MD5 ×3; templates parity ×3; the phases lean pool stays within budget.

## Shared / risky contracts (freeze these first)
- the §1 `M#` / §2 `# M#, R:code` tag grammar + the §4 `covers:` line + the coverage-WARN rule -> owning task rule-id-coverage
- the seeded-task §0 delta backlink shape + the dangling-lineage WARN -> owning task delta-task-backlink

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] rule-id-coverage     depends-on: none   — §1 Musts carry `M#`, scenarios/tests reference rule IDs; `check` WARNs on a Must/Reject with no scenario tag and no covering test
- [ ] delta-task-backlink  depends-on: none   — seeded task §0 cites its originating delta; `check` WARNs on a `seeded` delta whose pointer task is missing (dangling lineage)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A §1 Must or Reject with no §2 scenario tag and no §4 test covering its ID makes `add.py check` print a coverage WARN (exit 0)        (← rule-id-coverage)
- [ ] A task seeded via `--from-delta` carries a §0 backlink to its originating delta, and `check` WARNs when a `seeded` delta's pointer task is gone   (← delta-task-backlink)
- [ ] every add.py copy stays byte-identical == the re-pinned engine_pin.ENGINE_MD5; templates parity holds; full suite green   (← both)

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
