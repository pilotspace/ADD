════════════════════════════════════════════════════════════════════════
 strategy-intake · personas as ADD's adaptive project-management brain
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     8/8 done           CRITERIA  8/8 met
 GATES     8 PASS             WAIVERS   none

 goal  A fitting persona becomes the project-management AND
       user-experience brain — it shapes each milestone's strategy, owns
       how every human gate is communicated and paced (replacing the
       fixed report-template ceremony), and designs that gate as a UDD
       user-experience artifact (UDD redefined from UI-design into
       experience-driven development: UI + interaction/gate UX,
       first-class). Personas adapt per project; one floor stays hard —
       security is always HARD-STOP.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 gate-experience-udd         done      PASS 0     ●●●●
 persona-owns-gates          done      PASS 0     ●●●●
 udd-experience-pillar       done      PASS 0     ●●●●
 strategy-section            done      PASS 5†    ●●●●
 persona-at-intake           done      PASS 0     ●●●●
 strategy-guide              done      PASS 0     ●●●●
 advisor-strategy-trigger    done      PASS 0     ●●●●
 risk-proportional-skip      done      PASS 0     ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   gate-experience-udd      PASS Tin Dang <tindang.ht97@gmail.com>
   persona-owns-gates       PASS Tin Dang <tindang.ht97@gmail.com>
   udd-experience-pillar    PASS Tin Dang <tindang.ht97@gmail.com>
   strategy-section         PASS Tin Dang <tindang.ht97@gmail.com>
   persona-at-intake        PASS Tin Dang <tindang.ht97@gmail.com>
   strategy-guide           PASS Tin Dang <tindang.ht97@gmail.com>
   advisor-strategy-trigger PASS Tin Dang <tindang.ht97@gmail.com>
   risk-proportional-skip   PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 8/8 met

 LEARNINGS (15 carried)
   • ADD · open · the reference skill-pool slack is razor-thin — a
     method-doc ADDITION must offset via same-guide compression, never a
     pool rebaseline (evidence: reference pool +1484 B on the first
     draft → −113 B after compressing the now-optional prescriptive
     prose the persona-ownership reframing made redundant)
   • UDD · open · gate communication IS user experience and belongs
     under the UDD pillar, not a standalone chat-report spec —
     persona-owns-gates made the gate persona-owned; its natural home is
     UDD (evidence: the user's redefine-UDD directive followed directly
     from this task)
   • UDD · open · UDD generalizes cleanly from UI-design to
     experience-driven development by ADDING an axis (INTERACTION) +
     broadening the framing, without touching the 5-beat loop or capture
     machinery — the axes are the extensible seam (evidence: design.md
     reframed experience-driven with 5 axes; test_design_intake_beat
     15/15 still green, loop machinery untouched)
   • TDD · open · a naive first-match string locator in a test
     (`find("interaction")`) can be fooled by NEW prose that reuses the
     term; fixed at the source (framing → "interactive flow") so the
     locator lands on the axis, NOT by weakening the test (evidence:
     FifthAxisTest.test_interaction_axis_covers_cadence_and_seeking went
     green after the design.md wording tweak, no test edit)
   • ADD · open · a doc addition in a razor-thin lean pool is fundable
     by same-guide compression even at the SKILL.md ceiling (9490<9500):
     the +11 B trigger broadening offset by a "the default mode" trim —
     compress-not-rebaseline held (evidence: orchestration pool 774 B
     headroom; core pool +1 B net; ENGINE_MD5 unchanged)
   • ADD · open · a persona at intake is worth shipping ONLY as
     advisory-with-a-generic-fallback — the risk-proportional design
     keeps it zero-cost when no persona fits, which is the same shape
     design.md uses; a blocking persona-load would have contradicted the
     milestone's own "personas REMOVE ceremony" thesis (evidence:
     proceed-generically path kept; nudge path stayed green)
   • TDD · open · scope a "must contain X" content check to the RELEVANT
     SECTION, not the whole file — M3 checking the whole intake.md for
     "security" would have passed vacuously on the pre-existing
     inline-lane HARD-STOP prose; heading-to-next-heading slicing made
     it actually test the persona step (evidence: intake.md already
     contained "security" before this task)
   • ADD · open · a cwd-relative path in a throwaway mutation probe is a
     foot-gun — mine clobbered a twin AND its backup by resolving
     against the wrong dir; the recovery was clean only because canon
     was untouched and byte-identical twins are trivially restorable by
     cp (evidence: M4 briefly red mid-verify, restored from canon,
     md5-equal). Prefer absolute paths in scratch probes.
   • ADD · open · running one test as a bare module (`unittest
     tooling.test_x`) can raise a false ModuleNotFoundError('add') that
     `unittest discover -s tooling` does not — always confirm a
     "regression" under CI's actual invocation before believing it
     (evidence: nudge test errored bare, passed 15/15 via discover)
   • ADD · open · a new skill guide's prose is scanned by the
     shipped-surface wording-lint
     (test_autonomy_command.WordingFenceTest) — draft against
     WORDING_RUBRIC.md's enforced swaps up front ("human seam"→"human
     decision point"), else the full suite catches it at the regression
     floor, not the targeted guard (evidence: 2299-test suite's ONLY
     failure was the lint, invisible to test_strategy_guide) (evidence:
     full run 221s, failures=1).
   • SDD · open · the honest resolution of a "load-bearing vs redundant"
     [spec] flag is EVIDENCE, not assertion: reading the actual `##
     Strategy` slot prose showed it already carried the four facets +
     SOFT + skip, so the guide's real value narrowed to the procedure
     alone — which kept it TIGHT (point, don't restate) (evidence: PLAN
     §3 [spec] RESOLVED note).
   • ADD · open · a content-guard assert that passes against
     PRE-EXISTING prose isn't red-first — M3 ("refute cannot block")
     first matched strategy.md's own SOFT "never blocked on a confidence
     bar"; scoping the assert to the refute context (from the
     `add-advisor`/`refute` marker onward) made it genuinely red before
     / green after (evidence: guard went 2-red → 3-red after the
     tighten).
   • TDD · open · when a NEW feature restates a caveat the surface
     already carries (advisory/SOFT/HARD-STOP), the guard must anchor
     the caveat to the NEW construct's context, not the whole file —
     else the regression guard and the feature guard collide into a
     vacuous green (evidence: same M3 tighten).
   • ADD · open · when an exit criterion is LITERALLY already met by
     shipped prose (the micro-skip was at strategy.md:8), the honest
     task is LEGIBILITY not mechanism — scope it as "make the scattered
     rule explicit," disclose the redundancy in §1/§3, and prove the
     delta with a guard that only a UNIFIED artifact satisfies
     (evidence: guard targets a dedicated depth section the scattered
     lines fail).
   • SDD · open · a red-first guard for "unify scattered prose" must
     anchor to a NEW container (a dedicated heading), not the keywords —
     else it passes on the scattered instances and never goes red
     (evidence: _depth_section() matches a heading, not the Skip/Trigger
     lines).

 SPEC DELTAS    58 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone strategy-intake
════════════════════════════════════════════════════════════════════════