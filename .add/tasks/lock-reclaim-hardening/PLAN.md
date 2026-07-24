# PLAN: Harden _update_lock stale-reclaim: peak<=1 holds under publish-job load

slug: lock-reclaim-hardening · created: 2026-07-24 · stage: mvp · risk: high
milestone: lock-reclaim-hardening
sensitivity: architecture
autonomy: conservative
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: make `_installer._update_lock`'s stale-reclaim path pass `peak<=1` (mutual exclusion) DETERMINISTICALLY under the publish-job's concurrent load, so `test_concurrent_stale_reclaim_exactly_one_wins` / `_survives_scheduling_delay` stop flaking and the release publish gate is reliable.
Framings weighed: (a) fix a residual TOCTOU/double-hold in the reclaim path (chosen IF a real overlap is reproducible locally under load — the peak-tracking in the test is correctly synchronized, so peak=2 is a genuine momentary double-hold when it occurs) · (b) prove the failure is a CI-filesystem O_EXCL-atomicity artifact (overlayfs/tmpfs not honoring O_EXCL atomically) and make the test assert only what the FS guarantees — WITHOUT weakening the `peak<=1` contract (e.g. detect non-atomic-O_EXCL filesystems and xfail there, keeping the guarantee on real filesystems) · (c) do nothing / keep RISK-ACCEPTED (rejected — it now BLOCKS the publish gate, not just a PR).
Context (CI evidence, 2026-07-24): failed 2/2 on `publish.yml`'s "Test suite + tag/version match" gate under load (runs alongside the fresh-checkout materialize suite); PASSED both py3.10+3.12 on #178's normal `ci.yml`. `_update_lock` (add-method/src/add_method/_installer.py:1466) is already heavily hardened: per-generation inode reclaim tickets (`.reclaim-<st_ino>`), re-stat-before-unlink identity checks, deadline handling. So the remaining failure is subtle — a deep residual race OR an FS-atomicity artifact.
Must:
<must>
  - M1 the two concurrency tests pass deterministically across ≥20 consecutive runs under artificial load locally, AND on the publish.yml gate
  - M2 the `peak<=1` mutual-exclusion contract is NEVER weakened — O_EXCL stays the sole arbiter; any test change must preserve the temporal double-hold detection
  - M3 if the cause is FS-level (non-atomic O_EXCL), the resolution DETECTS that filesystem and scopes the assertion honestly (xfail/skip with a named reason), never a blanket skip
  - M4 no regression to the lock's existing guarantees (fail-fast BlockingIOError, --lock-timeout polling, no leaked lock/ticket, cross-twin npm/pip serialization)
</must>
Reject:
<reject>
  - weakening `peak<=1` to `count==1` or removing the temporal check to make it pass -> "weakened_mutual_exclusion"
  - a blanket unconditional skip of the concurrency tests -> "silent_skip"
</reject>
After:
<after>
  - the v2.4.0 publish (already tagged on main @ 7490603f, unpublished) can be re-run and reaches npm+PyPI green
  - the release publish gate no longer flakes on this test class
Boundary: two environments the fix must hold in — a normal single-suite CI runner (already green) AND the publish job's concurrent multi-suite load (currently 2/2 red).
<assumptions>
  ⚠ ROOT CAUSE CONFIRMED (2026-07-24): it is a genuine code bug — **inode-number reuse**, NOT an O_EXCL-atomicity artifact. The reclaim's re-stat-before-unlink guard (`current_ino == st.st_ino`, _installer.py:1610) trusts that a fresh replacement lock file always gets a NEW inode (its own comment at :1521 asserts this). FALSE on Linux ext4/tmpfs, which aggressively REUSE freed inode numbers; TRUE on macOS APFS (64-bit, no short-window reuse) — which is exactly why it fails only on the Linux CI runner and never locally (0/80 under heavy macOS oversubscription this session). The race: racer A reclaims stale inode I, recreates a fresh lock file that REUSES inode I, enters its CS; delayed racer B (still holding the crashed generation's st.st_ino=I) wins the ticket, re-stats → I==I ✓ → unlinks A's LIVE file → both hold → peak=2. Residual assumption: mtime is a reliable generation discriminator on the CI FS (a fresh reused-inode file has mtime≈now vs the crashed file's aged mtime) — true on ext4/tmpfs (fine ns mtime, and here the gap is ~100s).
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
EDIT add-method/src/add_method/_installer.py (+ the build/ twin if tracked) — the
stale-reclaim UNLINK guard must re-verify STALENESS, not just inode identity:

  NEW helper (module-level, near _aged_reclaim_tickets):
    def _still_stale_generation(path, observed_ino, stale_after, now=None):
        """True iff `path` is STILL the exact stale generation identified by
        observed_ino AND still stale. Inode number alone is NOT a stable identity
        across delete+recreate — Linux (ext4/tmpfs) REUSES freed inode numbers, so a
        fresh replacement lock can reuse the crashed file's inode. Re-verifying that
        the CURRENT file is itself still stale (mtime age > stale_after) distinguishes
        a live reused-inode holder from the crashed generation we meant to reclaim."""
        now = time.time() if now is None else now
        try:
            cur = path.stat()
        except OSError:
            return False
        return cur.st_ino == observed_ino and (now - cur.st_mtime) > stale_after

  WIRE it at the lock-reclaim unlink (the `current_ino == st.st_ino` guard, ~1610):
    replace the inode-only test with
      if _still_stale_generation(lock_path, st.st_ino, stale_after):
          os.unlink(str(lock_path))
    so a fresh reused-inode file (age ~0 < stale_after) is NEVER unlinked.

  APPLY the same discipline to the orphan-TICKET unlink (~1574): re-verify the ticket
    is still its observed inode AND still aged past _LOCK_TICKET_STALE_SECONDS before
    unlink (same reuse class, one level down) — reuse the helper.

