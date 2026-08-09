════════════════════════════════════════════════════════════════════════
 flag-first-freeze · Flag-first freeze + autonomy dial
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  3/3 met
 GATES     2 PASS             WAIVERS   none

 goal  close the freeze-and-autonomy seam: the lowest-confidence flag is
       mechanically required at every freeze, and the autonomy level is
       an explicit 3-mode dial (manual/conservative/auto) the human sets

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 unflagged-freeze            done      PASS 13†   ●●●●●●●●
 explicit-autonomy-dial      done      PASS 12†   ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (4 carried)
   • ADD · folded · a guard gains teeth without retro-redding
     predecessors via a verified-marker — stamp on the guarded crossing,
     enforce only on marked records (evidence: live audit 48→49 clean;
     the 45 pre-existing frozen tasks stayed silent)
   • SDD · folded · a lived artifact label can drift from its canonical
     glossary term — §3 `Least-sure flag surfaced at freeze:` vs
     `lowest-confidence flag`; bridged, not migrated, this loop
     (evidence: needed a MACHINE_SPAN + GLOSSARY bridge + guide reword
     to keep the ubiquitous-language & wording linters green)
   • ADD · folded · a docs-accord test must pin EVERY surface the §1
     Must names, or "prose ≡ enforcement" is only as wide as the pin —
     frozen §4 said "GLOSSARY + autonomy docs … synced ×3" but the
     implemented DocsAccordTest pinned 1 of 4, so 2 surfaces shipped
     stale-green and the gap was caught by human review at the gate, not
     by CI (evidence: DocsAccordTest extended 1→4 surfaces, RED on
     GLOSSARY + 11-governance before close)
   • ADD · folded · a word-ban linter does not catch a stale
     multi-valued DESCRIPTION — once a 3rd rung lands, "auto |
     conservative" enumerations read green to the slang fence; level-set
     prose widens by a structural/test pin or manual sweep, never by the
     vocab ban (evidence: streams.md + SKILL.md 2-mode stragglers passed
     the vocab linter, found only by the advisor-prompted method-wide
     grep)

 DECIDE NEXT  consolidate learnings + archive-milestone
              flag-first-freeze
════════════════════════════════════════════════════════════════════════