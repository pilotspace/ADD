# TASK: Restore user-data from the global home on a fresh clone (--from-global-data) + prune-data orphan cleanup

slug: global-data-restore · created: 2026-06-28 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `add-method/src/add_method/_installer.py:install(target, *, as_global, as_global_data, …) -> int` (775-933) — installer public entry; `as_global_data` IMPLIES `as_global` + ONE-WAY persists user-data to `<home>/data/<key>`. The restore direction is its INVERSE (home→project) — add an `as_global_data_restore` (or `from_global_data`) param + restore branch.
- `add-method/src/add_method/_installer.py:_persist_data(home, project_abspath) -> bool` (705-725) — the one-way snapshot to mirror in reverse: clean-replace `<home>/data/<key>` from `<proj>/.add/` user-data; `shutil.copytree`/`copyfile` after `rmtree`. NEW `_restore_data(home, project)` is its inverse, made NON-destructive.
- `add-method/src/add_method/_installer.py:resolve_global_home(env=None) -> Path` (597-610) — `ADD_HOME → XDG_DATA_HOME/add → <HOME>/.add`; pure/total/never-throws; reads HOME from injected `env`. Restore + prune-data resolve the home through this.
- `add-method/src/add_method/_installer.py:data_key(project_abspath) -> str` — `<sanitized-basename>-<sha1(abspath)[:12]>`; snapshot dir is `<home>/data/<key>/`. Twin `bin/cli.js:dataKey()`. prune-data enumerates `<home>/data/*` and compares against keys derived from the live registry.
- `add-method/src/add_method/_installer.py:_is_user_data(name) / _DATA_EXCLUDE` — the user-data filter (excludes `tooling`/`docs`/`.update-cache`/STAMP/`scope-snapshot*`/`*.bak.json`); restore writes back only these.
- `add-method/src/add_method/_installer.py:_read_registry(home)/_write_registry(home,paths)/_registry_path(home)` — flat JSON list of project roots; `_read_registry` raises `ValueError("registry_corrupt:…")` (LOUD fail, file left intact); `_write_registry` atomic temp+`os.replace`, de-duped. prune-data reads the registry to know which snapshots are still owned.
- `add-method/src/add_method/_cli.py:main()` (112 lines) — pip `pilotspace-add` dispatch (`if cmd == "init"/"update"`); add `--from-global-data` to init + a `prune-data` branch.
- `add-method/bin/cli.js` (1040) — the npm twin; ALL of the above need a parity twin here (enforced by `ParityDataTest`).

Context (working folder):
- `.add/milestones/installer-polish/MILESTONE.md` — owns this task; freeze-first contracts named: restore conflict/byte-copy semantics (this task) + registered-path validation (`global-update-harden`). Shared decisions: home is one-way today → RESTORE must be EXPLICIT + NON-destructive; corrupt registry = LOUD fail; atomic single-writer.
- Tests (canonical, `add-method/tooling/`): `test_global_data.py` (207 — `ParityDataTest` asserts `cli.js`↔`_installer.py` surface-name parity: `data_key`/`dataKey`, `"data"`, `"global-data"`, `as_global_data`; D1-D8 snapshot cases; `data_unwritable` fail-closed) · `test_global_install.py` (229 — home resolution G1, registry corrupt-loud-fail, no state.json in home) · `test_update.py` · `test_pty_clack.py`. NEW `test_global_restore.py` + prune-data coverage follow the `test_<area>.py` convention; no restore/prune test exists yet.
- Data layout: `<home>/registry.json` (project-root list) + `<home>/data/<key>/` (per-project user-data snapshot) + `<home>/` managed-layer (tooling/docs/skill) + stamp file.

Honors (patterns / conventions):
- **One-way today → restore is the explicit, non-destructive inverse** (MILESTONE shared decision): never clobber a newer local without intent; write a `.bak` before any destructive mutation of a user-owned file (established design-for-failure precedent).
- **NO-EXEC / installer drops files only** — restore COPIES files; it must NOT spawn `add.py init`. (`_installer.py` header: "DROPS FILES ONLY".)
- **Atomic single-writer + fail-closed** — verify all sources exist BEFORE touching the target; corrupt registry → `_fail(...)` + return 1, file LEFT INTACT (read-before-write). Helpers: `_installer.py:_fail(msg)->int`; byte-copy via `shutil.copytree`/`copyfile` (clean-replace), `add_engine/io_state.py:_atomic_write_bytes` for atomic per-file copies.
- **cli.js ↔ Python parity** — every new installer symbol needs a twin in `bin/cli.js` or a parity test that acknowledges the divergence (`ParityDataTest`).
- **Hermetic tests** — inject `env`/`bundled` (never touch the real `$HOME`); no Python subprocess spawn (asserted by D7).

