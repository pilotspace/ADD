# MILESTONE: installer-polish — round out the global-home and installer lane

goal: complete the global lane: data restore, orphan prune, update --global concurrency + path-safety, reconcile roll-up, and a reusable PTY test helper
rationale: sub-milestone — harvested from the global-install / global-data / installer SPEC deltas (global-data, global-install, heal-reconcile, installer-prompts). Grouped because they all round out the global-home + installer lane that shipped one-way in 1.7.x.
stage: mvp · status: queued · created: 2026-06-26T10:28:42+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) the RESTORE direction — `--from-global-data` rehydrates a project's user-data from the home on a fresh clone, + a `prune-data` orphan cleanup, (2) `update --global` made concurrency-safe (file-lock) and path-validated (reject traversal / non-project registry paths), (3) a heal-reconcile manifest/file-count check + an "N restored / M refreshed" roll-up, (4) a reusable PTY test helper so interactive happy-paths are CI-automatable.
Out: a richer pip interactive prompt lib (questionary/rich) — deferred by the standing single-stdlib-input decision; a cross-agent global-skill map (Claude-only home skill stays as-is); registry.json object-schema enrichment unless per-project metadata is actually needed.

## Shared decisions & glossary deltas   (living — every task must honor these)
- the home is a one-way backup today; RESTORE must be explicit and non-destructive (never clobber a newer local without intent).
- corrupt registry / out-of-allowlist path = LOUD fail, never a silent reconcile-into.
- atomic single-writer for any home mutation; a file-lock serializes concurrent `update --global`.

## Shared / risky contracts (freeze these first)
- the `--from-global-data` restore semantics (what wins on conflict, what is byte-copied) -> owning task `global-data-restore`
- the registered-path validation rule (allowlist / traversal rejection) -> owning task `global-update-harden`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] global-data-restore   depends-on: none   — `--from-global-data` (or `init` detecting a matching `<home>/data/<key>`) rehydrates user-data on a fresh clone; `prune-data` removes orphaned snapshots; pick one symlink rule for cross-twin byte-parity
- [ ] global-update-harden  depends-on: none   — file-lock around `update --global` (serialize concurrent runs); validate registered project paths (reject traversal / non-project dirs) before reconciling
- [ ] reconcile-rollup      depends-on: none   — manifest/file-count check that heals a partially-gutted present tree; a one-line "N restored / M refreshed" reconcile summary
- [ ] pty-test-helper       depends-on: none   — extract a reusable PTY test helper; route installer-prompts + agent-detect happy-paths through it for CI coverage

## Exit criteria (observable; map each to the task that delivers it)
- [ ] a fresh clone can rehydrate its user-data from the home; `prune-data` removes orphans   (← global-data-restore)
- [ ] concurrent `update --global` serialize; an out-of-allowlist registry path is rejected   (← global-update-harden)
- [ ] reconcile heals a partially-gutted tree and prints an "N restored / M refreshed" summary (← reconcile-rollup)
- [ ] an interactive installer happy-path runs under a committed PTY test in CI               (← pty-test-helper)

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
