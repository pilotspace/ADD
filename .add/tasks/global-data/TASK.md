# TASK: --global-data opt-in: per-project data persisted under the global home, keyed by path

slug: global-data · created: 2026-06-17 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
  - `add-method/src/add_method/_installer.py:install/_update_global/resolve_global_home/_clean_replace` — pip twin (shipped in global-install). install()/update() already take `env`+`as_global`; add `as_global_data` + a data-persist helper. `<home>` + registry + `_reconcile_global` already exist.
  - `add-method/bin/cli.js:cmdInit/cmdUpdateGlobal/installGlobal/resolveGlobalHome` — npm twin (parity). parseArgs is where `--global-data` lands.
  - `add-method/src/add_method/_cli.py:main` — pip arg routing; add `--global-data` to the init parser (update --global re-persists automatically — no separate update flag).
  - `add-method/tooling/add.py:find_root` — resolves the project DATA root by cwd-walk for `.add/state.json`. NOT modified: the persisted snapshot is a BACKUP; the engine still reads the LOCAL `.add` (the self-contained/git-tracked default is untouched).
Context (working folder):
  - The MANAGED layer = skill (`.claude/skills/add`) + `.add/tooling` + `.add/docs` (ship-controlled). USER-DATA = the rest of `.add/`: `state.json` · `PROJECT.md` · `SOUL.md` · `CONVENTIONS.md` · `GLOSSARY.md` · `milestones/` · `tasks/` · `archive/` · `RELEASES.md`. Transient/managed-meta (NOT user-data): `.add-version` · `.update-cache/` · `scope-snapshot*` · `*pre-archive-bak*` · `*.bak.json`.
  - global-install (just shipped, task 4) gives `<home>` + `<home>/registry.json` (flat list of abs project roots) + `resolve_global_home` + `_reconcile_global`. global-data ADDS a `<home>/data/<key>/` snapshot of USER-DATA, keyed by abspath — strictly additive, opt-in.
  - A FRESH install drops files only (no init) → a brand-new project has NO user-data yet → `init --global-data` there honestly SKIPS ("nothing to persist"). Persist is meaningful for an already-initialised project (has state.json) or via `update --global` re-persist.
Honors (patterns / conventions):
  - managed↔user-data boundary (the snapshot copies ONLY user-data, NEVER the managed trees) · OPT-IN (default leaves data purely local + git-tracked) · drops-files-only + no-Python-spawn (persist COPIES existing data, never authors a new state.json) · npm↔pip parity (identical key derivation · data layout · include/exclude rule) · design-for-failure (no `.add`/no user-data → skip with a notice, not an error; unwritable `<home>/data` → clear fail) · clean-replace the snapshot (no orphans) · keep the registry a FLAT list (the data-dir's existence is the per-project opt-in record — no registry-shape churn).
Anchors the contract cites: `data_key(abspath)`/`dataKey()` (filesystem-safe `<basename>-<sha1[:12]>`, identical on both twins); `_persist_data(home, project)`/`persistData()` (clean-replace USER-DATA → `<home>/data/<key>/`, skip-if-empty, raise→`data_unwritable`); `install(as_global_data=…)` (implies `--global`); `update --global` re-persist of already-snapshotted+existing projects; the `--global-data` flag on both twins + `_cli.py`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `--global-data` opt-in — persist a project's USER-DATA (not the managed layer) under `<home>/data/<key>` keyed by absolute project path, so the global ADD home remembers each opting project's data; the per-project local + git-tracked default is untouched
Framings weighed: ONE-WAY persist/snapshot keyed by path (chosen — additive, no engine change, preserves the self-contained default; reuses the home from global-install) · REDIRECT the engine's find_root to read/write the home (rejected: breaks self-containment + touches the engine — explicitly OUT per the milestone) · ENRICH registry.json to objects carrying a per-project data flag (rejected for mvp: churns the just-frozen flat-list registry + the propagation loop; the data-dir's existence is a simpler, backward-compatible opt-in record)
Must:
<must>
  - D1 `data_key(abspath)` is PURE · total · deterministic · collision-resistant · filesystem-safe: `<sanitized-basename>-<sha1(abspath_utf8)[:12]>`; no path separator in the result; identical on both twins.
  - D2 `init --global-data [dir]` IMPLIES `--global` (no home → nowhere to persist): it runs the full `init --global` (managed home + register + per-project drop) THEN persists dir's user-data.
  - D3 the persist copies ONLY user-data — everything under `<dir>/.add/` EXCEPT the managed trees (`tooling/`, `docs/`) and transient/managed-meta (`.add-version`, `.update-cache`, `scope-snapshot*`, `*pre-archive-bak*`, `*.bak.json`) — into `<home>/data/<data_key(dir)>/`, CLEAN-REPLACED (a file removed locally leaves no orphan in the snapshot).
  - D4 `update --global` (entry unchanged) ALSO re-persists every registered+existing project that ALREADY has a `<home>/data/<key>/` snapshot (keeps persisted data current); a vanished project is pruned from the registry but its data snapshot is KEPT (persist = the backup outlives the project dir).
  - D5 the DEFAULT is UNCHANGED: without `--global-data`, no `<home>/data` is created and data stays local + git-tracked; the managed `--global` (no data) path is also byte-unchanged.
  - D6 npm↔pip parity: identical key derivation, `<home>/data/<key>` layout, and user-data include/exclude rule.
  - D7 drops-files-only holds: persisting COPIES existing user-data; no `add.py init`, no Python spawn, NO new state.json is authored anywhere.
  - D8 design-for-failure: a project with no `.add/` (or no user-data — e.g. a fresh drop) → SKIP with a notice (not an error, exit 0); an unwritable `<home>/data/<key>` → clear "data_unwritable" error.
