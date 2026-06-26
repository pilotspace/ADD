# MILESTONE: multi-active-polish — finish the deferred team-collaboration seams

goal: make parallel-front work and ownership first-class: complete the multi-active accessors, state-doctor, ownership surface, and command-policy seams 1.8.0 carried forward
rationale: sub-milestone — harvested from the team-collaboration SPEC deltas 1.8.0 deliberately carried forward (open SPEC deltas across active-accessors, ownership-*, state-doctor, multi-active-commands, cross-active-waves). Grouped because they all complete the multi-active / parallel-front model.
stage: mvp · status: queued · created: 2026-06-26T10:28:42+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the deferred multi-active seams — (1) multi-active state accessors that own the active-task lifecycle, (2) an `add.py doctor` state integrity + referential validator, (3) owner/assignee surfaced in status·report·--json + per-stream, (4) consistent use/activate/new-milestone command policy for a parallel active SET, (5) cross-milestone waves + a wider `mine` lens.
Out: NEW collaboration features beyond closing the carried-forward deltas; remote/multi-machine federation (that's component-polish); any change to the frozen state-schema migration shape beyond safe-read tolerance.

## Shared decisions & glossary deltas   (living — every task must honor these)
- "active SET" = the N active milestones + their active tasks; reads must treat `active_tasks` as advisory and filter against LIVE milestones.
- byte-identical default: single-active projects must see no behavior change from any seam here.
- never widen a referential check into a retro-red of grandfathered records — doctor reports, it does not auto-fail history.

## Shared / risky contracts (freeze these first)
- the `add.py doctor` output shape (text + `--json`) -> owning task `state-doctor` (other tasks may read it)
- the per-task active-task accessor seam -> owning task `active-accessors` (ownership-surface + multi-active-commands depend on it)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] active-accessors      depends-on: none              — `cmd_use` records the active task under its OWN milestone; filter `active_tasks` vs LIVE milestones; `.get("active_tasks",{})` read-tolerance for partial migrations
- [ ] state-doctor          depends-on: none              — `add.py doctor` integrity + referential validator (+ `--json`); widen set: owner/assignee shape · gate∈{PASS,RISK-ACCEPTED,HARD-STOP} · phase∈PHASES · archived consistency
- [ ] ownership-surface     depends-on: active-accessors  — show owner/assignee in status + report + `--json`; per-stream owner+assignee in the `streams:` block
- [ ] multi-active-commands depends-on: active-accessors  — unify `use`/`activate` done-milestone policy; `new-milestone` ADD-and-focus (preserve the active SET); `_parse_actor_arg` rejects a double-bracket value
- [ ] cross-active-waves    depends-on: none              — `waves --merge` cross-milestone critical path; corrupt `active_milestones` entry SKIPs (not dies); `mine --all` + email-OR-name match

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `add.py use <task>` labels the active task under the task's own milestone, never the primary   (← active-accessors)
- [ ] `add.py doctor` reports state integrity + referential health and supports `--json`             (← state-doctor)
- [ ] status / report / `--json` show owner + assignee per active stream                              (← ownership-surface)
- [ ] `use`/`activate` share one done-milestone policy; `new-milestone` preserves the active SET      (← multi-active-commands)
- [ ] `waves --merge` unifies cross-milestone deps; `mine --all` widens past active milestones        (← cross-active-waves)

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
