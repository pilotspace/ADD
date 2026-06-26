════════════════════════════════════════════════════════════════════════
 engine-modularization · Split the 7k-line add.py engine into a focused add_engine/ package
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     16/16 done         CRITERIA  5/5 met
 GATES     16 PASS            WAIVERS   none

 goal  the engine is a navigable package of focused modules behind a
       stable import surface, with the entry path, 3-tree mirror, and
       ENGINE_MD5 pin all preserved
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 engine-package-skeleton     done      PASS 28†   ●●●●●●●●●
 extract-io-state            done      PASS 7†    ●●●●●●●●●
 extract-state               done      PASS 8†    ●●●●●●●●●
 extract-accessors           done      PASS 8†    ●●●●●●●●●
 extract-predicates          done      PASS 8†    ●●●●●●●●●
 extract-identity            done      PASS 55†   ●●●●●●●●●
 extract-pure-leaves         done      PASS 8†    ●●●●●●●●●
 extract-guidelines          done      PASS 8†    ●●●●●●●●●
 extract-render              done      PASS 11†   ●●●●●●●●●
 extract-milestones          done      PASS 8†    ●●●●●●●●●
 extract-components          done      PASS 8†    ●●●●●●●●●
 extract-md5                 done      PASS 10†   ●●●●●●●●●
 extract-version             done      PASS 9†    ●●●●●●●●●
 extract-release             done      PASS 10†   ●●●●●●●●●
 extract-taskdoc             done      PASS 10†   ●●●●●●●●●
 extract-autonomy            done      PASS 11†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   engine-package-skeleton  PASS Tin Dang <tindang.ht97@gmail.com>
   extract-io-state         PASS Tin Dang <tindang.ht97@gmail.com>
   extract-state            PASS Tin Dang <tindang.ht97@gmail.com>
   extract-accessors        PASS Tin Dang <tindang.ht97@gmail.com>
   extract-predicates       PASS Tin Dang <tindang.ht97@gmail.com>
   extract-identity         PASS Tin Dang <tindang.ht97@gmail.com>
   extract-pure-leaves      PASS Tin Dang <tindang.ht97@gmail.com>
   extract-guidelines       PASS Tin Dang <tindang.ht97@gmail.com>
   extract-render           PASS Tin Dang <tindang.ht97@gmail.com>
   extract-milestones       PASS Tin Dang <tindang.ht97@gmail.com>
   extract-components       PASS Tin Dang <tindang.ht97@gmail.com>
   extract-md5              PASS Tin Dang <tindang.ht97@gmail.com>
   extract-version          PASS Tin Dang <tindang.ht97@gmail.com>
   extract-release          PASS Tin Dang <tindang.ht97@gmail.com>
   extract-taskdoc          PASS Tin Dang <tindang.ht97@gmail.com>
   extract-autonomy         PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (14 carried)
   • ADD · open · the re-export pattern preserves cross-module
     monkeypatching for add.py-level callers; only INTERNAL-call patches
     need repointing (evidence: tasks 1-3 needed zero patch edits)
   • ADD · open · running the AST free-name scan UPFRONT (at ground)
     pre-empts the 806-error class from extract-state (evidence: this
     task's scan was clean before any code moved)
   • ADD · open · new module per cohesive concern keeps each extraction
     a clean leaf with a distinct dependency profile (evidence:
     accessors=import-free, predicates=re/const/io_state)
   • ADD · open · when commands call a fn BOTH directly and via an
     intermediary, a single patch target requires CALL-QUALIFICATION at
     every add.py site (evidence: identity dual-path; Tin authorized
     over reduce)
   • ADD · open · a pure helper's rightful home is the existing module
     that owns its concern/deps (predicate→predicates,
     state-load→io_state) — extend, don't proliferate modules (evidence:
     _task_done, _load_state_for_json)
   • ADD · open · a transitive-closure AST scan (not just one-level
     free-names) proves a cluster is self-contained → a closed unpatched
     cluster moves by plain re-export, no qualification (evidence: the
     8-fn guidelines subsystem, empty outbound set)
   • ADD · open · a SHARED constant (used by both moving + staying code)
     relocates to constants.py as the single source — distinguish from a
     cluster-PRIVATE const (travels with the cluster, like
     _ANSI/_INIT_EXCLUDE) (evidence: _DEFAULT_WIDTH vs _ANSI)
   • ADD · open · a scattered cluster member (e.g.
     _has_production_roadmap far from the rest) extracts fine — AST
     line-range capture handles non-contiguity (evidence: this cluster
     spanned 1105 + 3056-3174)
   • ADD · open · a degrade-safe stdlib guard (try/except import → None)
     must be REPLICATED in the new module, not bare-imported — the
     staying module keeps its own copy for its own users (evidence:
     tomllib in both components.py and add.py for _component_findings)
   • ADD · open · a 2-line low-level helper folds INTO the nearest
     foundational module (io_state) rather than spawning a thin
     single-purpose module — modularization groups by concern, not by
     maximizing module count (evidence: md5 → io_state, not a new
     hashing.py)
   • ADD · open · a test that REBINDS a module global (`add.X = lambda`,
     not patch.object) is re-export-safe IFF the caller stays in the
     host module (bare call resolves the host global) AND the moved fns
     don't call X internally — same rule as patch.object, different
     syntax (evidence: test_update_nudge.py rebinds
     add._fetch_latest_version; caller is the staying nudge-check)
   • ADD · open · the RELEASE-pillar render helpers form their own
     closed module (release.py) distinct from the milestone-doc readers
     (milestones.py) — scope-level concerns (RELEASE vs MILESTONE) map
     to separate modules even when both read ledgers (evidence:
     release.py vs milestones.py)
   • ADD · open · a SHARED constant interleaved with same-concern
     siblings is relocated by precise AST Assign-node ranges (move ONLY
     the shared names), leaving the siblings — text-region deletion
     would over-capture the interleaved keepers (evidence: 3 delta
     regexes among _SPEC_STATUSES/_STATUS_SETS/_TAG_BROAD_RE)
   • ADD · open · the modularization terminates when the residual is a
     single connected web around the central state I/O
     (load_state/save_state/report_data) — that spine IS the entry
     module; extracting further would require qualifying its mutual
     recursion, not a re-export (evidence: the deltas/cmd_* closure = 31
     fns around load_state)

 SPEC DELTAS    68 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              engine-modularization
              6 planned not yet scaffolded: extract-contracts ·
              extract-scope · extract-audit · extract-udd ·
              extract-guidelines-cli · migrate-test-imports
════════════════════════════════════════════════════════════════════════