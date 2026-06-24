════════════════════════════════════════════════════════════════════════
 component-aware-add · Component-aware ADD
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     6/6 done           CRITERIA  6/6 met
 GATES     6 PASS             WAIVERS   none

 goal  ADD treats every codebase as a graph of components — each owning
       its source root, green-bar, and produced/consumed contracts — so
       a single milestone can ship a vertical slice across components
       living in one repo or many.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 component-registry          done      PASS 20†   ●●●●●●●●●
 per-component-verify        done      PASS 16†   ●●●●●●●●●
 cross-component-contract    done      PASS 0     ●●●●●●●●●
 cross-component-milestone   done      PASS 5†    ●●●●●●●●●
 multirepo-federation        done      PASS 11†   ●●●●●●●●●
 component-method-docs       done      PASS 4†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   component-registry       PASS Tin Dang <tindang.ht97@gmail.com>
   per-component-verify     PASS Tin Dang <tindang.ht97@gmail.com>
   cross-component-contract PASS Tin Dang <tindang.ht97@gmail.com>
   cross-component-milesto… PASS Tin Dang <tindang.ht97@gmail.com>
   multirepo-federation     PASS Tin Dang <tindang.ht97@gmail.com>
   component-method-docs    PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 6/6 met

 LEARNINGS (4 carried)
   • ADD · open · a degrade-safe contract clause ("never raise on a
     read") needs an explicit unreadable-dir/permission test — the
     happy-path tests passed while one OSError-subclass path
     (PermissionError from iterdir) still crashed; the refute-read
     caught it (evidence: refute-read MAJOR, fixed by
     `test_unreadable_tasks_dir_degrades_safe`).
   • ADD · open · a sentinel value used in logic (`"?"`) must be
     reserved from any user-supplied namespace it shares (TOML component
     names) or it silently collides (evidence: refute-read MINOR, fixed
     by reserving `"?"` +
     `test_reserved_question_mark_name_is_malformed`).
   • TDD · open · a byte-equality claim needs a fixture that can
     actually DIFFER in bytes — a `json.dumps` (\n-only) fixture made
     the byte-copy assert vacuous; the CRLF case exposed the
     text-mode-translation bug (evidence: refute-read Finding 1;
     red→green after `_atomic_write_bytes`).
   • ADD · open · a new agent-facing prose file ripples into THREE
     registries — the wording-lint surface count (×2 tests) + the skill
     lean fence — not just parity; a new skill guide's true cost is
     registration in all of them (evidence: component-method-docs build
     hit test_wording_lint + test_per_step_hooks + test_skill_lean
     before green).

 SPEC DELTAS    52 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              component-aware-add
════════════════════════════════════════════════════════════════════════