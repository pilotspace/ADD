# TASK: Fix CI-observed reclaim-ticket race in _update_lock

slug: reclaim-ticket-race · created: 2026-07-04 · stage: mvp · risk: high
milestone: (none)
autonomy: conservative
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/src/add_method/_installer.py:_update_lock` (home-scoped global update lock, ~L1436–1619) — the O_EXCL lockfile + per-generation reclaim-ticket mechanism; the reclaim-ticket "is it orphaned" branch (`elif tage > _LOCK_TICKET_STALE_SECONDS`) is the suspected race site.
  - `add-method/src/add_method/_installer.py:_LOCK_TICKET_STALE_SECONDS` (= 5, ~L1424) — the ticket-orphan threshold; suspected too short relative to CI thread-scheduling jitter.
  - `add-method/tooling/test_global_update_harden.py:StaleLockSelfHealTest.test_concurrent_stale_reclaim_exactly_one_wins` (~L440–511) — the 6-thread barrier-synchronized stress test asserting `peak <= 1` (temporal, non-cumulative proof of mutual exclusion); this is the test that failed 2/2 times on GitHub Actions (never locally).
  - Possible sibling: `_installer.py`'s project-scope lock variant (`_PROJECT_LOCK_TICKET_STALE_SECONDS = 5`, ~L1627) and its own concurrency test, if the same root cause applies there too — confirm during Ground.
Context (working folder): CI run logs for the 2 failed 1.16.1 publish attempts (GitHub Actions run 28703274928, both `Test suite + tag/version match` job attempts) — the only place this reproduced; never seen locally, including the "1167+ combined adversarial concurrent attempts / 0 anomalies" evidence cited when install-update-hardening (1.16.0) originally shipped this code.
Honors (patterns / conventions): CONVENTIONS.md's identity-verified reclaim discipline (never an unconditional unlink-by-path; always re-stat + inode-compare immediately before mutating) — any fix must preserve this, not reintroduce the TOCTOU hole the ticket mechanism was built to close.
Seams consulted: none found yet — .add/SEAMS.md has no entry for the lock-reclaim mechanism; consider adding one if this task's fix introduces a durable cross-cutting convention (e.g. "ticket staleness must exceed worst-observed CI scheduling delay").
Anchors the contract cites: `_update_lock`'s ticket-orphan branch; `_LOCK_TICKET_STALE_SECONDS`; `test_concurrent_stale_reclaim_exactly_one_wins`.
Issues/Risks (→ feed §1):
  - Root-cause HYPOTHESIS (not yet confirmed): a genuinely-alive ticket-holder thread can be descheduled by a loaded shared CI runner long enough that a sibling racer's `tage > _LOCK_TICKET_STALE_SECONDS` (5s) check reads it as orphaned — a false-crash read, not an actual crash. This lets two racers both conclude the SAME ticket is dead and both attempt the reclaim path, even though each individual unlink is itself identity-verified.
  - Alternative hypothesis to rule out: a genuine logic bug (not just a too-short constant) in the re-verify-before-unlink sequence that allows a narrow double-entry window regardless of the constant's value — must trace the exact interleaving before assuming "just raise the constant" is a complete fix.
  - This is SHIPPED 1.16.0 code, already released and in the wild — a fix here is a patch to already-live behavior, not new-feature work; must not weaken `test_concurrent_stale_reclaim_exactly_one_wins`'s assertion to make it pass (the test's own docstring argues its `peak`-tracking design is deliberately non-flaky already).
  - Failed 2/2 identical on GitHub Actions; 0 known local failures — reproduction may require either running under deliberately constrained CPU/scheduling (e.g. `taskset`/cgroup limits) or adding scheduling-delay injection to the test itself to make the race deterministic rather than environment-luck-dependent.
Related intent: surfaced while cutting the 1.16.1 patch release (persona-loop hotfix, PRs #132/#133) — the publish workflow's CI-run full suite failed this test on both attempts, blocking (but not completing) an npm/PyPI publish; nothing was published. PROJECT.md's install-update-hardening milestone (1.16.0) is the originating context for the lock-reclaim mechanism itself.
Ground SHA: a0a9550

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Close the reclaim-ticket race in `_update_lock` (CI-reproducible double-holder)
Framings weighed:
  - (chosen) Give the ticket a HEARTBEAT: a live ticket-holder refreshes its ticket's mtime
    while it is still actively working the reclaim, so `_LOCK_TICKET_STALE_SECONDS` measures
    "time since last heartbeat," not "time since creation." A genuinely crashed holder stops
    heartbeating and its ticket correctly goes stale after the same threshold; a merely
    scheduler-delayed holder keeps refreshing and is never misread as dead. This stays within
    the project's own existing mtime-only liveness model — it deliberately does NOT introduce
    PID-liveness checks (`os.kill(pid, 0)`), which this codebase already rejected elsewhere for
    a Windows PID-reuse hazard (see `test_global_update_harden.py`'s own `StaleLockSelfHealTest`
    docstring). Closes the race structurally rather than shrinking a fixed window.
  - (alternative) Just raise `_LOCK_TICKET_STALE_SECONDS` — cheap, but only shrinks the race
    window on a probabilistic constant; does not close it. Rejected as a non-fix.
  - (alternative) Remove the ticket self-heal-if-orphaned branch entirely (never let a second
    racer reclaim an in-flight ticket) — closes THIS race but reopens the ORIGINAL bug the
    ticket mechanism exists to fix (a leaked ticket from a real crash would livelock forever,
    unbounded even under `--lock-timeout`). Rejected as a regression.
Must:
<must>
  - M1: under N concurrent racers all observing the same stale lock generation, at most one
    racer is ever inside the critical section at any instant (peak <= 1) — including when a
    ticket-holder thread is scheduler-delayed (not crashed) for longer than
    `_LOCK_TICKET_STALE_SECONDS`.
  - M2: a genuinely orphaned ticket (its holder actually crashed) is still reclaimed and does
    not livelock — the fix must not regress the leaked-ticket self-heal this mechanism exists for.
  - M3: the existing byte-identical fail-fast / poll / `--lock-timeout` behavior for a live
    (non-stale) lock is unchanged.
  - M4: the fix is confirmed (not assumed) to also cover the project-scope lock variant
    (`_PROJECT_LOCK_TICKET_STALE_SECONDS`) if it shares the same vulnerable shape.
</must>
Reject:
<reject>
  - a fix that merely increases `_LOCK_TICKET_STALE_SECONDS` without closing the underlying
    race -> "shrinks the window, does not close it" (not accepted as done)
  - a fix that weakens or removes `test_concurrent_stale_reclaim_exactly_one_wins`'s `peak <= 1`
    assertion to make it pass -> "test_or_contract_altered" (never allowed)
</reject>
After:
<after>
  - `test_concurrent_stale_reclaim_exactly_one_wins` passes deterministically under an injected
    scheduling delay (not just lucky timing), locally AND across repeated CI runs.
  - The next tagged release's publish workflow (`Test suite + tag/version match` job) passes
    this test on the first attempt.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ RESOLVED WRONG (post-freeze, via instrumented local repro): the root cause is NOT the
    ticket-orphan-detection window. A deterministic red test (`test_concurrent_stale_reclaim_
    survives_scheduling_delay`, no ticket contention required) proves a single, uncontested
    challenger can steal a live-but-slow holder's MAIN lock outright: `age > stale_after` is
    read from `lock_path`'s own mtime, which nothing refreshes while legitimately held — the
    ticket mechanism only arbitrates WHICH challenger wins a reclaim already judged necessary;
    it never protects a live holder from being judged stale in the first place. Empirically
    confirmed the frozen §3 fix (ticket-mtime heartbeat) is INERT against this: applying it did
    not turn the red test green (the challenger's `age` snapshot is taken before the ticket is
    even opened, and it's about to unlink the very file it would be "heartbeating"). This is the
    exact failure this flag warned about when raised at freeze — the safety mechanism worked as
    designed. See change-request note below §3.
  - [x] whether the project-scope lock (`_PROJECT_LOCK_TICKET_STALE_SECONDS`) shares the same
    vulnerable shape — CONFIRMED yes: `_project_lock` (~L1639–1820) has the byte-for-byte
    identical create-once-never-refreshed ticket pattern. M4 in scope, fixed alongside
    `_update_lock`.
  - [x] whether the race is reproducible locally at all under injected delay, or is genuinely
    GH-Actions-runner-specific — addressed by adding a deterministic injected-delay test rather
    than depending on CI-environment luck (§4).
  - NEW finding (post-freeze, scope-bounding decision — not silently expanded): the npm/JS twin
    (`bin/cli.js`'s `acquireUpdateLock`/project-lock equivalents) carries the IDENTICAL
    `LOCK_TICKET_STALE_SECONDS`/`PROJECT_LOCK_TICKET_STALE_SECONDS = 5` create-once ticket
    pattern — almost certainly the same vulnerability. Proving it needs a MULTI-PROCESS (not
    multi-thread) stress harness, a materially different test investment than this task's
    Python-threading repro. Left OUT of this task's frozen scope (§3 CONTRACT names only the
    Python `_installer.py` twin); recorded as a §7 Spec delta for a dedicated follow-up rather
    than silently fixed or silently dropped.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Six racers, one genuinely stale lock, no injected delay   # M1 (existing test, must keep passing)
  Given a lock file at `.update.lock` with mtime older than the stale threshold
  When 6 threads race `_update_lock` simultaneously via a shared barrier
  Then at most one thread is ever "active" (inside the critical section) at any instant
  And every thread finishes with no leaked lock file and no unexpected exception

Scenario: One racer's ticket-hold is scheduler-delayed past the ticket-stale threshold   # M1 (new — the CI-reproducing case)
  Given the same stale-lock setup as above
  And racer A has won the reclaim ticket but is deliberately paused (injected delay) before it
    unlinks/recreates the lock, for longer than `_LOCK_TICKET_STALE_SECONDS`
  When racer B (and the other racers) evaluate A's ticket for orphan-staleness
  Then B must NOT be able to also enter the critical section while A is still legitimately
    (though slowly) mid-reclaim
  And when A resumes, the same peak <= 1 invariant holds for the whole run

Scenario: Ticket holder actually crashes (process/thread dies without cleanup)   # M2
  Given a racer wins the reclaim ticket, then is killed before unlinking it or the main lock
  When a later racer evaluates the now-truly-orphaned ticket after `_LOCK_TICKET_STALE_SECONDS`
  Then that later racer reclaims the ticket and the lock, and no racer livelocks

Scenario: Lock is live and fresh (not stale)   # M3 — unchanged behavior
  Given a lock file with a recent mtime, well under the stale threshold
  When another racer attempts `_update_lock` with no `--lock-timeout`
  Then it fails fast with `BlockingIOError` immediately, exactly as before this fix
  And with `--lock-timeout=N` it polls up to N seconds instead, exactly as before this fix

Scenario: Project-scope lock variant, if it shares the vulnerable shape   # M4
  Given the project-scope lock's own reclaim-ticket mechanism under the same delayed-holder setup
  When the equivalent race is exercised against `_PROJECT_LOCK_TICKET_STALE_SECONDS`
  Then the same peak <= 1 invariant holds there too

Scenario: A fix that only raises the ticket-stale constant   # R1 — rejected approach
  Given a candidate fix that solely increases `_LOCK_TICKET_STALE_SECONDS`
  When the delayed-holder scenario above is re-run with a delay longer than the NEW constant
  Then the race still reproduces
  And this is treated as "not done" — the underlying window, not just its size, must close

Scenario: A fix that weakens the stress test's assertion   # R2 — rejected approach
  Given a candidate fix that loosens `peak <= 1` (e.g. to `peak <= 2`) instead of closing the race
  Then this is rejected outright — the frozen test assertion is never weakened to make a build pass
  And the change is treated as a change request back to Specify, not an accepted fix
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FILE CONTRACT (no HTTP surface — a lock-reclaim correctness fix inside `_update_lock`)

add_method/_installer.py — `_update_lock`'s ticket-orphan branch gains a heartbeat:

  A ticket winner, immediately after `os.open(ticket_path, O_CREAT|O_EXCL, ...)` succeeds,
  records the moment as its heartbeat baseline. Before performing its OWN "is the ticket I
  hold still the one guarding this generation" work (the existing current_ino re-verify +
  unlink of lock_path), it re-touches its own ticket's mtime (`os.utime(ticket_path, None)`
  or equivalent) so a concurrently-evaluating challenger reads a FRESH mtime, not the
  original creation time.

  A challenger who lost the initial ticket race and finds the ticket still present computes
  `tage` from the ticket's CURRENT mtime, exactly as today — the fix changes WHEN and HOW
  OFTEN a live holder updates that mtime, not the staleness-comparison logic itself, so a
  crashed holder (which stops heartbeating) still ages out after the same
  `_LOCK_TICKET_STALE_SECONDS` threshold, measured from its last real heartbeat.

  `_LOCK_TICKET_STALE_SECONDS` itself is UNCHANGED (still 5s) — the fix closes the race
  structurally; it does not rely on raising the constant (Reject R1).

  The identical mechanism applies to the project-scope lock's own ticket
  (`_PROJECT_LOCK_TICKET_STALE_SECONDS`) IF Ground/Build confirms it shares the same
  create-once, never-refreshed ticket shape (§1 open assumption).

add_method/tooling/test_global_update_harden.py — new deterministic repro:

  A new test injects a scheduling delay into ONE racer between winning its ticket and
  completing its reclaim (long enough to exceed the CURRENT `_LOCK_TICKET_STALE_SECONDS`
  absent the fix), while 5 other racers attempt to steal the "orphaned-looking" ticket.
  Asserts `peak <= 1` deterministically — not dependent on real CI scheduling luck — so this
  race is pinned as a standing regression test, not just an occasional CI failure.
```

