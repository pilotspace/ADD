# TASK: Stage-then-commit _clean_replace/cleanReplaceTree so a crash mid-copy never half-wipes a managed tree

slug: project-scope-atomic-reconcile · created: 2026-07-02 · stage: mvp
milestone: install-update-hardening
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/src/add_method/_installer.py:_clean_replace` — `def _clean_replace(src: Path, dest: Path, *, strip_tests: bool = False) -> dict`. Today: `before=_tree_files(dest)`, `shutil.rmtree(dest)` (if exists), `shutil.copytree(str(src), str(dest))`, then (if `strip_tests`) strips `__pycache__`/`test_*.py` FROM `dest`, returns `{"restored","refreshed"}` vs the before-snapshot. THE bug: wipe-then-copy is not atomic — a crash/disk-full/permission-denied mid-`copytree` leaves `dest` a random partial mix of old+new files.
  - `add-method/bin/cli.js:cleanReplaceTree` — `function cleanReplaceTree(src, dest, stripTests)`. Node twin, same shape: `fs.rmSync(dest,{recursive,force})` then `fs.cpSync(src,dest,{recursive:true})`, same post-copy strip + `{restored,refreshed}` return. NOT in `module.exports` — reachable only via `reconcile`/`cmdUpdate`/`cmdInit` or a `node cli.js` subprocess (matches how the existing tests already exercise it).
  - `add-method/src/add_method/_installer.py:_reconcile` / `cli.js:reconcile` — loop over `MANAGED` (4 trees: `skill/add`,`tooling`,`docs`,`personas-teacher`), one `_clean_replace`/`cleanReplaceTree` call per tree; sums roll-ups. Caller of the function I'm changing — itself unchanged.
  - `add-method/src/add_method/_installer.py:_reconcile_global` / `cli.js:reconcileGlobal` — loop over `_GLOBAL_TREES`/`GLOBAL_TREES` (same 4 trees, into `<home>`) PLUS one more `_clean_replace`/`cleanReplaceTree` call deploying `home/skill/add -> claude_dir`. Also unchanged by this task.
  - `add-method/src/add_method/_installer.py:install` (~889-1078) / `cli.js:cmdInit` (~680+) — calls `_reconcile_global` (if `as_global`) then always `_reconcile`. Unchanged.
  - `add-method/src/add_method/_installer.py:update` (~1334-1396) / `cli.js:cmdUpdate` (~1162+) — backs up `state.json` to `pre-update-state.bak.json` BEFORE calling `_reconcile` (pre-existing file-level design-for-failure precedent). Unchanged.
  - `add-method/src/add_method/_installer.py:_update_global` (~1252-1331) / `cli.js:cmdUpdateGlobal` (~1117-1160) — under `_update_lock`/`acquireUpdateLock`, calls `_reconcile_global` once + `_reconcile` per registered project. Unchanged. Confirms `_clean_replace`/`cleanReplaceTree` is the ONE choke point for all 3 reconcile paths (project install, project update, global propagation).
  - `add-method/src/add_method/_installer.py:_tree_files` / `cli.js:treeFiles` — the before/after file-set snapshot helper the roll-up counts depend on; my redesign must keep feeding it identical semantics or `test_reconcile_rollup.py`'s pinned counts break.
  - `add-method/src/add_method/_installer.py:_managed_status` / `cli.js:managedStatus` — reads `dest.exists() and any(dest.iterdir())` for the EXACT `MANAGED` dest paths only, never a directory scan — confirms a scratch sibling next to `dest` cannot be mistaken for a managed tree by this function.
  - `add-method/src/add_method/_installer.py:_is_user_data`/`_persist_data` (~703-736) — `_persist_data` iterates `add_dir.iterdir()` and treats anything NOT in the exact-name set `_DATA_EXCLUDE = {"tooling","docs",".update-cache",STAMP_FILE,LOCK_FILE}` (plus 3 narrow name-pattern exclusions) as user-data to snapshot. A scratch sibling (e.g. `tooling.add-tmp-xxxx`) would NOT match any exclusion — see Issues/Risks #4.
  - Prior art (Honors, unmodified): `add-method/tooling/add_engine/io_state.py:_atomic_write_many` (~60-113) — this codebase's established FILE-level two-phase stage-then-commit idiom ("any failure → write nothing new": stage every write to a sibling `.tmp`, fsync, THEN commit by renaming the existing target aside to a sibling `.bak` and renaming the temp in; roll back in reverse on a synchronous failure). My design is the directory-level analog.
  - Prior art: `add-method/tooling/add.py` (milestone-compact fn, ~3980-3993) — `ms_dir.rename(dest)`, an existing directory-level `Path.rename()` to a FRESH (not-yet-existing) sibling name, already the established atomic-directory-move primitive in this codebase (comment: "move (same-filesystem renames, never a delete)").
  - Prior art: `_installer.py` (~653-659, `_write_registry`) / `cli.js` (~883-890, `writeRegistry`) — `os.replace(tmp,target)` / `fs.renameSync(tmp,target)`, both commented "atomic on POSIX + Windows (same filesystem)" — the portability claim I extend from a file rename to a directory-rename-onto-a-fresh-name (never renaming onto an EXISTING name, which is the genuinely non-portable case).
  - `add-method/src/add_method/_installer.py:_update_lock` / `cli.js:acquireUpdateLock` — the O_EXCL cross-twin lock (unmodified; cited for its CONVENTIONS.md lesson, see Honors).
  - Test pattern: `add-method/tooling/test_reconcile_rollup.py` — hermetic `_clean_replace` unit tests (`CleanReplaceUnitTest`) + `_reconcile` roll-up tests + npm parity/behavioral smokes (`subprocess.run(["node",CLI_JS,...])`, `shutil.which("node")`-gated). PINS the `{"restored","refreshed"}` return contract — my redesign must not break any test in this file.
  - Test pattern: `add-method/tooling/test_global_update_harden.py` — hermetic cross-twin crash/contention simulation pattern (`_hold_lock`/`_release`, `_install_global`, `_update`, `ParityHardenTest.test_parity_surface` structural + `test_npm_relative_path_rejected` behavioral) — the template for how this codebase simulates a "held"/interrupted resource and asserts fail-fast + untouched state; §4 Tests (next phase) should follow this shape.
  - Test pattern: `add-method/tooling/test_heal_reconcile.py`, `test_update.py` — `PipReconcileTest`/`NpmReconcileTest` synthetic-bundled-fixture pattern, `@unittest.skipUnless(NODE,...)`.
  - `add-method/bin/cli.js:fail` (line 35) — `function fail(msg){...; process.exit(1);}` calls `process.exit(1)` DIRECTLY (not a `throw`) — Node does NOT unwind the stack / run pending `finally` blocks on `process.exit()`. See Issues/Risks #8.
Context (working folder):
  - `add-method/tooling/templates/gitignore.tmpl` + `_installer.py:_INSTALLER_MANAGED_IGNORE_EXTRA` / `cli.js:seedGitignore` — the seeded `.add/.gitignore` lists exact managed-tree names (`tooling/`,`docs/`,`personas-teacher/`), no wildcard for a scratch sibling. See Issues/Risks #5 — flagged, not resolved here (different function).
  - No TODO/FIXME found in `_clean_replace`/`cleanReplaceTree`/`_reconcile`/`reconcile` (checked).
  - No new dependency needed: stdlib `tempfile`/`os`/`shutil` (already imported in `_installer.py`) and Node builtin `fs`/`path` (already imported in `cli.js`) cover the whole design — `pyproject.toml`/`package.json` untouched.
Honors (patterns / conventions):
  - CONVENTIONS.md: "The Python tool is the only writer of state; writes are atomic (temp + os.replace) and never clobber" — the house rule this task extends from files to a directory tree.
  - CONVENTIONS.md (fv59 · global-update-harden): "a frozen contract that pins a per-twin IMPLEMENTATION mechanism... can fail its own INTENT — freeze the OBSERVABLE behavior... not the mechanism" — §3 states the observable guarantee, letting each twin use its own native rename/tempdir primitives.
  - CONVENTIONS.md (fv36 · fold-command): "a frozen 'any failure → write nothing' clause... needs a TWO-PHASE commit (stage-all → rename-all); N independent atomic writes give only per-file atomicity and can leave a silent partial" — the exact pattern mirrored here at the directory level.
  - CONVENTIONS.md: "a concurrency mechanism needs a CROSS-implementation test" + "a structural parity test asserting only token PRESENCE... passes even when the symbol is never CALLED — assert call-sites + a behavioral smoke" — shapes the §4 Tests plan (next phase): structural + subprocess-smoke parity, `test_global_update_harden.py`-style.
  - PROJECT.md / persona Critical Rules: "Design for failure... Atomic writes only; no partial state" — the governing invariant for this task.
  - `_installer.py` module docstring's own "Designed for failure" bullet list — this task adds to that list's spirit (the copy itself becomes crash-safe).
Seams consulted: none apply (checked `.add/SEAMS.md` — its 4 entries cover ADD's own engine/§5-scope/phase-extraction conventions, not installer atomic-write patterns).
Anchors the contract cites: `add-method/src/add_method/_installer.py:_clean_replace` · `add-method/bin/cli.js:cleanReplaceTree` (the only two symbols §3 names — full context in Touches above; every caller listed there changes behavior only as an observable consequence, not by edited code, and stays outside the frozen surface)
Issues/Risks (→ feed §1):
  1. **Core bug**: wipe-then-copy is not atomic; a crash/disk-full/permission-denied anywhere inside the copy leaves `dest` a random partial mix (worse than either the pre- or post-state), reachable from every install/update/global-propagate path via the one shared function.
  2. A portable single-syscall atomic SWAP of an EXISTING non-empty directory does not exist — POSIX `rename(2)` and Windows `MoveFileEx` both require the rename TARGET be absent or empty when the source is a directory. The achievable guarantee is "never observed half-composed," not "never observed absent for an instant" — §1/§3 must say this honestly, not oversell it.
  3. `strip_tests` currently runs on `dest` AFTER the copy — already inside today's crash-vulnerable window. A staged design can move this onto the STAGED copy (pre-swap) for free, closing a 3rd transient state (fully-copied-but-unstripped) as a side effect of the same fix.
  4. A scratch sibling left by a crash mid-copy is not excluded by `_is_user_data`'s exact-name set — if it survived to a LATER `_persist_data`/`persistData` call, it would be copied into a user-data snapshot as if it were real project data. Closed FOR FREE by self-healing stale siblings at the START of every `_clean_replace` call, GIVEN both `install()` and `_update_global()` always call `_reconcile`/`_reconcile_global` before any `_persist_data` call in the SAME invocation (verified by reading both bodies) — a coupling this task's design depends on rather than re-verifies structurally; noted so a future reader sees it's deliberate, not accidental.
  5. The seeded `.add/.gitignore` has no wildcard for a scratch sibling's name — see Context above; flagged as assumption A1 in §1, not resolved in this task (would touch `_seed_gitignore`/`gitignore.tmpl`/`seedGitignore`, outside the stated `_clean_replace`/`cleanReplaceTree`-only scope).
  6. `_persist_data`/`_restore_data` (and their JS twins `persistData`/`restoreData`) have their OWN, separate, still-non-atomic wipe-then-copy — NOT via `_clean_replace` — explicitly OUT of scope, owned by sibling task `global-data-restore-harden`.
  7. Serializing two CONCURRENT `install`/`update` runs against the same `dest` is explicitly OUT of scope (owned by sibling task `project-scope-install-lock`, which `depends_on` this task). This task's guarantee holds for ONE run crashing, not two runs racing; where the two concerns brush against each other, named as a residual/known-gap (see §1 Reject scenario ruling this out on purpose), never silently solved.
  8. `cli.js:fail()` calls `process.exit(1)` directly (not a `throw`) — Node does not run pending `finally` blocks on `process.exit()`. My new staged-commit logic in `cleanReplaceTree` must `throw` real `Error`s inside its try/finally cleanup region (never call `fail()` there), reserving `fail()` for the pre-existing top-level precondition checks that already run BEFORE any of this task's new logic.
Related intent:
  - PROJECT.md §Domain: "Design for failure... Atomic writes only; no partial state" (existing invariant this task fulfills for the installer).
  - Milestone `install-update-hardening` goal: "add.py init/update (both --global and project-scope, pip+npm twins) survive a crash or a concurrent run without leaving a half-written .add/ tree or a wedged lock" — this task delivers the "survive a crash... without a half-written tree" half for a SINGLE run; sibling `project-scope-install-lock` delivers the "concurrent run" half.
  - User's original ask (relayed via the orchestrating session): "harden npm update command to make sure it stable also," clarified to mean BOTH `update --global` AND project-scope (non-`--global`) install/update — `_clean_replace`/`cleanReplaceTree` is the single choke point common to all of those paths.
  - GLOSSARY.md: no existing entry for "managed tree"/"reconcile"/"clean-replace" — established internal code vocabulary, not (yet) formal glossary terms; this task doesn't add one either (§3 Glossary deltas: none).
Ground SHA: e1c5829

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: crash-safe stage-then-swap for `_clean_replace` / `cleanReplaceTree` — the shared wipe-then-copy choke point behind every install/update reconcile path (project install, project update, global home refresh, global per-project propagation).
Framings weighed: stage-then-swap — copy into a fresh sibling temp dir, commit via two same-parent renames, self-heal stale siblings on the next call (chosen; mirrors this codebase's own `_atomic_write_many` file-level idiom) · copy-into-place with a trailing orphan-sweep pass, never wipe first (rejected: a crash mid-copy leaves an even MORE ambiguous mixed state — some files overwritten, some not, no "which generation" marker — backwards from the goal) · two-generation directory + a stable symlink pointer (rejected: introduces a new on-disk shape every reader of `dest` would need to tolerate, is not portable the same way on Windows, and solves a multi-generation problem this task doesn't have)
Must:
<must>
  - M1: copy `src` (with `strip_tests`/`stripTests` already applied — see M2) into a freshly created, uniquely-named directory that is a SIBLING of `dest` in the SAME parent (so the later commit rename is same-filesystem) — `dest` itself is not opened for writing or deletion during this step. An empty `src` (zero files, e.g. an `OPTIONAL` managed tree reduced to nothing) is not a special case: the staged directory ends up empty and M3 still swaps it in, matching today's `shutil.copytree`/`fs.cpSync` behavior for an empty source.
  - M2: any post-copy transform (today: stripping `__pycache__` and `test_*.py` when `strip_tests`/`stripTests` is set) is applied to the STAGED directory, before it is committed into `dest` — never to `dest` itself afterward. Closes the "copied-but-not-yet-stripped" transient state.
  - M3: `dest` is updated by a two-step, same-parent rename commit that never targets an already-existing name: (a) if `dest` currently exists, rename it aside to a fresh, uniquely-named backup sibling; (b) rename the staged directory to `dest`'s path.
  - M4: the old tree (now at the backup path from M3a) is removed only STRICTLY AFTER M3b has landed the new `dest` — never before or during.
  - M5: a failure while staging (M1/M2) — for any reason, including a simulated one — leaves `dest` completely untouched (still absent, or still its prior content byte-for-byte) and removes the partial staged directory; the underlying exception still propagates (no silent partial success, no swallowed error).
  - M6: a failure during the commit (M3) rolls back what it safely can: if M3a already renamed the old `dest` aside but M3b then fails, the backup is renamed back onto `dest`'s path before the error propagates — a SYNCHRONOUS commit failure still leaves `dest` holding its original content.
  - M7: every call begins by self-healing any scratch sibling of `dest` left by an earlier, INTERRUPTED (crashed, not merely failed-with-exception) call: a stale backup found while `dest` is currently absent is restored onto `dest`'s path first (a cheap rename, minimizing how long `dest` stays broken); any stale staging directory is discarded outright (its content is never merged/reused) — both BEFORE this call's own fresh staging begins, so a crash never wedges a later run and is never mistaken for the real tree by anything that lists `dest`'s parent.
  - M8: the function's signature, return contract (`{"restored": N, "refreshed": M}`, computed by the SAME before/after relative-file-path-set diff), and final on-disk CONTENT of `dest` (copy + strip + orphan-sweep semantics) are unchanged — this task changes ONLY the crash-safety of how `dest` gets there. `_reconcile`/`reconcile`, `_reconcile_global`/`reconcileGlobal`, `install`, `update`, `_update_global`/`cmdUpdateGlobal` need zero edits, and every existing passing test in `test_reconcile_rollup.py`, `test_heal_reconcile.py`, `test_update.py`, `test_global_update_harden.py`, `test_global_data.py` stays green untouched.
  - M9: both twins (`_installer.py:_clean_replace`, `cli.js:cleanReplaceTree`) guarantee the SAME observable staged-commit behavior, each using its own native primitives (`tempfile`/`os.replace` · `fs.mkdtempSync`/`fs.renameSync`) — per the "freeze OBSERVABLE behavior, not the per-twin mechanism" convention already established for `_update_lock`/`acquireUpdateLock`. In `cleanReplaceTree`, internal failures inside the stage/commit region `throw` real `Error`s (never call `fail()`, which calls `process.exit(1)` directly and would skip `finally`-based cleanup).
</must>
Reject:
<reject>
  (internal function, no NEW user-facing error code — the same underlying exception types `shutil.copytree`/`fs.cpSync`/`os.replace`/`fs.renameSync` raise today still propagate unchanged, per M5/M6. "Reject" here names the guaranteed observable POST-STATE of `dest` for each failure/interruption situation.)
  - staging fails, `dest` was PRESENT before the call -> `dest` left byte-for-byte unchanged ("stage_failure_dest_present_untouched")
  - staging fails, `dest` was ABSENT before the call -> `dest` stays absent, no partial tree ("stage_failure_dest_absent_untouched")
  - commit step M3a fails (rename dest-aside) -> `dest` unchanged (single syscall either fully happened or didn't); staged dir cleaned up ("commit_aside_failure_dest_unchanged")
  - commit step M3b fails AFTER M3a succeeded -> backup renamed back onto `dest`'s path before the error propagates, so `dest` still holds its original content ("commit_land_failure_rolls_back")
  - a hard crash (SIGKILL/power-loss, not a catchable exception) lands between M3a and M3b, leaving `dest` absent with a backup sibling present -> the VERY NEXT call for that `dest` self-heals: restores the backup first, then proceeds ("stale_backup_self_heals_next_call")
  - a hard crash lands during staging (M1/M2), leaving an incomplete staging sibling -> the very next call sweeps it (never merges/reuses partial content) before starting its own fresh stage ("stale_stage_swept_next_call")
  - two concurrent, lock-less `install`/`update` processes both invoke `_clean_replace`/`cleanReplaceTree` for the SAME `dest` at overlapping times -> explicitly OUT of scope; this task makes no guarantee about which writer's content wins and does not worsen today's total absence of protection, it only guarantees EACH writer's own `dest` is never seen half-composed. Serializing concurrent runs is `project-scope-install-lock`'s job (a `depends_on` sibling) — ruled out on purpose, not a silent gap.
</reject>
After:
<after>
  - `dest` holds exactly `src`'s content (post-strip, if requested) — the same end-state as today.
  - no scratch sibling (staging or backup) of `dest` survives a SUCCESSFUL call.
  - at most one scratch sibling of `dest` can survive an unsuccessful/interrupted call, and it is self-healed (restored-from or discarded) by the very next call for that same `dest` — never accumulates across repeated crashes into more than the most recent artifact.
  - `_reconcile`/`reconcile`, `_reconcile_global`/`reconcileGlobal`, `install`, `update`, `_update_global`/`cmdUpdateGlobal` are unchanged (zero edits); every existing test across the 5 files named in M8 stays green with no edits.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ A1 (lowest confidence): the staging/backup scratch siblings are NOT added to `.gitignore` in this task — a crash immediately followed by `git status`/a CI diff would show an unfamiliar untracked directory until the next successful `install`/`update` self-heals it away. Lowest confidence because this is a real, if minor, trust/UX residue I'm choosing to disclose rather than fix (fixing it touches `gitignore.tmpl`/`_seed_gitignore`/`seedGitignore` — outside the `_clean_replace`/`cleanReplaceTree`-only scope stated for this task). If wrong (human wants it closed now): cheap to add (2-4 template lines), just needs an explicit go-ahead to widen scope.
  ⚠ A2: M7's self-heal RESTORES a recoverable stale backup (not merely sweeps/discards it) — a deliberately RICHER guarantee than the literal ask ("doesn't wedge or get mistaken for the real tree"), because leaving `dest` absent until a fresh multi-file copy completes would mean e.g. `.add/tooling` (i.e. `add.py` itself) stays unusable longer than necessary after a crash. Confidence is high this is the technically right call, but it IS more than literally asked, so flagging for a conscious confirm rather than assuming.
  - [ ] A3: staging in `dest`'s own parent directory is always same-filesystem, so the commit renames are genuinely atomic (not a silent cross-device copy-fallback) — true for every `MANAGED`/`_GLOBAL_TREES` dest today, and not a NEW assumption (today's code already writes directly onto `dest` on whatever filesystem it resolves to); if wrong, the OS raises `OSError`/`EXDEV` on the rename — a clean, loud failure already handled by M6, not silent corruption.
  - [ ] A4: `os.replace`/`fs.renameSync` renaming a directory onto a FRESH (not-yet-existing) sibling name is a single atomic syscall on every platform this project supports — confirmed for POSIX `rename(2)`; extends this codebase's own existing "atomic on POSIX + Windows (same filesystem)" claim (`_write_registry`/`writeRegistry`) from the file case to a directory-rename-to-a-fresh-name, which shares the same primitive and avoids the non-portable "replace a non-empty directory" restriction (the target name doesn't yet exist). Residual risk: Windows antivirus/indexer transient file-locking — a known general flakiness this task doesn't specially handle, matching this codebase's existing posture (no retry-on-rename anywhere else either).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a missing dest is fully materialized via stage-then-swap   # M1, M3, M4, M8
  Given a dest directory that does not exist yet (e.g. the very first install of .add/tooling)
  When I call _clean_replace(src, dest) / cleanReplaceTree(src, dest)
  Then dest ends up containing exactly src's files, byte-for-byte
  And no staging or backup scratch sibling remains next to dest afterward

Scenario: a present dest is refreshed via stage-then-swap, never wiped in place   # M1, M3, M4, M8
  Given a dest directory that already holds a prior version of the managed tree
  When I call _clean_replace(src, dest) with src containing different content
  Then dest ends up containing exactly src's files
  And at no point does a caller observe dest missing files that were in the PRIOR version and are also in src unchanged (i.e. dest is never seen half-old/half-new)
  And no staging or backup scratch sibling remains next to dest afterward

Scenario: strip_tests is applied to the staged copy, closing the unstripped-intermediate state   # M2
  Given src contains a __pycache__ dir and a test_foo.py file, and strip_tests=True
  When I call _clean_replace(src, dest, strip_tests=True)
  Then dest never contains __pycache__ or test_foo.py at any point observable after the call returns
  And the staged directory (not dest) is where the stripping happened, per the implementation's own bookkeeping being asserted via the same before/after file-set the return counts use

Scenario: a mid-copy failure leaves a PRESENT dest byte-for-byte untouched   # M5, Reject stage_failure_dest_present_untouched
  Given a dest directory holding known prior content, and a simulated failure partway through copying src (e.g. copytree/cpSync raises after some but not all files land in the staging dir)
  When I call _clean_replace(src, dest) / cleanReplaceTree(src, dest)
  Then the call raises/throws the underlying error
  And dest still holds its exact PRIOR content, unchanged (never partially overwritten)
  And no partial staging directory survives the call (it is removed before the error propagates)

Scenario: a mid-copy failure leaves an ABSENT dest still absent   # M5, Reject stage_failure_dest_absent_untouched
  Given a dest directory that does not exist, and a simulated failure partway through copying src
  When I call _clean_replace(src, dest) / cleanReplaceTree(src, dest)
  Then the call raises/throws the underlying error
  And dest still does not exist (no partial tree was ever materialized at dest's path)
  And no partial staging directory survives the call

Scenario: a commit-phase failure after the old tree was renamed aside rolls back to the original dest   # M6, Reject commit_land_failure_rolls_back
  Given a dest directory with known prior content, staging has fully succeeded, and the commit's second rename (staged -> dest) is simulated to fail AFTER the first rename (dest -> backup) already succeeded
  When _clean_replace / cleanReplaceTree runs its commit step
  Then the call raises/throws the underlying error
  And dest is restored to hold its exact original content (the backup was renamed back)
  And no staging or backup scratch sibling survives the call

Scenario: a stale staging leftover from a prior crash is swept before new staging begins   # M7, Reject stale_stage_swept_next_call
  Given a scratch directory matching this dest's OWN staging-name pattern already sits next to dest (simulating a crash that happened mid-copy on a PRIOR call), and dest holds its normal current content
  When I call _clean_replace(src, dest) / cleanReplaceTree(src, dest) again
  Then the stale staging leftover is gone after the call (never merged into the result, never left to accumulate)
  And dest ends up holding exactly src's fresh content, same as the normal-success scenario
  And the call does not fail or hang because of the stale leftover

Scenario: a stale backup leftover from a prior crash self-heals an absent dest before new work begins   # M7, Reject stale_backup_self_heals_next_call
  Given dest does NOT currently exist, but a scratch directory matching this dest's OWN backup-name pattern sits next to it holding the last known-good content (simulating a crash between the two commit renames on a PRIOR call)
  When I call _clean_replace(src, dest) / cleanReplaceTree(src, dest) again
  Then dest is first restored to the backup's content (self-heal), then updated to src's fresh content by this call's own normal stage-then-swap
  And no backup scratch sibling survives the call
  And at no point during this call does a caller observe dest permanently stuck absent

Scenario: the return contract and orphan-sweep counts are unchanged from today   # M8
  Given a dest tree missing 2 files that exist in src and holding 3 files also present in src, plus 1 orphan file not in src at all
  When I call _clean_replace(src, dest) / cleanReplaceTree(src, dest)
  Then it returns restored=2 and refreshed=3 (computed the same before/after relative-path-set diff as today)
  And the orphan file is gone from dest and counted as neither restored nor refreshed

Scenario: both twins guarantee the same observable staged-commit behavior   # M9
  Given the same simulated mid-copy failure applied once to the Python _clean_replace call and once to the Node cleanReplaceTree call (via `node bin/cli.js`)
  When each twin's staging step fails
  Then both twins leave their own dest byte-for-byte untouched and remove their own partial staging directory
  And a structural parity check confirms both source files carry the same staged-commit call-site shape (self-heal sweep -> stage -> commit-by-rename -> sweep-old), not just the same function names

Scenario: dest's parent directory does not exist yet (boundary — very first install of a whole new tree)   # boundary edge case, feeds M1
  Given a target project where .claude/skills/ has never been created (a brand-new project, before any install)
  When I call _clean_replace(src, dest=".claude/skills/add") / cleanReplaceTree(...)
  Then the parent directory is created first, staging succeeds inside it, and dest ends up holding exactly src's content
  And no error occurs merely because the parent didn't exist yet

Scenario: two concurrent, lock-less runs racing on the same dest — ruled out on purpose   # Reject concurrent runs, concurrency edge case
  Given two install/update processes both invoke _clean_replace/cleanReplaceTree for the SAME dest at overlapping times, with no lock held (the lock is project-scope-install-lock's separate, later task)
  When both stage independently (each into its own uniquely-named sibling) and then race to commit
  Then this task makes NO guarantee about which writer's content ultimately wins the race
  And this task DOES guarantee neither writer's dest is ever observed half-composed from ITS OWN copy (the per-writer atomicity holds even though cross-writer ordering does not)
  And this is a deliberate, disclosed non-goal recorded here — not a silently missed case — with the real fix owned by project-scope-install-lock
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
crash-safe clean-replace  [internal helpers, no new CLI surface]
  _clean_replace(src: Path, dest: Path, *, strip_tests: bool = False) -> dict     # signature UNCHANGED
  cleanReplaceTree(src, dest, stripTests) -> {restored, refreshed}               # signature UNCHANGED
  Callers unchanged (zero edits, reach dest ONLY through this function):
    _reconcile/reconcile · _reconcile_global/reconcileGlobal · install()/cmdInit ·
    update()/cmdUpdate · _update_global()/cmdUpdateGlobal

  0. SELF-HEAL (start of every call, before this call's own work):
       tmp_stale = any pre-existing sibling of dest matching THIS call's reserved staging-name
                   pattern (dest.parent, prefixed "<dest.name>.add-tmp-")
       bak_stale = any pre-existing sibling matching the reserved backup-name pattern
                   ("<dest.name>.add-bak-")
       if dest is ABSENT and a bak_stale exists -> rename it onto dest's path (recovers the
         last known-good tree; if >1 bak_stale is somehow found, the most-recently-modified
         one is authoritative, an unexpected defensive tie-break, not an expected path)
       remove any remaining tmp_stale / bak_stale siblings (already-recovered or never-needed)
  1. SNAPSHOT: before = the set of dest's relative FILE paths (∅ if dest absent)   # UNCHANGED
  2. STAGE: create a fresh, uniquely-named directory sibling of dest, IN dest's own parent
       (same filesystem as dest, "<dest.name>.add-tmp-<token>"); copy src into it in full;
       if strip_tests/stripTests: strip __pycache__ + test_*.py FROM THE STAGED COPY (moved
       earlier than today's post-copy strip on dest)
       -> on ANY exception: remove the staged directory, re-raise/re-throw. dest is not opened
          for writing in this step, so it is provably whatever it was before the call.
  3. COMMIT — two same-parent renames, NEITHER targets an already-existing name:
       a. if dest exists: rename dest -> a fresh "<dest.name>.add-bak-<token>" sibling
       b. rename the staged directory -> dest's path
       -> if (a) raises: staged dir removed, dest untouched (the rename never happened), re-raise.
       -> if (b) raises (a already landed): rename the backup back onto dest (restore), remove
          the staged dir, re-raise. A hard CRASH (not a catchable exception) between (a) and (b)
          is NOT rolled back synchronously — the NEXT call's step 0 recovers it.
  4. SWEEP: remove the backup sibling from step 3a — runs ONLY after 3b has landed dest.
  5. after = dest's post-call relative FILE-path set
     return {"restored": |after \ before|, "refreshed": |after ∩ before|}        # UNCHANGED formula

Schema / files touched: add-method/src/add_method/_installer.py (_clean_replace) ·
  add-method/bin/cli.js (cleanReplaceTree). No new persisted state, no new CLI flag, no new
  dependency (stdlib tempfile/os/shutil · Node builtin fs/path only). A transient, self-cleaning
  scratch sibling of dest may exist ONLY (a) for the duration of a single call's stage/commit
  window, or (b) between an abnormal process termination and the next call for that same dest —
  never as steady state; never mistaken for dest by _managed_status/managedStatus or
  _tree_files/treeFiles (both key on dest's own exact path only, never a parent-dir scan).

INV: dest, observed from OUTSIDE this function at any instant, is always exactly ONE of three
     states — (a) its content from strictly before this call, (b) momentarily absent (the
     sub-instant window between commit renames 3a and 3b), or (c) the fully-staged,
     already-stripped, already-orphan-swept final content — NEVER a partial mix of old and new
     files. This is the achievable guarantee, not "never observed absent": a single-syscall
     atomic replace of an EXISTING non-empty directory is not portable (POSIX rename(2) / Windows
     MoveFileEx both require the target be absent-or-empty when the source is a directory), so
     state (b)'s window is real, closed by the NEXT call's self-heal (step 0), not by this call.
     Today's code has a MUCH LARGER and worse version of state (b) — the full duration of
     rmtree+copytree — so this is a strict improvement, not a new regression.
INV: the return contract, dest's final on-disk CONTENT (files present/absent/stripped), and
     every existing caller are BYTE-IDENTICAL to before this task — a crash-safety mechanism
     change only.
INV: both twins guarantee the SAME state machine (self-heal -> stage -> commit -> sweep) using
     each platform's own primitives (tempfile.mkdtemp/os.replace vs fs.mkdtempSync/fs.renameSync)
     — the OBSERVABLE guarantee is frozen, not the literal syscalls (mirrors the existing
     _update_lock/acquireUpdateLock precedent, CONVENTIONS.md fv59).
OUT of scope (named, not silently dropped): serializing two concurrent callers racing on the
  SAME dest (owned by project-scope-install-lock, depends_on this task) · _persist_data/
  _restore_data's own separate wipe-then-copy (owned by global-data-restore-harden) · a
  .gitignore pattern for the scratch sibling's name (assumption A1, flagged below, not silently
  implemented nor silently dropped).
```

