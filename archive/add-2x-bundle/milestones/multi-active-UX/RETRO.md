════════════════════════════════════════════════════════════════════════
 multi-active-UX · Multi Active Ux
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  a team running several active milestones at once sees, in one
       place, what is theirs to work on and what is schedulable across
       all streams — ADD surfaces a per-actor 'my work' view, a
       per-stream owner, and a cross-active waves/ready frontier,
       instead of a single-milestone-at-a-time lens
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 my-work-lens                done      PASS 0     ●●●●●●●●●
 per-stream-owner            done      PASS 0     ●●●●●●●●●
 cross-active-waves          done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   my-work-lens             PASS Tin Dang <tindang.ht97@gmail.com>
   per-stream-owner         PASS Tin Dang <tindang.ht97@gmail.com>
   cross-active-waves       PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (6 carried)
   • TDD · open · when a setup command REPLACES rather than ADDS to a
     set (here `new-milestone` resets `active_milestones` to `[new]`),
     build the desired set EXPLICITLY at the end of arrange (a
     complete-value `_poke` or a final reconcile) instead of relying on
     per-create activation — interleaved create+activate silently drops
     earlier members (evidence: the first my-work-lens fixture left only
     the last milestone active → t1 vanished from the lens)
   • ADD · open · a multi-field identity match (owner/assignee vs
     resolved actor) needs an explicit BOTH-DIRECTIONS test — the
     positive (matches) AND the near-miss (same name, different email →
     no match) — or the discriminating half of the rule is unverified
     (evidence: refute-read confirmed
     test_mine_match_email_first_name_fallback exercises both branches;
     the role="both" + ordering branches were initially untested and
     added post-review)
   • TDD · open · a test named `*_byte_identical` must actually assert
     byte-identity (or absence of EVERY new fragment, incl. empty
     separators), not just absence of the one new keyword — else a
     different spurious fragment passes under a name that claims more
     than it checks (evidence: refute-read Finding 2 —
     `test_no_owner_stream_byte_identical` only checked `not in
     "owner:"`; renamed + strengthened to also reject the `· `
     separator)
   • ADD · open · a present-only render that reuses a formatter
     (`_fmt_actor`) must replicate that formatter's OWN emptiness guard
     at the call site — `_fmt_actor` returns a truthy ` <email>` for a
     blank-NAME record, so a naked `if _fmt_actor(x)` check emits a
     fragment the contract forbids; guard on `.get("name")` like
     `_fmt_ownership` does (evidence: refute-read Finding 1 — blank-name
     owner leaked an `owner: <email>` fragment until the name-guard was
     added)
   • ADD · open · when widening a single-target command to multi-target,
     EXTRACT the per-target render into a pure helper and keep the
     len==1 path calling it verbatim — `print("\n".join(lines))` is
     byte-identical to the old per-line `print()`s, so the single-target
     output (and every existing test) stays green while the multi-target
     path is purely additive (evidence: cross-active-waves extracted
     `_wave_block_lines`; the whole unchanged test_dag_scheduler suite
     stayed green)
   • TDD · open · a "spans multiple X" test must assert the
     SEPARATOR/fencing, not just that both X appear — both-present
     passes even if the blocks run together or the header sits in the
     wrong place (evidence: refute-read nit — added
     `assertIn("\n\nmilestone: m2")` to pin the blank-line fence between
     stream blocks)

 SPEC DELTAS    35 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone multi-active-UX
════════════════════════════════════════════════════════════════════════