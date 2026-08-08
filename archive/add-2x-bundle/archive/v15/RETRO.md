════════════════════════════════════════════════════════════════════════
 v15 · Zero-command on-ramp
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  After the single install command, a newcomer reaches their first
       verified feature purely by talking to the AI — no typed add.py
       commands

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 getting-started-rewrite     done      PASS 6†    ●●●●●●●●
 installer-handoff           done      PASS 9†    ●●●●●●●●
 skill-onramp                done      PASS 9†    ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (9 carried)
   • SDD · folded · designing to the grepped guard-UNION before writing
     landed a 16-guard doc rewrite green first pass — the union rule's
     first premeditated application (evidence: zero pre-existing guard
     reds at build)
   • UDD · folded · "zero-command" survived contact only as "one SHELL
     command" — /add is still typed; precise promises beat catchy
     absolutes (evidence: doc-truth verifier caught the intro
     contradicting §1)
   • ADD · folded · adversarial verify lenses catch cross-surface
     DIVERGENCE the suite structurally cannot — cli.js silently dropped
     a valueless flag while argparse errored; pair every multi-surface
     build with a parity hunter (evidence: the blocker finding, fixed
     via disclosed strengthening amendment)
   • TDD · folded · behavioral pins on the happy path found nothing new;
     the missing-value EDGE found a real bug — pin behavior at the edges
     first (evidence: test_missing_flag_value_fails red on npx, green on
     pip)
   • SDD · folded · re-verifying the routed gap shrank this task from
     "implement the handoff" to "pin it + fix the hint" — half the
     scoped work already existed (evidence: §1 GAP RE-VERIFIED block;
     v12 shipped the handoff)
   • ADD · folded · a cross-cutting reword must enumerate EVERY file
     carrying the pattern before freezing, not just the one named in the
     gap. The v1 contract scoped only 0-setup.md §4; the structural
     suite (incl. the green protocol walk) was satisfied while the SAME
     human-types-the-lock instruction sat in two unswept guides
     (setup-review.md, adopt.md). The adversarial cross-surface lens,
     not the test suite, caught it → CR v2 (evidence: 3× MAJOR from
     verify-skill-onramp).
   • SDD · folded · a behavioral journey test (protocol walk) and a
     prose-coherence test are different guarantees; the walk proved the
     MACHINERY works at v1 while the GUIDE still told the human to type
     — words-exist ≠ method-works cuts both ways (evidence:
     test_v8_onramp's own honest-scope note, now closed by this walk).
   • ADD · folded · moving WHO-EXECUTES a gated action (human→agent)
     leaves the DECISION with the human only if the trigger is defined
     tightly; "recorded confirmation" needed "an explicit yes to the
     lock-down itself" to keep an eager agent from reading ambient
     agreement as consent (evidence: seam-integrity lens, 2× MAJOR).
   • ADD · folded · the docs/book is a shipped surface too — sweep it in
     the same grep as the skill tree (it was dry here only because the
     advisor flagged the gap in coverage before the gate; the lens
     prompt had soft-pedaled .add/docs/ to NOTE).

 DECIDE NEXT  fold learnings + archive-milestone v15
════════════════════════════════════════════════════════════════════════