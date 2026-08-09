════════════════════════════════════════════════════════════════════════
 v14 · Production-ready ADD
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     6/6 done           CRITERIA  6/6 met
 GATES     6 PASS             WAIVERS   none

 goal  gates enforced by CI distinct from the agent; AI agents beyond
       Claude follow ADD; 1.1.0 published

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 gate-audit                  done      PASS 14†   ●●●●●●●●
 audit-ci                    done      PASS 6†    ●●●●●●●●
 high-risk-signal            done      PASS 12†   ●●●●●●●●
 agent-portability           done      PASS 7†    ●●●●●●●●
 review-checklist            done      PASS 6†    ●●●●●●●●
 release-1-1-0               done      PASS 7†    ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 6/6 met

 LEARNINGS (14 carried)
   • ADD · folded · a new enforcement surface applied to a legacy board
     surfaces convention-epoch debt as true positives — adjudicate at
     the human gate (here: retro-ratify as an honest present-day act),
     never auto-grandfather and never fabricate past records (evidence:
     43 unstamped_freeze findings on first live run, human-resolved same
     day)
   • ADD · folded · bulk adjudication must surface the CONTRADICTING
     SUBSET, not just the count — a blanket stamp over 43 records
     silently wrote "approved by Tin" onto 6 tasks whose own record said
     "NOT human-approved"; the audit (shape-only) reported clean over
     the contradiction. Fix ritual: grep the target set for text that
     negates the act being stamped, show that subset to the human, get
     an informed yes BEFORE writing (evidence: advisor-caught
     post-commit; human re-adjudicated the 6 as informed ratification,
     lines reworded to one coherent claim, 2026-06-05)
   • TDD · folded · a fixture arranging through the REAL engine inherits
     the engine's own input contracts — the RISK-ACCEPTED arrange step
     crashed until it passed the waiver flags the engine enforces;
     arrange-through-CLI is stronger than file-writing but costs
     fidelity to its argument grammar (evidence:
     test_risk_accepted_security errored pre-assert)
   • TDD · folded · a test that executes a string extracted from a repo
     artifact must refuse-on-drift — assert the extracted value equals
     the pinned constant BEFORE executing, so drift turns the suite red
     without ever running unpinned input (evidence: drifted ci.yml run
     line refused; proven non-vacuously, then reverted)
   • ADD · folded · an in-build test amendment that strictly STRENGTHENS
     is legal but never silent — disclose it at the gate beside the
     security note that motivated it, and let the human adjudicate both
     in one escalation (evidence: this gate, confirmed by Tin
     2026-06-05)
   • SDD · folded · when a guide documents a machine-read token, the
     reader must ignore documentation forms of it — strip comments
     before token matching, or every scaffold self-triggers (evidence:
     the template's `risk: high` comment would have declared every new
     task high-risk; caught in build, pinned by the ordinary-task
     regression test)
   • ADD · folded · a method-defining task should dogfood the rule it
     ships in its own header — the gate that records it becomes the
     rule's first live proof (evidence: high-risk-signal's own `gate
     PASS` ran the new guard and completed only because its dial was
     lowered)
   • TDD · folded · when a feature's exit criterion is a USER JOURNEY,
     write the protocol-walk test that executes the journey literally
     (parse the entry artifact for its instructions, run them, assert
     the destination) — it pins the criterion itself, not a proxy
     (evidence: test_protocol_walk_from_agents_md)
   • SDD · folded · prose artifacts accrete PROPERTY guards across
     milestones (v8: ≤22 lines, no manual framing; v14: any-agent
     routing) — before rewriting one, grep its guards and design to the
     UNION, or the rewrite red-flags late (evidence: block rewrite
     tripped two v8 pins mid-build, satisfied by reshaping output)
   • UDD · folded · a review prompt belongs AT the seam where the
     decision already happens, sized to the reviewer's real attention
     (one minute, six lines, ⚠-first) — a separate review artifact is
     ceremony that competes with the decision instead of aiming it
     (evidence: checklist landed inside 3-contract.md with a ≤16-line
     pin; zero new gates)
   • ADD · folded · a hard-to-reverse release act under the conservative
     dial absorbs REPEATED change requests cleanly — five contract
     versions, each human-worded, no test weakened, zero partial state
     (evidence: v1–v5 trail in §1/§3, runs
     27007111170/27008622520/27009193988/27009563639)
   • SDD · folded · a CI job that runs another ecosystem's tests must
     provision THAT ecosystem's declared floor itself — pyproject's
     `setuptools>=77` was honored by build isolation everywhere except
     the in-process npm-job path (evidence: attempt-1 traceback in apt
     setuptools)
   • TDD · folded · the prepublishOnly seam
     (tests-as-publish-precondition) caught a real env gap no local run
     could see — keep tests in the publish path even when they
     "duplicate" the guard job (evidence: attempt 1 failed closed before
     npm accepted anything)
   • ADD · folded · when an external service's silent auth fallback
     hides the broken layer (OIDC mint never engaging -> 404/ENEEDAUTH),
     pivoting the MECHANISM on the human's word beats deeper debugging
     of an opaque seam (evidence: v5 token pivot went green on the first
     try after two OIDC-shaped failures)

 DECIDE NEXT  fold learnings + archive-milestone v14
════════════════════════════════════════════════════════════════════════