</must>
Reject:
<reject>
  - `<home>/data/<key>` cannot be created/written -> "data_unwritable" (clear error, exit 1; the managed home + the per-project default path remain usable)
  # a project with nothing to persist is NOT a reject — it is a skip+notice, exit 0 (D8).
</reject>
After:
<after>
  - after `init --global-data` on an initialised project, `<home>/data/<key>/` holds a copy of the project's user-data (state.json · PROJECT.md · milestones · tasks…) and NONE of the managed trees; the project + home are otherwise exactly as `init --global` leaves them.
  - after `update --global`, every opted-in (snapshotted) + existing project's `<home>/data/<key>/` mirrors its current local user-data; a vanished project's registry entry is pruned while its snapshot is retained.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ D-A1 [contract] a ONE-WAY persist (project→home snapshot, never home→project) is the right mvp — lowest confidence because "persist" could be read as two-way sync or restore-on-clone. Mitigation: a one-way snapshot keyed by path satisfies the exit criterion literally AND is the SAFE subset (it can never clobber local data); RESTORE (home→project) + bidirectional sync are seeded SPEC deltas. (Accept — project-lead call under full-auto.)
  ⚠ D-A2 [contract] keep registry.json a FLAT list and use the `<home>/data/<key>/` dir's EXISTENCE as the per-project opt-in record (do NOT enrich the registry to objects) — lowest because global-install's §1 hinted "global-data may enrich it to objects". Mitigation: the data-dir presence is a simpler, backward-compatible marker that keeps the frozen flat-list + propagation loop intact; enriching is deferred to a delta if per-project metadata is ever needed. (Accept.)
  - [x] user-data = `.add/` minus managed trees (tooling/docs) minus transient — ADOPTED (mirrors the managed↔user boundary the whole milestone honors).
  - [x] a vanished project KEEPS its snapshot (persist outlives the dir); a `prune-data` cleanup is a deferred delta — ADOPTED.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: data_key is deterministic, distinct, and filesystem-safe          # D1
  Given two different absolute project paths
  When data_key() is computed
  Then the same path always yields the same key, different paths yield different keys,
       and no key contains a path separator

Scenario: init --global-data persists user-data, excludes the managed layer  # D2, D3
  Given an initialised project (it has .add/state.json + .add/PROJECT.md + .add/tasks/)
  When init --global-data runs
  Then <home>/data/<key>/state.json and PROJECT.md and tasks/ exist
  And <home>/data/<key>/tooling and docs do NOT exist (managed layer excluded)
  And the home + registry are populated (it implied --global)

Scenario: init --global-data clean-replaces a stale snapshot                 # D3
  Given a project already snapshotted, then a user-data file is deleted locally
  When init --global-data runs again
  Then the deleted file is gone from <home>/data/<key>/ (no orphan)

Scenario: update --global re-persists an opted-in project                    # D4
  Given a snapshotted project whose local state.json then changes
  When update --global runs
  Then <home>/data/<key>/state.json mirrors the new local content

Scenario: update --global keeps a vanished project's snapshot                # D4
  Given a snapshotted project that is then deleted from disk
  When update --global runs
  Then the project is pruned from registry.json but <home>/data/<key>/ is retained

Scenario: default install persists nothing                                    # D5
  Given init --global WITHOUT --global-data
  Then no <home>/data directory is created; data stays local & git-tracked

