════════════════════════════════════════════════════════════════════════
 installer-polish · installer-polish — round out the global-home and installer lane
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  complete the global lane: data restore, orphan prune, update
       --global concurrency + path-safety, and a reconcile roll-up. (The
       reusable PTY test helper was DEFERRED to a standalone task — todo
       #24 — so this milestone closes at 3/4; see Scope.)
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 global-data-restore         done      PASS 17†   ●●●●●●●●●
 global-update-harden        done      PASS 15†   ●●●●●●●●●
 reconcile-rollup            done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   global-data-restore      PASS Tin Dang <tindang.ht97@gmail.com>
   global-update-harden     PASS Tin Dang <tindang.ht97@gmail.com>
   reconcile-rollup         PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (7 carried)
   • TDD · open · a hermetic unit test that keys on an UNresolved tmp
     path misses a snapshot keyed on the RESOLVED path on macOS
     (`/var`→`/private/var`) — key on the resolved abspath in BOTH the
     helper and the impl, or the suite is green-on-Linux/red-on-macOS
     (evidence: 3 RestoreUnitTest red until `_restore_data` resolved
     internally).
   • ADD · open · a literal `<…>` token in a §6 Build-expectations
     bullet (e.g. a backticked `<name>.bak`) trips `_section_unfilled`'s
     placeholder regex → the build-expectations gate false-fires
     `build_expectations_unfilled` — write concrete names, never
     `<placeholder>`-shaped prose (evidence: first tests→build advance
     rejected on the `<name>.bak` bullet).
   • ADD · open · a frozen contract that pins a per-twin IMPLEMENTATION
     mechanism (flock for pip, O_EXCL for npm) can fail its own INTENT
     ("pip + npm serializes concurrent runs") — freeze the OBSERVABLE
     behavior (cross-twin serialize), not the mechanism; the
     verify-phase refute-read is what caught it → re-freeze v2
     (evidence: v1 NOT-EARNED, the two twins didn't interoperate).
   • TDD · open · a structural parity test asserting only token PRESENCE
     (string-in-source) passes even when the symbol is never CALLED —
     assert call-sites + a behavioral smoke (evidence: refute-read
     Finding 3; strengthened test_parity_surface to check `with
     _update_lock(home):` / `acquireUpdateLock(home)`).
   • TDD · open · a concurrency mechanism needs a CROSS-implementation
     test (a pip-held lock must block npm and vice-versa), not just
     same-twin contention — the v1 same-twin tests were green while
     cross-twin was broken (evidence:
     test_cross_twin_lockfile_blocks_both added at v2).
   • ADD · open · freeze OBSERVABLE behavior, not an over-broad INV — a
     verify refute-read caught the v1 contract claiming "identical
     counts + wording" when two divergences pre-dated the task; the
     honest fix was re-freeze @ v2 to the provable scope + file the rest
     as deltas, NOT change code or weaken a test (evidence:
     reconcile-rollup re-frozen v1→v2, code byte-identical across the
     re-freeze)
   • TDD · open · a parity test that asserts "output CONTAINS a count"
     is vacuous for proving cross-twin equality — the `restored ==
     files-deleted` invariant asserted on EACH twin proves identical
     computation without coupling to differing bundle contents
     (evidence: the v1 `test_npm_update_prints_rollup` regex-passed
     despite the twins being able to diverge; replaced by
     `test_*_restored_equals_files_deleted`)

 SPEC DELTAS    10 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              installer-polish
              1 planned not yet scaffolded: pty-test-helper
════════════════════════════════════════════════════════════════════════