Anchors the contract cites: `install()` (+ new `as_global_data_restore`/`--from-global-data`) · NEW `_restore_data(home, project_abspath) -> bool` · NEW `prune-data` subcommand (+ `_prune_data(home) -> (kept, removed)`) · `resolve_global_home` · `data_key` · `_read_registry`/`_write_registry` · `_is_user_data` · `bin/cli.js` parity twins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: global-data-restore — rehydrate a project's user-data from the global home on a fresh clone (`--from-global-data`), the non-destructive inverse of the one-way snapshot; plus `prune-data` to clean orphaned snapshots.
Framings weighed: fill-gaps + --force-with-bak (chosen) · backup-then-overwrite-always · newer-wins-by-mtime (rejected — mtime meaningless on a fresh clone)
Must:
<must>
  - `pilotspace-add init --from-global-data` (+ npm twin `npx @pilotspace/add init --from-global-data`) runs the normal managed-layer install AND restores user-data from `<home>/data/<key>` into the target `.add/`; home via `resolve_global_home`, key via `data_key(target_abspath)`.
  - Restore is FILL-GAPS by default: writes only user-data entries ABSENT in the target `.add/`; a present local entry is never clobbered.
  - `--force` (with `--from-global-data`) overwrites present entries too, writing a `.bak` sidecar of each replaced entry first (`<name>.bak` for a file, `<name>.bak` dir for a directory).
  - Restore copies only the same set the snapshot captures — `_is_user_data` filter (PROJECT.md · SOUL.md · state.json · tasks/ · milestones/ …; excludes the managed layer tooling/docs + `scope-snapshot*`/`*.bak.json`).
  - Byte-copy dereferences symlinks to content (no symlink recreation) so the Python/JS twins are byte-identical; restored entries are byte-identical to the snapshot.
  - New `_restore_data(home, project_abspath, *, force=False) -> bool` is the non-destructive inverse of `_persist_data`; reached from `install(..., as_global_data_restore=True)`. Restore CONSUMES only — it does not persist back, and does not auto-register the project.
  - `pilotspace-add prune-data` (+ npm twin) lists orphaned snapshots — a `<home>/data/<key>` dir whose key is owned by NO LIVE registry entry (LIVE = a registry path that still EXISTS on disk; so BOTH an unregistered key AND a registered-but-vanished-on-disk key are orphans) — and removes NOTHING by default (dry-run); prints the orphan list + "N orphan(s); re-run with --force to remove".
  - `prune-data --force` deletes the orphaned snapshots and prints "N removed"; a snapshot whose registry path still EXISTS is never touched.
  - New `_prune_data(home, *, force=False) -> (orphans, removed)`; reads the registry and tests each owner path's on-disk existence to determine liveness. (DIVERGES from `update --global`, which KEEPS vanished — update = gentle auto-sync that never deletes; prune = explicit reclaim.)
