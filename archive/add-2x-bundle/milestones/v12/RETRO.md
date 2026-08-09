════════════════════════════════════════════════════════════════════════
 v12 · Autonomous Onboarding — zero-touch setup → human lock-down
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     6/6 done           CRITERIA  8/8 met
 GATES     6 PASS             WAIVERS   none

 goal  Point ADD at any repo and it autonomously drafts the foundation,
       first-milestone scope, and a candidate first contract — silent
       for an existing codebase, interview-then-autonomous for a new one
       — all frozen at a single human lock-down.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 setup-lock-state            done      PASS 0     ●●●●●●●●
 brownfield-scan             done      PASS 0     ●●●●●●●●
 setup-review-artifact       done      PASS 0     ●●●●●●●●
 autonomous-setup-guide      done      PASS 0     ●●●●●●●●
 book-align                  done      PASS 0     ●●●●●●●●
 installer-arm               done      PASS 0     ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 8/8 met

 LEARNINGS (1 carried)
   • ADD · open · `add.py status` doesn't surface the unlocked-setup →
     lock step (evidence: check 3, post-init status prints "run /add",
     not "review SETUP-REVIEW.md then lock"); follow-up: a small
     `cmd_status` hint when `setup.locked is False`. Behind task 1's
     frozen engine — schedule as a v12 fast-follow or next-milestone
     task.
════════════════════════════════════════════════════════════════════════