INVARIANT preserved: O_EXCL stays the SOLE mutual-exclusion primitive; a genuinely
crashed stale lock (aged mtime, no heartbeat) still reclaims exactly as before. The fix
only STOPS a live reused-inode file from being mistaken for the crashed generation.
NOT changed: no new lock primitive (no flock/link rewrite), no test weakened.
```

Target (measurable): `test_concurrent_stale_reclaim_exactly_one_wins` + `_survives_scheduling_delay` pass deterministically (≥20 consecutive local runs green + the publish.yml gate green); a NEW deterministic unit test proves `_still_stale_generation` returns False for a same-inode-but-fresh file (the reused-inode-live-holder case) and True for a genuinely-aged same-inode file — red before the helper exists, green after; full `tooling/` suite green; a genuinely crashed stale lock still self-heals (existing empty/stamped stale-lock reclaim tests stay green).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/tooling/test_lock_reclaim_hardening.py` `add-method/bin/cli.js` `./tests/`
Regression floor: the full `tooling/` suite via CI's `unittest discover` — especially test_global_update_harden (the reclaim/self-heal suite), test_js_reclaim_lock_heartbeat (the JS twin's heartbeat guard) and the project-lock sibling tests must stay green; the fix must not regress the crashed-lock self-heal path in EITHER twin.

Scope WIDENED post-freeze (re-cross, approved by Tin Dang 2026-07-24): the JS/npm twin `bin/cli.js` carries the IDENTICAL inode-identity reclaim guard at four sites (1438 · 1467 · 1601 · 1629 — ticket + main lock in each of acquireUpdateLock/acquireProjectLock), i.e. the same reused-inode double-hold. `bin/cli.js` is the npm install path users actually run, so gating on the Python fix alone would ship a half-fix. Same helper, mirrored.
Persona (optional): `.add/personas/methodology-engine-dev.md` — the engine/concurrency lens.

