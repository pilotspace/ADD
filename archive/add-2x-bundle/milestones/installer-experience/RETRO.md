════════════════════════════════════════════════════════════════════════
 installer-experience · Installer Experience
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     5/5 done           CRITERIA  5/5 met
 GATES     5 PASS             WAIVERS   none

 goal  stand up or repair ADD for any coding agent through one guided
       installer — interactive when the terminal allows, agent-aware,
       self-healing on partial setups, and installable globally or
       per-project

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 installer-prompts           done      PASS 15†   ●●●●●●●●●
 agent-detect                done      PASS 16†   ●●●●●●●●●
 heal-reconcile              done      PASS 11†   ●●●●●●●●●
 global-install              done      PASS 13†   ●●●●●●●●●
 global-data                 done      PASS 11†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (15 carried)
   • ADD · open · an ESM-only dep forces a CJS installer to
     dynamic-import() + go async; keep the non-interactive path
     await-free so exit-code/stdout ordering the piped tests assert is
     preserved (evidence: A1 flag held; clack 1.x is type:module; full
     suite stayed green after the async refactor).
   • TDD · open · interactive TUI flows aren't feedable via piped stdin
     (clack raw-mode); test branch-reachability via a CONTRACTED force
     seam ({"1","fail"}) + the happy path via a PTY probe — the seam is
     fault-injection, not a logic-deleting stub (evidence: earned-green
     refute-read passed; pty probe closed the M1 gap).
   • SDD · open · a new runtime dependency falsifies any "zero-dep"
     prose; grep + fix the claim in the SAME change (evidence: cli.js
     header corrected from "Zero npm dependencies";
     README/GETTING-STARTED/docs grepped clean).
   • ADD · open · "detect + auto-correct the agent" splits cleanly into
     a PURE detect (unit-testable) + a fail-soft WRITE (mirror the
     existing marker-injector, same markers so the canonical writer
     supersedes it) — never a second source of truth for the block
     (evidence: test_init_supersedes_pointer proves sync-guidelines
     replaces the drop-time pointer in place)
   • TDD · open · a test that inherits the ambient agent env (CLAUDECODE
     under Claude Code) silently changes behavior between local and CI —
     scrub the signal to pin the intended scenario deterministically
     (evidence: test_installer_handoff passed in CI but failed locally
     until its runners scrubbed the agent env)
   • ADD · open · env-signal detection should degrade to a SAFE default
     that equals prior behavior, so a wrong guess is never harmful —
     gate the feature on graceful fallback, not signal accuracy
     (evidence: every unmatched env → the generic AGENTS.md path proven
     agent-portable by test_agent_portability)
   • ADD · open · a refactor that collapses a structural shape (two-arg
     copy → one MANAGED mapping) silently breaks structural-regex tests
     OUTSIDE the declared §5 scope — disclose + re-aim the regex to the
     new shape, never weaken intent (evidence:
     test_v8_install::test_cli_bundles_brain went red on the MANAGED
     collapse, fixed by re-aiming to `"skill/add"`)
   • TDD · open · interactive/clean-replace IO is best proven by real
     on-disk asserts on a synthetic bundle (mirrors test_update.py)
     rather than mocking the copy — keeps the green earned (evidence:
     all 11 heal tests assert real file content/absence, caught the
     orphan-sweep + fail-closed behaviors)
   • ADD · open · a refactor leaves orphaned helpers (copyDir/_warn)
     behind — sweep dead code in the same loop and re-run the full suite
     to prove nothing referenced them (evidence: both removed, suite
     held 1226 green)
   • ADD · open · a frozen-contract INTERNAL inconsistency found at
     build (here: "propagate from <home>" but the home layout lacked the
     skill source MANAGED needs) is a legit CHANGE REQUEST — re-freeze
     (v2) + re-cross contract→tests→build BEFORE coding around it, never
     a silent code-around (evidence: §3 v2 mirror change).
   • TDD · open · a "propagate FROM X" contract where, at runtime, X is
     rebuilt from the same fixture the test seeds, is UN-distinguishable
     by a naive presence test — assert the SOURCE is complete instead of
     trying to prove which source was read (evidence: review N2 → §6
     hardening asserts the home holds skill/add+tooling+docs).
   • ADD · open · for the riskiest task in a milestone, an INDEPENDENT
     adversarial review subagent is a proportionate stand-in for the
     human gate under full-auto — and its disclosed NITs should be
     CLOSED (test-hardening) before the PASS, not just filed (evidence:
     review found N5/N2; both addressed pre-gate).
   • DDD · open · the managed↔user-data boundary is now a REUSED domain
     concept: heal-reconcile/global-install copy the MANAGED layer,
     global-data copies its COMPLEMENT (user-data) — naming the boundary
     once (an explicit include/exclude rule) let both sides share it
     (evidence: `_is_user_data` is the inverse of MANAGED).
   • TDD · open · for a COPY/snapshot feature, assert on CONTENT +
     ABSENCE (new state mirrored · deleted file gone · managed trees NOT
     present), never just "the dir exists" — presence-only tests pass
     for the wrong reason (evidence: §6 earned-green read).
   • ADD · open · a task whose word ("persist") spans a spectrum
     (snapshot↔sync↔restore) should freeze the SAFE subset (one-way,
     can't clobber) + seed the rest as deltas, rather than over-build
     under full-auto (evidence: D-A1 → one-way mvp + restore/sync
     deltas).

 SPEC DELTAS    14 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              installer-experience
════════════════════════════════════════════════════════════════════════