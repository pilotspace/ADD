# TASK: Harden update --global: file-lock concurrent runs + validate/reject traversal & non-project registry paths

slug: global-update-harden · created: 2026-06-28 · stage: mvp · risk: high
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
- `add-method/src/add_method/_installer.py:_update_global(target, *, force, bundled, version, env) -> int` (1165-1214) — the command to harden. Today: stamp-check → read registry (corrupt=LOUD) → `_reconcile_global` → for each registry path p: skip+prune if not exists, else `_reconcile(Path(p), home)` (1207) + re-persist opted-in. ADD (1) a home-LOCK around the whole body (serialize concurrent runs) + (2) per-path VALIDATION before the reconcile at 1207.
- `add-method/src/add_method/_installer.py:_read_registry/_write_registry/_registry_path` — the flat project-root list; `_read_registry` already raises `ValueError("registry_corrupt")` (LOUD). Validation runs on each path it returns.
- `add-method/src/add_method/_installer.py:resolve_global_home(env)/_stamp_path(home)` — home resolution + the `<home>/.add-version` stamp; the lockfile lives at `<home>/<lock>`.
- NEW `_update_lock(home)` (context manager — v2: O_EXCL lockfile `<home>/.update.lock` in BOTH twins, FAIL-FAST if present → "update_in_progress"; the v1 flock-pip/O_EXCL-npm split didn't serialize cross-twin) + NEW `_valid_registry_path(p) -> bool` (reject non-absolute · `..`-traversal that escapes · non-project dir [no `.add/`]).
- `add-method/bin/cli.js:cmdUpdateGlobal()` (1031) + `installGlobal()` (1011) — the npm twins; both need the same lock + path-validation (Node has no flock → lockfile via `O_EXCL`/`mkdirSync` atomicity).
- NO existing lock helper anywhere (`grep flock|fcntl|LOCK` empty) — locking is greenfield here.

Context (working folder):
- `.add/milestones/installer-polish/MILESTONE.md` — this is the 2nd freeze-first contract: "the registered-path validation rule (allowlist / traversal rejection) -> owning task global-update-harden". Shared decisions: corrupt registry / out-of-allowlist path = LOUD fail, never a silent reconcile-into; atomic single-writer; a file-lock serializes concurrent `update --global`. The home file-lock was also filed as a §7 delta by the sibling task [[project_installer_polish_milestone]] global-data-restore.
- Tests (canonical `add-method/tooling/`): `test_global_install.py` (G4 `update --global` propagates + prunes vanished) · `test_update.py` (per-project update). NEW `test_global_update_harden.py` follows `test_<area>.py`.

Honors (patterns / conventions):
- **LOUD on bad input, read-before-write** — mirror the existing corrupt-registry pattern (`_fail` + return 1, ZERO mutations). A traversal / non-project path must be rejected BEFORE `_reconcile` writes into it.
- **SECURITY** — path traversal (reconcile writing managed files into an arbitrary dir) is a security concern → reject fail-closed; any security note ESCALATES to human even under `autonomy: auto`.
- **Atomic single-writer** — the lock makes concurrent `update --global` serialize; fail-fast (no indefinite block). v2: an O_EXCL lockfile in BOTH twins (presence = held), released by unlink on normal/handled exit; a hard crash leaves a stale lock to remove by hand (the v1 flock-pip/O_EXCL-npm split did not serialize cross-twin).
- **cli.js ↔ pip parity** + **cross-platform** (O_EXCL lockfile both twins — no POSIX-only fcntl) + **hermetic tests** (inject `env=` home).

Anchors the contract cites: `_update_global` · NEW `_update_lock(home)` (+ "update_in_progress") · NEW `_valid_registry_path(p)` (+ the reject rule) · `_read_registry`/`_write_registry` · `resolve_global_home`/`_stamp_path` · `bin/cli.js:cmdUpdateGlobal`/`installGlobal` twins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: global-update-harden — make `update --global` concurrency-safe (a home file-lock) and reject unsafe registered paths before reconciling managed files into them.
Framings weighed: SOFTENED hybrid — LOUD only on non-absolute (the real traversal vector) · normalize+skip benign absolute entries · is-ADD-project is the security backstop (chosen) · LOUD-on-any-non-normalized (rejected: false-positive aborts) · skip+warn-all  ||  fail-fast-lock (chosen) · block-with-timeout
Must:
<must>
  - `update --global` (pip + npm) acquires a HOME file-lock at `<home>/.update.lock` for the whole run and releases it on exit (success OR failure); the lock serializes concurrent runs.
  - If the lock is already held, FAIL-FAST: exit non-zero with "update_in_progress", reconciling NOTHING (non-blocking; the user re-runs).
  - New `_valid_registry_path(p) -> bool`: True iff `os.path.normpath(p)` is an EXISTING ADD project — `os.path.isdir(np)` AND `os.path.isdir(np/".add")`. Decides reconcile-vs-drop for an absolute entry; absoluteness is the SEPARATE LOUD gate below.
  - PRE-SCAN every registry path BEFORE any reconcile (home or project): the ONLY LOUD case is a NON-ABSOLUTE (relative) path — it can't be a trusted abspath and is the traversal vector → exit 1 "unsafe_registry_path", reconcile NOTHING, registry LEFT INTACT.
  - For each ABSOLUTE entry: NORMALIZE it (`np = os.path.normpath(p)`), then — a vanished (`not exists(np)`) → skip + prune (snapshot kept); an existing non-ADD-project (no `np/.add`) → skip + warn + DROP from the registry (benign — the is-project check is the security backstop, a reconcile NEVER lands in a dir without `.add/`); an existing ADD project → `_reconcile(np)` + re-persist opted-in. A non-normalized-but-legit entry is thereby HEALED: the rewritten registry stores the kept NORMALIZED project paths.
  - Preserve today's behavior: a corrupt registry → LOUD "registry_corrupt"; no home → "no_global_home"; opted-in snapshots re-persisted; managed layer reconciled; registry rewritten atomically.
  - `bin/cli.js:cmdUpdateGlobal` + `installGlobal` mirror the lock (Node lockfile via `O_EXCL`/`mkdir` atomicity) + the same validation (non-absolute → LOUD; normalize + is-project) + the same error codes.
</must>
Reject:
<reject>
  - another `update --global` already holds the lock -> "update_in_progress"  (exit ≠0, nothing reconciled, the held lock untouched)
  - a registered path is NON-ABSOLUTE (relative) -> "unsafe_registry_path"  (exit 1, FAIL BEFORE any reconcile, registry byte-intact, home not refreshed)
  - (preserved) corrupt/unparseable registry -> "registry_corrupt"  (exit 1, registry intact)
  - (preserved) no global home / stamp -> "no_global_home"  (exit 1)
</reject>
After:
<after>
  - success: lock acquired+released; home refreshed; every existing ADD-project (at its normalized path) reconciled + opted-in snapshot re-persisted; existing non-project entries dropped+warned; vanished pruned; registry rewritten with the kept NORMALIZED project paths (non-normalized legit entries healed); exit 0.
  - update_in_progress: nothing reconciled, the home untouched by this run, the other run's lock intact, exit ≠0.
  - unsafe_registry_path (a relative path present): nothing reconciled (home NOT refreshed), registry.json byte-intact, lock released, exit 1.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the is-ADD-project check (`np/.add` is a dir) is a SUFFICIENT security backstop for absolute entries — lowest confidence because, with the softened rule, an absolute path is normalized and reconciled whenever a `.add/` dir exists at it, so a planted `<somewhere>/.add` could draw a reconcile there; if wrong: a managed-file write into an attacker-chosen dir. Mitigation: the registry + that dir are already user-write-controlled (planting `<dir>/.add` presumes write access the attacker already has), and a relative path — the only true traversal vector — is still LOUD; cost is low.
  - [ ] the lock is FAIL-FAST (an O_EXCL lockfile present = held → update_in_progress, in BOTH twins so it serializes cross-twin); if a user expected it to wait, they re-run — low cost. Tradeoff: not auto-released on SIGKILL (a stale `.update.lock` is removed by hand; both twins hint it).
  - [ ] healing non-normalized entries by rewriting the registry with normalized paths on success is desirable (self-heal) and never surprises the user — low cost (the installer already only writes normalized abspaths, so real registries are unchanged).
  - [ ] the lockfile at `<home>/.update.lock` is excluded from the managed mirror + `_is_user_data` so it never leaks into a snapshot or a reconcile (verify at build).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: update --global runs under the lock and releases it   # Must 1
  Given a stamped home with one registered, existing ADD project
  When I run `update --global`
  Then the project's managed layer is reconciled from the home and the run exits 0
  And after it returns, <home>/.update.lock is free (a second `update --global` acquires it and also exits 0)

Scenario: a concurrent update fails fast while the lock is held   # Must 2 + Reject update_in_progress
  Given the home lock <home>/.update.lock is already held by another process
  When I run `update --global`
  Then it fails with "update_in_progress" and a non-zero exit
  And nothing is reconciled and the held lock is left intact (the holder still owns it)

Scenario: _valid_registry_path accepts a real project, rejects a non-project   # Must 3
  Given an absolute path to a dir containing .add/, a non-normalized absolute path whose normpath is that same project, and an absolute path to a dir with no .add/
  When I check _valid_registry_path on each
  Then the real ADD-project path is valid AND the non-normalized path that normalizes to it is valid
  And the non-project path is invalid

Scenario: a NON-ABSOLUTE registry path aborts the whole run LOUD   # Must 4 + Reject unsafe_registry_path
  Given a stamped home whose registry contains a relative path "rel/proj" alongside a valid project
  When I run `update --global`
  Then it fails with "unsafe_registry_path" and exits 1
  And NOTHING is reconciled (the valid project's managed layer is untouched, the home is NOT refreshed/re-stamped)
  And registry.json is left byte-intact

Scenario: an absolute non-normalized path is normalized then dropped when it is not a project   # Must 5 (benign, NOT loud)
  Given a stamped home whose registry contains "/tmp/area/../gone-nonproject" (absolute, no .add/ at the normalized path) alongside a valid project
  When I run `update --global`
  Then the valid ADD project is reconciled and the run exits 0 (NOT unsafe_registry_path)
  And the non-project path is warned about, NOT reconciled into (no .add/ created there), and dropped from the rewritten registry

Scenario: an absolute non-normalized project entry is healed to its normalized form   # Must 5 (heal)
  Given a stamped home whose registry lists "/work/sub/../proj" where /work/proj is a real ADD project
  When I run `update --global`
  Then /work/proj is reconciled and the run exits 0
  And the rewritten registry lists the normalized "/work/proj" (not the "/work/sub/../proj" form)

Scenario: an existing non-ADD-project dir is skipped, warned, and dropped   # Must 5
  Given a stamped home whose registry lists a valid ADD project AND an existing dir with no .add/
  When I run `update --global`
  Then the valid ADD project is reconciled and the run exits 0
  And the non-project dir is warned about and is NOT reconciled into (no .add/ is created there)
  And the rewritten registry no longer lists the non-project dir

Scenario: preserved — a vanished project is pruned, an opted-in snapshot re-persisted   # Must 6
  Given a stamped home with a registered project that no longer exists AND a registered project with an opted-in snapshot
  When I run `update --global`
  Then the vanished project is pruned from the registry (its snapshot is KEPT)
  And the opted-in project's snapshot is re-persisted and the run exits 0

Scenario: preserved — a corrupt registry fails LOUD with the file intact   # Must 6 + Reject registry_corrupt
  Given a stamped home whose registry.json is present but unparseable
  When I run `update --global`
  Then it fails with "registry_corrupt" and exits 1
  And registry.json is left byte-intact and nothing is reconciled

Scenario: the lock is released even when the run fails   # Must 1 (release-on-failure)
  Given a run that fails on an unsafe_registry_path
  When the failed run returns
  Then <home>/.update.lock is free (a subsequent `update --global` can acquire it)

Scenario: parity — cli.js locks + validates the same way   # Must 7
  Given the npm cli.js update --global path
  When I read its source
  Then it acquires a home lockfile, validates registry paths (LOUD on a relative path; normalize + is-ADD-project otherwise), and uses the same error codes
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
update --global   [CLI: `pilotspace-add update --global` · `node bin/cli.js update --global`]
  → _update_global(target, *, force=False, bundled=None, version=None, env=None) -> int   (run UNDER the home lock)

  _update_lock(home) -> context manager        # v2: O_EXCL lockfile in BOTH twins (cross-twin compatible)
    creates `<home>/.update.lock` EXCLUSIVELY (os.open O_CREAT|O_EXCL|O_WRONLY ≡ npm `fs.openSync(..,"wx")`);
    already EXISTS → raises BlockingIOError (caught by _update_global → _fail "update_in_progress", 1);
    on __exit__ for success OR exception, closes the fd AND unlinks the file — released, never outlives a
    normal/handled exit. (A hard crash / SIGKILL may leave a stale lockfile — the error hints to remove it;
    same for both twins. The v1 flock-for-pip + O_EXCL-for-npm split did NOT serialize cross-twin — fixed.)

  _valid_registry_path(p: str) -> bool        # reconcile-vs-drop predicate (Must 3)
    np = os.path.normpath(p);  return os.path.isdir(np) AND os.path.isdir(os.path.join(np, ".add"))
    # absoluteness is the SEPARATE LOUD gate (step 4); this answers "is np a live ADD project to reconcile into".

  _update_global sequence (whole body wrapped in `with _update_lock(home):`):
    1. resolve home; no `.add-version` stamp → _fail "no_global_home" (1)
    2. bundled source missing → _fail (1)
    3. reg = _read_registry(home);  ValueError → _fail "registry_corrupt" (1)   [registry intact]
    4. PRE-SCAN (security, BEFORE any write): any p with NOT os.path.isabs(p)   # relative = the traversal vector
         → _fail "unsafe_registry_path" (1) — home NOT refreshed, registry byte-intact
    5. _reconcile_global(home, claude_dir, bundled_root);  _write_stamp(home, …)
    6. for p in reg (all absolute after step 4):  np = os.path.normpath(p)
         not Path(np).exists()                        → warn + prune (snapshot KEPT)        [preserved]
         exists but not (Path(np)/".add").is_dir()     → warn + DROP from registry (skip)     [new · benign · security backstop]
         else                                          → _reconcile(Path(np), home) + re-persist opted-in (key on np) [preserved]
         on reconcile/prune-keep, append np (NORMALIZED) to kept   # heals a non-normalized legit entry
       _write_registry(home, kept)   # kept = surviving normalized ADD-project paths
    7. return 0

  4xx-equiv codes: "update_in_progress" | "unsafe_registry_path" (relative path) | "registry_corrupt" | "no_global_home"

Schema / files touched:
  <home>/.update.lock   — NEW O_EXCL lockfile (presence = held; same mechanism in BOTH twins so a pip-held
                          lock blocks an npm run and vice-versa). EXCLUDED from the MANAGED mirror AND
                          _is_user_data → never snapshotted, never reconciled, never restored.
  <home>/registry.json  — read BEFORE any write; rewritten only with kept VALID paths; byte-intact on every reject.
  bin/cli.js: cmdUpdateGlobal acquires the SAME O_EXCL lockfile (acquireUpdateLock, released on process exit)
              + the validation (relative → LOUD; else normalize + is-ADD-project) + the same four codes.

INV: a managed-file reconcile NEVER targets a non-absolute path nor a dir lacking `.add/` (the is-project backstop).
INV: every reject (lock-busy / relative-path-unsafe / corrupt / no-home) leaves registry.json byte-identical.
```

Least-sure flag surfaced at freeze: [contract] v2 swaps the lock to an O_EXCL lockfile in BOTH twins (the v1 flock-pip/O_EXCL-npm split was found by the refute-read NOT to serialize cross-twin) — the residual is that an O_EXCL lockfile is NOT auto-released on a hard crash/SIGKILL (flock was), so a killed run can leave a stale `.update.lock` that wedges the next run until removed; mitigated by a "remove if stale" hint in both twins and that update --global is a rare, re-runnable admin action. (Prior [spec] flag still holds: the is-ADD-project check is the security backstop for absolute entries — low residual.)

Status: FROZEN @ v2 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject (14 tests, hermetic via injected env)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_runs_under_lock_then_releases: install proj + reg=[proj]; delete .add/docs / run update --global / docs restored + a 2nd run also exits 0 (lock freed)
  - test_concurrent_update_fails_fast: hold the flock on <home>/.update.lock / run update --global / non-zero + "update_in_progress" + .add/docs NOT restored (nothing reconciled)
  - test_lock_released_after_failure: reg has a relative path (fails) / run then fix reg + re-run / the 2nd run exits 0 (lock was released)
  - test_valid_registry_path_predicate: a real ADD project / non-normalized-to-it / a non-project dir / True · True · False
  - test_relative_path_aborts_loud: reg=[rel, proj] / run / non-zero + "unsafe_registry_path" + registry byte-intact + sibling NOT reconciled + home not re-stamped
  - test_absolute_nonnormalized_nonproject_dropped: reg=[proj, "<abs>/area/../gone"] (no .add at normpath) / run / exit 0 + no .add created + dropped
  - test_absolute_nonnormalized_project_healed: reg=["<abs>/sub/../proj"] / run / exit 0 + registry rewritten with the normalized "/…/proj"
  - test_existing_nonproject_dropped: reg=[proj, plain-dir] / run / proj reconciled + no .add in plain + plain dropped
  - test_vanished_pruned: reg=[proj, vanished] / run / vanished pruned, proj kept (preserved)
  - test_corrupt_registry_loud: corrupt registry.json / run / non-zero + "registry_corrupt" + byte-intact
  - test_no_home_fails: home unstamped / run / non-zero + "no_global_home"
  - test_lockfile_never_leaks: after a reconcile / no .update.lock under any project .add/ + not _is_user_data
  - test_parity_surface: cli.js + _installer.py carry _update_lock / _valid_registry_path / update.lock / the codes
  - test_npm_relative_path_rejected: node cli.js update --global with a relative reg entry / non-zero + "unsafe_registry_path"
</test_plan>

Tests live in: `add-method/tooling/test_global_update_harden.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/bin/cli.js`
Strategy (ordered batches): 1. `_update_lock` ctx-mgr (flock LOCK_EX|LOCK_NB on `<home>/.update.lock`) + `_valid_registry_path`. 2. wrap `_update_global` body in the lock + pre-scan + in-loop classify (vanished/non-project/ok). 3. exclude the lockfile from MANAGED + `_is_user_data`. 4. mirror in cli.js (O_EXCL/mkdir lockfile + validation + codes).
Known-problem fixes: flock-not-released-on-exception → use a `try/finally` (or `with`) so the fd closes + unlock even on _fail; macOS `/var`→`/private/var` resolved-path skew → tests build the home via a real install + resolve project paths (lesson from global-data-restore); softened rule → a reconcile is gated by the is-ADD-project (`np/.add`) backstop, NOT by normpath equality, so only a relative path is LOUD (the ⚠ §1 backstop assumption).
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): the lock guards the WHOLE run (read→reconcile→rewrite) as one critical section; a reject path must release the lock AND leave registry.json byte-intact (no partial write).
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

- [x] all tests pass — full canonical suite 2267/0; the task's own 15 tests green
- [x] coverage did not decrease — +15 tests (incl. a cross-twin concurrency regression test added at v2)
- [x] no test or contract was altered during build — the v2 change went through the PROPER change-request loop (specify→re-freeze §3 @ v2→tests RED→build); no test/contract hand-edited on a dirty build
- [x] the green was EARNED, not gamed — refute-read EARNED (see verdict); the v1 NOT-EARNED finding (cross-twin lock gap) was a REAL bug, fixed under v2 and re-confirmed by a second independent reviewer
- [x] concurrency / timing of the risky operation is safe — v2 O_EXCL lockfile serializes BOTH twins (the v1 flock-pip/O_EXCL-npm split did NOT — caught + fixed); lock released on success, on early `_fail`, and (no fd opened) on the contention path
- [x] no exposed secrets, injection openings, or unexpected dependencies — NO new deps (dropped fcntl; uses stdlib os/contextlib); a relative path (traversal vector) is rejected LOUD, a reconcile never lands in a non-`.add/` dir
- [x] layering & dependencies follow CONVENTIONS.md — installer-only (`_installer.py` + `bin/cli.js`); ENGINE_MD5 6cc73630 + ENGINE_PKG digests UNCHANGED (installer is outside both pins)
- [x] a person reviewed and approved the change — Tin Dang signed off the gate PASS at verify (risk: high · conservative)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] while one `update --global` holds the home's `.update.lock` (the O_EXCL lockfile), a second returns "update_in_progress" non-zero with nothing reconciled — confirmed by test_concurrent_update_fails_fast (holds the lockfile, asserts exit≠0 + the sentinel docs/ NOT restored) + test_cross_twin_lockfile_blocks_both (a plain pre-existing lockfile fails BOTH pip and the node subprocess)
- [x] a registry containing a RELATIVE path aborts the whole run with "unsafe_registry_path" exit 1, registry.json byte-identical, the valid sibling project NOT reconciled, home not re-stamped — confirmed by test_relative_path_aborts_loud (exact-byte registry compare + "9.9.9" absent from the stamp)
- [x] an absolute non-normalized path whose normalized form is a real project is HEALED — confirmed by test_absolute_nonnormalized_project_healed (rewritten registry holds the normalized path, not the "../" form)
- [x] an existing dir with no .add/ (including via an absolute "../" path) is warned + dropped and never has .add/ created in it, while a sibling ADD project IS reconciled — confirmed by test_existing_nonproject_dropped + test_absolute_nonnormalized_nonproject_dropped
- [x] the lock is released after a failed run (a follow-up `update --global` succeeds) — confirmed by test_lock_released_after_failure (asserts the lockfile is unlinked even on the failed run, then a 2nd run exits 0)
- [x] the home's `.update.lock` never appears inside any project's `.add/` after a reconcile and is not user-data — confirmed by test_lockfile_never_leaks (rglob empty + `not _is_user_data(".update.lock")`)
- [x] cli.js update --global acquires the SAME O_EXCL lockfile, rejects a relative registry path, and emits the same four codes — confirmed by test_parity_surface (call-sites: `acquireUpdateLock(home)`, `openSync(lockPath,"wx")`) + test_npm_relative_path_rejected (node subprocess) + test_cross_twin_lockfile_blocks_both

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_update_lock` is called at `_update_global` (`with _update_lock(home):`); `_valid_registry_path` is called in the reconcile loop; `acquireUpdateLock`/`validRegistryPath` are called in `cmdUpdateGlobal`; `LOCK_FILE` is referenced by both `_DATA_EXCLUDE`/`DATA_EXCLUDE` and the lock helpers. Confirmed by grep + the strengthened call-site parity test.
- [x] DEAD-CODE (code) — none: the prior `import fcntl` + `_HAVE_FLOCK` skip were removed from the test; no orphaned symbol left (the 2nd reviewer confirmed no unused symbol).
- [x] SEMANTIC (prose / non-code) — read the frozen §3 v2 in full: the O_EXCL-both mechanism, the four codes, and the stale-lock disclosure all match the impl; both twins' update_in_progress messages carry the "remove if stale" hint.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED (at v2)
By: agent (2 independent subagents) · adversarially checked: (1st pass) traversal bypass attempts, lock TOCTOU/release-on-every-path, registry byte-intact on every reject, py↔js parity, per-test earned-green → found a REAL cross-twin lock-incompatibility bug (flock-pip/O_EXCL-npm don't interoperate) ⇒ NOT-EARNED; fixed via the v2 re-freeze (O_EXCL both twins) + a cross-twin regression test. (2nd pass) re-verified the fix → FIX-CONFIRMED: cross-twin serialization both directions, lockfile released on success/early-fail/contention, npm release-on-exit, parity SAFE, no new defect (only a stale code comment, now corrected). Residual: stale-lock-on-SIGKILL — accepted + disclosed in both twins' messages and §3.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): rate of update_in_progress (lock contention) · rate of unsafe_registry_path / non-project drops (registry drift or tampering) · stale-lockfile incidents (a `.update.lock` outliving its run).

### Decisions (ADR)
- [AI] specify — chose skip+warn-all  ||  fail-fast-lock; rejected SOFTENED hybrid — LOUD only on non-absolute (the real traversal vector) · normalize+skip benign absolute entries · LOUD-on-any-non-normalized (rejected: false-positive aborts) · block-with-timeout
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · dropped] stale-lock recovery: detect a dead-holder / age out the `.update.lock` so a SIGKILL'd `update --global` doesn't wedge future runs (evidence: refute-read residual — O_EXCL is not auto-released on crash, unlike flock).
- [SPEC · dropped] serialize `install --global` under the same lock in both twins (evidence: refute-read Finding 2 + the §3 schema names installGlobal; v2 scoped the lock to `update --global` only — the multi-project critical section).
- [SPEC · dropped] optional block-with-timeout lock mode for CI flows that prefer a short wait over fail-fast (evidence: fail-fast was the chosen default; a pipeline may want to queue).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a frozen contract that pins a per-twin IMPLEMENTATION mechanism (flock for pip, O_EXCL for npm) can fail its own INTENT ("pip + npm serializes concurrent runs") — freeze the OBSERVABLE behavior (cross-twin serialize), not the mechanism; the verify-phase refute-read is what caught it → re-freeze v2 (evidence: v1 NOT-EARNED, the two twins didn't interoperate). [folded foundation-version 59]
- [TDD · folded] a structural parity test asserting only token PRESENCE (string-in-source) passes even when the symbol is never CALLED — assert call-sites + a behavioral smoke (evidence: refute-read Finding 3; strengthened test_parity_surface to check `with _update_lock(home):` / `acquireUpdateLock(home)`). [folded foundation-version 59]
- [TDD · folded] a concurrency mechanism needs a CROSS-implementation test (a pip-held lock must block npm and vice-versa), not just same-twin contention — the v1 same-twin tests were green while cross-twin was broken (evidence: test_cross_twin_lockfile_blocks_both added at v2). [folded foundation-version 59]