Least-sure flag surfaced at freeze: [contract] whether re-checking STALENESS (mtime age) is the right discriminator vs. capturing (st_ino, st_mtime_ns) identity at observation. Chosen staleness re-check: it directly encodes the true invariant ("only unlink a file that is STILL a stale lock"), also covers the heartbeat case (a live holder refreshing mtime is spared), and needs no threading of the observed mtime through the ticket dance. Residual risk: a coarse-mtime filesystem could blur a just-created file's age — mitigated because the reclaim margin here is the stale_after threshold itself (≥8s in tests, 600s prod), far above any FS mtime granularity.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_reused_inode_live_file_not_reclaimable: `_still_stale_generation(path, ino, stale_after)` returns False for a file whose inode equals the observed stale inode BUT whose mtime is now fresh (the reused-inode live holder) — the exact double-hold trigger · covers: M2, R:weakened_mutual_exclusion
  - test_genuinely_stale_same_inode_is_reclaimable: returns True for a same-inode file still aged past stale_after (a real crashed lock must still self-heal) · covers: M4
  - test_vanished_file_not_reclaimable: returns False when the path no longer exists (OSError → not a target) · covers: M4
  - test_concurrent_stale_reclaim_exactly_one_wins: (EXISTING, in test_global_update_harden) peak<=1 holds — kept as the integration guard; must stay green post-fix · covers: M1, M2
  - test_crashed_stale_lock_still_self_heals: (EXISTING self-heal tests in test_global_update_harden) a genuinely stale empty/stamped lock is still reclaimed — no regression · covers: M4
  - test_js_reused_inode_live_file_not_reclaimable: the JS twin's `stillStaleGeneration(p, observedIno, staleAfterSeconds)` (exported from cli.js, driven via `node -e`) returns false for a same-inode file whose mtime is now fresh — the npm-path mirror of the double-hold trigger · covers: M2, R:weakened_mutual_exclusion
  - test_js_genuinely_stale_same_inode_is_reclaimable: the JS helper returns true for a same-inode file still aged past staleAfter, and false for a vanished path — the npm-path self-heal floor · covers: M4
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. The NEW red test is the deterministic `_still_stale_generation` unit test (the concurrency integration test can't be made to reproduce inode-reuse on APFS — 0/80 under load — so the invariant is proven at the helper level, deterministically, and the integration test remains the on-CI regression guard). Minor/secondary behaviors are DESCRIBED in prose as build-guidance.

Kind: code — executable unit tests. test_reused_inode_live_file_not_reclaimable is RED before the helper exists (import fails / helper absent), GREEN after. The existing concurrency + self-heal tests are the regression floor.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — added module-level `_still_stale_generation(path, observed_ino, stale_after, now=None)` and wired it at ALL FOUR reclaim-unlink sites (the main-lock + ticket unlink in both `_update_lock` and `_project_lock`), replacing the bare `current_ino == st.st_ino` inode-identity guard. Each ticket site passes its own stale constant (`_LOCK_TICKET_STALE_SECONDS` / `_PROJECT_LOCK_TICKET_STALE_SECONDS`); each main-lock site passes the live `stale_after`. Build hiccup harvested to §7: inserting the helper just above `def _lock_heartbeat` initially stranded that function's `@contextlib.contextmanager` decorator onto the helper — caught by the guard failing 3/4 with a `_GeneratorContextManager` assertion; fixed by giving the helper no decorator and re-attaching `@contextlib.contextmanager` to `_lock_heartbeat`.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite) — guard `test_lock_reclaim_hardening.py` **6/6** (4 Python + 2 JS twin); `test_global_update_harden` 36/36; `test_js_reclaim_lock_heartbeat` 6/6; project-lock siblings 31/31; the two concurrency tests 5/5 deterministic; full `tooling/` discover **2316 tests OK, 0 fail/error** (241s)
- [x] coverage did not decrease — net +2 helpers (one per twin) + a new 6-test module; no test removed or weakened
- [x] no test or contract was altered during build — the frozen §3 Contract is untouched; the §5 Scope widening + the 2 added §4 JS cases were human-approved via `add.py re-cross --by "Tin Dang"` (the sanctioned post-freeze path), not a silent edit
- [x] the green was EARNED, not gamed — the deterministic helper unit tests prove the reused-inode-live invariant the APFS integration test cannot reproduce (0/80 under load); both twins driven independently (Python import, JS `node -e` against the real export); each was RED first for the right reason (missing helper / `stillStaleGeneration is not a function`)
- [x] concurrency / timing of the risky operation is safe — O_EXCL (`wx` in JS) remains the sole mutual-exclusion primitive; the staleness re-check only NARROWS the pre-existing stat→unlink TOCTOU (a live/heartbeated file, age < stale_after, is now spared); a genuinely crashed lock still ages out and self-heals in BOTH twins
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `time`/`os` and node `fs` only; no new imports or packages
- [x] layering & dependencies follow CONVENTIONS.md — a module-level helper beside the lock code it serves in each twin, mirrored 1:1 and cross-referenced in both docstrings; `stillStaleGeneration` added to cli.js's existing `module.exports`
- [x] a person reviewed and approved the change — Tin Dang: approved the gate on the Python fix, then (on my disclosure of the JS twin gap) approved widening scope to fix `bin/cli.js` in the same task rather than shipping a half-fix

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) does the re-check add a new race? — no, it narrows the pre-existing TOCTOU; (2) can it now MISS a real crashed lock? — no, only a live heartbeat refreshes mtime, so a truly crashed lock still ages out (self-heal floor 36/36 green); (3) reused-inode live file mistaken for stale? — no, a fresh lock is created at mtime=now and the code never back-dates mtime, so a live reused-inode holder always has age ~0 → spared; (4) right stale constant at each of the 4 sites? — verified in the diff (ticket sites use their ticket constants, main sites use the live `stale_after` / `staleAfterMs / 1000`); (5) **is the fix COMPLETE across shipped surfaces?** — this is the probe that caught the real gap: the JS/npm twin `bin/cli.js` carried the IDENTICAL guard at four sites, so the Python-only fix would have shipped a half-fix on the install path users actually run. Scope widened (human-approved re-cross) and both twins fixed. A first `replace_all` edit on the JS ticket sites introduced an undefined `ticketStaleSeconds` placeholder at both — caught immediately and repaired per-site with each lock's own constant, then `node --check` + the guard confirmed it.

