════════════════════════════════════════════════════════════════════════
 honest-fidelity-meter · Honest fidelity meter: deterministic requirement_coverage replaces artifact-blind spec_fidelity
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     6/6 done           CRITERIA  5/5 met
 GATES     6 PASS             WAIVERS   none

 goal  Replace the artifact-blind LLM spec_fidelity metric with a
       deterministic requirement_coverage meter (frozen per-requirement
       checklists + probes across all 6 WMs), promote oracle_pass_rate
       to the headline, and demote the LLM judge to an advisory
       source-aware code_quality_annotation
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 report-diagnostics          done      PASS 0     ●●●●
 coverage-scorer             done      PASS 0     ●●●●
 coverage-detail             done      PASS 0     ●●●●
 status-lean-default         done      PASS 0     ●●●●
 hermetic-scoring            done      PASS 0     ●●●●
 judge-advisory              done      PASS 0     ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   report-diagnostics       PASS Tin Dang <tindang.ht97@gmail.com>
   coverage-scorer          PASS Tin Dang <tindang.ht97@gmail.com>
   coverage-detail          PASS Tin Dang <tindang.ht97@gmail.com>
   status-lean-default      PASS Tin Dang <tindang.ht97@gmail.com>
   hermetic-scoring         PASS Tin Dang <tindang.ht97@gmail.com>
   judge-advisory           PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (2 carried)
   • TDD · open · a frozen build-expectation ("score the EXISTING
     record") is a stronger gate than the red suite — the suite's
     fixtures all wrote NEW-schema records, so only running the tool on
     real archived data surfaced the strict-read gap (evidence: `run.py
     score --arm add --wm 1` → invalid_run_record, un-pinned by any test
     until added)
   • SDD · open · a metric rename ripples past the schema into every
     CONSUMER that maps a label to it (pilot `_REP_METRICS` "fidelity",
     the attest audit CLI, the report audit hook) — a "swap one key"
     contract quietly retires a whole feature (evidence:
     spec_fidelity→requirement_coverage pulled in pilot.py + 3 test
     files beyond the declared §5 Scope)

 SPEC DELTAS    46 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone
              honest-fidelity-meter
              2 planned not yet scaffolded: wm-checklists ·
              rescore-progression
════════════════════════════════════════════════════════════════════════