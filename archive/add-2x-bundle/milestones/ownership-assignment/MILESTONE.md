# MILESTONE: Ownership & assignment

goal: a user can assign an owner and assignee to any task or milestone (to self or a named actor) and SEE who owns and works what in status and report — descriptive only, unassigned records unchanged
rationale: sub-milestone of the **team-collaboration** major (confirmed intake 2026-06-22). Milestone 3 of 5. DEPENDS-ON `user-identity` (milestone 2, just shipped) — you cannot assign an owner without a resolved identity to assign; this milestone REUSES that milestone's actor `{name,email,source}` shape and `_whoami` resolver. Relationship to the map: EXTENDS the actor concept from an IMMUTABLE who-DID-it stamp (gate_actor/done_actor — descriptive, historical) to a MUTABLE who-is-RESPONSIBLE assignment (owner/assignee — directive, prospective; reassignable). OVERLAPS nothing live: the cross-milestone "my work" filter + waves-across-active-milestones belong to the sibling `multi-active-UX` and are explicitly OUT here. risk:high — it edits the byte-pinned engine, so the 3-copy + ENGINE_MD5 + lowered-autonomy discipline carries over from milestones 1–2.
stage: mvp · status: active · created: 2026-06-22

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  TWO mutable ownership fields on a task AND a milestone record — `owner` (the actor ACCOUNTABLE
     for the work) and `assignee` (the actor currently WORKING it), each the same `{name,email,source}`
     shape `_whoami` already returns (the two roles MAY differ; either may be absent). Write commands:
     `add.py assign <slug> [--owner "Name <email>"] [--assignee "Name <email>"]` (a bare flag, or a
     bare `assign <slug>` with neither, defaults to the resolved self via `_whoami`) and
     `add.py unassign <slug> [--owner] [--assignee]` (bare `unassign` clears BOTH). Surfacing the
     owner/assignee present-only in `status`, `report`, and the `--json`/report-data machine surfaces.
     All THREE byte-identical `add.py` copies edited in lockstep and ENGINE_MD5 re-established per task.
Out: ACCESS ENFORCEMENT / owner-only gates / separation-of-duties — the assignment is DESCRIPTIVE,
     it NEVER blocks an action (the major's standing rule; same as the actor stamp). The cross-milestone
     "my work" filter + waves spanning active milestones — sibling `multi-active-UX`. A reassignment
     HISTORY / audit log — out (we record the CURRENT owner/assignee, not a changelog; the actor STAMPS
     already give the historical who-did-what). Auto-assignment / load-balancing / notifications — out.
     Owner/assignee on a RELEASE or any record other than task/milestone — out. NO change to the 0–7
     phase flow, the existing actor-stamp format, or any reject/decision semantics (assignment is purely
     additive state).

## Shared decisions & glossary deltas   (living — every task must honor these)
- owner (NEW term) — the actor ACCOUNTABLE for a task/milestone going forward: `{name,email,source}`.
  MUTABLE + directive (reassignable), in contrast to the actor STAMP (gate_actor/done_actor), which is
  immutable + historical. Add to GLOSSARY.
- assignee (NEW term) — the actor currently DOING the work; same shape as owner; MAY differ from owner
  (delegation). Either field may be absent (unassigned). Add to GLOSSARY.
- assign resolution (confirmed) — `assign <slug>` with no role flag defaults BOTH owner+assignee to the
  resolved `_whoami` self (assign-to-self); `--owner`/`--assignee "Name <email>"` set a named actor for
  that role only; `source` of a `--to`-named actor is `"assigned"` (it was neither git-resolved nor an
  override). `unassign <slug>` with no flag clears BOTH; `--owner`/`--assignee` clears one.
- descriptive, not enforcing — assignment records WHO; it NEVER gates an action or checks permissions
  (no owner-only verify). Solo behavior unchanged.
- additive + back-compat — owner/assignee are new OPTIONAL fields; a record without them is valid and
  renders no owner/assignee line (never a placeholder, never a crash); solo/unassigned output is
  byte-identical except for the always-absent-when-unset fields.
- engine-edit discipline — every task edits all THREE add.py copies byte-identically AND re-pins
  ENGINE_MD5 in the SAME commit; parity/pin tests stay green.

## Shared / risky contracts (freeze these first)
- the OWNERSHIP DATA MODEL — the `owner`/`assignee` field shape + WHERE they live (task record AND
  milestone record), the `assign`/`unassign` write grammar (default-self vs `--owner`/`--assignee`
  named, `source: "assigned"` for a named actor), and the additive-not-enforcing rule that keeps every
  existing decision untouched -> owning task `ownership-model`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] ownership-model    depends-on: none              — the `owner`/`assignee` fields on task + milestone records + `assign`/`unassign` write commands (default-self or `--owner`/`--assignee` named; bare `unassign` clears both); freeze the data-model contract. risk:high.