### GATE RECORD
Reported: yes — the gate report (banner/ARC) rendered before this outcome recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose (a) fix a residual TOCTOU/double-hold in the reclaim path; rejected (b) prove the failure is a CI-filesystem O_EXCL-atomicity artifact (overlayfs/tmpfs not honoring O_EXCL atomically) and make the test assert only what the FS guarantees — WITHOUT weakening the `peak<=1` contract (e.g. detect non-atomic-O_EXCL filesystems and xfail there, keeping the guarantee on real filesystems) · (c) do nothing / keep RISK-ACCEPTED (rejected — it now BLOCKS the publish gate, not just a PR).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — added module-level `_still_stale_generation(path, observed_ino, stale_after, now=None)` and wired it at ALL FOUR reclaim-unlink sites (the main-lock + ticket unlink in both `_update_lock` and `_project_lock`), replacing the bare `current_ino == st.st_ino` inode-identity guard. Each ticket site passes its own stale constant (`_LOCK_TICKET_STALE_SECONDS` / `_PROJECT_LOCK_TICKET_STALE_SECONDS`); each main-lock site passes the live `stale_after`. Build hiccup harvested to §7: inserting the helper just above `def _lock_heartbeat` initially stranded that function's `@contextlib.contextmanager` decorator onto the helper — caught by the guard failing 3/4 with a `_GeneratorContextManager` assertion; fixed by giving the helper no decorator and re-attaching `@contextlib.contextmanager` to `_lock_heartbeat`.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] The Python `_installer.py` and JS `bin/cli.js` lock implementations are hand-mirrored twins with NO parity test — a fix to one can silently ship half-done. Consider a parity guard that asserts the reclaim-guard shape exists in both (evidence: this task's frozen scope covered only the Python twin; the identical 4-site inode bug in cli.js was found by an ad-hoc grep at verify, not by any test — `grep -n "currentIno\|currentTino" bin/cli.js` returned 1438·1467·1601·1629)
- [SPEC · open] The two concurrency tests are timing-sensitive enough that publish.yml's heavier load surfaced a real bug ci.yml never did — worth asking whether the publish gate's load profile should also run in normal CI (evidence: publish.yml FAILED 2/2 on `test_concurrent_stale_reclaim_exactly_one_wins` while #178's ci.yml passed both py 3.10 and 3.12)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] When a bug is FS-behaviour-dependent, the integration test may be structurally unable to reproduce it on the dev platform — prove the invariant at a deterministic HELPER level instead of weakening or blanket-skipping the integration guard, and keep the integration test as the on-CI regression net (evidence: inode reuse never reproduces on macOS APFS — 0/80 under oversubscription — but `_still_stale_generation` unit tests are deterministic and went RED→GREEN on both twins)
- [ADD · open] A "close the gap before the gate" check should explicitly ask *is the fix complete across every SHIPPED surface?* — a frozen scope naturally fences the twin you started from, and the gate is the last honest moment to widen it (evidence: refute-probe 5 caught `bin/cli.js`; the human chose re-cross over shipping a half-fix, +2 tests and one build cycle)
- [ADD · open] `re-cross --by <human>` is the sanctioned path for a post-freeze scope/test widening — it re-snapshots scope + tripwire so the gate does not later read the widening as `scope_violation` or `contract_tampered` (evidence: added `add-method/bin/cli.js` to §5 Scope + 2 §4 cases, re-crossed, gate PASS clean)
- [TDD · open] A `replace_all` edit across sites that LOOK identical but bind different constants silently introduces an undefined name at every site but the one you reasoned about — patch such sites individually, or verify each afterwards (evidence: `ticketStaleSeconds` landed undefined at both JS ticket sites; caught by re-grep before running, then fixed per-site with `LOCK_TICKET_STALE_SECONDS` / `PROJECT_LOCK_TICKET_STALE_SECONDS`)
