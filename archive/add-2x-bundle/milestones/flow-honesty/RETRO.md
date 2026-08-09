════════════════════════════════════════════════════════════════════════
 flow-honesty · flow-honesty — make ADD's stated guarantees engine-true or honestly labeled
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     7/7 done           CRITERIA  7/7 met
 GATES     7 PASS             WAIVERS   none

 goal  close the gap between ADD's stated guarantees and what the engine
       mechanically enforces, making each gate either engine-true or
       honestly disclosed
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 freeze-gate-universal       done      PASS 15†   ●●●●●●●●●
 delta-drain                 done      PASS 0     ●●●●●●●●●
 security-escalation-disclo… done      PASS 5†    ●●●●●●●●●
 guarantee-audit-lints       done      PASS 9†    ●●●●●●●●●
 honest-reject-naming        done      PASS 23†   ●●●●●●●●●
 self-grading-refute-record  done      PASS 13†   ●●●●●●●●●
 stale-guide-sync            done      PASS 10†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   freeze-gate-universal    PASS Tin Dang <tindang.ht97@gmail.com>
   delta-drain              PASS Tin Dang <tindang.ht97@gmail.com>
   security-escalation-dis… PASS Tin Dang <tindang.ht97@gmail.com>
   guarantee-audit-lints    PASS Tin Dang <tindang.ht97@gmail.com>
   honest-reject-naming     PASS Tin Dang <tindang.ht97@gmail.com>
   self-grading-refute-rec… PASS Tin Dang <tindang.ht97@gmail.com>
   stale-guide-sync         PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 7/7 met

 LEARNINGS (15 carried)
   • ADD · folded · a universal-gate change carries a large test-fixture
     blast radius; pre-declaring the sweep in §5 ("collateral helpers
     re-declared once measured") + a DIRECTORY scope token turns
     reconciliation into a one-line `state.scope.declared` patch — no
     dirty-tree re-cross (evidence: 57 fixtures reconciled via one
     `add-method/tooling/` token; `snapshot_md5` guards the sidecar, not
     `declared`, so the patch is safe) [folded foundation-version 56]
   • TDD · folded · when a fixture drove a plain task to build on a
     DRAFT §3, the FAITHFUL fix is to freeze a real stub §3 in setup
     (not `--skip-freeze`) — every fixture stays a true frozen-contract
     task; an adversarial refute-read across all 25 edited files
     confirmed no assertion was weakened (evidence: refute-read VERDICT
     EARNED, 551 diff lines) [folded foundation-version 56]
   • ADD · folded · do ALL of a task's own §4-declared red-test edits in
     the TESTS phase, but the COLLATERAL blast-radius sweep necessarily
     happens at BUILD — safe because the tamper tripwire hashes ONLY the
     §4-declared set, never a glob (evidence: tripwire tracked 2 files,
     the 23 swept fixtures were untracked → no `build_tampered`) [folded
     foundation-version 56]
   • ADD · folded · a frozen contract drafted on a GROUND miss must be
     reconciled by a v1→v2 change-request + re-freeze, never a
     silently-deviating build — the §3 froze a `stale :` status prefix
     without knowing the shipped spec-delta-guards contract pins a `spec
     :` cue; the build kept `spec :` but left the contract saying `stale
     :` (evidence: refute-read #1 NOT-EARNED → human-approved v2
     amendment → refute-read #2 BLOCKER-CLOSED) [folded
     foundation-version 56]
   • TDD · folded · a status/format-cue test must pin the LINE (prefix +
     count + framing + pointer) via assertRegex, not `assertIn` a single
     keyword — a keyword-only assert under-specifies the contract and
     lets a non-conforming impl pass invisibly (evidence:
     `assertIn("stale")` passed a `spec :`-prefixed line the v1 contract
     said must be `stale :`) [folded foundation-version 56]
   • ADD · folded · `_collect_open_spec_deltas` scans every
     `.add/tasks/*` dir (live AND archived-but-lingering), so a count
     that reads as project-live can include shipped history — a release
     FLOOR should count only what its verbs can clear (gather-wide,
     gate-narrow) (evidence: 62 "open" deltas were 5 live + 57 archived;
     the floor is now live-filtered) [folded foundation-version 56]
   • ADD · folded · when the engine's enforcement has an EPISTEMIC blind
     spot (it cannot see what was never written down), DISCLOSE the
     limitation in the guide rather than fake a gate that manufactures
     false precision — measure-not-block honesty (evidence:
     `unescalated_security_note` catches mis-escalation but is
     structurally blind to a missed finding; a forced human-signoff
     checkbox would not change that) [folded foundation-version 56]
   • TDD · folded · a presence/format test must anchor on a
     DISCLOSURE-UNIQUE token, not a common word — bare "invisible" was
     vacuously satisfied by unrelated prose (line 40);
     "spot-audit"/"never marked" uniquely gate the disclosure (evidence:
     refute-read caught the vacuous branch; closed before the gate by
     re-anchoring) [folded foundation-version 56]
   • ADD · folded · a MEASURE-NOT-BLOCK lint (non-failing audit notice)
     is the honest tool when the engine can check PRESENCE but cannot
     JUDGE quality — surface the gap, never gate on it; reserve
     forceable gates for the structural holes (evidence:
     shallow_deep_check/risk_unset would have failed CI on 79 existing
     tasks if blocking — dishonest; as notices they inform without
     breaking) [folded foundation-version 56]
   • TDD · folded · a behavior change to a SHARED output surface (audit)
     ripples into sibling "clean board" fixtures — fix by making the
     fixture WELL-FORMED (declare risk) not by loosening the assertion;
     a presence/format test stays strong (evidence: 3 collateral
     fixtures gained `risk: normal`; refute-read confirmed no coverage
     lost) [folded foundation-version 56]
   • TDD · folded · when a later task legitimately relaxes an earlier
     invariant (engine now NAMES the deep-check block), update the guard
     to the NARROWER true invariant (no content tokens) rather than
     deleting it (evidence: test_verify_deepen `assertNotIn("Deep
     check")` → `assertNotIn("DEAD-CODE")` + WIRING, preserving
     judgment-free) [folded foundation-version 56]
   • ADD · open · a code rename ripples beyond emit sites into folded
     foundation lessons (`CONVENTIONS.md`) + the shipped template; a
     hygiene grep / refute-read scoped to "engine+guide+book" misses
     them — sweep ALL tracked files (exclude only
     CHANGELOG/archive/`.add/tasks`/`.add/milestones`/engine_pin-genealogy/worktrees)
     (evidence: comprehensive `git grep` caught
     `.add/CONVENTIONS.md:171` after the narrow refute-read passed
     EARNED).
   • ADD · open · `.add/` is `_SCOPE_EXCLUDE_DIRS`-pruned, so editing
     any `.add/`-tree file is invisible to the scope gate — a `.add/` §5
     token is documentary, not gated, and re-anchoring an excluded-dir
     fix needs NO tests→build re-cross (evidence: the verify-time
     CONVENTIONS.md fix tripped no `scope_violation`; corrects the §5
     "Known-problem" note that assumed a re-cross).
   • ADD · open · method/trust-layer edits (the BOOK + guides +
     reject-code strings) escalate the verify gate to a human even under
     `autonomy: auto` — a built-in auto-gate carve-out like security
     (PROJECT.md v6 residue category) (evidence: this gate escalated via
     AskUserQuestion; not auto-passed).
   • TDD · open · when an honest-reframe ADDS prose bytes and trips
     `test_skill_lean`, reclaim from the same guide's own gloss (book
     carries the full description; the guide stays terse) rather than
     rebaselining the budget (evidence: reference pool 45148→≤45114
     after a 2-line trim, ratios untouched).

 DECIDE NEXT  consolidate learnings + archive-milestone flow-honesty
════════════════════════════════════════════════════════════════════════