# TASK: JS/npm reclaim-lock heartbeat twin fix

slug: js-reclaim-lock-heartbeat · created: 2026-07-04 · stage: mvp · risk: high
milestone: (none)
sensitivity: architecture
autonomy: conservative
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/bin/cli.js:acquireUpdateLock` (L1353-1486, home-scoped lock, poll/timeout mode) and `add-method/bin/cli.js:acquireProjectLock` (L1511+, project-scoped lock, fail-fast-only, no poll mode) — the npm/JS twins of `_installer.py:_update_lock`/`_project_lock`, sharing the identical identity-verified (inode-compared) per-generation reclaim-ticket design (`LOCK_TICKET_STALE_SECONDS`/`PROJECT_LOCK_TICKET_STALE_SECONDS = 5`, L769/783)
Context (working folder): `add-method/package.json` — `"test": "python3 -m unittest discover -s tooling -p 'test_*.py'"`; NO JavaScript test file or JS test runner exists anywhere in this repo (confirmed: `find . -iname "*.test.js"` and `find add-method -iname "*.js" -path "*test*"` both empty). `npm test` runs the PYTHON suite only — `cli.js`'s lock functions have ZERO existing automated test coverage of any kind, in any language.
Honors (patterns / conventions): the existing Python reclaim-race fix (`reclaim-ticket-race` task, commit 678cd7b/5a61425) — same bug class, proven v2 (holder-side heartbeat) + v3 (widened test-threshold margin) fix shape to port, NOT to re-derive from scratch
Seams consulted: none cited
Anchors the contract cites: `acquireUpdateLock`'s reclaim branch (`Date.now() - st.mtimeMs > staleAfterMs`, L1372) and `acquireProjectLock`'s identical shape (L1511+); the `release` closure (L1480-1485) that must host the new heartbeat's teardown
Issues/Risks (→ feed §1): (1) IDENTICAL root-cause bug to the Python side confirmed by direct code read — nothing in `acquireUpdateLock` or `acquireProjectLock` ever refreshes `lockPath`'s own mtime while legitimately held (the open `fd` just sits there; no `fs.utimesSync` call exists anywhere in either function), so `Date.now() - st.mtimeMs > staleAfterMs` can misjudge a live-but-slow holder as crashed, exactly as the Python bug did before its heartbeat fix. (2) Node's single-threaded event loop means a `setInterval`-based heartbeat is the natural JS analog of Python's daemon thread, but carries the IDENTICAL residue the Python v2 fix discovered on real CI: a heartbeat callback only fires between synchronous JS turns — if the whole process's event loop is blocked by a long synchronous operation, the heartbeat can't fire either, same as a Python thread stalling with a starved process. (3) NO TEST INFRASTRUCTURE EXISTS for this file in any form — this is a bigger gap than "write a red test": it requires deciding HOW to test JS code in a Python-test-only repo (options: a Python test that shells out to real `node cli.js`/spawns child_process races, mirroring the existing all-Python convention with zero new tooling; OR standing up an actual JS test runner + npm devDependency, a more invasive precedent). (4) The Python fix's own test used `threading.Thread` (multi-thread, single-process) contention — the advisor flagged mid-session that a faithful JS-side test needs multi-PROCESS contention (`child_process.fork`/`spawn`, real separate `node cli.js` invocations racing), which is actually MORE representative of real production usage (concurrent `npm install`/`add init` runs are always separate OS processes, never threads) but is a heavier test harness than anything in this repo's precedent.
Related intent: PROJECT.md's cross-platform/dual-package promise (ship as both `@pilotspace/add` npm and `pilotspace-add` pip, byte-identical behavior) — a fixed-in-Python-only, unfixed-in-JS lock race would leave the two installers with materially different concurrency-safety guarantees despite the project's own "byte-identical mirrors" convention (methodology-engine-dev persona, Critical Rules). Originating ask: user's "fix all" → "All 7 backlog tasks + reconcile + JS twin" (explicit AskUserQuestion selection, this session).
Ground SHA: `ba42053` (`git rev-parse --short HEAD`) — all cited line numbers are current as of this commit

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: port the Python `_lock_heartbeat` fix to `acquireUpdateLock`/`acquireProjectLock` in `cli.js` — a background heartbeat that refreshes the held lock file's own mtime, closing the identical live-holder-misjudged-stale race — tested via a NEW Python subprocess test that races real `node cli.js` child processes (chosen by Tin Dang, AskUserQuestion, over standing up a JS test runner or shipping untested)
Framings weighed: `setInterval(() => fs.utimesSync(lockPath, now, now), interval)` heartbeat, cleared in the existing `release()` closure (chosen — direct JS analog of the proven Python daemon-thread shape, same interval formula `max(50ms, min(staleAfterMs/4, 5000ms))`) · a `fs.watch`-based liveness signal — rejected, solves a different problem (file-change notification, not a self-refreshing timestamp) and adds platform-inconsistent behavior (fs.watch is notoriously inconsistent across macOS/Linux/Windows) · bumping `LOCK_STALE_DEFAULT`/`PROJECT_LOCK_STALE_DEFAULT` alone with no heartbeat — rejected, same reasoning the Python task's own Reject-R1 already ruled out: raises the false-positive bar but never fixes the structural race, and produces a materially slower self-heal from a genuine crash
Must:
<must>
  - a legitimately-held `acquireUpdateLock`/`acquireProjectLock` lock's own mtime is refreshed periodically for as long as it is held, so `Date.now() - st.mtimeMs > staleAfterMs` never misjudges a live holder as crashed purely due to a slow critical section
  - the heartbeat is torn down cleanly on release (both normal completion and `fail()`'s `process.exit` path — mirrors the existing `process.on("exit", release)` wiring) so it never outlives the process or blocks Node's event loop from exiting on its own
  - a genuinely crashed holder (no heartbeat, real staleness) still self-heals via the existing identity-verified (inode-compared) reclaim-ticket mechanism — UNCHANGED, this task only fixes the staleness *judgment*, never the reclaim-ticket arbitration itself
  - the new Python subprocess test races real, separate `node cli.js` invocations (not threads) contending for the SAME lock file, and asserts exactly one holds it at any instant (peak <= 1) under an injected artificial critical-section delay
</must>
Reject:
<reject>
  - a heartbeat interval so long it can't refresh mtime before `staleAfterMs` elapses under normal load -> the interval formula must always keep interval < staleAfterMs (mirrors the Python fix's `max(50ms, min(staleAfterMs/4, 5000ms))`)
  - the heartbeat timer itself keeps the Node process alive after the lock is released -> use `.unref()` (or clear it explicitly in `release()`) so a released lock never prevents natural process exit
  - a test that only proves the mechanism fires at all, without proving it prevents a real misjudged-stale reclaim under contention -> the test must inject a real critical-section delay past `staleAfterMs` and assert the race a pre-fix run would lose
</reject>
After:
<after>
  - `acquireUpdateLock` and `acquireProjectLock` both carry the same live-holder-misjudged-stale protection as their Python twins (`_update_lock`/`_project_lock`)
  - a new `tooling/test_js_reclaim_lock_heartbeat.py` proves it via real multi-process contention, red before the fix, green after
  - the fix ships in the SAME published package version stream as the Python side once both are verified (no user-visible asymmetry between the npm and pip installers' concurrency guarantees)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ a `setInterval`-based heartbeat surviving whole-event-loop starvation is UNPROVEN here — the Python v2 heartbeat (a real OS thread) still failed on real CI once under whole-PROCESS scheduling starvation; a JS `setInterval` callback is strictly weaker (it can't fire at all while any synchronous JS is running, not just while descheduled by the OS) — lowest confidence because this residue was only discovered empirically on the Python side AFTER a real CI failure, not derivable from reading the code; if wrong: this fix could ship with the SAME false sense of safety the Python v1/v2 rounds had, requiring an identical widened-threshold companion fix (v3-equivalent) once/if it's caught on real CI
  - [ ] a new internal, test-only CLI entrypoint/flag on `cli.js` (e.g. `--internal-acquire-lock <home|addDir> <hold-ms>`) is needed so the Python subprocess test can drive real lock acquisition/hold/release from the outside without duplicating `acquireUpdateLock`'s logic in the test itself — confirm this is an acceptable, clearly-test-only addition to cli.js's surface (not a user-facing command) before Build
  - [ ] child_process-level contention (separate `node` processes) reproduces the SAME race shape as the Python test's thread-based one (both ultimately race on the same `fs.openSync(path, "wx")` OS-level primitive) — high confidence but not yet empirically run
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a slow-but-live holder survives contention   # M1
  Given process A acquires acquireUpdateLock and holds it past staleAfterMs via a slow critical section
  When process B contends for the same lock while A still legitimately holds it
  Then A's heartbeat has refreshed the lock's mtime, so B never misjudges A as crashed and never reclaims
  And exactly one process (A) holds the lock at every instant (peak <= 1)

Scenario: heartbeat torn down cleanly on release   # M2
  Given a process acquires the lock, holds it briefly, then releases normally
  When the process exits
  Then no heartbeat timer remains active and the process exits on its own (no hang from an un-.unref()'d interval)

Scenario: a genuinely crashed holder still self-heals   # M3
  Given a lock file is left behind by a process that never releases it (simulated: no heartbeat ever ran, real staleness)
  When a new process contends for the lock after staleAfterMs has genuinely elapsed
  Then the existing identity-verified reclaim-ticket mechanism reclaims it exactly as before this fix — unchanged behavior

Scenario: multi-process race proves exactly one winner   # M4
  Given N separate `node cli.js` child processes (not threads) race to acquire the same lock file
  When one wins and holds through an injected delay past staleAfterMs
  Then the Python subprocess test observes peak-held <= 1 across the whole race, red before the fix and green after

Scenario: an over-long heartbeat interval is rejected at code review, not runtime   # R1
  Given a heartbeat interval is chosen for a given staleAfterMs
  When the interval is computed
  Then it is always strictly less than staleAfterMs (mirrors max(50ms, min(staleAfterMs/4, 5000ms)))
  And no staleAfterMs value can produce an interval that fails to refresh mtime before the threshold elapses

Scenario: the heartbeat never blocks process exit   # R2
  Given a lock has been released (normal completion or fail()'s process.exit)
  When the process would otherwise be idle
  Then the heartbeat timer does not keep the event loop alive — process exits naturally
  And no dangling timer references the released lockPath
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION acquireUpdateLock(home, {timeout}, env)   body: { held: fresh | stale-genuine | stale-misjudged-fixed }
  fs.openSync(lockPath, "wx") succeeds -> heartbeat started, mtime refreshed every
    max(50ms, min(staleAfterMs/4, 5000ms)) until release() fires
  release() (normal or fail()'s process.exit) -> heartbeat cleared FIRST, then fd closed + lockPath
    unlinked (unchanged order otherwise) — timer is .unref()'d so it never blocks natural exit
  contended + fresh (age <= staleAfterMs, heartbeat-refreshed while genuinely held) -> unchanged:
    timeout null/0 fails "update_in_progress" immediately; timeout=N polls up to N seconds
  contended + genuinely stale (no heartbeat ever ran / process truly crashed) -> UNCHANGED existing
    identity-verified (inode-compared) reclaim-ticket mechanism reclaims it, exactly as today

FUNCTION acquireProjectLock(addDir, env)   body: { held: fresh | stale-genuine | stale-misjudged-fixed }
  IDENTICAL heartbeat shape, mirrored independently (zero shared code with acquireUpdateLock,
    per this file's own existing "NEW, INDEPENDENT primitive" convention) — fail-fast only, no poll

FUNCTION acquireLockForTest(kind, path, holdMs)   body: { kind: "update" | "project" }
  NEW, test-only internal entrypoint (guarded behind an undocumented CLI flag, e.g.
    --internal-acquire-lock <update|project> <path> <holdMs>) — acquires the named lock, sleeps
    holdMs (simulating a slow critical section), writes one line to stdout the moment it is HELD
    and one line the moment it releases, then releases and exits 0. Exists SOLELY so the Python
    subprocess test can drive real multi-process contention without duplicating acquire/release
    logic in the test itself. Never documented in --help; not part of the public CLI surface.

Schema: no data schema touched — pure process-lifecycle/timer behavior over 2 existing lock files
  (LOCK_FILE under <home>, PROJECT_LOCK_FILE under <addDir>) plus their pre-existing .reclaim-<ino>
  ticket siblings (unchanged)
```

