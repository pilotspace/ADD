# MILESTONE: multi-active-polish — close the genuinely-open parallel-front residuals

goal: close the multi-active residuals an audit confirmed still open: cross-milestone wave scheduling, a widened ownership lens, doctor value-domain validation, and parallel-preserving milestone creation.
rationale: sub-milestone — originally harvested from the team-collaboration SPEC deltas 1.8.0 carried forward. A 2026-06-26 running-evidence audit (69 area tests green + behavior probes) found the bulk already shipped by intervening work: `use`-under-own-milestone DONE, owner/assignee surfacing DONE, `doctor`+`--json` + referential pointers DONE. RE-SCOPED to the 4 genuinely-open residuals; the original 5 task slugs were retired (they collide with the done/archived 1.8.0 tasks of the same name).
stage: mvp · status: active · created: 2026-06-26T10:28:42+00:00 · re-scoped: 2026-06-26 (audit-driven slim, 5→4 tasks)

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the audit-confirmed open residuals — (1) `waves --merge` cross-milestone critical-path scheduling, (2) `mine --all` widening the ownership lens past active milestones (email-OR-name match), (3) `doctor` VALUE-domain checks beyond referential pointers (gate∈{PASS,RISK-ACCEPTED,HARD-STOP} · phase∈PHASES · archived consistency · owner/assignee shape), (4) `new-milestone` ADD-and-focus so creating a milestone in parallel preserves the active SET (add, not replace).
Out: the already-shipped 1.8.0 work (active-accessors · `use`-under-own-milestone · ownership surfacing · doctor referential pointers + `--json`) — DONE, not re-touched; the standalone `_parse_actor_arg` double-bracket guard (dropped as low-value; may ride along in new-milestone-add-focus if trivial); remote/multi-machine federation (that's component-polish); any change to the frozen state-schema migration shape beyond safe-read tolerance.

## Shared decisions & glossary deltas   (living — every task must honor these)
- "active SET" = the N active milestones + their active tasks; reads must treat `active_tasks` as advisory and filter against LIVE milestones.
- byte-identical default: single-active projects must see no behavior change from any seam here.
- never widen a referential check into a retro-red of grandfathered records — doctor REPORTS findings, it does not auto-fail history (critical for doctor-value-checks).

## Shared / risky contracts (freeze these first)
- These 4 residuals are independent additive changes — no cross-task freeze dependency; each freezes its OWN contract in its bundle.
- the riskiest is `doctor-value-checks` (it widens `_doctor_findings` output): freeze that it ADDS findings only, never auto-fails or retro-reds grandfathered records.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] waves-merge             depends-on: none   — `waves --merge` cross-milestone critical path (today `waves` is per-milestone only: `--milestone`/`--json`); fold the active SET into one DAG/schedule
- [ ] mine-all-lens           depends-on: none   — `mine --all` widens past active milestones; email-OR-name match (today `mine` is `--actor`/`--json` over active only)
- [ ] doctor-value-checks     depends-on: none   — extend `_doctor_findings` with value-domain validation: gate∈{PASS,RISK-ACCEPTED,HARD-STOP} · phase∈PHASES · archived consistency · owner/assignee shape (ADD findings; never retro-red)
- [ ] new-milestone-add-focus depends-on: none   — `cmd_new_milestone` preserves the active SET (swap `_set_active_milestone` replace → `_activate_milestone` add-and-focus); optional: fold in the actor double-bracket reject if trivial

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py waves --merge` unifies cross-milestone deps into one critical path                      (← waves-merge · PASS 2026-06-26 · +11 tests, suite 2037 green)
- [ ] `add.py mine --all` lists work across ALL milestones with email-OR-name match                   (← mine-all-lens)
- [ ] `add.py doctor` flags a bad gate/phase enum, archived inconsistency, or malformed owner/assignee (← doctor-value-checks)
- [ ] creating a milestone while one is active PRESERVES the active SET (adds, never replaces)         (← new-milestone-add-focus)

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
