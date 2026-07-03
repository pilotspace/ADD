# TASK: global-update-harden follow-ups: stale-lock recovery, install --global coverage, CI timeout mode

slug: global-lock-followups · created: 2026-07-02 · stage: mvp · risk: high
milestone: install-update-hardening
autonomy: conservative
phase: build

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
- [ ] the green was EARNED, not gamed — LEFT for independent verify (not self-graded; see the
      Refute-read verdict section below).
- [ ] concurrency / timing of the risky operation is safe — LEFT for independent verify by design
      (this task's own STOP-and-escalate criteria names concurrency/timing judgment as an
      escalation, not a self-certification). Evidence offered, not a verdict: a 6-thread
      Barrier-synced race directly exercises `_update_lock`'s stale-reclaim path (no unexpected
      exception, no leaked lock, >=1 acquire) — but this is IN-PROCESS multi-threaded concurrency
      against real OS syscalls (os.open/os.unlink), not a genuine multi-PROCESS race; the
      install-global "two concurrent runs" test is a SEQUENTIAL simulation (hold -> release ->
      second call), not simultaneous separate processes. Named as a disclosed test-design scope
      limit in OBSERVE-NOTES.md, not silently assumed equivalent.
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
By: add-verify agent (tdd-verifier persona) — principal concurrency/filesystem-reliability
  review; a FRESH reviewer for this redo (did not write the original code, the abandoned
  rename-to-quarantine attempt, or this ticket+identity-reverify fix) · NOTE: this task's own
  GATE RECORD below (Outcome: PASS, reviewed 2026-07-03) predates the redo entirely — it was
  recorded BEFORE the shared TOCTOU race was ever found and is SUPERSEDED by everything below;
  it should not be relied on. Adversarially checked, re-deriving from the current tree, never
  from any prior agent's own narrative:
  (1) Re-ran the evidence myself, from scratch: `test_global_update_harden.py` 32/32 green (own
  run); the 6-file broader sweep (test_global_install/test_global_update_harden/
  test_global_restore/test_global_data/test_reconcile_rollup/test_project_scope_lock, 145
  tests) 145/145 green (own run); `add.py check` 509 passed/0 failed (own run — NO
  `build_tampered`/`scope_violation` WARN was emitted for THIS task specifically; see the
  explicit caveat at the end of this verdict on why that absence is a bookkeeping gap, not a
  cleaner mechanical situation).
  (2) Re-ran `StaleLockSelfHealTest::test_concurrent_stale_reclaim_exactly_one_wins` myself 50
  times standalone (a fresh, independent 50 — not the builder's reported 90) — 50/50 green, 0
  failures.
  (3) Independently re-derived the ticket+identity-reverify algorithm by hand against the ACTUAL
  current code (`_installer.py:1417-1537` `_update_lock`, `cli.js:1329-1418`
  `acquireUpdateLock`) — the identical trace method as the sibling task's own Refute-read (N
  simultaneous racers on one stale generation -> one ticket winner -> every loser's `continue`
  never touches `lock_path` itself -> the winner's re-stat-before-unlink identity check -> a
  fresh interloper landing in the winner's own unlink-to-retry gap is benign nondeterminism, not
  a double-hold), independently corroborated by 90-190+ combined stress runs this session (my
  own 50 + the builder's 90) at 0 instances of a peak-concurrent-holder count above 1.
  (4) Read every changed assertion line-by-line: the identical `peak = max(peak, active)` /
  `self.assertLessEqual(peak, 1, ...)` (line 499) temporal proof as the sibling, closing the
  identical `results.count("acquired") >= 1` cumulative-assertion gap the reopening
  (`1e30cf8`) found at this exact file's line 480 pre-redo. No vacuous assert, no stubbed logic
  in `_update_lock`/`acquireUpdateLock` (read both in full against the current tree).
  (5) Confirmed via `git log -p --follow` on this TASK.md that §0-§3 (the frozen bundle) are
  byte-unchanged since this task's own freeze — every post-freeze diff lands inside §5's
  "Strategy actually used" prose only (hunks at lines ~378 and ~438, both well inside §5). The
  frozen contract was NOT edited during this redo.
  (6) Wrote 4 independent repro scripts (this session's scratchpad — no tracked test touched)
  attacking a DIFFERENT angle than either prior agent tried: does a crash landing INSIDE the NEW
  ticket-held window (between a ticket-winner's `os.open`/`fs.openSync` success and its own
  `finally` cleanup) leave anything behind that matters? Full finding under Advisor Concurrency
  below — it does NOT reveal the recorded green as gamed (the recorded suite proves what it
  claims, for the scenarios it actually runs); it reveals a scenario neither the builder's
  Strategy nor any prior verify pass ever attempted. A coverage gap, not a rigor gap in what is
  already green — EARNED stands for the recorded suite; the new finding is carried as
  Concurrency residue below, not as a refutation of this checklist.
  (7) Evidence-integrity disclosure, mirroring the sibling task's own (7), adapted: my own
  `add.py check` run emits NO `build_tampered`/`scope_violation` WARN for this task — but this
  task's `.add/state.json` entry carries NO `tripwire`/`scope` fields at all (confirmed by
  direct inspection: only `freeze`/`gate_actor`/`reopens` are present), unlike its sibling. The
  identical shared test-strengthening commit (`3e85619`) touched THIS task's own
  `test_global_update_harden.py` too (23 lines added, confirmed via `git show --stat`). The
  absence of a WARN here reflects an absent tracking structure for this task, not a cleaner
  mechanical state — the underlying situation (a tracked test legitimately strengthened after
  this task's own original build/freeze, without a phase re-cross since) is IDENTICAL to the
  sibling's. Disclosed so a human does not read "no WARN" as "nothing to reconcile" for this
  task either.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: add-verify agent (tdd-verifier persona) — independent adversarial pass; fresh reviewer
  (not the builder, not the earlier pass that recorded the now-superseded PASS below)
1. Security: CLEAR — re-grepped the full current diff surface for eval/exec/`child_process`/
   new-dependency patterns (none); Python additions remain stdlib-only (`time`; `os`/`datetime`
   already present — confirmed, no new `import` line); JS additions are Node builtins only
   (`Atomics`/`SharedArrayBuffer`/`Int32Array`, no new `require`). The diagnostic lock-stamp
   writes only `os.getpid()` + a UTC timestamp — no untrusted input reaches a security-relevant
   decision. The Windows `os.kill(pid,0)`-can-TERMINATE hazard remains correctly avoided by
   design (mtime-age, never PID-liveness). My own NEW finding below (a ticket-leak livelock)
   crosses no privilege/trust boundary: every actor able to trigger or be affected by it already
   has direct filesystem write access to the shared home — the same CWE-367/reliability
   classification precedent the sibling's own verify pass used for the original TOCTOU race
   applies identically here. No exposed secrets. No HARD-STOP.
2. Concurrency: RESIDUE — two findings, kept explicitly separate:
   (a) THE ORIGINAL RACE (multiple simultaneous racers on one stale generation): FIXED, and
   independently reconfirmed by me — see Refute-read (1)-(3) above, plus a fresh empirical
   re-verification (50/50, this pass), PLUS genuine multi-PROCESS evidence (this task's own
   frozen §6 already records 8 trials x 6 real `subprocess.Popen` processes racing the raw lock,
   and 6 trials x 8 real processes racing the full `install(as_global=True)` path, both 0
   corruption/interleave/duplicate/lost-write — re-read and independently judged sound, not
   re-run byte-for-byte this pass, since the mechanism is unchanged since that evidence was
   gathered and my own fresh 50/50 in-process run plus the ticket-algorithm re-derivation
   corroborate it). CLEAR.
   (b) THE SAME ticket-leak defect as the sibling task, independently confirmed in THIS task's
   own `_update_lock`/`acquireUpdateLock` (ticket created at `_installer.py:1476` /
   `cli.js:1361`; best-effort `finally` cleanup at `_installer.py:1512-1516` /
   `cli.js:1393-1395`) — but with a DIFFERENT, arguably WORSE symptom, because `_update_lock`
   LOOPS (it supports `--lock-timeout`) rather than failing once: a ticket-loser's branch does
   `continue` (`_installer.py:1485` / `cli.js:1371`), sending control back to the TOP of the
   acquire loop, which re-enters the SAME "still stale, ticket still taken" branch every
   iteration — the loop's own `deadline`/`--lock-timeout` check (`_installer.py:1518` /
   `cli.js:1398`) is structurally UNREACHABLE from inside the `age > stale_after` branch, which
   always `continue`s before ever falling through to it. Empirically confirmed via a real thread
   calling `_update_lock(home, timeout=3.0, ...)` against a pre-leaked ticket (external-state
   simulation, no product code or test touched): still running 6+ seconds later — double its
   own declared 3-second budget — a genuine, UNBOUNDED LIVELOCK (a tight busy-spin on
   `os.open`/`os.stat`, no `sleep` anywhere in this branch), not a clean fail (this session's
   scratchpad script + captured output). Reproduced identically via a REAL
   `node cli.js update --global --lock-timeout 3` subprocess against the unmodified JS twin:
   still running 7+ seconds later, had to be killed by the repro script rather than exiting on
   its own. This is WORSE than the sibling's own fail-fast wedge: a caller that explicitly opted
   into `--lock-timeout` for exactly this kind of resilience (e.g. a CI job) would hang
   indefinitely instead of ever receiving the `update_in_progress` it was designed to eventually
   receive.
   (c) UNLIKE the sibling: this task's OWN ticket file (`<home>/.update.lock.reclaim-<inode>`)
   lives in the shared home directory, never inside any project's `<target>/.add/` tree —
   `_persist_data`/`persistData` only ever scans a PROJECT's own `.add/` (confirmed by reading
   `_persist_data(home, project_abspath)`'s own scan target), never the home itself. This task
   does NOT carry the sibling's secondary bogus-persist-then-restore risk — only the direct
   wedge/livelock in (b) above. The severity asymmetry cuts the OTHER way here: this task's own
   failure mode (an unbounded livelock) is arguably MORE severe than the sibling's (a clean
   fail-fast wedge), even though it lacks the sibling's second path to the same bug class.
   Suggested fix direction (not implemented here — a build-phase decision), identical to the
   sibling's: apply the SAME age-based staleness check already used for the main lock file,
   recursively, to the ticket file itself — safe for the same reason (a ticket name is already
   inode-scoped to one generation, so a stale-ticket reclaim does not reopen the identity-blind
   hazard just closed for the lock file). For this task specifically, the loop's `deadline`
   check would ALSO need to be reachable from the stale-ticket branch so a genuinely wedged
   ticket cannot out-live an explicit `--lock-timeout` budget either.
