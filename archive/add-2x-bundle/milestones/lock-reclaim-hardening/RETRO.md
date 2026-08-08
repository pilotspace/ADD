════════════════════════════════════════════════════════════════════════
 lock-reclaim-hardening · Harden the global-update stale-reclaim lock so the publish gate is flake-free
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     1/1 done           CRITERIA  1/1 met
 GATES     1 PASS             WAIVERS   none

 goal  The concurrency suite (test_concurrent_stale_reclaim_*) passes
       deterministically under publish-job load — either the residual
       TOCTOU/double-hold in _update_lock's stale-reclaim path is fixed,
       or the test is proven to assert only what the CI filesystem can
       guarantee (without weakening the peak<=1 mutual-exclusion
       contract). Unblocks the v2.4.0 npm/PyPI publish.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 lock-reclaim-hardening      done      PASS 0     ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   lock-reclaim-hardening   PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 1/1 met

 LEARNINGS (4 carried)
   • TDD · open · When a bug is FS-behaviour-dependent, the integration
     test may be structurally unable to reproduce it on the dev platform
     — prove the invariant at a deterministic HELPER level instead of
     weakening or blanket-skipping the integration guard, and keep the
     integration test as the on-CI regression net (evidence: inode reuse
     never reproduces on macOS APFS — 0/80 under oversubscription — but
     `_still_stale_generation` unit tests are deterministic and went
     RED→GREEN on both twins)
   • ADD · open · A "close the gap before the gate" check should
     explicitly ask *is the fix complete across every SHIPPED surface?*
     — a frozen scope naturally fences the twin you started from, and
     the gate is the last honest moment to widen it (evidence:
     refute-probe 5 caught `bin/cli.js`; the human chose re-cross over
     shipping a half-fix, +2 tests and one build cycle)
   • ADD · open · `re-cross --by <human>` is the sanctioned path for a
     post-freeze scope/test widening — it re-snapshots scope + tripwire
     so the gate does not later read the widening as `scope_violation`
     or `contract_tampered` (evidence: added `add-method/bin/cli.js` to
     §5 Scope + 2 §4 cases, re-crossed, gate PASS clean)
   • TDD · open · A `replace_all` edit across sites that LOOK identical
     but bind different constants silently introduces an undefined name
     at every site but the one you reasoned about — patch such sites
     individually, or verify each afterwards (evidence:
     `ticketStaleSeconds` landed undefined at both JS ticket sites;
     caught by re-grep before running, then fixed per-site with
     `LOCK_TICKET_STALE_SECONDS` / `PROJECT_LOCK_TICKET_STALE_SECONDS`)

 SPEC DELTAS    60 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone
              lock-reclaim-hardening
════════════════════════════════════════════════════════════════════════