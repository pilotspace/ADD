════════════════════════════════════════════════════════════════════════
 v22 · Stage Graduation — the 4th scope altitude (mvp → production)
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  6/6 met
 GATES     4 PASS             WAIVERS   none

 goal  When the MVP is covered, ADD proposes the move to production as
       an analytics-driven, interview-led roadmap of milestones the
       human confirms before the stage ever advances.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 stage-goal-criteria         done      PASS 10†   ●●●●●●●●
 graduation-analytics        done      PASS 12†   ●●●●●●●●
 graduate-guide              done      PASS 9†    ●●●●●●●●
 stage-book-align            done      PASS 25†   ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 6/6 met

 LEARNINGS (14 carried)
   • SDD · open · **Contract-freeze must check whether the seam it
     extends was already frozen-closed by a prior contract.** Freezing
     §3 here (status --json +2 keys) silently collided with v4-1
     `machine-state-json`'s closed 5-key set; the collision surfaced
     only at the full-suite run in verify (`test_json_surface_frozen`
     red), not at freeze. Fix the contract guide: before freezing an
     additive extension to an existing `--json`/state surface, grep for
     the prior contract that froze it and state additive-vs-closed
     explicitly. (evidence: a HARD-STOP + human change-request
     mid-verify that a freeze-time cross-check would have pre-empted)
   • ADD · open · **Reinterpreting a frozen contract must sweep the
     loaded trust layer for stale prose, not just the test guard.**
     Re-aiming `test_json_surface_frozen` made the suite green, but a
     green suite cannot catch prose drift (tests don't exercise docs).
     The advisor-prompted sweep found the closed-shape statement lived
     only in the *archived* v4-1 TASK.md (not
     PROJECT/CONVENTIONS/GLOSSARY/docs) → safe — but the check was
     nearly skipped. Fix: add "sweep loaded-layer prose for the old
     shape" to the change-request checklist (close-gap-before-gate).
     (evidence: blind-spot caught at the gate, not by any test)
   • DDD · open · **The done-tally over `state["milestones"]` has an
     archive blind spot: every milestone archived → empty map →
     `bool(ms)` False → cue never fires.** Dogfood exercised the
     archived-*present* case; the all-archived case is unverified and is
     a real graduation path (a long-lived project archives finished
     milestones). `graduate-guide` (task 3) must decide the all-archived
     semantics — count archived milestones toward the done-tally, or
     document why not. (evidence: §1 assumption #2 flagged it
     lowest-confidence; no test covers it)
   • TDD · open · **A gather-not-judge invariant guarded by a denylist
     is only as strong as the list — pin the invariant STRUCTURALLY, not
     lexically.** `test_never_readiness_verdict`'s FORBIDDEN set omits
     "theme"/"ready" (dropped deliberately), so the test is narrower
     than the §3 contract's "no verdict / score / ranking / theme"
     claim. Lesson: when an invariant is "the engine never concludes",
     assert the *absence of a conclusion field in the schema*
     (impossible to add a verdict), not the *absence of specific words
     in the output* (a denylist always lags the contract's vocabulary).
     (evidence: advisor caught the gap; the code genuinely judges
     nothing — the JSON schema has no verdict field — so it is a
     test-completeness gap, not a defect)
   • ADD · open · **A multi-source report must declare ONE traversal
     basis per tier, or the sets silently diverge under archival.**
     `open_deltas` globs the filesystem (`_collect_open_deltas` over
     `tasks/*`) while `residue_disclosed` + `coverage_gaps` iterate
     `state["tasks"]`. They agree today ONLY because all 12 archived
     milestones are *compacted* (files moved out of `tasks/`); a future
     *light-archived* milestone (files stay, state entry dropped) would
     appear in `open_deltas` but vanish from the state-iterated sets.
     This is the same archive seam as stage-goal-criteria's DDD delta
     (done-tally over `state["milestones"]`). Lesson: pin each tier's
     source-of-truth (filesystem OR state) in the contract and prove the
     two bases agree, or document the divergence as a known limitation.
     (evidence: open_deltas globs tasks/* while residue_disclosed +
     coverage_gaps iterate state["tasks"]; the sets agree today only
     because all 12 archived milestones are compacted out of tasks/)
   • SDD · open · **When a harvest's coverage is bounded by current DATA
     SHAPE (not by design), the contract must record the boundary AND
     the empirical check that made it safe — so a future shape that
     violates it re-opens the clause.** The `archived_summarized` reject
     clause bounds the fine-grained sets (waivers, gate-verdicts, §6
     residue) to the live tier; it was frozen safe by a discriminating
     grep (0 archived waivers / non-PASS gates exist today), not by
     argument. Lesson: a data-shape-bounded contract clause should name
     its trigger (here: the first archived RISK-ACCEPTED/HARD-STOP) so
     the limitation surfaces as a change-request the day it stops being
     empty, instead of silently under-reporting. (evidence: pre-freeze
     advisor flagged the limitation as possibly silent; the grep made it
     empirically empty — 0 archived waivers / non-PASS gates)
   • ADD · open · **To verify a "X can NEVER reach state S" guarantee,
     enumerate every WRITER of S — not the string-callers of the
     command.** The first pass grepped `stage production` (string
     callers); the load-bearing proof was grepping every assignment to
     `state["stage"]` (the guarded field). Lesson: a transition guard's
     completeness is the full set of mutators of the target state —
     enumerate it, never infer it from the obvious entry point.
     (evidence: advisor's pre-gate check turned the central claim
     believed→verified — exactly two writers, cmd_init=declared_at_init
     boundary + cmd_stage=guard, no third, load_state does not
     normalize)
   • SDD · open · **A guarded transition must explicitly NAME its
     at-creation door, or the "NEVER" silently leaks.** `init --stage
     production` writes the guarded state directly, bypassing the
     transition guard — a "second door." Resolved by scoping the guard
     to transitions and naming `init` the `declared_at_init` boundary
     (same human authority as `--force`), not by silently leaving it nor
     over-extending the guard into init. Lesson: floor = `cmd_stage`
     guard · path = `graduate.md` · judgment = the human interview — and
     every door into the floored state is either guarded or
     named-as-boundary, never unlisted. (evidence: advisor caught the
     second door at the freeze; the §3 After-claim was tightened from
     "cannot reach" to "cannot TRANSITION to" production)
   • TDD · open · **A prose deliverable's content tests are lexical
     MARKER checks, not proof the behavior works — keep §6 honest about
     what they verify.** `test_graduate_md_documents_orchestration` /
     `test_skill_routes_to_graduate` assert the guide NAMES the right
     steps; they cannot prove the orchestration actually drives a human
     through cue→roadmap→flip. Lesson: prose tests pin vocabulary (a
     regression fence); the behavior is verified by the human and by
     whatever ENGINE seam the prose points at, never by the marker test
     alone — sibling of graduation-analytics' structural-vs-lexical
     delta. (evidence: advisor flagged the SEMANTIC over-claim risk; §6
     records the guide's real proof as the human read + the guard's
     runtime behavior + the live refusal dogfood)
   • TDD · open · **A new guard that invalidates an existing test's
     PREMISE is adapted by SPLITTING, not loosening — and disclosed at
     the gate as a precondition-change.** `test_stage_change` flipped
     straight to production with no roadmap; the guard broke that
     premise. Fix: keep the bare-flip mechanic on a non-guarded stage
     (`stage poc`) AND add the guard tests (refuse@0 / succeed@≥1 /
     --force) → net coverage +9. Lesson: never weaken an assertion to
     buy green — when a precondition genuinely changes, move the old
     guarantee to where it still holds, add the new guarantee, and
     surface the touch at verify so it is judged, not hidden. (evidence:
     §6 ⚠ discloses both touched test files — this + test_wording_lint's
     sanctioned surface-count bump — as non-weakenings; the human-led
     gate accepted them)
   • ADD · open · **Docs/book tasks have a ceremonial TDD red.** For a
     trust-layer edit the parity guard proves the three trees MATCH,
     never that the prose is RIGHT — the real guard is the human read at
     the gate. Codified in this task's §4 (no new content test). Lesson:
     do not manufacture a content test to fake a red; name the human
     read as the substantive guard and keep the parity red honest
     (evidence: §4 records "Coverage target: parity + human read"; the
     build red was 2 parity failures from canon-ahead-of-mirror, with
     zero content-presence red because there is no content test)
   • ADD · open · **A cross-surface term can carry two axes;
     disambiguate before unify.** "Scope level" means
     decision-granularity in the glossary and orchestration-loop in
     graduate.md; unifying or overwriting loses a sense. Lesson: when a
     shipped skill reuses a term the book already defines differently,
     keep both senses and add one bridging clause rather than merging
     the lists (evidence: glossary line 69 keeps {intake · milestone ·
     setup/foundation · task} + a bridge clause, while graduate.md:5
     uses {setup · intake · milestone-loop · stage-graduation}; both
     coexist post-task)
   • SDD · open · **A MILESTONE-declared task slug can collide with a
     prior done task.** v22 declared task 4 as `book-align`, already a
     done v12 task; `new-task` would have overwritten it. Lesson: needed
     a manual rename to `stage-book-align` + a MILESTONE.md reference
     reconciliation — a future engine guard could warn when a declared
     task slug matches an existing `tasks/` dir (evidence: `book-align`
     exists as a done v12 task dir; v22 MILESTONE.md lines 65/82 still
     read `book-align` while the delivering task is `stage-book-align`)
   • TDD · open · **The `.add/docs` dogfood mirror is only partially
     parity-guarded.** test_bundle_parity covers canon↔bundle (full) and
     test_v8_docs covers canon↔dogfood for the GLOSSARY only —
     `.add/docs/10` has no test, so that mirror can drift silently.
     Lesson: verified here by manual md5; a future guard could md5 the
     whole `.add/docs` tree when it is present (evidence:
     test_v8_docs:90 checks only GLOSSARY_DOGFOOD md5; no test
     references `.add/docs/10`; this task synced and md5-verified that
     mirror by hand)

 DECIDE NEXT  consolidate learnings + archive-milestone v22
════════════════════════════════════════════════════════════════════════