3. Architecture: CLEAR — independently re-verified `_valid_registry_path`/`_update_global`/
   `resolve_global_home` and this task's other named anchors remain byte-identical bodies since
   freeze; O_EXCL/`"wx"` remains the sole DESIGN-level mutual-exclusion primitive; no new
   dependency; the 2 previously-disclosed 💭 notes (lock-hold-duration asymmetry, malformed
   `--lock-timeout` degrading silently in JS) are unaffected by anything found this pass and
   still stand as before, neither blocking. Unlike the sibling, no `_is_user_data` completeness
   note applies here — this task's own ticket file is never scanned as user-data by anything
   (see 2(c) above).
Verdict: HARD-STOP
Residue: concurrency — the identical leaked-reclaim-ticket defect as the sibling task, but
  manifesting as an UNBOUNDED LIVELOCK here (not a clean fail-fast wedge), because
  `_update_lock`'s own retry loop never reaches its `--lock-timeout` deadline check while a
  ticket is contested — confirmed by direct execution against both the real Python function and
  a real `node cli.js` subprocess, not simulated/assumed. The ORIGINAL multi-racer TOCTOU race
  this reopening targeted is independently reconfirmed FIXED. This task's own ticket file carries
  NO secondary persist/restore risk (asymmetric vs. the sibling — see 2(c) above). Separately
  (not part of this Residue, but a required disclosure): the identical shared test-strengthening
  commit that trips a mechanical `build_tampered`/`scope_violation` pair on the sibling task
  produces NO engine WARN here only because this task's own state.json never carried a
  tripwire/scope snapshot to begin with (Refute-read (7) above) — a bookkeeping absence, not
  evidence of a cleaner mechanical state.
