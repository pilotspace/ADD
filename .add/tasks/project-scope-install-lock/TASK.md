# TASK: Project-scoped lock around install()/update() reconcile, both twins

slug: project-scope-install-lock · created: 2026-07-02 · stage: mvp
milestone: install-update-hardening
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/src/add_method/_installer.py:install(target, force, stage, name, yes, non_interactive, bundled, env, as_global, as_global_data, as_global_data_restore, rule_file) -> int` (889-1079) — CONFIRMED (read in full): the project-scope entry point. Validates `target_path.exists()`, then (interactive only) may run `_prompt_target`, which can REASSIGN `target_path` to a DIFFERENT directory than the one first passed — a lock must key on the FINAL, post-prompt value, not the initial argument. After the interactive block, `_log(f"Installing ADD into {target_path}")` runs, then `bundled_root` resolution, the `as_global` sub-block (home/registry writes — a DIFFERENT target, see below), `_reconcile(target_path, bundled_root)`, `_seed_soul_md`, `_seed_gitignore`, agent-pointer write, Gemini settings, intent note, and (opt-in) `_persist_data`/`_restore_data` — ALL of it currently runs with ZERO mutual exclusion against a second concurrent call on the SAME target.
  - `add-method/src/add_method/_installer.py:update(target, force, bundled, version, channel, env, as_global) -> int` (1384-1446) — CONFIRMED: `as_global=True` short-circuits entirely to `_update_global(...)` (a DIFFERENT target — the shared home — already covered, eventually, by `_update_lock`; UNCHANGED and out of my scope). The non-`as_global` branch resolves `add_dir = _add_dir(target_path)`, checks the "no ADD project here" precondition (lock-free), then bundled-root validation, a same-version no-op early `return 0` (no writes), state-file backup, `_reconcile`, migrations, stamp write, soul/gitignore seed — ZERO mutual exclusion today.
  - `add-method/bin/cli.js:cmdInit(args)` (680-730) / `dropFiles(args, target, profile, intent)` (635-678) — JS mirror of `install()`. CONFIRMED: `chosenTarget` (initialized to `target`) can be REASSIGNED by the interactive clack flow (`chosenTarget = path.resolve(outcome.target)`) before `if (args.global) installGlobal(args, chosenTarget)` and `dropFiles(args, chosenTarget, ...)` run — the same "lock the FINAL target, not the initial argument" requirement as the Python side.
  - `add-method/bin/cli.js:cmdUpdate(args)` (1226-1266) — JS mirror of `update()`. CONFIRMED: `if (args.global) return cmdUpdateGlobal(args);` (unchanged, out of scope) else resolves `target`/`addDir`, the same precondition check, THEN an INLINED `if (args.check) { ...; return; }` read-only report (lines 1237-1242) — a genuine, PRE-EXISTING cross-twin asymmetry: Python's `--check` is dispatched to a fully separate function `update_check()` BEFORE `update()` is ever invoked (confirmed via `_cli.py:52-53`: `if args.check: return update_check(target=args.target)`), so Python's `update()` body never sees a check request at all, while JS inlines it inside the SAME function my lock wraps. My JS-side lock acquisition must sit AFTER this early return; Python needs no equivalent carve-out.
  - `add-method/src/add_method/_installer.py:_update_lock(home: Path)` (1268-1290, `@contextlib.contextmanager`) / `cli.js:acquireUpdateLock(home)` (1161-1179) — CONFIRMED CURRENT (pre-`global-lock-followups`) shape: a plain O_EXCL (`os.open(..., os.O_CREAT|os.O_EXCL|os.O_WRONLY)`) / `"wx"` (`fs.openSync(lockPath,"wx")`) sentinel-file create at `<home>/.update.lock`; `FileExistsError`/`EEXIST` -> `update_in_progress`; cleanup is unconditional (Python: `finally: os.close(fd); os.unlink(...)`; JS: `process.on("exit", release)`, registered BECAUSE `cli.js:fail()` (line 35) calls `process.exit(1)` DIRECTLY — Node does NOT unwind the stack or run a pending `finally` on `process.exit()`, so a plain `try/finally` would silently skip releasing the lock if anything nested inside the guarded region calls `fail()`; `acquireUpdateLock`'s `process.on("exit", release)` hook is how the ALREADY-SHIPPED code correctly handles this). UPDATE (re-confirmed post-draft, orchestrator note): `global-lock-followups`'s own hardening (which adds exactly those three things — stale self-heal, timeout, diagnostic stamp) merged into `release/1.15.0` at commit `7396456`, shortly after this grounding was written against `1cc4065`. The shape described above is now the CURRENT merged `_update_lock`/`acquireUpdateLock`, not a future one. Still cited here as PROVEN-PATTERN precedent to mirror, never as code this task calls into or extends (see §1 Framings weighed — the reuse-vs-new-primitive reasoning stands on the resource-shape difference, independent of merge timing).
  - `add-method/src/add_method/_installer.py:_update_global(target, *, force, bundled, version, env) -> int` (1302-1381) — demonstrates the established HIGH-LEVEL idiom I mirror: a cheap, lock-free existence precondition (`no_global_home`) is checked first; `with _update_lock(home): ...` then wraps the mutating span through to `return 0`; `BlockingIOError` is caught OUTSIDE that `with`/an enclosing `try`, mapped to `_fail("update_in_progress: ...")`. NOTE (precise, not overclaimed): `_update_global` ALSO keeps its own bundled-root/MANAGED-sources validation lock-free (before the `with`) — a finer-grained optimization that matters at the global case's scale (a broken package shouldn't need to contend for a lock that may be serializing propagation to many registered projects). My own `install()`/`update()` design (§3) makes a DELIBERATE, disclosed simplification: it holds the lock across bundled-root validation too (one single acquire point, not two), since that validation is a handful of cheap `Path.exists()` calls — negligible extra hold time at this smaller, per-target scale. I mirror the high-level pattern (cheap precondition free, then acquire-and-hold for the rest), not this one finer-grained sub-optimization.
  - `add-method/src/add_method/_installer.py:_clean_replace(src, dest, *, strip_tests=False) -> dict` (1130-1202) / `cli.js:cleanReplaceTree(src, dest, stripTests)` (798-869) — CONFIRMED ALREADY HARDENED: this task's OWN dependency, `project-scope-atomic-reconcile`, merged at `d6c7e91` (merge commit `c703495`, verified via `git log`/`git show --stat c703495`: `Merge: 3d69f4e ec03de1`, tip commit `d6c7e91 feat(installer): stage-then-swap clean-replace, crash-safe on both twins`, landed on `release/1.15.0`). Self-heal (`.add-tmp-*`/`.add-bak-*` glob) -> stage into a fresh same-parent tempdir -> two-rename commit (aside, then land) -> sweep. Its own INV is explicit that this guarantee is PER-CALLER ("never observed half-composed FROM ITS OWN COPY") — silent on TWO CALLERS racing the SAME `dest`, by design: its own Reject scenario names this exact gap as OUT of scope, owned by THIS task. My task does not touch this function at all; it adds a DIFFERENT, layered guarantee (cross-call mutual exclusion) on top of the SAME call sites this function already makes single-call-crash-safe.
  - `add-method/src/add_method/_installer.py:_reconcile(target_path, bundled_root) -> dict` (1218-1239) / `cli.js:reconcile(args, target, srcRoot)` (888-913) — loops over `MANAGED` (4 trees), one `_clean_replace`/`cleanReplaceTree` call per tree. The CORE work my new lock serializes; UNCHANGED by this task.
  - `add-method/src/add_method/_installer.py:_is_user_data(name) -> bool` (704-714) / `cli.js:isUserData(name)` (996-1002) — CONFIRMED (read the actual current body, not inferred from the milestone doc): excludes the exact-name `_DATA_EXCLUDE`/`DATA_EXCLUDE` set, a `scope-snapshot` prefix, a `pre-archive-bak` substring, and a `.bak.json` suffix. Does **NOT** yet exclude any `.add-tmp-`/`.add-bak-` scratch marker — that extension is `global-data-restore-harden`'s own M11, and that task's own phase marker still reads `phase: contract` (not yet built/merged); `project-scope-atomic-reconcile` deliberately declined to touch this function too (its own Issue/Risk #4 relies on same-invocation call-order instead). This matters directly for my own design (see Issues/Risks below) — I ground against the REAL current body, not the milestone doc's forward-looking description of a not-yet-shipped state.
  - `add-method/src/add_method/_installer.py:_DATA_EXCLUDE` (692) / `cli.js:DATA_EXCLUDE` (985) — CONFIRMED: `{"tooling", "docs", ".update-cache", STAMP_FILE, LOCK_FILE}` (Python set) / `["tooling", "docs", ".update-cache", STAMP_FILE, LOCK_FILE]` (JS array). `LOCK_FILE`'s value (`.update.lock`) is ALREADY an exact-name member of this set — the established precedent that "a lock file's name is excluded from the user-data scan," even though `.update.lock` itself lives at `<home>/.update.lock` (never inside a project's own `.add/`, so this particular membership is a documentation/consistency inclusion more than an exercised one). My own new lock file WILL live inside a scanned `<project>/.add/` (see below), making the identical exact-name treatment functionally load-bearing this time, not just decorative.
  - `add-method/src/add_method/_installer.py:_persist_data(home, project_abspath) -> bool` (717-737) — CONFIRMED: scans `Path(project_abspath) / ".add"`'s top-level entries (`add_dir.iterdir()`), filtered by `_is_user_data`, snapshotting into `<home>/data/<key>`. Ground description was the OLD, non-atomic wipe-then-copy shape; `global-data-restore-harden`'s own hardening of this function has SINCE merged too (commit `52aafdf`, stage-then-commit) — irrelevant either way to my task's OWN correctness (I don't touch this function's body regardless of which shape it's in), but its SCAN DIRECTORY is exactly where my new lock file would live, which is why it matters here.
  - `add-method/src/add_method/_installer.py:_add_dir(target_path) -> Path` (1264-1265) — `return target_path / ".add"`. Trivial, already-shared helper; the natural "project root" analog to `resolve_global_home`'s `<home>` — I reuse it (unchanged) to resolve where my new lock's own directory lives.
  - `add-method/src/add_method/_installer.py:resolve_global_home(env=None) -> Path` (605-618) — cited ONLY as the ALREADY-MERGED precedent for "env-injectable for hermetic tests" (`ADD_HOME` -> `XDG_DATA_HOME/add` -> `<HOME>/.add`, reading from an injected `env` mapping, never `os.environ` directly) — the pattern my own new lock's `env` parameter mirrors, so a test can inject `ADD_PROJECT_LOCK_STALE_SECONDS` without a real wait. (`global-lock-followups`'s OWN env-injection for `_update_lock` has since merged too, per the note at Ground line 24 above — this precedent choice was grounded against the pre-merge shape but holds identically against the current one.)
  - `add-method/src/add_method/_cli.py` (~24-53) — CONFIRMED: pip's `update --check` dispatches to a standalone `update_check(target=...)` function BEFORE `update()` is ever invoked (`if args.check: return update_check(target=args.target)`, line 52-53) — confirms the cross-twin asymmetry noted above from the OTHER side.
  - `add-method/src/add_method/_installer.py` imports (confirmed via `grep "^import\|^from"`): `contextlib, hashlib, importlib.resources, json, os, re, shutil, sys, tempfile`, `from datetime import datetime, timezone`, `from pathlib import Path`. **No `time` module yet.** My mtime-staleness check needs `time.time()` (or an equivalent); `import time` is a plain stdlib addition, not a new dependency — `global-lock-followups`'s own (now-merged, commit `7396456`) implementation already established this exact same addition for the identical purpose, an independently-confirming precedent.
  - `add-method/src/add_method/_installer.py:_fail(msg) -> int` (53-56) — CONFIRMED: `sys.stderr.write(...); sys.stderr.flush(); return 1` — an ORDINARY function returning `1`, never `sys.exit()`/an exception. Every `return _fail(...)` inside a `with _project_lock(...):` block therefore unwinds and releases the lock completely normally — Python needs NO exit-hook trick (unlike JS's `fail()`/`process.exit(1)` above); this asymmetry is real and pre-existing, not introduced by this task.
Context (working folder):
  - `.add/milestones/install-update-hardening/MILESTONE.md` — read in full; this task is the 4th and last of the milestone, `depends_on: project-scope-atomic-reconcile` (DONE, merged). The milestone's own Tasks checklist still shows this task as "not yet drafted (waits on its dependency's evidence)" — that dependency is now satisfied.
  - No other project-scope lock, timeout, or staleness mechanism exists anywhere in `_installer.py`/`cli.js` today (confirmed by a full-file search for "lock" on `_installer.py`: every hit is either the DOCSTRING-only phrase "lock-down gate" (an unrelated ADD-methodology concept — the v12 gate `/add`'s own `init --await-lock` arms — NOT a file lock), or `_update_lock`/`LOCK_FILE`/`_DATA_EXCLUDE` themselves). This task's mechanism is genuinely new, not a rename/extension of anything already present.
Honors (patterns / conventions):
  - `.add/personas/methodology-engine-dev.md:14` (CONFIRMED exact text): "Design for failure. Every IO touch has a fail-closed path (timeout, missing file, corrupt registry → loud error, never silent half-write). Atomic writes only; no partial state." — the SAME persona both sibling tasks in this milestone used; nominally scoped to `add.py`/`add_engine/*` (this task touches neither — no `ENGINE_MD5`/`ENGINE_PKG_MD5` re-pin is needed), but its rules apply directly here too, the same adapted-fit caveat both siblings made.
  - `.add/CONVENTIONS.md:63` (CONFIRMED exact text, "folded foundation-version 59, from global-update-harden"): "a frozen contract that pins a per-twin IMPLEMENTATION mechanism... can fail its own INTENT... — freeze the OBSERVABLE behavior... not the mechanism." — governs how §3 states this task's guarantee (both twins guarantee the same observable exclusivity/self-heal behavior, via each platform's own native primitive).
  - The user's own global CRITICAL RULE ("MUST design for failure: timeouts, retries, circuit breakers, rollback strategy in IO request") explicitly names "timeouts"/"retries" — addressed by the stale-lock self-heal's bounded, exactly-once retry (§1 M5), with the ABSENCE of a bounded-wait CLI flag being a considered, disclosed choice rather than an oversight (§1 Framings weighed).
  - `project-scope-atomic-reconcile`'s own frozen Reject scenario (verbatim): "two concurrent, lock-less `install`/`update` processes both invoke `_clean_replace`/`cleanReplaceTree` for the SAME `dest`... this task makes NO guarantee about which writer's content wins the race... Serializing concurrent runs is `project-scope-install-lock`'s job." — the literal origin of this task.
  - `global-lock-followups`'s own frozen OUT-of-scope text (verbatim, confirming the boundary from the OTHER direction): "Serializing two concurrent install/update runs against the SAME per-PROJECT target dir (a DIFFERENT, per-project lock) — owned by the sibling task `project-scope-install-lock`... this task's lock is scoped to the shared HOME + registry.json only, never a project directory." Its own hardening design (self-heal by mtime-age, O_EXCL/`"wx"` as the sole exclusion primitive, no PID-liveness check because it is not portable on Windows, an opt-in `--lock-timeout`, a diagnostic-only PID+timestamp stamp) is read here as PATTERN PRECEDENT, independently mirrored where it fits my own, smaller-blast-radius threat model (self-heal, primitive, diagnostic stamp) and deliberately DIVERGED from where it doesn't (no bounded-wait flag, a shorter/independent staleness default, no shared code) — see §1 Framings weighed for the reasoned split.
Seams consulted: none apply (`.add/SEAMS.md`'s 5 entries — engine-md5-repin, three-tree-parity, scope-token-grammar, phase-body-extraction, section-unfilled-truth-table — cover ADD's own engine/template/scope-parsing conventions, not installer concurrency primitives; matches both sibling tasks' own conclusion).
Anchors the contract cites: NEW `_project_lock`/`acquireProjectLock` · NEW `PROJECT_LOCK_FILE` constant (both twins) · `install`/`cmdInit` (new lock-wrap span) · `update`/`cmdUpdate` (new lock-wrap span, non-`--global` path only) · `_DATA_EXCLUDE`/`DATA_EXCLUDE` (one new exact-name member) · `_add_dir` (cited, unchanged, reused to resolve the lock's own directory) · the EXISTING `_update_lock`/`acquireUpdateLock` (cited as pattern precedent and for the lock-ordering invariant, NEVER called into, NEVER modified by this task).
Issues/Risks (→ feed §1):
  1. **Core gap**: project-scope `install()`/`update()` have ZERO mutual exclusion today. Each individual `_clean_replace`/`cleanReplaceTree` call is now internally crash-safe (the merged dependency), but nothing stops TWO SEPARATE, concurrently-racing calls to it (one per racing process) on the SAME `dest` — exactly the gap `project-scope-atomic-reconcile`'s own Reject scenario named and deferred to this task.
  2. `install()`'s (and `cmdInit`'s) interactive flow can REASSIGN the target directory (via `_prompt_target`/the clack preamble) AFTER the function starts but BEFORE any real work begins — the lock must key on the FINAL, post-prompt target, never the initial CLI argument, or two concurrent interactive installs could contend on the wrong directory (or fail to contend on the right one).
  3. Pre-existing, NOT-introduced-by-me cross-twin structural asymmetry: JS's `cmdUpdate` inlines its `--check` read-only report as an early return WITHIN the same function my lock wraps; Python's `--check` is a fully separate function (`update_check()`) that never calls `update()` at all. My JS-side lock acquisition must sit after that early return; Python needs no equivalent carve-out. Left unaddressed, an over-hasty "just wrap the whole function" edit on the JS side would make a purely-informational `--check` invocation needlessly contend for (and, if held, fail on) a lock it has no reason to touch.
  4. If my new lock file lives inside `<target>/.add/` (the natural choice, mirroring `<home>/.update.lock`'s own placement at the analogous root) and is NOT excluded from `_is_user_data`/`isUserData`, a `--global-data` persist call — itself invoked from WITHIN the SAME locked `install()` span, after `_reconcile` completes but before the function returns — would scan `<target>/.add` and snapshot the CURRENTLY-HELD lock file as if it were user-data, later restorable into a fresh clone as a bogus pre-existing lock artifact. Closed by a one-line exact-name addition to `_DATA_EXCLUDE`/`DATA_EXCLUDE`, mirroring `LOCK_FILE`'s own existing membership — independent of, and not waiting on, `global-data-restore-harden`'s separate (not-yet-built) `.add-tmp-`/`.add-bak-` pattern-exclusion, since my lock file is a FIXED exact name, not a token-suffixed scratch sibling.
  5. Lock-ordering / deadlock consideration — UPGRADED from forward-looking to LIVE (orchestrator re-check, post-draft): `global-lock-followups` merged (`7396456`) after this grounding was written. `install()`'s `as_global` sub-block NOW holds `with _update_lock(home, timeout=lock_timeout, env=env_map):` today (confirmed by reading the current merged body, `_installer.py` ~1090-1099) — so the nested-lock scenario is no longer hypothetical. Verified the ordering is still SAFE by construction: M1 (§1) wraps the project-scope lock around install()'s ENTIRE call, acquired before any write begins — which means, once built, the project lock will sit OUTSIDE the function call and the already-merged home lock will sit INSIDE it (nested only within the as_global sub-span), matching INV (§3, "a project-scope lock is ALWAYS acquired before, never nested inside, any home-scoped lock") by the shape of the wrap itself, not by a coincidence of merge order. This is now a concretely testable invariant for THIS task's own §4 TESTS phase (a real `install(as_global=True)` call exercising both locks simultaneously), not a note deferred to "whichever task lands second."
  6. Same non-portable-PID-liveness ceiling `global-lock-followups` already independently discovered (Windows `os.kill(pid, 0)` can actually TERMINATE the held process rather than merely probe it) applies identically here — mtime-age, never PID, is the only viable staleness signal for ANY stdlib-only lock in this codebase, project-scope or global.
  7. Same non-portable-atomic-directory-swap ceiling underlies why a SEPARATE lock is needed alongside (never instead of) `_clean_replace`'s own crash-safety: that function's own INV is explicit that its guarantee is PER-CALLER, not cross-caller — this task supplies the cross-caller half.
Related intent:
  - Milestone `install-update-hardening` goal (verbatim): "add.py init/update (both --global and project-scope, pip+npm twins) survive a crash or a concurrent run without leaving a half-written .add/ tree or a wedged lock" — this task delivers the "concurrent run" AND "wedged lock" halves for the PROJECT-scope case, the LAST of the milestone's 4 exit criteria.
  - Milestone's own named exit criterion (verbatim, cited per this task's own brief): "Two concurrent install/update runs against the SAME project-scope destination cannot interleave writes — one waits or fails cleanly (verify: project-scope-install-lock §4 concurrent-run scenarios, once drafted)."
  - `project-scope-atomic-reconcile`'s and `global-lock-followups`'s own frozen texts (both quoted verbatim above under Honors) jointly and precisely bound this task's scope from BOTH directions: not the copy mechanism (that task's job), not the shared home (that task's job) — exactly and only the project-scope mutual-exclusion gap.
  - GLOSSARY.md: no existing "lock" domain term — stays internal code vocabulary + a new machine-readable reject code, matching both sibling tasks' own "none" precedent for a hardening/mechanism-only task.
Ground SHA: 1cc4065

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a NEW per-project-scope lock (`_project_lock`/`acquireProjectLock`) serializing concurrent `install()`/`cmdInit` and `update()`/`cmdUpdate`'s non-`--global` path against the SAME target directory's own `.add/` tree — a peer to, but mechanically and architecturally INDEPENDENT from, the existing/eventual global-home lock (`_update_lock`/`acquireUpdateLock`).
Framings weighed: a NEW, independent lock primitive — own function, own lock file (`<target>/.add/.install.lock`), own env-overridable staleness default — that MIRRORS the proven O_EXCL/`"wx"` + mtime-age-self-heal PATTERN already established in this codebase, without calling into or extending either the current or the eventual `_update_lock`/`acquireUpdateLock` (chosen) · generalize/extend `_update_lock`/`acquireUpdateLock` itself to accept ANY root (home OR a project's `.add/` dir), calling it from both `_update_global` (existing) and `install`/`update` (new) (rejected: at draft time, `global-lock-followups`'s own hardening of that function was FROZEN but not yet merged — that specific coupling concern is now moot, since it merged (`7396456`) shortly after this draft was written; the choice still stands on its OWN, merge-order-independent merits — the two locks guard genuinely different-shaped resources — one shared, machine-wide, potentially-many-registered-projects propagation (tolerating a long ~600s staleness window and motivating an opt-in CI wait) versus one per-target, typically-few-seconds reconcile (wanting a much shorter default and no wait mode) — forcing one shared knob would be an awkward compromise between the two (this reasoning holds regardless of merge order, which is now moot: both tasks merged, `global-lock-followups` first) · no lock at all, relying solely on `_clean_replace`'s already-shipped per-call atomicity and accepting an unpredictable last-writer-wins outcome (rejected: the milestone's own 4th exit criterion explicitly demands "cannot interleave writes — one waits or fails cleanly," a strictly stronger guarantee than "each writer's OWN copy is internally atomic," which already exists today without any new work) · an OS-level advisory file lock (`fcntl.flock`/Windows `msvcrt.locking`) instead of an O_EXCL sentinel file (rejected: the identical, already-learned CONVENTIONS.md fv59 lesson — an OS-level advisory lock is not observable/compatible cross-twin, since Node has no `flock` equivalent without a native dependency, which the "no new dependency anywhere in this milestone" constraint rules out) · an opt-in `--lock-timeout`-style bounded-wait CLI flag, mirroring `global-lock-followups`'s own M4 (considered and DECLINED, not silently omitted: that flag's motivating use case — a CI job waiting out a potentially-long multi-project global propagation — does not transfer cleanly to a per-project lock whose expected hold duration is a handful of `_clean_replace` calls; immediate fail-fast is simpler, needs no new CLI surface, matching this milestone's own "no new flag surface for routine tuning" spirit, and the exit criterion itself offers "waits OR fails cleanly" as two equally acceptable options, not a mandate for waiting).
Must:
<must>
  - M1: `install()` (Python) and `cmdInit` (JS) acquire the new project-scope lock keyed to the FINAL, post-interactive-prompt target directory's own `.add/` tree, BEFORE any write begins (bundled-root resolution onward) and hold it for the entire remainder of the call — the `as_global` sub-block, `_reconcile`, soul/gitignore seed, agent-pointer write, intent note, and (if opted in) persist/restore — releasing on EVERY exit path (every early `_fail()`/`fail()` return AND the final success return), regardless of whether `--global`/`--global-data`/`--from-global-data` is ALSO passed (the per-project drop always runs, so the lock always applies).
  - M2: `update()` (Python, non-`--global` branch only) and `cmdUpdate` (JS, non-`--global` branch only) acquire the SAME kind of project-scope lock, keyed to the target's `.add/` tree, immediately after the existing "no ADD project here" precondition check, and hold it for the entire remainder of the call — INCLUDING the same-version no-op check, so a second waiter re-evaluates it FRESH once it acquires (avoiding both a stale-read race and a redundant re-reconcile) — through to every exit (the no-op early return AND the final success return). `update(as_global=True)`/`cmdUpdateGlobal`'s wholesale delegation elsewhere is UNCHANGED and untouched (a DIFFERENT target, already covered by the existing/future global lock).
  - M3 (JS-only carve-out, a pre-existing cross-twin asymmetry, not a divergence this task introduces): `cmdUpdate`'s existing inlined `--check` early return (a pure, read-only report, no writes) stays OUTSIDE/BEFORE the lock acquisition. Python's `update()` never sees a `--check` request at all (dispatched separately by `_cli.py` to `update_check()`), so no equivalent carve-out exists or is needed on the Python side.
  - M4: the lock's sole mutual-exclusion primitive is an O_EXCL (Python `os.open(path, os.O_CREAT|os.O_EXCL|os.O_WRONLY)`) / `"wx"` (JS `fs.openSync(path,"wx")`) sentinel-file create at `<target>/.add/.install.lock` — the SAME cross-twin-safe primitive class `_update_lock`/`acquireUpdateLock` already established; never an OS-level advisory lock.
  - M5 (stale-lock self-heal — independently re-derived and independently defaulted for this task's own, shorter-duration threat model, mirroring the SAME proven shape `global-lock-followups`'s own frozen design uses for a different resource): on contention (`EEXIST`), stat the existing lock file; if `now − mtime > ADD_PROJECT_LOCK_STALE_SECONDS` (env-overridable; default proposed in Assumptions), unlink it and retry the create EXACTLY once before falling through to fail-fast. A future/bogus mtime (clock skew) is NEVER treated as stale (sign-aware age check). The create remains the SOLE exclusivity decision — staleness only ever decides whether to retry, never bypasses exclusivity: at most one racing process's create can succeed at any instant, even when two processes independently judge the same lock stale and both attempt to reclaim it.
  - M6 (diagnostic stamp, cheap and optional-in-spirit but included for parity with the sibling's own design): on a successful acquire (fresh or reclaimed), the lock file's content is stamped `"<PID> <ISO-8601 UTC timestamp>\n"` — informational ONLY, never read to decide staleness. A crash between create and this stamp write leaves the file EMPTY; staleness (mtime-keyed) is unaffected, and a later contention message degrades to "holder unknown" instead of erroring on unparseable content.
  - M7 (no bounded-wait flag — a deliberate, disclosed absence, not an oversight, see Framings weighed): this task introduces NO new CLI flag. A LIVE (non-stale) contended lock fails IMMEDIATELY with a new, distinct reject code (see Reject) — never waits, never polls.
  - M8 (`_DATA_EXCLUDE`/`DATA_EXCLUDE` extension): the lock's exact filename (`.install.lock`, held in a new `PROJECT_LOCK_FILE` constant) is added as a ONE-LINE, exact-name member of `_DATA_EXCLUDE`/`DATA_EXCLUDE` — mirroring `LOCK_FILE`'s own existing membership — so `_persist_data`/`persistData`'s scan of `<target>/.add`'s top-level entries never snapshots a currently-held (or stale-but-not-yet-swept) lock file as user-data.
  - M9 (both twins / parity): `_project_lock` (Python, `@contextlib.contextmanager`) and `acquireProjectLock` (JS, returning a `release()` closure per the SAME idiom `acquireUpdateLock` already uses, and registered via `process.on("exit", release)` for the IDENTICAL reason `acquireUpdateLock` already needs it — `cli.js:fail()` calls `process.exit(1)` directly, skipping any pending `finally`, so a plain `try/finally` would silently fail to release the lock if anything nested inside the guarded region calls `fail()`) guarantee the SAME observable behavior — exclusivity, self-heal, diagnostic stamp, immediate fail-fast — each via its own native primitive. Internal JS failures inside the lock's own acquire/release logic `throw` real `Error`s, never call `fail()` directly.
  - M10 (unchanged elsewhere): `_reconcile`/`reconcile`, `_clean_replace`/`cleanReplaceTree`, `_is_user_data`/`isUserData` (beyond the one new exact-name member in M8), `_update_lock`/`acquireUpdateLock`, `_update_global`/`cmdUpdateGlobal` are ALL byte-identical to before this task — this task adds a new, independent lock and its two call-site wraps, nothing else.
  - M11 (lock-ordering invariant — LIVE, not forward-looking: `global-lock-followups` merged first, `7396456`): a project-scope lock is ALWAYS acquired before, never nested inside, any home-scoped lock (`_update_lock`/`acquireUpdateLock`) acquisition for the same call. `install`'s `as_global` sub-block's home-lock acquisition already exists in the current tree, nested inside the function body — this task's own project-lock wrap (M1, whole-function span) MUST land OUTSIDE it, never the reverse. Verified safe by construction at draft time (the nesting direction M1 already specifies satisfies this); a real test exercising `install(as_global=True)` with both locks live is the concrete proof required at this task's own BUILD/VERIFY, not merely re-reading this note.
</must>
Reject:
<reject>
  - a live (non-stale) project lock is held, contended by a second `install()`/`update()` call against the SAME target -> "install_in_progress" (nothing written, the held lock untouched; distinct from the EXISTING `update_in_progress`, which guards a DIFFERENT resource — the shared home, never a project directory)
</reject>
After:
<after>
  - two concurrent `install()`/`update()` (project-scope) calls against the SAME target never interleave writes to that target's managed trees or seeded files — exactly one proceeds at a time; the other fails immediately with `install_in_progress`, having written nothing.
  - a crashed (SIGKILL'd) `install()`/`update()` never wedges a future call against the SAME target — the stale lock self-heals on the very next attempt, no manual deletion required.
  - the lock file is never mistaken for user-data by `_persist_data`/`persistData`'s snapshot scan, nor (consequently) ever restored into a fresh clone as a bogus pre-existing artifact.
  - `_clean_replace`/`cleanReplaceTree`'s own per-call crash-safety (the merged dependency) is unchanged and composes with, never duplicates, this task's cross-call mutual exclusion.
  - the existing global-home lock (`_update_lock`/`acquireUpdateLock`, current OR its own eventual hardened shape) is completely unchanged and untouched by this task.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ A1 (lowest confidence): `ADD_PROJECT_LOCK_STALE_SECONDS`'s proposed default, 120 seconds — deliberately SHORTER than the global lock's own 600s, reasoned from a project-scope reconcile typically being a handful of `_clean_replace` calls over 4 small-to-medium managed trees (sub-second to low-single-digit seconds even on a slow disk), so a genuinely wedged (crashed) holder should self-heal much sooner than the global case's own, propagation-driven tolerance. There is NO production timing data in this repo for a realistic worst-case (e.g., a large `personas-teacher` tree on a slow CI runner or network-mounted volume) to calibrate against — the identical calibration gap `global-lock-followups` itself already disclosed for its own threshold. If wrong (too short): a false-positive reclaim of a still-alive-but-slow holder, briefly defeating mutual exclusion for that one contended run. If wrong (too long): only delays self-heal of a genuinely wedged lock — inconvenient, not unsafe. Cheap to change either way (one constant).
  ⚠ A2: the reuse-vs-new-primitive architectural fork itself (Framings weighed) — building an INDEPENDENT primitive rather than extending `_update_lock`/`acquireUpdateLock`. `global-lock-followups` has SINCE merged (`7396456`), so the "avoids coupling to an unmerged sibling" half of the original reasoning no longer applies — but the "different threat models warrant different defaults" half (600s machine-wide tolerance + opt-in CI wait vs. a short per-target default with no wait mode) stands on its own regardless. This remains a genuine, either-way-defensible fork a human may weigh differently — e.g., preferring ONE unified lock implementation for future maintainability even at the cost of forcing a compromise default. If the human prefers the reuse path instead: the redesign is moderate, not a rewrite — the OBSERVABLE guarantees (M1-M9) stay the same, only the internal call-site/shared-vs-separate-function question changes.
  - [ ] A3: the lock file's exact name/location (`<target>/.add/.install.lock`) — a low-stakes bikeshed; any other exact, fixed, `.add/`-relative name works identically once added to `_DATA_EXCLUDE`/`DATA_EXCLUDE` (M8). If the human prefers a different name (or a location OUTSIDE `.add/`, sidestepping the `_DATA_EXCLUDE` addition entirely), this is a trivial rename with zero ripple into the rest of the design.
  - [ ] A4: no bounded-wait CLI flag (Framings weighed) — a deliberate, disclosed choice, not an oversight; if the human wants CI-friendly waiting for the project-scope case too (symmetry with `global-lock-followups`'s own `--lock-timeout`), it is a small, additive follow-up (the same polling-loop shape, a new flag on `init`/`update`), not a redesign of anything M1-M11 already establish.
  - [x] A5 (RESOLVED, orchestrator re-check post-draft): M11's lock-ordering invariant was drafted as vacuous/forward-looking; `global-lock-followups` has since merged FIRST (`7396456`), so its own `install(as_global=True)` `_update_lock` wrap now exists in the current tree. Checked (not assumed): it sits inside the `as_global` sub-block, which M1's whole-function project-lock wrap will correctly nest OUTSIDE of — the invariant holds by the shape of the design, confirmed against the real merged code. No longer an open assumption; promoted to an explicit §4 TESTS item instead (a real `install(as_global=True)` call exercising both locks together).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a fresh, uncontended install acquires and releases the lock transparently   # M1 (baseline)
  Given a target directory with no ADD project yet, and no lock held
  When I run install() / cmdInit against it
  Then the install completes exactly as before this task (exit 0, all managed trees materialized)
  And .add/.install.lock does not exist once the call returns

Scenario: two concurrent install() calls racing on the SAME new target — one proceeds, one fails cleanly   # M1, M4, Reject install_in_progress (the core exit criterion)
  Given a target directory with no ADD project yet
  When two install() calls start against it at overlapping times
  Then exactly one acquires the lock and completes its full managed-tree drop
  And the other fails immediately with "install_in_progress", having written nothing to the target
  And the target's managed trees are never observed as an interleaved mix of the two runs' content

Scenario: two concurrent update() calls racing on the SAME existing target — one proceeds, one fails cleanly   # M2, M4, Reject install_in_progress
  Given a target directory with an existing ADD project (.add/tooling present) at an older version
  When two update() calls start against it at overlapping times
  Then exactly one acquires the lock, reconciles, and writes the new stamp
  And the other fails immediately with "install_in_progress", having written nothing

Scenario: the lock keys on the FINAL, post-prompt target, not the initial argument   # M1 edge case
  Given an interactive install() call whose target-selection prompt redirects from directory X to directory Y
  When the call proceeds past the prompt
  Then the lock is acquired against Y's .add/ tree, never X's
  And a second, concurrent install() call against Y (not X) correctly contends with the first

Scenario: install --global still serializes the per-project drop under the same new lock   # M1
  Given a target directory with no ADD project yet, and --global (or --global-data) requested
  When install() runs
  Then the project-scope lock is held across BOTH the as_global sub-block AND the per-project _reconcile call
  And a second concurrent install --global call against the SAME target still fails "install_in_progress", not merely racing on the home

Scenario: update()'s same-version no-op path is also serialized, and a second waiter re-checks freshly   # M2
  Given a target already at the same version as the installed package, no lock held
  And a second update() call that starts only after the first one already landed a NEWER package version's reconcile while holding the lock
  When the second call finally acquires the lock (after the first releases)
  Then the second call's own same-version check runs FRESH under the lock and correctly finds "already at the new version" (or correctly finds still-missing trees), never acting on a stale pre-lock read

Scenario: update --global and update --check are both unaffected by the new lock   # M2 boundary, M3 JS-only carve-out
  Given a project-scope lock is currently HELD by another process against a target
  When I run update(as_global=True) / cmdUpdateGlobal against the shared home, and separately `cmdUpdate --check` against the SAME locked target
  Then update(as_global=True)/cmdUpdateGlobal proceeds unaffected (a different resource, the shared home, never checks the project lock)
  And `--check`'s read-only report also proceeds unaffected (JS's inlined check stays before lock acquisition; Python's update() never sees --check at all)

Scenario: a stale lock (crashed holder) self-heals on the very next call   # M5
  Given <target>/.add/.install.lock exists and its mtime is older than ADD_PROJECT_LOCK_STALE_SECONDS (simulating a SIGKILL'd holder)
  When I run install() / update() against that target
  Then the stale lockfile is reclaimed (unlinked and re-created) and the run proceeds to completion (exit 0)
  And no manual deletion of the lockfile was needed

Scenario: a live, non-stale lock is NOT reclaimed — fail-fast is exact   # M5 (regression guard) + Reject install_in_progress
  Given <target>/.add/.install.lock exists and its mtime is WITHIN ADD_PROJECT_LOCK_STALE_SECONDS (a genuinely in-flight holder)
  When I run install() / update() against that target
  Then the run fails immediately with "install_in_progress" and nothing is reconciled
  And the held lockfile is left untouched (not reclaimed)

Scenario: a lock whose mtime is bogusly in the future is never treated as stale   # M5 edge case (clock-skew safe direction)
  Given <target>/.add/.install.lock exists with an mtime set AHEAD of the current clock (simulating clock skew)
  When I run install() / update() against that target
  Then the lock is NOT reclaimed (treated as live) and the run fails fast with "install_in_progress"

Scenario: a crash between lock-create and the diagnostic stamp leaves a self-healable empty lock   # M6 edge case
  Given <target>/.add/.install.lock exists, is EMPTY (0 bytes — simulating a crash before the PID/timestamp write), and its mtime is older than the staleness threshold
  When I run install() / update() against that target
  Then the empty stale lock is reclaimed exactly like a stamped one (mtime alone decides staleness)
  And no error is raised while attempting to read the (absent) diagnostic content

Scenario: the lock file is excluded from a --global-data persist snapshot   # M8
  Given install(as_global_data=True) is running and currently holds its own project-scope lock at <target>/.add/.install.lock
  When _persist_data/persistData scans <target>/.add for user-data entries to snapshot (a step that runs later in this SAME call)
  Then .install.lock is excluded from the entries list, never copied into <home>/data/<key>
  And a later --from-global-data restore into a fresh clone never plants a bogus pre-existing lock file

Scenario: both twins guarantee the same observable behavior under a simulated contention   # M9
  Given the same simulated live-lock contention applied once to the Python install()/update() call and once to the Node cmdInit/cmdUpdate call (via `node bin/cli.js`)
  When each twin's acquire attempt is contended
  Then both twins fail with the same "install_in_progress" text, having written nothing
  And a structural parity check confirms both source files carry the same acquire shape (self-heal check -> create -> stamp -> release), not just matching function names

Scenario: this task's cross-call exclusivity composes with, never duplicates, _clean_replace's own per-call crash-safety   # edge case tying the dependency relationship
  Given a single install() call holding the new project-scope lock, and a simulated crash mid-copy inside one of its _clean_replace calls
  When the call is interrupted
  Then _clean_replace's OWN self-heal (already shipped, unmodified by this task) recovers that ONE managed tree on the next call, exactly as project-scope-atomic-reconcile already guarantees
  And this task's lock is what ensures no SECOND, concurrent caller was ever racing that same _clean_replace call in the first place — the two guarantees are independent and additive, never overlapping

Scenario: no CLI flag exists for a bounded wait — contention always fails immediately, never polls   # M7
  Given a live, non-stale project-scope lock is held on a target
  When I run install() / update() against that target, with no new flag available to request a wait
  Then the call fails "install_in_progress" immediately (sub-second), never polling or blocking for any measurable duration

Scenario: every other touched function's behavior is byte-identical to before this task   # M10
  Given the full pre-task test suites for _reconcile/reconcile, _clean_replace/cleanReplaceTree, _is_user_data/isUserData, _update_lock/acquireUpdateLock, and _update_global/cmdUpdateGlobal
  When this task's new lock and its two call-site wraps are added
  Then every one of those pre-existing suites still passes unmodified
  And a source diff shows zero lines changed in any of those 5 functions' own bodies (only install()/update()/cmdInit/cmdUpdate gain the new lock-wrap, plus the one new _DATA_EXCLUDE/DATA_EXCLUDE member)
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
project-scope lock  [internal helper, no new CLI surface]
  _project_lock(add_dir: Path, *, env: Mapping | None = None) -> context manager    # Python, NEW
  acquireProjectLock(addDir, env = process.env) -> release()                        # JS twin, NEW

  ACQUIRE (mirrors the proven _update_lock/acquireUpdateLock PATTERN — a NEW, independent
  primitive; never calls into or extends either):
    env_map = os.environ if env is None else env                     # / env (JS default: process.env)
    stale_after = float(env_map.get("ADD_PROJECT_LOCK_STALE_SECONDS", 120))   # env-overridable;
                  own default, deliberately shorter than the global lock's 600s (least-sure flag A1)
    lock_path = add_dir / PROJECT_LOCK_FILE                          # PROJECT_LOCK_FILE = ".install.lock"
    add_dir.mkdir(parents=True, exist_ok=True)                       # safe/idempotent — mirrors
                                                                       # _update_lock's own home.mkdir
    try: fd = os.open(str(lock_path), O_CREAT|O_EXCL|O_WRONLY, 0o600)   # / fs.openSync(lockPath,"wx")
    except already-exists:
      age = now() - stat(lock_path).mtime          # negative age (future mtime) => never stale (sign-safe)
      if age > stale_after:
        unlink(lock_path)      # best-effort — a losing race's ENOENT/vanished-file is swallowed, not an error
        retry the create EXACTLY once
        if the retry ALSO hits already-exists: raise BlockingIOError    # -> caller maps to install_in_progress
      else:
        raise BlockingIOError    # -> "install_in_progress" — NO wait, NO poll (this task adds no
                                   #    bounded-wait mode; JS: acquireProjectLock calls
                                   #    fail("install_in_progress: ...") directly on this path)
    # acquired (fresh or reclaimed) — best-effort diagnostic stamp, NEVER read to decide staleness
    write(fd, f"{pid} {utc_iso_now()}\n")    # write errors here are swallowed — informational only
    -> on the SAME exit paths as _update_lock (success or exception): close(fd); unlink(lock_path)
       best-effort (Python: `finally` inside the contextmanager). JS: release is registered via
       process.on("exit", release) — NOT a plain try/finally — because cli.js:fail() calls
       process.exit(1) directly and would skip a finally if called from anywhere nested inside
       the guarded region (the identical, already-solved hazard acquireUpdateLock's own design
       addresses this same way).

  UNCHANGED-BY-DESIGN: the O_EXCL/"wx" create is the ONLY mutual-exclusion primitive; staleness-
  reclaim only ever decides whether to RETRY, never substitutes for it — at most one racing
  create succeeds at any instant (the identical TOCTOU-safety invariant _update_lock's own design
  already relies on).

install(target=".", ..., as_global=False, ..., env=None) -> int      # signature UNCHANGED (env
                                                                       # already existed; reused,
                                                                       # not a new parameter)
  -> AFTER the interactive block resolves target_path to its FINAL value (unchanged control flow
     up to that point), BEFORE bundled_root resolution:
     [simplification, disclosed in §0: unlike _update_global (which keeps its own bundled-root
      validation lock-free, a finer-grained optimization that matters at the global-propagation
      scale), this wrap includes bundled-root validation INSIDE the lock too — one single acquire
      point, negligible extra hold time (a few Path.exists() calls) at this smaller, per-target scale]
       add_dir = _add_dir(target_path)
       env_map = os.environ if env is None else env
       try:
         with _project_lock(add_dir, env=env_map):
           <every existing statement from bundled_root resolution through the final `return 0`,
            UNCHANGED — including the as_global sub-block, _reconcile, seed_soul_md,
            seed_gitignore, agent-pointer write, intent note, persist, restore>
       except BlockingIOError:
         return _fail(f"install_in_progress: another install/update is already running against "
                       f"{target_path} — retry shortly (remove {add_dir / PROJECT_LOCK_FILE} if stale)")

cmdInit(args)                                                          # signature UNCHANGED
  -> AFTER chosenTarget is resolved to its FINAL value (unchanged control flow up to that point),
     BEFORE `if (args.global) installGlobal(...)`:
       const addDir = path.join(chosenTarget, ".add");
       acquireProjectLock(addDir);    # registers its own process.on("exit", release) — no
                                        # explicit release()/finally needed at the call site,
                                        # mirrors acquireUpdateLock's own usage at cmdUpdateGlobal
       <every existing statement from `if (args.global) installGlobal(...)` through the
        function's end, UNCHANGED>

update(target=".", ..., as_global=False, ..., env=None) -> int        # signature UNCHANGED
  if as_global: return _update_global(...)    # UNCHANGED — a DIFFERENT target, DIFFERENT lock
  target_path = Path(target).resolve()
  add_dir = _add_dir(target_path)
  if not (add_dir / "tooling").exists() and not (add_dir / "state.json").exists():
    return _fail(...)     # UNCHANGED precondition, still lock-free
  env_map = os.environ if env is None else env
  try:
    with _project_lock(add_dir, env=env_map):
      <every existing statement from bundled_root resolution through the final `return 0`,
       UNCHANGED — including the same-version no-op early return, which a second waiter now
       re-evaluates FRESH once it acquires>
  except BlockingIOError:
    return _fail(f"install_in_progress: another install/update is already running against "
                  f"{target_path} — retry shortly (remove {add_dir / PROJECT_LOCK_FILE} if stale)")

cmdUpdate(args)
  if (args.global) return cmdUpdateGlobal(args);    # UNCHANGED
  const target = ...; const addDir = ...;
  if (!fs.existsSync(...)) fail(...);                 # UNCHANGED precondition, still lock-free
  if (args.check) { <UNCHANGED check-only report>; return; }   # UNCHANGED, stays BEFORE the lock
                                                                  # (JS-only carve-out — see §0/M3)
  acquireProjectLock(addDir);
  <every existing statement from the same-version no-op check through the function's end,
   UNCHANGED>

# ── new constant, both twins ──
PROJECT_LOCK_FILE = ".install.lock"     # add_dir / PROJECT_LOCK_FILE — NEVER user-data (see below)

# ── _DATA_EXCLUDE / DATA_EXCLUDE — ONE new exact-name member ──
_DATA_EXCLUDE = {"tooling", "docs", ".update-cache", STAMP_FILE, LOCK_FILE, PROJECT_LOCK_FILE}
DATA_EXCLUDE  = ["tooling", "docs", ".update-cache", STAMP_FILE, LOCK_FILE, PROJECT_LOCK_FILE]
  # mirrors LOCK_FILE's own existing membership — _persist_data/persistData's scan of
  # <target>/.add's top-level entries never snapshots a currently-held or stale lock file.

# ── Reject code (ONE new code) ──
install_in_progress   fires from: install()/cmdInit AND update()/cmdUpdate's non-global path, on
                      a LIVE (non-stale) contended project lock — no wait, no poll, nothing
                      written. Distinct from the EXISTING update_in_progress (a different
                      resource: this project's own .add/ tree, never the shared home).

Schema / files touched:
  <target>/.add/.install.lock   NEW transient file. Content: empty momentarily after create, then
                                 "<PID> <UTC ISO ts>\n" once the diagnostic stamp lands — purely
                                 informational, mtime is the ONLY staleness signal. Excluded from
                                 _is_user_data/isUserData scans via the ONE new _DATA_EXCLUDE/
                                 DATA_EXCLUDE member above. Never present as steady state — exists
                                 only for the duration of one held install()/update() call, or
                                 between an abnormal termination and the next call's self-heal.
  No new dependency (stdlib os/time/tempfile · Node builtin fs/path only). No new CLI flag.

INV: the O_EXCL ("wx") create is the SOLE mutual-exclusion primitive for this NEW lock, exactly as
     for _update_lock/acquireUpdateLock — staleness-reclaim only ever decides WHETHER to retry
     that create, never grants the lock by any other means.
INV: this lock is entirely INDEPENDENT of _update_lock/acquireUpdateLock — different function,
     different file, different default threshold, zero shared code — by DELIBERATE design (§1
     Framings weighed), not an oversight. A future decision to unify them is a new contract, not a
     natural evolution of this one.
INV: a project-scope lock is ALWAYS acquired before, never nested inside, any home-scoped lock
     acquisition for the SAME call — global-lock-followups's own install(as_global=True) home-lock
     wrap has SINCE merged (commit 7396456; §0 Issue/Risk #5 upgraded from forward-looking to a
     live, checked invariant) — confirmed to sit inside the as_global sub-block, which this task's
     M1 whole-function wrap will correctly nest OUTSIDE of. Verify at build time with a real test,
     not by re-reading this note.
INV: `_reconcile`/`reconcile`, `_clean_replace`/`cleanReplaceTree`, `_is_user_data`/`isUserData`
     (beyond the one new exact-name member), `_update_lock`/`acquireUpdateLock`,
     `_update_global`/`cmdUpdateGlobal` are BYTE-IDENTICAL to before this task.
INV: both twins guarantee the SAME state machine (self-heal-check -> create -> stamp -> release)
     via each platform's own primitives (os.open/os.stat/os.unlink vs fs.openSync/fs.statSync/
     fs.unlinkSync) — the OBSERVABLE guarantee is frozen, not the literal syscalls (mirrors the
     _update_lock/acquireUpdateLock and _clean_replace/cleanReplaceTree precedent, CONVENTIONS.md
     fv59, "folded foundation-version 59").

OUT of scope (named, not silently dropped):
  - A bounded-wait / CI-timeout mode for the project-scope lock (symmetry with
    global-lock-followups's own --lock-timeout) — considered and DECLINED (§1 Framings weighed,
    Assumption A4), a disclosed non-goal, not an oversight; a cheap additive follow-up if wanted.
  - Unifying this lock with _update_lock/acquireUpdateLock into one shared primitive — considered
    and DECLINED (§1 Framings weighed, Assumption A2); a legitimate future redesign, not something
    this task's shape blocks.
  - prune_data's own concurrency, _persist_data/_restore_data's own crash-safety hardening,
    _clean_replace/cleanReplaceTree's own crash-safety — all owned by sibling tasks (named in
    their own contracts), untouched here.
  - PID-liveness dead-holder detection — not portable (the same Windows os.kill(pid,0) hazard
    global-lock-followups already found); mtime-age is the only staleness signal, exactly as there.
```

Glossary deltas: none (this task introduces a new internal mechanism and one machine-readable
  reject code — "project lock" / "install_in_progress" stay internal code vocabulary, not
  GLOSSARY.md domain terms; matches both sibling tasks' own "none" precedent for a hardening/
  mechanism-only task).

Least-sure flag surfaced at freeze:
  ⚠ [spec] A2 — the reuse-vs-new-primitive architectural fork (an independent lock vs. extending
    `_update_lock`/`acquireUpdateLock`) is a genuine, either-way-defensible choice. This draft
    chooses independence to avoid coupling to `global-lock-followups`'s still-unmerged shape and
    to fit a different threat model (shorter expected hold duration, no wait-mode need), but a
    human who values ONE unified lock implementation over independent mergeability could
    reasonably choose the other path. Cost if wrong: a moderate (not full) redesign — the
    OBSERVABLE guarantees (M1-M9) stay the same, only the internal call-site/shared-vs-separate-
    function question changes, and it would introduce the merge-order dependency this draft
    currently avoids.
  Second flag: [spec] A1 — `ADD_PROJECT_LOCK_STALE_SECONDS`'s proposed default (120s, deliberately
    shorter than the global lock's own 600s, reasoned from project-scope's typically-brief
    reconcile duration) has no production timing data behind it — the same calibration gap
    `global-lock-followups` itself already disclosed for its own threshold. Cheap to change (one
    constant) if wrong.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 16 §2 scenarios + the M11 lock-ordering invariant (an explicit ask
  in §0/§3, not one of the 16 gherkin scenarios) + 1 bonus TOCTOU concurrency test — 26 test
  methods total. Confirmed RED: 16 fail for a genuine missing-implementation reason (an
  AttributeError on the new `_project_lock`/`PROJECT_LOCK_FILE` symbols, or the OLD, lock-less
  `install()`/`update()` correctly ignoring a pre-existing/held lock file it doesn't check for
  yet). The other 10 are honest baseline/regression guards (the uncontended happy path, the
  disclosed --global/--check unaffectedness, the empty-lock read-safety edge case, the
  reconcile-crash composition, 2 of the 3 M11 tests) — already true pre-build by construction
  and must STAY true post-build; mirrors `global-lock-followups`' own precedent of disclosing
  "N legitimate regression guards already green pre-build" rather than forcing an artificial
  failure into a test whose scenario is inherently a not-yet-affected boundary.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_fresh_uncontended_install_releases_lock_transparently: arrange a target with no project yet, no lock held / act install() / assert exit 0 + tooling materialized + .install.lock absent after · covers: M1 (baseline; green pre-build)
  - test_two_concurrent_installs_one_proceeds_one_fails_cleanly: arrange a fresh target, hold the project lock directly / act install() while held, then again once released / assert the first fails "install_in_progress" with nothing written, the second succeeds · covers: M1, M4, Reject
  - test_two_concurrent_updates_one_proceeds_one_fails_cleanly: arrange an existing project with docs deleted (sentinel), hold the lock / act update() while held, then again once released / assert the first fails with nothing reconciled, the second reconciles · covers: M2, M4, Reject
  - test_lock_keys_on_final_post_prompt_target_not_initial_arg: arrange a forced-interactive install() whose mocked _prompt_target redirects X->Y / act install(target=X) / assert installed into Y not X, a 2nd call redirected to Y contends when Y (not X) is locked, and locking X never blocks a call keyed on Y · covers: M1 edge case
  - test_install_global_still_locks_the_per_project_drop: arrange a fresh target / act install(as_global=True) once (uncontended), then again with the project lock held / assert the per-project drop still ran, and the 2nd call contends on the PROJECT lock (registry touched exactly once) · covers: M1
  - test_update_same_version_noop_is_locked_and_rechecked_fresh: arrange an existing same-version project, hold the lock / act update() while held, then again once released / assert the first fails, the second's no-op re-check runs fresh and releases the lock · covers: M2
  - test_update_global_unaffected_by_a_held_project_lock + test_npm_check_unaffected_by_a_held_project_lock: arrange a held project lock on a registered project / act update(as_global=True) [pip] and `cmdUpdate --check` [node] / assert both proceed unaffected (a different resource / a carve-out that stays before the lock) · covers: M2 boundary, M3 JS-only carve-out (both green pre-build; disclosed)
  - test_stale_project_lock_self_heals: arrange a backdated (stale) lock + a deleted docs sentinel / act update() with a tiny stale threshold / assert self-healed, run completes, lock gone after · covers: M5
  - test_live_project_lock_not_reclaimed_fails_fast: arrange a fresh (age 0) lock / act update() / assert fails fast, lock left untouched · covers: M5 regression, Reject
  - test_future_mtime_project_lock_never_stale: arrange a lock with mtime an hour in the future / act update() with a tiny threshold / assert NOT reclaimed, fails fast · covers: M5 edge case
  - test_crash_before_stamp_leaves_self_healable_empty_lock: arrange a 0-byte stale lock / act update() / assert reclaimed exactly like a stamped one, no error · covers: M6 edge case (green pre-build; disclosed)
  - test_is_user_data_excludes_the_project_lock_by_name + test_lock_file_excluded_from_a_global_data_persist_snapshot: arrange real user-data + a live project lock during install(as_global_data=True) / act persist / assert the lock file is never snapshotted · covers: M8
  - test_parity_surface + test_npm_fresh_install_unaffected + test_npm_contended_install_fails_fast + test_npm_stale_project_lock_self_heals: arrange source reads + real `node cli.js` subprocess runs (fresh / contended / stale) / assert both twins define the same call-site shape and observably behave the same · covers: M9
  - test_lock_release_is_independent_of_a_reconcile_crash: arrange a mocked _reconcile that raises mid-call / act install() / assert the exception propagates, the lock still releases, and a subsequent call is not wedged · covers: edge case tying the _clean_replace-crash-safety composition (green pre-build; disclosed)
  - test_contention_always_fails_immediately_never_polls: arrange a held lock / act update(), timed / assert fails in well under a second — no poll, no wait · covers: M7
  - test_untouched_lock_and_reconcile_call_sites_are_unchanged + test_is_user_data_baseline_and_new_exclusion: arrange a source read + direct _is_user_data calls / assert the 5 named unchanged functions/call-sites are untouched and ordinary user-data classification is unaffected · covers: M10
  - test_project_lock_blocks_before_the_home_lock_is_ever_touched: arrange the PROJECT lock held (home free) / act install(as_global=True) / assert fails "install_in_progress" (not update_in_progress), the home lock/stamp were never created · covers: M11 (own required test, not a named §2 scenario)
  - test_home_lock_contention_surfaces_independently_when_project_lock_is_free: arrange the HOME lock held (project free) / act install(as_global=True) on a 2nd target / assert fails "update_in_progress" (not install_in_progress), and the outer project lock still released cleanly despite the inner failure · covers: M11 (green pre-build — the pre-existing home lock's own contention is unaffected either way)
  - test_fresh_install_global_releases_both_locks_no_deadlock: arrange no locks held / act install(as_global=True), timed / assert success, both lock files absent after, no deadlock · covers: M11 (green pre-build — only one lock exists today)
  - test_concurrent_stale_reclaim_exactly_one_wins: arrange a stale lock + 6 Barrier-synced threads calling _project_lock directly / act release all racers concurrently / assert exactly one "acquired", zero unexpected exceptions, no leaked lock file · covers: M4/M5 TOCTOU safety (bonus, beyond the 16 named scenarios)
</test_plan>

Tests live in: `add-method/tooling/test_project_scope_lock.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/bin/cli.js` `add-method/tooling/test_project_scope_lock.py`
Strategy (ordered batches): 1. Add `PROJECT_LOCK_FILE = ".install.lock"` (both twins, near `LOCK_FILE`/`STAMP_FILE`); add it as a new exact-name member of `_DATA_EXCLUDE`/`DATA_EXCLUDE`. 2. Python: `import time` (new stdlib import); write `_project_lock(add_dir: Path, *, env: Mapping | None = None)` as a NEW `@contextlib.contextmanager`, placed near `_update_lock` for discoverability (not shared code) — self-heal-check (stat + sign-aware age compare) -> `os.open(O_CREAT|O_EXCL|O_WRONLY)` (retry once after an unlink on a confirmed-stale contention) -> best-effort diagnostic stamp write -> `yield` -> `finally: close + unlink best-effort`. 3. JS: write `acquireProjectLock(addDir, env = process.env)` as a NEW function near `acquireUpdateLock` — identical self-heal-check -> `fs.openSync(path,"wx")` (retry once) -> best-effort stamp write -> register `process.on("exit", release)` -> return `release`; on a live contention, call `fail("install_in_progress: ...")` directly (mirrors `acquireUpdateLock`'s own precedent). 4. Python `install()`: compute `add_dir`/`env_map` right after the interactive block resolves `target_path`'s FINAL value; wrap everything from `bundled_root` resolution through the final `return 0` in `with _project_lock(add_dir, env=env_map):`, `except BlockingIOError: return _fail("install_in_progress: ...")` immediately outside it (mirrors `_update_global`'s own try/with/except shape) — re-indentation only, no line inside the wrap changes. 5. Python `update()`: after the existing "no ADD project" precondition, wrap the same way (including the same-version no-op branch). 6. JS `cmdInit`: after `chosenTarget` is final, call `acquireProjectLock(addDir)` before `if (args.global) installGlobal(...)` — no re-indentation needed (exit-hook release, not scope-based). 7. JS `cmdUpdate`: call `acquireProjectLock(addDir)` AFTER the existing `if (args.check) {...; return;}` early return, before the same-version no-op check — ordering matters (see Known-problem fixes). 8. Grep both files afterward to confirm `_reconcile`/`reconcile`, `_clean_replace`/`cleanReplaceTree`, `_update_lock`/`acquireUpdateLock`, `_update_global`/`cmdUpdateGlobal` remain byte-unchanged and no other call site was touched.

Persona (optional): methodology-engine-dev (same persona both sibling tasks in this milestone used — nominally scoped to `add.py`/`add_engine/*`, adapted-fit for the installer; see §0 Honors)
Known-problem fixes: `cli.js:fail()` calls `process.exit(1)` directly, skipping any pending `finally` -> `acquireProjectLock`'s release MUST be wired via `process.on("exit", release)`, never a plain try/finally at the call site (mirrors `acquireUpdateLock`'s own already-solved precedent) — a plain try/finally would silently fail to release the lock whenever a nested call (`installGlobal`, `cleanReplaceTree`, etc.) invokes `fail()` · JS's `cmdUpdate` inlines its `--check` early return WITHIN the function my lock wraps — the lock acquisition line must be placed AFTER that early return, never before it, or a purely read-only `--check` invocation would needlessly contend for (and potentially fail on) a lock it has no reason to touch; Python's `update()` has no equivalent hazard (its `--check` is the fully separate, never-locking `update_check()`) · a portable PID-liveness check does not exist (Windows `os.kill(pid,0)` can terminate rather than merely probe — the same hazard `global-lock-followups` already found) -> mtime-age is the only staleness signal, never PID · clock skew making a live lock look stale -> only reclaim when `age > threshold` (a future/bogus mtime never counts as stale) · `install()`'s interactive flow can reassign `target_path` -> the lock's `add_dir` must be computed AFTER that reassignment settles, never before it · the new `_DATA_EXCLUDE`/`DATA_EXCLUDE` member must be the lock file's own literal exact name (`.install.lock`), not a `.add-tmp-`/`.add-bak-`-style prefix pattern (that convention belongs to a different, not-yet-built sibling mechanism and doesn't apply to this fixed-name file).
Strategy actually used: AS PLANNED, in the same 8-step batch order (constants -> Python `_project_lock` -> JS `acquireProjectLock` -> `install()` wrap -> `update()` wrap -> `cmdInit` wire -> `cmdUpdate` wire -> grep-confirm the 5 named untouched call sites stayed byte-identical), with the §4 RED suite (26 tests) written and committed FIRST as its own commit (`4682b00`), confirmed 16/26 failing for the traced right reason (an AttributeError on the not-yet-existing `_project_lock`/`PROJECT_LOCK_FILE` symbols, or the OLD lock-less `install()`/`update()` correctly not noticing a pre-existing/held lock file it doesn't check for yet) before any implementation line — the same TDD discipline both sibling tasks in this milestone followed.
  One refinement, found via the BROADER regression sweep (my own new suite was green start-to-finish once each batch landed — this was never one of the 16 red tests; it only surfaced once I swept siblings beyond this task's own declared Scope): 2 PRE-EXISTING regression-guard tests — `test_global_install.py::GlobalInstallTest::test_home_unwritable_fails` and
  `test_global_update_harden.py::InstallGlobalLockTest::test_install_global_blocked_by_a_held_lock`
  — regressed. Both assert `.add/` does not exist AT ALL after an `as_global` failure that aborts
  BEFORE the per-project drop (an unwritable home; a held home lock). Root cause: `_project_lock`/
  `acquireProjectLock` must `mkdir` `add_dir` (`.add/`) so its own O_EXCL/`"wx"` sentinel file has
  somewhere to live, and M11 requires the project lock to wrap `install()`'s ENTIRE call —
  including the `as_global` sub-block — so on a virgin target that `mkdir` now runs BEFORE the
  `as_global` sub-block's own failure point, leaving a new, empty `.add/` behind where nothing
  used to be written. Neither test was in this task's declared Scope, and weakening either was
  never considered — both are exactly the class of pre-existing regression-guard the broader
  sweep exists to protect (an almost identical `test_home_unwritable_fails` interaction is
  independently documented in this milestone's OWN sibling task `global-lock-followups`'s own §5,
  a different code path, the same test, the same root class of "an as_global sub-block failure
  must leave the target exactly as untouched as before").
  Fixed entirely in my own new lock code, in NEITHER test: `_project_lock`/`acquireProjectLock`
  now track whether THIS call is the one that froze `add_dir` into existence (`created_dir` in
  Python / `createdDir` in JS — an existence check taken immediately before the `mkdir`); on
  release (every exit path: success, an internal raise/throw, or an early return/`fail()` from the
  caller's own guarded span), if `created_dir` is true AND `add_dir` is now completely empty (the
  lock file was its only occupant — nothing else ever landed before the failure), the directory is
  removed again. A non-empty `add_dir` (the real managed-layer drop landed, or the directory
  pre-existed for any unrelated reason) is NEVER touched: `Path.rmdir()`/`fs.rmdirSync()` only
  ever succeed on a genuinely empty directory, so the fix is safe by construction, not by trying to
  distinguish success from failure at the call site (which a `@contextlib.contextmanager` generator
  cannot actually do for a plain `return` inside the caller's `with`-block — the fix does not
  attempt to; the empty-directory check is correct regardless of why the call ended early).
  Verified in 3 layers: (1) both previously-failing tests pass standalone, same test identity,
  before(red)/after(green); (2) the full 26-test `test_project_scope_lock.py` suite plus all 14
  OTHER sibling installer/lock/restore tooling test files (231 tests total, run from within
  `add-method/tooling/`) all green — 3 of those 15 files (`test_setup_lock.py`,
  `test_installer_prompts.py`, `test_status_lock_hint.py`) import a bare `add`/`engine_pin` and
  only resolve from that cwd, a PRE-EXISTING, unrelated-to-this-task invocation convention
  independently confirmed via a `git stash`-based baseline diff (the identical 3-file ImportError
  reproduces byte-for-byte with my 2 changed files stashed out); (3) `add.py check`'s own tripwire
  (509 passed, 0 failed — unchanged) confirms neither the frozen contract nor
  `test_project_scope_lock.py` (MD5-verified byte-identical to the tests->build tripwire snapshot,
  `a25cfce670bcb87b66eb07d2a7e7fc60`) was touched to arrive at this fix — the change is 100%
  confined to `_project_lock`/`acquireProjectLock`'s own bodies, both already within the declared
  Scope. `git diff`'s own hunk CONTENT (not just its nearest-function header, which git anchors to
  the closest PRECEDING signature even for a pure insertion) independently confirms `_update_lock`/
  `acquireUpdateLock`/`_update_global`/`cmdUpdateGlobal`/`_reconcile`/`reconcile` stayed
  byte-identical — the constants-block and new-function hunks are ADDITIVE-ONLY next to those
  names, never a line inside them (M10).
  Order: RED committed first (`4682b00`) -> constants + `_project_lock` + `acquireProjectLock` ->
  `install()`/`update()` wraps -> `cmdInit`/`cmdUpdate` wiring -> own-suite GREEN (26/26) -> the
  broader sweep surfaced the 2 regressions above -> the empty-dir cleanup fix (both twins) -> full
  re-sweep GREEN (231/231, own suite included) -> this fill.
  Second build attempt (2026-07-03, reopened to `build` via `add.py heal` after an independent
  verify pass found a LIVE TOCTOU race in this lock's stale-reclaim path — §6's own Advisor 3-lens
  HARD-STOP finding, left as-is below for the next verify pass): the reclaim's
  `os.unlink(lock_path)` was unconditional and identity-blind — it removed whatever currently sat
  at the path with no check that it was still the SAME stale file just inspected, letting 2+
  racers hold "the lock" simultaneously. Reproduced pre-fix at 7/30 (23.3%) against my own
  strengthened test below (same family as the original verify pass's own larger-sample 66/250,
  26.4%). TDD followed exactly: the test change landed FIRST, alone, confirmed red against the
  untouched buggy code (7/30) before any implementation line changed.
    Fix shape deviated from this reopening's own suggested pattern TWICE, each time for a concrete,
  empirically-proven reason (re-derived from the actual code, not the paraphrase): (1) "rename to a
  per-attempt quarantine name" (mirroring this codebase's own `_persist_data` idiom) was tried
  FIRST and made the race MEASURABLY WORSE — 16/30 (53%), up from the 7/30 baseline. Root cause,
  proved via an instrumented standalone reproduction: a rename is JUST as identity-blind as an
  unlink — it operates on whatever currently sits at the shared path, so a delayed racer's rename
  steals an already-recreated WINNER's fresh file exactly as easily as the original unlink could,
  and the extra syscall widens the vulnerable window rather than closing it. Abandoned; not present
  in the final code. (2) Redesigned to a "ticket-gated reclaim": an EXCLUSIVE, per-generation
  ticket file keyed to the stale file's own inode number (`st_ino` — confirmed empirically
  non-reused immediately after unlink+recreate on this filesystem) gates entry to the reclaim
  itself; a losing racer never touches `lock_path` at all. This improved the rate to 1/30 (3.3%)
  but did not fully close it — direct instrumentation of the real function (temporary
  `_DIAG_TRACE`-gated trace prints, since fully removed: `grep -rn "_DIAG_TRACE" add-method/` is
  zero hits) caught the residual live: winning the ticket proves exclusive rights to reclaim ONE
  specific generation, but not that `lock_path` is STILL that generation by the time the code acts
  on it — a scheduling gap can let the SAME path fully cycle through an entire, unrelated reclaim
  in the interim, and the ticket-winner's unconditional unlink then blindly destroys that
  unrelated, currently-live holder's file. Final fix (delivered): after winning the ticket, re-stat
  `lock_path` IMMEDIATELY before unlinking and compare its CURRENT inode against the ticket's
  inode; unlink ONLY on a match, otherwise treat the ticket as moot and leave the (unrelated, live)
  file alone — one extra syscall that shrinks the window from an arbitrary scheduling delay down to
  the gap between two adjacent syscalls (a residual now bounded by needing TWO independent,
  unrelated parties to both act inside that sub-microsecond gap — judged acceptable and disclosed,
  not further reducible with only cross-platform stdlib/builtin primitives). Applied independently
  in `_project_lock` and its own JS twin `acquireProjectLock` — no shared helper introduced between
  them or with `_update_lock`/`acquireUpdateLock` (the frozen contract's own INV honored); the
  sibling task `global-lock-followups` carries the identical fix shape for its own pair,
  independently applied and independently proven (its own §5).
    Test strengthening (this reopening's other half): the test's OWN assertion was part of the
  gap — a cumulative `results.count("acquired") == 1` cannot distinguish "at most one holder at
  any INSTANT" (the real invariant) from racers legitimately, sequentially re-acquiring one after
  another (normal, correct behavior). Replaced with a temporal proof: an `active` counter
  incremented the instant a racer is inside the critical section and decremented the instant
  before it leaves, `peak = max(peak, active)` latched under the same lock guarding the shared
  `results` list — `peak` can only exceed 1 on a genuine simultaneous-holder bug. Note for the
  record (a scope observation, not a decision): `test_project_scope_lock.py` is not named on this
  section's own "Scope (may touch)" line above, even though it IS the §4-declared suite for this
  same, already-named `test_concurrent_stale_reclaim_exactly_one_wins` scenario ("bonus… M4/M5
  TOCTOU safety") — this build only strengthened that existing test's assertion rigor, added no
  new test, and did so on this reopening's own explicit instruction.
    Stress evidence: the strengthened test run repeatedly after the final fix — 0/30, then 0/60
  more (0/90 total, 0 failures). The full sibling regression sweep (`test_global_install` +
  `test_global_update_harden` + `test_global_restore` + `test_global_data` + `test_reconcile_rollup`
  + `test_project_scope_lock`, 145 tests, run together from `add-method/tooling/`) was run 4 times
  after the final fix — 145/145 every time; the dedicated `test_project_scope_lock.py` suite is
  26/26 standalone. All temporary diagnostic tracing has been removed from the delivered code (none
  was added to this task's own function during this build; the sibling task's function is the one
  that briefly carried it during diagnosis, also since removed).
    Disclosed residual (found during my own self-review, not by a failing test): the final fix's
  identity check compares inode NUMBERS (`st_ino`), which is sound only as long as the filesystem
  does not reuse an inode number for an unrelated new file inside the tiny re-stat-to-unlink window.
  Empirically ruled out on THIS session's test filesystem (macOS/APFS — a tight create/unlink loop
  showed strictly sequential, never-reused inode allocation), and `st_ino` is meaningful (not always
  0) on Linux and on modern Windows/NTFS (Python's `os.stat`/Node's `fs.Stat` both surface the real
  NTFS File ID there) — but this build's 90-per-lock stress validation ran on macOS/APFS ONLY;
  Linux/Windows behavior is assumed-correct by the documented API contract, not independently
  re-verified in this session. Same disclosed-not-hidden category as the sub-syscall race noted
  above, not a known live bug — flagged for the next verify pass to weigh, not decided here.
  Third build attempt (2026-07-03, reopened for this same still-`build`-phase task after a fresh
  adversarial verify pass — building external-state repro scripts against the real, unmodified
  code rather than trusting the ticket mechanism's own comments — found and empirically confirmed
  a LEAKED-TICKET WEDGE: `_project_lock`'s own per-generation reclaim ticket
  (`<add_dir>/.install.lock.reclaim-<inode>`) can itself be leaked by a crash landing between a
  winner's ticket-open and its own `finally: os.unlink(ticket_path)` a few lines later. Because
  the ticket's name is deterministically keyed to the STALE MAIN LOCK's own (unchanging) inode,
  and this lock's own reclaim never mutates that inode unless it actually wins the ticket, a
  leaked ticket makes EVERY future contender recompute the IDENTICAL ticket path, lose the
  identical EEXIST race, and — pre-fix — immediately `raise BlockingIOError(...) from None` (this
  lock never polls, M7) — "install_in_progress" forever, with no manual recourse short of deleting
  both files by hand. Independently re-derived by tracing the actual current code (not accepting
  the finding's own paraphrase): confirmed via a direct `_project_lock()` call against a
  synthetically-leaked ticket (a stale main lock + an orphaned `.reclaim-<inode>` sibling with no
  corresponding live process) — reproduced as an uncaught `BlockingIOError` against the untouched
  pre-fix code, every single call, no matter how many times retried.
    Fix: apply the SAME age-based staleness check already governing the main lock to the ticket
  file too — before treating a lost ticket-open as "someone else legitimately owns this reclaim,"
  first stat the EXISTING ticket; if its own age exceeds a threshold, self-heal it and retry the
  ticket-open exactly once (mirroring this lock's own existing "one extra attempt, never a
  second, never a poll" ethos, M7). Chose a SEPARATE, independently-defined, much SHORTER
  threshold for the ticket (`_PROJECT_LOCK_TICKET_STALE_SECONDS`/`PROJECT_LOCK_TICKET_STALE_SECONDS`
  = 5s, own module-level constant per twin, not env-overridable) rather than reusing
  `stale_after`/`ADD_PROJECT_LOCK_STALE_SECONDS` (120s default) outright — reasoned explicitly, not
  assumed: a ticket's own critical section is a small, FIXED handful of syscalls
  (close/stat/maybe-unlink/unlink), microseconds under normal operation regardless of which lock
  it guards, so a multi-second margin is already generous; reusing the main lock's own much longer
  threshold would still be SAFE (never a false-positive reclaim of a genuinely in-flight ticket)
  but would needlessly delay recovery from a real crash by up to 120s for no benefit. Considered,
  and explicitly REJECTED, a simpler "unconditional unlink-by-path if the ticket looks old, then
  retry the create" shortcut at the ticket level: worked through it by hand and found it REOPENS
  THE IDENTICAL TOCTOU HOLE ONE LEVEL DOWN — if a THIRD racer's legitimately fresh ticket (for the
  SAME generation) is created in the gap between our stat-check and our unlink, an unconditional
  unlink would destroy it, letting BOTH racers believe they are the sole reclaimer of the same
  stale main-lock generation, exactly the double-hold bug this whole ticket mechanism exists to
  prevent. Applied the IDENTICAL identity-verified discipline instead (re-stat the ticket
  IMMEDIATELY before unlinking it and compare its inode to the one just observed stale; unlink
  only on a match) — the same shape as the main lock's own already-proven fix, recursed one level,
  never a shortcut.
    A second, independent defect surfaced while tracing this lock's own sibling
  (`_update_lock`/`acquireUpdateLock`, owned by `global-lock-followups`, not this task's own
  Scope): because that lock LOOPS (it supports `--lock-timeout`), the identical leaked-ticket
  condition manifests there as an UNBOUNDED LIVELOCK, not a clean fail-fast wedge — both the
  "lost the ticket" and "won the ticket" branches unconditionally `continue`d back to the top of
  its `while fd is None:` loop, pre-fix, without ever reaching the `deadline`/`--lock-timeout`
  check beneath the `if age > stale_after:` block. That task's own TASK.md carries the matching
  fix and evidence for its own function; noted here only because both locks share the SAME root
  cause (independently discovered, independently fixed, zero shared code between them — this
  task's own §1/§3 "zero shared code" invariant, re-affirmed, not violated by fixing both in the
  same session).
    Also extended `_is_user_data`/`isUserData` (both twins) with a new `.reclaim-` infix
  exclusion — mirrors the EXISTING `.add-tmp-`/`.add-bak-` infix convention already in the same
  function — so a leaked (or merely transiently-live, mid-reclaim) ticket sibling inside a
  scanned `<target>/.add/` tree is never bogusly snapshotted by `_persist_data`/`persistData` as
  user-data, closing the exact class of gap `_DATA_EXCLUDE`'s own exact-name `PROJECT_LOCK_FILE`
  membership (M8, already shipped) exists to prevent for the main lock file itself.
    TDD followed exactly: both new regression tests (the direct-mechanism leaked-ticket test and
  the full `install()`/`update()`-level test) were written FIRST and confirmed RED against the
  UNTOUCHED pre-fix code via a scoped `git stash push -- _installer.py cli.js` (stashing ONLY the
  2 source files, keeping the new tests) — the direct-mechanism test errored with an uncaught
  `BlockingIOError` (the exact wedge symptom) and the full-call test asserted `install_in_progress`
  instead of exit 0, both for the traced reason, not a broken harness; the `node cli.js` twin
  reproduced the identical wedge as a real subprocess. `git stash pop` restored the fix; the SAME
  4 new tests (2 above + a fresh-ticket-is-never-reclaimed regression guard + the npm parity
  smoke) then ran GREEN (7/7 including the sibling task's own 3, in 1.7s — versus needing the
  full bounded timeout budgets to even finish failing, pre-fix).
    Stress evidence (this redo): the EXISTING `test_concurrent_stale_reclaim_exactly_one_wins`
  (proving the ORIGINAL multi-racer TOCTOU race stays fixed) was re-run, in fresh subprocesses,
  30 times then 60 more (90/90 total, 0 failures) — confirms this ticket-level self-heal addition
  did not reintroduce that already-fixed race. The dedicated suite is 30/30 (26 prior + 4 new);
  the 6-file sibling sweep (`test_global_install`/`test_global_update_harden`/`test_global_restore`
  /`test_global_data`/`test_reconcile_rollup`/`test_project_scope_lock`, 152 tests) is 152/152.
Safety rule (feature-specific): the O_EXCL/`"wx"` create stays the SOLE mutual-exclusion primitive at every layer — staleness-reclaim only ever decides whether/when to retry that create, never grants the lock by any other means (identical in spirit to `_update_lock`'s own safety rule, independently restated for this new, separate primitive).
Code lives in: `add-method/` (the package — NOT this task's `./src/`).
Constraints: do NOT change any test or the contract; no new dependency (stdlib `os`/`time`/`tempfile` · Node builtin `fs`/`path` only); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_project_scope_lock.py`: 26/26 green. Broader targeted regression
      sweep (all 14 OTHER sibling installer/lock/restore tooling files, run from within
      `add-method/tooling/` per their own native cwd convention — see Strategy actually used):
      231/231 green (this task's own 26 included). NOT run: the full ~2500-test repo suite (per
      this repo's own standing lesson: too long for a synchronous foreground run; this targeted
      sweep is the evidence offered here, full-suite confirmation defers to CI-on-push).
- [x] coverage did not decrease — 26 new test methods added in a brand-new file (nothing
      pre-existing to weaken); all 14 sibling files' pre-existing tests pass unmodified (0
      removed, 0 weakened — confirmed via `git diff`: no test file appears in the build-phase
      diff, only `_installer.py`/`cli.js`); all 16 §2 scenarios + M11 + 1 bonus TOCTOU test
      covered (§4 test_plan maps each by name).
- [x] no test or contract was altered during build — `git diff` since the RED commit (`4682b00`)
      touches only `add-method/src/add_method/_installer.py` + `add-method/bin/cli.js` (plus the
      engine-managed `.add/state.json` phase marker+tripwire and this file's own phase-marker
      line — both expected, neither a content edit to §0-§3); `test_project_scope_lock.py`'s MD5
      (`a25cfce670bcb87b66eb07d2a7e7fc60`) is byte-identical to the tests->build tripwire
      snapshot recorded in state.json; §0-§3 remain byte-identical to the FROZEN @ v1 bundle
      (only §4/§5/§6 were ever filled, never frozen).
- [ ] the green was EARNED, not gamed — LEFT for independent verify (not self-graded; see the
      Refute-read verdict section below, deliberately left blank — build-phase, not mine to fill).
- [ ] concurrency / timing of the risky operation is safe — LEFT for independent verify by design
      (this task's own STOP-and-escalate criteria names concurrency/timing judgment as an
      escalation, not a self-certification). Evidence offered, not a verdict:
      `ProjectLockConcurrencySafetyTest::test_concurrent_stale_reclaim_exactly_one_wins` (a
      6-thread Barrier-synced race directly against `_project_lock` — exactly one "acquired",
      zero unexpected exceptions, no leaked lock file) plus `LockOrderingInvariantTest`'s 3 tests
      exercising `install(as_global=True)` with BOTH locks live via REAL execution (not a static
      source read) for M11. Same disclosed scope limit as `global-lock-followups`'s own
      precedent: in-process multi-threading against real OS syscalls, not genuine multi-process
      races — named here, not silently assumed equivalent.
- [x] no exposed secrets, injection openings, or unexpected dependencies — no credential/secret
      strings introduced (grepped my own diff); zero new package.json/pyproject.toml dependency
      entries; the Python addition uses only already-imported stdlib (`os`/`time`/`contextlib`,
      confirmed all 3 pre-date this task — no new `import` line added); the JS addition uses only
      already-imported Node builtins (`fs`/`path`, no new `require`).
- [x] layering & dependencies follow CONVENTIONS.md — O_EXCL/`"wx"` remains the SOLE
      mutual-exclusion primitive at every layer (no `fcntl.flock`; no PID-liveness check —
      mtime-age only, per the non-portable-PID hazard both this task's own §0 Honors and
      `global-lock-followups` already named); the empty-dir cleanup fix added during build uses
      only `Path.rmdir()`/`fs.rmdirSync()`, both already-used stdlib/builtin primitives elsewhere
      in the same 2 files.
- [ ] a person reviewed and approved the change — NOT YET; pending human review (this task's
      autonomy: auto still routes the final GATE RECORD to a human per the template's own design).

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a live-held project lock makes a SECOND concurrent `install()`/`update()` call against the
      SAME target fail immediately with `install_in_progress` and write NOTHING (no managed-layer
      drop, no lock-file residue) — confirmed by `ConcurrentInstallTest`/`ConcurrentUpdateTest`
      (exit code + explicit filesystem-absence assertions, not just the reject string) and
      `LockOrderingInvariantTest::test_project_lock_blocks_before_the_home_lock_is_ever_touched`
- [x] a stale project lock (age > threshold, default 120s) self-heals transparently — the very
      next call reclaims it and completes normally, no manual deletion — confirmed by
      `StaleProjectLockSelfHealTest` (Python) and a REAL `node cli.js` subprocess in
      `TwinParityTest::test_npm_stale_project_lock_self_heals`
- [x] M11: the project lock is ALWAYS acquired before, never nested inside, the home-scoped lock
      for the same call — confirmed by REAL execution (not a static source read) via
      `LockOrderingInvariantTest`'s 3 tests, exercising `install(as_global=True)` with both locks
      live independently (project-held/home-free, home-held/project-free, both-free-no-deadlock)
- [x] cross-twin observable parity (Python O_EXCL vs. Node `"wx"`, same fail-fast/self-heal/
      exclusion behavior) — confirmed by `TwinParityTest`'s structural call-site check plus 3
      REAL `node cli.js` subprocess smokes (fresh / contended / stale)
- [x] (arising DURING build, not originally pre-declared here — see Strategy actually used) a
      failure before the per-project drop leaves `.add/` exactly as absent as it was before this
      lock existed — no orphan empty-directory residue — confirmed by the 2 previously-regressed,
      now-fixed sibling tests (`test_home_unwritable_fails`,
      `test_install_global_blocked_by_a_held_lock`)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol is referenced. `PROJECT_LOCK_FILE` used by
      `_project_lock`/`acquireProjectLock` (the lock's own path) and by `_DATA_EXCLUDE`/
      `DATA_EXCLUDE` (both twins); `_PROJECT_LOCK_STALE_DEFAULT`/`PROJECT_LOCK_STALE_DEFAULT` used
      inside `_project_lock`/`acquireProjectLock`'s own staleness compare; `_project_lock` called
      from `install()` (_installer.py:1076, `with _project_lock(add_dir, env=env_map):`) and
      `update()` (_installer.py:1715, same shape); `acquireProjectLock` called from `cmdInit`
      (cli.js:735) and `cmdUpdate` (cli.js:1507) — confirmed via direct read-through of both files
      post-edit, not grep-only.
- [x] DEAD-CODE (code) — no new unused/orphaned symbol. Caught and removed one myself during
      self-review before running the suite: an intermediate `reclaimed` local in
      `acquireProjectLock`'s self-heal branch was write-only with no consuming read — deleted;
      confirmed via a final grep pass (no definition without a matching use-site) that nothing
      else new is unreferenced.
- [x] SEMANTIC (prose / non-code) — N/A as a build deliverable (this task's Scope is code-only);
      the only prose touched is this TASK.md's own §4/§5/§6 fills (never frozen); §0-§3's frozen
      prose was re-read in full (not skimmed) before this fill, re-verifying the M1-M11 clauses
      against the actual committed code, not the milestone doc's forward-looking description.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct
      grep/read against the post-build tree: `_installer.py` — `LOCK_FILE` 693, `PROJECT_LOCK_FILE`
      694 (NEW), `_DATA_EXCLUDE` 695, `install` 998, `_add_dir` 1408 (untouched), `_LOCK_STALE_DEFAULT`
      1412, `_update_lock` 1417 (untouched, cited as precedent only), `_PROJECT_LOCK_STALE_DEFAULT`
      1488 (NEW), `_project_lock` 1496 (NEW), `_reconcile` 1362 (untouched), `_update_global` 1595
      (untouched), `update` 1680, `_fail` 55 (untouched); `cli.js` — `fail` 35 (untouched),
      `cmdInit` 688, `dropFiles` 643 (untouched), `LOCK_FILE` 764, `PROJECT_LOCK_FILE` 767 (NEW),
      `PROJECT_LOCK_STALE_DEFAULT` 768 (NEW), `DATA_EXCLUDE` 1014, `reconcile` 917 (untouched),
      `isUserData` 1027 (untouched), `installGlobal` 1274 (untouched), `acquireUpdateLock` 1329
      (untouched, cited as precedent only), `acquireProjectLock` 1396 (NEW), `cmdUpdate` 1487.
- [x] any anchor that moved/renamed since Ground SHA (`1cc4065`) is named here, not left silent —
      NONE renamed (all names identical to Ground, per M10). Every cited anchor MOVED (line-shifted
      only): most of the drift predates THIS task's own edits — 2 sibling tasks
      (`global-lock-followups` @ `7396456`, `global-data-restore-harden` @ `52aafdf`) both merged
      onto this branch between Ground and this task's own TESTS/BUILD phases (already disclosed in
      §0's own "UPDATE (re-confirmed post-draft)" notes). This task's OWN edits additionally shifted
      `install` (Ground 889 -> 998, the lock-wrap's +4-space re-indent + 2 new doc paragraphs),
      `update` (Ground 1384 -> 1680, cumulative shift from `_project_lock`'s own insertion earlier
      in the file plus its own lock-wrap), `cmdInit` (Ground 680 -> 688, pre-existing drift only —
      this task's own edit lands at the END of the body, not before the signature), and `cmdUpdate`
      (Ground 1226 -> 1487, cumulative shift from `acquireProjectLock`'s own insertion earlier in
      the file). Independently re-verified via `git diff`'s own hunk CONTENT (not just its
      nearest-function header, which git anchors to the closest PRECEDING signature even for a
      pure insertion) that `_update_lock`/`acquireUpdateLock`/`_update_global`/`cmdUpdateGlobal`/
      `_reconcile`/`reconcile`/`_add_dir`/`resolve_global_home` stayed byte-identical — every hunk
      landing near one of those names is ADDITIVE-ONLY immediately adjacent to it, never a line
      inside its own body (M10).

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
  closes BOTH the permanent wedge AND the secondary persist-then-restore risk recorded as
  HARD-STOP below, and specifically investigate whether the ticket's OWN self-heal can
  leak/wedge one level further down — the one question the orchestrator's own hand-trace (this
  session, prior turn) deliberately left open. Every point below is re-derived from the CURRENT
  tree, never from round 3's own build narrative or the superseded text this replaces:
  (1) Re-ran the evidence myself, from scratch, fresh runs, none copied: `test_project_scope_
  lock.py` 30/30 green (own run — 26 pre-existing + 4 new from round 3: `LeakedTicketWedgeTest`'s
  `test_leaked_ticket_self_heals_instead_of_permanent_wedge`,
  `test_project_lock_direct_leaked_ticket_self_heals`,
  `test_fresh_ticket_is_never_reclaimed_no_new_hole_introduced`,
  `test_npm_leaked_ticket_self_heals_instead_of_permanent_wedge` — the "26/26" figure in this
  section's own checkbox above predates these 4 and is superseded by this count); the 6-file
  sibling sweep (test_global_install/test_global_update_harden/test_global_restore/
  test_global_data/test_reconcile_rollup/test_project_scope_lock, 152 tests — up from 145,
  reflecting round 3's 3+4 new tests across both sibling suites) 152/152 green (own run);
  `add.py check` 509 passed/0 failed (own run) with ZERO `build_tampered`/`scope_violation` WARN
  for THIS task — the 2 mechanical WARNs the round-2 pass disclosed in its own (7) are GONE, not
  merely re-disclosed: `a515943`/`6505b6a` (round 3's own re-cross commits) updated
  `.add/state.json`'s `tripwire.tests` MD5 to match the CURRENT `test_project_scope_lock.py`
  byte-for-byte (independently confirmed via direct `md5`/`json` inspection this pass:
  `2c6f286c08cf985204b7c1473c4179e2`, matching the recorded snapshot exactly), and the declared
  `scope.declared` list now includes both test files actually touched — genuinely fixed, not a
  bookkeeping absence.
  (2) Re-ran `ProjectLockConcurrencySafetyTest::test_concurrent_stale_reclaim_exactly_one_wins`
  (the ORIGINAL multi-racer TOCTOU race's own regression guard) myself 30 times standalone,
  fresh — 30/30 green, 0 failures; confirms round 3's ticket-leak fix did not reintroduce the
  race round 2 closed.
  (3) Re-ran ALL 4 of round 3's own new `LeakedTicketWedgeTest` methods (including the npm
  subprocess smoke) 30 times standalone, fresh — 30/30 green, 0 failures: reliability confirmed,
  not a one-shot pass.
  (4) Independently re-derived the ticket-level self-heal by hand against the ACTUAL current
  code (`_installer.py:1633-1840` `_project_lock`, `cli.js:1509-1642` `acquireProjectLock`),
  never round 3's own paraphrase: traced the EXACT crash window round 3 fixed (a process wins
  the per-generation reclaim ticket, then dies before its own `finally: os.unlink(ticket_path)`
  a few lines later) and confirmed the delivered fix — on losing the ticket, stat it; if
  `tage > _PROJECT_LOCK_TICKET_STALE_SECONDS`/`PROJECT_LOCK_TICKET_STALE_SECONDS` (5s,
  independent of the main lock's own 120s default), apply the IDENTICAL identity-verified
  discipline (re-stat immediately before unlinking, compare inode, unlink only on a match)
  directly to the ticket file, then a plain
  `os.open(ticket_path, O_CREAT|O_EXCL...)`/`fs.openSync(ticketPath,"wx")` to re-win it exactly
  once (M7's own "no poll, ever" ethos, correctly preserved at this level too — this lock never
  loops, so unlike its sibling it never had a livelock risk, only the clean permanent-wedge
  shape the sibling's own §6 also names) — genuinely resolves the wedge.
  (5) THE CRUX QUESTION this pass exists to answer (not attempted by round 3's build or the
  round-2 verify text below): does the ticket's own self-heal have an analogous leak ONE LEVEL
  FURTHER DOWN — could a crash between winning a "ticket for the ticket" and cleaning it up wedge
  things again? Answer, with both a structural argument and fresh adversarial evidence: NO — see
  Advisor Concurrency (c) below for the full derivation and 1167+-attempt adversarial evidence
  (741 attempts on this task's own `_project_lock`/`acquireProjectLock` alone: 680 Python
  threads + 36 real Python multi-process + 25 real `node` subprocess attempts). This is a
  STRUCTURAL "cannot recur here" finding, not a "did not find one yet" finding — the reasoning
  is laid out in full below, not merely asserted.
  (6) Re-ran the round-2 pass's OWN secondary finding (2(c) below, now closed): confirmed
  `_is_user_data(".install.lock.reclaim-123456")` now returns `False` (was `True` pre-fix), and
  a direct `_persist_data` repro (a leaked ticket sitting alongside real `PROJECT.md` in a
  scanned `.add/`) now snapshots ONLY `PROJECT.md`, never the ticket — round 3's own `.reclaim-`
  infix addition to `_is_user_data`/`isUserData` (`_installer.py:726`, `cli.js:1054`) genuinely
  closes the secondary bogus-persist-then-restore path the round-2 pass flagged as unique to
  this task, not merely disclosed as a residual.
  (7) Read every assertion in the 4 new tests line-by-line:
  `test_leaked_ticket_self_heals_instead_of_permanent_wedge` asserts exit 0, no
  `install_in_progress`, the reconcile actually completing (a deleted `docs` sentinel restored),
  AND both the lock and the ticket gone afterward (no residue left to re-wedge a future call);
  `test_fresh_ticket_is_never_reclaimed_no_new_hole_introduced` asserts the OPPOSITE direction —
  a ticket that is NOT yet stale is left completely untouched and the call still fails fast,
  proving the fix does not become a new over-eager-reclaim hole itself. No vacuous assert, no
  stubbed logic, no overfit-to-fixture pattern found in either new test or in
  `_project_lock`/`acquireProjectLock` (read both in full against the CURRENT tree, not the
  diff).
  (8) Confirmed via `git diff --stat` between the round-2-verify commit (`e35ab42`'s own
  preceding code state) and current HEAD, restricted to `add-method/`: exactly 4 files touched
  (`_installer.py`, `cli.js`, `test_global_update_harden.py`, `test_project_scope_lock.py`; 752
  insertions, 24 deletions) — no file outside declared scope. Confirmed via `git log -p --follow`
  that this task's own §0-§3 remain byte-unchanged since the `73c2627` freeze commit — every
  post-freeze diff to this TASK.md lands inside §5's "Strategy actually used" prose or this §6
  fill, never the frozen bundle.
  (9) Evidence-integrity note, retiring the round-2 pass's own (7): the `build_tampered`/
  `scope_violation pending` pair it disclosed (root-caused there to a stale tests->build
  snapshot after the `add.py heal` reopening) is now MOOT — a fresh `add.py check`/`state.json`
  inspection this pass shows a clean, byte-matching mechanical state for this task (see (1)
  above), not a mere absence of a WARN masking an unresolved precondition.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: add-verify agent (tdd-verifier persona) — round-4 independent pass; fresh reviewer (not
  the round-3 builder, not the round-2 pass that recorded the now-superseded HARD-STOP below)
1. Security: CLEAR — re-grepped the full current diff surface (since the round-2 baseline) for
   eval/exec/`child_process`/new-dependency patterns: none. `_project_lock`'s additions remain
   stdlib-only (`os`/`time`/`contextlib`, all pre-existing, no new `import`); `acquireProjectLock`'s
   remain Node builtins only (`fs`/`path`, no new `require`). The ticket file's content is never
   written to (created empty, closed immediately) and never read back — no untrusted input
   reaches a security-relevant decision anywhere in the reclaim path either. This pass's own new
   finding (Concurrency (c) below) crosses no privilege/trust boundary: every actor able to
   trigger or be affected by it already has direct filesystem write access to the same `.add/`
   tree — the same CWE-367/reliability classification precedent both prior passes used. No
   exposed secrets. No HARD-STOP.
2. Concurrency: CLEAR. Three findings, kept explicit:
   (a) THE ORIGINAL TOCTOU RACE (round 2's target): FIXED, independently reconfirmed — Refute-
   read (2) above (30/30 fresh). CLEAR.
   (b) THE LEAKED-TICKET PERMANENT WEDGE (round 3's target, this task's own prior HARD-STOP
   below) — FIXED, independently re-derived (Refute-read (4)) and independently re-run 30/30
   fresh (Refute-read (3)). The secondary, lower-probability bogus-persist-then-restore path
   unique to this task (round 2's own 2(c)) is ALSO independently reconfirmed CLOSED (Refute-
   read (6): `_is_user_data` now correctly excludes the `.reclaim-` infix; a direct
   `_persist_data` repro snapshots only real user-data, never a leaked ticket). CLEAR.
   (c) THE RECURSIVE QUESTION (this pass's own specific mandate — does the ticket's OWN
   self-heal have an analogous leak one level further down: a crash between winning a "ticket
   for the ticket" and cleaning it up)? Answer: the bug CLASS is STRUCTURALLY CLOSED at this
   level — not merely "not found yet." Derivation:
     - The one invariant that actually matters is "at most one process is ever inside the
       critical section `lock_path` guards, at any instant." This is enforced by exactly ONE
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
       file itself, then a plain O_EXCL re-create of that SAME path (`_installer.py:1759-1771`,
       `cli.js:1561-1583`) — it did NOT invent a third, separately-named file to gate entry to
       ITS OWN reclaim. This is sufficient, structurally, because the re-create step IS ITSELF
       the atomic, kernel-arbitrated exclusivity primitive — the SAME primitive that already
       makes a plain, never-contended first acquire safe with NO ticket at all. A "ticket for
       the ticket" would just reapply the identical already-self-sufficient pattern one more
       time, arbitrating nothing a bare O_EXCL create doesn't already arbitrate. This is the
       recursion's actual base case: level 0 (fresh acquire) = a bare O_EXCL create; level 1
       (reclaiming a stale main lock) = identity-verified-unlink + O_EXCL create; level 2
       (reclaiming a stale TICKET that gates level 1) = identity-verified-unlink + O_EXCL create
       — structurally IDENTICAL to level 1, aimed at a different path. There is no level-3 need,
       because level 2's own re-create already IS its own complete election. This lock's own
       M7 ("no poll, ever") shape makes the argument even tighter than its looping sibling's: a
       ticket-level double-winner here degrades into, at most, ONE extra `install_in_progress`
       fail-fast for the loser — never a hang, since nothing in this function ever loops.
     - Verified this is not merely theoretical: wrote a NEW adversarial repro
       (`verify_round4_ticket_recursion.py`, this session's scratchpad — no tracked test or
       product file touched) that pre-leaks a STALE ticket every round, forcing EVERY racer
       through the harder "ticket already stale, must itself be reclaimed" branch (never the
       simpler "win it outright" branch), and measures PEAK concurrent holders of the real
       critical section via the same active/peak temporal-proof technique the dedicated suite
       already uses. Results against THIS task's own `_project_lock`, directly: 20 rounds x 10
       threads (200 attempts) then 40 rounds x 12 threads (480 more, 680 total) — peak=1, 0
       errors, every time (20/200 acquired, the rest correctly fail-fast per M7 — this lock
       never polls, so most racers in a single round correctly lose, unlike the looping
       sibling). A REAL multi-PROCESS check (6 rounds x 6 genuine OS processes racing a
       pre-leaked stale ticket, checking for ANY overlapping [enter,exit] critical-section
       interval, not just an in-process thread count) — 36 attempts, 0 overlaps, 0 errors: the
       strongest form of "no double-hold" evidence gathered this pass, since real OS processes
       have genuine parallelism beyond Python's GIL. A REAL `node cli.js init --yes` 5-rounds-
       x-5-concurrent-subprocess check against the JS twin — 25 attempts, 0 anomalies. Combined
       with the sibling task's own analogous `_update_lock` evidence (same script, same
       session): 1167+ real adversarial attempts targeting exactly this question across both
       tasks — 0 double-holds, 0 livelocks, 0 hangs, 0 errors.
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
       sitting in the same `.add/`; a full-repo grep for any unlink/rmtree/sweep/gc/prune
       reference to "reclaim" is zero hits — nothing sweeps `.reclaim-*` orphans). Zero
       correctness impact confirmed (even if the exact inode number were later reused, the
       self-heal would correctly identity-verify and reclaim the ancient orphan exactly as any
       other stale ticket, AND it is now correctly excluded from a persist-data snapshot either
       way per (b) above) — a disk-hygiene/directory-clutter cosmetic gap only, worth a
       lightweight future spec-delta (a periodic sweep of aged `.reclaim-*` orphans), not a
       blocking defect.
3. Architecture: CLEAR — the completeness gap the round-2 pass flagged (the new ticket-file
   artifact type missing from the `_is_user_data`/`_DATA_EXCLUDE` registry) is CLOSED by round
   3's own `.reclaim-` infix addition (Refute-read (6)), independently re-verified, not merely
   trusted. `_reconcile`/`_clean_replace`/`_update_lock`/`_update_global`/`_add_dir`/`_fail`
   remain byte-identical bodies since the freeze commit (`73c2627`), independently re-confirmed;
   the new-independent-primitive-vs-extend-`_update_lock` fork (§1 A2) remains a reasoned,
   disclosed, legitimate design choice, not a layering violation. No new dependency. O_EXCL/
   `"wx"` remains the sole DESIGN-level mutual-exclusion primitive at every layer, confirmed
   still true one level down at the ticket layer too.
Verdict: CLEAR (all 3 lenses)
Residue: none — 2 non-blocking 💭 notes disclosed above (the pre-existing, unchanged
  inode-reuse-on-untested-platforms assumption; a newly-observed, zero-correctness-impact
  orphan-ticket-litter hygiene gap). All 3 bug classes this task's own build rounds targeted (the
  original TOCTOU race, the leaked-ticket permanent wedge, the secondary bogus-persist path) are
  independently reconfirmed FIXED, and the specific recursive "does the fix's own fix need
  fixing" question is answered STRUCTURALLY CLOSED (Concurrency (c) above), not merely "not yet
  found" — backed by 1167+ real adversarial attempts targeting exactly that question (741 of
  them against this task's own lock specifically), 0 anomalies.
Binding: advisory — this task does not declare `risk: high` (autonomy: auto); with Residue now
  `none` and complete, freshly-reproduced evidence (not trusted from either prior pass), this is
  a genuinely clean finding — the condition under which this task's own autonomy level permits a
  legitimate auto-PASS, not merely an advisory recommendation deferred to a human.

Recommended GATE RECORD (not stamped — human/orchestrator decides): PASS. `autonomy: auto` + no
  declared `risk: high` + complete, freshly-reproduced evidence + NO residue (both prior
  HARD-STOP-worthy defects — the original TOCTOU race and the leaked-ticket permanent wedge,
  including its unique secondary persist-then-restore path — are independently reconfirmed
  fixed; the specific recursive "ticket-for-a-ticket" question this round exists to answer is
  resolved with both a structural argument and 741 real adversarial test attempts against this
  task's own lock, 0 anomalies) together make this the case this task's own design anticipates
  for a legitimate auto-PASS, not a rubber stamp. The EXISTING GATE RECORD at the bottom of this
  section (Outcome: <unset>, still templated) has never been stamped for this task at all; this
  is the first complete recommendation offered for it, superseding the round-2 pass's own
  HARD-STOP (recorded before round 3's fix existed) rather than reversing a prior human
  decision.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-03

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose a NEW, independent lock primitive — own function, own lock file (`<target>/.add/.install.lock`), own env-overridable staleness default — that MIRRORS the proven O_EXCL/`"wx"` + mtime-age-self-heal PATTERN already established in this codebase, without calling into or extending either the current or the eventual `_update_lock`/`acquireUpdateLock`; rejected generalize/extend `_update_lock`/`acquireUpdateLock` itself to accept ANY root (home OR a project's `.add/` dir), calling it from both `_update_global` (existing) and `install`/`update` (new) (rejected: at draft time, `global-lock-followups`'s own hardening of that function was FROZEN but not yet merged — that specific coupling concern is now moot, since it merged (`7396456`) shortly after this draft was written; the choice still stands on its OWN, merge-order-independent merits — the two locks guard genuinely different-shaped resources — one shared, machine-wide, potentially-many-registered-projects propagation (tolerating a long ~600s staleness window and motivating an opt-in CI wait) versus one per-target, typically-few-seconds reconcile (wanting a much shorter default and no wait mode) — forcing one shared knob would be an awkward compromise between the two (this reasoning holds regardless of merge order, which is now moot: both tasks merged, `global-lock-followups` first) · no lock at all, relying solely on `_clean_replace`'s already-shipped per-call atomicity and accepting an unpredictable last-writer-wins outcome (rejected: the milestone's own 4th exit criterion explicitly demands "cannot interleave writes — one waits or fails cleanly," a strictly stronger guarantee than "each writer's OWN copy is internally atomic," which already exists today without any new work) · an OS-level advisory file lock (`fcntl.flock`/Windows `msvcrt.locking`) instead of an O_EXCL sentinel file (rejected: the identical, already-learned CONVENTIONS.md fv59 lesson — an OS-level advisory lock is not observable/compatible cross-twin, since Node has no `flock` equivalent without a native dependency, which the "no new dependency anywhere in this milestone" constraint rules out) · an opt-in `--lock-timeout`-style bounded-wait CLI flag, mirroring `global-lock-followups`'s own M4 (considered and DECLINED, not silently omitted: that flag's motivating use case — a CI job waiting out a potentially-long multi-project global propagation — does not transfer cleanly to a per-project lock whose expected hold duration is a handful of `_clean_replace` calls; immediate fail-fast is simpler, needs no new CLI surface, matching this milestone's own "no new flag surface for routine tuning" spirit, and the exit criterion itself offers "waits OR fails cleanly" as two equally acceptable options, not a mandate for waiting).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: AS PLANNED, in the same 8-step batch order (constants -> Python `_project_lock` -> JS `acquireProjectLock` -> `install()` wrap -> `update()` wrap -> `cmdInit` wire -> `cmdUpdate` wire -> grep-confirm the 5 named untouched call sites stayed byte-identical), with the §4 RED suite (26 tests) written and committed FIRST as its own commit (`4682b00`), confirmed 16/26 failing for the traced right reason (an AttributeError on the not-yet-existing `_project_lock`/`PROJECT_LOCK_FILE` symbols, or the OLD lock-less `install()`/`update()` correctly not noticing a pre-existing/held lock file it doesn't check for yet) before any implementation line — the same TDD discipline both sibling tasks in this milestone followed.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · seeded] sweep aged orphan `.reclaim-<inode>` ticket files (both `_project_lock`/ [→ sweep-orphan-reclaim-tickets]
  `_update_lock` and their JS twins) — a ticket leaked by a crash between winning it and its own
  cleanup is currently permanent, harmless disk litter with nothing to clean it up (evidence:
  round-4 independent verify's own repo-wide grep for any unlink/rmtree/sweep/gc/prune reference
  to "reclaim" returned zero hits; a fresh, uncontended acquire/release cycle never touches an
  orphaned ticket sitting in the same directory).
- [SPEC · seeded] independently stress-test the ticket/lock identity check's inode-reuse assumption [→ cross-platform-inode-reuse-stress]
  on Linux and Windows, not just macOS/APFS (evidence: rounds 2 through 4 each disclosed the same
  gap — every empirical concurrency repro this session, 1167+ adversarial attempts total, ran on
  macOS/APFS only; the assumption "the filesystem never reuses an inode number for an unrelated
  file inside the tiny re-stat-to-unlink window" rests on documented API contract, not
  cross-platform measurement).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a concurrency test can look like it proves exclusivity while actually proving only [folded foundation-version 63]
  liveness — `assertGreaterEqual(results.count("acquired"), 1, ...)` is silently compatible with
  MULTIPLE simultaneous winners, the exact violation it was named to catch (evidence: this
  session's own `test_concurrent_stale_reclaim_exactly_one_wins`, in both this task and its
  sibling, passed green through round 1's real double-acquisition bug; only an adversarial verify
  pass building its own repro — not re-reading the test — surfaced the gap; the fix was a
  temporal peak-concurrent-holders check, not a stronger count).
- [ADD · folded] a self-heal mechanism whose own bookkeeping can itself leak (a lock reclaimed via a [folded foundation-version 63]
  ticket file; the ticket itself un-swept) needs an explicit "does this recursion terminate"
  check at verify — a build round can correctly fix the REPORTED symptom while leaving the same
  bug CLASS one level deeper, and "no further bug found" is a different, weaker claim than "this
  bug class cannot recur here, structurally" (evidence: this session's own 3-round arc — a TOCTOU
  race, fixed by a ticket; the ticket itself leaked, fixed by a nested self-heal; only a 4th,
  explicitly-scoped verify pass asked whether THAT fix could leak too, and answered with a
  structural argument — the ticket is a contention filter above the one real exclusivity
  primitive, not a second instance of it — backed by 1167+ adversarial attempts, not simply
  another clean test run).
- [SDD · folded] a task's own §6 summary checkboxes can silently drift stale relative to its [folded foundation-version 63]
  Refute-read/Advisor verdict prose across multiple build-fix rounds, misrepresenting genuinely
  resolved work as an open judgment call to a `report --decide` reader (evidence: this exact
  session, 2 separate tasks — `global-data-restore-harden` earlier, `global-lock-followups` this
  arc — each needed a manual checkbox-to-verdict reconciliation pass before their gate report
  was accurate).

