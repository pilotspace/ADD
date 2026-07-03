# MILESTONE: Install/update hardening — atomic + concurrency-safe writes

goal: add.py init/update (both --global and project-scope, pip+npm twins) survive a crash or a concurrent run without leaving a half-written .add/ tree or a wedged lock
rationale: <why this scope — the confirmed intake classification (bucket + reason)>
stage: mvp · status: active · created: 2026-07-02T14:46:06+00:00
release: 1.16.0

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  crash-safe (self-healing, stage-then-commit) install/update paths across BOTH twins
     (pip `_installer.py` + npm `cli.js`) for: (1) the managed-tree reconcile copy
     (`_clean_replace`/`cleanReplaceTree`), (2) the user-data persist/restore path
     (`_persist_data`/`_restore_data`), (3) the global home update-lock (stale-lock self-heal,
     `install --global` coverage, an opt-in CI timeout mode), and (4) a NEW per-project lock
     serializing concurrent project-scope `install`/`update` runs against the same destination.
Out: cross-process locking of paths not named above (e.g. `prune-data`'s own concurrency —
     named, consciously deferred, a cheap natural follow-up); Windows PID-liveness dead-holder
     detection (mtime-age chosen instead — see global-lock-followups §3); a user-facing CLI knob
     for staleness thresholds (env-var override only, no new flag surface for routine tuning);
     making the multi-entry restore loop one all-or-nothing transaction (per-entry atomicity only
     — see global-data-restore-harden's lowest-confidence flag A1).

## Shared decisions & glossary deltas   (living — every task must honor these)
- The **stage-then-commit idiom** — self-heal stale scratch siblings -> stage into a freshly
  created, uniquely-named sibling -> commit via same-parent renames (never targeting an existing
  name) -> sweep the old backup — is the ONE shared shape for every crash-safety task in this
  milestone, extending this codebase's existing FILE-level `_atomic_write_many` idiom
  (`add_engine/io_state.py`) to directory trees. `project-scope-atomic-reconcile` is the
  reference implementation; `global-data-restore-harden` adapts it (whole-tree for
  `_persist_data`, per-entry for `_restore_data` — its shared `.add/` dest can't be whole-tree
  staged without swapping the engine itself).
- **One new shared exclusion**: `_is_user_data`/`isUserData` gains ONE new rule — exclude any
  name carrying the reserved `.add-tmp-`/`.add-bak-` scratch-staging marker — so a stale sibling
  left by ANY of the stage-then-commit tasks is never mistaken for real user-data. Both
  `project-scope-atomic-reconcile` and `global-data-restore-harden` deposit siblings inside
  `.add/`; whichever task builds second should confirm the other's marker convention still
  matches (same `.add-tmp-`/`.add-bak-` infix) rather than defining a second, incompatible one.
- **Freeze the OBSERVABLE cross-twin behavior, not the per-twin mechanism** (CONVENTIONS.md
  fv59) — every task here states what pip + npm both guarantee, letting each twin use its own
  native primitive (`tempfile`/`os.replace` vs `fs.mkdtempSync`/`fs.renameSync`;
  `os.open(O_EXCL)` vs `fs.openSync("wx")`).
- **No new dependency** anywhere in this milestone — stdlib `tempfile`/`os`/`shutil` and Node
  builtin `fs`/`path` cover every task's design.
- **Risk classification is inconsistent across tasks as drafted** — `global-lock-followups` is
  `risk: high` / `autonomy: conservative` (mirrors its predecessor `global-update-harden`'s own
  precedent); `project-scope-atomic-reconcile` and `global-data-restore-harden` both stayed at
  the project default `autonomy: auto`, each explicitly considering and declining to raise it,
  but both flagged the question rather than deciding it unilaterally (all three touch
  crash-safety of core install/update paths with comparable blast radius). Surfaced to the human
  at contract-freeze for a consistent, deliberate call across the milestone — not silently
  resolved either way.

## Shared / risky contracts (freeze these first)
- `_clean_replace`/`cleanReplaceTree` stage-then-commit state machine -> owning task
  `project-scope-atomic-reconcile` (the pattern `global-data-restore-harden` reuses/adapts —
  freeze this one first so the second task's build has a settled reference shape, not a moving
  target)
- `.add-tmp-`/`.add-bak-` scratch-marker naming convention -> shared by
  `project-scope-atomic-reconcile` + `global-data-restore-harden` (both extend
  `_is_user_data`/`isUserData` with the SAME exclusion rule)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] project-scope-atomic-reconcile   depends-on: none     — crash-safe stage-then-commit for
      the managed-tree reconcile copy (`_clean_replace`/`cleanReplaceTree`); gate: PASS (independent
      add-verify pass — 27 new + 47 sibling tests green, advisor 3-lens CLEAR/CLEAR/CLEAR)
- [x] global-lock-followups   depends-on: none     — stale `.update.lock` self-heal +
      `install --global` lock coverage + an opt-in `--lock-timeout` CI mode; gate: PASS
      (risk:high + autonomy:conservative — human-reviewed, Tin Dang, 2026-07-03). REOPENED
      mid-milestone: an independent verify pass on the sibling task found a real TOCTOU race in
      the shared stale-reclaim pattern this task's own `_update_lock` also carried — fixed across
      3 rounds (the race itself; a leaked-ticket unbounded livelock the first fix introduced; a
      final pass confirming the "ticket-for-a-ticket" recursion is structurally closed, backed by
      1167+ adversarial attempts, 0 anomalies). Fresh independent verify: EARNED / CLEAR×3 /
      Residue: none — 35/35 own tests green, 152/152 sibling sweep. Supersedes the original
      2026-07-03 PASS, which predated this discovery.
