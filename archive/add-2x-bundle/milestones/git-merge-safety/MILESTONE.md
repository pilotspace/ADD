# MILESTONE: Git-merge safety

goal: a team merging parallel branches never silently corrupts .add/state.json — ADD recognizes a conflicted or inconsistent state at load and via a doctor command, and guides reconciliation instead of crashing or proceeding on bad data
rationale: sub-milestone of the **team-collaboration** major (confirmed intake 2026-06-22). Milestone 4 of 5. The major is git-native multi-user with NO server, so the #1 failure mode is two users writing `.add/state.json` on parallel branches → a merge that either crashes ADD (conflict markers = invalid JSON) or silently proceeds on inconsistent data. This milestone is the SAFETY NET for exactly that — it is the direct answer to the live parallel-writer clobber we hit during M2/M3. Relationship to the map: DEPENDS-ON the multi-active state model (M1, the schema it validates); ORTHOGONAL to user-identity (M2) + ownership-assignment (M3); OVERLAPS nothing live. Scope altitude confirmed with the human (2026-06-22): GUARD + DOCTOR (lean safety net) — NOT merge-friendly reformat, NOT a custom git merge driver (both deferred, see Out). risk:high — it edits the byte-pinned engine (the load path), so the 3-copy + ENGINE_MD5 + lowered-autonomy discipline carries over.
stage: mvp · status: active · created: 2026-06-22

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A merge-AWARE load guard — when `.add/state.json` carries git conflict markers
     (`<<<<<<<` / `=======` / `>>>>>>>`) or is otherwise unparseable, ADD fails LOUD with a
     merge-SPECIFIC, actionable message (`state_conflicted` — name the markers + how to reconcile),
     distinct from the existing generic `state_invalid`. A `doctor` command that PROACTIVELY
     validates state mergeability + integrity (parseable · conflict-marker-free · referential:
     every active_milestone/active_task points to a real record, every task's `milestone` exists)
     and reports PASS or each specific problem + its fix — the check a user runs after a merge.
     All THREE byte-identical `add.py` copies edited in lockstep + ENGINE_MD5 re-established per task.
Out: MERGE-FRIENDLY SERIALIZATION (sort_keys / deterministic reorder so independent adds merge
     line-cleanly) — deferred (human-chosen lean scope; a future task/milestone, seeded as a delta).
     A CUSTOM GIT MERGE DRIVER / `.gitattributes` semantic 3-way merge — deferred (per-clone config,
     brittle; over-engineered for a no-server MVP). State SHARDING (per-milestone/per-task files) —
     deferred. AUTO-REPAIR / auto-reconcile of a conflicted state — OUT (doctor REPORTS + guides; the
     human resolves — never an engine auto-mutate of a diverged state). ANY server / hosted backend.
     NO change to the 0–7 phase flow, the state schema, or existing decision semantics.

## Shared decisions & glossary deltas   (living — every task must honor these)
- state_conflicted (NEW reject code) — a load-time failure raised when state.json contains git
  conflict markers: distinct from `state_invalid` (generic parse/IO failure) so the message can be
  merge-SPECIFIC. Add to the reject-code vocabulary.
- doctor (NEW command) — a read-only diagnostic that validates state integrity + mergeability and
  reports; it NEVER mutates state (no auto-repair). Add to GLOSSARY.
- detect, never auto-resolve — every check REPORTS and guides; reconciliation is the human's (mirrors
  the major's descriptive-not-enforcing posture). A diverged state is surfaced, never silently fixed.
- fail-loud + actionable — a guard message NAMES the file + the concrete next step (resolve markers /
  `git checkout --ours`/`--theirs` / `add.py doctor`), never a raw traceback (design-for-failure).
- engine-edit discipline — every task edits all THREE add.py copies byte-identically AND re-pins
  ENGINE_MD5 in the SAME commit; parity/pin tests stay green.

## Shared / risky contracts (freeze these first)
- the CONFLICT-DETECTION rule + `state_conflicted` message contract — what byte pattern counts as a
  git conflict marker, where the check sits in the load path (BEFORE the JSON parse so a marker'd file
  is recognized as a conflict, not generic corruption), and the exact actionable message -> owning task `merge-guard`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] merge-guard    depends-on: none           — detect git conflict markers in state.json at load → fail with a merge-specific `state_conflicted` message (markers + reconciliation steps), distinct from generic `state_invalid`; the load-time safety net. risk:high.