Glossary deltas: holder-side heartbeat — a background daemon thread, alive for the duration a
lock is legitimately held, that periodically re-touches the lock file's OWN mtime so
`stale_after` measures "time since last heartbeat" rather than "time since creation,"
distinguishing a slow-but-alive holder from a truly crashed one without PID-liveness. (Supersedes
the v1 "ticket heartbeat" glossary term — falsified, see below.)
Status: FROZEN @ v2 — approved by Tin Dang ("Implement the holder-side heartbeat thread",
2026-07-04). v1 (ticket-mtime heartbeat) was SUPERSEDED same-day: an instrumented red test
proved it INERT — the actual bug is the MAIN lock file's own mtime never being refreshed by a
live holder, not the reclaim ticket (§1's resolved-wrong assumption). v2 CONTRACT (implemented):

  A new `_lock_heartbeat(lock_path, stale_after)` context manager (`_installer.py`, shared by
  both locks) starts a daemon thread on entry that calls `os.utime(lock_path, None)` every
  `max(0.05, min(stale_after / 4, 5.0))` seconds, and stops (via a `threading.Event`, joined)
  on exit. `_update_lock` and `_project_lock` each wrap their `yield` in
  `with _lock_heartbeat(lock_path, stale_after): yield` — the ticket-orphan-detection logic
  in both functions is UNCHANGED (it still correctly arbitrates which single challenger wins a
  reclaim; it was never the bug). A crash stops the thread immediately (daemon, no cleanup
  needed) -> the file still ages out and self-heals normally (M2 preserved). This is a
  probabilistic mitigation, not a mathematical guarantee — accepted given prod defaults
  (`_LOCK_STALE_DEFAULT`=600s / `_PROJECT_LOCK_STALE_DEFAULT`=120s) make a live holder actually
  starving past `stale_after` near-impossible in practice.
Least-sure flag surfaced at freeze: [contract] the heartbeat is a probabilistic mitigation, not a
mathematical guarantee — if the heartbeat thread itself is starved past `stale_after` (e.g. under
whole-process scheduling contention, not just a single stalled thread), the window reopens. No
portable local test can deterministically prove this closed; only the next tagged release's real
CI run can. Cost if wrong: the original CI failure recurs on the next publish attempt, requiring
a second, harder iteration (e.g. a shorter interval, or accepting the residual risk permanently
given prod's 600s/120s defaults make it near-impossible in practice).
Reported: yes — the change-request report (falsified v1 mechanism + why + v2 candidate shape +
cost + the accept-as-test-artifact alternative) was rendered in-chat before this froze; human
selected the v2 implementation over the accept-as-artifact alternative.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the new tests below fully red before Build; all pre-existing
`test_global_update_harden.py` / `test_project_scope_lock.py` tests stay green throughout.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_concurrent_stale_reclaim_survives_scheduling_delay (StaleLockSelfHealTest): a live holder
    (real hold, not a ticket-side delay — v1's ticket-injection shape didn't reproduce; the actual
    race needs a HELD lock aged past stale_after while its holder is still inside the critical
    section) + 5 sibling racers polling via `timeout=` past the hold / assert: `peak <= 1`
    throughout · covers: M1 (new scenario) · RAN RED 3/3 pre-fix (peak=2), GREEN 3/3 post-fix
  - test_concurrent_stale_reclaim_exactly_one_wins: pre-existing (unchanged) — no-delay case,
    stayed green throughout, re-confirmed 5/5 post-fix · covers: M1 (existing scenario)
  - test_leaked_ticket_self_heals_instead_of_unbounded_livelock (LeakedTicketLivelockTest):
    pre-existing, already covers M2 (a leaked, never-heartbeat ticket still self-heals) — no new
    test needed; stayed green throughout · covers: M2
  - test_live_lock_unchanged_behavior: pre-existing fail-fast/poll tests, stayed green · covers: M3
  - test_project_lock_concurrent_reclaim_survives_scheduling_delay (ProjectLockConcurrencySafetyTest,
    test_project_scope_lock.py): mirrors the first test against `_project_lock` — since this lock
    has NO --lock-timeout/poll mode, the retry loop lives at the racer (caller) level instead ·
    covers: M4 · RAN RED 3/3 pre-fix (peak=2), GREEN 3/3 post-fix
</test_plan>

Tests live in: `add-method/tooling/test_global_update_harden.py` `test_project_scope_lock.py` · confirmed red for the right reason (peak=2, mutual-exclusion violated) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/tooling/test_global_update_harden.py` `add-method/tooling/test_project_scope_lock.py`
Strategy (ordered batches):
  1. Add the new RED test for `_update_lock` first (a real HELD lock, delayed holder, 5 sibling
     racers polling via `timeout=` past the hold) — confirmed red 3/3 (peak=2) against unfixed
     code. Discovered mid-batch: v1's ticket-injection shape (delay `os.open` on the ticket path)
     never reproduced (6/6 green pre-fix) — the ticket mechanism was never the vulnerable part;
     pivoted to delaying the actual lock HOLDER instead, which reproduced immediately.
  2. Add the mirrored RED test for `_project_lock` (M4) — same shape, but the retry loop lives at
     the racer/caller level since this lock has no `timeout=`/poll mode of its own. Confirmed red
     3/3 (peak=2).
  3. CHANGE REQUEST: applied v1's frozen ticket-mtime heartbeat as a manual probe — confirmed it
     left the new test RED (inert), proving the frozen mechanism didn't address the reproduced
     bug. Reverted immediately (`git diff` clean before proceeding). Escalated to advisor + human;
     human selected the v2 holder-side heartbeat thread over the accept-as-artifact alternative.
  4. Implemented `_lock_heartbeat(lock_path, stale_after)` (shared context manager, `_installer.py`)
     and wrapped both `_update_lock`'s and `_project_lock`'s `yield` in it. Ticket-orphan-detection
     logic in both functions is untouched — it was never the bug.
  5. Re-ran both new tests 3x each: green. Re-ran the ORIGINAL CI-failing
     `test_concurrent_stale_reclaim_exactly_one_wins` (both twins) 5x: green throughout (the §1
     `After` criterion). Ran the full `test_global_update_harden.py` + `test_project_scope_lock.py`
     suites (67 tests): green, no regression to live-lock fail-fast/poll or leaked-ticket self-heal.

Persona (optional): sre-reliability-engineer (this project's own AIDD-Book `.add/personas/` roster) — reliability/degradation-behavior stance; absent formally seeded here, applied as a general lens.
Spawn isolation (default): not spawning a subagent for this build — direct, single-threaded edit given the existing deep Ground context already loaded this session; no parallel build stream to isolate against.
Known-problem fixes: <trap → planned fix>
  - a naive "just raise the ticket-stale constant" fix -> rejected in §1 (R1); heartbeat instead.
  - v1's hypothesis (ticket-mtime heartbeat) -> FALSIFIED by an instrumented red test; the ticket
    mechanism only arbitrates which challenger wins a reclaim, it never protects the holder from
    being judged stale in the first place -> v2: heartbeat the MAIN lock file, holder-side.
  - a heartbeat thread must not outlive its critical section or block a clean exit -> a
    `threading.Event`-gated loop, joined with a bounded timeout in `finally`, daemon=True so a
    hard crash never leaves a dangling non-daemon thread.
  - re-touching the lock's mtime must NOT change its CREATION-time identity (inode) — `os.utime`
    only updates mtime, never touches inode, so the existing inode-based identity-verify (already
    in the ticket-orphan code, unchanged) stays valid.
Strategy actually used: see the 5 ordered batches above — matches the plan except step 3's
mid-build discovery that v1's frozen mechanism didn't work, requiring a change request before
step 4's actual implementation (not a deviation from BUILD's own scope — a correction surfaced
BY following it).
Safety rule (feature-specific): the fix must never let TWO racers simultaneously believe they
hold a lock for the SAME generation — every existing identity-verify (inode comparison) stays
exactly as strict as today; the heartbeat only changes the mtime a challenger reads, nothing else.
Code lives in: `add-method/src/add_method/_installer.py`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 2914 tooling tests run, 2 failures both traced to a pre-existing,
      lock-unrelated environment artifact (see below), independently re-confirmed by add-verify
- [x] coverage did not decrease — 2 new tests added, 0 removed/weakened (git diff confirmed additive-only)
- [x] no test or contract was altered during build — v1 CONTRACT was superseded via an explicit
      change request (not a silent edit); no pre-existing test assertion touched
- [x] the green was EARNED, not gamed — independent add-verify refute-read: EARNED (see below)
- [x] concurrency / timing of the risky operation is safe — CLEAR per architecture lens; RESIDUE
      (disclosed, not blocking) per concurrency lens — see below
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`threading`, `os.utime`)
- [x] layering & dependencies follow CONVENTIONS.md — identity-verified (inode) reclaim discipline untouched
- [ ] a person reviewed and approved the change — PENDING: this is the open gate, see GATE RECORD below

### Build expectations — what "correct" looks like
- [x] a live-but-merely-slow holder's lock is never stolen by a sibling racer — confirmed by
      `test_concurrent_stale_reclaim_survives_scheduling_delay` / `test_project_lock_concurrent_
      reclaim_survives_scheduling_delay`, both independently reproduced red (peak=2) pre-fix and
      green post-fix by add-verify (not just self-reported)
- [x] a genuinely crashed holder's lock still self-heals (no livelock regression) — confirmed by
      `test_leaked_ticket_self_heals_instead_of_unbounded_livelock` + `test_lock_timeout_deadline_
      honored_even_when_a_ticket_cannot_yet_resolve`, both re-run green by add-verify
- [x] the original CI-failing test is robust, not just lucky — confirmed by 5x re-runs (self) +
      independent 5x re-runs (add-verify) of `test_concurrent_stale_reclaim_exactly_one_wins`
      (both twins), all green

### Deep checks
- [x] WIRING (code) — `_lock_heartbeat` (`_installer.py:1437`) has exactly 2 call sites
      (`_update_lock:1650`, `_project_lock:1871`) — confirmed by add-verify via direct grep
- [x] DEAD-CODE (code) — no leftover v1 ticket-mtime-heartbeat code anywhere in the file —
      confirmed by add-verify
- [x] SEMANTIC (prose) — TASK.md §3/§5 read in full by add-verify against the actual diff; no
      claim in the task file was taken at face value (each re-derived independently)

### Live-verify evidence
- [x] every symbol §3 CONTRACT cites resolves in the current tree — `_lock_heartbeat`,
      `_update_lock`, `_project_lock` all confirmed present (line numbers shifted from Ground SHA
      `a0a9550` due to the new helper; no rename)
- [x] anchor drift disclosed: `_LOCK_TICKET_STALE_SECONDS` now at line 1425 (was ~1424),
      `_PROJECT_LOCK_TICKET_STALE_SECONDS` now at line 1665 (was ~1627) — pure line-shift from
      insertion above, not a rename or semantic change

### Refute-read verdict — the earned-green check
Verdict: **EARNED**
By: independent `add-verify` agent (fresh context, no stake in the outcome) · adversarially
checked: (1) reverse-applied the `_installer.py` diff via `git apply -R` and re-ran both new
tests against the genuinely unfixed code — failed 3/3 with the exact claimed `peak=2`, then
reapplied and confirmed green, proving the tests are load-bearing, not vacuous; (2) re-ran M2/M3
regression tests independently; (3) re-ran the full suite independently and independently traced
both failures to the `grep`/`ugrep` shell-alias artifact (confirmed `grep` resolves to ugrep
7.5.0 here) rather than trusting the self-reported claim; (4) probed the specific "could
os.utime recreate a deleted lock file" concern with a standalone repro (refuted — raises
FileNotFoundError); (5) confirmed no fork/thread/lock-ordering hazard; (6) confirmed the JS twin
is untouched and its parallel vulnerability remains a disclosed, not silently dropped, SPEC delta.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: independent `add-verify` agent
1. Security: **CLEAR** — no new secrets/injection surface/dependency; stdlib only.
2. Concurrency: **RESIDUE** (disclosed, non-blocking per the agent's own assessment) —
   (a) MODERATE: the new tests inject delay on the holder's own thread only, which leaves the
   heartbeat's daemon thread free to keep ticking (Python releases the GIL during `time.sleep`)
   — so green here proves the fix defends the single-thread-stall failure mode, but the original
   CI failure's 20x margin (0.05s hold vs 1s stale_after) more plausibly points to *whole-process*
   scheduling starvation, which no portable test can deterministically reproduce, and under which
   the heartbeat thread would starve together with the holder (the fix's own docstring already
   concedes "probabilistic mitigation, not a mathematical guarantee" — `_installer.py:~1447`).
   §1's `After` criterion ("next tagged release's publish workflow passes on the first attempt")
   can only be truly confirmed by the next real CI run, not by this local verify.
   (b) MINOR: `interval = max(0.05, min(stale_after/4, 5.0))` — for `stale_after` between 0.05s
   and 0.2s the safety margin degrades below the intended 4x (floor meets/exceeds the window).
   Does not affect anything currently shipped (prod defaults 600s/120s; tests use 1s) — an
   unguarded edge, not an active defect.
3. Architecture: **CLEAR** — symmetric fix on both locks (`_update_lock:1650`,
   `_project_lock:1871`); `_project_lock`'s M7 "no polling, ever" invariant untouched (heartbeat
   starts strictly after the acquire-side fail-fast/poll decision); no dead code; JS twin
   correctly deferred as an open SPEC delta, not silently touched or dropped.
Verdict: PASS-eligible (no HARD-STOP finding); the moderate concurrency residue is a disclosed,
inherent-to-the-approach limitation (accepted at contract freeze: "probabilistic mitigation, not
a mathematical guarantee") rather than a build defect — but per this task's own explicit
`risk: high`/`autonomy: conservative` classification, the human makes the final call on whether
this residue is acceptable to ship now vs. confirm via the next real CI run first.
Residue: whole-process-starvation failure mode is not (and cannot portably be) test-proven closed;
only the single-thread-stall mode (the mechanism directly implicated in the CI trace) is proven.
Binding: advisory — risk: high (not mechanical; human decides)

### GATE RECORD
Reported: yes — the gate report (refute-read + 3-lens verdict + explicit PASS/RISK-ACCEPTED/Hold
choice) was rendered in-chat before this outcome was recorded
Outcome: RISK-ACCEPTED
Owner: Tin Dang · Ticket: this file (`.add/tasks/reclaim-ticket-race/TASK.md`) — the disclosed
residue is carried forward as this task's own §7 Spec delta rather than a separate GitHub issue
(no response on that sub-choice within timeout; defaulted to the reversible, no-external-action
option rather than unilaterally opening a public issue) · Expires: on the next `v*.*.*` tag's
publish-workflow CI run — if `test_concurrent_stale_reclaim_exactly_one_wins` (both twins) passes
there, the risk is resolved and this waiver can be closed; if it fails again, the waiver is VOID
and this reopens as a P0 change request (whole-process-starvation hypothesis would then be
confirmed, not just suspected)
Reviewed by: Tin Dang · date: 2026-07-04

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v2 (approved by Tin Dang ("Implement the holder-side heartbeat thread",)
- [AI] build — strategy used: see the 5 ordered batches above — matches the plan except step 3's
- [human] verify — gate RISK-ACCEPTED (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