</must>
Reject:
<reject>
  - `--from-global-data` (or `prune-data`) but no global home exists (no stamp / `<home>` absent) -> "no_global_home"  (hard fail, exit 1 — asked to act on a home that isn't there)
  - `prune-data` with a corrupt/unparseable registry -> "registry_corrupt"  (LOUD fail, exit 1, file left intact, nothing pruned)
  - restore cannot write the target `.add/` (unwritable) -> "restore_failed"  (fail-closed before partial restore)
</reject>
After:
<after>
  - restore (fill-gaps): every snapshot user-data entry absent locally now exists in `.add/`, byte-identical to the snapshot; pre-existing local entries unchanged; managed layer installed; exit 0.
  - restore (--force): all snapshot user-data entries present in `.add/`; each previously-present entry has a `.bak` sidecar written before replacement; exit 0.
  - home exists but no snapshot for this key: honest skip — warn "no snapshot for this project at <home>/data/<key>", managed layer still installed, exit 0 (NOT a reject).
  - prune-data (dry-run): orphan keys listed, `<home>/data/` byte-unchanged, exit 0.
  - prune-data (--force): orphaned snapshot dirs (unregistered + registered-but-vanished) removed; a snapshot whose registry path still exists is intact; "N removed" printed; exit 0.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `no_snapshot` (home present, no per-project snapshot) is a SOFT skip (exit 0, warn) not a hard error — lowest confidence because an explicit `--from-global-data` that finds nothing still exits 0; mirrors `_persist_data`'s "honest skip, not error"; if wrong: a user thinks restore worked when there was nothing (clear message printed, low cost).
  - [x] DECIDED (was ⚠, resolved at freeze): prune's orphan = a key owned by NO LIVE registry entry (unregistered OR registered-but-vanished-on-disk). This DIVERGES intentionally from `update --global`'s keep-vanished (D4): update never deletes; prune is the explicit reclaim.
  - [ ] `--from-global-data` ALSO runs the full managed-layer install (a fresh clone needs tooling/docs) — if a user wanted user-data-only, not supported; cost low (managed-layer drop is idempotent reconcile).
  - [ ] restore does NOT auto-register the project in the home (consume-only); if the user expects to stay synced afterward they run `--global`/`--global-data` separately; cost low.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: restore rehydrates a fresh clone from the home   # Must 1
  Given a global home with a snapshot at <home>/data/<key> holding PROJECT.md + state.json + tasks/
  And a fresh target whose .add/ has no user-data (managed layer only or absent)
  When I run `init --from-global-data` against the target
  Then the target .add/ contains PROJECT.md, state.json and tasks/ byte-identical to the snapshot
  And the managed layer (tooling/, docs/) is installed
  And the run exits 0

Scenario: fill-gaps never clobbers a present local entry   # Must 2
  Given the snapshot holds PROJECT.md (content "HOME") and SOUL.md
  And the target .add/ already has PROJECT.md (content "LOCAL") but no SOUL.md
  When I run `init --from-global-data` (no --force)
  Then SOUL.md is restored from the snapshot
  And PROJECT.md still reads "LOCAL" (untouched)
  And no .bak sidecar is written

Scenario: --force overwrites present entries, backing each up first   # Must 3
  Given the snapshot holds PROJECT.md (content "HOME")
  And the target .add/ already has PROJECT.md (content "LOCAL")
  When I run `init --from-global-data --force`
  Then PROJECT.md now reads "HOME"
  And PROJECT.md.bak reads "LOCAL" (the replaced original, backed up before replacement)

Scenario: restore copies only user-data, never the managed layer   # Must 4
  Given a snapshot dir that (defensively) also contains a tooling/ entry
  When I run `init --from-global-data`
  Then user-data entries are restored
  And no snapshot tooling/ or docs/ is copied into the target as user-data (the _is_user_data filter)

Scenario: restored bytes are identical and symlinks are dereferenced   # Must 5
  Given the snapshot holds a regular file note.md and a symlink link.md -> note.md
  When I run `init --from-global-data`
  Then target note.md is byte-identical to the snapshot
  And target link.md is a regular file holding note.md's content (not a symlink)

Scenario: restore consumes only — no persist-back, no auto-register   # Must 6
  Given a global home with a snapshot for the target and a registry NOT listing the target
  When I run `init --from-global-data`
  Then user-data is restored into the target
  And <home>/data/<key> is byte-unchanged (no persist-back)
  And registry.json still does not list the target (no auto-register)

Scenario: prune-data dry-run lists orphans and removes nothing   # Must 7
  Given <home>/data has snapshot dirs for key-A (registered, its path EXISTS on disk) and key-B (no registry entry)
  When I run `prune-data` (no --force)
  Then the output names key-B as an orphan and prints "1 orphan ... --force to remove"
  And both <home>/data/key-A and <home>/data/key-B still exist (nothing removed)
  And the run exits 0

Scenario: prune-data --force removes orphans, keeps the live owner   # Must 8 + Must 9
  Given <home>/data has snapshot dirs for key-A (registered, path EXISTS) and key-B (no registry entry)
  When I run `prune-data --force`
  Then <home>/data/key-B is removed
  And <home>/data/key-A still exists (its registry path exists → LIVE owner, untouched)
  And the output prints "1 removed"

Scenario: registered-but-vanished snapshot is RECLAIMED by prune   # orphan = unregistered OR registered-but-gone
  Given <home>/data has a snapshot for key-V whose registry path no longer EXISTS on disk
  And <home>/data also has key-A whose registry path still exists
  When I run `prune-data --force`
  Then <home>/data/key-V is removed (no LIVE owner → orphan, the explicit reclaim)
  And <home>/data/key-A still exists (LIVE owner, kept)

Scenario: home exists but no snapshot for this project — honest skip   # After: soft skip, not reject
  Given a global home exists but <home>/data/<key> is absent for the target
  When I run `init --from-global-data`
  Then a warning "no snapshot for this project" is printed
  And the managed layer is still installed
  And the run exits 0 (not an error)

Scenario: REJECT — no global home   # Reject: no_global_home
  Given no global home exists (no stamp / <home> absent)
  When I run `init --from-global-data` (or `prune-data`)
  Then the run fails with error "no_global_home" and exits 1
  And nothing is written to the target .add/ user-data and no home is created

Scenario: REJECT — corrupt registry on prune   # Reject: registry_corrupt
  Given <home>/registry.json is present but unparseable
  When I run `prune-data --force`
  Then the run fails LOUD with error "registry_corrupt" and exits 1
  And registry.json is left byte-intact
  And no snapshot dir under <home>/data is removed

Scenario: REJECT — target .add/ unwritable during restore   # Reject: restore_failed
  Given a snapshot exists for the target but the target .add/ cannot be written
  When I run `init --from-global-data`
  Then the run fails with error "restore_failed" and exits 1
  And no partial / half-restored user-data is left in the target
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# ── Python installer surface ── add-method/src/add_method/_installer.py
install(target=".", *, force=False, …, as_global=False, as_global_data=False,
        as_global_data_restore=False, rule_file=False, env=None) -> int
  as_global_data_restore=True  ->  install managed layer  AND  _restore_data(home, target, force=force)
  returns 0 ok (incl. honest no-snapshot skip) · 1 error · 130 user-cancel
  (as_global_data_restore is independent of as_global/as_global_data; consume-only, no register, no persist)

_restore_data(home: Path, project_abspath, *, force=False) -> bool
  source: <home>/data/<key>  (key = data_key(project_abspath));  dest: <project>/.add
  copies ONLY _is_user_data(name) entries; deref symlinks to content (regular file out)
  fill-gaps (force=False): write only entries ABSENT in dest; present entry untouched, no .bak
  force=True: also overwrite a present entry, writing <name>.bak (file) / <name>.bak dir first
  returns True if ≥1 entry restored, False if nothing to restore (snapshot dir absent or empty)
  raises OSError on an unwritable dest  ->  caller maps to "restore_failed"

_prune_data(home: Path, *, force=False) -> (orphans: list[str], removed: list[str])
  live  = { data_key(p) for p in _read_registry(home) if Path(p).exists() }   # owner path must EXIST
  orphans = sorted <home>/data/<key> dirs whose key NOT in live
            (unregistered OR registered-but-vanished-on-disk — BOTH reclaimed; diverges from update's keep-vanished)
  force=False (dry-run): removed == []          ;  data/ byte-unchanged
  force=True            : removed == orphans     ;  each orphan dir shutil.rmtree'd
  reads _read_registry(home) FIRST — a ValueError("registry_corrupt:…") propagates (LOUD, no removal)

# ── CLI surface ── add-method/src/add_method/_cli.py  +  parity twin add-method/bin/cli.js
init  [--from-global-data] [--force] [--global] [--global-data] …
   --from-global-data  ->  install(..., as_global_data_restore=True, force=<--force present>)
prune-data  [--force]
   ->  home = resolve_global_home(env); if no stamp -> "no_global_home"/exit 1
       (orphans, removed) = _prune_data(home, force)
       dry-run: print each orphan + "N orphan(s); re-run with --force to remove"
       --force : print "N removed"

# ── Error responses (one per §1 Reject code) ──  stderr "error: <code>", exit 1
no_global_home    restore+prune asked but no home/stamp  ->  no target user-data written, no home created
registry_corrupt  prune, registry present-but-unparseable ->  registry.json byte-intact, no data/ dir removed
restore_failed    dest .add/ unwritable during restore    ->  no partial/half-restored user-data left

Schema (filesystem — no DB):
  <home>/data/<key>/      per-project user-data SNAPSHOT      (restore source · prune unit · read-only to restore)
  <home>/registry.json    flat JSON list of project roots     (ownership oracle for prune; corrupt = LOUD)
  <project>/.add/<entry>  restore DEST (user-data only)        (fill-gaps writes absent; --force overwrites)
  <project>/.add/<name>.bak   backup sidecar                   (written before a --force overwrite only)
```

Least-sure flag surfaced at freeze:
  ⚠ [spec] `no_snapshot` (home present, no per-project snapshot) is a SOFT skip (warn, exit 0), not a reject —
     mirrors `_persist_data`'s honest-skip. If wrong, an explicit restore that finds nothing exits 0 (low cost).
  • [DECIDED at freeze] prune's "orphan" = a data key owned by NO LIVE registry entry (unregistered OR
     registered-but-vanished-on-disk) — both reclaimed. Intentionally DIVERGES from `update --global`'s
     keep-vanished (D4): update is gentle auto-sync (never deletes); prune is the explicit reclaim.

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: ~90% of the new symbols (`_restore_data`, `_prune_data`, `prune_data`, the `install` restore branch). 17 tests; RED for the right reason: 16 missing-implementation errors (`_restore_data`/`_prune_data`/`prune_data` AttributeError · `as_global_data_restore` TypeError) + 1 parity FAIL (cli.js/_cli.py not yet wired).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - RestoreTest.test_restore_rehydrates_fresh_clone (Must 1): seed snapshot · install(as_global_data_restore) · assert PROJECT/state/tasks byte-identical + managed layer + exit 0
  - RestoreTest.test_fill_gaps_never_clobbers_present (Must 2): local PROJECT="LOCAL", SOUL absent · restore · assert SOUL filled, PROJECT unchanged, NO .bak
  - RestoreTest.test_force_overwrites_with_bak (Must 3): --force · assert PROJECT="HOME" + PROJECT.md.bak="LOCAL"
  - RestoreUnitTest.test_filter_excludes_managed (Must 4): snapshot polluted with tooling/ · _restore_data · assert PROJECT restored, tooling filtered out
  - RestoreUnitTest.test_symlinks_dereferenced (Must 5): snapshot symlink · assert restored as regular file w/ content (skips if no symlink)
  - RestoreTest.test_restore_consumes_only (Must 6): assert registry NOT extended + snapshot byte-unchanged
  - PruneTest.test_dry_run_lists_removes_nothing (Must 7): assert orphan listed, removed==[], both dirs survive
  - PruneTest.test_force_removes_orphan_keeps_live (Must 8+9): assert orphan removed, live owner kept
  - PruneTest.test_reclaims_registered_but_vanished (orphan rule): registered-but-gone removed, live kept
  - RestoreTest.test_no_snapshot_is_soft_skip (After): home present, no snapshot · assert exit 0 + managed layer (unchanged: not a reject)
  - RestoreTest.test_no_global_home_rejects (Reject): no home · assert exit≠0 + nothing restored
  - RestoreUnitTest.test_unwritable_dest_raises (Reject restore_failed): dest=.add-as-file · assert OSError + (no partial)
  - PruneTest.test_corrupt_registry_loud_no_removal (Reject registry_corrupt): assert ValueError + registry byte-intact + no snapshot removed
  - PruneTest.test_prune_data_no_global_home_rejects (Reject): prune_data, no home · assert exit≠0
  - +RestoreUnitTest.test_nothing_to_restore_returns_false · PruneTest.test_prune_data_command_force_removes · ParityRestoreTest.test_parity_surface (cli.js + _cli.py + _installer.py surface names)
</test_plan>

Tests live in: `add-method/tooling/test_global_restore.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/src/add_method/_cli.py` `add-method/bin/cli.js`
Strategy (ordered batches): 1. `_restore_data` in `_installer.py` — the non-destructive inverse copy (fill-gaps · `--force` writes `<name>.bak` then overwrites · deref symlinks to content · verify snapshot dir before writing dest · raise→`restore_failed`). 2. wire `as_global_data_restore` into `install()` — install managed layer then restore; consume-only (no register, no persist); honest no-snapshot skip (exit 0); `no_global_home` hard fail. 3. `_prune_data` — orphan = data key owned by NO registry entry (registered-but-vanished kept); read registry FIRST (corrupt→propagate LOUD); dry-run lists, `force` rmtree's. 4. `_cli.py` — init `--from-global-data` flag + `prune-data` subcommand branch. 5. `bin/cli.js` parity twins (`restoreData`/`pruneData`, `--from-global-data`, `prune-data`) — keep `ParityDataTest` green.
Known-problem fixes: `ParityDataTest` asserts cli.js↔_installer.py surface-name parity → add matching tokens BOTH sides (else red) · engine pins NOT touched — installer is outside the `add_engine/` digest; do NOT re-pin ENGINE_MD5/ENGINE_PKG_MD5 (confirmed via engine_manifest.py) · hermetic tests inject `env=` home, never touch real `$HOME`, no Python subprocess spawn (D7) · fail-closed ORDER: verify home/snapshot + read registry BEFORE any mutation · symlink deref via `shutil.copyfile`/`copytree(symlinks=False)` so a link becomes a real file (byte-parity with JS).
Strategy actually used: as planned (batches 1-5), with one robustness deviation: `_restore_data` resolves the project path INTERNALLY (`Path(project_abspath).resolve()`) for the snapshot key — snapshots are always keyed by the resolved abspath (install resolves before persist), so a unit caller passing an unresolved path now matches on macOS (`/var`→`/private/var`). cli.js mirrors via `fs.realpathSync` in `installGlobalDataRestore` (its established pattern). No engine pin touched (installer outside the digest).
Safety rule (feature-specific): write a `<name>.bak` BEFORE any destructive overwrite; verify the snapshot source exists before touching the dest; prune reads the registry (fail-closed on corrupt) before removing anything — no partial restore, no orphan removed on a bad read.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2252/0 (baseline 2235 + 17 new); global suites 59/0
- [x] coverage did not decrease — 17 new tests added; only additive (no test removed/weakened)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; test_global_restore.py written in the TESTS phase, unchanged during build
- [x] the green was EARNED, not gamed — adversarial refute-read VERDICT: EARNED (no overfit / vacuous / stubbed; all real temp-dir I/O, zero mocks). 3 coverage gaps surfaced, none a cheat — disposition below + §7
- [x] concurrency / timing — single-process file ops; no NEW concurrency class beyond the existing one-way `_persist_data` (no home file-lock). The home file-lock is the SIBLING task `global-update-harden`'s declared scope; NOTE in §7, not a blocker
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (os/shutil/json/pathlib already imported; cli.js fs/path/crypto already required); entry names come from `iterdir()` (basenames, never `..`/`/`) → no path traversal; `_is_user_data` blocks managed names
- [x] layering & dependencies follow CONVENTIONS.md — mirrors installer idioms (`_fail`/`_log`, byte-copy clean-replace, fail-closed read-before-write, cli.js↔pip parity twins, NO-EXEC: copies files, never spawns add.py)
- [x] a person reviewed and approved the change — auto-resolved under `autonomy: auto` (Tin Dang accountable); no security/blocking residue. Human froze §3; holes disclosed below

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a fresh-clone target with no user-data ends with PROJECT.md/state.json/tasks restored byte-identical to the snapshot + managed layer present — `test_restore_rehydrates_fresh_clone` asserts content + `tooling/add.py` present (green)
- [x] fill-gaps leaves a present local entry byte-unchanged and writes NO .bak; --force overwrites it and leaves a `PROJECT.md.bak` of the original — `test_fill_gaps_never_clobbers_present` + `test_force_overwrites_with_bak` (green); the DIRECTORY-entry --force path (tasks/ → tasks.bak/) verified manually at the gate (fill-gaps keeps local dir; --force backs original to tasks.bak/, restores all files)
- [x] a snapshot symlink lands as a regular file holding the target's content (no symlink) — `test_symlinks_dereferenced` asserts `is_symlink()` False + content (green)
- [x] prune dry-run removes nothing; --force removes the unregistered AND the registered-but-vanished keys, keeps ONLY the live one — `test_dry_run_lists_removes_nothing` + `test_force_removes_orphan_keeps_live` + `test_reclaims_registered_but_vanished` (green)
- [x] corrupt registry on prune → ValueError/exit 1, registry.json byte-unchanged, no data/ dir removed — `test_corrupt_registry_loud_no_removal` byte-compares the registry + asserts the orphan survives (green)
- [x] no_global_home / restore_failed surface the named error + exit≠0 with nothing partially written — `test_no_global_home_rejects` (nothing restored) + `test_prune_data_no_global_home_rejects` + `test_unwritable_dest_raises` (OSError before any write) (green)
- [x] `ParityRestoreTest` green (cli.js + _cli.py expose the surface names) AND the JS path proven BEHAVIORALLY (not just strings): a subprocess smoke ran `node cli.js init --from-global-data` (rehydrated PROJECT.md + tasks/), `prune-data` dry-run (lists, removes nothing), `prune-data --force` (1 removed), and `prune-data` with no home (exit 1, no_global_home)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol is referenced: `_restore_data`←install():1044 + tests · `_prune_data`←prune_data():802 + tests · `prune_data`←_cli.py:63 + tests · `as_global_data_restore`←_cli.py:119, used at install():939/1040 · cli.js `restoreData`←installGlobalDataRestore · `installGlobalDataRestore`/`installGlobalData`... ←cmdInit · `pruneData`←cmdPruneData←main dispatch · `isSymlink`←restoreData (grep-confirmed + subprocess-exercised)
- [x] DEAD-CODE (code) — no new unused/orphaned symbol; every new function is on a reachable call path (proven by the subprocess smoke + the 17 unit tests)
- [ ] SEMANTIC (prose / non-code) — n/a (code task)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent (general-purpose refute-read) · adversarially checked: probed all 3 cheat classes — OVERFIT (no literal-name special-casing; `_is_user_data`/`data_key`/`_prune_data` fully general), VACUOUS (every assert probes state produced by real production I/O, not test-written), STUBBED (zero mocks; all real temp-dir calls). Surfaced 3 coverage GAPS (not cheats), disposed: (1) mid-write atomicity — beyond the contract's `restore_failed`="dest unwritable" scope (which fails on the first write → no partial); filed §7 hardening delta. (2) --force-on-directory — verified manually at the gate (green); committed-test filed §7. (3) JS behavioral parity — closed by the subprocess smoke above.

### GATE RECORD
Outcome: PASS
Auto-resolved under `autonomy: auto` — evidence complete (2252/0), refute-read EARNED, no security/concurrency/architecture residue that blocks (the one concurrency note is the sibling task's declared scope). 3 coverage gaps disclosed + filed as §7 open deltas; none a cheat or a contract violation.
Reviewed by: Tin Dang (accountable owner; froze §3 @ v1) · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): restore_failed / no_global_home reject-rate on real `--from-global-data` runs; how often `prune-data` finds orphans (registry churn); whether a fresh-clone restore is the actual onboarding path users take.

### Decisions (ADR)
- [AI] specify — chose fill-gaps + --force-with-bak; rejected backup-then-overwrite-always · newer-wins-by-mtime (rejected — mtime meaningless on a fresh clone)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned (batches 1-5), with one robustness deviation: `_restore_data` resolves the project path INTERNALLY (`Path(project_abspath).resolve()`) for the snapshot key — snapshots are always keyed by the resolved abspath (install resolves before persist), so a unit caller passing an unresolved path now matches on macOS (`/var`→`/private/var`). cli.js mirrors via `fs.realpathSync` in `installGlobalDataRestore` (its established pattern). No engine pin touched (installer outside the digest).
- [AI] verify — gate PASS (reviewed by Tin Dang (accountable owner; froze §3 @ v1))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] commit a test for `--force` restore on a DIRECTORY entry (tasks/ → tasks.bak/) — code path verified manually at the gate but has no committed test (evidence: refute-read Hole 2).
- [SPEC · open] harden `_restore_data`/`restoreData` mid-write atomicity (stage-then-commit) so a disk-full on the Nth entry leaves no partial restore — today it's fail-closed only for an unwritable dest (evidence: refute-read Hole 1).
- [SPEC · open] add an npm BEHAVIORAL test (subprocess) for restore + prune to replace the structural-only `ParityRestoreTest` — the cli.js path is proven by a manual smoke, not a committed test (evidence: refute-read Hole 3).
- [SPEC · open] a home file-lock to serialize concurrent `prune-data` / `update --global` (two `prune-data --force` could race on rmtree) — belongs to the sibling task `global-update-harden` (evidence: §6 concurrency note).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · open] a hermetic unit test that keys on an UNresolved tmp path misses a snapshot keyed on the RESOLVED path on macOS (`/var`→`/private/var`) — key on the resolved abspath in BOTH the helper and the impl, or the suite is green-on-Linux/red-on-macOS (evidence: 3 RestoreUnitTest red until `_restore_data` resolved internally).
- [ADD · open] a literal `<…>` token in a §6 Build-expectations bullet (e.g. a backticked `<name>.bak`) trips `_section_unfilled`'s placeholder regex → the build-expectations gate false-fires `build_expectations_unfilled` — write concrete names, never `<placeholder>`-shaped prose (evidence: first tests→build advance rejected on the `<name>.bak` bullet).
