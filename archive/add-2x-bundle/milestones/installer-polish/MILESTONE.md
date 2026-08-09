# MILESTONE: installer-polish — round out the global-home and installer lane

goal: complete the global lane: data restore, orphan prune, update --global concurrency + path-safety, and a reconcile roll-up. (The reusable PTY test helper was DEFERRED to a standalone task — todo #24 — so this milestone closes at 3/4; see Scope.)
rationale: sub-milestone — harvested from the global-install / global-data / installer SPEC deltas (global-data, global-install, heal-reconcile, installer-prompts). Grouped because they all round out the global-home + installer lane that shipped one-way in 1.7.x.
stage: mvp · status: queued · created: 2026-06-26T10:28:42+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) the RESTORE direction — `--from-global-data` rehydrates a project's user-data from the home on a fresh clone, + a `prune-data` orphan cleanup, (2) `update --global` made concurrency-safe (file-lock) and path-validated (reject traversal / non-project registry paths), (3) a heal-reconcile manifest/file-count check + an "N restored / M refreshed" roll-up.
Out: (4) a reusable PTY test helper for interactive happy-paths — DEFERRED 2026-06-28 (Tin) to a standalone milestone-free task, captured as todo #24 (it is independent of the global-lane trio and gates nothing here); a richer pip interactive prompt lib (questionary/rich) — deferred by the standing single-stdlib-input decision; a cross-agent global-skill map (Claude-only home skill stays as-is); registry.json object-schema enrichment unless per-project metadata is actually needed.

## Shared decisions & glossary deltas   (living — every task must honor these)
- the home is a one-way backup today; RESTORE must be explicit and non-destructive (never clobber a newer local without intent).
- corrupt registry / out-of-allowlist path = LOUD fail, never a silent reconcile-into.
- atomic single-writer for any home mutation; a file-lock serializes concurrent `update --global`.

## Shared / risky contracts (freeze these first)
- the `--from-global-data` restore semantics (what wins on conflict, what is byte-copied) -> owning task `global-data-restore`
- the registered-path validation rule (allowlist / traversal rejection) -> owning task `global-update-harden`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] global-data-restore   depends-on: none   — `--from-global-data` (or `init` detecting a matching `<home>/data/<key>`) rehydrates user-data on a fresh clone; `prune-data` removes orphaned snapshots; pick one symlink rule for cross-twin byte-parity   (gate PASS · commit bbc8562)
- [x] global-update-harden  depends-on: none   — file-lock around `update --global` (serialize concurrent runs); validate registered project paths (reject traversal / non-project dirs) before reconciling   (gate PASS · commit da0d6b2)
- [x] reconcile-rollup      depends-on: none   — manifest/file-count check that heals a partially-gutted present tree; a one-line "N restored / M refreshed" reconcile summary   (gate PASS · commit 62d2e5e)
- [~] pty-test-helper       depends-on: none   — DEFERRED (todo #24, standalone) — extract a reusable PTY test helper; route installer-prompts + agent-detect happy-paths through it for CI coverage

## Exit criteria (observable; map each to the task that delivers it)
- [x] a fresh clone can rehydrate its user-data from the home; `prune-data` removes orphans   (← global-data-restore)
- [x] concurrent `update --global` serialize; an out-of-allowlist registry path is rejected   (← global-update-harden)
- [x] reconcile heals a partially-gutted tree and prints an "N restored / M refreshed" summary (← reconcile-rollup)
- DEFERRED — an interactive installer happy-path runs under a committed PTY test in CI         (← pty-test-helper → todo #24; out of scope, see Scope)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : the INSTALLER twins only — `add-method/src/add_method/_installer.py` + `_cli.py` and `add-method/bin/cli.js`. Added: `install --from-global-data` + `_restore_data`/`prune_data` + `prune-data` CLI (restore direction); `_update_lock`/`acquireUpdateLock` O_EXCL home lock + `_valid_registry_path` path validation around `update --global`; `_tree_files`/`treeFiles` + file-level `{restored,refreshed}` roll-up in `_clean_replace`/`_reconcile`/`update`. The ENGINE (`add.py` / `add_engine/*`) is UNTOUCHED — ENGINE_MD5 6cc73630 + package digest unchanged across all 3 tasks (the installer is outside both pins).
- skill   : untouched.
- book    : untouched.

### Cross-task evidence   (one row per task)
- global-data-restore  : gate=PASS · tests=17 green (test_global_restore.py) · residue=none · refute-read EARNED
- global-update-harden : gate=PASS (risk:high, human-signed) · tests=15 green (test_global_update_harden.py) · residue=none · refute-read CAUGHT a real cross-twin lock bug → re-froze v2 (O_EXCL both twins) → 2nd reviewer FIX-CONFIRMED
- reconcile-rollup     : gate=PASS · tests=12 green (test_reconcile_rollup.py) · residue=none · refute-read forced a v1→v2 INV correction (no code change) → independent reviewer FIX-CONFIRMED
- full suite at close: 2279 green / 0 failed · `add.py check` 460/0 · `audit` clean (pre-existing measure-not-block warnings only).

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each (in-scope) Exit criterion is satisfied: criterion 1 ← global-data-restore row · criterion 2 ← global-update-harden row · criterion 3 ← reconcile-rollup row. Criterion 4 (PTY test helper) is DEFERRED out of scope (todo #24) — it is independent of the global-lane trio and gated nothing.
- goal: complete the global lane (restore · prune · update --global concurrency+path-safety · reconcile roll-up). Proof: the three gate-PASS rows above ship all four global-lane behaviors in BOTH installer twins, 2279/0 green, engine pins unchanged. The PTY helper (a test-infra nicety, not a global-lane behavior) is deferred without affecting the goal.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
