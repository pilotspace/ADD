# TASK: global-update-harden follow-ups: stale-lock recovery, install --global coverage, CI timeout mode

slug: global-lock-followups · created: 2026-07-02 · stage: mvp · risk: high
milestone: install-update-hardening
autonomy: conservative
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `add-method/src/add_method/_installer.py:_update_lock(home: Path) -> contextmanager` (1218-1240) — the cross-twin O_EXCL lockfile at `<home>/.update.lock`. CONFIRMED (read in full): `os.open(O_CREAT|O_EXCL|O_WRONLY)`, `FileExistsError`→`BlockingIOError`, unconditional `os.close`+`os.unlink` in `finally`. Zero staleness/liveness signal is read anywhere in this function today — a SIGKILL'd holder's lockfile survives forever. ADD: (1) a stale-lock self-heal before falling back to fail-fast, (2) an opt-in bounded wait (`timeout`), (3) a diagnostic PID+UTC-timestamp stamp written into the lock's content (informational only).
- `add-method/src/add_method/_installer.py:_update_global(target, *, force, bundled, version, env) -> int` (1252-1331) — the ONLY current caller of `_update_lock`, via `with _update_lock(home):` (inside a `try/except BlockingIOError` at the function's outer level). ADD: thread a new `lock_timeout` parameter through to `_update_lock`.
- `add-method/src/add_method/_installer.py:install(target, force, stage, name, yes, non_interactive, bundled, env, as_global, as_global_data, as_global_data_restore, rule_file) -> int` (888-1078) — CONFIRMED by reading the full body: the `as_global` block (`_reconcile_global` → `_write_stamp` → `_read_registry` → `reg.append` → `_write_registry`) runs completely UNGUARDED today — zero references to `_update_lock` anywhere in this function. This is the exact gap Must-b closes: a fresh `install --global` racing a concurrent `update --global` (or another `install --global`) can interleave writes to the SAME `<home>/registry.json`/home mirror (each individual write is atomic; the read→modify→write SEQUENCE across two racing processes is not).
- `add-method/src/add_method/_installer.py:LOCK_FILE` (690, value confirmed `".update.lock"`) · `_DATA_EXCLUDE` (691, confirmed `{"tooling","docs",".update-cache",STAMP_FILE,LOCK_FILE}`) — the lockfile is ALREADY excluded from user-data (never snapshotted/reconciled/restored); this exclusion needs NO change, confirmed by reading the literal values, not assumed.
- `add-method/src/add_method/_installer.py:resolve_global_home(env=None) -> Path` (604-617) — pure/total, reads HOME from an INJECTED `env` mapping (`ADD_HOME → XDG_DATA_HOME/add → <HOME>/.add`); the SAME injection point this task reuses for a new `ADD_LOCK_STALE_SECONDS` override, so §4 (next phase) can prove self-heal hermetically without a real multi-minute sleep.
- `add-method/src/add_method/_installer.py:_prune_data(home, *, force=False)` (779-799) / `prune_data(*, force=False, env=None) -> int` (802-824) — CONFIRMED: neither takes `_update_lock` today (read both bodies in full; zero lock references). A `prune-data --force` racing `update --global`'s re-persist of an opted-in snapshot (`_update_global`'s `_persist_data(home, np)` call), or racing another `prune-data --force`'s `shutil.rmtree`, is unguarded — real, but a CONSCIOUS deferral for this task (see §1 Framings weighed / §3 OUT-of-scope), not an accidental omission.
- `add-method/bin/cli.js:acquireUpdateLock(home)` (1097-1115) — the npm twin. CONFIRMED: `fs.openSync(lockPath,"wx")`; on `EEXIST`, calls `fail("update_in_progress: ...")` directly — and `fail()` (line 35: `function fail(msg){ process.stderr.write(...); process.exit(1); }`) calls `process.exit(1)` DIRECTLY, never throws. Release is wired via `process.on("exit", release)` (not a `try/finally` at the call site). This shapes the retry/self-heal loop: it must be a plain control-flow loop that calls `fail()` at most ONCE, only after every retry/self-heal attempt is exhausted — never inside a construct `process.exit` would skip.
- `add-method/bin/cli.js:cmdUpdateGlobal(args)` (1117-1160) — calls `acquireUpdateLock(home)` (1123) unconditionally before reading the registry. ADD: thread a `--lock-timeout` value through.
- `add-method/bin/cli.js:installGlobal(args, chosenTarget)` (1063-1079) / `cmdInit(args)` (680-730, calls `installGlobal` at line 724: `if (args.global) installGlobal(args, chosenTarget);`) — CONFIRMED unguarded: `installGlobal` runs `reconcileGlobal` → `writeStamp` → `readRegistry` → `reg.push` → `writeRegistry` with zero lock calls — mirrors the Python gap exactly.
- `add-method/bin/cli.js:parseArgs(argv)` (37-79) — the flag parser. CONFIRMED: value-taking flags (`--stage`, `--name`) follow one exact idiom (lines 68-74): `const v = argv[++i]; if (v == null || v.startsWith("--")) fail(a + " requires a value");`. The new `--lock-timeout <seconds>` flag reuses this EXACT shape, not a new parsing convention.
- `add-method/src/add_method/_cli.py:main(argv)` (12-120) — the pip dispatch. CONFIRMED: the `update` subcommand's argparse block and the `init` subcommand's argparse block both have NO `--lock-timeout` today. Both need the new flag, threaded to `update(..., lock_timeout=...)` / `install(..., lock_timeout=...)`.
- `add-method/tooling/test_global_update_harden.py` — the EXISTING test file (its own docstring: "FROZEN @ v2", testing `global-update-harden`'s OWN frozen §3). Its `_Base`/`_env()`/`_hold_lock`/`_release`/`_update()` hermetic pattern is the template §4 (a LATER phase, not drafted here) should extend for the new self-heal/timeout/install-lock coverage — cited for context only.

Context (working folder):
- `.add/milestones/install-update-hardening/MILESTONE.md` — still template-blank (only the `goal:` line is filled: "add.py init/update (both --global and project-scope, pip+npm twins) survive a crash or a concurrent run without leaving a half-written .add/ tree or a wedged lock"); NOT filled by this task — the orchestrator's job once all sibling tasks' scope is known.
- `.add/tasks/global-update-harden/TASK.md` (ARCHIVED, phase: done, FROZEN @ v2) — the VERBATIM source of this task's entire scope: its own §7 Spec delta lines name exactly stale-lock recovery · serialize `install --global` under the same lock · an optional block-with-timeout mode. Its own §1 ⚠ assumption ("the lock is FAIL-FAST... not auto-released on SIGKILL... a stale `.update.lock` is removed by hand") is the residual this task closes.
- `.add/tasks/global-data-restore/TASK.md` §7 (DONE) — a 4th, adjacent delta tagged `[global-update-harden]`: "a home file-lock to serialize concurrent prune-data / update --global (two prune-data --force could race on rmtree)". CONSCIOUSLY addressed (see §1 Framings weighed) — decided OUT of this task's Must list; named, not dropped.
- `.add/tasks/project-scope-atomic-reconcile/TASK.md` (SIBLING, Status: DRAFT, same milestone) — touches `_clean_replace`/`cleanReplaceTree` (crash-safety of the COPY mechanism itself), a DIFFERENT function from anything this task touches. Its own OUT-of-scope block names a 4th sibling task, `project-scope-install-lock`, as the owner of "serializing two concurrent install/update runs against the SAME per-project dest" — a PER-PROJECT lock, confirmed DIFFERENT from this task's PER-HOME lock (`_update_lock` guards `<home>/registry.json` + the home mirror, never a per-project target directory). No overlap.
- No existing "timeout"/"retry"/"stale" mechanism anywhere else in `_installer.py` or `cli.js` (grepped both files) — this task introduces genuinely new vocabulary for 2 of its 3 Musts (staleness + timeout); the 3rd (install --global under the lock) reuses the EXISTING `update_in_progress` code with zero new taxonomy.

Honors (patterns / conventions):
- **Freeze OBSERVABLE behavior, not the per-twin mechanism** (CONVENTIONS.md fv59, `global-update-harden`'s own v1→v2 lesson) — §3 states the observable self-heal/timeout guarantee once; each twin keeps its own native primitive (`os.stat`/`os.open` vs `fs.statSync`/`fs.openSync`).
- **cli.js's `fail()` calls `process.exit(1)` directly, skipping pending `finally`/loop state** (confirmed line 35; re-affirmed by `project-scope-atomic-reconcile`'s own §0 Issues/Risks #8 on this SAME function) — the retry/self-heal loop in `acquireUpdateLock` must call `fail()` at most once, only after every retry/self-heal attempt is exhausted.
- **Env-injectable configuration for hermetic tests** (`resolve_global_home(env=None)`'s own pattern) — reused for the new `ADD_LOCK_STALE_SECONDS` override, so §4 can prove self-heal without a real multi-minute sleep.
- **A dead-PID liveness check is NOT safely portable via stdlib/builtins alone.** CPython's `os.kill(pid, sig)` on Windows opens the process and calls `TerminateProcess(handle, sig)` for any `sig` other than `CTRL_C_EVENT`/`CTRL_BREAK_EVENT` — so `os.kill(pid, 0)` does not merely PROBE liveness on Windows, it can actually TERMINATE the target process. This is well-documented CPython/Windows behavior; it was NOT independently re-verified on a live Windows host this session (see the lowest-confidence flag in §3). It directly shapes the chosen mechanism: age (mtime), never PID-liveness, is the DECISIONAL signal.
- **Reuse the existing reject code, never a new one** — `update_in_progress` already exists and is asserted by name in `test_global_update_harden.py`; this task extends its CALL SITES (install --global, an expired `--lock-timeout` wait) rather than inventing a parallel code — matches this codebase's demonstrated preference for a minimal, non-proliferating error taxonomy.
- **CLI value-flag parsing idiom** — Python: `argparse.add_argument("--flag", type=X, default=None)`; JS: the `--stage`/`--name` shape (`argv[++i]` + `fail(a + " requires a value")`). The new `--lock-timeout <seconds>` flag reuses both idioms verbatim.

Seams consulted: none apply (checked `.add/SEAMS.md` — its entries cover ADD's own engine/§5-scope/phase-extraction conventions, not installer lock primitives).

Anchors the contract cites: `_update_lock` (extended signature) · `acquireUpdateLock` (extended) · `_update_global` (threads `lock_timeout`) · `cmdUpdateGlobal` (threads `--lock-timeout`) · `install`/`cmdInit` (NEW: the `as_global` block wrapped under the same lock) · `installGlobal` (NEW: wrapped) · NEW `ADD_LOCK_STALE_SECONDS` env override · NEW `--lock-timeout <seconds>` CLI flag (both twins) · `LOCK_FILE`/`_DATA_EXCLUDE` (cited, unchanged — already correct).

Issues/Risks (→ feed §1):
1. **Core gap**: a SIGKILL'd `update --global` (or, after Must-b, a SIGKILL'd `install --global`) leaves `<home>/.update.lock` forever — every future global operation fails "update_in_progress" until a human manually deletes the file. No existing signal (liveness or age) is checked.
2. **`install --global` is unguarded today** — confirmed by reading the full function body: zero `_update_lock` references. A racing `install --global` + `update --global` (or two concurrent `install --global`s) can interleave `_reconcile_global`/`_write_stamp`/`_read_registry`/`_write_registry` on the SAME home; each write is individually atomic, but the read→modify→write SEQUENCE is not, so one process's registration can be silently lost (last-writer-wins on the whole list, not a merge).
3. A portable "is the holder process still alive" check does NOT exist via stdlib/builtins alone on Windows (see Honors) — the achievable guarantee is age-based (mtime), not liveness-based; a real, disclosed LIMIT (see §3's least-sure flag), not an oversold "we detect crashes" claim.
4. Clock skew is a genuine hazard for an age-based staleness check: if a live holder's lock is judged OLDER than the threshold because of a forward clock jump on the CHECKING process, two processes could believe they hold the lock at once — the O_EXCL create still lets only one WIN at the syscall level, but the ORIGINAL (still-alive) holder's in-flight write is no longer serialized against the new holder's. A real, disclosed residual, mitigated only by a generous default threshold, not eliminated.
5. `prune_data`'s own concurrency gap (see Context) is a 4th, adjacent, CONSCIOUSLY-deferred decision — named so it is not lost, not silently rolled in or silently dropped.

Related intent:
- PROJECT.md §Domain: "Design for failure... Atomic writes only; no partial state," and the user's own global critical rule ("design for failure: timeouts, retries, circuit breakers, rollback strategy in IO request") — this task is precisely that discipline applied to the one lock primitive the whole milestone goal depends on.
- Milestone `install-update-hardening` goal: "...survive a crash or a concurrent run without leaving a half-written .add/ tree or a wedged lock" — this task delivers the "wedged lock" half in full (stale-recovery) and closes the "install --global" gap in the "concurrent run" half; `project-scope-atomic-reconcile`'s sibling half covers the copy mechanism, not the lock.
- `.add/tasks/global-update-harden/TASK.md` §7 Spec delta — the verbatim source of Musts (a)/(b)/(c) (see Context).
- GLOSSARY.md: no existing "lock"/"timeout"/"stale" domain term — these stay internal code vocabulary (mirrors `project-scope-atomic-reconcile`'s own "Glossary deltas: none" precedent for a hardening-only task).

Ground SHA: c8d373a

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: global-lock-followups — close the 3 named residuals from `global-update-harden`'s own v2 freeze: self-heal a wedged `.update.lock`, extend the SAME lock to `install --global`, and add an opt-in bounded-wait mode for CI.
Framings weighed: mtime age-out as the DECISIONAL staleness signal + an informational PID/UTC-timestamp stamp (diagnostic-only, never read to decide staleness) + an opt-in `--lock-timeout` bounded wait + `install --global` sharing the SAME `_update_lock`, scoped to only its existing home-touching span (chosen) · PID-liveness dead-holder detection via `os.kill(pid,0)`/Windows `OpenProcess` (rejected: not safely portable — on Windows, `os.kill(pid,0)` opens the process and calls `TerminateProcess(handle,0)`, i.e. it can KILL the holder rather than merely probe it; PID reuse after a reboot is a second, independent false-positive) · re-adding an advisory `fcntl.flock` alongside or instead of O_EXCL (rejected: reopens the exact cross-twin incompatibility `global-update-harden`'s own v1→v2 refute-read found and fixed — Node has no flock equivalent without a native dependency, breaking the stdlib/builtin-only constraint) · making a bounded wait the new DEFAULT with no flag (rejected: silently changes the observed behavior of every existing caller that relies on today's immediate fail-fast; an opt-in flag preserves it byte-for-byte) · a user-facing CLI flag for the staleness threshold itself (rejected: adds surface for a knob nobody should routinely tune; an env-var override plus a generous constant default is enough, mirroring how `ADD_HOME` is already an env-only knob, never a flag) · folding `prune_data` into this task's Must list (considered; DECIDED OUT — named in §3 OUT-of-scope, not silently dropped: same mechanism, cheap, but keeps this task's blast radius to the 3 named follow-ups rather than opportunistically growing it).
Must:
<must>
  - M1 (a — stale-lock self-heal): on lock contention (`EEXIST`/`"wx"`-`EEXIST`), `_update_lock`/`acquireUpdateLock` stat the existing lockfile; if `now − mtime > ADD_LOCK_STALE_SECONDS` (env-overridable, default 600s), unlink it and retry the create EXACTLY once before falling through to today's fail-fast. The O_EXCL/`"wx"` create remains the SOLE mutual-exclusion primitive — staleness only ever decides whether to RETRY, never bypasses exclusivity (at most one racing process's create can succeed at any instant, even when two processes independently judge the SAME lock stale and both attempt to reclaim it).
  - M2 (diagnostic stamp): on a successful acquire (fresh or reclaimed), the lock file's content is stamped `"<PID> <ISO-8601 UTC timestamp>\n"` — informational ONLY, never read to decide staleness (see Framings weighed). A crash between create and this stamp write leaves the file EMPTY; staleness (mtime-keyed) is unaffected, and a later contention message degrades to "holder unknown" instead of erroring on unparseable content.
  - M3 (b — install --global under the same lock): `install(..., as_global=True)`'s existing home-touching span (`_reconcile_global` → `_write_stamp` → `_read_registry` → append → `_write_registry`) runs inside the SAME `_update_lock(home, ...)`/`acquireUpdateLock(home, ...)` as `_update_global`. On contention (after M1's self-heal fails to clear it), `install()` fails "update_in_progress" and returns BEFORE any home/registry write and BEFORE the per-project managed-layer drop — mirroring the existing all-or-nothing precedent every other `as_global`-path failure in `install()` already has (e.g. "cannot write global home"), not a new partial-success shape.
  - M4 (c — opt-in bounded wait): a NEW `--lock-timeout <seconds>` flag on BOTH `init --global`/`update --global` (both twins). UNSET (default) is BYTE-IDENTICAL to today: immediate fail-fast on a live (non-stale) contended lock. When set to N > 0, a LIVE contended lock is retried/polled for up to N seconds before falling back to "update_in_progress"; `--lock-timeout 0` is defined identical to unset (immediate fail-fast, no wait). M1's self-heal fires regardless of whether `--lock-timeout` is set (a stale lock is reclaimed immediately either way; the timeout only governs waiting out a LIVE holder).
  - M5 (parity): both twins (`_installer.py`, `cli.js`) guarantee the SAME 3 observable behaviors (self-heal · install-global-locked · bounded-wait), each via its own native primitive (`os.stat`/`os.open` vs `fs.statSync`/`fs.openSync`) — per the "freeze OBSERVABLE behavior, not the mechanism" convention. `acquireUpdateLock`'s retry/self-heal loop is structured so `fail()` (which calls `process.exit(1)` directly) is invoked at most once, only after every retry/self-heal attempt is exhausted.
  - M6 (no new taxonomy): the ONLY reject code involved is the EXISTING `update_in_progress` — extended to a 2nd call site (`install --global`) and a 3rd trigger (a `--lock-timeout` wait expiring); no new machine-readable code is introduced by this task.
</must>
Reject:
<reject>
  - a lock exists, is NOT stale (age ≤ threshold), and no `--lock-timeout` (or `--lock-timeout 0`) is set -> "update_in_progress"  (unchanged from today: immediate fail-fast, nothing written, the held lock untouched)
  - a lock exists, is NOT stale, `--lock-timeout N>0` is set, and it is STILL held after N seconds -> "update_in_progress"  (same code, fires only after ~N seconds of polling, nothing written)
  - `install --global` hits either case above -> "update_in_progress"  (NEW call site, same code; the per-project managed-layer drop does NOT proceed, matching the all-or-nothing precedent of every other as_global-path failure)
</reject>
After:
<after>
  - a stale lock (age > `ADD_LOCK_STALE_SECONDS`) never wedges a future `update --global`/`install --global` — it self-heals on the very next attempt; no manual deletion required.
  - a live (non-stale) contention still fails fast by default — zero behavior change for any existing caller that never passes `--lock-timeout`.
  - `install --global` and `update --global` (and two concurrent instances of either) can never interleave writes to `<home>/registry.json` or the home mirror — exactly one wins at a time.
  - the lock file's content (PID + UTC timestamp) is purely diagnostic; no code path decides staleness from it.
  - `prune-data` is UNCHANGED by this task (see Framings weighed) — still unguarded against a concurrent `update --global`/another `prune-data --force`, a consciously named, deferred gap.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `ADD_LOCK_STALE_SECONDS` default of 600s (10 minutes) is a judgment call with a REAL two-sided cost if wrong — too short risks a false-positive reclaim of a still-alive, merely-slow holder (defeats mutual exclusion for that run, see §0 Issues/Risks #4); too long just delays self-heal of a genuinely wedged lock (inconvenient, not unsafe). Lowest confidence because there is no production timing data in this repo for a realistic worst-case registered-project count on a slow disk/CI runner to calibrate against; if wrong, it is a 1-line constant change, not a re-design.
  ⚠ the Windows `os.kill(pid, 0)` hazard (§0 Honors: it can TERMINATE the target rather than probe it) is well-documented CPython/Windows behavior but was NOT independently verified on a live Windows host this session — it is the deciding reason this design uses mtime-age, never PID-liveness, as the DECISIONAL mechanism. If wrong (a safe liveness check exists), this design is still SAFE, just more conservative than necessary (a dead holder self-heals only after the timeout elapses, not near-instantly) — a UX cost, not a correctness bug.
  - [ ] the diagnostic PID/timestamp stamp (M2) adds negligible risk (one small write right after `open`) but is genuinely new, separable surface; if the human would rather ship M1/M3/M4 WITHOUT it (pure age-out, no content write), it is a cheap, isolated cut.
  - [ ] `prune_data` staying OUT of this task's Must list (see Framings weighed) is a scope call, not a technical constraint — folding it in later is a small, mechanical change request (same primitive, ~1 line), not a re-design.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a stale lock self-heals so a wedged run recovers   # M1
  Given <home>/.update.lock exists and its mtime is older than ADD_LOCK_STALE_SECONDS (simulating a SIGKILL'd holder)
  When I run `update --global` (or `install --global`)
  Then the stale lockfile is reclaimed (unlinked and re-created) and the run proceeds to completion (exit 0)
  And no manual deletion of the lockfile was needed

Scenario: a live, non-stale lock is NOT reclaimed — fail-fast is unchanged   # M1 (regression guard) + Reject update_in_progress
  Given <home>/.update.lock exists and its mtime is WITHIN ADD_LOCK_STALE_SECONDS (a genuinely in-flight holder)
  When I run `update --global` with no --lock-timeout
  Then the run fails immediately with "update_in_progress" and nothing is reconciled
  And the held lockfile is left untouched (not reclaimed)

Scenario: mutual exclusion holds even when two processes race to reclaim the SAME stale lock   # M1 (TOCTOU safety)
  Given a stale <home>/.update.lock and two processes that both observe it as stale at the same instant
  When both attempt to reclaim (unlink + re-create) concurrently
  Then exactly one process's create succeeds and proceeds under the lock
  And the other observes the lock as freshly held (by the winner) and falls back to its own normal contention handling (immediate fail-fast, or its own --lock-timeout wait)

Scenario: a lock whose mtime is bogusly in the future is never treated as stale   # M1 edge case (clock-skew safe direction)
  Given <home>/.update.lock exists with an mtime set AHEAD of the current clock (simulating clock skew)
  When I run `update --global`
  Then the lock is NOT reclaimed (treated as live) and the run fails fast with "update_in_progress"

Scenario: a crash between lock-create and the diagnostic stamp leaves a self-healable empty lock   # M2 edge case
  Given <home>/.update.lock exists, is EMPTY (0 bytes — simulating a crash before the PID/timestamp write), and its mtime is older than the staleness threshold
  When I run `update --global`
  Then the empty stale lock is reclaimed exactly like a stamped one (mtime alone decides staleness)
  And no error is raised while attempting to read the (absent) diagnostic content

Scenario: the diagnostic PID/timestamp is informational only   # M2
  Given a lock currently held by a live process
  When a second run observes the contention
  Then the "update_in_progress" message MAY include the holder's PID and acquisition timestamp read from the lock file's content
  And that content is NEVER consulted to decide whether the lock is stale (only mtime is)

Scenario: install --global is serialized under the same lock as update --global   # M3
  Given update --global currently holds <home>/.update.lock (a live, non-stale hold)
  When I run `install --global` against a fresh target
  Then it fails fast with "update_in_progress"
  And nothing is written to the home mirror or registry.json, and the target's per-project managed-layer drop does NOT occur

Scenario: two concurrent install --global runs cannot interleave registry writes   # M3
  Given no lock is currently held
  When two `install --global` runs start at overlapping times
  Then exactly one acquires the lock and completes its home+registry write; the other fails fast with "update_in_progress" (or self-heals per M1 if the first is stale) with nothing written
  And registry.json never reflects a partially-interleaved write from both runs

Scenario: a fresh (uncontended) install --global is unaffected   # M3 (regression guard)
  Given no lock is held and the home is unstamped (first-ever global install)
  When I run `install --global`
  Then it completes exactly as before: the home is stamped, the target is registered, and the per-project drop runs
  And the lock is released (the file is gone) by the time the run returns

Scenario: --lock-timeout waits out a live holder that releases in time   # M4
  Given update --global currently holds the lock, and the holder releases it 2 seconds later
  When I run `update --global --lock-timeout 10`
  Then the waiting run acquires the lock once it is freed and completes (exit 0)
  And it did not fail "update_in_progress"

Scenario: --lock-timeout still fails fast once the wait budget is exhausted   # M4 + Reject update_in_progress
  Given update --global currently holds the lock for LONGER than the wait budget
  When I run `update --global --lock-timeout 2`
  Then the waiting run fails with "update_in_progress" after roughly 2 seconds (not instantly, not indefinitely)
  And nothing is reconciled

Scenario: --lock-timeout unset (or 0) behaves byte-identically to today's default   # M4 (regression / back-compat guard)
  Given a live, non-stale lock is held
  When I run `update --global` with no --lock-timeout flag, and separately with --lock-timeout 0
  Then both fail immediately with "update_in_progress" (no observable wait in either case)

Scenario: parity — cli.js self-heals, locks install --global, and honors --lock-timeout the same way   # M5
  Given the npm cli.js code paths for acquireUpdateLock / installGlobal / cmdUpdateGlobal
  When I read the source and run the node subprocess smokes
  Then acquireUpdateLock performs the same stale-mtime reclaim before calling fail(), installGlobal is called only after acquiring the lock, and --lock-timeout is parsed with the same "requires a value" idiom as --stage/--name
  And a behavioral smoke (node subprocess) confirms a stale lock self-heals and a live lock fails fast with the same "update_in_progress" text

Scenario: prune-data concurrency is explicitly ruled out of this task's scope   # deliberate ruling-out (Framings weighed)
  Given two prune-data --force runs (or a prune-data --force racing an update --global re-persist) overlapping in time
  When both run against the same home
  Then this task makes NO new guarantee about their interleaving — prune_data is UNCHANGED by this task
  And this is a disclosed, conscious deferral (named in §3 OUT-of-scope), not a silently missed case
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_update_lock(home: Path, *, timeout: float | None = None, env: Mapping | None = None) -> context manager
acquireUpdateLock(home, { timeout = null } = {}, env = process.env) -> release()   # JS twin, same observable shape

  ACQUIRE loop (replaces today's single-shot open):
    stale_after = float(env.get("ADD_LOCK_STALE_SECONDS", 600))   # env-overridable; default 600s (10 min)
    deadline = (now() + timeout) if timeout else None              # None/0 = today's byte-identical fail-fast
    loop:
      try: fd = os.open(lock_path, O_CREAT|O_EXCL|O_WRONLY)        # / fs.openSync(lockPath, "wx")
      except already-exists:
        age = now() - stat(lock_path).mtime                        # NEGATIVE age (future mtime) => never stale
        if age > stale_after:
          unlink(lock_path)   # best-effort — ENOENT from a losing race is swallowed, not an error
          continue loop       # retry the create immediately (≤1 extra hop)
        if deadline and now() < deadline:
          sleep(short poll interval); continue loop
        raise BlockingIOError   # -> caller's existing `except` maps to "update_in_progress"
                                 # (JS: acquireUpdateLock calls fail("update_in_progress: ...") directly —
                                 #  unchanged trigger text, now reached only after self-heal + any
                                 #  --lock-timeout wait are exhausted)
      # acquired (fresh or reclaimed) — best-effort diagnostic stamp, NEVER read to decide staleness
      write(fd, f"{pid} {utc_iso_now()}\n")   # write errors here are swallowed — informational only
      -> on the SAME exit paths as today (success or exception): close(fd); unlink(lock_path) best-effort.

  UNCHANGED: the O_EXCL/"wx" create is still the ONLY mutual-exclusion primitive; staleness-reclaim only
  decides whether to RETRY the create, never substitutes for it — at most one racing create succeeds at any instant.

_update_global(target, *, force=False, bundled=None, version=None, env=None, lock_timeout=None) -> int
  -> with _update_lock(home, timeout=lock_timeout, env=env_map): ...           # body UNCHANGED, new param threaded

install(target=".", force=False, ..., as_global=False, ..., lock_timeout=None) -> int
  as_global block ->
    try:
      with _update_lock(home, timeout=lock_timeout, env=env_map):
        _reconcile_global(...); _write_stamp(...); reg = _read_registry(...); reg.append(...); _write_registry(...)
    except BlockingIOError:
      return _fail("update_in_progress: ...")     # SAME code/message shape _update_global already uses
  # scope is EXACTLY today's as_global block — the per-project _reconcile() call further below stays OUTSIDE
  # the lock, unchanged. A lock failure aborts install() ENTIRELY (no per-project drop) — matches the existing
  # all-or-nothing precedent every other as_global-path error already has (e.g. "cannot write global home").

installGlobal(args, chosenTarget)
  -> const release = acquireUpdateLock(home, { timeout: args.lockTimeout });
     reconcileGlobal(...); writeStamp(...); ...; writeRegistry(...);
     # release fires via acquireUpdateLock's own process.on("exit", release) — unchanged mechanism
cmdInit(args) -> if (args.global) installGlobal(args, chosenTarget);   # unchanged call site, now lock-guarded inside

# ── CLI surface ── one new flag, BOTH twins, the SAME idiom as --stage/--name (JS) / type=float (argparse)
init      [--lock-timeout <seconds>] [--global] ...
update    [--lock-timeout <seconds>] [--global] ...
  --lock-timeout <seconds>   absent/omitted -> None -> today's immediate fail-fast, byte-identical.
                             0              -> identical to omitted (no wait).
                             N > 0          -> poll up to N seconds for a LIVE (non-stale) lock before
                                               "update_in_progress". A stale lock (see above) self-heals
                                               regardless of this flag.

# ── Reject code (REUSED, not new) ──
update_in_progress   fires from: (a) update --global, unchanged trigger · (b) install --global, NEW call
                      site · (c) a --lock-timeout wait that expires still holding — 1 code, 3 triggers, 0
                      new taxonomy.

Schema / files touched:
  <home>/.update.lock   content CHANGES from always-empty to "<PID> <UTC ISO ts>\n" on a successful acquire —
                        purely diagnostic (surfaced in a later contention message when readable/parseable;
                        degrades to "holder unknown" otherwise). mtime (unchanged mechanism: file creation
                        time) is the ONLY signal staleness decides on. Still excluded from
                        _is_user_data/_DATA_EXCLUDE (unchanged — already correct, confirmed by reading the
                        constant at Ground).
  <home>/registry.json  unchanged shape; now ALSO protected during install --global's read-modify-write
                        (previously only during update --global's).

INV: the O_EXCL ("wx") create is the SOLE mutual-exclusion primitive at every layer of this design — staleness
     detection and the --lock-timeout wait both only ever decide WHETHER/WHEN to retry that create; neither
     ever grants the lock by any other means. At most one racing create succeeds at any instant (unchanged).
INV: the diagnostic PID/timestamp content is NEVER read to decide staleness (mtime-only) — named explicitly
     because it is the one deliberately-NOT-chosen alternative (see the least-sure flag) and must stay that
     way even as an implementation evolves; a future task wanting LIVENESS-based staleness is a new contract.
INV: `--lock-timeout` absent or 0 reproduces TODAY's behavior byte-for-byte — every existing caller (nothing
     passes this new flag today) observes ZERO change from this task.
INV: a lock failure inside `install(as_global=True)` aborts the WHOLE call (no partial home write, no
     per-project drop) — the same all-or-nothing shape every other as_global-path error already has; not a
     new failure mode.
OUT of scope (named, not silently dropped):
  - `prune_data`/`pruneData`'s OWN concurrency (a `prune-data --force` racing another, or racing
    `update --global`'s re-persist step) — the SAME `_update_lock` mechanism would cover it cheaply, but is a
    CONSCIOUS deferral (see §1 Framings weighed), not an accidental omission; a natural next follow-up, not
    required to ship with this task.
  - `_persist_data`/`_restore_data`'s own hardening — owned by the parallel sibling task
    (global-data-restore-harden).
  - Serializing two concurrent install/update runs against the SAME per-PROJECT target dir (a DIFFERENT,
    per-project lock) — owned by the sibling task `project-scope-install-lock` (named in
    `project-scope-atomic-reconcile`'s own OUT-of-scope block); this task's lock is scoped to the shared HOME +
    registry.json only, never a project directory.
  - Crash-safety of the COPY mechanism itself (`_clean_replace`/`cleanReplaceTree`) — owned by the sibling task
    `project-scope-atomic-reconcile`; this task only ever wraps EXISTING calls to it in a lock, never touches
    its body.
```

Glossary deltas: none (this task hardens an existing internal mechanism — `_update_lock`/lockfile/staleness
  are pre-existing or natural-extension internal code vocabulary, not GLOSSARY.md domain terms; mirrors
  `project-scope-atomic-reconcile`'s own "none" precedent for a hardening-only task).

Least-sure flag surfaced at freeze:
  ⚠ [spec] the Windows `os.kill(pid, 0)` hazard (documented CPython/Windows behavior: it can TERMINATE the
    held process rather than merely probe it, via `TerminateProcess` for any signal other than
    CTRL_C_EVENT/CTRL_BREAK_EVENT) is the deciding reason this design uses mtime-AGE, never PID-liveness, to
    decide staleness — well-documented but NOT independently verified on a live Windows host this session.
    Cost if wrong (a safe liveness check exists): this design is still SAFE, just more conservative than
    necessary (a dead holder self-heals only after `ADD_LOCK_STALE_SECONDS` elapses, not near-instantly) — a
    UX cost, not a correctness bug.
  Second flag: [spec] the `ADD_LOCK_STALE_SECONDS` default (600s) is a judgment call with no production timing
    data behind it — too short risks a false-positive reclaim of a still-alive, merely-slow holder (defeats
    mutual exclusion for that run); too long just delays self-heal of a genuinely wedged lock. Cheap to change
    (a single constant) if wrong.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject + the deliberate ruling-out scenario (18 tests touched:
  17 new + 1 strengthened-not-weakened, hermetic via injected env; 14 scenarios in §2, several
  covered by more than one test where a scenario has multiple assertable facets)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_stale_lock_self_heals: arrange a backdated-mtime (stale) lock at home / act run update --global / assert exit 0 + lock reclaimed + run completes, no manual deletion · covers: M1
  - test_live_lock_not_reclaimed_fails_fast: arrange a fresh (age 0) held lock / act run update --global, no --lock-timeout / assert non-zero + "update_in_progress" + lock left untouched (regression: already true pre-build, must stay true) · covers: M1, Reject
  - test_concurrent_stale_reclaim_exactly_one_wins: arrange a stale lock + 6 racer threads (Barrier-synced) calling _update_lock directly / act release all racers concurrently / assert exactly one "acquired", zero unexpected exceptions, no leaked lock file after · covers: M1 (TOCTOU safety)
  - test_future_mtime_lock_never_stale: arrange a lock with mtime set AHEAD of now (clock-skew sim) / act run update --global / assert NOT reclaimed (treated as live) + fails fast "update_in_progress" (regression: already true pre-build by having no reclaim logic; must stay true for the RIGHT reason post-build — sign-aware age check) · covers: M1 (edge case)
  - test_empty_stale_lock_self_heals: arrange a 0-byte stale lock (simulates a crash before the stamp write) / act run update --global / assert reclaimed exactly like a stamped one, no error reading absent content · covers: M2 (edge case)
  - test_successful_acquire_stamps_pid_and_timestamp: arrange no lock held / act acquire directly via _update_lock / assert lock content matches `^\d+ \S+\n?$` (PID + ISO-8601 UTC timestamp) · covers: M2
  - test_garbage_lock_content_never_errors_or_affects_staleness: arrange a stale lock with unparseable garbage content / act run update --global / assert reclaimed without error — staleness decided by mtime alone, content never consulted · covers: M2
  - test_install_global_blocked_by_a_held_lock: arrange update --global holds a live (non-stale) lock / act run install --global against a fresh target / assert fails fast "update_in_progress" + nothing written to home mirror/registry.json + the target's per-project managed-layer drop does NOT occur · covers: M3, Reject
  - test_two_concurrent_install_global_no_interleave: arrange no lock held / act two install --global runs overlap / assert exactly one wins and completes its write, the other fails fast with nothing written, registry.json never reflects a partial interleave · covers: M3
  - test_fresh_install_global_unaffected: arrange no lock held, home unstamped (first-ever) / act run install --global / assert completes exactly as before (stamped + registered + per-project drop ran) + lock file gone by return (regression guard — must stay true, the common uncontended path) · covers: M3 (regression)
  - test_lock_timeout_waits_out_a_holder_that_releases_in_time: arrange update --global holds the lock, releases ~0.2s later (a Timer) / act run update --global --lock-timeout N / assert the waiting run acquires once freed and exits 0, never raised "update_in_progress" · covers: M4
  - test_lock_timeout_expires_still_fails: arrange a holder that outlives the wait budget / act run update --global --lock-timeout 2 / assert fails "update_in_progress" after roughly the budget elapses (not instantly, not indefinitely) · covers: M4, Reject
  - test_lock_timeout_unset_or_zero_is_immediate: arrange a live, non-stale lock held / act run update --global with no flag, then separately --lock-timeout 0 / assert both fail immediately — no observable wait either way (back-compat regression guard) · covers: M4 (regression)
  - test_lock_timeout_flag_parity: arrange none (static source read) / act read _cli.py + cli.js source / assert --lock-timeout is registered on both init/update subparsers (Python) and parsed in cli.js, threaded as lock_timeout=args.lock_timeout / lockTimeout, and ADD_LOCK_STALE_SECONDS is referenced in cli.js · covers: M5
  - test_npm_stale_lock_self_heals: arrange a stale (backdated-mtime, empty) lock + ADD_LOCK_STALE_SECONDS=1 env / act run `node cli.js update --global` as a subprocess / assert exit 0, self-healed · covers: M5
  - test_npm_live_lock_still_fails_fast: arrange a real O_EXCL-held ("wx") lock / act run `node cli.js update --global` as a subprocess / assert non-zero + "update_in_progress" text (regression: already true pre-build, must stay true) · covers: M5 (regression)
  - test_prune_data_deliberately_unlocked: arrange none (static source read) / act inspect.getsource on _prune_data + prune_data (Python) and slice the pruneData..cmdPruneData span (JS) / assert neither references _update_lock/acquireUpdateLock — proves the conscious OUT-of-scope deferral stays true · covers: deliberate ruling-out (§3 OUT-of-scope)
  - test_parity_surface (PRE-EXISTING, FROZEN @ v2 — STRENGTHENED not weakened for this task's new call-site shape): arrange none (static source read) / act read _installer.py + cli.js source / assert the fuller call-site text `with _update_lock(home, timeout=lock_timeout, env=env_map):` / `acquireUpdateLock(home, { timeout: args.lockTimeout }, process.env)` each appear exactly twice (proving BOTH _update_global AND install's as_global block share the identical call site; BOTH cmdUpdateGlobal AND installGlobal share theirs) · covers: M3, M5
</test_plan>

Tests live in: `add-method/tooling/test_global_update_harden.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/src/add_method/_cli.py` `add-method/bin/cli.js` `add-method/tooling/test_global_update_harden.py`
Strategy (ordered batches): 1. `_update_lock` (Python): wrap the existing `os.open(O_EXCL)` in a self-heal + retry loop — on `FileExistsError`, stat the lockfile; if stale (mtime age > `ADD_LOCK_STALE_SECONDS`), unlink + retry once; else if a `timeout` was given, poll until the deadline; else raise `BlockingIOError` as today. Stamp `f"{pid} {utc_iso}\n"` into the fd right after a successful open (best-effort, swallow write errors). 2. `install()`'s `as_global` block: wrap the existing `_reconcile_global → _write_stamp → _read_registry → append → _write_registry` span in `with _update_lock(home, timeout=lock_timeout, env=env_map):` / `except BlockingIOError: return _fail("update_in_progress: ...")`. 3. `_cli.py`: add a `--lock-timeout` argparse flag (type=float, default=None) to the `init`/`update` subparsers; thread through to `install(..., lock_timeout=...)` / `update(..., lock_timeout=...)` / `_update_global(..., lock_timeout=...)`. 4. `cli.js` mirror: `acquireUpdateLock` gets the identical stale-check/self-heal/timeout loop (never call `fail()` inside the retry region — only `throw`); `installGlobal` wrapped in `acquireUpdateLock`; `parseArgs` gets `--lock-timeout` via the existing `argv[++i]` + "requires a value" idiom; `cmdInit`/`cmdUpdateGlobal` thread `lockTimeout` through. 5. Extend `test_global_update_harden.py` with the stale-self-heal, install-global-locked, and `--lock-timeout` scenarios, reusing its existing hermetic `_hold_lock`/`_release`/`_env()` fixtures + cross-twin subprocess smokes — do not weaken or remove any of its existing v2-frozen assertions.

Persona (optional): methodology-engine-dev
Known-problem fixes: `cli.js:fail()` calls `process.exit(1)` directly (skips `finally`) → the retry/self-heal loop in `acquireUpdateLock` must only ever call `fail()` once, after every retry/self-heal attempt is exhausted, never inside the loop body · a portable PID-liveness check does not exist (Windows `os.kill(pid,0)` can terminate) → mtime-age is the only staleness signal, never PID · clock skew making a live lock look stale → only reclaim when `age > threshold` (a future/bogus mtime never counts as stale).
Strategy actually used: AS PLANNED, in the same 5-batch order, with 3 refinements discovered mid-build:
  (1) `_update_lock`'s self-heal branch additionally guards `lock_path.stat()` itself (not just the
  `os.open`) against a vanished-file OSError — a losing racer that reaches the stat AFTER another
  thread's reclaim-unlink would otherwise crash with an uncaught FileNotFoundError instead of just
  retrying the create; required for `test_concurrent_stale_reclaim_exactly_one_wins`'s "no racer hit
  an unexpected exception" guarantee, not spelled out in the original strategy text.
  (2) install()'s as_global lock-wrap needed a SECOND except clause — `except OSError as exc:
  return _fail(f"cannot write global home {home} — {exc}")` — alongside the planned `except
  BlockingIOError`. Root cause: `_update_lock`'s own (pre-existing, unchanged) `home.mkdir(parents=
  True, exist_ok=True)` raises a plain FileExistsError when `home` exists as a non-directory —
  `_update_global` never hits this because its own `no_global_home` pre-check short-circuits first,
  but `install()`'s as_global block has no such pre-check (it is what CREATES the home). Caught by
  the PRE-EXISTING `test_global_install.py::test_home_unwritable_fails` (outside this task's declared
  touch scope — could not have been silently masked by editing that test, and wasn't; fixed in my
  own new code instead). Verified via a stash-based baseline diff: this was the ONLY one of 9
  initially-failing tests in the broader regression sweep that did NOT reproduce without my changes
  — the other 8 are pre-existing/environmental (see Decisions + OBSERVE-NOTES.md).
  (3) cli.js's bounded poll-wait needed a synchronous sleep with no new dependency; used
  `Atomics.wait` on a throwaway `SharedArrayBuffer`/`Int32Array` (builtin, permitted on Node's main
  thread unlike a browser's) — the strategy named the constraint (stdlib/builtin only) but left the
  mechanism open.
  Order: tests (TASK.md §4 + the 32-test suite) were completed and committed FIRST as commit 1
  (RED), confirmed failing for the right reason (9 AssertionError + 4 TypeError; the other 5
  new tests are legitimate regression guards already green pre-build), THEN implementation
  followed the planned batch order 1(_update_lock)->2(install's as_global wrap)->3(_cli.py flag)->
  4(cli.js mirror), landing GREEN (32/32) on the first full run after batch 4, before the 2
  refinements above were separately discovered via the broader regression sweep and fixed.
  Second build attempt (2026-07-03, reopened to `build` via `add.py reopen --to build` after an
  independent verify pass found a LIVE TOCTOU race in this lock's stale-reclaim path — this task's
  own §6 below still shows the EARLIER, now-superseded PASSED gate from before this finding;
  left untouched, the next verify pass's job to redo): `_update_lock`'s reclaim used an
  unconditional, identity-blind `os.unlink(lock_path)` — it removed whatever currently sat at the
  path with no check that it was still the SAME stale file just inspected, letting 2+ racers hold
  "the lock" simultaneously. Reproduced pre-fix at 4/30 (13.3%) against my own strengthened test
  below (same family as the original verify pass's own larger-sample 55/150, 36.7%). TDD followed
  exactly: the test change landed FIRST, alone, confirmed red against the untouched buggy code
  (4/30) before any implementation line changed.
    Fix shape deviated from this reopening's own suggested pattern TWICE, each time for a concrete,
  empirically-proven reason (re-derived from the actual code, not the paraphrase) — full mechanism
  detail in the sibling task `project-scope-install-lock`'s own §5 (identical root causes, this
  lock's own independent code and own independent measurements): (1) "rename to a per-attempt
  quarantine name" was tried first; proved identity-blind in exactly the same way as the unlink it
  was meant to replace (a rename also just operates on whatever currently sits at the shared path)
  — abandoned before a full 30-run measurement against this specific function, since the
  mechanism-level disproof (an instrumented standalone reproduction) already generalized: this
  lock's reclaim branch is structurally the same "stat -> act on a shared path" shape. (2)
  Redesigned to a "ticket-gated reclaim" keyed to the stale file's own inode number (`st_ino`) —
  improved but did NOT fully close the race: 9/30 (30%), WORSE than the 4/30 pre-fix baseline (this
  loop-based function retries far more densely than `_project_lock`'s single-retry shape, exposing
  the residual far more often). Root cause, caught via direct instrumentation of the real function
  (temporary `_DIAG_TRACE`-gated trace prints, since fully removed — `grep -rn "_DIAG_TRACE"
  add-method/` is zero hits): winning the ticket proves exclusive rights to reclaim ONE specific
  generation, but not that `lock_path` is STILL that generation by the time the code acts on it — a
  scheduling gap let the SAME path fully cycle through an entire, unrelated reclaim in the interim,
  and the ticket-winner's unconditional unlink then blindly destroyed that unrelated, currently-live
  holder's file (full captured trace: a 6th, very-late-scheduled racer's stat read the ORIGINAL
  stale inode 10s earlier; by the time it acted, the lock had already cycled through a full
  intervening reclaim by a different racer; its "won" ticket for the now-defunct inode still
  succeeded trivially, and its unlink destroyed the CURRENT live holder's fresh file instead).
  Final fix (delivered): after winning the ticket, re-stat `lock_path` IMMEDIATELY before unlinking
  and compare its CURRENT inode against the ticket's inode; unlink ONLY on a match, otherwise treat
  the ticket as moot and `continue` the loop, letting the ordinary open/EEXIST/age logic
  re-evaluate reality fresh — one extra syscall that shrinks the window from an arbitrary
  scheduling delay down to the gap between two adjacent syscalls (a residual now bounded by needing
  TWO independent, unrelated parties to both act inside that sub-microsecond gap — judged
  acceptable and disclosed, not further reducible with only cross-platform stdlib/builtin
  primitives, consistent with this task's own existing PID-liveness and clock-skew disclosures
  above). Applied independently in `_update_lock` and its own JS twin `acquireUpdateLock` — no
  shared helper introduced between them or with `_project_lock`/`acquireProjectLock` (this task's
  own §1 Framings, re-affirmed).
    Test strengthening: the test's OWN assertion was part of the gap — a cumulative
  `results.count("acquired") == 1` cannot distinguish "at most one holder at any INSTANT" (the real
  invariant) from racers legitimately, sequentially re-acquiring one after another (normal, correct
  behavior). Replaced with a temporal proof: an `active` counter incremented the instant a racer is
  inside the critical section and decremented the instant before it leaves, `peak = max(peak,
  active)` latched under the same lock guarding the shared `results` list — `peak` can only exceed
  1 on a genuine simultaneous-holder bug. `test_global_update_harden.py` is already named on this
  section's own "Scope (may touch)" line above, so this test edit needed no scope-gap note (unlike
  the sibling task) — it strengthens this existing, already-named `test_concurrent_stale_reclaim_
  exactly_one_wins` scenario's assertion rigor only, adds no new test.
    Stress evidence: the strengthened test run repeatedly after the final fix — 0/30, then 0/60
  more (0/90 total, 0 failures). The full sibling regression sweep (`test_global_install` +
  `test_global_update_harden` + `test_global_restore` + `test_global_data` + `test_reconcile_rollup`
  + `test_project_scope_lock`, 145 tests, run together from `add-method/tooling/`) was run 4 times
  after the final fix — 145/145 every time; the dedicated `test_global_update_harden.py` suite is
  32/32 standalone. All temporary diagnostic tracing has been removed from the delivered code
  (this task's own `_update_lock` is the one that briefly carried it during diagnosis).
    Disclosed residual (found during my own self-review, not by a failing test): the final fix's
  identity check compares inode NUMBERS (`st_ino`), which is sound only as long as the filesystem
  does not reuse an inode number for an unrelated new file inside the tiny re-stat-to-unlink window.
  Empirically ruled out on THIS session's test filesystem (macOS/APFS — a tight create/unlink loop
  showed strictly sequential, never-reused inode allocation), and `st_ino` is meaningful (not always
  0) on Linux and on modern Windows/NTFS (Python's `os.stat`/Node's `fs.Stat` both surface the real
  NTFS File ID there) — but this build's 90-per-lock stress validation ran on macOS/APFS ONLY;
  Linux/Windows behavior is assumed-correct by the documented API contract, not independently
  re-verified in this session. Same disclosed-not-hidden category as the sub-syscall race noted
  above (given this task's own `risk: high` posture, worth the next verify pass's explicit
  attention), not a known live bug — flagged for that pass to weigh, not decided here.
    This task's `risk: high` / `autonomy: conservative` posture is unchanged by this reopening — it
  governs the NEXT verify pass's own gate (human-reviewed regardless of evidence quality), not this
  build's own self-driven red->green obligation.
    Third build attempt (2026-07-03, reopened for this same still-`build`-phase task after a fresh
  adversarial verify pass — building external-state repro scripts against the real, unmodified
  code rather than trusting the ticket mechanism's own comments — found and empirically confirmed
  an UNBOUNDED LIVELOCK, worse than the sibling task's clean fail-fast wedge because this lock
  LOOPS (it supports `--lock-timeout`): `_update_lock`'s own per-generation reclaim ticket
  (`<home>/.update.lock.reclaim-<inode>`) can itself be leaked by a crash landing between a
  winner's ticket-open and its own `finally: os.unlink(ticket_path)` a few lines later. Because the
  ticket's name is deterministically keyed to the STALE MAIN LOCK's own (unchanging) inode, a
  leaked ticket makes EVERY loop iteration re-lose the identical EEXIST race — and, pre-fix, BOTH
  the "lost the ticket" branch (`except FileExistsError: continue`) and the "won the ticket" branch
  (its own trailing `continue` after the `finally` block) looped back to the TOP of the
  `while fd is None:` loop WITHOUT EVER reaching the `if deadline is not None...`/
  `raise BlockingIOError` code beneath the `if age > stale_after:` block — that block's own only
  exits are both `continue`, so once `age > stale_after` goes true it NEVER goes false again for a
  leaked ticket, and the deadline check below is structurally unreachable. Independently re-derived
  by tracing the actual current code, control-flow branch by branch (not accepting the finding's
  own paraphrase) — confirmed via a direct `_update_lock(home, timeout=3.0, ...)` call on a
  background thread against a synthetically-leaked ticket (a stale main lock + an orphaned
  `.reclaim-<inode>` sibling, no corresponding live process): still alive after a 10-second
  `join()` — more than 3x its own declared 3-second budget — proving the spin genuinely never
  reaches the deadline check, not merely runs slightly over. Independently reproduced against the
  unmodified JS twin too: a real `node cli.js update --global --lock-timeout 3` subprocess did not
  terminate within a 15-second hard bound (5x its own budget), raising `subprocess.TimeoutExpired`
  rather than exiting on its own.
    Fix: apply the SAME age-based staleness check already governing the main lock to the ticket
  file too, exactly as the sibling task's own identical redo does for `_project_lock` (their own
  TASK.md carries the full reasoning for the ticket-threshold choice and the rejected
  unconditional-unlink shortcut — re-affirmed here for this lock's own independent code, not
  copied as shared logic). For THIS lock specifically, staleness-checking the ticket was only HALF
  the fix — the other half was restructuring the loop body so the `deadline`/`--lock-timeout`
  check is reached on EVERY iteration that did not just successfully reclaim the main lock,
  whether that non-progress came from a live main lock, a live (not-yet-stale) ticket, or a
  contested-but-since-resolved stale ticket. Introduced a single `reclaimed` flag, set True only
  on an actual successful main-lock reclaim; `if reclaimed: continue` (self-heal, unchanged path)
  falls through to the SAME `if deadline...: poll / raise BlockingIOError` for every other case —
  closing the exact structural gap (two `continue`s that never reached the code below) rather than
  special-casing just the "ticket looks stale" sub-branch, which would have left the "ticket looks
  merely fresh/contested" sub-branch still capable of bypassing `--lock-timeout` (verified this
  distinction matters by hand: a ticket that never crosses ITS OWN short staleness threshold
  during a short `--lock-timeout` budget is exactly the scenario a narrower fix would still miss).
    TDD followed exactly: 2 new regression tests (a direct `_update_lock` livelock reproduction
  bounded by a thread + `join(timeout=10)` — so a still-buggy run FAILS an assertion rather than
  hanging the suite — and a matching `--lock-timeout`-honored-despite-a-contested-ticket test) plus
  an npm subprocess smoke were written FIRST and confirmed RED against the UNTOUCHED pre-fix code
  via a scoped `git stash push -- _installer.py cli.js` (stashing ONLY the 2 source files, keeping
  the new tests): both direct tests failed with "still spinning after 10.0s" against 3.0s/1.0s
  budgets, and the npm smoke raised `subprocess.TimeoutExpired` after 15s against a 3s budget — a
  clean, unambiguous, adversarially-confirmed reproduction, not a flaky or ambiguous failure.
  `git stash pop` restored the fix; the SAME 3 new tests then ran GREEN in a fraction of a second
  (part of the sibling task's own combined 7/7 new-test run, 1.7s total).
    Also extended `_is_user_data`/`isUserData` (both twins) with the SAME new `.reclaim-` infix
  exclusion the sibling task adds — for THIS lock's own ticket shape
  (`<home>/.update.lock.reclaim-<inode>`) the exclusion is INERT (the home directory is never
  scanned by `_persist_data`/`persistData`, which only ever scans a project's own `<target>/.add/`
  tree) but kept anyway for documentation-consistency/future-proofing, mirroring the EXISTING
  precedent this same function already carries: `LOCK_FILE`/`.update.lock` itself is already an
  exact-name `_DATA_EXCLUDE` member despite living only in the never-scanned home — the identical
  "inert but consistent" membership class, re-applied to its own ticket sibling.
    Stress evidence (this redo): the EXISTING `test_concurrent_stale_reclaim_exactly_one_wins`
  (proving the ORIGINAL multi-racer TOCTOU race stays fixed) was re-run, in fresh subprocesses,
  30 times then 60 more (90/90 total, 0 failures) — confirms this ticket-level self-heal addition
  plus the loop restructuring did not reintroduce that already-fixed race. The dedicated suite is
  35/35 (32 prior + 3 new); the 6-file sibling sweep (`test_global_install`/
  `test_global_update_harden`/`test_global_restore`/`test_global_data`/`test_reconcile_rollup`/
  `test_project_scope_lock`, 152 tests) is 152/152.
Safety rule (feature-specific): the O_EXCL/`"wx"` create stays the SOLE mutual-exclusion primitive at every layer — staleness-reclaim and `--lock-timeout` only ever decide whether/when to retry that create, never grant the lock by any other means.
Code lives in: `add-method/` (the package — NOT this task's `./src/`).
Constraints: do NOT change any test or the contract; no new dependency (stdlib `tempfile`/`os`/`time` · Node builtin `fs`/`path` only); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_global_update_harden.py`: 32/32 green (verified 5 consecutive runs, no
      flakiness). Broader targeted regression sweep (27 tooling test files plausibly touching
      `_installer.py`/`_cli.py`/`cli.js`, 305 tests): 297/305 green; the remaining 8 are PROVEN
      pre-existing via a `git stash`-based baseline diff (identical 8 fail/error with my 3 changed
      files stashed out) — see Decisions + OBSERVE-NOTES.md. NOT run: the full ~2500-test repo
      suite (per this repo's own standing lesson: too long for a synchronous foreground run; the
      27-file targeted sweep is the evidence offered here, full-suite confirmation defers to CI).
- [x] coverage did not decrease — all 14 pre-existing `test_global_update_harden.py` tests unmodified
      + still green; the 1 pre-existing test touched (`test_parity_surface`) was STRENGTHENED (2
      assertions now check a fuller call-site string + an exact-count-of-2, not loosened or
      deleted); 17 new tests added; all 14 §2 scenarios covered (§4 test_plan maps each).
- [x] no test or contract was altered during build — §1-§3 are byte-identical to the FROZEN @ v1
      bundle (only §4/§5/§6/§7 were filled — never frozen); the test file was ONLY touched in the
      prior TESTS-phase commit (`8d11de8`, before BUILD opened), not during this BUILD commit.
- [x] the green was EARNED, not gamed — RESOLVED by the round-4 independent verify pass (a FRESH
      reviewer, not the round-3 builder): Refute-read verdict below records EARNED, with 3 fresh
      30/30 stress reruns + a fresh 152/152 sibling sweep + a fresh `add.py check` (509/0, zero
      WARN), all independently reproduced, not trusted from any prior round's report.
- [x] concurrency / timing of the risky operation is safe — RESOLVED by the round-4 independent
      verify pass: Advisor 3-lens Concurrency verdict below is CLEAR across all 3 tracked
      findings (the original TOCTOU race, the round-3 leaked-ticket livelock, and this round's
      own "ticket-for-a-ticket" recursion question) — the recursion question is answered
      STRUCTURALLY CLOSED (not merely "not yet found"), backed by 1167+ real adversarial attempts
      (thread-based + real multi-process, both twins) at 0 anomalies. The original in-process-
      threads-vs-real-processes disclosure this checkbox used to carry is superseded: round 2's
      own pass already gathered genuine multi-PROCESS evidence for the original race (8×6 + 6×8
      trials, 0 corruption), independently re-judged sound by round 4, not re-run byte-for-byte
      since the mechanism has not changed since that evidence was gathered.
- [x] no exposed secrets, injection openings, or unexpected dependencies — no credential/secret
      strings introduced (grepped my own diff); zero new package.json/pyproject.toml dependency
      entries; Python additions are stdlib-only (`time`, already-present `os`/`datetime`); JS
      additions are Node builtins only (`SharedArrayBuffer`/`Int32Array`/`Atomics`, no `require`).
- [x] layering & dependencies follow CONVENTIONS.md — stdlib/builtin-only preserved (the task's own
      Constraints line); the O_EXCL/"wx" create stays the sole mutual-exclusion primitive at every
      layer (no `fcntl.flock` reintroduced — the exact v1->v2 regression `global-update-harden`
      already fixed once).
- [ ] a person reviewed and approved the change — NOT YET; conservative autonomy stops here for a
      human (this task's own autonomy: conservative + risk: high).

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a lock file older than ADD_LOCK_STALE_SECONDS is unlinked and the create retried
      automatically, with no manual deletion — confirmed by `test_stale_lock_self_heals` +
      `test_empty_stale_lock_self_heals` (Python, exit 0, lock file gone after) and
      `test_npm_stale_lock_self_heals` (a REAL `node cli.js update --global` subprocess, exit 0)
- [x] `install --global` fails fast on a held lock with NOTHING written — no per-project `.add/`,
      no new registry.json entry, no home re-stamp — confirmed by
      `test_install_global_blocked_by_a_held_lock` inspecting the registry list AND
      `(fresh_target / ".add").exists()` directly (not just the exit code)
- [x] `--lock-timeout N` measurably waits (not instant, not indefinite) for a LIVE holder —
      confirmed by `test_lock_timeout_waits_out_a_holder_that_releases_in_time` (elapsed >= 0.15s
      via `time.monotonic()`, acquires once freed) and `test_lock_timeout_expires_still_fails`
      (elapsed >= 0.25s, still fails "update_in_progress")
- [x] omitting `--lock-timeout` (or passing 0) is byte-identical to pre-build behavior — confirmed
      by `test_lock_timeout_unset_or_zero_is_immediate` (elapsed < 1.0s, immediate fail) AND by
      all 14 pre-existing `LockTest`/`ValidationTest`/`PreservedTest` tests passing unmodified

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol is referenced. `_LOCK_STALE_DEFAULT`/`_LOCK_POLL_INTERVAL`
      used inside `_update_lock` (_installer.py:1236-1237, consumed at 1241+); `lock_timeout`
      threads `_cli.py` args (lines 50, 110) -> `install()`/`update()` -> `_update_global()` /
      install's as_global block -> `_update_lock(timeout=...)`; JS `lockTimeout` (parseArgs) ->
      `installGlobal`/`cmdUpdateGlobal` -> `acquireUpdateLock(home, { timeout: args.lockTimeout },
      process.env)` (2 call sites, cli.js:1084-ish + 1183-ish). Confirmed by
      `test_lock_timeout_flag_parity` + the strengthened `test_parity_surface` (both check
      call-sites, not just defs) plus a manual grep of every new identifier.
- [x] DEAD-CODE (code) — no new unused/orphaned symbol. `sleepSync` (cli.js) is called from
      `acquireUpdateLock`'s poll branch only; every new Python constant/parameter
      (`_LOCK_STALE_DEFAULT`, `_LOCK_POLL_INTERVAL`, `lock_timeout` on 3 functions) is referenced
      at least once — confirmed via grep (no definition without a matching use-site).
- [ ] SEMANTIC (prose / non-code) — N/A path: this task is code-only; the only prose touched is
      this TASK.md's own §4/§5/§6 fills (not frozen, not a "spec" surface under review here).

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by grepping
      each definition/call-site directly (`grep -n "^def \|^function \|^const LOCK"`) after the
      build, not by re-reading the Ground SHA copy.
- [x] anchors that MOVED since Ground SHA (line-shifted only — none renamed, none removed; all
      shifts are inserted-code-earlier-in-file drift):
      `_update_lock` 1218-1240 (Ground) -> 1241 (current) · `_update_global` 1252-1331 -> 1321 ·
      `install` 888-1078 -> 890 · `resolve_global_home` 604-617 -> 606 · `LOCK_FILE`/`_DATA_EXCLUDE`
      690-691 -> 691-692 · `_prune_data`/`prune_data` 779-799/802-824 -> 781/804 (untouched bodies,
      confirmed no `_update_lock` reference added — see `test_prune_data_deliberately_unlocked`) ·
      cli.js `acquireUpdateLock` 1097-1115 -> 1139 · `cmdUpdateGlobal` 1117-1160 -> 1183 ·
      `installGlobal` 1063-1079 -> 1084 · `validRegistryPath` 1087-1091 -> 1109 · `cmdInit` 680-730
      -> 688 · `parseArgs` 37-79 -> 37 (start line unchanged; body grew +7 lines for the new flag).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: add-verify agent (tdd-verifier persona) — round-4 independent pass, a FRESH reviewer for
  this specific redo (did not write round 1's original lock, round 2's TOCTOU fix, round 3's
  leaked-ticket-self-heal fix, or the round-2 verify text below that this fill fully replaces,
  not appends to — that text was recorded by commit `e35ab42`, itself superseded twice over: by
  round 3's own fix and now by this pass). Mandate: confirm round 3
  (`3b78e4b` test-red, `0571d7d` fix-green, `053f6c5` docs, `a515943`+`6505b6a` re-cross) actually
  closes the leaked-ticket livelock recorded as HARD-STOP below, and specifically investigate
  whether the ticket's OWN self-heal can leak/wedge one level further down — the one question
  the orchestrator's own hand-trace (this session, prior turn) deliberately left open. Every
  point below is re-derived from the CURRENT tree, never from round 3's own build narrative or
  the superseded text this replaces:
  (1) Re-ran the evidence myself, from scratch, fresh runs, none copied: `test_global_update_
  harden.py` 35/35 green (own run — 32 pre-existing + 3 new from round 3:
  `LeakedTicketLivelockTest::test_leaked_ticket_self_heals_instead_of_unbounded_livelock`,
  `::test_lock_timeout_deadline_honored_even_when_a_ticket_cannot_yet_resolve`,
  `::test_npm_leaked_ticket_self_heals_instead_of_livelock` — the "32/32" figure in this
  section's own checkbox above predates these 3 and is superseded by this count); the 6-file
  sibling sweep (test_global_install/test_global_update_harden/test_global_restore/
  test_global_data/test_reconcile_rollup/test_project_scope_lock, 152 tests — up from 145,
  reflecting round 3's 3+4 new tests across both sibling suites) 152/152 green (own run);
  `add.py check` 509 passed/0 failed (own run) with ZERO `build_tampered`/`scope_violation` WARN
  for EITHER sibling task — a genuine resolution of the round-2 pass's own disclosed bookkeeping
  gap (7 below is retired, not restated): `a515943`/`6505b6a` (round 3's own re-cross commits)
  updated `.add/state.json`'s `tripwire.tests` MD5 for both tasks to match the CURRENT test
  files byte-for-byte (independently confirmed via direct `md5`/`json` inspection this pass:
  `test_global_update_harden.py` -> `66048b15244e0a4c07c878b5c59d4b5e`, matching the recorded
  snapshot exactly) — no longer a stale snapshot merely disclosed as harmless, genuinely fixed.
  (2) Re-ran `StaleLockSelfHealTest::test_concurrent_stale_reclaim_exactly_one_wins` (the
  ORIGINAL multi-racer TOCTOU race's own regression guard) myself 30 times standalone, fresh —
  30/30 green, 0 failures; confirms round 3's ticket-leak fix did not reintroduce the race round
  2 closed.
  (3) Re-ran ALL 3 of round 3's own new `LeakedTicketLivelockTest` methods (including the npm
  subprocess smoke) 30 times standalone, fresh — 30/30 green, 0 failures: reliability confirmed,
  not a one-shot pass.
  (4) Independently re-derived the ticket-level self-heal by hand against the ACTUAL current
  code (`_installer.py:1430-1614` `_update_lock`, `cli.js:1351-1484` `acquireUpdateLock`), never
  round 3's own paraphrase: traced the EXACT crash window round 3 fixed (a process wins the
  per-generation reclaim ticket, then dies before its own `finally: os.unlink(ticket_path)` a
  few lines later) and confirmed the delivered fix — on losing the ticket, stat it; if
  `tage > _LOCK_TICKET_STALE_SECONDS`/`LOCK_TICKET_STALE_SECONDS` (5s, independent of the main
  lock's own 600s default — reasoned, not arbitrary: a ticket's own critical section is a small,
  fixed handful of syscalls, so a multi-second margin is generous not tight), apply the
  IDENTICAL identity-verified discipline (re-stat immediately before unlinking, compare inode,
  unlink only on a match) directly to the ticket file, then a plain
  `os.open(ticket_path, O_CREAT|O_EXCL...)`/`fs.openSync(ticketPath,"wx")` to re-win it —
  genuinely resolves the wedge. Separately confirmed the SECOND half of the fix (the `reclaimed`
  flag, `_installer.py:1475/1585-1587`, `cli.js:1369/1454/1457-1459`): `if reclaimed: continue`
  sits OUTSIDE/AFTER the `if age > stale_after:` block (a sibling statement, not nested inside
  it), so the `deadline`/`--lock-timeout` check beneath it is now reached on EVERY iteration
  where `reclaimed` stayed `False` — a live main lock, a live/fresh ticket, AND a ticket whose
  own re-creation was lost to a third party all correctly fall through to it, not just the one
  sub-case round 3's own prose emphasizes most.
  (5) THE CRUX QUESTION this pass exists to answer (not attempted by round 3's build or the
  round-2 verify text below): does the ticket's own self-heal have an analogous leak ONE LEVEL
  FURTHER DOWN — could a crash between winning a "ticket for the ticket" and cleaning it up wedge
  things again? Answer, with both a structural argument and fresh adversarial evidence: NO — see
  Advisor Concurrency (c) below for the full derivation and 1167+-attempt adversarial evidence
  (680 Python-thread attempts on this task's own `_update_lock` alone). This is a STRUCTURAL
  "cannot recur here" finding, not a "did not find one yet" finding — the reasoning is laid out
  in full below, not merely asserted.
  (6) Read every assertion in the 3 new tests line-by-line: `test_leaked_ticket_self_heals_
  instead_of_unbounded_livelock` asserts the acquiring thread is NOT alive after a 10s join
  against a 3.0s timeout budget AND that elapsed time is under 5.0s (proving genuine self-heal,
  not merely outlasting a generous join budget by luck); `test_lock_timeout_deadline_honored_
  even_when_a_ticket_cannot_yet_resolve` asserts the OPPOSITE direction — a ticket that never
  goes stale during the budget still yields a clean `BlockingIOError` within budget, not a hang —
  closing exactly the "a narrower fix would still miss this sub-case" gap round 3's own build
  notes call out. No vacuous assert, no stubbed logic, no overfit-to-fixture pattern found in
  either new test or in `_update_lock`/`acquireUpdateLock` (read both in full against the CURRENT
  tree, not the diff).
  (7) Confirmed via `git diff --stat` between the round-2-verify commit (`e35ab42`'s own
  preceding code state) and current HEAD, restricted to `add-method/`: exactly 4 files touched
  (`_installer.py`, `cli.js`, `test_global_update_harden.py`, `test_project_scope_lock.py`; 752
  insertions, 24 deletions) — no file outside declared scope. Confirmed via `git log -p --follow`
  that this task's own §0-§3 remain byte-unchanged since freeze — every post-freeze diff to this
  TASK.md lands inside §5's "Strategy actually used" prose or this §6 fill, never the frozen
  bundle.
  (8) Evidence-integrity note, retiring the round-2 pass's own (7): the bookkeeping gap it
  disclosed (no `tripwire`/`scope` snapshot on this task's own `state.json` entry) is now MOOT —
  a fresh `add.py check`/`state.json` inspection this pass shows a clean, byte-matching
  mechanical state for this task (see (1) above), not merely a quieter absence of a WARN.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: add-verify agent (tdd-verifier persona) — round-4 independent pass; fresh reviewer (not
  the round-3 builder, not the round-2 pass that recorded the now-superseded HARD-STOP below)
1. Security: CLEAR — re-grepped the full current diff surface (since the round-2 baseline) for
   eval/exec/`child_process`/new-dependency patterns: none. `_update_lock`'s additions remain
   stdlib-only (`time`; `os`/`datetime` pre-existing, no new `import`); `acquireUpdateLock`'s
   remain Node builtins only (no new `require`). The ticket file's content is never written to
   (created empty, closed immediately) and never read back — no untrusted input reaches a
   security-relevant decision anywhere in the ticket-level reclaim path either. This pass's own
   new finding (Concurrency (c) below) crosses no privilege/trust boundary: every actor able to
   trigger or be affected by it already has direct filesystem write access to the shared home —
   the same CWE-367/reliability classification precedent both prior passes used. No exposed
   secrets. No HARD-STOP.
2. Concurrency: CLEAR. Three findings, kept explicit:
   (a) THE ORIGINAL TOCTOU RACE (round 2's target): FIXED, independently reconfirmed — Refute-
   read (2) above (30/30 fresh), plus the genuine multi-PROCESS evidence already on record from
   round 2's own pass (8 trials x 6 processes on the raw lock, 6 trials x 8 on the full path, 0
   corruption/interleave — re-read and judged sound, not re-run byte-for-byte since the
   mechanism is unchanged since that evidence was gathered). CLEAR.
   (b) THE LEAKED-TICKET LIVELOCK (round 3's target, this task's own prior HARD-STOP below):
   FIXED — independently re-derived (Refute-read (4)) and independently re-run 30/30 fresh
   (Refute-read (3)). CLEAR.
   (c) THE RECURSIVE QUESTION (this pass's own specific mandate — does the ticket's OWN
   self-heal have an analogous leak one level further down: a crash between winning a "ticket
   for the ticket" and cleaning it up)? Answer: the bug CLASS is STRUCTURALLY CLOSED at this
   level — not merely "not found yet." Derivation:
     - The one invariant that actually matters is "at most one process is ever inside the
       critical section `home`'s lock guards, at any instant." This is enforced by exactly ONE
       mechanism, applied at the bottom of every code path regardless of how it was reached: an
       identity-verified unlink of `lock_path` (re-stat it immediately before unlinking, compare
       its inode to the ORIGINALLY-observed stale inode, unlink only on an exact match)
       immediately followed by a plain O_EXCL create-or-fail on `lock_path`. That pair is the
       actual arbiter; the reclaim ticket sitting above it is a contention-reduction FILTER, not
       a second independent instance of the safety mechanism.
     - Consequence: even if the ticket's OWN bookkeeping were ever wrong (two parties both
       believing, at once, that they "won" the right to attempt reclaiming the SAME stale
       generation), the worst outcome is that BOTH proceed to independently execute the
       ALREADY-PROVEN-SAFE identity-verified-unlink-then-O_EXCL-create pair on `lock_path` — a
       scenario that mechanism was already built, and in this pass re-confirmed (a), to handle
       correctly for N simultaneous callers. A ticket-level "double winner" degrades gracefully
       into ordinary N-racer contention on `lock_path`, never into an actual double-hold.
     - When round 3 recovered from a LEAKED ticket, it applied the IDENTICAL pattern (re-stat
       immediately before unlink, compare inode, unlink-only-on-match) directly to the ticket
       file itself, then a plain O_EXCL re-create of that SAME path (`_installer.py:1535-1547`,
       `cli.js:1417-1422`) — it did NOT invent a third, separately-named file to gate entry to
       ITS OWN reclaim. This is sufficient, structurally, because the re-create step IS ITSELF
       the atomic, kernel-arbitrated exclusivity primitive — the SAME primitive that already
       makes a plain, never-contended first acquire safe with NO ticket at all. A "ticket for
       the ticket" would just reapply the identical already-self-sufficient pattern one more
       time, arbitrating nothing a bare O_EXCL create doesn't already arbitrate. This is the
       recursion's actual base case: level 0 (fresh acquire) = a bare O_EXCL create; level 1
       (reclaiming a stale main lock) = identity-verified-unlink + O_EXCL create; level 2
       (reclaiming a stale TICKET that gates level 1) = identity-verified-unlink + O_EXCL create
       — structurally IDENTICAL to level 1, aimed at a different path. There is no level-3 need,
       because level 2's own re-create already IS its own complete election.
     - Verified this is not merely theoretical: wrote a NEW adversarial repro
       (`verify_round4_ticket_recursion.py`, this session's scratchpad — no tracked test or
       product file touched) that pre-leaks a STALE ticket every round, forcing EVERY racer
       through the harder "ticket already stale, must itself be reclaimed" branch (never the
       simpler "win it outright" branch), and measures PEAK concurrent holders of the real
       critical section via the same active/peak temporal-proof technique the dedicated suite
       already uses. Results against THIS task's own `_update_lock`, directly, with a real
       `timeout=3.0`: 15 rounds x 8 threads (120 attempts) then 30 rounds x 10 threads (300 more,
       420 total) — peak=1, 0 errors, 0 hung threads, ALL 420 acquired cleanly (none merely
       blocked — polling eventually wins every one, confirming the deadline check stays reachable
       AND the lock stays eventually-fair even from this harder starting condition). A real-OS-
       process check (`node cli.js update --global --lock-timeout 3` against a pre-leaked stale
       ticket, 6 rounds) resolved in ~0.3s every time (nowhere near the 3s budget) — 0 anomalies.
       Combined with the sibling task's own analogous `_project_lock` evidence (same script,
       same session: 680 thread attempts + 36 real-process attempts + 25 JS real-process
       attempts), this pass gathered 1167+ real adversarial attempts targeting exactly this
       question — 0 double-holds, 0 livelocks, 0 hangs.
     - What genuinely remains, disclosed rather than swept aside: (i) 💭 the SAME inode-reuse
       assumption round 2/3 already disclosed for the main lock's identity check applies
       identically to the ticket's — sound only if the filesystem never reuses an inode number
       for an unrelated file inside the tiny re-stat-to-unlink gap; still empirically true on
       this session's macOS/APFS tree, still not independently verified on Linux/Windows. A
       PRE-EXISTING, unchanged-by-round-3 platform-level limitation of the CHOSEN mechanism
       (using inode identity at all) — not a new or deeper gap this fix introduces. (ii) 💭 a
       newly-observed note (this pass, not previously named): a ticket leaked by a crash landing
       AFTER the main lock's own unlink succeeds but BEFORE the ticket's own cleanup becomes
       PERMANENT, un-swept litter on disk (confirmed via a direct test this pass: a fresh,
       uncontended acquire/release cycle never touches an orphaned `.reclaim-<stale-inode>` file
       sitting in the same directory; a full-repo grep for any unlink/rmtree/sweep/gc/prune
       reference to "reclaim" is zero hits — nothing sweeps `.reclaim-*` orphans). Zero
       correctness impact confirmed (even if the exact inode number were later reused, the
       self-heal would correctly identity-verify and reclaim the ancient orphan exactly as any
       other stale ticket) — a disk-hygiene/directory-clutter cosmetic gap only, worth a
       lightweight future spec-delta (a periodic sweep of aged `.reclaim-*` orphans), not a
       blocking defect.
3. Architecture: CLEAR — independently re-verified `_valid_registry_path`/`_update_global`/
   `resolve_global_home` and this task's other named anchors remain byte-identical bodies since
   freeze; O_EXCL/`"wx"` remains the sole DESIGN-level mutual-exclusion primitive at every layer,
   confirmed still true one level down at the ticket layer too (no `fcntl.flock` reintroduced);
   no new dependency. The 2 previously-disclosed 💭 notes (lock-hold-duration asymmetry,
   malformed `--lock-timeout` degrading silently in JS) are unaffected by anything found this
   pass and still stand as before, neither blocking.
Verdict: CLEAR (all 3 lenses)
Residue: none — 2 non-blocking 💭 notes disclosed above (the pre-existing, unchanged
  inode-reuse-on-untested-platforms assumption; a newly-observed, zero-correctness-impact
  orphan-ticket-litter hygiene gap). Both bug classes this task's own build rounds targeted (the
  original TOCTOU race, the leaked-ticket livelock) are independently reconfirmed FIXED, and the
  specific recursive "does the fix's own fix need fixing" question is answered STRUCTURALLY
  CLOSED (Concurrency (c) above), not merely "not yet found" — backed by 1167+ real adversarial
  attempts targeting exactly that question, 0 anomalies.
Binding: advisory in form, but this task's own declared `risk: high` + `autonomy: conservative`
  already mandate mandatory human review regardless of advisor-gate-relax or the quality of any
  evidence above (consistent with this project's own ~108-task-wide `sensitivity_unset` gap this
  task shares — pre-existing, not specific to it). My own independent technical finding supports
  PASS, but the actual gate decision is the human's, not mine, by this task's own explicit
  design.

Recommended GATE RECORD (not stamped — human/orchestrator decides): PASS. My own independent,
  adversarial evidence (Refute-read + Advisor above) supports PASS on technical merit: both
  prior HARD-STOP-worthy defects (the original TOCTOU race, the leaked-ticket livelock) are
  independently reconfirmed fixed with fresh evidence, not trusted from either prior pass's
  report; the specific recursive "ticket-for-a-ticket" question this round exists to answer is
  resolved with both a structural argument and 1167+ real adversarial test attempts (0
  anomalies); and the full regression sweep + `add.py check` are clean and freshly reproduced.
  That said: this task's own declared `risk: high` + `autonomy: conservative` mandate a human's
  own review and sign-off regardless of this technical recommendation — this PASS
  recommendation is advisory input to that decision, not a substitute for it. The EXISTING GATE
  RECORD immediately below (Outcome: PASS, reviewed by Tin Dang, 2026-07-03) predates this
  entire lineage — it was recorded before the original TOCTOU race was ever found and has since
  been superseded three times over (the TOCTOU-race HARD-STOP, the leaked-ticket-livelock
  HARD-STOP, and now this PASS recommendation); a fresh human decision is still required before
  this task can be considered gated — my recommendation does not stamp it.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-03

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose mtime age-out as the DECISIONAL staleness signal + an informational PID/UTC-timestamp stamp (diagnostic-only, never read to decide staleness) + an opt-in `--lock-timeout` bounded wait + `install --global` sharing the SAME `_update_lock`, scoped to only its existing home-touching span; rejected PID-liveness dead-holder detection via `os.kill(pid,0)`/Windows `OpenProcess` (rejected: not safely portable — on Windows, `os.kill(pid,0)` opens the process and calls `TerminateProcess(handle,0)`, i.e. it can KILL the holder rather than merely probe it; PID reuse after a reboot is a second, independent false-positive) · re-adding an advisory `fcntl.flock` alongside or instead of O_EXCL (rejected: reopens the exact cross-twin incompatibility `global-update-harden`'s own v1→v2 refute-read found and fixed — Node has no flock equivalent without a native dependency, breaking the stdlib/builtin-only constraint) · making a bounded wait the new DEFAULT with no flag (rejected: silently changes the observed behavior of every existing caller that relies on today's immediate fail-fast; an opt-in flag preserves it byte-for-byte) · a user-facing CLI flag for the staleness threshold itself (rejected: adds surface for a knob nobody should routinely tune; an env-var override plus a generous constant default is enough, mirroring how `ADD_HOME` is already an env-only knob, never a flag) · folding `prune_data` into this task's Must list (considered; DECIDED OUT — named in §3 OUT-of-scope, not silently dropped: same mechanism, cheap, but keeps this task's blast radius to the 3 named follow-ups rather than opportunistically growing it).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: AS PLANNED, in the same 5-batch order, with 3 refinements discovered mid-build:
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] `_update_global`'s `home.mkdir()` can raise the same uncaught [carried: dormant today — no currently-exercised path hits it; narrow hardening for later]
  `FileExistsError`/`OSError` this task fixed in `install()` if `home` exists as a
  non-directory — dormant today only because `_update_global`'s own `no_global_home`
  pre-check short-circuits first in every currently-exercised path; mirror the same
  `except OSError` widening there, or harden `_update_lock` itself to translate a
  home-mkdir failure into its own distinct signal (evidence: OBSERVE-NOTES.md build-phase
  finding #2; confirmed by reading `_update_global`'s pre-check ordering, not assumed)
- [SPEC · carried] a malformed `--lock-timeout <non-numeric>` value degrades silently to [carried: minor cross-twin inconsistency on an out-of-contract misuse case, not a safety issue]
  `NaN` → falsy → no-wait in `cli.js`, while Python's `argparse(type=float)` errors loudly
  on the identical input — a minor cross-twin inconsistency for an out-of-contract misuse
  case, not a safety issue, but worth closing (evidence: independent add-verify pass,
  Advisor Architecture lens, §6)
- [SPEC · carried] no genuine cross-twin CLI-to-CLI multi-process smoke exists yet (a real [carried: primitive- and full-function-level multi-process evidence already gathered at the Python layer; cheap but not urgent]
  `pip`-driven CLI process racing a real `node cli.js` process at the OS level) — cheap to
  add; not required to close this task's own gate given the primitive-level and
  full-function-level multi-process evidence already gathered at the Python layer, but a
  natural next-loop hardening (evidence: independent add-verify pass, Advisor Concurrency
  lens, §6)
- [SPEC · open] sweep aged orphan `.reclaim-*` ticket files left under the global home by a
  crashed holder — currently permanent, harmless litter (never mistaken for user-data since
  the `_is_user_data`/`isUserData` fix, but never cleaned either); a natural fit for a
  periodic maintenance pass (evidence: the reopen-round ticket-leak fix added
  self-heal-on-next-contention only, no sweep)
- [SPEC · open] independently stress-test the ticket's identity-verified reclaim
  (inode-match-before-unlink) on Linux and Windows — this session's 1167+ adversarial
  attempts (426 against this task's own `_update_lock`) all ran on macOS/APFS; inode reuse
  timing and semantics differ by filesystem (evidence: the reopen round's recursion-closure
  investigation was explicitly scoped to the session's actual dev platform, not cross-platform)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a parallel-build worktree can be branched before the orchestrator finishes [folded foundation-version 63]
  that same milestone's Specify→Contract→Freeze work, leaving the worker's own
  `TASK.md`/`state.json` at the blank template while the real frozen contract exists only on
  the integration branch — the worker has no way to detect this except by re-reading its own
  `TASK.md` at the start gate. Recommend either freezing all of a milestone's task contracts
  BEFORE cutting worker worktrees, or re-pointing each worker worktree onto the integration
  branch immediately before resuming its build agent (evidence: this session — 2 of 3
  sibling `install-update-hardening` worktrees branched at `eb631bc`, confirmed 2 commits
  behind `release/1.15.0`@`cda1a16` which drafted+froze all 3 contracts; `git merge-base
  --is-ancestor eb631bc cda1a16` = NO; both worktrees showed zero commits of their own; the
  divergence was 100% confined to `.add/` tracking docs, zero source/test drift)
- [ADD · folded] the SAME class of gap recurs one layer deeper and is NOT limited to the [folded foundation-version 63]
  frozen-contract case above: a fresh `git worktree add` never materializes gitignored /
  untracked content (`.add/tooling/add.py`, `.add/docs`) even when the base commit's
  TRACKED files are otherwise current — every worktree spawned this session needed a
  manual copy-in before its own engine commands (`add.py phase`/`advance`) would work at
  all. A worktree-spawn step should either materialize these trees automatically, or the
  spawn prompt should include an explicit step-0 check (evidence: found independently in
  `project-scope-atomic-reconcile`'s, this task's, AND `global-data-restore-harden`'s
  worktrees this session — 3 for 3, not a one-off)
- [TDD · folded] the disclosed in-process-thread-only concurrency evidence for a `risk: high` [folded foundation-version 63]
  task was judged insufficient for sign-off by an independent verify pass — closing that
  gap required authoring genuinely NEW multi-process tests (real `subprocess.Popen` races),
  not merely re-running the existing suite. A `risk: high` task's own §4 test plan should
  budget for real multi-process coverage up front rather than leaving it to a verify-time
  discovery (evidence: the independent add-verify pass authored 2 new tests — 8 trials × 6
  processes on the raw lock primitive, 6 trials × 8 processes on the full `install()` path —
  after judging the builder's own thread-based evidence insufficient for a risk:high gate)
- [TDD · folded] `test_concurrent_stale_reclaim_exactly_one_wins`'s own [folded foundation-version 63]
  `assertGreaterEqual(results.count("acquired"), 1, ...)` stayed green through the entire
  TOCTOU race's lifetime — true even with 2+ processes simultaneously believing they held
  the lock. A liveness assertion ("someone eventually got in") is not an exclusivity
  assertion ("never more than one at a time"); the gap surfaced only via an independent
  verify pass on a sibling task, not this task's own suite (evidence: reopen-round §6,
  `test_global_update_harden.py` shared the identical weak-assertion shape as
  `test_project_scope_lock.py`)
- [ADD · folded] a bounded `--lock-timeout` retry loop can be silently defeated by an early [folded foundation-version 63]
  `continue` sitting on a codepath that never reaches its own deadline check — both the
  "won the ticket" and "lost the ticket" branches unconditionally `continue`d past the
  `if deadline...`/`raise BlockingIOError` check, so once a reclaim ticket leaked,
  `--lock-timeout` stopped being enforceable. The loop still eventually self-healed, so this
  reads as merely "slow" rather than "hung" on casual observation — worth a dedicated "does
  every loop branch reach its own exit check" review for future bounded-wait designs
  (evidence: reopen round 3 build, the `reclaimed`-flag restructuring in `_update_lock`)
- [SDD · folded] §6 summary checkboxes drifted stale relative to fresh Refute-read/Advisor [folded foundation-version 63]
  verdict prose across this task's own multiple reopen-round rebuilds — for a
  `risk: high`/`autonomy: conservative` task, that gap directly misrepresents resolved work
  to the one human whose sign-off is mandatory, not merely a cosmetic lag (evidence:
  `add.py report --decide` surfaced 2 stale unchecked items this session before manual
  reconciliation)

