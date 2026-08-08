════════════════════════════════════════════════════════════════════════
 v18 · Prompt structure & file hygiene
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  0/0 met
 GATES     2 PASS             WAIVERS   none

 goal  ADD artifacts and guides are XML-structured for AI effectiveness,
       and done work compacts out of the active tree

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 xml-prompt-structure        done      PASS 18†   ●●●●●●●●
 archive-compaction          done      PASS 11†   ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ○○○○○○○○○○ 0/0 met

 LEARNINGS (8 carried)
   • SDD · folded · contracts that name mirror trees must enumerate ALL
     copies — the v18 MIRRORS clause missed the _bundled third tree
     (evidence: §6 residue 2, discovered in build)
   • TDD · folded · never pin a speculative number before counting the
     baseline — pin the contracted semantics ("shrank") or count first
     (evidence: §6 residue 1, the ≤8 lean threshold)
   • ADD · folded · form tags (v18) make fill regions machine-delimited
     — a future engine feature can parse <must>/<reject> for rule-level
     reporting without touching templates again (evidence: frozen §3
     amendment)
   • DDD · folded · "instruction tags" vs "form tags" entered the
     ubiquitous language — GLOSSARY should carry both terms at the next
     fold (evidence: §3 CLASS RULE)
   • SDD · folded · "sole sanctioned test edit" clauses under-enumerate
     the same way mirror clauses did: SELF-MAINTAINING instruments
     (min_pillar's LIFECYCLE census, the ubiquitous-language prose ban)
     react to ANY new CLI verb — a contract adding a subcommand should
     pre-declare the instrument-reaction class (evidence: 2 disclosed
     residues at this gate)
   • TDD · folded · run the FULL suite once during the tests phase, not
     only the new file — both instrument reactions were discoverable
     pre-freeze and would have entered the contract instead of the
     residue list (evidence: test_min_pillar + test_ubiquitous_language
     failed only at the first full-suite build run)
   • ADD · folded · archive is now a two-step lifecycle
     (archive-milestone -> compact) — the milestone-close fold-pressure
     nudge and fold.md could name compact as the step after
     consolidation (evidence: cmd_compact landed; status nudge still
     ends at the fold)
   • DDD · folded · "compact" / "heavy archive" / "recovery bundle"
     entered the language — GLOSSARY should carry them at the next
     retrospective consolidation (evidence: new CLI verb + the
     .add/archive/ namespace)

 DECIDE NEXT  consolidate learnings + archive-milestone v18
════════════════════════════════════════════════════════════════════════