Binding: advisory — this task declares no explicit `sensitivity:` line (consistent with ~108
  other tasks project-wide per `add.py audit`'s `sensitivity_unset` list — a pre-existing,
  project-wide gap, not introduced by or specific to this task); this task's own declared
  `risk: high` / `autonomy: conservative` already route it to mandatory human review regardless
  of advisor-gate-relax or the quality of any evidence above — this HARD-STOP is my own
  independent recommendation, not a mechanical override of that pre-existing human-review
  requirement.

Recommended GATE RECORD (not stamped — human/orchestrator decides): HARD-STOP. This task's
  declared `risk: high` + `autonomy: conservative` already mandate human review regardless of my
  own findings — but my own independent evidence supports HARD-STOP, not PASS: a genuine,
  empirically-confirmed, cross-twin livelock residue is present in
  `_update_lock`/`acquireUpdateLock` (see Advisor Concurrency 2(b) above). The EXISTING GATE
  RECORD immediately below (Outcome: PASS, reviewed by Tin Dang, 2026-07-03) predates this
  entire redo — it was recorded against evidence that has since been superseded twice over
  (once by the reopening that found the original TOCTOU race, again by the finding above) and
  should not be treated as current; a fresh human decision is required before this task can be
  considered gated.

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
- [SPEC · open] `_update_global`'s `home.mkdir()` can raise the same uncaught
  `FileExistsError`/`OSError` this task fixed in `install()` if `home` exists as a
  non-directory — dormant today only because `_update_global`'s own `no_global_home`
  pre-check short-circuits first in every currently-exercised path; mirror the same
  `except OSError` widening there, or harden `_update_lock` itself to translate a
  home-mkdir failure into its own distinct signal (evidence: OBSERVE-NOTES.md build-phase
  finding #2; confirmed by reading `_update_global`'s pre-check ordering, not assumed)
- [SPEC · open] a malformed `--lock-timeout <non-numeric>` value degrades silently to
  `NaN` → falsy → no-wait in `cli.js`, while Python's `argparse(type=float)` errors loudly
  on the identical input — a minor cross-twin inconsistency for an out-of-contract misuse
  case, not a safety issue, but worth closing (evidence: independent add-verify pass,
  Advisor Architecture lens, §6)
- [SPEC · open] no genuine cross-twin CLI-to-CLI multi-process smoke exists yet (a real
  `pip`-driven CLI process racing a real `node cli.js` process at the OS level) — cheap to
  add; not required to close this task's own gate given the primitive-level and
  full-function-level multi-process evidence already gathered at the Python layer, but a
  natural next-loop hardening (evidence: independent add-verify pass, Advisor Concurrency
  lens, §6)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · open] a parallel-build worktree can be branched before the orchestrator finishes
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
- [ADD · open] the SAME class of gap recurs one layer deeper and is NOT limited to the
  frozen-contract case above: a fresh `git worktree add` never materializes gitignored /
  untracked content (`.add/tooling/add.py`, `.add/docs`) even when the base commit's
  TRACKED files are otherwise current — every worktree spawned this session needed a
  manual copy-in before its own engine commands (`add.py phase`/`advance`) would work at
  all. A worktree-spawn step should either materialize these trees automatically, or the
  spawn prompt should include an explicit step-0 check (evidence: found independently in
  `project-scope-atomic-reconcile`'s, this task's, AND `global-data-restore-harden`'s
  worktrees this session — 3 for 3, not a one-off)
- [TDD · open] the disclosed in-process-thread-only concurrency evidence for a `risk: high`
  task was judged insufficient for sign-off by an independent verify pass — closing that
  gap required authoring genuinely NEW multi-process tests (real `subprocess.Popen` races),
  not merely re-running the existing suite. A `risk: high` task's own §4 test plan should
  budget for real multi-process coverage up front rather than leaving it to a verify-time
  discovery (evidence: the independent add-verify pass authored 2 new tests — 8 trials × 6
  processes on the raw lock primitive, 6 trials × 8 processes on the full `install()` path —
  after judging the builder's own thread-based evidence insufficient for a risk:high gate)

