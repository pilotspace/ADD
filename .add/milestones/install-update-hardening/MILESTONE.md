# MILESTONE: Install/update hardening — atomic + concurrency-safe writes

goal: add.py init/update (both --global and project-scope, pip+npm twins) survive a crash or a concurrent run without leaving a half-written .add/ tree or a wedged lock
rationale: <why this scope — the confirmed intake classification (bucket + reason)>
stage: mvp · status: active · created: 2026-07-02T14:46:06+00:00
release: pending

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
- [ ] project-scope-atomic-reconcile   depends-on: none     — crash-safe stage-then-commit for
      the managed-tree reconcile copy (`_clean_replace`/`cleanReplaceTree`); CONTRACT drafted
- [ ] global-lock-followups   depends-on: none     — stale `.update.lock` self-heal +
      `install --global` lock coverage + an opt-in `--lock-timeout` CI mode; CONTRACT drafted
- [ ] global-data-restore-harden   depends-on: none     — crash-safe stage-then-commit for the
      user-data persist/restore path (`_persist_data`/`_restore_data`) + 2 committed test gaps;
      CONTRACT drafted
- [ ] project-scope-install-lock   depends-on: project-scope-atomic-reconcile   — a NEW
      per-project lock serializing concurrent `install`/`update` runs against the same
      project-scope destination; not yet drafted (waits on its dependency's evidence)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A simulated mid-copy failure during `add.py init`/`update` never leaves `.add/tooling`, `.add/docs`, `.add/personas-teacher`, or `.claude/skills/add` half-copied — self-heals next run (verify: project-scope-atomic-reconcile §4 mid-copy-failure + self-heal scenarios)   (← project-scope-atomic-reconcile)
- [ ] A simulated mid-write failure during `update --global`'s re-persist, or `init --from-global-data`/`--force` restore, never leaves a snapshot/restored entry half-written — self-heals next call (verify: global-data-restore-harden §4 mid-write-failure + self-heal scenarios)   (← global-data-restore-harden)
- [ ] A SIGKILL'd `update --global`/`install --global` never wedges a future global op — the stale lock self-heals, `install --global` is now lock-serialized, an opt-in `--lock-timeout` lets CI wait (verify: global-lock-followups §4 stale-lock + install-global-locked + timeout scenarios)   (← global-lock-followups)
- [ ] Two concurrent `install`/`update` runs against the SAME project-scope destination cannot interleave writes — one waits or fails cleanly (verify: project-scope-install-lock §4 concurrent-run scenarios, once drafted)   (← project-scope-install-lock)

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