- [x] ownership-surface  depends-on: ownership-model   — surface owner/assignee present-only in `status` (current focus) + `report` (per-task + milestone) + the `--json`/report-data machine facts; additive, unassigned output byte-identical. risk:high.

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py assign <task|milestone>` records owner+assignee (default self, or `--owner`/`--assignee "Name <email>"`); `unassign` clears them (bare = both); a record with neither stays valid   (← ownership-model) (verify: test_ownership_model.py — 12 green)
- [x] `status`, `report`, and `--json` surface the owner/assignee present-only; a record with neither renders no owner/assignee (solo/unassigned output unchanged)   (← ownership-surface) (verify: test_ownership_surface.py — 7 green)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py — NEW `_parse_actor_arg` (parse "Name <email>" → actor, source "assigned") + `_ownership_record` (task-first slug resolver) + `cmd_assign`/`cmd_unassign` (validate-before-mutate write commands) + the `assign`/`unassign` subparsers; NEW `_fmt_ownership` + read-only surfaces (report_data task-row + milestone owner/assignee, render_report `owned by`/`OWNED BY` blocks, cmd_status `owned   :` line, `status --json` per-task owner/assignee). engine_pin.py re-pinned 4× (2206226f → 5a709f28 → f1256114 → 369b2a86); all 3 add.py copies byte-identical. state.json: new optional `owner`/`assignee` on task + milestone records (no migration — absent = unassigned). test_min_pillar LIFECYCLE gained assign/unassign (census).
- skill   : untouched (the loop drives this method-on-method; no guide change).
- book    : untouched.

### Cross-task evidence   (one row per task)
- ownership-model   : gate=PASS · tests=12 green (test_ownership_model.py) · residue=note — adversarial review found + FIXED one BLOCKING defect pre-gate (blank-name write via `--owner "<>"`); a §7 SPEC delta carried forward (tighten `_parse_actor_arg` double-bracket mis-parse)
- ownership-surface : gate=PASS · tests=7 green (test_ownership_surface.py) · residue=none (review MERGE 0.93, 0 blocking; one NIT applied — blank-name render guard)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which): criterion 1 ← ownership-model row; criterion 2 ← ownership-surface row
- goal: a user can assign an owner+assignee to any task or milestone and SEE who owns/works what — proven on the real project: `assign ownership-surface --owner "Tin Dang <…>" --assignee "Tin Dang"` then `status` shows `owned   : owner: Tin Dang <…> · assignee: Tin Dang` and `report ownership-assignment` renders an `owned by` milestone line + an `OWNED BY` block; `unassign` returns the record to clean. Descriptive only (no enforcement); unassigned output byte-identical; full suite 1480 OK.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] fold the open §7 deltas (the `_parse_actor_arg` double-bracket SPEC delta + the ADD/TDD/DDD competency lessons) into the foundation via `add.py fold`, then archive this milestone.
- [ ] the milestone rides PR #47 (feat/fold-suggestion-seams) alongside milestones 1 (state-model-reshape) + 2 (user-identity); the human reviews + merges that PR — MERGE is the ship step here.
- [ ] tag / publish is deferred to the next release cut (release.md), which bundles the team-collaboration major; not a per-milestone publish.
