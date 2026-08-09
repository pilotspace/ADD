# MILESTONE: Traceability-ids

goal: Give every §1 rule a stable ID (M#/R#) that §2 scenarios and §4 tests reference, and lint coverage so no Must/Reject ships unscenarioed or untested.
rationale: sub-milestone of the artifact-trust roadmap (M4) — the PR40 audit found a rule restated 5× downstream (§1/§2/§3/§5/§6) with NO machine link between them: a Must can silently ship unscenarioed or untested, and a SPEC delta turned into a task has only a one-way pointer. Make the rule→scenario→test chain (and the delta→task lineage) machine-checkable, so coverage gaps surface as a WARN instead of being invisible.
stage: mvp · status: active · created: 2026-06-30T11:47:47+00:00
release: 1.15.0

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
- [x] rule-id-coverage     depends-on: none   — §1 Musts carry `M#`, scenarios/tests reference rule IDs; `check` WARNs on a Must/Reject with no scenario tag and no covering test
- [x] delta-task-backlink  depends-on: none   — seeded task §0 cites its originating delta; `check` WARNs on a `seeded` delta whose pointer task is missing (dangling lineage)
- [x] template-structural-gaps       depends-on: none   — picked up via the loop: 3 TASK.md.tmpl gaps (glossary deltas, scenario IDs, live-verify evidence) that the coverage/backlink convention exposed
- [x] fresh-checkout-skip-tolerance  depends-on: none   — picked up via the loop: fresh-checkout CI regex now tolerates the recursion guard's own expected self-skip

## Exit criteria (observable; map each to the task that delivers it)
- [x] A §1 Must or Reject with no §2 scenario tag and no §4 test covering its ID makes `add.py check` print a coverage WARN (exit 0)        (← rule-id-coverage)
- [x] A task seeded via `--from-delta` carries a §0 backlink to its originating delta, and `check` WARNs when a `seeded` delta's pointer task is gone   (← delta-task-backlink)
- [x] every add.py copy stays byte-identical == the re-pinned engine_pin.ENGINE_MD5; templates parity holds; full suite green   (← both)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `rule-id-coverage` adds `add_engine/predicates._rule_coverage_gaps` + 5 new regexes in `add_engine/constants.py` (`_MUST_ID_RE`, `_REJECT_CODE_RE`, `_SCENARIO_TAG_RE`, `_COVERS_LINE_RE`, `_TAG_TOKEN_RE`), wires a WARN into `add.py:cmd_check`, adds a `covers:` field to `templates/TASK.md.tmpl` §4 — ENGINE_MD5 re-pinned. `delta-task-backlink` adds `cmd_new_task`'s §0 backlink pre-fill, `_seeded_delta_pointers` dangling-lineage WARN, new `_SEED_POINTER_RE` — ENGINE_MD5→`e23cd35e`, ENGINE_PKG_MD5→`d66bd8da` re-pinned. `template-structural-gaps` (TASK.md.tmpl only) and `fresh-checkout-skip-tolerance` (test file only) touched no engine code — pins untouched.
- skill   : untouched by all 4 tasks — `rule-id-coverage`'s TASK.md explicitly protects the phase-guide lean-pool byte budget.
- book    : `rule-id-coverage` adds a short M#/R:code convention paragraph to `03-step-1-specify.md`, `04-step-2-scenarios.md`, `06-step-4-tests.md` (+ repo-root twins). Other 3 tasks: untouched.

### Cross-task evidence   (one row per task)
- rule-id-coverage : gate=PASS · tests=2635 green (0 failed, incl. 13 new `test_rule_id_coverage.py`) · residue=2 open SPEC deltas (older `M4/R2` positional-tag dialect not recognized; untracked byte-identical `_bundled/tooling/engine_pin.py` flagged for reconciliation)
- template-structural-gaps : gate=PASS · tests=2595 green (+9 from pre-build 2586) · residue=1 open spec delta (TASK.md's own literal `<!--...-->` prose gets garbled by the engine's closed-doc comment-stripper)
- fresh-checkout-skip-tolerance : gate=PASS · tests=2586 green (+4 from pre-build 2582) · residue=none (fast-lane task; §7 Observe absent by design)
- delta-task-backlink : gate=PASS · tests=2559 green (exit 0) · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which): EC1 ("coverage WARN") ← rule-id-coverage's `_rule_coverage_gaps` + `cmd_check` wiring, verified live against real gaps while `check` still exits 0. EC2 ("--from-delta backlink + dangling WARN") ← delta-task-backlink's `cmd_new_task` pre-fill + `_seeded_delta_pointers` WARN (`test_seed_prefills_section0_backlink` + 3 dangling-WARN tests). EC3 ("byte-identical pins + templates parity + full suite green") ← rule-id-coverage (ENGINE_MD5 re-pinned, 2635/0) + delta-task-backlink (ENGINE_MD5→`e23cd35e`, ENGINE_PKG_MD5→`d66bd8da`, 2559/0), with template-structural-gaps (2595/0) and fresh-checkout-skip-tolerance (2586/0) holding parity/green without touching the pin.
- goal: every §1 rule now carries a stable `M#`/`R:code` ID that §2/§4 reference, `check` WARNs (never blocks) on an unscenarioed/untested rule, and the delta→task lineage is a two-way, WARN-checked link — proven by 2635/0 (rule-id-coverage) and 2559/0 (delta-task-backlink), both engine pins re-anchored.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] all 4 tasks' commits are already on `main` (139bd8c, e4d287d, ba09498, 1fa91ca) — no PR needed
- [ ] `add.py fold` to consolidate this milestone's open lessons into the foundation
- [ ] `add.py archive-milestone traceability-ids` once folded
- [ ] bundle into the next release cut (`add.py release`) — human-run, per release.md
