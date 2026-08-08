════════════════════════════════════════════════════════════════════════
 state-model-reshape · Multi-active state model + migration (team-collaboration foundation)
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     5/5 done           CRITERIA  5/5 met
 GATES     5 PASS             WAIVERS   none

 goal  ADD's engine tracks N truly-parallel active milestones —
       state.json holds a SET of active milestones, each with its own
       active task — with a backward-compatible migration from the
       single-active schema and the ENGINE_MD5 pin deliberately
       re-established.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 state-schema-migration      done      PASS 11†   ●●●●●●●●●
 active-accessors            done      PASS 10†   ●●●●●●●●●
 multi-active-commands       done      PASS 13†   ●●●●●●●●●
 parallel-status-view        done      PASS 9†    ●●●●●●●●●
 engine-repin-parity         done      PASS 7†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (8 carried)
   • ADD · open · an engine-editing milestone should run a verify-gate
     independent review by default — it caught a false self-audit WIRING
     claim (a third undocumented load seam) that a manual refute-read
     had passed over (evidence: python-expert review nit 2, this task)
   • ADD · open · a global find-and-replace that routes accessors will
     also rewrite the accessor's OWN body into self-recursion —
     introduce the helper, then route, then re-fix the two helper bodies
     (evidence: the _active_milestone/_active_task RecursionError caught
     at first test run, this task)
   • ADD · open · a frozen contract can hold an INTERNAL tension — here
     "replace the clear-pair with `_deactivate_milestone`" collided with
     the frozen "every N≤1 decision unchanged" invariant; the literal
     instruction REGRESSED the invariant. Resolution: honor the
     structural instruction (route through the SET writer) AND restore
     the invariant additively (a back-compat guard), rather than treat
     either clause as the whole truth (evidence: independent verify-gate
     review found the BLOCK that the green suite missed because no test
     exercised a non-primary archive with a live scalar)
   • TDD · open · a behavior-preserving refactor's regression hides
     where NO test arranges the precondition — the stale-scalar path
     needed a task created BEFORE the replace-to-focus `new-milestone`;
     add a coverage case for each pre-existing guard a routing change
     subsumes (evidence: test_archive_deactivates_from_set created zero
     tasks, so the dropped guard read green)
   • TDD · open · a "byte-identical at N≤1" claim needs a test that
     LOCKS the unchanged path (the N=1 rollup `*`, the N=1 json shape),
     not just one asserting the new path's ABSENCE — else the oracle
     can't catch a future regression in the boundary (evidence: review
     NIT — the absence-only tests left the rollup-mark change unproven
     until the hardening assertions were added)
   • ADD · open · a frozen presentation-only render still has a guarded
     SURFACE — `status --json` is ratified by an explicit
     sanctioned-keys test; adding keys is a census co-update (extend the
     sanctioned set, keep base immutable + the equality tight), not a
     silent append (evidence:
     test_wave_status_hint.test_json_surface_frozen went red on the 2
     new keys until ratified)
   • TDD · open · a byte-identity + pin guard proves the copies MATCH,
     not that they still DO anything — a parity backstop for a feature
     must also assert the feature's BEHAVIOR survives (born-migrated
     init · migration · the verbs · the render), else a refactor can
     keep 3 files identical+pinned while silently dropping the feature
     (evidence: this task's hardening guards exist precisely to close
     that blind spot)
   • ADD · open · a backstop/audit task is honest TDD when each guard is
     PROVEN to bite under the regression it names —
     green-on-correct-engine is fine IF the bite is demonstrated
     (transient real-file drift for the file guard; in-memory predicate
     for the rest), not assumed (evidence: independent review flagged
     the 2 in-memory "bites" tests as demonstrations-not-guards until
     the docstrings named the scope + the out-of-band real-drift proof
     was recorded)

 SPEC DELTAS    21 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              state-model-reshape
════════════════════════════════════════════════════════════════════════