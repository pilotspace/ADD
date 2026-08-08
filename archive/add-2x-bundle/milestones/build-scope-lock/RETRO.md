════════════════════════════════════════════════════════════════════════
 build-scope-lock · Build Scope Lock
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  a build's scope of impact is declared before it starts and
       engine-enforced when it ends — touched is a subset of declared,
       so a passing build cannot quietly modify files outside its frozen
       scope

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 scope-decl-template         done      PASS 6†    ●●●●●●●●●
 scope-gate-enforce          done      PASS 16†   ●●●●●●●●●
 scope-violation-heal        done      PASS 10†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (11 carried)
   • SDD · open · §0 GROUND for a prose-surface task must sweep the
     WORDING guards (WORDING_RUBRIC.md +
     ubiquitous-language/wording-lint/rewrite suites), not just the
     structural ones — the frozen §3 named a banned idiom and a
     comment-budget breach the ground map never surfaced (evidence: 5
     guard failures at the first full discover; v2 change-request
     approved 2026-06-12)
   • ADD · open · a human-approved mid-build change-request still trips
     the tamper tripwire; the honest re-arm is phase tests→advance after
     the bundle edits — worth one line in run.md so agents don't read
     build_tampered as a cheat signal (evidence: add.py check
     build_tampered after the v2 re-freeze, cleared by re-advance)
   • TDD · open · when a frozen §4 plan says "both lines above X", write
     BOTH ordering asserts — the refute-read caught Strategy's position
     unasserted while the plan claimed it (evidence: refute subagent
     coverage-gap finding; assert added before the gate)
   • ADD · open · sibling-session commits landing on the shared branch
     mid-task can redden unrelated guards; the full-suite-before-gate
     rule caught and routed it instead of letting the gate record over
     it (evidence: helios commits 37ce66a..7f778be → 3 guard reds; fix
     commit 30153a1)
   • TDD · open · a co-witness pair must be born ATOMICALLY in the same
     crossing or single-file erasure splits them — the tripwire got this
     right by accident of history (flag_verified born with it); new
     snapshot seams must design the witness in (evidence: refute pass 1
     reproduced the anchor-erase bypass scope_anchor_missing now blocks)
   • ADD · open · every state-creating seam needs its state-REMOVING
     transition specified in the same contract — declared->undeclared
     had no cleanup path until a refute pass disclosed it (evidence: v3
     change-request; test_undeclared_recross_cleans_up)
   • SDD · open · "same trust boundary as X" is a testable parity CLAIM,
     not a rhetorical flag — the refuter falsified it empirically and
     the contract had to be re-frozen (evidence: v1 flag #2 vs the
     one-key erase repro)
   • TDD · open · declare green pins by NAME in §4 (not "one pin") —
     this task declared 4 and the refute pass audited each against its
     claim (evidence: §4 coverage line; refute pass green-pin honesty
     check)
   • ADD · open · a finding is loop-healable ONLY if fixable from BUILD;
     erased evidence (missing sidecar, erased anchor) must stay
     die-in-place — the recoverable/erased split is the reusable routing
     rule any future guard inherits by calling the shared router
     (evidence: _scope_guard `missing`-split vs heal,
     test_sidecar_missing_still_dies + test_anchor_missing_still_dies
     green-pinned against test_sidecar_diverged_heals_then_restores)
   • TDD · open · a behavior-FLIP task (same trigger, exit 1 → exit 3)
     is best pinned by a GREEN-pin partition — the unchanged invariants
     (die-in-place ×2, monitor, mirrors) pin green-before-AND-after
     while only the flipped branches red, so the red/green split itself
     encodes the contract (evidence: test_scope_violation_heal recorded
     red run 2026-06-12 — 4 green pins + 5 routing reds + 1 repin-flip)
   • ADD · open · proving a SHARED cap needs a cross-source escalation
     test, never a same-source one — seeding the counter from "tamper"
     then triggering a "scope" arrival is the only assertion that
     distinguishes a shared cap from a parallel one (evidence:
     test_cap_is_shared_across_sources escalates heal_exhausted with
     history[-1].source=="scope")

 DECIDE NEXT  consolidate learnings + archive-milestone
              build-scope-lock
════════════════════════════════════════════════════════════════════════