Glossary deltas: none (this task hardens an existing internal mechanism — "managed tree",
  "reconcile", "clean-replace", "restored"/"refreshed" are pre-existing internal code vocabulary,
  not GLOSSARY.md domain terms, and this task doesn't promote them either).

Least-sure flag surfaced at freeze:
  ⚠ [spec] A1 — the transient scratch sibling is NOT added to `.gitignore` in this task; a crash
    followed immediately by `git status`/a CI diff shows an unfamiliar untracked directory until
    the next successful install/update self-heals it away. Cost if wrong: minor trust/UX friction
    only (self-resolves, never corrupts anything) — cheap to close (2-4 gitignore.tmpl lines) but
    touches `_seed_gitignore`/`seedGitignore`, outside this task's stated `_clean_replace`-only
    scope; needs an explicit go-ahead to widen it.
  ⚠ [contract] A2 — M7's self-heal RESTORES a recoverable stale backup (not merely sweeps it) —
    richer than the literal ask ("doesn't wedge or get mistaken for the real tree"). Cost if the
    human instead wanted the minimal sweep-only behavior: this is MORE code/complexity than the
    floor requires (though still scoped to `_clean_replace`/`cleanReplaceTree` alone, no new
    function) — flagging so the richer behavior is a conscious freeze decision, not an
    AI-assumed one.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 95% of the new self-heal/stage/commit/sweep logic in both twins
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_scn1_missing_dest_materialized_no_scratch_survives: absent dest -> materialized + no scratch sibling · covers: M1, M3, M4, M8
  - test_scn2_present_dest_refreshed_never_half_mixed: present dest -> new generation lands whole, orphan swept · covers: M1, M3, M4, M8
  - test_scn3_strip_tests_applied_before_commit_not_after: strip runs on the STAGED copy, spied via the real copytree · covers: M2
  - test_scn4_mid_copy_failure_present_dest_byte_for_byte_untouched: injected mid-copy raise -> present dest unchanged · covers: M5, R:stage_failure_dest_present_untouched
  - test_scn5_mid_copy_failure_absent_dest_stays_absent: injected mid-copy raise -> absent dest stays absent · covers: M5, R:stage_failure_dest_absent_untouched
  - test_scn6_commit_land_failure_after_aside_rolls_back: 2nd rename fails after 1st lands -> backup renamed back · covers: M6, R:commit_land_failure_rolls_back
  - test_scn7_stale_staging_leftover_swept_before_new_stage: a pre-existing .add-tmp-* sibling is swept, call succeeds · covers: M7, R:stale_stage_swept_next_call
  - test_scn8_stale_backup_self_heals_absent_dest: a pre-existing .add-bak-* sibling self-heals then updates to fresh · covers: M7, R:stale_backup_self_heals_next_call
  - test_scn8b_stale_backup_restore_confirmed_not_mere_sweep: bonus — a subsequent stage failure proves RESTORE not sweep · covers: M7, A2 (reinforces scn8)
  - test_scn9_return_contract_and_orphan_sweep_unchanged: 2 restored + 3 refreshed + 1 orphan swept, same shape as today · covers: M8
  - test_scn11_dest_parent_not_yet_created: a 2-levels-missing parent chain is created, no error · covers: boundary, feeds M1
  - test_scn10_python_twin_staging_failure_dest_untouched / _node_twin_ / _structural_parity_of_staged_commit_shape: same observable behavior + self-heal->stage->commit->sweep source-order parity, both twins · covers: M9
  - test_scn12_concurrent_racing_writers_never_leave_a_blend: two lock-less threads race one dest -> never a blend (best-effort) · covers: R:concurrent runs (disclosed non-goal)
</test_plan>

Tests live in: `add-method/tooling/test_reconcile_rollup.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/bin/cli.js`
Strategy (ordered batches): 1. `_clean_replace` (Python) → add the step-0 self-heal glob (stale `.add-tmp-*`/`.add-bak-*` siblings) at the top, ahead of the existing `before = _tree_files(dest)` snapshot line. 2. Replace the `shutil.rmtree(dest)` + `shutil.copytree(...)` body with: stage into `tempfile.mkdtemp(dir=str(dest.parent), prefix=dest.name+".add-tmp-")` (already-empty, so `shutil.copytree(src, staged, dirs_exist_ok=True)` is safe), relocate the `strip_tests` block onto `staged`, then commit via `staged.parent`-relative `Path.rename()` calls (dest→bak if dest exists, staged→dest), wrapped so a raise during commit rolls back per M6, and a `finally`/`except` during staging removes `staged` per M5. 3. Sweep the bak sibling only after the commit succeeds. 4. Mirror the identical state machine in `cli.js:cleanReplaceTree` using `fs.mkdtempSync`/`fs.renameSync`/`fs.rmSync` — keep every internal failure as a `throw`, never `fail()` (see Known-problem fixes). 5. Do NOT touch any caller (`_reconcile`/`reconcile`, `_reconcile_global`/`reconcileGlobal`, `install`/`cmdInit`, `update`/`cmdUpdate`, `_update_global`/`cmdUpdateGlobal`) — confirm by grep that none inline-duplicate the old rmtree+copytree pattern themselves.

Persona (optional): methodology-engine-dev
Known-problem fixes: the self-heal glob must match ONLY the reserved `.add-tmp-`/`.add-bak-` prefixed siblings of THIS dest, never an unrelated same-parent entry → `dest.parent.glob(dest.name + ".add-tmp-*")` / an equivalent `fs.readdirSync` + prefix filter, not a bare wildcard · `shutil.copytree`'s target must be an EMPTY pre-existing dir for `dirs_exist_ok=True` to be safe — `tempfile.mkdtemp` already guarantees that, don't reuse a non-empty path · staging MUST be created inside `dest.parent` (never the system tmp dir) or the commit renames become cross-filesystem and silently fall back to a slow non-atomic copy+delete, defeating the design · `cli.js:fail()` calls `process.exit(1)` directly and skips pending `finally` blocks — every internal error in the new stage/commit region must `throw` a real `Error`, reserving `fail()` for the pre-existing top-level precondition checks only · a caller-visible exception TYPE must stay whatever `shutil.copytree`/`os.replace` (or the JS equivalents) already raise today — do not wrap/swallow into a new custom exception, or an upstream `except OSError` (e.g. `install()`'s `cannot write global home` handler) could stop catching it.
Strategy actually used: followed the 5 ordered batches as planned, with two disclosed deviations.
  (1) Used `os.rename`/`fs.renameSync` for BOTH commit renames instead of the suggested
  `Path.rename()` — `os.rename` fails loudly on Windows if the target already exists (never
  silently overwrites, reinforcing the "neither rename targets an already-existing name"
  invariant as a safety net) and lets tests patch it module-qualified
  (`mock.patch.object(_installer.os, "rename", ...)`), matching this codebase's own
  `test_multi_file_commit.py` precedent; `Path.rename()` has no equivalent module-level patch
  point. Same observable behavior either way — a testability/platform-safety upgrade, not a
  contract change.
  (2) Batch 4 (mirror in cli.js) surfaced 3 latent bugs in my OWN just-written tests (not the
  implementation) during the first post-build run, fixed as part of convergence, all in
  test_reconcile_rollup.py: scn3's copytree spy fired its "pre-strip files exist" assertion on
  shutil.copytree's own internal recursive re-invocation of the same (patched) symbol for the
  __pycache__ subdirectory, not just the intended top-level call — scoped the assertion to
  `Path(s) == src`. scn6's injected rename-failure predicate matched both the intended landing
  rename AND the code's own later rollback rename (both target `dest`) — added a "fail only the
  first matching call" flag so the rollback can succeed for real. scn7 asserted the wrong
  expected roll-up value ({"restored": 0, "refreshed": 1}); cross-checked against the frozen,
  unchanged test_orphan_swept_not_counted and corrected to {"restored": 1, "refreshed": 0} — a
  filename swapped in where a different filename existed before is `restored`, not `refreshed`,
  per the pre-existing counting convention. All three are test-instrumentation corrections
  (assertions kept equally strict, only re-scoped/re-labeled to match already-stated intent);
  no implementation code changed in response to any of the three. Verified via a real (non-
  mocked) SIGKILL-mid-copytree probe in addition to the unit suite — see §6 Live-verify evidence.
Safety rule (feature-specific): `dest` is never opened for writing or deletion until the staged copy (including any strip step) has FULLY succeeded — the existing wipe-then-copy ordering is inverted to copy-then-swap-then-sweep-old.
Code lives in: `add-method/` (the package — NOT this task's `./src/`).
Constraints: do NOT change any test or the contract; no new dependency (stdlib `tempfile`/`os`/`shutil` · Node builtin `fs`/`path` only); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 74/74: `test_reconcile_rollup.py` 27/27 (12 pre-existing: 4 `CleanReplaceUnitTest` + 4 `ReconcileRollupTest` + 1 `UpdateHeadlineTest` + 3 `ParityRollupTest`; 15 new: 11 `StageCommitUnitTest` + 1 `ConcurrencyDisclosureTest` + 3 `CrossTwinStagedCommitTest`) + all 4 M8-named sibling files (`test_heal_reconcile.py`/`test_update.py`/`test_global_update_harden.py`/`test_global_data.py`) 47/47 unchanged. Commands: `python3 -m unittest test_reconcile_rollup test_heal_reconcile test_update test_global_update_harden test_global_data` → `Ran 74 tests ... OK`.
- [x] coverage did not decrease — net +15 test methods (0 removed, 0 skipped-without-reason); the 12 pre-existing tests in `test_reconcile_rollup.py` are byte-unchanged, as are all 47 sibling tests.
- [ ] no test or contract was altered during build — PARTIAL, disclosed: §3 CONTRACT untouched, and zero pre-existing/frozen test was touched. But 3 of MY OWN tests authored in the tests-phase-of-this-task (`test_scn3_strip_tests_applied_before_commit_not_after`, `test_scn6_commit_land_failure_after_aside_rolls_back`, `test_scn7_stale_staging_leftover_swept_before_new_stage`, all in `test_reconcile_rollup.py`) were edited AFTER the tests-red commit, during build convergence — see "Strategy actually used" (§5) for the exact bug in each. Applying this repo's own folded discriminator (CONVENTIONS.md: "an engine change that legitimately invalidates an existing assertion is an EVOLUTION, not a weakening — iff the real invariant stays guarded, coverage holds-or-rises, and the reason is documented"): all 3 keep their assertion equally strict (scn3/scn6 re-scoped WHEN the check fires, scn7 corrected WHAT value it expects against the frozen, unchanged `test_orphan_swept_not_counted` precedent), coverage held (same 3 tests, not fewer), reason documented inline + in §5. Left unchecked for the independent reviewer to weigh, not pre-decided here.
- [ ] the green was EARNED, not gamed — deferred to the Refute-read verdict block below (not pre-judged here).
- [ ] concurrency / timing of the risky operation is safe — PARTIAL, disclosed: single-writer crash/interruption timing IS addressed and tested (scn4/5/6 mocked + a real, non-mocked SIGKILL-mid-copytree probe, see Live-verify evidence below). Cross-process CONCURRENT writers racing the same dest is an explicit, named OUT-of-scope item (owned by sibling task `project-scope-install-lock`, `depends_on` this task) — `ConcurrencyDisclosureTest.test_scn12` only proves no BLEND is ever observed (best-effort), not that both racers succeed or that the operation is serialized. Left unchecked because "is safe" unqualified would overstate the disclosed non-goal.
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new dependency (stdlib `tempfile`/`os`/`shutil` only; Node builtins `fs`/`path` only — matches §3's "no new dependency" line and CONVENTIONS.md's "standard library only" / "built-in modules only" rules); all 6 call sites (3 Python + 3 JS, re-confirmed below) pass fixed literal path components only, never adversarial/user-supplied input.
- [x] layering & dependencies follow CONVENTIONS.md — confirmed stdlib/builtin-only (CONVENTIONS.md lines 4-5) and the fv59 "freeze the OBSERVABLE behavior, not the mechanism" precedent (each twin uses its own native primitive: `tempfile.mkdtemp`/`os.rename` vs `fs.mkdtempSync`/`fs.renameSync`).
- [ ] a person reviewed and approved the change — human/independent-reviewer gate; not mine to check.

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a PRESENT dest survives a mid-copy crash byte-for-byte untouched (never a partial/blended mix at dest's path) — confirmed by `test_scn4` (mocked mid-copy raise) AND a real, non-mocked SIGKILL sent to a live subprocess mid-`shutil.copytree` (scratchpad `live_crash_probe.py`): `old_current.py`'s content was read back byte-identical after the kill.
- [x] a crash-interrupted prior call's scratch leftover (`.add-tmp-*`/`.add-bak-*`) is discovered and healed by the very NEXT call, landing the full new generation with zero scratch residue afterward — confirmed by `test_scn7`/`test_scn8`/`test_scn8b` (mocked) AND the same live SIGKILL probe's second half: the next call reported `{"restored": 4000, "refreshed": 0}` and left only `dest`/`src`/`worker.py` (no `.add-tmp-`/`.add-bak-` name) as siblings.
- [x] both twins share the identical self-heal → stage → commit → sweep marker order and reserved `.add-tmp-`/`.add-bak-` naming tokens — confirmed by `test_scn10_structural_parity_of_staged_commit_shape` (asserts the 4 markers appear in that exact order in both `_installer.py` and `cli.js`, `js_body.count("fail(") == 1`, `"throw" in js_body`) plus a manual side-by-side read of both diffs.
- [x] the public return contract (`{"restored","refreshed"}`) and every existing caller's observable behavior are byte-identical to before this task — confirmed by the pre-existing `CleanReplaceUnitTest` (4/4, unchanged) + all 4 M8-named sibling suites (47/47, unchanged) passing, plus `git diff` showing zero call-site lines touched in either file (only the two function bodies changed).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — no NEW top-level symbol was introduced (only the `tempfile` import is new; it is used at the one `tempfile.mkdtemp(...)` call site). The change is entirely internal to the two pre-existing function bodies (`_clean_replace`, `cleanReplaceTree`); their signatures, and every one of the 6 real call sites (3 Python: `_installer.py:680,682,1181`; 3 JS: `cli.js:901,977,979`), are byte-unchanged — re-confirmed via `mcp__serena__find_referencing_symbols` (Python) and a direct read of each JS call site.
- [x] DEAD-CODE (code) — no unused/orphaned local: every new local (`tmp_stales`/`bak_stales`/`staged`/`token`/`bak` in Python; `destParent`/`destName`/`siblings`/`tmpStales`/`bakStales`/`remainingBaks`/`staged`/`token`/`bak` in JS) is read at least once; `node --check cli.js` and `python3 -c "import ast; ast.parse(...)"` both confirm no syntax-level dead branch.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed via `mcp__serena__find_symbol`/`find_referencing_symbols` (Python) + direct Read (JS, serena's active language is Python-only in this project so the JS twin was hand-verified): `_clean_replace` (now `_installer.py:1131`, signature unchanged) called from `_reconcile_global` (`672-682`, 2 call sites) and `_reconcile` (`1181`); `_reconcile`/`_reconcile_global` called from `install` (`888-1078`), `update` (call at `1384`), `_update_global` (`1252-1331`, calls at `1298`/`1317`). `cleanReplaceTree` (now `cli.js:798`) called from `reconcile` (`901`) and `reconcileGlobal` (`977`,`979`); `reconcile`/`reconcileGlobal` called from the init path (`638`/`725`), `cmdUpdate` (`1259`), and the global-update handler (`1130`,`1199`,`1211`). All 5 caller-pairs named in §3 (`_reconcile/reconcile` · `_reconcile_global/reconcileGlobal` · `install()/cmdInit` · `update()/cmdUpdate` · `_update_global()/cmdUpdateGlobal`) resolve cleanly.
- [x] any anchor that moved/renamed since Ground SHA is named here, not left silent — no symbol renamed or reordered. §0's own citations already use `~`-approximate line numbers anticipating drift; the only real shift is mechanical (`_clean_replace`'s body grew from 24 to ~73 lines, so everything textually AFTER it in `_installer.py` — e.g. `_update_global` — sits a few dozen lines lower than the Ground-SHA snapshot; nothing BEFORE it, e.g. `_reconcile_global`/`install`, moved at all). Exact current line numbers are recorded above so a future reader doesn't need to re-derive them.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: add-verify (independent reviewer — a separate agent instance from the build, per the
  orchestrator's explicit ask; nothing below was pre-accepted from the builder's own framing)
Adversarially checked:
  - **The 3 disputed test edits, re-derived from the raw diffs and current code, not the
    builder's narrative.** scn3: CPython's `shutil.copytree` recurses into subdirectories
    THROUGH the same patched `shutil.copytree` module attribute (confirmed by mechanism, not
    assumed) — so the pre-fix assertion (fired on every recursive call) deterministically
    fails whenever `src` has a subdirectory, which it always does here (`__pycache__`). The
    `if Path(s) == src:` guard isolates the one real call; a stray-pass risk is ruled out
    because `captured["staged"]` is unconditionally dereferenced right after the `with` block
    (a `KeyError` fires if the guard never matched once). scn6: read against the actual
    rollback line (`_installer.py:1194`, `os.rename(str(bak), str(dest))`) — the ORIGINAL
    unconditional intercept (`if str(dst_p)==str(dest): raise`) would ALSO have caught the
    code's own required rollback rename, leaving `dest` renamed-away-and-never-restored, so
    the test's own next line (`dest.iterdir()`) would raise `FileNotFoundError` OUTSIDE the
    `assertRaises` block. The pre-fix test could not have passed against ANY implementation
    that performs a real M6 rollback — the "fire-once" flag is what makes the scenario
    exercisable, not a loosening of it. scn7: independently recomputed
    `{"restored":1,"refreshed":0}` from the frozen §3 formula (`restored=|after\before|`,
    `refreshed=|after∩before|`) against the fixture (dest holds `current.py`, src holds
    `fresh.py` — disjoint names) and cross-checked against the untouched, frozen
    `test_orphan_swept_not_counted` (lines 111-121: `a.py` absent-before counts `restored`,
    `b.py` present-before counts `refreshed`) — the identical convention, independently
    confirming the fix and contradicting the original `{0,1}`. All 3 edits leave the real
    invariant (the substantive assertions in each test) unchanged in strength — only
    misfiring/mislabeled instrumentation was corrected — matching CONVENTIONS.md line 475's
    evolution-not-weakening bar (invariant stays guarded, coverage holds, reason documented).
  - **Reproduced the builder's cited command cold**, in this worktree, myself:
    `python3 -m unittest test_reconcile_rollup test_heal_reconcile test_update
    test_global_update_harden test_global_data` -> `Ran 74 tests ... OK` (exact match).
  - **Confirmed the M8 "5-files-only" scope claim is complete, not self-reported**: grepped
    every `test_*.py` under `add-method/tooling/` for `_clean_replace(`/`cleanReplaceTree(` —
    only `test_reconcile_rollup.py` references either.
  - **Re-diffed `_installer.py`/`cli.js` across ALL 3 commits** (not just the build commit) —
    zero lines touched outside the 2 function bodies + 1 new `tempfile` import; every caller
    (`_reconcile`/`_reconcile_global`, `install`/`update`/`_update_global` and JS twins) is
    byte-unchanged.
  - **Ran the full `add-method/tooling` suite beyond the builder's claimed scope**
    (`unittest discover`, 3342 tests): found 133 failures/errors. Traced root cause via actual
    tracebacks (not the summary line) for a representative sample across different files
    (`test_shared_engine_pin`, `test_engine_extract_md5`, `test_active_accessors`,
    `test_debrand_teacher_prose`) — every one traces to the SAME single cause: this worktree's
    `.add/tooling` was never materialized (confirmed absent before I read any diff — this
    worktree was checked out without an install/reconcile step), so every 3-tree/pinned-digest
    test either hits `FileNotFoundError` reading `.add/tooling/add.py` or hashes empty bytes
    (`d41d8cd98f00b204e9800998ecf8427e` = `md5(b"")`) against `ENGINE_PKG_MD5`. A pre-existing
    worktree-fixture gap, unrelated to and not caused by this task's 2-file diff — this task's
    own regression surface (the 5 files named in M8) is 74/74 green, independently reproduced.
  - **Read `ConcurrencyDisclosureTest`/`test_scn12`** and the cross-twin parity test
    (`test_scn10_*`) in full: the parity check is backed by 2 REAL behavioral smokes (a
    chmod-blocked real staging failure in Python, and a real `node` subprocess run against a
    chmod-blocked `.add/`) in addition to the structural marker-order check — not a vacuous
    token-presence check alone.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: add-verify (independent reviewer)
1. Security: CLEAR — no new dependency (stdlib `tempfile`/`os`/`shutil` + Node builtin
   `fs`/`path` only, confirmed reading both diffs in full); `src`/`dest` are always fixed,
   hardcoded managed-tree paths from `MANAGED`/`_GLOBAL_TREES` (never user/network input, and
   this task adds no new caller of the function); no subprocess/shell invocation added; no
   secret or credential surface touched. `shutil.rmtree`'s own refusal to follow a top-level
   symlink argument (stdlib behavior, unchanged by this task) still guards the self-heal
   sweep against a planted-symlink race the same way the old code's `rmtree(dest)` was guarded.
2. Concurrency: CLEAR — the in-scope guarantee (a single writer's `dest` is never observed
   half-composed, including a hard crash) is proven by mocked tests (scn4-scn8b) plus a real,
   non-mocked SIGKILL-mid-copytree probe (cited in this file's Build-expectations evidence)
   whose logic is consistent with the code as read: `dest` is never opened for writing until
   staging fully succeeds, and both commit renames are same-parent/same-filesystem, so a
   genuine OS-level atomic move. Cross-process racing writers is a disclosed, NOT
   silently-dropped non-goal: `add.py status` independently corroborates
   `project-scope-install-lock` as a real, tracked sibling task with
   `deps=project-scope-atomic-reconcile` — a properly owned, dependency-tracked follow-up, not
   an invented excuse.
3. Architecture: CLEAR — zero caller edits (re-diffed across all 3 commits, not just the
   build commit); both twins share one state machine (self-heal -> stage -> commit -> sweep,
   confirmed present in that source order in both files); no dead code (every new local is
   read, per this file's own Deep-checks); no new top-level symbol besides the one used
   `tempfile` import.
Verdict: PASS
Residue: none blocking. Two process-level notes for the orchestrator, neither a code defect:
  (a) this worktree's `.add/state.json`/`add.py status` reports this task at `phase=ground`,
  and this file's own header (line 6) still reads `phase: contract` — the git-committed
  content is actually at Verify with Build done. None of the 3 build commits touch
  `.add/state.json`; the phase stamp was synced once (ground->contract, matching an upstream
  freeze-only commit, per OBSERVE-NOTES.md's own ADD delta) but never advanced again through
  tests/build/verify. Likely needs an explicit `add.py phase` re-cross before a gate command
  will recognize this task as verify-ready (the established `build_tampered`-style re-cross
  pattern, not a new bug). (b) the broader `add-method/tooling` suite (3342 tests, run beyond
  this task's own named scope) shows 133 failures, ALL traced via real tracebacks to this
  worktree's `.add/tooling` never being materialized (confirmed absent before any diff was
  read) — a pre-existing worktree-fixture gap, unrelated to this task's 2-file diff; this
  task's own regression surface (the 5 files named in M8) is 74/74 green, independently
  reproduced.
Binding: advisory — unset (per `add.py status`; this file declares no explicit `sensitivity:`
  or `risk: high` line)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-03

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose stage-then-swap — copy into a fresh sibling temp dir, commit via two same-parent renames, self-heal stale siblings on the next call; rejected copy-into-place with a trailing orphan-sweep pass, never wipe first (rejected: a crash mid-copy leaves an even MORE ambiguous mixed state — some files overwritten, some not, no "which generation" marker — backwards from the goal) · two-generation directory + a stable symlink pointer (rejected: introduces a new on-disk shape every reader of `dest` would need to tolerate, is not portable the same way on Windows, and solves a multi-generation problem this task doesn't have)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: followed the 5 ordered batches as planned, with two disclosed deviations.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