- [x] global-data-restore-harden   depends-on: none     — crash-safe stage-then-commit for the
      user-data persist/restore path (`_persist_data`/`_restore_data`) + 2 committed test gaps;
      gate: PASS (independent add-verify pass — 75/75 green, RED independently reproduced,
      advisor 3-lens Security CLEAR / Concurrency RESIDUE / Architecture RESIDUE, both judged
      bounded and non-blocking; human-reviewed — Tin Dang, 2026-07-03)
- [x] project-scope-install-lock   depends-on: project-scope-atomic-reconcile   — a NEW
      per-project lock serializing concurrent `install`/`update` runs against the same
      project-scope destination; gate: PASS (autonomy: auto, no risk:high — auto-eligible on
      clean evidence). Built across the same 3-round arc as its sibling above (a TOCTOU race in
      the new `_project_lock`'s stale-reclaim, then a leaked-ticket permanent wedge, then a
      confirmed-closed recursion check); independent verify: EARNED / CLEAR×3 / Residue: none.

## Exit criteria (observable; map each to the task that delivers it)
- [x] A simulated mid-copy failure during `add.py init`/`update` never leaves `.add/tooling`, `.add/docs`, `.add/personas-teacher`, or `.claude/skills/add` half-copied — self-heals next run (verify: project-scope-atomic-reconcile §4 mid-copy-failure + self-heal scenarios)   (← project-scope-atomic-reconcile)
- [x] A simulated mid-write failure during `update --global`'s re-persist, or `init --from-global-data`/`--force` restore, never leaves a snapshot/restored entry half-written — self-heals next call (verify: global-data-restore-harden §4 mid-write-failure + self-heal scenarios)   (← global-data-restore-harden)
- [x] A SIGKILL'd `update --global`/`install --global` never wedges a future global op — the stale lock self-heals, `install --global` is now lock-serialized, an opt-in `--lock-timeout` lets CI wait (verify: global-lock-followups §4 stale-lock + install-global-locked + timeout scenarios); RE-VERIFIED this session after a real leaked-ticket livelock was found and fixed — evidence clean, gate: PASS (human-reviewed, Tin Dang, 2026-07-03)   (← global-lock-followups)
- [x] Two concurrent `install`/`update` runs against the SAME project-scope destination cannot interleave writes — one waits or fails cleanly (verify: project-scope-install-lock §4 concurrent-run scenarios) — gated PASS   (← project-scope-install-lock)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add_method/_installer.py` + `bin/cli.js` (both pip+npm twins) — 4 crash/concurrency-safe
  paths: (1) `_clean_replace`/`cleanReplaceTree` stage-then-commit managed-tree reconcile copy,
  (2) `_persist_data`/`_restore_data` stage-then-commit user-data persist/restore, (3)
  `_update_lock`/`acquireUpdateLock` — TOCTOU-race-fixed + ticket-leak-livelock-fixed stale
  reclaim, `install --global` lock coverage, opt-in `--lock-timeout`, (4) NEW
  `_project_lock`/`acquireProjectLock` — a per-project lock serializing concurrent project-scope
  `install`/`update` runs, same TOCTOU-race + ticket-leak-wedge fix pattern as (3). Shared:
  `_is_user_data`/`isUserData` extended twice (`.add-tmp-`/`.add-bak-` scratch markers, then a
  `.reclaim-` ticket-file marker). No new dependency (stdlib/builtin only, per plan).
- skill   : untouched
- book    : untouched

### Cross-task evidence   (one row per task)
- project-scope-atomic-reconcile : gate=PASS · tests=27 new + 47 sibling green · residue=none
- global-data-restore-harden : gate=PASS · tests=75/75 green · residue=Concurrency+Architecture
  RESIDUE (both judged bounded/non-blocking; human-reviewed, Tin Dang, 2026-07-03)
- project-scope-install-lock : gate=PASS · tests=30/30 own + 152/152 sibling sweep · residue=none
  (741 adversarial multi-process/thread attempts against this task's own lock, 0 anomalies)
- global-lock-followups : gate=PASS · tests=35/35 own + 152/152 sibling sweep · residue=none (680
  adversarial attempts against this task's own lock — 1167+ combined across both lock tasks, 0
  anomalies); risk:high/autonomy:conservative — human-reviewed, Tin Dang, 2026-07-03

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row (all 4 rows: gate=PASS,
  green suites, residue none or bounded/human-reviewed)
- goal: add.py init/update (both --global and project-scope, pip+npm twins) survive a crash or a
  concurrent run without leaving a half-written .add/ tree or a wedged lock — met: the
  stage-then-commit idiom (atomic-reconcile + data-restore-harden rows) proves crash-safety for
  both the managed-tree copy and the user-data persist/restore path; the TOCTOU-race-fixed +
  ticket-leak-fixed lock pattern (install-lock + lock-followups rows, 1167+ combined adversarial
  attempts, 0 anomalies) proves concurrency-safety for both the new project-scope lock and the
  existing global lock — across both pip+npm twins, both global and project scope.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] run `add.py milestone-done` to record the goal-met close (this Close section is the evidence)
- [ ] open a PR bundling all 4 tasks' commits since `release/1.15.0` branched; human reviews + merges
- [ ] fold this milestone's OBSERVE deltas (2 Spec + 3 Competency per lock task, 4 total tasks) into
  `PROJECT.md` at the next `add.py fold` pass — not required to close, but don't let them go stale
- [ ] tag / publish per `release.md` when this milestone is bundled into a release (human-run)