Glossary deltas: `Heartbeat (JS)`: a `setInterval`-driven periodic `fs.utimesSync` refresh of a held lock file's own mtime, the JS analog of the Python `_lock_heartbeat` context manager — refreshes liveness, never arbitrates reclaim ordering (that remains the ticket mechanism's job)
Status: FROZEN @ v1 — approved by Tin Dang, 2026-07-05 ("freeze as drafted")
Reported: yes — the framing above + the AskUserQuestion test-strategy decision were shown before this draft
Least-sure flag surfaced at freeze: [spec] a `setInterval` heartbeat's survival under whole-event-loop starvation is UNPROVEN — the Python daemon-thread heartbeat (a strictly stronger primitive) still failed once on real CI under whole-process scheduling starvation, requiring a widened-threshold follow-up; this JS port could ship with the same false sense of safety until/unless it is caught the same way. Cost if wrong: a repeat of the Python task's 2-round CI-failure cycle, this time on the JS side.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: n/a — concurrency behavior proven by race outcome, not line coverage
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_slow_holder_survives_contention: arrange one `node cli.js --internal-acquire-lock update <path> <holdMs>` child holding past staleAfterMs / act spawn contenders racing the same lock while it holds / assert peak-held-count <= 1 the whole time (via stdout HELD/RELEASED markers with timestamps) · covers: M1
  - test_heartbeat_does_not_block_exit: arrange acquire+release via the same internal entrypoint with a short holdMs / act wait for the child process to exit on its own / assert it exits within a bounded time with no hang · covers: M2, R2
  - test_genuine_crash_still_reclaims: arrange a lock file with a real stale mtime and NO live process ever running (simulates a crash — heartbeat never started) / act contend from a new process after staleAfterMs / assert the existing ticket-reclaim mechanism still reclaims it, unchanged · covers: M3
  - test_concurrent_stale_reclaim_exactly_one_wins: arrange N=6 real child `node cli.js` processes racing the same lock file, one injected with holdMs past staleAfterMs / act run all N to completion / assert exactly one peak holder throughout (mirrors the Python fix's own proven test shape) · covers: M4
  - test_heartbeat_interval_always_below_threshold: arrange a range of staleAfterMs values (via ADD_LOCK_STALE_SECONDS/ADD_PROJECT_LOCK_STALE_SECONDS) / act compute the heartbeat interval cli.js would use / assert interval < staleAfterMs for every value in range · covers: R1
</test_plan>

Tests live in: `add-method/tooling/test_js_reclaim_lock_heartbeat.py` (new file) · `add-method/bin/cli.js` (new `--internal-acquire-lock` test-only entrypoint, no separate test file needed for it — exercised entirely through the Python test above) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js`, `add-method/tooling/test_js_reclaim_lock_heartbeat.py`
Strategy (ordered batches): 1. add the `_lockHeartbeat(lockPath, staleAfterMs)`-equivalent helper to cli.js (returns a `{stop}` handle wrapping a `.unref()`'d `setInterval`) · 2. wire it into `acquireUpdateLock`'s success path + `release()` closure · 3. wire the identical shape into `acquireProjectLock` (independently — no shared code, per this file's own existing convention) · 4. add the test-only `--internal-acquire-lock` entrypoint · 5. write `test_js_reclaim_lock_heartbeat.py` RED first (confirm it fails against pre-fix cli.js by testing against the CURRENT committed cli.js, or a git-stash of the fix) · 6. apply the cli.js fix, confirm GREEN · 7. re-run with widened ADD_LOCK_STALE_SECONDS-style env overrides if real subprocess timing proves as noisy as the Python task's CI experience predicts

Persona (optional): methodology-engine-dev — engine/lock concurrency discipline; also review against the Python fix's own hard-won lessons (v1 falsified, v2 partial, v3 widened-threshold) before declaring this "done"
Spawn isolation (default): not applicable — no subagent spawn planned for this build; if delegated later, prefer isolation: "worktree" per the project's now-standing preference (worktree-isolated-spawn-default backlog item)
Known-problem fixes: (1) whole-event-loop starvation could silently defeat the heartbeat exactly as whole-process starvation did in Python → planned fix: do NOT assume this is solved by the heartbeat alone; explicitly test under injected delay AND flag in Verify's concurrency lens that this residue is inherited, not newly introduced. (2) an un-.unref()'d timer could hang a short-lived CLI invocation forever → planned fix: `.unref()` the interval immediately, verified by the exit-boundedness test (M2/R2/test_heartbeat_does_not_block_exit). (3) `acquireProjectLock` currently has NO poll/timeout mode (fail-fast only) → the heartbeat must not change this; only the staleness *judgment*, never the contention-handling shape
Strategy actually used: as planned, batches 1-6 in order, with two build-time decisions the plan
  left open: (1) the `--internal-acquire-lock` entrypoint's "slow critical section" is simulated
  via a NEW `sleepAsync` (setTimeout-based, event-loop-yielding) helper, never the codebase's
  existing `sleepSync` (Atomics.wait) — a synchronous block would starve the very event loop the
  `setInterval` heartbeat needs to fire on, which would make every contention test fail even
  post-fix (this is also the realistic shape: real slow Node work — network/fs I/O — is async,
  not a synchronous spin; the disclosed whole-event-loop-starvation residue is a DIFFERENT,
  already-named risk, not what this test simulates). (2) added a 6th test beyond the declared
  5-test plan (`test_project_lock_slow_holder_survives_contention`) because Must #1 explicitly
  requires BOTH acquireUpdateLock AND acquireProjectLock protected, and none of the 5 planned
  tests exercised the `project` kind under contention. Batch 7 (widened ADD_LOCK_STALE_SECONDS
  re-run) was not needed — 3 consecutive full re-runs of the new suite were stable (no flake) at
  the chosen thresholds (300-400ms stale / 700-800ms pre-contend wait), a wider margin than
  strictly required.
Safety rule (feature-specific): the heartbeat must NEVER touch the reclaim-ticket mechanism's own logic (inode-comparison, ticket staleness) — this task is additive-only to the staleness-judgment path; the existing, already-proven ticket arbitration is out of scope and must remain byte-for-byte unchanged
Code lives in: `add-method/bin/cli.js`
Constraints: do NOT change any test or the contract; allow-list packages only (Node built-ins: `fs`, `path`, `child_process` for the test — no new npm dependency); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — new `test_js_reclaim_lock_heartbeat.py`: 6/6 green (re-run this session; stable, no flake); pre-existing `test_project_scope_lock`+`test_setup_lock`+`test_status_lock_hint`: 46/46 green, no regression from the heartbeat wiring
- [x] coverage did not decrease — coverage target is n/a (concurrency behavior proven by race outcome, per §4); no existing test removed or weakened
- [x] no test or contract was altered during build — confirmed via `git diff --stat`: only `add-method/bin/cli.js` (+64 lines) and the new test file are touched; §1–§4 of this TASK.md are untouched since Ground SHA `ba42053`
- [x] the green was EARNED, not gamed — see Refute-read verdict below (mutation-tested, not just inspected)
- [x] concurrency / timing of the risky operation is safe — see Advisor 3-lens Concurrency below (CLEAR for stated scope + one named, inherited residue)
- [x] no exposed secrets, injection openings, or unexpected dependencies — see Advisor 3-lens Security below (CLEAR)
- [x] layering & dependencies follow CONVENTIONS.md — see Advisor 3-lens Architecture below (CLEAR + one advisory note)
- [ ] a person reviewed and approved the change — PENDING: this Verify pass produces the evidence for that human gate; not self-recorded here (conservative autonomy)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a live-but-slow holder is never reclaimed by a contender purely on wall-clock age — confirmed by `test_slow_holder_survives_contention` + `test_project_lock_slow_holder_survives_contention` passing, AND by the mutation test below: neutering the heartbeat's actual `fs.utimesSync` refresh (while leaving the entrypoint/wiring intact) makes exactly those tests regress to FAIL — the causal link is demonstrated, not assumed
- [x] a released lock's heartbeat never blocks natural process exit — confirmed by `test_heartbeat_does_not_block_exit` (both `update` and `project` kinds) completing within its 5s bound, AND remaining GREEN even under the heartbeat-neutering mutation (proves it tests exit-boundedness specifically, not accidentally coupled to the mtime-refresh mechanism)
- [x] a genuinely crashed (never-heartbeated) holder still self-heals via the unchanged reclaim-ticket mechanism — confirmed by `test_genuine_crash_still_reclaims` passing, and by reading the diff: the identity-verified (inode-compared) reclaim-ticket branches in both `acquireUpdateLock` and `acquireProjectLock` have 0 lines touched by this build
- [x] the heartbeat interval formula always stays strictly below `staleAfterMs` — confirmed by `test_heartbeat_interval_always_below_threshold`'s regex-plus-arithmetic check across 8 representative thresholds (200ms–3,600,000ms)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: `sleepAsync` (1 call site — `cmdInternalAcquireLock`), `startLockHeartbeat` (2 call sites — `acquireUpdateLock` L1511, `acquireProjectLock` L1667), `cmdInternalAcquireLock` (1 call site — `main()`'s pre-dispatch interception at L1802) — confirmed via `grep -n` across the whole file, no orphans
- [x] DEAD-CODE (code) — no new unused or orphaned symbol; all 3 new top-level additions are exercised by the new test file on every run (confirmed by the mutation test below actually changing their observed behavior)
- [ ] SEMANTIC (prose / non-code) — n/a, this is a code-only change (no prose/doc surface touched)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — `acquireUpdateLock` now at cli.js:1384 (Ground SHA cited ~L1353), `acquireProjectLock` now at cli.js:1544 (Ground SHA cited ~L1511+), both `release()` closures at L1512/L1668 — confirmed by direct read
- [x] any anchor that moved/renamed since Ground SHA is named here, not left silent — `git log ba42053..HEAD -- add-method/bin/cli.js` shows ZERO intervening commits touched this file since Ground; the entire line-number shift is attributable solely to THIS build's own additive insertions (`sleepAsync` + `startLockHeartbeat`, ~64 lines, inserted before both functions) — self-caused, expected, not external drift

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self (add-verify, tdd-verifier persona) · adversarially checked: (1) reverted `cli.js` entirely
  to pre-fix (via `git stash push -- add-method/bin/cli.js`) and re-ran the new 6-test file — all 6
  genuinely FAILED (right reason: missing `--internal-acquire-lock` entrypoint / observed
  misjudged-stale double-hold), confirming the suite is not a vacuous pass-regardless-of-code
  fixture. (2) restored the fix, then surgically neutered ONLY the heartbeat's causal effect —
  commented out the `fs.utimesSync(lockPath, now, now)` call inside `startLockHeartbeat` while
  leaving the `.unref()`'d timer, the entrypoint, and all wiring fully intact — and re-ran the 4
  contention-relevant tests: `test_slow_holder_survives_contention`,
  `test_concurrent_stale_reclaim_exactly_one_wins` (observed peak=2, was asserting <=1), and
  `test_project_lock_slow_holder_survives_contention` correctly went RED, while
  `test_heartbeat_does_not_block_exit` correctly stayed GREEN (it doesn't depend on the
  mtime-refresh effect, only on `.unref()` teardown) — this proves the contention tests kill a
  real mutant and assert the heartbeat's actual causal effect, not merely "does the entrypoint
  exist," and proves the suite has test-level specificity (an unrelated test wasn't collaterally
  broken by the mutation). (3) reverted the mutation, confirmed `git diff --stat` matched the
  original build diff exactly (64 lines added, unchanged), re-ran the full 6-test file green (OK)
  plus the 3 pre-existing lock test files (`test_project_scope_lock` + `test_setup_lock` +
  `test_status_lock_hint`, 46/46 green) confirming zero regression from the heartbeat wiring. (4)
  confirmed via `grep`/read that every new symbol (`sleepAsync`, `startLockHeartbeat`,
  `cmdInternalAcquireLock`) is referenced exactly where the contract says, no dead code. (5)
  confirmed `.github/workflows/ci.yml` sets up Node 20 (L40-42) before running the tooling suite
  (L58) so the new subprocess-dependent test file genuinely executes in CI, not silently skipped.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self (add-verify, tdd-verifier persona; STRIDE checklist borrowed from the
  security-gatekeeper persona for the security lens specifically, since sensitivity: architecture
  here also touches a shipped CLI's real attack surface)
1. Security: CLEAR — `--internal-acquire-lock` confirmed absent from `--help` text (read in
  full) and from every documented command; intercepted via a single `argv[0] === "--internal-
  acquire-lock"` check BEFORE the public `cmd`/switch dispatch (cli.js:1801); no new npm
  dependency (`git diff` on package.json/package-lock.json is empty — confirmed). The flag DOES
  ship, unremoved, in the published binary and is locally invocable by any user of the CLI — but
  it grants no capability beyond what the already-public `init`/`update` commands expose (opening
  a file / making a dir at a user-supplied path, with the same OS permissions as the invoker
  already has): no privilege escalation, no widened remote surface, since a local attacker
  capable of invoking this flag at all already has equivalent-or-greater capability via the
  documented commands. 💭 note (non-blocking): a cheap defense-in-depth improvement for a later
  task would be gating the flag behind an additional env var (e.g. `ADD_TEST_MODE=1`) so it's not
  reachable by flag alone — not required by this task's frozen contract.
2. Concurrency: CLEAR for the fix's stated scope; RESIDUE named (pre-existing, not introduced by
  this task) — mutation-testing (see Refute-read above) empirically proves the heartbeat
  correctly protects a live holder doing realistic async work. Whole-event-loop synchronous-block
  starvation can still defeat a `setInterval` heartbeat exactly as whole-process OS scheduling
  starvation once defeated the Python daemon-thread heartbeat on real CI — this is honestly and
  explicitly disclosed in THREE places (§1 assumptions ⚠-flag, §5 Known-problem-fixes(1), and the
  `startLockHeartbeat` code comment at cli.js:813-819), not newly discovered or hidden by this
  review. Judgment on the `sleepAsync`-not-`sleepSync` test-design choice: HONEST, not evasive —
  it exercises exactly the failure mode this fix targets (a live holder doing realistic async
  I/O, the only realistic shape of a slow critical section in this CLI); testing via `sleepSync`'s
  thread-blocking `Atomics.wait` would test a DIFFERENT, already-out-of-scope failure mode (whole-
  event-loop starvation) the frozen contract never claims to fix — a test that fails post-fix for
  a reason unrelated to what shipped would be a false negative, not stronger verification. One
  real gap: no test empirically REPRODUCES the starvation residue itself here (it's asserted by
  analogy to the Python task's own CI history, not demonstrated in this repo) — a gap in evidence
  generation, not a misrepresentation; the Python side also only caught it empirically after a
  real CI failure, so this is proportionate to precedent, not lax. Also verified: the new
  `cmdInternalAcquireLock` is the ONLY call site that invokes the returned `release()` manually IN
  ADDITION to the pre-existing `process.on("exit", release)` firing it again at `process.exit(0)`
  — checked this double-release is safe: `clearInterval` is idempotent, and the second
  `fs.closeSync`/`fs.unlinkSync` calls throw EBADF/ENOENT respectively, both already caught by the
  existing try/catch inside `release()` — confirmed by the suite's own repeated green runs, which
  exercise this exact path every single test.
3. Architecture: CLEAR, 1 advisory note — no new npm dependency; `acquireProjectLock`'s heartbeat
  is wired independently (its own `startLockHeartbeat()` call + its own `release()` closure),
  consistent with this file's own pre-existing "NEW, INDEPENDENT primitive, zero shared code"
  convention (confirmed by direct read, not just the comment's claim); the identity-verified
  reclaim-ticket mechanism is confirmed byte-for-byte untouched (0 diff lines inside those
  branches). Advisory note (non-blocking): `--internal-acquire-lock` is a test-only code path
  permanently baked into the shipped production binary rather than isolated behind a build-time
  exclusion — an accepted, human-approved tradeoff (Tin Dang, AskUserQuestion, recorded in §1/§5)
  given this repo has zero JS test-runner infrastructure; worth a future spec delta, not a
  blocker for this frozen scope.
Verdict: PASS-eligible (no HARD-STOP finding — security CLEAR); the whole-event-loop-starvation
  residue is a disclosed, inherent-to-the-`setInterval`-approach limitation (accepted at contract
  freeze: §1's own ⚠-flagged assumption), not a build defect — but per this task's own
  `risk: high`/`autonomy: conservative` classification AND direct precedent, the human makes the
  final PASS-vs-RISK-ACCEPTED call, not this review. PRECEDENT CHECKED: the pip twin
  (`reclaim-ticket-race`, `.add/tasks/reclaim-ticket-race/TASK.md` GATE RECORD, 2026-07-04)
  recorded this IDENTICAL residue class (whole-process/whole-event-loop scheduling starvation
  defeating the heartbeat) as `Outcome: RISK-ACCEPTED` — not PASS — with an explicit
  owner/ticket/expiry ("expires on the next `v*.*.*` tag's publish-workflow CI run"), and that
  waiver was subsequently VOIDED by a real CI failure, requiring a v3 widened-threshold follow-up
  fix before it was genuinely resolved. This task's residue is arguably a STRICTLY WEAKER
  liveness guarantee than the pip twin's own (a JS `setInterval` callback cannot fire during ANY
  synchronous JS execution, not only during OS-level whole-process descheduling, which is what a
  Python daemon thread can sometimes survive via GIL release). A clean PASS here, with no
  matching RISK-ACCEPTED/owner/ticket/expiry, would itself be the very npm/pip asymmetry this
  task exists to close — recommend the human apply the SAME RISK-ACCEPTED treatment (or
  explicitly decide this JS case differs enough from the pip precedent to warrant a plain PASS)
  rather than defaulting to PASS by omission.
Residue: whole-event-loop synchronous-starvation window (pre-existing risk class, inherited
  unchanged from the Python fix's own known limitation, honestly disclosed in 3 places, not newly
  introduced by this task; DIRECT PRECEDENT: pip twin recorded this as RISK-ACCEPTED then VOIDED
  once by real CI before a v3 fix resolved it — see above) — plus 2 advisory-only
  architecture/security notes (permanently-shipped test-only CLI flag; no empirical
  starvation-failure reproduction in this repo). None is security-class; none is a HARD-STOP; the
  concurrency residue is the human's PASS-vs-RISK-ACCEPTED call to make, informed by the twin's
  own history above.
Binding: advisory — architecture (this task's declared sensitivity; §6's own text: "Binding for
  sensitivity: mechanical ... advisory for all other sensitivities")

### GATE RECORD
Reported: yes — the gate report (refute-read + 3-lens verdict + explicit PASS/RISK-ACCEPTED/HARD-STOP
choice) was rendered in-chat before this outcome was recorded
Outcome: RISK-ACCEPTED
Owner: Tin Dang · Ticket: this file (`.add/tasks/js-reclaim-lock-heartbeat/TASK.md`) — mirrors the
pip twin (reclaim-ticket-race)'s own choice to carry the disclosed residue forward as this task's
own §7 Spec delta rather than a separate GitHub issue · Expires: on the next `v*.*.*` tag's
publish-workflow CI run — if the JS concurrency tests hold up there, the risk is resolved and this
waiver can be closed; if a real whole-event-loop-starvation failure is observed (mirroring the pip
twin's own CI-observed voiding), the waiver is VOID and this reopens as a P0 change request
Reviewed by: Tin Dang · date: 2026-07-05

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose `setInterval(() => fs.utimesSync(lockPath, now, now), interval)` heartbeat, cleared in the existing `release()` closure; rejected a `fs.watch`-based liveness signal — rejected, solves a different problem (file-change notification, not a self-refreshing timestamp) and adds platform-inconsistent behavior (fs.watch is notoriously inconsistent across macOS/Linux/Windows) · bumping `LOCK_STALE_DEFAULT`/`PROJECT_LOCK_STALE_DEFAULT` alone with no heartbeat — rejected, same reasoning the Python task's own Reject-R1 already ruled out: raises the false-positive bar but never fixes the structural race, and produces a materially slower self-heal from a genuine crash
- [human] freeze — froze §3 @ v1 (approved by Tin Dang, 2026-07-05 ("freeze as drafted"))
- [AI] build — strategy used: as planned, batches 1-6 in order, with two build-time decisions the plan left open: (1) the `--internal-acquire-lock` entrypoint's "slow critical section" is simulated via a NEW `sleepAsync` (setTimeout-based, event-loop-yielding) helper, never the codebase's existing `sleepSync` (Atomics.wait) — a synchronous block would starve the very event loop the `setInterval` heartbeat needs to fire on, which would make every contention test fail even post-fix (this is also the realistic shape: real slow Node work — network/fs I/O — is async, not a synchronous spin; the disclosed whole-event-loop-starvation residue is a DIFFERENT, already-named risk, not what this test simulates). (2) added a 6th test beyond the declared 5-test plan (`test_project_lock_slow_holder_survives_contention`) because Must #1 explicitly requires BOTH acquireUpdateLock AND acquireProjectLock protected, and none of the 5 planned tests exercised the `project` kind under contention. Batch 7 (widened ADD_LOCK_STALE_SECONDS re-run) was not needed — 3 consecutive full re-runs of the new suite were stable (no flake) at the chosen thresholds (300-400ms stale / 700-800ms pre-contend wait), a wider margin than strictly required.
- [human] verify — gate RISK-ACCEPTED (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] if the RISK-ACCEPTED waiver above voids (a real whole-event-loop-starvation
  failure observed on a future publish-workflow CI run), reopen as a P0 change request for a
  widened-threshold JS companion fix — mirrors the Python task's own v2→v3 progression (evidence:
  `reclaim-ticket-race`'s own CI-voided precedent, `.add/tasks/reclaim-ticket-race/TASK.md`)
- [SPEC · seeded] gate `--internal-acquire-lock` behind an additional env-var check (not just an
  undocumented flag) for defense-in-depth, per the add-verify agent's advisory security note
  (evidence: Security lens, non-blocking)

### Competency deltas
- [TDD · open] a surgical mutation of the fix (neuter only the causal line — here,
  `fs.utimesSync` — leaving the rest of the wiring intact) is a stronger earned-green refute-read
  than static review or a plain revert-and-rerun: it isolates whether the SPECIFIC mechanism is
  what the test suite is actually detecting, not just whether the suite is sensitive to unrelated
  code churn (evidence: this task's refute-read regressed exactly the 3 contention tests, leaving
  the unrelated exit-boundedness test green, proving test-level specificity)
- [ADD · open] the adr-harvester-multiline-fields fix (this session, commit `731755f`) correctly
  harvested this task's own multi-paragraph "Strategy actually used" field into the §7 ADR block
  above without truncation or bleed into the next field — a real in-production confirmation of
  that fix, not just its own fixture tests (evidence: §7 Decisions (ADR) `[AI] build` line above)