Scenario: persisting a project with no data yet is a skip, not an error       # D8
  Given a fresh drop (no .add/state.json — no user-data yet)
  When init --global-data runs
  Then it exits 0 with a "nothing to persist" notice and creates no <home>/data/<key>

Scenario: drops-files-only holds under --global-data                          # D7
  Given init --global-data runs
  Then no NEW state.json is authored (only existing data is copied) and no subprocess is spawned

Scenario: an unwritable data dir fails closed                                 # Reject data_unwritable
  Given <home>/data cannot be written
  When init --global-data runs on an initialised project
  Then it errors (nonzero) and the managed home + per-project default remain usable
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
data_key(project_abspath) -> str        # dataKey() is the npm twin
  = "<sanitized-basename>-<sha1(abspath_utf8)[:12]>"   # [^A-Za-z0-9._-] in basename -> "_"
  pure · total · deterministic · collision-resistant · NO path separator · identical on both twins

GLOBAL DATA LAYOUT   (created ONLY under --global-data; opt-in, additive to global-install)
  <home>/data/<key>/   a clean-replace snapshot of <project>/.add USER-DATA:
                         state.json · PROJECT.md · SOUL.md · CONVENTIONS.md · GLOSSARY.md ·
                         milestones/ · tasks/ · archive/ · RELEASES.md  (everything under .add/
                         EXCEPT managed trees tooling/ + docs/, and transient/managed-meta:
                         .add-version · .update-cache · scope-snapshot* · *pre-archive-bak* · *.bak.json)

persist_data(home, project_abspath) -> bool        # _persist_data; True=persisted, False=skipped
  add_dir = <project>/.add
  entries = [e in add_dir if is_user_data(e.name)]          # the include/exclude rule above
  if add_dir absent OR entries empty -> return False         # skip (nothing to persist)
  dest = <home>/data/<data_key(project_abspath)>
  clean-replace: rmtree(dest) if exists; copy each entry (file/dir) -> dest
  an unwritable dest -> raise OSError -> caller fails "data_unwritable"

init --global-data [dir]   (IMPLIES --global)
  run the full init --global (managed home + register + per-project drop)   # global-install
  persisted = persist_data(home, abspath(dir))
  print: "persisted data -> <home>/data/<key>"  | else  "no project data to persist yet"
  drops-files-only: COPIES existing user-data; NO init, NO spawn, NO new state.json authored

update --global   (entry UNCHANGED; data re-persist is additive)
  ... existing managed refresh + propagate + registry prune ...
  for each registered+existing project p:
     if <home>/data/<data_key(p)> exists -> persist_data(home, p)   # keep the snapshot current
  a pruned (vanished) project: registry entry removed, <home>/data/<key>/ RETAINED (backup outlives it)

plain init/update + init --global (NO --global-data) -> UNCHANGED (no <home>/data written)

errors (fail-closed; nothing partially written on the rejecting step)
  data_unwritable -> "cannot write global data <home>/data/<key> — <err>" + exit 1
                     (the managed home + the per-project default path are unaffected)