- [x] state-doctor   depends-on: merge-guard     — a read-only `add.py doctor` command that validates state integrity + referential consistency (parseable · conflict-free · active refs → real records · task.milestone exists) and reports PASS or each problem + its fix; never mutates state. risk:high.

## Exit criteria (observable; map each to the task that delivers it)
- [x] a state.json with git conflict markers makes every state-loading command fail with a clear `state_conflicted` message (file + how to reconcile), not a crash or a generic "corrupt"   (← merge-guard) (verify: `python3 -m unittest test_merge_guard` — 7 green incl. status/json/check paths + non-false-positive)
- [x] `add.py doctor` validates a healthy state as PASS and reports each specific problem + fix on a conflicted/inconsistent state, mutating nothing   (← state-doctor) (verify: `python3 -m unittest test_state_doctor` — 9 green incl. PASS, conflict, bad-JSON, 3 referential, type-corrupt robustness)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py gains a merge-AWARE load guard (`_CONFLICT_MARKER_RE` + `_state_text_or_die`, routed through all 3 state-read sites → merge-specific `state_conflicted`) and a read-only `doctor` command (`_doctor_findings` + `cmd_doctor` + `doctor` subparser) that REPORTS integrity/referential problems or PASS, mutating nothing. `test_min_pillar` LIFECYCLE census gains `["doctor"]`. All 3 add.py copies byte-identical; ENGINE_MD5 re-pinned per task. New suites: test_merge_guard (7), test_state_doctor (9).
- skill   : untouched (no phase/guide change — the guard + diagnostic are engine behavior, surfaced via existing `add.py` commands).
- book    : untouched (no new chapter — design-for-failure + detect-never-auto-resolve are existing method principles this milestone instantiates in code).

### Cross-task evidence   (one row per task)
- merge-guard  : gate=PASS · tests=7 green (status/json/check conflict paths + non-false-positive + healthy) · residue=none
- state-doctor : gate=PASS · tests=9 green (PASS · conflict · bad-JSON · 3 referential · mislabeled · type-corrupt robustness) · residue=none — 2 refute-read nits fixed in-build (type-robustness + vacuous assert), not waived

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — criterion 1 ← merge-guard row (state_conflicted on every load path); criterion 2 ← state-doctor row (PASS + per-problem report, read-only)
- goal: a team merging parallel branches never silently corrupts .add/state.json — ADD recognizes a conflicted/inconsistent state at load AND via `doctor`, and guides reconciliation instead of crashing or proceeding on bad data. Proof: a marker'd state.json now fails LOUD with `state_conflicted` (file + reconcile steps) on every load path, and `add.py doctor` reports each integrity/referential problem with a fix while leaving the file byte-identical — the two halves (fail-fast guard + proactive full-picture diagnosis) close exactly the live parallel-writer clobber that motivated the milestone.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] continue the team-collaboration major on PR #47 (feat/fold-suggestion-seams) — this milestone's two commits ride that PR alongside M1–M3; no separate PR.
- [ ] when the major's last sibling (multi-active-UX) closes, bundle the whole major into one release cut (release.md) — git-merge-safety is one closed milestone among the major's set, attributed in RELEASES.md.
- [ ] human-run at the cut: bump the 4 version sources in lockstep + tag → CI-gated publish (npm + PyPI), per the release-gate recipe.
