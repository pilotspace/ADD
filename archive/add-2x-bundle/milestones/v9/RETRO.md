════════════════════════════════════════════════════════════════════════
 v9 · Awareness surface — render what happened
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  4/4 met
 GATES     2 PASS             WAIVERS   none

 goal  A person can see what just happened, what it cost, and what was
       learned — per-task phase results rolled up under a milestone
       retrospective — rendered on demand to stdout and persisted as
       RETRO.md at milestone close, without reading prose by hand

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 report-render               done      PASS 0     ●●●●●●●●
 retro-artifact              done      PASS 0     ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (7 carried)
   • ADD · open · Presentation is not a freezable contract the way a
     behavioral/data seam is. The contract re-froze 3× (v1→v2→v3) and
     EVERY change was presentation; the data seam (`report_data` facts,
     reject codes, purity, fail-closed) never moved. Evidence: §3
     history line + the v2→v3 test churn touched only assertions about
     glyphs/columns, never about which facts. Fold: ADD's freeze-once
     discipline should bind the *facts/interface*, and explicitly mark a
     *presentation layer* as iterate-freely (don't stamp pixel layout
     "FROZEN @ vN"). This retroactively validates the tool-emits-data /
     agent-formats-report split (`--json` is the stable seam; the
     dashboard is a secondary, swappable surface).
   • SDD · open · A milestone's frozen exit criteria can silently rot
     when a task's own contract changes shape. Evidence: v3 made
     `report` stdout multi-valued (tty color/width vs canonical plain),
     which falsified v9 MILESTONE.md's "RETRO.md byte-identical to
     stdout" — caught only by the advisor, not by any gate. Fold: add a
     verify-checklist line "do the milestone's frozen exit criteria
     still hold after what I built?" so a shared-contract drift turns a
     gate red instead of slipping to milestone close.
   • TDD · open · When the test harness's capture stream (StringIO)
     lacks `.encoding`, the presentation tier auto-selects ASCII — so a
     test that drives the CLI and asserts Unicode glyphs is asserting
     against the wrong tier. Evidence: test_phase_track_compact /
     test_progress_bar_glyphs had to call `render_report(...)` directly
     (the canonical Unicode render) rather than capture `cmd_report`
     stdout. Fold: for tier-sensitive output, test the pure renderer at
     its canonical args; reserve CLI-capture tests for asserting the
     *tier-selection* logic itself.
   • UDD · open · A no-`wcwidth` terminal UI stays aligned by
     construction if richness rides on width-neutral channels (color)
     and only ASCII-safe text sits in `len()`-aligned columns, with
     Unicode glyphs confined to line-end. Evidence: 200 green incl.
     test_columns_aligned_no_len_rightpad with zero width-measurement
     code. Fold: capture this as the house rule for any future ADD TUI.
   • ADD · open · v9 reports the phase ROLLUP (which phase each task
     REACHED — the `●◉○` track + PHASE column), but NOT each phase's
     RESULT (what scenarios were set, what the contract froze, what
     verify actually found, the per-phase observe delta). The original
     ask was "report of each phase's result" — so v9 answers the
     milestone-level half and leaves the per-phase-detail half open.
     Evidence: a person reading `report v9` sees `report-render · done ·
     PASS` but must still open TASK.md to learn WHAT each phase decided.
     Fold: a future loop adds a per-phase detail view (e.g. `report
     <milestone> <task>` or a `--phases` drill-down) that surfaces each
     phase's frozen artifact + outcome — turning the rollup into a true
     phase-by-phase narrative. Owner-directed (user, 2026-06-02):
     "improve ADD to report each phase."
   • TDD · open · A "fail-closed / abort-before-mutate" guarantee is
     directly testable by monkeypatching the IO step to raise and
     asserting the downstream state commit did NOT happen. Evidence:
     test_failed_write_aborts_close patches `_write_retro`→OSError and
     asserts status never flips to done. Fold: make this the house
     pattern for any ordered "do-risky-IO THEN commit-state" path — the
     rollback is proven by the test, not just by reading the ordering.
   • ADD · open · A directed PRESENTATION change mid-flight
     (report-render v4, while retro-artifact was at verify) cost only a
     shape-sketch + test-assertion update — no re-freeze, no SPECIFY
     round-trip. Evidence: the v4 layout landed by updating §3's shape
     sketch + 4 assertions + 2 new guards, 208 green, while the frozen
     DATA seam was untouched. Fold: this empirically confirms
     report-render's [ADD] "presentation isn't a freezable contract"
     delta — bind the data seam, let the layer iterate. Worth promoting
     both to PROJECT.md as one method rule.
════════════════════════════════════════════════════════════════════════