State / schema: writes ONLY <home>/data/<key>/ (a copy of existing user-data). The registry stays
  a FLAT list (the data-dir's existence is the per-project opt-in record — no registry-shape change).
  NO new state.json is authored. One-way (project→home); RESTORE/sync are §7 deltas.
```

Least-sure flag surfaced at freeze:
  ⚠ [contract] ONE-WAY persist only (project→home) — "persist" might be expected to RESTORE (home→project) on a fresh clone. Chosen as the safe mvp subset (can never clobber local data); restore + bidirectional sync seeded as §7 SPEC deltas. (D-A1)
  ⚠ [contract] the opt-in is recorded by the EXISTENCE of `<home>/data/<key>/` (registry stays a flat list), NOT by enriching registry.json — keeps global-install's frozen registry + propagation intact; per-project metadata in the registry is a deferred delta. (D-A2)

Status: FROZEN @ v1 — approved by Tin Dang (full-auto mode delegated 2026-06-17; project-lead judgment: one-way snapshot is the safe mvp, registry stays flat; open assumptions D-A1/D-A2 resolved → both adopted, restore/sync deferred as deltas)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete across the 9 scenarios. Fully hermetic — home + skill base
resolved from the injected `env` (reusing global-install's `env` hook): tests pass `env={"ADD_HOME":
<tmp>, "HOME": <tmp>}` so nothing touches the real ~/.add or ~/.claude. To get user-data into a
project, tests pre-seed `<proj>/.add/state.json` etc. (NOT via init — the installer drops files only).
npm uses subprocess with the same env injected (skips without node).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_data_key_pure_distinct_safe: data_key(p)==data_key(p); data_key(p1)!=data_key(p2); os.sep not in key (D1).
  - test_global_data_persists_user_data: pre-seed proj/.add/{state.json,PROJECT.md,tasks/}; install(global_data) / <home>/data/<key>/{state.json,PROJECT.md,tasks} exist AND tooling/docs do NOT; home+registry populated (D2,D3).
  - test_global_data_clean_replaces_snapshot: snapshot, delete a local user-data file, re-persist / the file is gone from the snapshot (no orphan) (D3).
  - test_update_global_repersists_optedin: snapshot proj, change local state.json, update(global) / <home>/data/<key>/state.json mirrors the new content (D4).
  - test_update_global_keeps_vanished_snapshot: snapshot proj, rmtree proj, update(global) / proj pruned from registry BUT <home>/data/<key>/ retained (D4).
  - test_default_persists_nothing: install(global) WITHOUT global_data / no <home>/data dir (D5).
  - test_persist_nothing_to_persist_skips: fresh drop (no user-data), install(global_data) / exits 0, no <home>/data/<key> created (D8).
  - test_global_data_no_python_spawn: (structural) cli.js has no spawnSync; install(global_data) authors no NEW state.json (D7).
  - test_data_unwritable_fails: <home>/data is a FILE (mkdir impossible), install(global_data) on a seeded project / nonzero (Reject data_unwritable).
  - test_global_data_npm: subprocess init --global-data with seeded .add / <home>/data/<key>/state.json exists, tooling excluded (D2,D3,D6) [skipUnless node].
  - test_parity_data: cli.js+_installer.py both name data_key/dataKey + the "data" dir + "global-data" flag (D6 structural).
</test_plan>

Tests live in: `add-method/tooling/test_global_data.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/src/add_method/_cli.py` `add-method/tooling/test_global_data.py`
  (NO add.py change — find_root is only relied on. _cli.py gains `--global-data` on the init parser.)
Strategy (ordered batches): 1. add `data_key`/`dataKey` + `is_user_data`/`isUserData` + `_persist_data`/`persistData` (clean-replace USER-DATA → `<home>/data/<key>`, skip-if-empty, raise→data_unwritable) on both twins → 2. wire `install(as_global_data)`: implies `as_global`, persist after the per-project drop, skip+notice when empty → 3. wire `update --global` re-persist (only projects that already have a `<home>/data/<key>` snapshot; keep vanished snapshots) on both twins → 4. thread `--global-data` through parseArgs (cli.js, implies `--global`) + `_cli.py` init parser (dest=`as_global_data`).
Safety rule (feature-specific): the snapshot copies ONLY user-data (managed trees + transient excluded) — NEVER touches the managed layer or authors a state.json; clean-replace so a locally-deleted file leaves no orphan; one-way (project→home) only; an unwritable data dir is a clear fail (managed home + per-project default unaffected); the default (no `--global-data`) path is byte-unchanged.
Code lives in: `add-method/` (the package — NOT this task's `./src/`).
Constraints: do NOT change any test or the contract; no new dependency (hashlib/crypto are stdlib); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — global-data 11/11; FULL suite 1266 green (was 1255 + 11 new).
- [x] coverage did not decrease — +11 tests (data_key purity · persist+exclude · clean-replace · re-persist · vanished-keep · default-nothing · skip-when-empty · no-spawn · data_unwritable · npm · parity); no test removed or weakened.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 before tests; one test edit (strengthening the vacuous parity assertion) was made AT the tests phase before the tests→build snapshot; build_tampered clean.
- [x] the green was EARNED, not gamed — manual adversarial refute-read (global-data is purely additive, lower-risk than global-install which got the committed independent review): the persist tests assert the SNAPSHOT CONTENT (state.json mirrors NEW local content after update; a deleted file is GONE — not just "dir exists"); the exclude is proven by asserting tooling/docs are ABSENT from the snapshot; the skip test asserts NO snapshot dir (not a vacuous pass); data_unwritable proves nonzero on a file-blocked data dir. The weak parity assertion (looped but ignored its token) was rewritten to assert dataKey/data_key + the `--global-data` flag + the quoted `"data"` dir segment in BOTH twins.
- [x] concurrency / timing of the risky operation is safe — the snapshot is a clean-replace (rmtree+copy) per project dir; no shared mutable state across projects; the registry is untouched by persist. Same single-writer caveat as global-install (concurrent runs → deferred file-lock delta). One-way only — persist never reads-then-writes the project, so it cannot race local edits destructively.
- [x] no exposed secrets, injection openings, or unexpected dependencies — no shell-exec of any kind (hashlib/crypto are stdlib; no new dependency). data_key is a pure hash; paths come from the local project + user env. NOTE (accepted, not a HARD-STOP): the snapshot copies whatever is under the user's own `.add/` on their own machine — a local backup of their own data; a symlink inside `.add` is followed by the pip copytree (content copied INTO the snapshot, never written outside it) — see §7 delta for the snapshot symlink-handling parity nuance. NOT a security finding.
- [x] layering & dependencies follow conventions — reuses `_clean_replace`/`cpSync` + `resolve_global_home` (no new copy/resolve primitive); managed↔user-data boundary ENFORCED (the persist's whole job is to copy ONLY user-data, excluding the managed trees); registry stays a flat list (no shape churn); npm↔pip parity (identical key derivation, layout, include/exclude rule — structural + behavioral npm subprocess test).
- [x] a person reviewed and approved the change — full-auto mode (Tin Dang delegated 2026-06-17); careful manual self-review (the lower-risk last task; the independent review was the committed safeguard for the riskiest task, global-install). Auto-gated on complete evidence (auto-resolved — an explicit PASS, not a skip).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: pip `data_key`/`_is_user_data`/`_persist_data` called from `install()` (as_global_data persist block) + `_update_global` (re-persist) + the data_key unit test; npm `dataKey`/`isUserData`/`persistData`/`installGlobalData` reached via `cmdInit` (after dropFiles) + `cmdUpdateGlobal` (re-persist loop); `--global-data` threads parseArgs→cmdInit and `_cli.py` init parser→`install(as_global_data=…)`.
- [x] DEAD-CODE (code) — no new unused symbol (`_DATA_EXCLUDE`/`DATA_EXCLUDE` consumed by `_is_user_data`/`isUserData`; every helper has a caller).
- [ ] SEMANTIC (prose / non-code) — n/a (code task).

### GATE RECORD
Outcome: PASS  (auto-resolved under autonomy: auto — complete evidence; no security HARD-STOP; purely-additive lower-risk task, careful manual self-review)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: AI auto-gate + manual self-review (full-auto, Tin Dang delegated) · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): data_unwritable rate · snapshot size growth in `<home>/data`
(unbounded backups of large archives could bloat the home — a retention/prune policy may be needed)
· skip rate (high = users running --global-data on fresh, un-initialised projects).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

  - [SPEC · carried] RESTORE direction — a `--from-global-data` (or `init` detecting a matching `<home>/data/<key>`) that rehydrates a project's user-data from the home on a fresh clone/wipe (evidence: D-A1 — mvp is one-way persist; restore is the natural completion of "persist"). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
  - [SPEC · carried] a `prune-data` command to remove orphaned snapshots of long-gone projects (evidence: D4 keeps a vanished project's snapshot forever — a deliberate backup, but it needs a cleanup path + the Watch note on home/data growth). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
  - [SPEC · carried] snapshot symlink-handling parity — the pip copytree FOLLOWS symlinks in `.add` (copies content) while the npm cpSync preserves them; pick one rule for cross-twin byte-parity (evidence: §6 review — a minor divergence, harmless for a local backup today). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
  - [SPEC · carried] enrich registry.json to objects carrying a per-project `data: true` flag IF per-project metadata is ever needed (evidence: D-A2 — today the data-dir's existence is the opt-in record; deferred to avoid churning the frozen flat-list). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->

  - [DDD · folded] the managed↔user-data boundary is now a REUSED domain concept: heal-reconcile/global-install copy the MANAGED layer, global-data copies its COMPLEMENT (user-data) — naming the boundary once (an explicit include/exclude rule) let both sides share it (evidence: `_is_user_data` is the inverse of MANAGED). [folded foundation-version 38]
  - [TDD · folded] for a COPY/snapshot feature, assert on CONTENT + ABSENCE (new state mirrored · deleted file gone · managed trees NOT present), never just "the dir exists" — presence-only tests pass for the wrong reason (evidence: §6 earned-green read). [folded foundation-version 38]
  - [ADD · folded] a task whose word ("persist") spans a spectrum (snapshot↔sync↔restore) should freeze the SAFE subset (one-way, can't clobber) + seed the rest as deltas, rather than over-build under full-auto (evidence: D-A1 → one-way mvp + restore/sync deltas). [folded foundation-version 38]
