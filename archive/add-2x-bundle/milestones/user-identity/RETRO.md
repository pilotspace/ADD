════════════════════════════════════════════════════════════════════════
 user-identity · User Identity
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  ADD resolves a git-native actor (whoami: git config
       user.name/email, OS-user fallback) and stamps WHO performed each
       human-owned action — contract freeze, verify gate,
       milestone-done, lock, release — as a structured actor field
       alongside today's free-text, giving a multi-user team an
       auditable who-decided-what trail. Descriptive only (no access
       enforcement); solo behavior unchanged; the byte-pinned engine
       edited in lockstep across all 3 copies.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 actor-identity              done      PASS 17†   ●●●●●●●●●
 actor-stamping              done      PASS 9†    ●●●●●●●●●
 identity-in-status          done      PASS 5†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   actor-stamping           PASS Tin Dang <tindang.ht97@gmail.com>
   identity-in-status       PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (3 carried)
   • ADD · open · the descriptive-additive stamp still rippled an
     exact-diff invariant test (test_retro `changed <=
     {status,updated}`) — an "additive" record write needs a census
     sweep for tests that pin a record's EXACT key-set, not just its
     values (evidence: test_close_state_diff_is_status_only went red
     until done_actor was ratified into the allowed set)
   • ADD · open · a write-then-render ordering coupling: when a render
     reads a state field, the field must be set BEFORE the render that
     persists it (RETRO.md), or the persisted artifact diverges from the
     canonical recompute (evidence: cmd_milestone_done wrote done_actor
     AFTER `_write_retro`, so the saved RETRO.md lacked the `closed by`
     line the report re-render adds — fixed by reordering the stamp
     before the retro write).
   • ADD · open · a present-only render helper must default-read every
     key (`actor.get('name','')`, not `actor['name']`) so a
     hand-edited/partial state record degrades to empty, not a KeyError
     crash (evidence: python-expert refute-read NIT; hardened
     `_fmt_actor`).

 SPEC DELTAS    23 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone user-identity
════════════════════════════════════════════════════════════════════════